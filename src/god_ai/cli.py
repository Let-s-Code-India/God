"""Console entry point installed as the ``god`` command."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from .config import configure
from .executor import run_commands
from .llm import LLMClient, LLMError
from .memory import Memory
from .system import system_prompt


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="god", description="God AI cross-platform terminal assistant")
    parser.add_argument("prompt", nargs="*", help="Task for the assistant")
    parser.add_argument("--web", action="store_true", help="Start the localhost web UI")
    parser.add_argument("--free", action="store_true", help="Use OpenRouter free-tier routing")
    args = parser.parse_args(argv)
    try:
        config = configure(free_only=args.free)
    except ValueError as exc:
        parser.error(str(exc))
    if args.web:
        from .web import serve
        serve()
        return 0
    if not args.prompt:
        parser.print_help()
        return 0
    prompt = " ".join(args.prompt)
    memory = Memory("json")
    session = os.getenv("GOD_SESSION_ID", "cli")
    memory.add(session, "user", prompt)
    client = LLMClient(config)
    system = f"You are a practical coding assistant. {system_prompt()}\nPrevious context:\n{memory.context(session)}"
    try:
        response = client.chat([{"role": "user", "content": prompt}], system)
    except LLMError as exc:
        print(f"LLM error: {exc}", file=sys.stderr)
        return 1
    try:
        from rich.console import Console
        from rich.markdown import Markdown
        Console().print(Markdown(response.text))
    except ImportError:
        print(response.text)
    def debug(command: str, error: str) -> str:
        repair = client.chat([{"role": "user", "content": f"Fix this shell command and return one fenced command.\n{command}\n{error}"}], system)
        commands = __import__("god_ai.executor", fromlist=["extract_commands"]).extract_commands(repair.text)
        return commands[0] if commands else command
    for result in run_commands(response.text, safe=True, debug=debug, retries=config.heal_retries):
        print(f"\n$ {result.command}\n{result.output}")
    memory.add(session, "assistant", response.text)
    return 0