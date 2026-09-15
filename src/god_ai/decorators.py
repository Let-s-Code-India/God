"""Decorators that add model-assisted diagnostics without hiding failures."""

from __future__ import annotations

import functools
import inspect
import logging
import sys
import traceback
from collections.abc import Callable
from typing import Any, TypeVar, cast

from .config import get_config
from .llm import LLMClient, LLMError


logger = logging.getLogger("god_ai")
F = TypeVar("F", bound=Callable[..., Any])


def heal(function: F) -> F:
    """Log a model diagnosis and retry a failing function once by default.

    The original exception is re-raised if the retry fails; production code never
    silently converts an application failure into an apparently successful call.
    """
    @functools.wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except Exception as original:
            config = get_config()
            source = _source(function)
            arguments = {"args": repr(args), "kwargs": repr(kwargs)}
            locals_snapshot = _traceback_locals(sys.exc_info()[2])
            prompt = f"Diagnose this Python failure and suggest a minimal fix.\nFunction:\n{source}\nArguments:\n{arguments}\nLocals:\n{locals_snapshot}\nTraceback:\n{traceback.format_exc()}"
            try:
                diagnosis = LLMClient(config).chat([{"role": "user", "content": prompt}], "You are a precise Python debugging assistant.").text
                logger.error("%s failed. Model diagnosis:\n%s", function.__qualname__, diagnosis)
            except LLMError as exc:
                logger.warning("Could not obtain healing diagnosis: %s", exc)
            for _ in range(config.heal_retries):
                try:
                    return function(*args, **kwargs)
                except Exception:
                    logger.exception("Retry failed for %s", function.__qualname__)
            raise original

    return cast(F, wrapped)


def _source(function: Callable[..., Any]) -> str:
    try:
        return inspect.getsource(function)
    except (OSError, TypeError):
        return f"Source unavailable for {function.__qualname__}"


def _traceback_locals(traceback_object: Any) -> dict[str, str]:
    values: dict[str, str] = {}
    while traceback_object is not None:
        for name, value in traceback_object.tb_frame.f_locals.items():
            values[name] = repr(value)[:500]
        traceback_object = traceback_object.tb_next
    return values