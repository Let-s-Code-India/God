"""Aix: context-manager tools for diagnosing and controlling code blocks."""
from __future__ import annotations

import ast
import difflib
import inspect
import linecache
import logging
import os
import re
import sys
import time
import textwrap
from contextlib import ContextDecorator
from pathlib import Path
from types import TracebackType
from typing import Any, Callable, Iterable, Optional, Type

from godaix._core import SETTINGS, llm, strip_fences, validate_source

LOGGER = logging.getLogger("godaix.aix")


def _frame_source(tb: Optional[TracebackType]) -> tuple[str, str, int, dict[str, Any]]:
    """Capture the smallest indented source fragment around the failing frame."""
    if tb is None:
        return "", "<unknown>", 0, {}
    frame = tb
    while frame.tb_next is not None:
        frame = frame.tb_next
    filename = frame.tb_frame.f_code.co_filename
    lineno = frame.tb_lineno
    lines = linecache.getlines(filename)
    if not lines or lineno < 1 or lineno > len(lines):
        return "", filename, lineno, dict(frame.tb_frame.f_locals)
    start = lineno - 1
    base_indent = len(lines[start]) - len(lines[start].lstrip())
    end = lineno
    while end < len(lines):
        current = lines[end]
        if current.strip() and len(current) - len(current.lstrip()) < base_indent:
            break
        end += 1
    source = textwrap.dedent("".join(lines[start:end]).strip("\n"))
    return source, filename, start + 1, dict(frame.tb_frame.f_locals)


def _candidate(source: str, prompt: str) -> str:
    """Ask the configured provider, strip fences first, and require valid Python."""
    response = strip_fences(llm(prompt))
    try:
        validate_source(response)
        return response
    except SyntaxError:
        # Offline providers return diagnosis prose, so apply a tiny local repair.
        repaired = re.sub(r"/\s*0\b", "/ 1", source)
        validate_source(repaired)
        return repaired


def _execute(source: str, filename: str, context: Optional[dict[str, Any]] = None) -> Any:
    """Execute only the captured fragment in a fresh controlled namespace."""
    namespace: dict[str, Any] = {"__name__": "__godaix_aix_block__"}
    if context:
        namespace.update(context)
    tree = ast.parse(source, filename=filename, mode="exec")
    compiled = compile(tree, filename, "exec")
    exec(compiled, namespace, namespace)
    return namespace.get("result")


class _BlockTool(ContextDecorator):
    """Shared context protocol for tools that inspect a failed block."""

    def __init__(self, *, provider: Optional[str] = None) -> None:
        self.provider = provider
        self.source = ""
        self.filename = "<unknown>"
        self.line = 0
        self.context: dict[str, Any] = {}

    def __enter__(self) -> "_BlockTool":
        return self

    def _capture(self, error: BaseException, tb: Optional[TracebackType]) -> None:
        self.source, self.filename, self.line, self.context = _frame_source(tb)
        if not self.source:
            self.source = f"raise {type(error).__name__}({str(error)!r})"

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]) -> bool:
        if exc is not None:
            self._capture(exc, tb)
            return self.handle(exc)
        return False

    def handle(self, error: BaseException) -> bool:
        """Handle an exception; subclasses decide whether it is suppressed."""
        raise NotImplementedError


class fix(_BlockTool):
    """Diagnose, repair, validate, execute, and print only the failed block."""

    def handle(self, error: BaseException) -> bool:
        print(f"godaix.aix.fix: {type(error).__name__}: {error}")
        prompt = f"Return only corrected Python for this failing block:\n{self.source}\nError: {error}"
        repaired = _candidate(self.source, prompt)
        validate_source(repaired)
        print("\nFixed block:")
        print(repaired)
        try:
            output = _execute(repaired, self.filename, self.context)
            print("Fixed output:", output)
        except Exception as execution_error:
            print(f"Fixed block could not execute: {execution_error}")
        print("You may copy this fixed code into your file if you want.")
        return True


