"""Shared config and path helpers for the portfolio package."""

import json
import os
from pathlib import Path
from typing import Dict


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config() -> Dict[str, str]:
    config_env = os.environ.get("DRAS_CONFIG")
    if config_env:
        config_path = Path(config_env)
        if not config_path.is_absolute():
            config_path = repo_root() / config_path
    else:
        default_path = repo_root() / "config.json"
        config_path = default_path if default_path.exists() else repo_root() / "configs" / "config.dev.json"

    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def resolve_path(config_value: str) -> Path:
    path = Path(config_value)
    if not path.is_absolute():
        path = repo_root() / path
    return path

