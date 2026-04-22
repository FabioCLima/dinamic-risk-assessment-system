import argparse
import logging
import shutil

from dynamic_risk_assessment.config import load_config, resolve_path

logger = logging.getLogger(__name__)


def store_model_into_pickle() -> None:
    config = load_config()
    ingested_dir = resolve_path(config["output_folder_path"])
    model_dir = resolve_path(config["output_model_path"])
    prod_dir = resolve_path(config["prod_deployment_path"])
    prod_dir.mkdir(parents=True, exist_ok=True)

    sources = [
        model_dir / "trainedmodel.pkl",
        model_dir / "latestscore.txt",
        ingested_dir / "ingestedfiles.txt",
    ]
    for src in sources:
        if not src.exists():
            raise FileNotFoundError(f"Required artifact not found: {src}")
    for src in sources:
        shutil.copy2(src, prod_dir / src.name)


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