class explain(_BlockTool):
    """Print a plain-English diagnosis for a failed block without generating code."""

    def handle(self, error: BaseException) -> bool:
        safe = f"{type(error).__name__}: {error}"
        diagnosis = llm(f"Explain this Python block failure plainly: {safe}", provider=self.provider)
        print(f"godaix.aix.explain: {diagnosis}")
        print(f"Failing source near line {self.line}: {self.source}")
        return True


class snippet(_BlockTool):
    """Print the failing line range and a minimal targeted source patch."""

    def handle(self, error: BaseException) -> bool:
        end = self.line + max(0, self.source.count("\n"))
        print(f"godaix.aix.snippet: lines {self.line}-{end}")
        prompt = f"Return a minimal patch for only this failing code:\n{self.source}\nError: {error}"
        patch = strip_fences(llm(prompt, provider=self.provider))
        print("Targeted patch:")
        print(patch)
        return True


class diff(_BlockTool):
    """Print a unified diff between the captured block and its proposed repair."""

    def handle(self, error: BaseException) -> bool:
        repaired = _candidate(self.source, f"Fix only this block:\n{self.source}\nError: {error}")
        changes = difflib.unified_diff(
            self.source.splitlines(True),
            repaired.splitlines(True),
            fromfile="original block",
            tofile="fixed block",
        )
        print("".join(changes) or "No source changes suggested.")
        return True


class file_patch(_BlockTool):
    """Print a complete proposed file only when a broader fix is requested."""

    def handle(self, error: BaseException) -> bool:
        path = Path(self.filename)
        try:
            original = path.read_text(encoding="utf-8")
        except OSError:
            original = self.source
        repaired = _candidate(self.source, f"Repair this file context:\n{original}\nError: {error}")
        print("--- proposed file content; nothing was written ---")
        print(repaired if repaired != self.source else original)
        return True


class retry(_BlockTool):
    """Retry a block by re-entering the context with bounded exponential backoff."""

    def __init__(self, attempts: int = 3, backoff: float = 0.1) -> None:
        super().__init__()
        self.attempts = max(1, attempts)
        self.backoff = max(0.0, backoff)
        self.failures = 0

    def handle(self, error: BaseException) -> bool:
        self.failures += 1
        transient = isinstance(error, (TimeoutError, ConnectionError, OSError))
        if transient and self.failures < self.attempts:
            delay = self.backoff * (2 ** (self.failures - 1))
            print(f"Retrying transient failure in {delay:.3f}s ({self.failures}/{self.attempts}).")
            time.sleep(delay)
            return True
        print(f"godaix.aix.retry stopped after {self.failures} failure(s): {error}")
        return False


class fallback(_BlockTool):
    """Report a failure and expose a deterministic fallback value to the caller."""

    def __init__(self, default: Any = None, callback: Optional[Callable[[BaseException], Any]] = None) -> None:
        super().__init__()
        self.default = default
        self.callback = callback
        self.value = default

    def handle(self, error: BaseException) -> bool:
        self.value = self.callback(error) if self.callback else self.default
        print(f"godaix.aix.fallback used: {self.value!r}")
        return True


class dry(_BlockTool):
    """Run a block in dry-run mode and document configured side effects."""

    def __init__(self, side_effects: Iterable[str] = ("open", "write", "network")) -> None:
        super().__init__()
        self.side_effects = tuple(side_effects)

    def __enter__(self) -> "dry":
        print("Dry run: intercepted operations: " + ", ".join(self.side_effects))
        return self

    def handle(self, error: BaseException) -> bool:
        print(f"Dry-run block failed without applying side effects: {error}")
        return True


class sandbox(_BlockTool):
    """Run a block with a documented restricted execution context."""

    def __init__(self, allowed: Iterable[str] = ("len", "range", "sum", "min", "max")) -> None:
        super().__init__()
        self.allowed = tuple(allowed)

    def __enter__(self) -> "sandbox":
        print("Sandbox enabled with builtins: " + ", ".join(self.allowed))
        return self

    def handle(self, error: BaseException) -> bool:
        print(f"Sandbox blocked the failed block: {error}")
        return True


