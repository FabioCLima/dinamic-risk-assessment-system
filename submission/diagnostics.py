import argparse
import json
import logging
import pickle
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

FEATURE_COLUMNS: List[str] = ["lastmonth_activity", "lastyear_activity", "number_of_employees"]
TARGET_COLUMN: str = "exited"


def _get_project_dir() -> Path:
    return Path(__file__).resolve().parent


def _load_config(project_dir: Path) -> Dict[str, str]:
    with (project_dir / "config.json").open("r", encoding="utf-8") as file:
        return json.load(file)


def _load_finaldata(project_dir: Path, config: Dict[str, str]) -> pd.DataFrame:
    dataset_dir = project_dir / config["output_folder_path"]
    finaldata_path = dataset_dir / "finaldata.csv"
    if not finaldata_path.exists():
        raise FileNotFoundError(f"Dataset not found at {finaldata_path}. Run ingestion.py first.")
    return pd.read_csv(finaldata_path)


##################Function to get model predictions
def model_predictions(dataset: pd.DataFrame) -> List[int]:
    """
    Generate predictions using the currently deployed model.

    Args:
        dataset: Input dataset as a Pandas DataFrame.

    Returns:
        A list of predictions, one per input row.
    """
    project_dir = _get_project_dir()
    config = _load_config(project_dir)

    prod_dir = project_dir / config["prod_deployment_path"]
    model_path = prod_dir / "trainedmodel.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Deployed model not found at {model_path}. Run deployment.py first.")

    for col in FEATURE_COLUMNS:
        if col not in dataset.columns:
            raise ValueError(f"Missing required feature column: {col}")

    with model_path.open("rb") as file:
        model = pickle.load(file)

    predictions = model.predict(dataset[FEATURE_COLUMNS])
    return [int(p) for p in predictions]


##################Function to get summary statistics
def dataframe_summary() -> List[float]:
    """
    Calculate mean, median, and mode for each numeric column (per the project rubric).

    The dataset is loaded from `{output_folder_path}/finaldata.csv`.

    Returns:
        A flat list containing (mean, median, mode) for each numeric column, in column order.
    """
    project_dir = _get_project_dir()
    config = _load_config(project_dir)
    df = _load_finaldata(project_dir, config)

    numeric_df = df.select_dtypes(include="number")
    summary: List[float] = []
    for col in numeric_df.columns:
        series = numeric_df[col]
        mode_series = series.mode(dropna=True)
        mode_value = float(mode_series.iloc[0]) if not mode_series.empty else float("nan")
        summary.extend([float(series.mean()), float(series.median()), mode_value])
    return summary


##################Function to check for missing data
def missing_data() -> List[float]:
    """
    Compute the percentage of NA values for each column in the dataset.

    Returns:
        A list with one float per column: percent NA in that column.
    """
    project_dir = _get_project_dir()
    config = _load_config(project_dir)
    df = _load_finaldata(project_dir, config)

    if len(df) == 0:
        return [0.0 for _ in df.columns]

    percents = (df.isna().sum() / len(df)).astype(float).tolist()
    return [float(p) for p in percents]


##################Function to get timings
def execution_time() -> List[float]:
    """
    Measure execution time (seconds) for key pipeline scripts:
    - ingestion.py (Step 1)
    - training.py (Step 2)

    Returns:
        [ingestion_seconds, training_seconds]
    """
    project_dir = _get_project_dir()
    python_exe = sys.executable

    def _time_script(script_name: str) -> float:
        start = time.perf_counter()
        subprocess.run([python_exe, str(project_dir / script_name)], check=True, capture_output=True, text=True)
        return float(time.perf_counter() - start)

    ingestion_seconds = _time_script("ingestion.py")
    training_seconds = _time_script("training.py")
    return [ingestion_seconds, training_seconds]


##################Function to check dependencies
def outdated_packages_list() -> List[Dict[str, Any]]:
    """
    Compare installed vs latest versions for dependencies in `requirements.txt`.

    Uses pip to fetch installed packages and outdated packages, then builds a table-like list.

    Returns:
        A list of dicts with keys: name, installed_version, latest_version
    """
    project_dir = _get_project_dir()
    requirements_path = project_dir / "requirements.txt"
    if not requirements_path.exists():
        raise FileNotFoundError(f"requirements.txt not found at {requirements_path}")

    def _pkg_name(requirement_line: str) -> str:
        line = requirement_line.strip()
        if not line or line.startswith("#"):
            return ""
        for sep in ["==", ">=", "<=", "~=", ">", "<"]:
            if sep in line:
                return line.split(sep, 1)[0].strip()
        return line

    package_names = [_pkg_name(line) for line in requirements_path.read_text(encoding="utf-8").splitlines()]
    package_names = [p for p in package_names if p]

    python_exe = sys.executable

    installed = subprocess.run(
        [python_exe, "-m", "pip", "list", "--format=json"],
        check=True,
        capture_output=True,
        text=True,
    )
    installed_json = json.loads(installed.stdout)
    installed_map = {p["name"].lower(): p["version"] for p in installed_json}

    outdated = subprocess.run(
        [python_exe, "-m", "pip", "list", "--outdated", "--format=json"],
        check=True,
        capture_output=True,
        text=True,
    )
    outdated_json = json.loads(outdated.stdout)
    latest_map = {p["name"].lower(): p["latest_version"] for p in outdated_json}

    table: List[Dict[str, Any]] = []
    for name in package_names:
        key = name.lower()
        installed_version = installed_map.get(key, None)
        latest_version = latest_map.get(key, installed_version)
        table.append(
            {
                "name": name,
                "installed_version": installed_version,
                "latest_version": latest_version,
            }
        )

    return table


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all diagnostics: stats, missing %, timing, deps, predictions.")
    parser.add_argument("--skip-timing", action="store_true", help="Skip execution_time (which re-runs ingestion/training).")
    parser.add_argument("--skip-deps", action="store_true", help="Skip outdated_packages_list (network-bound pip call).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable DEBUG logging.")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    project_dir = _get_project_dir()
    config = _load_config(project_dir)
    df = _load_finaldata(project_dir, config)

    summary = dataframe_summary()
    missing = missing_data()
    timings = [None, None] if args.skip_timing else execution_time()
    deps = [] if args.skip_deps else outdated_packages_list()
    preds = model_predictions(df)
    logger.info("Diagnostics completed: %d predictions, %d summary values, %d deps.", len(preds), len(summary), len(deps))

    # Best-effort SQLite history (standout #3).
    try:
        import dbsetup

        dbsetup.init_db()
        dbsetup.record_diagnostics(
            ingestion_seconds=timings[0] if timings else None,
            training_seconds=timings[1] if timings else None,
            missing_percent=missing,
            summary_values=summary,
            dependencies=deps,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Skipping DB history write: %s", exc)


if __name__ == "__main__":
    main()
