"""The developer-facing Aura SDK namespace."""

from __future__ import annotations

from .agent import agent
from .config import configure, get_config
from .extra import (
    auto_patch,
    benchmark,
    cost_profiler,
    eval_expr,
    exec_sandboxed,
    to_dataclass,
    to_pydantic,
    trace_exceptions,
)
from .ghost import GhostExecutionError, do
from .heal import heal
from .optimize import optimize
from .parse import parse
from .system import system

# Backward-compatible names used by the v1.0 contract and v1.1 extension suite.
__all__ = [
    "configure",
    "get_config",
    "heal",
    "trace_exceptions",
    "auto_patch",
    "do",
    "exec_sandboxed",
    "eval_expr",
    "parse",
    "to_pydantic",
    "to_dataclass",
    "optimize",
    "benchmark",
    "cost_profiler",
    "agent",
    "system",
    "GhostExecutionError",
]