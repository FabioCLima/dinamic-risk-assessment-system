import argparse
import json
import logging
import shutil
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


def _get_project_dir() -> Path:
    return Path(__file__).resolve().parent


def _load_config(project_dir: Path) -> Dict[str, str]:
    """Load `config.json` from the project root (same folder as this file)."""
    with (project_dir / "config.json").open("r", encoding="utf-8") as file:
        return json.load(file)


####################function for deployment
def store_model_into_pickle() -> None:
    """
    Copy the latest model artifacts into the production deployment folder.

    This step should *only* copy existing files (no new training/scoring here).

    Copies:
        - `{output_model_path}/trainedmodel.pkl`
        - `{output_model_path}/latestscore.txt`
        - `{output_folder_path}/ingestedfiles.txt`
    Into:
        - `{prod_deployment_path}/`
    """
    project_dir = _get_project_dir()
    config = _load_config(project_dir)

    ingested_dir = project_dir / config["output_folder_path"]
    model_dir = project_dir / config["output_model_path"]
    prod_dir = project_dir / config["prod_deployment_path"]
    prod_dir.mkdir(parents=True, exist_ok=True)

    sources = [
        model_dir / "trainedmodel.pkl",
        model_dir / "latestscore.txt",
        ingested_dir / "ingestedfiles.txt",
    ]
    for src in sources:
        if not src.exists():
            raise FileNotFoundError(
                f"Required artifact not found: {src}. Ensure Step 1 + training/scoring ran successfully."
            )

    for src in sources:
        dest = prod_dir / src.name
        shutil.copy2(src, dest)
        logger.info("Copied %s -> %s", src, dest)


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy trained artifacts to prod_deployment_path.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable DEBUG logging.")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    store_model_into_pickle()


if __name__ == "__main__":
    main()
