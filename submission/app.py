import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from flask import Flask, jsonify, request

import diagnostics
import scoring

logger = logging.getLogger(__name__)


def _get_project_dir() -> Path:
    return Path(__file__).resolve().parent


def _load_config(project_dir: Path) -> Dict[str, str]:
    with (project_dir / "config.json").open("r", encoding="utf-8") as file:
        return json.load(file)


def create_app() -> Flask:
    """
    Create the Flask app with the required endpoints:
    - POST /prediction
    - GET  /scoring
    - GET  /summarystats
    - GET  /diagnostics
    """
    app = Flask(__name__)
    app.secret_key = "dynamic-risk-assessment"

    @app.route("/prediction", methods=["POST"])
    def prediction_endpoint():
        """
        Request payload can be either:
        - JSON: {"filepath": "path/to/file.csv"}
        - JSON: {"file_path": "path/to/file.csv"}
        """
        payload: Dict[str, Any] = request.get_json(silent=True) or {}
        filepath = payload.get("filepath") or payload.get("file_path")
        if not filepath:
            return jsonify({"error": "Missing required JSON field: filepath"}), 200

        csv_path = Path(str(filepath))
        if not csv_path.is_absolute():
            csv_path = _get_project_dir() / csv_path

        if not csv_path.exists():
            return jsonify({"error": f"File not found: {csv_path}"}), 200

        df = pd.read_csv(csv_path)
        preds = diagnostics.model_predictions(df)
        return jsonify({"predictions": preds}), 200

    @app.route("/scoring", methods=["GET"])
    def scoring_endpoint():
        score = scoring.score_model()
        return jsonify({"f1_score": score}), 200

    @app.route("/summarystats", methods=["GET"])
    def summarystats_endpoint():
        summary = diagnostics.dataframe_summary()
        return jsonify({"summary_statistics": summary}), 200

    @app.route("/diagnostics", methods=["GET"])
    def diagnostics_endpoint():
        timings = diagnostics.execution_time()
        missing = diagnostics.missing_data()
        deps = diagnostics.outdated_packages_list()
        return (
            jsonify(
                {
                    "timing_seconds": timings,
                    "missing_data_percent": missing,
                    "dependencies": deps,
                }
            ),
            200,
        )

    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Run the Dynamic Risk Assessment API.")
    parser.add_argument("--host", default=os.environ.get("APP_HOST", "0.0.0.0"), help="Bind host.")
    parser.add_argument("--port", type=int, default=int(os.environ.get("APP_PORT", "8000")), help="Bind port.")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode.")
    args = parser.parse_args()

    project_dir = _get_project_dir()
    config = _load_config(project_dir)
    logger.info("Starting API with output_model_path=%s", config.get("output_model_path"))

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == "__main__":
    main()