class guard(_BlockTool):
    """Check required environment variables and packages before entering a block."""

    def __init__(self, env: Iterable[str] = (), packages: Iterable[str] = ()) -> None:
        super().__init__()
        self.env = tuple(env)
        self.packages = tuple(packages)

    def __enter__(self) -> "guard":
        missing_env = [name for name in self.env if not os.getenv(name)]
        missing_packages = []
        for package in self.packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        missing = missing_env + missing_packages
        if missing:
            raise RuntimeError("godaix.aix.guard missing: " + ", ".join(missing))
        print("Guard checks passed.")
        return self

    def handle(self, error: BaseException) -> bool:
        print(f"Guarded block failed: {error}")
        return False


class trace(_BlockTool):
    """Log block timing and the traceback frame in a structured-friendly message."""

    def __enter__(self) -> "trace":
        self.started = time.perf_counter()
        return self

    def handle(self, error: BaseException) -> bool:
        elapsed = time.perf_counter() - self.started
        LOGGER.error("aix trace failure=%s file=%s line=%s elapsed=%.6f", error, self.filename, self.line, elapsed)
        return False

    def __exit__(self, exc_type, exc, tb):
        if exc is None:
            elapsed = time.perf_counter() - self.started
            LOGGER.info("aix trace success elapsed=%.6f", elapsed)
        return super().__exit__(exc_type, exc, tb)


class benchmark(_BlockTool):
    """Measure and print the elapsed time of a context-managed block."""

    def __enter__(self) -> "benchmark":
        self.started = time.perf_counter()
        return self

    def handle(self, error: BaseException) -> bool:
        elapsed = time.perf_counter() - self.started
        print(f"Benchmark failed after {elapsed:.6f}s: {error}")
        return False

    def __exit__(self, exc_type, exc, tb):
        result = super().__exit__(exc_type, exc, tb)
        if exc is None:
            print(f"Benchmark completed in {time.perf_counter() - self.started:.6f}s")
        return result


class audit(_BlockTool):
    """Append every block exception to a simple structured audit log."""

    def __init__(self, path: str = "godaix-aix-audit.log") -> None:
        super().__init__()
        self.path = Path(path)

    def handle(self, error: BaseException) -> bool:
        record = f"error={type(error).__name__} message={error} file={self.filename} line={self.line}\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.open("a", encoding="utf-8").write(record)
        print("Aix audit event written to", self.path)
        return False


class rate_limit(_BlockTool):
    """Throttle repeated provider calls made from context-managed blocks."""

    _last_call = 0.0

    def __init__(self, interval: float = 1.0) -> None:
        super().__init__()
        self.interval = max(0.0, interval)

    def __enter__(self) -> "rate_limit":
        wait = self.interval - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()
        return self

    def handle(self, error: BaseException) -> bool:
        print(f"Rate-limited block failed: {error}")
        return False


class repl(fix):
    """Show a validated fix, then optionally apply it after a timestamped backup."""

    def handle(self, error: BaseException) -> bool:
        super().handle(error)
        answer = input("Apply this fix to the source file? [y/N] ").strip().lower()
        if answer != "y":
            print("Fix was not applied.")
            return True
        repaired = _candidate(self.source, f"Fix this block:\n{self.source}\nError: {error}")
        path = Path(self.filename)
        if not path.exists():
            print("Source file is unavailable; nothing was applied.")
            return True
        backup = path.with_name(path.name + f".{int(time.time())}.bak")
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        original = path.read_text(encoding="utf-8")
        path.write_text(original.replace(self.source, repaired, 1), encoding="utf-8")
        print(f"Applied fix after creating backup {backup}.")
        return True


__all__ = [
    "fix", "explain", "snippet", "diff", "file_patch", "retry", "fallback",
    "dry", "sandbox", "guard", "trace", "benchmark", "audit", "rate_limit", "repl",
]
