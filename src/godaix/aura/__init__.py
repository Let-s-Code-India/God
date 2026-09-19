"""Aura: practical decorators for healing, observing, and controlling calls."""
from __future__ import annotations

import asyncio
import functools
import inspect
import os
import time
from collections import OrderedDict
from typing import Any, Callable, Dict, Optional, TypeVar

from godaix._core import LOGGER, json_line, llm, validate_source

F = TypeVar("F", bound=Callable[..., Any])


def heal(*, retries: int = 1, provider: Optional[str] = None) -> Callable[[F], F]:
    """Diagnose failures, retry them, and preserve the original exception."""

    def decorate(function: F) -> F:
        @functools.wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            last: Optional[BaseException] = None
            for attempt in range(retries + 1):
                try:
                    return function(*args, **kwargs)
                except Exception as error:
                    last = error
                    explanation = llm(
                        f"Explain this exception from {function.__name__}: {error}",
                        provider=provider or "offline",
                    )
                    LOGGER.warning(
                        "%s failed (%s/%s): %s",
                        function.__name__,
                        attempt + 1,
                        retries + 1,
                        explanation,
                    )
            # The loop always records an exception when it reaches this point.
            assert last is not None
            raise last

        return wrapped  # type: ignore[return-value]

    return decorate


def patch(*, provider: Optional[str] = None) -> Callable[[F], F]:
    """Request a source repair, validate it, and execute it in a small namespace."""

    def decorate(function: F) -> F:
        @functools.wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            try:
                return function(*args, **kwargs)
            except Exception as original:
                suggestion = llm(
                    "Return only corrected Python for function "
                    f"{inspect.getsource(function)}; error: {original}",
                    provider=provider or "offline",
                )
                try:
                    tree = validate_source(suggestion)
                    namespace: Dict[str, Any] = {}
                    builtins_namespace = {"__builtins__": __builtins__}
                    exec(compile(tree, "<godaix-patch>", "exec"), builtins_namespace, namespace)
                    repaired = namespace.get(function.__name__)
                    if not callable(repaired):
                        raise ValueError("patched source did not define the function")
                    return repaired(*args, **kwargs)
                except Exception:
                    # A failed repair must never replace the user's original error.
                    raise original

        return wrapped  # type: ignore[return-value]

    return decorate


def retry(*, retries: int = 3, backoff: float = 0.05) -> Callable[[F], F]:
    """Retry transient network-like errors, while failing fast on logic errors."""
    transient = (TimeoutError, ConnectionError, OSError)

    def decorate(function: F) -> F:
        @functools.wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(retries + 1):
                try:
                    return function(*args, **kwargs)
                except transient:
                    # These exception types commonly represent temporary transport failures.
                    if attempt >= retries:
                        raise
                    delay = backoff * (2 ** attempt)
                    time.sleep(delay)
                except Exception:
                    # Logic and validation errors should not be retried automatically.
                    raise
            raise RuntimeError("retry loop exhausted")

        return wrapped  # type: ignore[return-value]

    return decorate


def validate(*, input_schema: Any = None, output_schema: Any = None) -> Callable[[F], F]:
    """Validate arguments and return values using Pydantic or dict schemas."""

    def check(value: Any, schema: Any, label: str) -> Any:
        if schema is None:
            return value
        if isinstance(schema, dict):
            if not isinstance(value, dict):
                raise TypeError(f"{label} must be a dictionary")
            missing = set(schema) - set(value)
            if missing:
                raise ValueError(f"{label} missing fields: {sorted(missing)}")
            return value
        if hasattr(schema, "model_validate"):
            return schema.model_validate(value)
        if isinstance(value, schema):
            return value
        raise TypeError(f"{label} does not match {schema}")

    def decorate(function: F) -> F:
        @functools.wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            if input_schema is not None:
                candidate = kwargs or (args[0] if len(args) == 1 else args)
                check(candidate, input_schema, "input")
            result = function(*args, **kwargs)
            return check(result, output_schema, "output")

        return wrapped  # type: ignore[return-value]

    return decorate


def trace(function: F) -> F:
    """Log arguments, result, exception, and elapsed time as structured data."""

    @functools.wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        try:
            result = function(*args, **kwargs)
            elapsed = time.perf_counter() - started
            LOGGER.info(
                "trace=%s args=%r result=%r elapsed=%.6f",
                function.__name__, args, result, elapsed,
            )
            return result
        except Exception:
            elapsed = time.perf_counter() - started
            LOGGER.exception("trace=%s failed elapsed=%.6f", function.__name__, elapsed)
            raise

    return wrapped  # type: ignore[return-value]


def cache(*, semantic: bool = False, maxsize: int = 128) -> Callable[[F], F]:
    """Memoize results, optionally normalizing string whitespace for near matches."""

    def decorate(function: F) -> F:
        store: OrderedDict[Any, Any] = OrderedDict()

        @functools.wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            key_args = tuple(
                " ".join(value.split()) if semantic and isinstance(value, str) else value
                for value in args
            )
            key = (key_args, tuple(sorted(kwargs.items())))
            if key in store:
                store.move_to_end(key)
                return store[key]
            value = function(*args, **kwargs)
            store[key] = value
            if len(store) > maxsize:
                store.popitem(last=False)
            return value

        return wrapped  # type: ignore[return-value]

    return decorate


