"""Provider-neutral chat client for hosted and OpenAI-compatible local models."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from config import Settings


@dataclass
class LLMResponse:
    text: str
    raw: dict[str, Any] | None = None


class LLMError(RuntimeError):
    pass


class LLMHandler:
    DEFAULT_BASE_URLS = {
        "openai": "https://api.openai.com/v1",
        "groq": "https://api.groq.com/openai/v1",
        "local": "http://localhost:11434/v1",
        "gemini": "https://generativelanguage.googleapis.com/v1beta/models",
        "anthropic": "https://api.anthropic.com/v1",
    }

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def chat(self, messages: list[dict[str, str]], system: str = "") -> LLMResponse:
        provider = self.settings.provider
        if provider in {"openai", "local", "groq"}:
            return self._openai_compatible(messages, system)
        if provider == "gemini":
            return self._gemini(messages, system)
        if provider == "anthropic":
            return self._anthropic(messages, system)
        raise LLMError(f"Unsupported provider: {provider}")

    def _request(self, url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        request = urllib.request.Request(url, json.dumps(payload).encode(), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.settings.request_timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            raise LLMError(f"Provider returned HTTP {exc.code}: {detail or exc.reason}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise LLMError(f"Provider request failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise LLMError("Provider returned invalid JSON") from exc

    def _base_url(self) -> str:
        return (self.settings.base_url or self.DEFAULT_BASE_URLS[self.settings.provider]).rstrip("/")

    def _openai_compatible(self, messages: list[dict[str, str]], system: str) -> LLMResponse:
        base = self._base_url()
        payload_messages = ([{"role": "system", "content": system}] if system else []) + messages
        data = self._request(f"{base.rstrip('/')}/chat/completions", {"model": self.settings.model, "messages": payload_messages}, {"Content-Type": "application/json", **({"Authorization": f"Bearer {self.settings.api_key}"} if self.settings.api_key else {})})
        try:
            return LLMResponse(data["choices"][0]["message"]["content"], data)
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Provider returned an unexpected chat response") from exc

    def _gemini(self, messages: list[dict[str, str]], system: str) -> LLMResponse:
        contents = [{"role": "user" if message["role"] != "assistant" else "model", "parts": [{"text": message["content"]}]} for message in messages]
        url = f"{self._base_url()}/{self.settings.model}:generateContent?key={self.settings.api_key}"
        data = self._request(url, {"systemInstruction": {"parts": [{"text": system}]} if system else {}, "contents": contents}, {"Content-Type": "application/json"})
        try:
            return LLMResponse(data["candidates"][0]["content"]["parts"][0]["text"], data)
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Gemini returned an unexpected response") from exc

    def _anthropic(self, messages: list[dict[str, str]], system: str) -> LLMResponse:
        data = self._request(f"{self._base_url()}/messages", {"model": self.settings.model, "max_tokens": 4096, "system": system, "messages": messages}, {"Content-Type": "application/json", "x-api-key": self.settings.api_key, "anthropic-version": "2023-06-01"})
        try:
            return LLMResponse(data["content"][0]["text"], data)
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Anthropic returned an unexpected response") from exc