"""Lightweight profiling decorator with model-assisted suggestions."""

from __future__ import annotations

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar, cast

from ..llm import LLMClient, LLMError

logger = logging.getLogger("god_ai.optimize")
F = TypeVar("F", bound=Callable[..., Any])


def optimize(function: F) -> F:
    """Profile calls and log an optimization suggestion for slow executions."""
    @functools.wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        result = function(*args, **kwargs)
        elapsed = time.perf_counter() - started
        if elapsed >= 0.1:
            try:
                suggestion = LLMClient().chat([{"role": "user", "content": f"Suggest a faster implementation for {function.__qualname__}; runtime was {elapsed:.3f}s."}]).text
                logger.info("Optimization suggestion for %s: %s", function.__qualname__, suggestion)
            except LLMError as exc:
                logger.debug("Optimization suggestion unavailable: %s", exc)
        return result
    return cast(F, wrapped)