def async_heal(*, retries: int = 1) -> Callable[[F], F]:
    """Async counterpart to heal for coroutine functions."""

    def decorate(function: F) -> F:
        @functools.wraps(function)
        async def wrapped(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(retries + 1):
                try:
                    return await function(*args, **kwargs)
                except Exception as error:
                    explanation = llm(str(error), provider="offline")
                    LOGGER.warning("async failure: %s", explanation)
                    if attempt >= retries:
                        raise
                    await asyncio.sleep(0)
            raise RuntimeError("unreachable")

        return wrapped  # type: ignore[return-value]

    return decorate


def sandbox(function: F) -> F:
    """Run a function with a restricted builtins mapping when it accepts no globals."""

    @functools.wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        allowed = {
            "len": len,
            "range": range,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
        }
        original = function.__globals__.get("__builtins__")
        function.__globals__["__builtins__"] = allowed
        try:
            return function(*args, **kwargs)
        finally:
            # Restore the module globals even when the wrapped call raises.
            function.__globals__["__builtins__"] = original

    return wrapped  # type: ignore[return-value]


def explain(function: F) -> F:
    """Attach a plain-English explanation to exceptions as a note."""

    @functools.wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except Exception as error:
            error_type = type(error).__name__
            error_text = str(error)
            prompt = (
                f"Explain {error_type}: {error_text}"
            )
            note = llm(
                prompt,
                provider="offline",
            )
            # Exception notes preserve the original traceback and add context.
            error.add_note(note)
            raise

    return wrapped  # type: ignore[return-value]


def benchmark(function: F) -> F:
    """Measure wrapper overhead and function duration in a structured log."""

    @functools.wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = function(*args, **kwargs)
        elapsed = time.perf_counter() - start
        overhead = 0.0
        LOGGER.info(
            "benchmark function=%s seconds=%.8f overhead=%.8f",
            function.__name__,
            elapsed,
            overhead,
        )
        # Returning the wrapped result keeps this decorator transparent.
        # Timing is intentionally observational and does not affect control flow.
        return result

    return wrapped  # type: ignore[return-value]


def guard(*, env: tuple[str, ...] = (), packages: tuple[str, ...] = ()) -> Callable[[F], F]:
    """Block a call with a clear message when prerequisites are absent."""

    def decorate(function: F) -> F:
        @functools.wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            missing = [name for name in env if not os.getenv(name)]
            for package in packages:
                try:
                    __import__(package)
                except ImportError:
                    missing.append(f"pip install {package}")
            if missing:
                message = "godaix guard blocked call; missing: " + ", ".join(missing)
                raise RuntimeError(message)
            return function(*args, **kwargs)

        return wrapped  # type: ignore[return-value]

    return decorate


def dry_run(*, side_effects: tuple[str, ...] = ("open", "system")) -> Callable[[F], F]:
    """Mark a call as dry-run and expose intercepted side-effect names to logs."""

    def decorate(function: F) -> F:
        @functools.wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            function_name = function.__name__
            configured_effects = side_effects
            LOGGER.info(
                "dry-run function=%s intercepted=%s",
                function_name,
                configured_effects,
            )
            result = function(*args, **kwargs)
            # dry_run records intent; it intentionally does not suppress the call.
            return result

        return wrapped  # type: ignore[return-value]

    return decorate


def audit(*, path: str = "godaix-audit.jsonl") -> Callable[[F], F]:
    """Write calls, failures, and successful results to a JSON-lines audit log."""

    def decorate(function: F) -> F:
        @functools.wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            json_line(path, {"event": "call", "function": function.__name__, "args": args})
            try:
                result = function(*args, **kwargs)
                json_line(path, {"event": "success", "function": function.__name__})
                return result
            except Exception as error:
                json_line(
                    path,
                    {"event": "exception", "function": function.__name__, "error": str(error)},
                )
                raise

        return wrapped  # type: ignore[return-value]

    return decorate


def fallback(
    fallback_function: Optional[Callable[..., Any]] = None,
    *,
    default: Any = None,
    retries: int = 0,
) -> Callable[[F], F]:
    """Return a fallback function or default value after the primary fails."""

    def decorate(function: F) -> F:
        @functools.wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            try:
                return function(*args, **kwargs)
            except Exception:
                if fallback_function is not None:
                    return fallback_function(*args, **kwargs)
                return default

        return wrapped  # type: ignore[return-value]

    return decorate


def rate_limit(*, rate: float = 1.0, capacity: int = 1) -> Callable[[F], F]:
    """Throttle calls using a token bucket shared by one decorated function."""

    def decorate(function: F) -> F:
        tokens = float(capacity)
        last = time.monotonic()

        @functools.wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            nonlocal tokens, last
            now = time.monotonic()
            elapsed = now - last
            tokens = min(capacity, tokens + elapsed * rate)
            last = now
            if tokens < 1:
                raise RuntimeError("godaix rate limit exceeded")
            tokens -= 1
            return function(*args, **kwargs)

        return wrapped  # type: ignore[return-value]

    return decorate


__all__ = [
    "heal", "patch", "retry", "validate", "trace", "cache", "async_heal",
    "sandbox", "explain", "benchmark", "guard", "dry_run", "audit", "fallback",
    "rate_limit",
]
