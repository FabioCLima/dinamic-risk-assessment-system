"""Tiny integration test for CLI scoring dispatch."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import portfolio_pipeline.cli as cli


def test_run_step_scoring_dispatches_native_module(monkeypatch) -> None:
    calls = []

    def _fake_run(cmd, cwd, check, env):
        calls.append((cmd, cwd, check, env))

        class _Result:
            returncode = 0

        return _Result()

    monkeypatch.setattr(cli.subprocess, "run", _fake_run)

    exit_code = cli.run_step("scoring")
    assert exit_code == 0
    assert calls, "Expected subprocess.run to be called"
    command = calls[0][0]
    assert command[:3] == [sys.executable, "-m", "dynamic_risk_assessment.scoring"]
