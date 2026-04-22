import argparse
import json
import logging
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Set

import apicalls
import deployment
import ingestion
import reporting
import scoring
import training

logger = logging.getLogger(__name__)

try:
    import archive_diagnostics  # type: ignore
except ModuleNotFoundError:
    try:
        import standout.archive_diagnostics as archive_diagnostics  # type: ignore
    except ModuleNotFoundError:
        archive_diagnostics = None  # type: ignore[assignment]


def _get_project_dir() -> Path:
    return Path(__file__).resolve().parent


def _load_config(project_dir: Path) -> Dict[str, str]:
    with (project_dir / "config.json").open("r", encoding="utf-8") as file:
        return json.load(file)


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
    raw = score_path.read_text(encoding="utf-8").strip()
    try:
        return float(raw)
    except ValueError:
        return None


def _is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def _start_api_if_needed(project_dir: Path, host: str, port: int) -> Optional[subprocess.Popen]:
    """
    Start the Flask API in a subprocess if nothing is listening on the port.

    Returns:
        The subprocess Popen handle if we started it, else None.
    """
    if _is_port_open(host, port):
        logger.info("API already running on %s:%d", host, port)
        return None

    python_exe = sys.executable
    process = subprocess.Popen(
        [python_exe, str(project_dir / "app.py")],
        cwd=str(project_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    deadline = time.time() + 20
    while time.time() < deadline:
        if _is_port_open(host, port):
            logger.info("API started on %s:%d", host, port)
            return process
        if process.poll() is not None:
            output = ""
            if process.stdout is not None:
                output = process.stdout.read() or ""
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
    """
    Orchestrate the end-to-end monitoring and redeployment workflow (Step 5).

    Rubric logic (Section 5, `rubrica.md`):
    1. Stop early if no new (non-ingested) data is present in `input_folder_path`.
    2. Otherwise ingest, retrain, and score a candidate model.
    3. Read the deployed baseline score from `prod_deployment_path/latestscore.txt`.
    4. Deploy only when the candidate model is *better* than the deployed model
       (higher F1 score). If no deployed score exists, treat as initial deployment.
    5. After a deploy, regenerate the secondary reporting artifacts
       (`confusionmatrix2.png` and `apireturns2.txt`).

    Args:
        archive: If True (default), copy the current diagnostic artifacts into
            `olddiagnostics/` with a UTC timestamp before the run (standout #2).
    """
    project_dir = _get_project_dir()
    config = _load_config(project_dir)

    input_dir = project_dir / config["input_folder_path"]
    prod_dir = project_dir / config["prod_deployment_path"]
    prod_dir.mkdir(parents=True, exist_ok=True)

    ingestedfiles_path = prod_dir / "ingestedfiles.txt"
    already_ingested = _read_ingested_files(ingestedfiles_path)
    available = _list_csv_filenames(input_dir)
    new_files = sorted(list(available - already_ingested))

    # 1) Stop early if no new data.
    if len(new_files) == 0:
        logger.info("No new data files detected. Process ends here.")
        return

    if archive and archive_diagnostics is not None:
        try:
            archive_diagnostics.archive_current_diagnostics()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Diagnostics archive skipped: %s", exc)
    elif archive:
        logger.info("Diagnostics archive skipped: archive_diagnostics module not available.")

    logger.info("New data files detected: %s", new_files)

    # 2) Build candidate model from the updated dataset.
    ingestion.merge_multiple_dataframe()
    training.train_model()
    candidate_score = scoring.score_model()

    # 3) Compare with the deployed baseline score.
    deployed_score = _read_deployed_score(prod_dir / "latestscore.txt")
    if deployed_score is None:
        should_deploy = True
        logger.info("No deployed score found; initial deployment will be performed.")
    else:
        should_deploy = candidate_score > deployed_score
        logger.info(
            "Deployed F1=%s | Candidate F1=%s | Deploy=%s",
            deployed_score,
            candidate_score,
            should_deploy,
        )

    # 4) Deploy only when the new model strictly improves the deployed F1 score.
    if not should_deploy:
        logger.info("Candidate model does not outperform the deployed model. Process ends here.")
        return

    deployment.store_model_into_pickle()

    # 5) Post-deploy reporting artifacts.
    reporting.generate_confusion_matrix_plot(output_filename="confusionmatrix2.png")

    host = os.environ.get("APP_HOST", "127.0.0.1")
    port = int(os.environ.get("APP_PORT", "8000"))
    api_process: Optional[subprocess.Popen] = None
    try:
        api_process = _start_api_if_needed(project_dir, host=host, port=port)
        responses = apicalls.call_api_endpoints(
            prediction_filepath=str(Path(config["test_data_path"]) / "testdata.csv")
        )
        apicalls.write_api_returns((project_dir / config["output_model_path"]) / "apireturns2.txt", responses)
    finally:
        _stop_api(api_process)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Run the end-to-end Dynamic Risk Assessment pipeline.")
    parser.add_argument(
        "--no-archive",
        action="store_true",
        help="Skip archiving current diagnostics to olddiagnostics/.",
    )
    args = parser.parse_args()
    run_full_process(archive=not args.no_archive)


if __name__ == "__main__":
    main()
