import os
from unittest.mock import patch

import pytest

from godaix._core import _provider_request


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


@pytest.mark.parametrize(
    "provider",
    ["openai", "anthropic", "gemini", "groq", "xai", "qwen", "openrouter", "openai_compatible"],
)
def test_cloud_providers_prefer_shared_key_and_configured_model(provider):
    environment = {
        "GODAIX_API_KEY": "shared-key",
        "GODAIX_MODEL": "configured-model",
        "OPENAI_API_KEY": "legacy-openai-key",
        "ANTHROPIC_API_KEY": "legacy-anthropic-key",
        "GOOGLE_API_KEY": "legacy-google-key",
        "GROQ_API_KEY": "legacy-groq-key",
        "XAI_API_KEY": "legacy-xai-key",
        "DASHSCOPE_API_KEY": "legacy-qwen-key",
        "OPENROUTER_API_KEY": "legacy-openrouter-key",
    }
    payload = (
        {"content": [{"text": "ok"}]}
        if provider == "anthropic"
        else {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
        if provider == "gemini"
        else {"choices": [{"message": {"content": "ok"}}]}
    )

    with patch.dict(os.environ, environment, clear=True), patch(
        "requests.post", return_value=Response(payload)
    ) as post:
        _provider_request(provider, "hello", 4)

    _, request = post.call_args
    if provider == "gemini":
        assert request["params"]["key"] == "shared-key"
        assert post.call_args.args[0].endswith(
            "/models/configured-model:generateContent"
        )
    elif provider == "anthropic":
        assert request["json"]["model"] == "configured-model"
        assert request["headers"]["x-api-key"] == "shared-key"
    else:
        assert request["json"]["model"] == "configured-model"
        assert request["headers"]["Authorization"] == "Bearer shared-key"


def test_ollama_uses_configured_model_and_base_url():
    payload = {"response": "ok"}
    with patch.dict(
        os.environ,
        {"GODAIX_BASE_URL": "http://ollama.test", "GODAIX_MODEL": "qwen2.5"},
        clear=True,
    ), patch("requests.post", return_value=Response(payload)) as post:
        _provider_request("ollama", "hello", 4)

    _, request = post.call_args
    assert post.call_args.args[0] == "http://ollama.test/api/generate"
    assert request["json"]["model"] == "qwen2.5"


def test_gemini_falls_back_to_legacy_key_when_shared_key_is_absent():
    payload = {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
    with patch.dict(
        os.environ,
        {"GOOGLE_API_KEY": "legacy-google-key", "GODAIX_MODEL": "gemini-1.5-flash"},
        clear=True,
    ), patch("requests.post", return_value=Response(payload)) as post:
        _provider_request("gemini", "hello", 4)

    assert post.call_args.kwargs["params"]["key"] == "legacy-google-key"
