"""
Time-trend archival (standout suggestion #2).

Copy the current diagnostic artifacts into an `olddiagnostics/` folder, each
file tagged with a UTC timestamp, so we can retrospectively analyze how NA %,
score, and ingested files evolve across runs.
"""
import argparse
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


def _get_project_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_config(project_dir: Path) -> Dict[str, str]:
    import json

    with (project_dir / "config.json").open("r", encoding="utf-8") as file:
        return json.load(file)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def archive_current_diagnostics(archive_dirname: str = "olddiagnostics") -> List[Path]:
    """
    Copy each currently-available diagnostic artifact into `{project}/{archive_dirname}/`
    with a timestamp suffix. Missing sources are skipped (no error).

    Returns the list of archive paths written.
    """
    project_dir = _get_project_dir()
    config = _load_config(project_dir)

    archive_dir = project_dir / archive_dirname
    archive_dir.mkdir(parents=True, exist_ok=True)

    stamp = _timestamp()
    sources = [
        project_dir / config["output_folder_path"] / "ingestedfiles.txt",
        project_dir / config["output_folder_path"] / "finaldata.csv",
        project_dir / config["output_model_path"] / "latestscore.txt",
        project_dir / config["output_model_path"] / "apireturns.txt",
        project_dir / config["output_model_path"] / "apireturns2.txt",
        project_dir / config["output_model_path"] / "confusionmatrix.png",
        project_dir / config["output_model_path"] / "confusionmatrix2.png",
    ]

    written: List[Path] = []
    for src in sources:
        if not src.exists():
            continue
        dest = archive_dir / f"{src.stem}_{stamp}{src.suffix}"
        shutil.copy2(src, dest)
        written.append(dest)
        logger.info("Archived %s -> %s", src.name, dest.name)

    return written


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Archive current diagnostics with a UTC timestamp.")
    parser.add_argument(
        "--archive-dir",
        default="olddiagnostics",
        help="Directory name (relative to project root) where archives are written.",
    )
    args = parser.parse_args()
    archive_current_diagnostics(archive_dirname=args.archive_dir)


if __name__ == "__main__":
    main()
