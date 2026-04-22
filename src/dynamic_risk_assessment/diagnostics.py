import argparse
import json
import logging
import os
import pickle
import subprocess
import sys
import time
from typing import Any, Dict, List

import pandas as pd

from dynamic_risk_assessment.config import load_config, repo_root, resolve_path

logger = logging.getLogger(__name__)
FEATURE_COLUMNS: List[str] = ["lastmonth_activity", "lastyear_activity", "number_of_employees"]
TARGET_COLUMN: str = "exited"


def _load_finaldata(config: Dict[str, str]) -> pd.DataFrame:
    finaldata_path = resolve_path(config["output_folder_path"]) / "finaldata.csv"
    if not finaldata_path.exists():
        raise FileNotFoundError(f"Dataset not found at {finaldata_path}. Run ingestion first.")
    return pd.read_csv(finaldata_path)


def model_predictions(dataset: pd.DataFrame) -> List[int]:
    config = load_config()
    model_path = resolve_path(config["prod_deployment_path"]) / "trainedmodel.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Deployed model not found at {model_path}. Run deployment first.")
    for col in FEATURE_COLUMNS:
        if col not in dataset.columns:
            raise ValueError(f"Missing required feature column: {col}")
    with model_path.open("rb") as file:
        model = pickle.load(file)
    return [int(p) for p in model.predict(dataset[FEATURE_COLUMNS])]


def dataframe_summary() -> List[float]:
    df = _load_finaldata(load_config())
    numeric_df = df.select_dtypes(include="number")
    summary: List[float] = []
    for col in numeric_df.columns:
        series = numeric_df[col]
        mode_series = series.mode(dropna=True)
        mode_value = float(mode_series.iloc[0]) if not mode_series.empty else float("nan")
        summary.extend([float(series.mean()), float(series.median()), mode_value])
    return summary


def missing_data() -> List[float]:
    df = _load_finaldata(load_config())
    if len(df) == 0:
        return [0.0 for _ in df.columns]
    return [float(p) for p in (df.isna().sum() / len(df)).astype(float).tolist()]


def execution_time() -> List[float]:
    python_exe = sys.executable

    def _time_module(module_name: str) -> float:
        root = repo_root()
        src_path = str(root / "src")
        existing = os.environ.get("PYTHONPATH", "")
        pythonpath = src_path if not existing else f"{src_path}:{existing}"
        start = time.perf_counter()
        subprocess.run(
            [python_exe, "-m", module_name],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(root),
            env={**os.environ, "PYTHONPATH": pythonpath},
        )
        return float(time.perf_counter() - start)

    return [
        _time_module("dynamic_risk_assessment.ingestion"),
        _time_module("dynamic_risk_assessment.training"),
    ]


def outdated_packages_list() -> List[Dict[str, Any]]:
    requirements_path = repo_root() / "workspace_local" / "requirements.txt"
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

    installed = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"], check=True, capture_output=True, text=True
    )
    outdated = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"], check=True, capture_output=True, text=True
    )
    installed_map = {p["name"].lower(): p["version"] for p in json.loads(installed.stdout)}
    latest_map = {p["name"].lower(): p["latest_version"] for p in json.loads(outdated.stdout)}

    table: List[Dict[str, Any]] = []
    for name in package_names:
        key = name.lower()
        installed_version = installed_map.get(key, None)
        latest_version = latest_map.get(key, installed_version)
        table.append({"name": name, "installed_version": installed_version, "latest_version": latest_version})
    return table


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all diagnostics.")
    parser.add_argument("--skip-timing", action="store_true")
    parser.add_argument("--skip-deps", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    config = load_config()
    df = _load_finaldata(config)
    summary = dataframe_summary()
    missing = missing_data()
    timings = [None, None] if args.skip_timing else execution_time()
    deps = [] if args.skip_deps else outdated_packages_list()
    _ = model_predictions(df)
    try:
        from dynamic_risk_assessment import dbsetup

        dbsetup.init_db()
        dbsetup.record_diagnostics(
            ingestion_seconds=timings[0] if timings else None,
            training_seconds=timings[1] if timings else None,
            missing_percent=missing,
            summary_values=summary,
            dependencies=deps,
        )
    except Exception as exc:  # pragma: no cover
        logger.warning("Skipping DB history write: %s", exc)


if __name__ == "__main__":
    main()
