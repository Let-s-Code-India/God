from pathlib import Path

import god_ai
from god_ai import aura


def test_package_version_and_exports():
    assert god_ai.__version__ == "1.1.1"
    for name in ["heal", "trace_exceptions", "auto_patch", "do", "exec_sandboxed", "eval_expr", "parse", "optimize", "benchmark", "cost_profiler"]:
        assert hasattr(aura, name), f"Missing aura export: {name}"


def test_aura_config_defaults_are_valid():
    config = aura.get_config() if hasattr(aura, "get_config") else None
    assert config is not None
    assert config.provider in {"openrouter", "local"}


def test_project_assets_are_present():
    root = Path(__file__).resolve().parents[1]
    assert (root / "assets" / "logo.svg").exists()
    assert (root / "scripts").exists()
