"""Unified OpenRouter, cloud-provider, and local-model chat handler."""

from __future__ import annotations

from typing import Optional

from .config import GodConfig
from .llm import LLMClient, LLMError, LLMResponse


class LLMHandler(LLMClient):
    """Compatibility name with OpenRouter and free-tier routing support."""

    def __init__(self, config: Optional[GodConfig] = None, free_only: bool = False) -> None:
        selected = config or GodConfig()
        if free_only:
            values = {field: getattr(selected, field) for field in selected.__dataclass_fields__}
            values["free_only"] = True
            selected = GodConfig(**values)
        super().__init__(selected)
