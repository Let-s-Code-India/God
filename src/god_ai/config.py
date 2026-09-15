"""Configuration for both the CLI and the importable SDK."""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class GodConfig:
    provider: str = "openrouter"
    api_key: str = ""
    base_url: str = ""
    model: str = "openrouter/auto"
    request_timeout: int = 120
    heal_retries: int = 1
    ghost_timeout: int = 30
    free_only: bool = False

    def normalized(self) -> "GodConfig":
        provider = self.provider.lower().strip()
        if provider == "ollama":
            provider = "local"
        if provider == "openrouter" and not self.api_key:
            provider = "local"
        model = self.model
        if provider == "local" and model == "openrouter/auto":
            model = "llama3"
        base_url = self.base_url.strip().rstrip("/")
        if provider == "local" and (not base_url or "openrouter.ai" in base_url):
            base_url = "http://localhost:11434/v1"
        if provider == "openrouter" and not base_url:
            base_url = "https://openrouter.ai/api/v1"
        return replace(self, provider=provider, model=model, base_url=base_url)

    def validate(self) -> list[str]:
        valid = {"openai", "openrouter", "gemini", "anthropic", "groq", "local"}
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
        "free_only": os.getenv("AURA_FREE_ONLY", "false").lower() in {"1", "true", "yes"},
    }
    env_values.update({key: value for key, value in values.items() if value is not None})
    _config = replace(_config, **env_values).normalized()
    errors = _config.validate()
    if errors:
        raise ValueError("Invalid God AI configuration: " + "; ".join(errors))
    return _config