import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix

import diagnostics

logger = logging.getLogger(__name__)


def _get_project_dir() -> Path:
    return Path(__file__).resolve().parent


def _load_config(project_dir: Path) -> Dict[str, str]:
    with (project_dir / "config.json").open("r", encoding="utf-8") as file:
        return json.load(file)


def generate_confusion_matrix_plot(output_filename: str = "confusionmatrix.png") -> Path:
    """
    Generate a confusion matrix plot using the deployed model and the test dataset.

    Reads:
        - `{test_data_path}/testdata.csv`
        - Deployed model from `{prod_deployment_path}/trainedmodel.pkl` (via `diagnostics.model_predictions`)
    Writes:
        - `{output_model_path}/{output_filename}`

    Args:
        output_filename: Name of the PNG file to generate.

    Returns:
        The full path to the generated PNG.
    """
    project_dir = _get_project_dir()
    config = _load_config(project_dir)

    testdata_path = project_dir / config["test_data_path"] / "testdata.csv"
    if not testdata_path.exists():
        raise FileNotFoundError(f"Test dataset not found at {testdata_path}")

    output_dir = project_dir / config["output_model_path"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename

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

    logger.info("Confusion matrix plot written to %s", output_path)
    return output_path


def generate_pdf_report(
    pdf_filename: str = "report.pdf",
    confusion_matrix_filename: str = "confusionmatrix.png",
) -> Path:
    """
    Generate a PDF report (standout suggestion #1) bundling the confusion matrix,
    F1 score, summary statistics, missing-data %, timings, ingested files, and
    dependency status into a single file for stakeholders.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Image,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    project_dir = _get_project_dir()
    config = _load_config(project_dir)

    model_dir = project_dir / config["output_model_path"]
    ingested_dir = project_dir / config["output_folder_path"]
    model_dir.mkdir(parents=True, exist_ok=True)

    cm_path = generate_confusion_matrix_plot(output_filename=confusion_matrix_filename)
    pdf_path = model_dir / pdf_filename

    score_path = model_dir / "latestscore.txt"
    f1_text = score_path.read_text(encoding="utf-8").strip() if score_path.exists() else "n/a"

    ingested_path = ingested_dir / "ingestedfiles.txt"
    ingested = (
        ingested_path.read_text(encoding="utf-8").splitlines() if ingested_path.exists() else []
    )

    summary = diagnostics.dataframe_summary()
    missing = diagnostics.missing_data()

    # Avoid shelling out for timings inside the PDF generator — too slow.
    try:
        deps = diagnostics.outdated_packages_list()
    except Exception:  # pragma: no cover - defensive
        deps = []

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, title="Dynamic Risk Assessment — Model Report")
    story = []

    story.append(Paragraph("Dynamic Risk Assessment — Model Report", styles["Title"]))
    story.append(Paragraph(f"Generated from artifacts in <b>{model_dir}</b>.", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(f"<b>F1 score (production model):</b> {f1_text}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Confusion matrix (test set)", styles["Heading2"]))
    story.append(Image(str(cm_path), width=10 * cm, height=8 * cm))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Summary statistics (mean / median / mode per numeric column)", styles["Heading2"]))
    if summary:
        rows = [["Column", "Mean", "Median", "Mode"]]
        finaldata_path = ingested_dir / "finaldata.csv"
        if finaldata_path.exists():
            finaldata = pd.read_csv(finaldata_path)
            numeric_cols = list(finaldata.select_dtypes(include="number").columns)
        else:
            numeric_cols = [f"col_{i}" for i in range(len(summary) // 3)]
        for idx, col in enumerate(numeric_cols):
            base = idx * 3
            rows.append([col, f"{summary[base]:.4f}", f"{summary[base + 1]:.4f}", f"{summary[base + 2]:.4f}"])
        story.append(_make_table(rows, Table, TableStyle, colors))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Missing data (% per column)", styles["Heading2"]))
    finaldata_path = ingested_dir / "finaldata.csv"
    if finaldata_path.exists():
        columns = list(pd.read_csv(finaldata_path).columns)
    else:
        columns = [f"col_{i}" for i in range(len(missing))]
    rows = [["Column", "NA %"]] + [[c, f"{p * 100:.2f}%"] for c, p in zip(columns, missing)]
    story.append(_make_table(rows, Table, TableStyle, colors))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(f"Ingested files ({len(ingested)})", styles["Heading2"]))
    story.append(Paragraph(", ".join(ingested) if ingested else "<i>none</i>", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Dependency versions", styles["Heading2"]))
    dep_rows = [["Package", "Installed", "Latest"]]
    for dep in deps:
        dep_rows.append(
            [
                str(dep.get("name", "")),
                str(dep.get("installed_version", "") or "—"),
                str(dep.get("latest_version", "") or "—"),
            ]
        )
    if len(dep_rows) > 1:
        story.append(_make_table(dep_rows, Table, TableStyle, colors))
    else:
        story.append(Paragraph("<i>no dependency info</i>", styles["Normal"]))

    doc.build(story)
    logger.info("PDF report written to %s", pdf_path)
    return pdf_path


def _make_table(rows, Table, TableStyle, colors):
    table = Table(rows, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return table


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Generate the model reporting artifacts.")
    parser.add_argument(
        "--output",
        default="confusionmatrix.png",
        help="Filename for the confusion matrix PNG (saved under output_model_path).",
    )
    parser.add_argument(
        "--pdf",
        nargs="?",
        const="report.pdf",
        default=None,
        help="Also generate a PDF report. Optional filename (default: report.pdf).",
    )
    args = parser.parse_args()

    if args.pdf:
        generate_pdf_report(pdf_filename=args.pdf, confusion_matrix_filename=args.output)
    else:
        generate_confusion_matrix_plot(output_filename=args.output)


if __name__ == "__main__":
    main()
