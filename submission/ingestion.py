import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


logger = logging.getLogger(__name__)


def _get_project_dir() -> Path:
    return Path(__file__).resolve().parent


def _load_config(project_dir: Path) -> Dict[str, str]:
    with (project_dir / "config.json").open("r", encoding="utf-8") as file:
        return json.load(file)


#############Function for data ingestion
def merge_multiple_dataframe() -> Tuple[pd.DataFrame, List[str]]:
    """
    Merge all CSV files in the configured input directory into one dataset.

    Requirements (Udacity Step 1):
    - Auto-detect every `.csv` under `input_folder_path` (no hard-coded names)
    - Concatenate into a single DataFrame
    - Remove duplicate rows
    - Write `finaldata.csv` to `output_folder_path`
    - Write `ingestedfiles.txt` to `output_folder_path` (one filename per line)

    Returns:
        (merged_dataframe, ingested_filenames)
    """
    project_dir = _get_project_dir()
    config = _load_config(project_dir)

    input_dir = project_dir / config["input_folder_path"]
    output_dir = project_dir / config["output_folder_path"]
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

    finaldata_path = output_dir / "finaldata.csv"
    ingestedfiles_path = output_dir / "ingestedfiles.txt"

    merged_dataframe.to_csv(finaldata_path, index=False)
    ingestedfiles_path.write_text("\n".join(ingested_filenames) + "\n", encoding="utf-8")

    logger.info("Wrote %s (%d rows)", finaldata_path, len(merged_dataframe))
    logger.info("Wrote %s", ingestedfiles_path)

    # Best-effort SQLite history (standout suggestion #3). Never break ingestion if this fails.
    try:
        import dbsetup

        dbsetup.init_db()
        dbsetup.record_ingestion(len(merged_dataframe), ingested_filenames)
    except Exception as exc:  # pragma: no cover - defensive
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
