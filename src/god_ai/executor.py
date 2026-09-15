"""Explicitly confirmed shell execution for CLI tasks."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from collections.abc import Callable
from typing import Optional


COMMAND_BLOCK = re.compile(r"```(?:bash|sh|shell|powershell|pwsh)?\s*\n?(.*?)```", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class ExecutionResult:
    command: str
    output: str
    returncode: int
    attempts: int


def extract_commands(response: str) -> list[str]:
    return [block.strip() for block in COMMAND_BLOCK.findall(response) if block.strip()]


def run_commands(response: str, safe: bool = True, debug: Optional[Callable[[str, str], str]] = None, retries: int = 3) -> list[ExecutionResult]:
    results = []
    for command in extract_commands(response):
        if safe and input(f"Execute command? [y/N] {command}\n").strip().lower() not in {"y", "yes"}:
            results.append(ExecutionResult(command, "Skipped by user.", 0, 0))
            continue
        current = command
        for attempt in range(retries + 1):
            try:
                completed = subprocess.run(current, shell=True, capture_output=True, text=True, timeout=300)
                output, code = (completed.stdout + completed.stderr).strip(), completed.returncode
            except (OSError, subprocess.SubprocessError) as exc:
                output, code = str(exc), 1
            results.append(ExecutionResult(current, output, code, attempt + 1))
            if code == 0 or debug is None or attempt >= retries:
                break
            current = debug(current, output)
    return results