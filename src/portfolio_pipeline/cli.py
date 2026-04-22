"""Root-level CLI for running the portfolio-native pipeline."""

import argparse
import os
import subprocess
import sys

from dynamic_risk_assessment.config import repo_root


PIPELINE_ORDER = [
    "dynamic_risk_assessment.ingestion",
    "dynamic_risk_assessment.training",
    "dynamic_risk_assessment.scoring",
    "dynamic_risk_assessment.deployment",
    "dynamic_risk_assessment.reporting",
    "dynamic_risk_assessment.apicalls",
    "dynamic_risk_assessment.fullprocess",
]


def _run_module(module_name: str) -> int:
    root = repo_root()
    src_path = str(root / "src")
    existing = os.environ.get("PYTHONPATH", "")
    pythonpath = src_path if not existing else f"{src_path}:{existing}"
    cmd = [sys.executable, "-m", module_name]
    completed = subprocess.run(cmd, cwd=str(root), check=False, env={**os.environ, "PYTHONPATH": pythonpath})
    return int(completed.returncode)


def run_pipeline() -> int:
    for module_name in PIPELINE_ORDER:
        code = _run_module(module_name)
        if code != 0:
            return code
    return 0


def run_step(step: str) -> int:
    valid_steps = {name.split(".")[-1]: name for name in PIPELINE_ORDER}
    if step not in valid_steps:
        raise ValueError(f"Invalid step '{step}'. Choose from: {', '.join(valid_steps)}")
    return _run_module(valid_steps[step])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dras",
        description="Run Dynamic Risk Assessment System commands from repository root.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run-all", help="Run the full pipeline in sequence.")

    run_step_parser = subparsers.add_parser("run-step", help="Run a single pipeline step.")
    run_step_parser.add_argument(
        "--name",
        required=True,
        choices=[name.split(".")[-1] for name in PIPELINE_ORDER],
        help="Pipeline step name.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run-all":
        return run_pipeline()
    if args.command == "run-step":
        return run_step(args.name)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
