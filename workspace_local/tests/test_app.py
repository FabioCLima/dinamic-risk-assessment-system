"""Step 4 — Flask API endpoints."""
import json
from types import SimpleNamespace

import pytest


def _bootstrap(patched_modules):
    patched_modules["ingestion"].merge_multiple_dataframe()
    patched_modules["training"].train_model()
    patched_modules["scoring"].score_model()
    patched_modules["deployment"].store_model_into_pickle()


@pytest.fixture
def client(patched_modules):
    _bootstrap(patched_modules)
    app_module = patched_modules["app"]
    flask_app = app_module.create_app()
    flask_app.config.update(TESTING=True)
    return flask_app.test_client()


def test_prediction_endpoint_returns_200_and_list(client, patched_modules):
    project_root = patched_modules["app"]._get_project_dir()
    payload = {"filepath": str(project_root / "testdata" / "testdata.csv")}

    resp = client.post("/prediction", data=json.dumps(payload), content_type="application/json")

    assert resp.status_code == 200
    body = resp.get_json()
    assert "predictions" in body
    assert isinstance(body["predictions"], list)
    assert len(body["predictions"]) == 4  # matches fixture testdata size


def test_prediction_endpoint_returns_200_on_missing_filepath(client):
    resp = client.post("/prediction", data=json.dumps({}), content_type="application/json")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "error" in body


def test_prediction_endpoint_accepts_relative_path(client, patched_modules):
    """Relative paths must be resolved against the project root."""
    resp = client.post(
        "/prediction",
        data=json.dumps({"filepath": "testdata/testdata.csv"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert isinstance(resp.get_json()["predictions"], list)


def test_scoring_endpoint_returns_200_and_float(client):
    resp = client.get("/scoring")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "f1_score" in body
    assert isinstance(body["f1_score"], (float, int))


def test_summarystats_endpoint_returns_200_and_list(client):
    resp = client.get("/summarystats")
    assert resp.status_code == 200
    body = resp.get_json()
    assert isinstance(body["summary_statistics"], list)
    assert len(body["summary_statistics"]) == 12


def test_diagnostics_endpoint_returns_200_with_expected_keys(client, monkeypatch, patched_modules):
    diagnostics = patched_modules["diagnostics"]
    # Stub subprocess to keep this fast.
    monkeypatch.setattr(
        diagnostics.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="[]", stderr=""),
    )

    resp = client.get("/diagnostics")
    assert resp.status_code == 200
    body = resp.get_json()
    assert set(body.keys()) == {"timing_seconds", "missing_data_percent", "dependencies"}
    assert isinstance(body["timing_seconds"], list)
    assert len(body["timing_seconds"]) == 2
