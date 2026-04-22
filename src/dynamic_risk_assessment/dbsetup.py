import argparse
import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence

from dynamic_risk_assessment.config import load_config, repo_root, resolve_path

logger = logging.getLogger(__name__)
DEFAULT_DB_NAME = "pipeline_history.sqlite"


def resolve_db_path(db_filename: str = DEFAULT_DB_NAME) -> Path:
    config = load_config()
    output_dir = resolve_path(config["output_folder_path"])
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / db_filename


def connect(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = db_path or resolve_db_path()
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Optional[Path] = None) -> Path:
    path = db_path or resolve_db_path()
    with connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS ingestion_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_ts TEXT NOT NULL DEFAULT (datetime('now')),
                row_count INTEGER NOT NULL,
                filenames TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS model_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_ts TEXT NOT NULL DEFAULT (datetime('now')),
                f1_score REAL NOT NULL,
                source TEXT NOT NULL DEFAULT 'scoring'
            );
            CREATE TABLE IF NOT EXISTS diagnostics_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_ts TEXT NOT NULL DEFAULT (datetime('now')),
                ingestion_seconds REAL,
                training_seconds REAL,
                missing_percent_json TEXT,
                summary_json TEXT,
                dependencies_json TEXT
            );
            """
        )
    return path


def record_ingestion(row_count: int, filenames: Sequence[str], db_path: Optional[Path] = None) -> None:
    with connect(db_path or resolve_db_path()) as conn:
        conn.execute(
            "INSERT INTO ingestion_runs (row_count, filenames) VALUES (?, ?)",
            (int(row_count), json.dumps(list(filenames))),
        )


def record_score(f1_score: float, source: str = "scoring", db_path: Optional[Path] = None) -> None:
    with connect(db_path or resolve_db_path()) as conn:
        conn.execute(
            "INSERT INTO model_scores (f1_score, source) VALUES (?, ?)",
            (float(f1_score), source),
        )


def record_diagnostics(
    ingestion_seconds: Optional[float],
    training_seconds: Optional[float],
    missing_percent: Iterable[float],
    summary_values: Iterable[float],
    dependencies: Iterable[Dict[str, Any]],
    db_path: Optional[Path] = None,
) -> None:
    with connect(db_path or resolve_db_path()) as conn:
        conn.execute(
            """
            INSERT INTO diagnostics_runs (
                ingestion_seconds, training_seconds,
                missing_percent_json, summary_json, dependencies_json
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                None if ingestion_seconds is None else float(ingestion_seconds),
                None if training_seconds is None else float(training_seconds),
                json.dumps(list(missing_percent)),
                json.dumps(list(summary_values)),
                json.dumps(list(dependencies)),
            ),
        )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Initialize the pipeline history SQLite DB.")
    parser.add_argument("--db", type=Path, default=None, help="Override DB path.")
    args = parser.parse_args()
    path = init_db(db_path=args.db)
    logger.info("DB ready at %s", path)


if __name__ == "__main__":
    main()
