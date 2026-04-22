import argparse
import json
import logging
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

from dynamic_risk_assessment.config import load_config, repo_root, resolve_path

logger = logging.getLogger(__name__)
DEFAULT_PORT = int(os.environ.get("APP_PORT", "8000"))


def _is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def _start_api(host: str, port: int) -> subprocess.Popen:
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


def _post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url: str) -> Dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_api_endpoints(base_url: str, prediction_filepath: str) -> Dict[str, Any]:
    return {
        "prediction": _post_json(f"{base_url}/prediction", {"filepath": prediction_filepath}),
        "scoring": _get_json(f"{base_url}/scoring"),
        "summarystats": _get_json(f"{base_url}/summarystats"),
        "diagnostics": _get_json(f"{base_url}/diagnostics"),
    }


def write_api_returns(output_path: Path, responses: Dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(responses, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Call the Dynamic Risk Assessment API and save responses.")
    parser.add_argument("--host", default=os.environ.get("APP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("APP_PORT", str(DEFAULT_PORT))))
    parser.add_argument("--prediction-input", default=None)
    parser.add_argument("--output", default="apireturns.txt")
    args = parser.parse_args()

    config = load_config()
    prediction_input = args.prediction_input or str(Path(config["test_data_path"]) / "testdata.csv")
    base_url = f"http://{args.host}:{args.port}"
    output_dir = resolve_path(config["output_model_path"])

    api_process: Optional[subprocess.Popen] = None
    try:
        if not _is_port_open(args.host, args.port):
            api_process = _start_api(host=args.host, port=args.port)
        responses = call_api_endpoints(base_url=base_url, prediction_filepath=prediction_input)
        write_api_returns(output_dir / args.output, responses)
    finally:
        _stop_api(api_process)


if __name__ == "__main__":
    main()
