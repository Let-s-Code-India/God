"""Aether: bounded resilience, offline operation, and performance utilities."""
from __future__ import annotations

import functools
import hashlib
import json
import os
import socket
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from contextlib import ContextDecorator
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from godaix._core import LOGGER, SETTINGS


class timeout(ContextDecorator):
    """Enforce a deadline for a callable or context-managed operation."""

    def __init__(self, seconds: Optional[float] = None):
        self.seconds = seconds or SETTINGS.timeout

    def __enter__(self):
        self.started = time.monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = time.monotonic() - self.started
        if elapsed > self.seconds and exc is None:
            raise TimeoutError(f"godaix operation exceeded {self.seconds}s")
        return False

    def __call__(self, function):
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(function, *args, **kwargs)
            try:
                return future.result(timeout=self.seconds)
            except FutureTimeout as error:
                future.cancel()
                raise TimeoutError(
                    f"godaix operation exceeded {self.seconds}s"
                ) from error
            finally:
                executor.shutdown(wait=False, cancel_futures=True)

        return wrapped


class circuit_breaker:
    """Open a provider circuit after consecutive failures for a cooldown."""

    _states: Dict[str, Dict[str, float]] = {}

    def __init__(
        self,
        provider: str = "default",
        threshold: Optional[int] = None,
        cooldown: float = 30,
    ):
        self.provider = provider
        self.threshold = threshold or SETTINGS.circuit_threshold
        self.cooldown = cooldown

    def call(self, function: Callable[..., Any], *args, **kwargs):
        state = self._states.setdefault(
            self.provider,
            {"failures": 0, "opened": 0},
        )
        opened_at = state["opened"]
        if opened_at and time.monotonic() - opened_at < self.cooldown:
            raise RuntimeError(f"circuit open for provider {self.provider}")
        try:
            result = function(*args, **kwargs)
            state.update(failures=0, opened=0)
            return result
        except Exception:
            state["failures"] += 1
            if state["failures"] >= self.threshold:
                state["opened"] = time.monotonic()
            raise


class offline_queue:
    """Persist failed JSON requests in SQLite for later replay."""

    def __init__(self, path: str = "godaix-queue.sqlite3"):
        self.path = path
        connection = sqlite3.connect(path)
        connection.execute(
            "create table if not exists requests "
            "(id integer primary key, payload text not null, created real not null)"
        )
        connection.commit()
        connection.close()

    def put(self, payload: Dict[str, Any]) -> int:
        connection = sqlite3.connect(self.path)
        cursor = connection.execute(
            "insert into requests(payload, created) values (?, ?)",
            (json.dumps(payload), time.time()),
        )
        connection.commit()
        identifier = cursor.lastrowid
        connection.close()
        return int(identifier)

    def get_all(self):
        connection = sqlite3.connect(self.path)
        rows = connection.execute(
            "select id, payload, created from requests order by id"
        ).fetchall()
        connection.close()
        return [
            {"id": row[0], "payload": json.loads(row[1]), "created": row[2]}
            for row in rows
        ]


def heuristics(error: BaseException) -> str:
    """Diagnose common Python exceptions without network access."""
    messages = {
        KeyError: "A requested dictionary key is missing; check its spelling or use .get().",
        IndexError: "A sequence index is outside its bounds; check length before indexing.",
        TypeError: "An operation received an incompatible type; inspect the value and signature.",
        ZeroDivisionError: "A divisor is zero; validate it before division.",
        AttributeError: "The object lacks that attribute; check its type and initialization.",
        ImportError: "A dependency is unavailable; install it in the active environment.",
        FileNotFoundError: "The path does not exist; check the working directory and filename.",
    }
    # The mapping keeps common diagnoses deterministic and network-free.
    error_type = type(error)
    # isinstance preserves useful handling for subclasses of listed errors.
    for kind, message in messages.items():
        # Check specific known categories before returning the generic message.
        if isinstance(error, kind):
            return message
    del error_type
    return "No offline heuristic is available for this exception type."


