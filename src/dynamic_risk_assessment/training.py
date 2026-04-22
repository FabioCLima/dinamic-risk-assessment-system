import argparse
import logging
import pickle
from typing import List

import pandas as pd
from sklearn.linear_model import LogisticRegression

from dynamic_risk_assessment.config import load_config, resolve_path

logger = logging.getLogger(__name__)

FEATURE_COLUMNS: List[str] = ["lastmonth_activity", "lastyear_activity", "number_of_employees"]
TARGET_COLUMN: str = "exited"


def train_model() -> LogisticRegression:
    config = load_config()
    ingested_dir = resolve_path(config["output_folder_path"])
    model_dir = resolve_path(config["output_model_path"])
    model_dir.mkdir(parents=True, exist_ok=True)

    finaldata_path = ingested_dir / "finaldata.csv"
    if not finaldata_path.exists():
        raise FileNotFoundError(f"Training dataset not found at {finaldata_path}. Run ingestion first.")

    df = pd.read_csv(finaldata_path)
    missing = [c for c in (FEATURE_COLUMNS + [TARGET_COLUMN]) if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {finaldata_path}: {missing}")

    model = LogisticRegression(solver="liblinear", random_state=0, max_iter=1000)
    model.fit(df[FEATURE_COLUMNS], df[TARGET_COLUMN])

    with (model_dir / "trainedmodel.pkl").open("wb") as file:
        pickle.dump(model, file)

    logger.info("Trained model written to %s", model_dir / "trainedmodel.pkl")
    return model


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the attrition-risk logistic regression model.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable DEBUG logging.")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    train_model()


if __name__ == "__main__":
    main()
