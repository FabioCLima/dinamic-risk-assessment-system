"""Step 4 — apicalls helper (does not start a real server)."""
import json
from pathlib import Path


def test_write_api_returns_creates_parent_and_valid_json(tmp_path):
    import apicalls

    target = tmp_path / "nested" / "apireturns.txt"
    payload = {"prediction": {"predictions": [0, 1]}, "scoring": {"f1_score": 0.5}}

    apicalls.write_api_returns(target, payload)

    assert target.exists()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded == payload


def test_call_api_endpoints_assembles_responses(monkeypatch):
    import apicalls

    monkeypatch.setattr(apicalls, "_post_json", lambda url, body: {"predictions": [1]})
    monkeypatch.setattr(apicalls, "_get_json", lambda url: {"stub": url})

    result = apicalls.call_api_endpoints(base_url="http://fake", prediction_filepath="x.csv")
    assert set(result.keys()) == {"prediction", "scoring", "summarystats", "diagnostics"}
    assert result["prediction"] == {"predictions": [1]}
    # Each GET records the URL it was called with.
    assert result["scoring"]["stub"].endswith("/scoring")
    assert result["summarystats"]["stub"].endswith("/summarystats")
    assert result["diagnostics"]["stub"].endswith("/diagnostics")


def test_is_port_open_returns_false_for_unused_port():
    import apicalls

    # 1 is reserved and will not be bound.
    assert apicalls._is_port_open("127.0.0.1", 1) is False
