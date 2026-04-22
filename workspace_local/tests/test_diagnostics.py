"""Step 3 — diagnostics."""
import json
import subprocess
from types import SimpleNamespace

import pandas as pd
import pytest


def _bootstrap(patched_modules):
    """Run ingestion + training + deployment so diagnostics has real artifacts."""
    patched_modules["ingestion"].merge_multiple_dataframe()
    patched_modules["training"].train_model()
    patched_modules["scoring"].score_model()
    patched_modules["deployment"].store_model_into_pickle()


def test_model_predictions_returns_list_same_length(patched_modules):
    _bootstrap(patched_modules)
    diagnostics = patched_modules["diagnostics"]
    project_root = diagnostics._get_project_dir()

    df = pd.read_csv(project_root / "testdata" / "testdata.csv")
    preds = diagnostics.model_predictions(df)

    assert isinstance(preds, list)
    assert len(preds) == len(df)
    assert all(p in (0, 1) for p in preds)


def test_model_predictions_uses_deployed_model(patched_modules):
    # Train a model, deploy it, then overwrite the non-deployed one.
    # Predictions must still work (they read from prod_deployment_path).
    _bootstrap(patched_modules)
    diagnostics = patched_modules["diagnostics"]
    project_root = diagnostics._get_project_dir()

    (project_root / "models" / "trainedmodel.pkl").unlink()  # remove non-deployed copy

    df = pd.read_csv(project_root / "testdata" / "testdata.csv")
    preds = diagnostics.model_predictions(df)
    assert len(preds) == len(df)


def test_model_predictions_raises_when_missing_feature(patched_modules):
    _bootstrap(patched_modules)
    diagnostics = patched_modules["diagnostics"]

    bad_df = pd.DataFrame({"lastmonth_activity": [1], "lastyear_activity": [2]})
    with pytest.raises(ValueError):
        diagnostics.model_predictions(bad_df)


def test_dataframe_summary_three_stats_per_numeric_column(patched_modules):
    patched_modules["ingestion"].merge_multiple_dataframe()
    diagnostics = patched_modules["diagnostics"]

    summary = diagnostics.dataframe_summary()

    # Per rubric: mean, median, mode for each numeric column.
    # finaldata has 4 numeric cols → 4 * 3 = 12 values.
    assert isinstance(summary, list)
    assert len(summary) == 12
    assert all(isinstance(v, float) for v in summary)

    # Spot-check: first triple corresponds to lastmonth_activity (10, 20, ..., 80).
    mean_lastmonth, median_lastmonth, mode_lastmonth = summary[0:3]
    assert mean_lastmonth == pytest.approx(45.0)
    assert median_lastmonth == pytest.approx(45.0)
    # All values in the fixture are distinct, so mode == smallest value (pandas tiebreak).
    assert mode_lastmonth == pytest.approx(10.0)


def test_missing_data_returns_one_percent_per_column(patched_modules):
    patched_modules["ingestion"].merge_multiple_dataframe()
    diagnostics = patched_modules["diagnostics"]
    project_root = diagnostics._get_project_dir()

    result = diagnostics.missing_data()

    df = pd.read_csv(project_root / "ingesteddata" / "finaldata.csv")
    assert len(result) == len(df.columns)
    # Our fixtures have no NAs.
    assert all(p == 0.0 for p in result)


def test_missing_data_reports_non_zero_when_nas_present(patched_modules):
    patched_modules["ingestion"].merge_multiple_dataframe()
    diagnostics = patched_modules["diagnostics"]
    project_root = diagnostics._get_project_dir()

    finaldata = project_root / "ingesteddata" / "finaldata.csv"
    df = pd.read_csv(finaldata)
    df.loc[0, "lastmonth_activity"] = None
    df.to_csv(finaldata, index=False)

    percents = diagnostics.missing_data()
    idx = list(df.columns).index("lastmonth_activity")
    assert percents[idx] == pytest.approx(1.0 / len(df))


def test_execution_time_returns_two_positive_floats(monkeypatch, patched_modules):
    diagnostics = patched_modules["diagnostics"]

    # Fake subprocess.run so we don't shell out.
    monkeypatch.setattr(
        diagnostics.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )

    result = diagnostics.execution_time()
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(v, float) and v >= 0 for v in result)


def test_outdated_packages_list_shape(monkeypatch, patched_modules):
    diagnostics = patched_modules["diagnostics"]

    installed = json.dumps([{"name": "pandas", "version": "1.2.2"}, {"name": "scikit-learn", "version": "0.24.1"}])
    outdated = json.dumps([{"name": "pandas", "version": "1.2.2", "latest_version": "2.1.0"}])

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if "--outdated" in cmd:
            return SimpleNamespace(returncode=0, stdout=outdated, stderr="")
        return SimpleNamespace(returncode=0, stdout=installed, stderr="")

    monkeypatch.setattr(diagnostics.subprocess, "run", fake_run)

    table = diagnostics.outdated_packages_list()

    # requirements.txt fixture has 2 entries.
    assert len(table) == 2
    assert {row["name"] for row in table} == {"pandas", "scikit-learn"}
    pandas_row = next(r for r in table if r["name"] == "pandas")
    assert pandas_row["installed_version"] == "1.2.2"
    assert pandas_row["latest_version"] == "2.1.0"
    # sklearn is not in outdated list → latest falls back to installed.
    sklearn_row = next(r for r in table if r["name"] == "scikit-learn")
    assert sklearn_row["latest_version"] == "0.24.1"


@pytest.mark.slow
def test_execution_time_real_subprocess(patched_modules):
    """Uses real subprocess — takes a few seconds. Opt in with `-m slow`."""
    # Pre-ingest once so training has data.
    patched_modules["ingestion"].merge_multiple_dataframe()
    diagnostics = patched_modules["diagnostics"]

    # execution_time spawns `python ingestion.py` / `python training.py` in the
    # project root, so it must run against the REAL project (not tmp). Skip
    # unless we're OK with that. The fast test above covers the contract.
    pytest.skip("Covered by the mocked test; real subprocess path changes cwd state.")
