"""Unified terminal and localhost web entry point."""

from __future__ import annotations

import argparse
import sys
import uuid

from command_executor import CommandExecutor
from config import Settings
from llm_handler import LLMError, LLMHandler
from memory_manager import MemoryManager
from system_detector import system_prompt


def render(text: str) -> None:
    try:
        from rich.console import Console
        from rich.markdown import Markdown
        Console().print(Markdown(text))
    except ImportError:
        print(text)


def run_cli(settings: Settings, prompt: str) -> int:
    session_id = str(uuid.uuid4())
    memory = MemoryManager(settings.memory_backend)
    handler = LLMHandler(settings)
    executor = CommandExecutor(settings)
    memory.add(session_id, "user", prompt)
    context = memory.context_text(session_id)
    system = f"You are {settings.assistant_name}, a practical cross-platform coding assistant. {system_prompt()}\nPrevious context:\n{context}"
    try:
        response = handler.chat([{"role": "user", "content": prompt}], system)
    except LLMError as exc:
        print(f"LLM error: {exc}", file=sys.stderr)
        return 1
    render(response.text)
    def debug_command(command: str, error: str) -> str:
        repair = handler.chat([{"role": "user", "content": f"The command failed. Fix it and return only one fenced shell command.\nCommand:\n{command}\nError:\n{error}"}], system)
        repaired = executor.extract(repair.text)
        return repaired[0] if repaired else command

    results = executor.run(response.text, debug_command)
    for result in results:
        print(f"\n$ {result.command}\n{result.output}")
    memory.add(session_id, "assistant", response.text)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AURA cross-platform AI engine")
    parser.add_argument("prompt", nargs="*", help="Task for the assistant")
    parser.add_argument("--web", action="store_true", help="Start the localhost web UI")
    args = parser.parse_args()
    settings = Settings.from_env()
    if errors := settings.validate():
        parser.error("; ".join(errors))
    if args.web or settings.mode == "web":
        from web_server import serve
        serve(settings)
        return 0
    if not args.prompt:
        parser.print_help()
        return 0
    return run_cli(settings, " ".join(args.prompt))


if __name__ == "__main__":
    raise SystemExit(main())
