import argparse
import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List

import pandas as pd
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)

FEATURE_COLUMNS: List[str] = ["lastmonth_activity", "lastyear_activity", "number_of_employees"]
TARGET_COLUMN: str = "exited"


def _load_config(project_dir: Path) -> Dict[str, str]:
    """Load `config.json` from the project root (same folder as this file)."""
    with (project_dir / "config.json").open("r", encoding="utf-8") as file:
        return json.load(file)


def _get_project_dir() -> Path:
    return Path(__file__).resolve().parent


#################Function for training the model
def train_model() -> LogisticRegression:
    """
    Train an attrition-risk model (logistic regression) using Step 1 output data.

    Reads:
        - `{output_folder_path}/finaldata.csv`
    Writes:
        - `{output_model_path}/trainedmodel.pkl`

    Returns:
        The trained scikit-learn LogisticRegression model.
    """
    project_dir = _get_project_dir()
    config = _load_config(project_dir)

    ingested_dir = project_dir / config["output_folder_path"]
    model_dir = project_dir / config["output_model_path"]
    model_dir.mkdir(parents=True, exist_ok=True)

    finaldata_path = ingested_dir / "finaldata.csv"
    if not finaldata_path.exists():
        raise FileNotFoundError(
            f"Training dataset not found at {finaldata_path}. Run ingestion.py first."
        )

    df = pd.read_csv(finaldata_path)
    missing = [c for c in (FEATURE_COLUMNS + [TARGET_COLUMN]) if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {finaldata_path}: {missing}")

    x = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    model = LogisticRegression(solver="liblinear", random_state=0, max_iter=1000)
    model.fit(x, y)

    model_path = model_dir / "trainedmodel.pkl"
    with model_path.open("wb") as file:
        pickle.dump(model, file)

    logger.info("Trained model written to %s", model_path)
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
