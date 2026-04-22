import argparse
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix

from dynamic_risk_assessment import diagnostics
from dynamic_risk_assessment.config import load_config, resolve_path

logger = logging.getLogger(__name__)


def _resolve_output_path(output_value: str, default_name: str) -> Path:
    path = Path(output_value or default_name)
    if not path.is_absolute():
        path = resolve_path(path.as_posix())
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def generate_confusion_matrix_plot(output_filename: str = "confusionmatrix.png") -> Path:
    config = load_config()
    testdata_path = resolve_path(config["test_data_path"]) / "testdata.csv"
    if not testdata_path.exists():
        raise FileNotFoundError(f"Test dataset not found at {testdata_path}")

    if not Path(output_filename).is_absolute() and Path(output_filename).parent == Path("."):
        output_filename = f'{config["output_model_path"]}/{output_filename}'
    output_path = _resolve_output_path(output_filename, f'{config["output_model_path"]}/confusionmatrix.png')

    test_df = pd.read_csv(testdata_path)
    y_true = test_df[diagnostics.TARGET_COLUMN].astype(int).tolist()
    y_pred = diagnostics.model_predictions(test_df)
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])

    plt.figure(figsize=(5, 4))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", cbar=False, xticklabels=[0, 1], yticklabels=[0, 1])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Generate the model reporting artifacts.")
    parser.add_argument("--output", default="confusionmatrix.png")
    args = parser.parse_args()
    generate_confusion_matrix_plot(output_filename=args.output)


if __name__ == "__main__":
    main()
