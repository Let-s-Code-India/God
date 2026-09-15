"""Environment-backed configuration for AURA."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_dotenv(path: Path | None = None) -> None:
    """Load simple KEY=VALUE entries without requiring python-dotenv."""
    env_path = path or ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"\''))


@dataclass(slots=True)
class Settings:
    assistant_name: str = "AURA"
    provider: str = "openai"
    api_key: str = ""
    base_url: str = ""
    model: str = "gpt-4o-mini"
    mode: str = "cli"
    security_mode: str = "safe"
    memory_backend: str = "sqlite"
    termux_api: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    max_debug_retries: int = 3
    request_timeout: int = 120

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.provider not in {"openai", "gemini", "anthropic", "groq", "local"}:
            errors.append(f"Unsupported provider: {self.provider}")
        if self.mode not in {"cli", "web"}:
            errors.append(f"Unsupported mode: {self.mode}")
        if self.security_mode not in {"safe", "god"}:
            errors.append(f"Unsupported security mode: {self.security_mode}")
        if self.memory_backend not in {"sqlite", "json"}:
            errors.append(f"Unsupported memory backend: {self.memory_backend}")
        if not 1 <= self.port <= 65535:
            errors.append("Port must be between 1 and 65535")
        if not self.model.strip():
            errors.append("AURA_MODEL cannot be empty")
        if self.request_timeout < 5:
            errors.append("Request timeout must be at least 5 seconds")
        return errors

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        try:
            return cls(
                assistant_name=os.getenv("AURA_NAME", "AURA").strip() or "AURA",
                provider=os.getenv("AURA_PROVIDER", "openai").lower().strip(),
                api_key=os.getenv("AURA_API_KEY", "").strip(),
                base_url=os.getenv("AURA_BASE_URL", "").strip(),
                model=os.getenv("AURA_MODEL", "gpt-4o-mini").strip(),
                mode=os.getenv("AURA_MODE", "cli").lower().strip(),
                security_mode=os.getenv("AURA_SECURITY_MODE", "safe").lower().strip(),
                memory_backend=os.getenv("AURA_MEMORY_BACKEND", "sqlite").lower().strip(),
                termux_api=os.getenv("AURA_TERMUX_API", "false").lower() in {"1", "true", "yes"},
                host=os.getenv("AURA_HOST", "127.0.0.1").strip(),
                port=int(os.getenv("AURA_PORT", "8000")),
                max_debug_retries=max(0, int(os.getenv("AURA_MAX_DEBUG_RETRIES", "3"))),
                request_timeout=max(5, int(os.getenv("AURA_REQUEST_TIMEOUT", "120"))),
            )
        except ValueError as exc:
            raise ValueError(f"Invalid numeric AURA setting: {exc}") from exc

    def to_env(self) -> str:
        values = {"AURA_NAME": self.assistant_name, "AURA_PROVIDER": self.provider, "AURA_API_KEY": self.api_key, "AURA_BASE_URL": self.base_url, "AURA_MODEL": self.model, "AURA_MODE": self.mode, "AURA_SECURITY_MODE": self.security_mode, "AURA_MEMORY_BACKEND": self.memory_backend, "AURA_TERMUX_API": str(self.termux_api).lower(), "AURA_HOST": self.host, "AURA_PORT": str(self.port), "AURA_MAX_DEBUG_RETRIES": str(self.max_debug_retries), "AURA_REQUEST_TIMEOUT": str(self.request_timeout)}
        return "\n".join(f"{key}={value}" for key, value in values.items()) + "\n"
