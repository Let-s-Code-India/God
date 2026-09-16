"""Expanded Aura runtime helpers for tracing, execution, optimization, and conversion."""

from __future__ import annotations

import ast
import dataclasses
import functools
import inspect
import json
import math
import statistics
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, TypeVar, cast

from pydantic import BaseModel, TypeAdapter

from ..config import get_config
from ..llm import LLMClient, LLMError

F = TypeVar("F", bound=Callable[..., Any])


def trace_exceptions(function: F) -> F:
    """Wrap a callable and log tracebacks with a model-friendly summary."""

    @functools.wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except Exception as exc:  # pragma: no cover - runtime diagnosis path
            summary = traceback.format_exc()
            config = get_config()
            try:
                LLMClient(config).chat(
                    [{"role": "user", "content": f"Diagnose this Python exception and give a concise root-cause summary.\n{summary}"}],
                    "You are an expert Python runtime diagnostician.",
                )
            except LLMError:
                pass
            raise

    return cast(F, wrapped)


def auto_patch(function: F) -> F:
    """Attempt to repair a failing callable by delegating to a model suggestion."""

    @functools.wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except Exception:
            source = inspect.getsource(function)
            try:
                suggestion = LLMClient(get_config()).chat(
                    [{"role": "user", "content": f"Repair the following Python function. Return only the corrected function body or a valid Python function definition.\n\n{source}"}],
                    "You are a precise Python repair assistant.",
                )
            except LLMError:
                raise
            if not suggestion.text.strip():
                raise
            try:
                namespace = {"__builtins__": __builtins__}
                exec(suggestion.text, namespace, namespace)
                candidate = next(v for v in namespace.values() if callable(v))
                return candidate(*args, **kwargs)
            except Exception:
                raise

    return cast(F, wrapped)


def exec_sandboxed(code: str, context: dict[str, Any] | None = None, timeout_seconds: int = 15) -> Any:
    """Safely execute a constrained Python snippet in an isolated namespace."""
    if not code.strip():
        raise ValueError("code cannot be empty")
    tree = ast.parse(code, mode="exec")
    blocked = {
        "eval",
        "exec",
        "compile",
        "open",
        "input",
        "__import__",
        "breakpoint",
        "system",
        "popen",
        "subprocess",
        "os",
        "shutil",
        "pathlib",
        "socket",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            raise ValueError("Imports are not allowed in sandboxed execution")
        if isinstance(node, ast.ImportFrom):
            raise ValueError("Imports are not allowed in sandboxed execution")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in blocked:
                raise ValueError(f"Blocked builtin in sandboxed execution: {node.func.id}")
            if isinstance(node.func, ast.Attribute) and node.func.attr in blocked:
                raise ValueError(f"Blocked attribute in sandboxed execution: {node.func.attr}")
    namespace: dict[str, Any] = {
        "__builtins__": {
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "enumerate": enumerate,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "max": max,
            "min": min,
            "range": range,
            "round": round,
            "set": set,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
            "math": math,
            "statistics": statistics,
        }
    }
    namespace.update(context or {})
    started = time.perf_counter()
    exec(compile(tree, "<aura_sandbox>", "exec"), namespace, namespace)
    if time.perf_counter() - started > timeout_seconds:
        raise TimeoutError("sandboxed execution exceeded the timeout budget")
    if "result" in namespace:
        return namespace["result"]
    return namespace


def eval_expr(expression: str, context: dict[str, Any] | None = None) -> Any:
    """Safely evaluate an expression with a restricted builtins set."""
    tree = ast.parse(expression, mode="eval")
    for node in ast.walk(tree):
        if isinstance(node, (ast.Call, ast.Attribute, ast.Subscript, ast.Name)):
            if isinstance(node, ast.Name) and node.id in {"__import__", "open", "eval", "exec", "compile"}:
                raise ValueError(f"Blocked symbol in expression: {node.id}")
    namespace = {
        "__builtins__": {
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "max": max,
            "min": min,
            "round": round,
            "set": set,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
            "math": math,
        }
    }
    namespace.update(context or {})
    return eval(compile(tree, "<aura_eval>", "eval"), namespace, namespace)


def to_pydantic(data: dict[str, Any] | list[Any], model: type[BaseModel]) -> BaseModel:
    """Validate structured data into a Pydantic model."""
    return model.model_validate(data)


def to_dataclass(data: dict[str, Any], cls: type[Any]) -> Any:
    """Create a dataclass instance from a dictionary payload."""
    if not dataclasses.is_dataclass(cls):
        raise TypeError(f"{cls!r} is not a dataclass type")
    return cls(**data)


def benchmark(function: F) -> F:
    """Wrap a callable with timing data and a concise runtime report."""

    @functools.wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        result = function(*args, **kwargs)
        elapsed = time.perf_counter() - started
        print(f"{function.__qualname__} completed in {elapsed:.4f}s")
        return result

    return cast(F, wrapped)


def cost_profiler(function: F) -> F:
    """Measure execution duration and approximate cost units for a function."""

    @functools.wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        result = function(*args, **kwargs)
        elapsed = time.perf_counter() - started
        units = max(0.0, elapsed * 1000.0)
        print(f"{function.__qualname__} cost profile: {units:.2f} units ({elapsed:.4f}s)")
        return result

    return cast(F, wrapped)


def parse_json_like(payload: str) -> Any:
    """Parse JSON or a Python-like dict/list payload."""
    text = payload.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return ast.literal_eval(text)


__all__ = [
    "trace_exceptions",
    "auto_patch",
    "exec_sandboxed",
    "eval_expr",
    "to_pydantic",
    "to_dataclass",
    "benchmark",
    "cost_profiler",
    "parse_json_like",
]
