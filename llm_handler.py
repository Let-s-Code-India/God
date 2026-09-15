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
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            raise LLMError(f"Provider request failed: {exc}") from exc

    def _openai_compatible(self, messages: list[dict[str, str]], system: str) -> LLMResponse:
        base = self.settings.base_url or "https://api.openai.com/v1"
        payload_messages = ([{"role": "system", "content": system}] if system else []) + messages
        data = self._request(f"{base.rstrip('/')}/chat/completions", {"model": self.settings.model, "messages": payload_messages}, {"Content-Type": "application/json", **({"Authorization": f"Bearer {self.settings.api_key}"} if self.settings.api_key else {})})
        try:
            return LLMResponse(data["choices"][0]["message"]["content"], data)
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Provider returned an unexpected chat response") from exc

    def _gemini(self, messages: list[dict[str, str]], system: str) -> LLMResponse:
        contents = [{"role": "user" if message["role"] != "assistant" else "model", "parts": [{"text": message["content"]}]} for message in messages]
        url = f"{self.settings.base_url or 'https://generativelanguage.googleapis.com/v1beta/models'}/{self.settings.model}:generateContent?key={self.settings.api_key}"
        data = self._request(url, {"systemInstruction": {"parts": [{"text": system}]} if system else {}, "contents": contents}, {"Content-Type": "application/json"})
        try:
            return LLMResponse(data["candidates"][0]["content"]["parts"][0]["text"], data)
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Gemini returned an unexpected response") from exc

    def _anthropic(self, messages: list[dict[str, str]], system: str) -> LLMResponse:
        data = self._request(f"{self.settings.base_url or 'https://api.anthropic.com/v1'}/messages", {"model": self.settings.model, "max_tokens": 4096, "system": system, "messages": messages}, {"Content-Type": "application/json", "x-api-key": self.settings.api_key, "anthropic-version": "2023-06-01"})
        try:
            return LLMResponse(data["content"][0]["text"], data)
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Anthropic returned an unexpected response") from exc