def fallback_provider(providers: list[Callable[..., Any]], *args, **kwargs):
    """Try configured providers in order and return the first successful result."""
    errors = []
    provider_list = list(providers)
    # Copy the iterable because callers may pass a one-shot generator.
    for provider in provider_list:
        # Provider order is meaningful: the first success wins.
        try:
            return provider(*args, **kwargs)
        except Exception as error:
            # Preserve each failure so an exhausted provider chain is diagnosable.
            errors.append(str(error))
    error_summary = "; ".join(errors)
    # Include every provider error so a caller can diagnose an exhausted chain.
    # The summary is raised only after all providers have been attempted.
    # No provider is retried here; retry policy belongs to the provider itself.
    # The raised error describes the complete local fallback attempt.
    # Successful results return immediately and preserve provider ordering.
    raise RuntimeError("all providers failed: " + error_summary)


def degraded_mode() -> bool:
    """Detect unavailable network and log a clear degraded-mode warning."""
    host = os.getenv("GODAIX_PROBE_HOST", "1.1.1.1")
    port = 53
    timeout_seconds = 0.3
    # A short DNS-port probe avoids turning health reporting into a long wait.
    # The host can be overridden for controlled local or container probes.
    # Connection failures are interpreted as degraded operation, not fatal errors.
    # A successful socket is closed immediately because this is only a probe.
    # The boolean result is suitable for status and startup checks.
    # This function remains safe to call during offline startup.
    # No exception escapes for ordinary socket failures.
    # The logger receives the degraded-mode diagnostic instead.
    try:
        connection = socket.create_connection((host, port), timeout=timeout_seconds)
        connection.close()
        return False
    except OSError:
        LOGGER.warning("[godaix] running in degraded/offline mode")
        return True


def lazy_load(module: str, attribute: Optional[str] = None) -> Any:
    """Import a heavy module only when requested and optionally return an attribute."""
    import importlib

    module_name = module
    # The import stays inside this function so callers control when it happens.
    loaded = importlib.import_module(module_name)
    requested_attribute = attribute
    if requested_attribute:
        return getattr(loaded, requested_attribute)
    result = loaded
    # Returning the module itself is the no-attribute compatibility path.
    # The loaded object is returned without wrapping or caching it.
    # Attribute lookup failures therefore retain Python's normal exception type.
    # Keeping importlib local avoids expanding the module's public surface.
    # The caller controls whether an attribute or module is needed.
    # No import cache beyond Python's normal module cache is introduced here.
    # This makes the helper suitable for optional integrations.
    # It also preserves native import errors for invalid module names.
    return result


def zero_overhead(iterations: int = 1000) -> Dict[str, float]:
    """Benchmark a decorated fast path and return measured per-call overhead."""
    def plain(value):
        return value + 1

    wrapped = functools.wraps(plain)(lambda value: plain(value))
    start = time.perf_counter()
    for index in range(iterations):
        plain(index)
    baseline = time.perf_counter() - start
    start = time.perf_counter()
    for index in range(iterations):
        wrapped(index)
    decorated = time.perf_counter() - start
    overhead = max(0.0, decorated - baseline) / iterations
    return {
        "baseline_seconds": baseline,
        "decorated_seconds": decorated,
        "overhead_seconds": overhead,
    }


def network_probe(host: str = "1.1.1.1", port: int = 53) -> Dict[str, Any]:
    """Measure connection latency and recommend bounded retry settings."""
    started = time.perf_counter()
    try:
        connection = socket.create_connection((host, port), timeout=1)
        connection.close()
        latency = time.perf_counter() - started
        retries = 2 if latency < 1 else 1
        return {
            "online": True,
            "latency": latency,
            "timeout": max(2.0, latency * 5),
            "retries": retries,
        }
    except OSError as error:
        return {
            "online": False,
            "latency": None,
            "timeout": 1.0,
            "retries": 0,
            "error": str(error),
        }


def missing_dependency_helper(package: str) -> None:
    """Raise an actionable installation message for an expected package."""
    package_name = package
    # Importing first distinguishes a missing dependency from a pip failure.
    try:
        __import__(package_name)
    except ImportError as error:
        command = f"python -m pip install {package_name}"
        raise ImportError(
            f"godaix needs {package_name!r}; install it with: {command}"
        ) from error
    # Successful imports intentionally produce no return value.
    # This explicit return documents the helper's None contract.
    # Import errors retain the actionable pip command above.
    # The original ImportError is chained for debugging.
    # No installation is attempted automatically by this diagnostic helper.
    # Callers can decide whether to install, disable, or replace the feature.
    # Returning None after a successful import matches ordinary probe helpers.
    # The package name is never rewritten before import.
    return None


