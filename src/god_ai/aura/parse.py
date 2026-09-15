"""LLM-assisted structured text parsing."""

from __future__ import annotations

import json
from typing import Any, Optional, Type, TypeVar, Union

from pydantic import BaseModel, TypeAdapter

from ..llm import LLMClient

T = TypeVar("T")


def parse(text: str, model: Optional[Type[T]] = None) -> Union[T, dict[str, Any], list[Any]]:
    """Parse natural language into JSON or validate it against a Pydantic model."""
    client = LLMClient()
    response = client.chat([{"role": "user", "content": f"Return only valid JSON for this text:\n{text}"}], "You are a strict JSON parser.").text.strip()
    return _decode(response, model, client, text)


def _decode(response: str, model: Optional[Type[T]], client: LLMClient, original: str) -> Union[T, dict[str, Any], list[Any]]:
    if response.startswith("```"):
        response = response.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        data = json.loads(response)
    except json.JSONDecodeError as exc:
        repaired = client.chat([{"role": "user", "content": f"Repair this into valid JSON only. Original text: {original}\nMalformed response: {response}\nError: {exc}"}], "Return valid JSON and nothing else.").text.strip()
        try:
            data = json.loads(repaired.strip("` \n"))
        except json.JSONDecodeError as repair_error:
            raise ValueError(f"Model returned invalid JSON after repair: {repair_error}") from repair_error
    if model is None:
        return data
    if issubclass(model, BaseModel):
        return model.model_validate(data)
    return TypeAdapter(model).validate_python(data)