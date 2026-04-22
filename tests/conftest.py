"""Root-level conftest: add src/ to sys.path for all root tests."""

import sys
from pathlib import Path

_src = str(Path(__file__).resolve().parents[1] / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)
