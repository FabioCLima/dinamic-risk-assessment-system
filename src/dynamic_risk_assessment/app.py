import argparse
import logging
import os
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from flask import Flask, jsonify, request

from dynamic_risk_assessment import diagnostics, scoring
from dynamic_risk_assessment.config import repo_root

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "dynamic-risk-assessment"

    @app.route("/prediction", methods=["POST"])
    def prediction_endpoint():
        payload: Dict[str, Any] = request.get_json(silent=True) or {}
        filepath = payload.get("filepath") or payload.get("file_path")
        if not filepath:
            return jsonify({"error": "Missing required JSON field: filepath"}), 200
        csv_path = Path(str(filepath))
        if not csv_path.is_absolute():
            csv_path = repo_root() / "workspace_local" / csv_path
        if not csv_path.exists():
            return jsonify({"error": f"File not found: {csv_path}"}), 200
        return jsonify({"predictions": diagnostics.model_predictions(pd.read_csv(csv_path))}), 200

    @app.route("/scoring", methods=["GET"])
    def scoring_endpoint():
        return jsonify({"f1_score": scoring.score_model()}), 200

    @app.route("/summarystats", methods=["GET"])
    def summarystats_endpoint():
        return jsonify({"summary_statistics": diagnostics.dataframe_summary()}), 200

    @app.route("/diagnostics", methods=["GET"])
    def diagnostics_endpoint():
        return jsonify(
            {
                "timing_seconds": diagnostics.execution_time(),
                "missing_data_percent": diagnostics.missing_data(),
                "dependencies": diagnostics.outdated_packages_list(),
            }
        ), 200

    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Run the Dynamic Risk Assessment API.")
    parser.add_argument("--host", default=os.environ.get("APP_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("APP_PORT", "8000")))
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    create_app().run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == "__main__":
    main()
