import argparse
import logging
from typing import List, Tuple

import pandas as pd

from dynamic_risk_assessment.config import load_config, resolve_path

logger = logging.getLogger(__name__)


def merge_multiple_dataframe() -> Tuple[pd.DataFrame, List[str]]:
    config = load_config()
    input_dir = resolve_path(config["input_folder_path"])
    output_dir = resolve_path(config["output_folder_path"])
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_dir.exists() or not input_dir.is_dir():
        raise NotADirectoryError(f"Configured input_folder_path is not a directory: {input_dir}")

    csv_paths = sorted(p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".csv")
    if not csv_paths:
        raise FileNotFoundError(f"No .csv files found in input folder: {input_dir}")

    dataframes: List[pd.DataFrame] = []
    ingested_filenames: List[str] = []
    for csv_path in csv_paths:
        logger.info("Reading %s", csv_path.name)
        dataframes.append(pd.read_csv(csv_path))
        ingested_filenames.append(csv_path.name)

    merged_dataframe = pd.concat(dataframes, ignore_index=True).drop_duplicates().reset_index(drop=True)
    merged_dataframe.to_csv(output_dir / "finaldata.csv", index=False)
    (output_dir / "ingestedfiles.txt").write_text("\n".join(ingested_filenames) + "\n", encoding="utf-8")

    try:
        from dynamic_risk_assessment import dbsetup

        dbsetup.init_db()
        dbsetup.record_ingestion(len(merged_dataframe), ingested_filenames)
    except Exception as exc:  # pragma: no cover
        logger.warning("Skipping DB history write: %s", exc)

    return merged_dataframe, ingested_filenames


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest CSV files into a single deduplicated dataset.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable DEBUG logging.")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    merge_multiple_dataframe()


if __name__ == "__main__":
    main()
