"""LLM-assisted structured text parsing."""

from __future__ import annotations

import json
from typing import Any, Optional, Type, TypeVar, Union

from pydantic import BaseModel, TypeAdapter

from ..llm import LLMClient

T = TypeVar("T")


def parse(text: str, model: Optional[Type[T]] = None) -> Union[T, dict[str, Any], list[Any]]:
    """Parse natural language into JSON or validate it against a Pydantic model."""
    response = LLMClient().chat([{"role": "user", "content": f"Return only valid JSON for this text:\n{text}"}], "You are a strict JSON parser.").text.strip()
    if response.startswith("```"):
        response = response.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        data = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model returned invalid JSON: {exc}") from exc
    if model is None:
        return data
    if issubclass(model, BaseModel):
        return model.model_validate(data)
    return TypeAdapter(model).validate_python(data)