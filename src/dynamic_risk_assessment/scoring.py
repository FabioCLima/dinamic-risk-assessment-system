import argparse
import logging
import pickle
from typing import List

import pandas as pd
from sklearn.metrics import f1_score

from dynamic_risk_assessment.config import load_config, resolve_path

logger = logging.getLogger(__name__)

FEATURE_COLUMNS: List[str] = ["lastmonth_activity", "lastyear_activity", "number_of_employees"]
TARGET_COLUMN: str = "exited"


def score_model() -> float:
    config = load_config()
    test_dir = resolve_path(config["test_data_path"])
    model_dir = resolve_path(config["output_model_path"])
    model_dir.mkdir(parents=True, exist_ok=True)

    testdata_path = test_dir / "testdata.csv"
    model_path = model_dir / "trainedmodel.pkl"
    if not testdata_path.exists():
        raise FileNotFoundError(f"Test dataset not found at {testdata_path}")
    if not model_path.exists():
        raise FileNotFoundError(f"Trained model not found at {model_path}. Run training first.")

    test_df = pd.read_csv(testdata_path)
    missing = [c for c in (FEATURE_COLUMNS + [TARGET_COLUMN]) if c not in test_df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {testdata_path}: {missing}")

    with model_path.open("rb") as file:
        model = pickle.load(file)
    score = float(f1_score(test_df[TARGET_COLUMN], model.predict(test_df[FEATURE_COLUMNS])))
    (model_dir / "latestscore.txt").write_text(f"{score}\n", encoding="utf-8")

    try:
        from dynamic_risk_assessment import dbsetup

        dbsetup.init_db()
        dbsetup.record_score(score, source="scoring")
    except Exception as exc:  # pragma: no cover
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
