"""Configuration for both the CLI and the importable SDK."""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class GodConfig:
    provider: str = "openai"
    api_key: str = ""
    base_url: str = ""
    model: str = "gpt-4o-mini"
    request_timeout: int = 120
    heal_retries: int = 1
    ghost_timeout: int = 30

    def normalized(self) -> "GodConfig":
        provider = self.provider.lower().strip()
        if provider == "ollama":
            provider = "local"
        return replace(self, provider=provider, base_url=self.base_url.strip().rstrip("/"))

    def validate(self) -> list[str]:
        valid = {"openai", "gemini", "anthropic", "groq", "local"}
        errors = []
        if self.provider not in valid and self.provider != "ollama":
            errors.append(f"Unsupported provider: {self.provider}")
        if not self.model.strip():
            errors.append("model cannot be empty")
        if self.request_timeout < 5:
            errors.append("request_timeout must be at least 5")
        if self.heal_retries < 0 or self.ghost_timeout < 1:
            errors.append("retry and timeout values must be positive")
        return errors


_config = GodConfig()


def _load_dotenv() -> None:
    paths = [Path.cwd() / ".env", ROOT / ".env"]
    for path in paths:
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
        break


def get_config() -> GodConfig:
    return _config


def configure(**values: Any) -> GodConfig:
    """Configure the process-wide SDK client and return its immutable settings."""
    global _config
    _load_dotenv()
    aliases = {"name": "model", "timeout": "request_timeout"}
    values = {aliases.get(key, key): value for key, value in values.items()}
    env_values = {
        "provider": os.getenv("AURA_PROVIDER", _config.provider),
        "api_key": os.getenv("AURA_API_KEY", _config.api_key),
        "base_url": os.getenv("AURA_BASE_URL", _config.base_url),
        "model": os.getenv("AURA_MODEL", _config.model),
    }
    env_values.update({key: value for key, value in values.items() if value is not None})
    _config = replace(_config, **env_values).normalized()
    errors = _config.validate()
    if errors:
        raise ValueError("Invalid God AI configuration: " + "; ".join(errors))
    return _config