class cache_store:
    """Bounded TTL cache for diagnosis and patch results in memory and JSON."""

    def __init__(
        self,
        path: str = "godaix-cache.json",
        ttl: Optional[float] = None,
        max_items: int = 256,
    ):
        self.path = Path(path)
        self.ttl = ttl or SETTINGS.cache_ttl
        self.max_items = max_items
        self.data = self._load()

    def _load(self):
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def key(self, source: str, error: BaseException):
        material = f"{source}|{type(error).__name__}|{error}"
        return hashlib.sha256(material.encode()).hexdigest()

    def get(self, key: str):
        item = self.data.get(key)
        if not item:
            return None
        if time.time() - item["time"] > self.ttl:
            return None
        return item["value"]

    def put(self, key: str, value: Any):
        self.data[key] = {"time": time.time(), "value": value}
        self.data = dict(list(self.data.items())[-self.max_items:])
        self.path.write_text(json.dumps(self.data, default=str), encoding="utf-8")


def debounce(window: float = 10.0):
    """Suppress identical error-trigger calls inside a time window."""
    seen: Dict[str, float] = {}
    # State is scoped to this decorator instance, not shared globally.

    def decorator(function):
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            key = repr((args, kwargs))
            now = time.monotonic()
            # Monotonic time prevents wall-clock changes from reopening calls.
            previous = seen.get(key, 0)
            if now - previous < window:
                return None
            seen[key] = now
            result = function(*args, **kwargs)
            # Store the timestamp before the next identical invocation.
            return result

        return wrapped

    return decorator


def status() -> Dict[str, Any]:
    """Return current provider, connectivity, degradation, and circuit status."""
    offline = degraded_mode()
    # Connectivity is checked separately from the provider circuit state.
    provider = SETTINGS.provider
    state = circuit_breaker._states.get(provider, {})
    # Missing state means the provider has not failed yet.
    opened = bool(state.get("opened"))
    if opened:
        current_state = "circuit-open"
    elif offline:
        current_state = "offline"
    else:
        current_state = "online"
    result = {"state": current_state, "provider": provider, "degraded": offline}
    # Keep the result JSON-like for health endpoints and dashboards.
        # The provider field comes directly from the shared runtime settings.
        # Circuit state is reported before connectivity when both are present.
        # No state is mutated by this read-only status operation.
        # This keeps health reporting safe to call from dashboards and probes.
    return result


def rust_core(operation: str, values: list[int]) -> Any:
    """Use a future compiled extension when present, otherwise reference Python."""
    try:
        from godaix import _rust_core

        # Prefer the compiled implementation whenever it is available.
        implementation = getattr(_rust_core, operation)
        return implementation(values)
    except (ImportError, AttributeError):
        # Import and missing-operation failures share the reference fallback.
        # The reference path keeps the API useful when no optional extension exists.
        if operation == "sum":
            return sum(values)
        if operation == "max":
            return max(values)
        operation_name = operation
        raise ValueError(f"unsupported reference operation: {operation_name}")


class config:
    """Central resilience configuration with environment overrides."""

    def __init__(
        self,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        circuit_threshold: Optional[int] = None,
        cache_ttl: Optional[float] = None,
    ):
        self.timeout_seconds = timeout_seconds or SETTINGS.timeout
        self.max_retries = (
            max_retries if max_retries is not None else SETTINGS.retries
        )
        self.circuit_threshold = circuit_threshold or SETTINGS.circuit_threshold
        self.cache_ttl = cache_ttl or SETTINGS.cache_ttl

    def as_dict(self) -> Dict[str, Any]:
        """Return the effective settings as a serializable dictionary."""
        return {
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "circuit_threshold": self.circuit_threshold,
            "cache_ttl": self.cache_ttl,
        }


__all__ = [
    "timeout", "circuit_breaker", "offline_queue", "heuristics", "fallback_provider",
    "degraded_mode", "lazy_load", "zero_overhead", "network_probe",
    "missing_dependency_helper", "cache_store", "debounce", "status", "rust_core",
    "config",
]
