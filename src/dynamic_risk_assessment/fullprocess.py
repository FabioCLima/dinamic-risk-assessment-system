import argparse
import logging
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Set

from dynamic_risk_assessment import apicalls, archive_diagnostics, deployment, ingestion, reporting, scoring, training
from dynamic_risk_assessment.config import load_config, repo_root, resolve_path

logger = logging.getLogger(__name__)


def _read_ingested_files(ingestedfiles_path: Path) -> Set[str]:
    if not ingestedfiles_path.exists():
        return set()
    return {line.strip() for line in ingestedfiles_path.read_text(encoding="utf-8").splitlines() if line.strip()}


def _list_csv_filenames(folder: Path) -> Set[str]:
    if not folder.exists() or not folder.is_dir():
        raise NotADirectoryError(f"Input folder not found: {folder}")
    return {p.name for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".csv"}


def _read_deployed_score(score_path: Path) -> Optional[float]:
    if not score_path.exists():
        return None
    try:
        return float(score_path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def _is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def _start_api_if_needed(host: str, port: int) -> Optional[subprocess.Popen]:
    if _is_port_open(host, port):
        return None
    process = subprocess.Popen(
        [sys.executable, "-m", "dynamic_risk_assessment.app"],
        cwd=str(repo_root()),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env={**os.environ, "APP_PORT": str(port)},
    )
    deadline = time.time() + 20
    while time.time() < deadline:
        if _is_port_open(host, port):
            return process
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout is not None else ""
            raise RuntimeError(f"API process exited early. Output:\n{output}")
        time.sleep(0.2)
    process.terminate()
    raise TimeoutError("Timed out waiting for API server to start.")


def _stop_api(process: Optional[subprocess.Popen]) -> None:
    if process is None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def run_full_process(archive: bool = True) -> None:
    config = load_config()
    input_dir = resolve_path(config["input_folder_path"])
    prod_dir = resolve_path(config["prod_deployment_path"])
    prod_dir.mkdir(parents=True, exist_ok=True)

    new_files = sorted(list(_list_csv_filenames(input_dir) - _read_ingested_files(prod_dir / "ingestedfiles.txt")))
    if not new_files:
        return
    if archive:
        try:
            archive_diagnostics.archive_current_diagnostics()
        except Exception as exc:  # pragma: no cover
            logger.warning("Diagnostics archive skipped: %s", exc)

    ingestion.merge_multiple_dataframe()
    training.train_model()
    candidate_score = scoring.score_model()
    deployed_score = _read_deployed_score(prod_dir / "latestscore.txt")
    should_deploy = deployed_score is None or candidate_score > deployed_score
    if not should_deploy:
        return

    deployment.store_model_into_pickle()
    reporting.generate_confusion_matrix_plot(output_filename="confusionmatrix2.png")

    host = os.environ.get("APP_HOST", "127.0.0.1")
    port = int(os.environ.get("APP_PORT", "8000"))
    api_process: Optional[subprocess.Popen] = None
    try:
        api_process = _start_api_if_needed(host=host, port=port)
        responses = apicalls.call_api_endpoints(
            base_url=f"http://{host}:{port}",
            prediction_filepath=str(Path(config["test_data_path"]) / "testdata.csv"),
        )
        apicalls.write_api_returns(resolve_path(config["output_model_path"]) / "apireturns2.txt", responses)
    finally:
        _stop_api(api_process)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Run the end-to-end Dynamic Risk Assessment pipeline.")
    parser.add_argument("--no-archive", action="store_true")
    args = parser.parse_args()
    run_full_process(archive=not args.no_archive)


if __name__ == "__main__":
    main()
