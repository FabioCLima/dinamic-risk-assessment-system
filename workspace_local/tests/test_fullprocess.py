"""Step 5 — orchestration (fullprocess.py)."""
from pathlib import Path

import pytest


def _deploy_initial_model(patched_modules):
    """Run the pipeline once so production_deployment has baseline artifacts."""
    patched_modules["ingestion"].merge_multiple_dataframe()
    patched_modules["training"].train_model()
    patched_modules["scoring"].score_model()
    patched_modules["deployment"].store_model_into_pickle()


def _drop_new_csv(project_root: Path, name: str = "newbatch.csv") -> None:
    import pandas as pd

    columns = ["corporation", "lastmonth_activity", "lastyear_activity", "number_of_employees", "exited"]
    pd.DataFrame(
        [("zzzz", 99, 999, 50, 1), ("yyyy", 88, 888, 60, 0)],
        columns=columns,
    ).to_csv(project_root / "sourcedata" / name, index=False)


@pytest.fixture
def stubbed_api(monkeypatch, patched_modules):
    """Replace API startup + calls with no-ops so fullprocess stays fast."""
    fullprocess = patched_modules["fullprocess"]
    apicalls = fullprocess.apicalls
    monkeypatch.setattr(fullprocess, "_start_api_if_needed", lambda *a, **k: None)
    monkeypatch.setattr(fullprocess, "_stop_api", lambda *a, **k: None)
    monkeypatch.setattr(apicalls, "call_api_endpoints", lambda **k: {"stub": True})
    return fullprocess


def test_no_new_data_short_circuits(patched_modules, stubbed_api):
    _deploy_initial_model(patched_modules)
    fullprocess = stubbed_api
    project_root = fullprocess._get_project_dir()

    fullprocess.run_full_process()

    assert not (project_root / "models" / "apireturns2.txt").exists()
    assert not (project_root / "models" / "confusionmatrix2.png").exists()


def test_new_data_and_better_model_triggers_redeploy(monkeypatch, patched_modules, stubbed_api):
    _deploy_initial_model(patched_modules)
    fullprocess = stubbed_api
    project_root = fullprocess._get_project_dir()

    _drop_new_csv(project_root)

    # Force a deterministic "better" candidate score to isolate the deploy gate under test.
    monkeypatch.setattr(fullprocess.scoring, "score_model", lambda: 0.9)
    monkeypatch.setattr(fullprocess, "_read_deployed_score", lambda _p: 0.5)

    fullprocess.run_full_process()

    assert (project_root / "models" / "confusionmatrix2.png").exists()
    assert (project_root / "models" / "apireturns2.txt").exists()

    prod_dir = project_root / "production_deployment"
    deployed_ingested = (prod_dir / "ingestedfiles.txt").read_text()
    assert "newbatch.csv" in deployed_ingested


def test_new_data_but_worse_model_skips_deploy(monkeypatch, patched_modules, stubbed_api):
    _deploy_initial_model(patched_modules)
    fullprocess = stubbed_api
    project_root = fullprocess._get_project_dir()

    _drop_new_csv(project_root)

    # Candidate is strictly worse than deployed → must not redeploy.
    monkeypatch.setattr(fullprocess.scoring, "score_model", lambda: 0.3)
    monkeypatch.setattr(fullprocess, "_read_deployed_score", lambda _p: 0.8)

    fullprocess.run_full_process()

    assert not (project_root / "models" / "confusionmatrix2.png").exists()
    assert not (project_root / "models" / "apireturns2.txt").exists()

    prod_dir = project_root / "production_deployment"
    deployed_ingested = (prod_dir / "ingestedfiles.txt").read_text()
    assert "newbatch.csv" not in deployed_ingested


def test_new_data_but_equal_model_skips_deploy(monkeypatch, patched_modules, stubbed_api):
    _deploy_initial_model(patched_modules)
    fullprocess = stubbed_api
    project_root = fullprocess._get_project_dir()

    _drop_new_csv(project_root)

    # Equal score must NOT trigger a redeploy — gate is strict inequality.
    monkeypatch.setattr(fullprocess.scoring, "score_model", lambda: 0.7)
    monkeypatch.setattr(fullprocess, "_read_deployed_score", lambda _p: 0.7)

    fullprocess.run_full_process()

    assert not (project_root / "models" / "apireturns2.txt").exists()


def test_initial_deployment_when_no_deployed_score(patched_modules, stubbed_api):
    """If production has no latestscore.txt, the first run with new data must deploy."""
    fullprocess = stubbed_api
    project_root = fullprocess._get_project_dir()

    # Fresh sourcedata (existing fixture files are "new" — nothing has been ingested yet).
    # prod_deployment/ has no latestscore.txt, so `_read_deployed_score` returns None
    # and the "initial deployment" branch must fire.
    fullprocess.run_full_process()

    assert (project_root / "models" / "apireturns2.txt").exists()
    assert (project_root / "production_deployment" / "latestscore.txt").exists()


def test_missing_input_folder_raises(patched_modules, stubbed_api):
    fullprocess = stubbed_api
    project_root = fullprocess._get_project_dir()

    import shutil

    shutil.rmtree(project_root / "sourcedata")

    with pytest.raises(NotADirectoryError):
        fullprocess.run_full_process()


def test_cronjob_txt_is_well_formed():
    cron = Path(__file__).resolve().parents[1] / "cronjob.txt"
    content = cron.read_text(encoding="utf-8").strip()
    assert content, "cronjob.txt must not be empty"
    assert content.startswith("*/10 ")
    assert "fullprocess.py" in content
