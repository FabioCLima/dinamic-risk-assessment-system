"""Standout #3 — SQLite persistence layer."""
import json
import sqlite3


def test_init_db_creates_tables(project_root, monkeypatch):
    import dbsetup
    monkeypatch.setattr(dbsetup, "_get_project_dir", lambda: project_root)

    path = dbsetup.init_db()
    assert path.exists()

    with sqlite3.connect(path) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"ingestion_runs", "model_scores", "diagnostics_runs"} <= tables


def test_record_ingestion_and_score_persist(project_root, monkeypatch):
    import dbsetup
    monkeypatch.setattr(dbsetup, "_get_project_dir", lambda: project_root)

    dbsetup.init_db()
    dbsetup.record_ingestion(42, ["a.csv", "b.csv"])
    dbsetup.record_score(0.77, source="test")

    recent = dbsetup.fetch_recent_scores(limit=5)
    assert recent[0]["f1_score"] == 0.77
    assert recent[0]["source"] == "test"


def test_record_diagnostics_roundtrip(project_root, monkeypatch):
    import dbsetup
    monkeypatch.setattr(dbsetup, "_get_project_dir", lambda: project_root)

    dbsetup.init_db()
    dbsetup.record_diagnostics(
        ingestion_seconds=0.5,
        training_seconds=1.2,
        missing_percent=[0.0, 0.0],
        summary_values=[1.0, 2.0, 3.0],
        dependencies=[{"name": "pandas", "installed_version": "1.2.2", "latest_version": "2.0.0"}],
    )

    with sqlite3.connect(dbsetup.resolve_db_path()) as conn:
        row = conn.execute(
            "SELECT ingestion_seconds, training_seconds, summary_json FROM diagnostics_runs"
        ).fetchone()

    assert row[0] == 0.5
    assert row[1] == 1.2
    assert json.loads(row[2]) == [1.0, 2.0, 3.0]
