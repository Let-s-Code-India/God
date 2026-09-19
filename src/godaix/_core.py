"""Small shared primitives used by the five public godaix libraries."""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

LOGGER = logging.getLogger("godaix")

class ProviderUnavailable(RuntimeError):
    """Raised when an online provider was requested without credentials."""

@dataclass
class Settings:
    """Runtime settings loaded from environment variables."""
    provider: str = os.getenv("GODAIX_PROVIDER", "offline")
    timeout: float = float(os.getenv("GODAIX_TIMEOUT", "20"))
    retries: int = int(os.getenv("GODAIX_RETRIES", "2"))
    circuit_threshold: int = int(os.getenv("GODAIX_CIRCUIT_THRESHOLD", "3"))
    cache_ttl: float = float(os.getenv("GODAIX_CACHE_TTL", "3600"))

SETTINGS = Settings()

def redact(text: str) -> str:
    """Remove common credentials and personal identifiers before transport."""
    patterns = [
        (r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*['\"]?[^\s,'\"]+", r"\1=[REDACTED]"),
        (r"\b(sk-[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9]{20,})\b", "[REDACTED_TOKEN]"),
        (r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[REDACTED_EMAIL]"),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text

def llm(prompt: str, *, provider: Optional[str] = None, timeout: Optional[float] = None) -> str:
    """Call a configured provider through the common redaction boundary.

    Network SDKs are intentionally imported only inside this function. This keeps
    imports cheap while still making every declared dependency available.
    """
    chosen = provider or SETTINGS.provider
    safe_prompt = redact(prompt)
    if chosen in {"offline", "local"}:
        return "Offline analysis: inspect the failing input, validate assumptions, and retry only transient work."
    key_names = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "gemini": "GOOGLE_API_KEY", "groq": "GROQ_API_KEY", "xai": "XAI_API_KEY", "qwen": "DASHSCOPE_API_KEY", "openrouter": "OPENROUTER_API_KEY", "ollama": "OLLAMA_BASE_URL"}
    if not os.getenv(key_names.get(chosen, "GODAIX_API_KEY")):
        raise ProviderUnavailable(f"No credentials configured for {chosen}. Set {key_names.get(chosen, 'GODAIX_API_KEY')} to use this provider.")
    from godaix.aether import circuit_breaker, timeout as bounded_timeout
    request = lambda: _provider_request(chosen, safe_prompt, timeout or SETTINGS.timeout)
    return circuit_breaker(chosen).call(bounded_timeout(timeout or SETTINGS.timeout)(request))

def _provider_request(provider: str, prompt: str, timeout: float) -> str:
    """Use a small compatible HTTP request for supported provider families."""
    import requests
    base = os.getenv("GODAIX_BASE_URL", "")
    if provider == "ollama":
        base = base or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.post(base.rstrip("/") + "/api/generate", json={"model": os.getenv("GODAIX_MODEL", "llama3"), "prompt": prompt, "stream": False}, timeout=timeout)
        response.raise_for_status()
        return str(response.json().get("response", ""))
    if provider == "anthropic":
        response = requests.post(os.getenv("GODAIX_BASE_URL", "https://api.anthropic.com/v1/messages"), json={"model": os.getenv("GODAIX_MODEL", "claude-3-haiku-20240307"), "max_tokens": 1024, "messages": [{"role": "user", "content": prompt}]}, headers={"x-api-key": os.getenv("ANTHROPIC_API_KEY", ""), "anthropic-version": "2023-06-01"}, timeout=timeout)
        response.raise_for_status(); return str(response.json()["content"][0]["text"])
    if provider == "gemini":
        endpoint = os.getenv("GODAIX_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent")
        response = requests.post(endpoint, params={"key": os.getenv("GOOGLE_API_KEY", "")}, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=timeout)
        response.raise_for_status(); return str(response.json()["candidates"][0]["content"]["parts"][0]["text"])
    if provider in {"openai", "groq", "xai", "qwen", "openrouter", "openai_compatible"}:
        endpoint = base or os.getenv("GODAIX_BASE_URL", "https://api.openai.com/v1")
        response = requests.post(endpoint.rstrip("/") + "/chat/completions", json={"model": os.getenv("GODAIX_MODEL", "default"), "messages": [{"role": "user", "content": prompt}]}, headers={"Authorization": f"Bearer {os.getenv('GODAIX_API_KEY', '')}"}, timeout=timeout)
        response.raise_for_status()
        return str(response.json()["choices"][0]["message"]["content"])
    raise ProviderUnavailable(f"Provider {provider!r} is not configured with a transport.")

def strip_fences(text: str) -> str:
    """Strip Markdown fences before source validation."""
    return re.sub(r"^```(?:python|py)?\s*|\s*```$", "", text.strip(), flags=re.I | re.M).strip()

def validate_source(source: str) -> ast.Module:
    """Parse generated Python and reject syntactically invalid repairs."""
    return ast.parse(strip_fences(source), mode="exec")

def source_key(function: Callable[..., Any], error: BaseException) -> str:
    """Create a stable diagnosis key from source and exception details."""
    try:
        source = inspect.getsource(function)
    except (OSError, TypeError):
        source = repr(function)
    raw = f"{source}|{type(error).__name__}|{error}"
    return hashlib.sha256(raw.encode()).hexdigest()

def json_line(path: str, item: Dict[str, Any]) -> None:
    """Append one structured event to a local JSON-lines file."""
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, default=str) + "\n")