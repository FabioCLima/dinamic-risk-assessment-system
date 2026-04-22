"""Tests for root-level portfolio CLI wrappers."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import portfolio_pipeline.cli as cli
from dynamic_risk_assessment.config import repo_root


def test_repo_root_points_to_project_root() -> None:
    root = repo_root()
    assert (root / "README.md").exists()
    assert (root / "workspace_local").exists()


def test_pipeline_modules_are_configured() -> None:
    assert cli.PIPELINE_ORDER
    assert all(name.startswith("dynamic_risk_assessment.") for name in cli.PIPELINE_ORDER)


def test_build_parser_accepts_run_all() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(["run-all"])
    assert args.command == "run-all"

