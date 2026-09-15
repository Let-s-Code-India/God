"""Small provider router used by the SDK, CLI, and healing features."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Optional

from .config import GodConfig, get_config


class LLMError(RuntimeError):
    """Raised when a model provider cannot complete a request."""


@dataclass(frozen=True)
class LLMResponse:
    text: str
    raw: Optional[dict[str, Any]] = None


class LLMClient:
    defaults = {
        "openrouter": "https://openrouter.ai/api/v1",
        "openai": "https://api.openai.com/v1",
        "groq": "https://api.groq.com/openai/v1",
        "local": "http://localhost:11434/v1",
        "gemini": "https://generativelanguage.googleapis.com/v1beta/models",
        "anthropic": "https://api.anthropic.com/v1",
    }

    def __init__(self, config: Optional[GodConfig] = None) -> None:
        self.config = (config or get_config()).normalized()

    def chat(self, messages: list[dict[str, str]], system: str = "") -> LLMResponse:
        if self.config.provider in {"openai", "local", "groq", "openrouter"}:
            return self._openai(messages, system)
        if self.config.provider == "gemini":
            return self._gemini(messages, system)
        if self.config.provider == "anthropic":
            return self._anthropic(messages, system)
        raise LLMError(f"Unsupported provider: {self.config.provider}")

    def _request(self, url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        request = urllib.request.Request(url, json.dumps(payload).encode(), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.config.request_timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            raise LLMError(f"Provider returned HTTP {exc.code}: {detail or exc.reason}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise LLMError(f"Provider request failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise LLMError("Provider returned invalid JSON") from exc

    def _base(self) -> str:
        return (self.config.base_url or self.defaults[self.config.provider]).rstrip("/")

    def _openai(self, messages: list[dict[str, str]], system: str) -> LLMResponse:
        prompt = ([{"role": "system", "content": system}] if system else []) + messages
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        model = self.config.model
        if self.config.provider == "openrouter" and self.config.free_only and not model.endswith(":free") and model != "openrouter/auto":
            model += ":free"
        data = self._request(f"{self._base()}/chat/completions", {"model": model, "messages": prompt}, headers)
        try:
            return LLMResponse(data["choices"][0]["message"]["content"], data)
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Provider returned an unexpected chat response") from exc

    def _gemini(self, messages: list[dict[str, str]], system: str) -> LLMResponse:
        contents = [{"role": "user" if item["role"] != "assistant" else "model", "parts": [{"text": item["content"]}]} for item in messages]
        url = f"{self._base()}/{self.config.model}:generateContent?key={self.config.api_key}"
        data = self._request(url, {"systemInstruction": {"parts": [{"text": system}]} if system else {}, "contents": contents}, {"Content-Type": "application/json"})
        try:
            return LLMResponse(data["candidates"][0]["content"]["parts"][0]["text"], data)
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Gemini returned an unexpected response") from exc

    def _anthropic(self, messages: list[dict[str, str]], system: str) -> LLMResponse:
        data = self._request(f"{self._base()}/messages", {"model": self.config.model, "max_tokens": 4096, "system": system, "messages": messages}, {"Content-Type": "application/json", "x-api-key": self.config.api_key, "anthropic-version": "2023-06-01"})
        try:
            return LLMResponse(data["content"][0]["text"], data)
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Anthropic returned an unexpected response") from exc