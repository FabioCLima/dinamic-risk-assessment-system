import argparse
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from dynamic_risk_assessment.config import load_config, resolve_path

logger = logging.getLogger(__name__)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def archive_current_diagnostics(archive_dirname: str = "workspace_local/olddiagnostics") -> List[Path]:
    config = load_config()
    archive_dir = resolve_path(archive_dirname)
    archive_dir.mkdir(parents=True, exist_ok=True)
    stamp = _timestamp()

    sources = [
        resolve_path(config["output_folder_path"]) / "ingestedfiles.txt",
        resolve_path(config["output_folder_path"]) / "finaldata.csv",
        resolve_path(config["output_model_path"]) / "latestscore.txt",
        resolve_path(config["output_model_path"]) / "apireturns.txt",
        resolve_path(config["output_model_path"]) / "apireturns2.txt",
        resolve_path(config["output_model_path"]) / "confusionmatrix.png",
        resolve_path(config["output_model_path"]) / "confusionmatrix2.png",
    ]

    written: List[Path] = []
    for src in sources:
        if not src.exists():
            continue
        dest = archive_dir / f"{src.stem}_{stamp}{src.suffix}"
        shutil.copy2(src, dest)
        written.append(dest)
    return written


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Archive current diagnostics with a UTC timestamp.")
    parser.add_argument("--archive-dir", default="workspace_local/olddiagnostics")
    args = parser.parse_args()
    archive_current_diagnostics(archive_dirname=args.archive_dir)


if __name__ == "__main__":
    main()
