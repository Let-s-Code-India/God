"""Guarded natural-language-to-Python execution."""

from __future__ import annotations

import ast
import signal
import re
from typing import Any, Optional

from .config import get_config
from .llm import LLMClient, LLMError


class GhostExecutionError(RuntimeError):
    """Raised when generated code is invalid or uses blocked operations."""


_BLOCKED = {"__import__", "eval", "exec", "compile", "open", "input", "breakpoint", "system", "popen", "run"}


def do(instruction: str, context: Optional[dict[str, Any]] = None) -> Any:
    """Generate and execute a small Python expression in memory.

    Generated code must assign its result to ``result``. Imports, filesystem,
    process, and dynamic-code primitives are rejected before execution.
    """
    if not instruction.strip():
        raise ValueError("instruction cannot be empty")
    prompt = "Return only Python code in one fenced python block. Assign the final value to `result`.\nInstruction: " + instruction
    if context:
        prompt += "\nContext:\n" + repr(context)
    response = LLMClient().chat([{"role": "user", "content": prompt}], "You generate small, deterministic Python transformations.")
    match = re.search(r"```(?:python|py)?\s*\n?(.*?)```", response.text, re.IGNORECASE | re.DOTALL)
    code = (match.group(1) if match else response.text).strip()
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise GhostExecutionError(f"Generated Python is invalid: {exc}") from exc
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise GhostExecutionError("Ghost code cannot import modules")
        if isinstance(node, ast.Name) and node.id in _BLOCKED:
            raise GhostExecutionError(f"Ghost code uses blocked name: {node.id}")
        if isinstance(node, ast.Attribute) and node.attr in _BLOCKED:
            raise GhostExecutionError(f"Ghost code uses blocked attribute: {node.attr}")
    namespace = {"__builtins__": {"len": len, "str": str, "int": int, "float": float, "bool": bool, "list": list, "dict": dict, "sum": sum, "min": min, "max": max, "sorted": sorted, "range": range}, **(context or {})}
    previous_alarm = signal.getsignal(signal.SIGALRM) if hasattr(signal, "SIGALRM") else None
    try:
        if hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, _timeout)
            signal.alarm(get_config().ghost_timeout)
        exec(compile(tree, "<god_ai_ghost>", "exec"), namespace, namespace)
    except TimeoutError as exc:
        raise GhostExecutionError("Ghost code exceeded its execution time limit") from exc
    except Exception as exc:
        raise GhostExecutionError(f"Ghost code failed: {exc}") from exc
    finally:
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_alarm)
    if "result" not in namespace:
        raise GhostExecutionError("Generated code must assign a value to `result`")
    return namespace["result"]


def _timeout(signum: int, frame: Any) -> None:
    raise TimeoutError()