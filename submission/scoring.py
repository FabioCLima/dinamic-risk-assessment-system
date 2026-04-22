import argparse
import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List

import pandas as pd
from sklearn.metrics import f1_score

logger = logging.getLogger(__name__)

FEATURE_COLUMNS: List[str] = ["lastmonth_activity", "lastyear_activity", "number_of_employees"]
TARGET_COLUMN: str = "exited"


def _get_project_dir() -> Path:
    return Path(__file__).resolve().parent


def _load_config(project_dir: Path) -> Dict[str, str]:
    """Load `config.json` from the project root (same folder as this file)."""
    with (project_dir / "config.json").open("r", encoding="utf-8") as file:
        return json.load(file)


#################Function for model scoring
def score_model() -> float:
    """
    Score the trained model using the holdout test dataset.

    Reads:
        - `{test_data_path}/testdata.csv`
        - `{output_model_path}/trainedmodel.pkl`
    Writes:
        - `{output_model_path}/latestscore.txt`

    Returns:
        The F1 score.
    """
    project_dir = _get_project_dir()
    config = _load_config(project_dir)

    test_dir = project_dir / config["test_data_path"]
    model_dir = project_dir / config["output_model_path"]
    model_dir.mkdir(parents=True, exist_ok=True)

    testdata_path = test_dir / "testdata.csv"
    if not testdata_path.exists():
        raise FileNotFoundError(f"Test dataset not found at {testdata_path}")

    model_path = model_dir / "trainedmodel.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Trained model not found at {model_path}. Run training.py first.")

    test_df = pd.read_csv(testdata_path)
    missing = [c for c in (FEATURE_COLUMNS + [TARGET_COLUMN]) if c not in test_df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {testdata_path}: {missing}")

    x_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    with model_path.open("rb") as file:
        model = pickle.load(file)

    y_pred = model.predict(x_test)
    score = float(f1_score(y_test, y_pred))

    score_path = model_dir / "latestscore.txt"
    score_path.write_text(f"{score}\n", encoding="utf-8")

    logger.info("F1 score written to %s (%s)", score_path, score)

    # Best-effort SQLite history (standout suggestion #3).
    try:
        import dbsetup

        dbsetup.init_db()
        dbsetup.record_score(score, source="scoring")
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Skipping DB history write: %s", exc)

    return score


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute the F1 score of the trained model on the test set.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable DEBUG logging.")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    score_model()


if __name__ == "__main__":
    main()
