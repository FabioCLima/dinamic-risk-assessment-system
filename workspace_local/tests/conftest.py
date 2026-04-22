"""
Shared pytest fixtures for the Dynamic Risk Assessment pipeline.

Every pipeline module (ingestion, training, scoring, deployment, diagnostics,
reporting, app) resolves paths via a module-level `_get_project_dir()` helper.
Tests redirect that helper to a temporary project root so disk I/O is hermetic
and real artifacts are never touched.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
import pytest


REPO_DIR = Path(__file__).resolve().parents[1]
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))


TRAIN_ROWS = [
    ("aaaa", 10, 100, 5, 0),
    ("bbbb", 20, 200, 10, 1),
    ("cccc", 30, 300, 15, 0),
    ("dddd", 40, 400, 20, 1),
    ("eeee", 50, 500, 25, 0),
    ("ffff", 60, 600, 30, 1),
    ("gggg", 70, 700, 35, 0),
    ("hhhh", 80, 800, 40, 1),
]

TEST_ROWS = [
    ("iiii", 15, 150, 7, 0),
    ("jjjj", 25, 250, 12, 1),
    ("kkkk", 35, 350, 17, 0),
    ("llll", 45, 450, 22, 1),
]

COLUMNS = ["corporation", "lastmonth_activity", "lastyear_activity", "number_of_employees", "exited"]


def _write_csv(path: Path, rows: List[tuple]) -> None:
    pd.DataFrame(rows, columns=COLUMNS).to_csv(path, index=False)


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Synthesize a clean project root matching the layout declared in config.json."""
    config: Dict[str, str] = {
        "input_folder_path": "sourcedata",
        "output_folder_path": "ingesteddata",
        "test_data_path": "testdata",
        "output_model_path": "models",
        "prod_deployment_path": "production_deployment",
    }
    (tmp_path / "config.json").write_text(json.dumps(config), encoding="utf-8")

    for folder in config.values():
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)

    half = len(TRAIN_ROWS) // 2
    _write_csv(tmp_path / "sourcedata" / "dataset_a.csv", TRAIN_ROWS[:half])
    _write_csv(tmp_path / "sourcedata" / "dataset_b.csv", TRAIN_ROWS[half:])
    _write_csv(tmp_path / "testdata" / "testdata.csv", TEST_ROWS)

    # A minimal requirements.txt so diagnostics.outdated_packages_list() can parse something.
    (tmp_path / "requirements.txt").write_text("pandas==1.2.2\nscikit-learn==0.24.1\n", encoding="utf-8")

    return tmp_path


@pytest.fixture
def patched_modules(project_root: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Re-point every pipeline module's project dir helper at the temporary root.

    Returns a SimpleNamespace-like dict of the freshly imported modules.
    """
    import ingestion
    import training
    import scoring
    import deployment
    import diagnostics
    import reporting
    import app as app_module
    import fullprocess
    import archive_diagnostics
    import dbsetup

    modules = (
        ingestion,
        training,
        scoring,
        deployment,
        diagnostics,
        reporting,
        app_module,
        fullprocess,
        archive_diagnostics,
        dbsetup,
    )
    for module in modules:
        monkeypatch.setattr(module, "_get_project_dir", lambda root=project_root: root)

    return {
        "ingestion": ingestion,
        "training": training,
        "scoring": scoring,
        "deployment": deployment,
        "diagnostics": diagnostics,
        "reporting": reporting,
        "app": app_module,
        "fullprocess": fullprocess,
        "archive_diagnostics": archive_diagnostics,
        "dbsetup": dbsetup,
    }
