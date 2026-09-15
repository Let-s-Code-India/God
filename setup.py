"""Interactive first-run configuration for AURA."""

from __future__ import annotations

from pathlib import Path

from config import ROOT, Settings
from system_detector import detect_system


def ask(prompt: str, default: str = "") -> str:
    answer = input(f"{prompt} [{default}]: ").strip()
    return answer or default


def run() -> None:
    info = detect_system()
    print(f"AURA setup on {info.environment} ({info.os_name}, {info.architecture})")
    name = ask("Assistant name", "AURA")
    providers = {"1": "openai", "2": "gemini", "3": "anthropic", "4": "groq", "5": "local"}
    print("1. OpenAI\n2. Google Gemini\n3. Anthropic Claude\n4. Groq / Grok\n5. Local LLM")
    provider = providers.get(ask("AI provider", "1"), "openai")
    api_key = "" if provider == "local" else ask("API key", "")
    default_url = "http://localhost:11434/v1" if provider == "local" else ""
    base_url = ask("Base URL", default_url)
    model_defaults = {"openai": "gpt-4o-mini", "gemini": "gemini-2.0-flash", "anthropic": "claude-3-5-sonnet-latest", "groq": "llama-3.1-8b-instant", "local": "llama3.2"}
    model = ask("Model", model_defaults[provider])
    mode = "web" if ask("Interface (cli/web)", "cli").lower() == "web" else "cli"
    security = "god" if ask("Security mode (safe/god)", "safe").lower() == "god" else "safe"
    backend = "sqlite" if ask("Enable SQLite memory? (y/n)", "y").lower() in {"y", "yes"} else "json"
    termux_api = ask("Enable Termux API voice features? (y/n)", "n").lower() in {"y", "yes"}
    settings = Settings(name, provider, api_key, base_url, model, mode, security, backend, termux_api)
    (ROOT / ".env").write_text(settings.to_env(), encoding="utf-8")
    print(f"Saved {ROOT / '.env'}")
    if info.environment in {"Termux", "iSH"}:
        print(f"For dependencies, use {info.package_manager} for system packages and pip for Python packages.")


if __name__ == "__main__":
    run()
