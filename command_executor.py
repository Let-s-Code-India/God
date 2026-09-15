"""Extract and execute LLM-proposed shell commands with explicit guardrails."""

from __future__ import annotations

import re
import shlex
import subprocess
from dataclasses import dataclass
from typing import Callable

from config import Settings

COMMAND_BLOCK = re.compile(r"```(?:bash|sh|shell|powershell|pwsh)?\s*\n?(.*?)```", re.IGNORECASE | re.DOTALL)


@dataclass
class ExecutionResult:
    command: str
    output: str
    returncode: int
    attempts: int


class CommandExecutor:
    def __init__(self, settings: Settings, confirmer: Callable[[str], bool] | None = None) -> None:
        self.settings = settings
        self.confirmer = confirmer or (lambda command: input(f"Execute command? [y/N] {command}\n").strip().lower() in {"y", "yes"})

    @staticmethod
    def extract(response: str) -> list[str]:
        return [block.strip() for block in COMMAND_BLOCK.findall(response) if block.strip()]

    def run(self, response: str, debug: Callable[[str, str], str] | None = None) -> list[ExecutionResult]:
        results = []
        for command in self.extract(response):
            if self.settings.security_mode != "god" and not self.confirmer(command):
                results.append(ExecutionResult(command, "Skipped by user.", 0, 0))
                continue
            current = command
            for attempt in range(self.settings.max_debug_retries + 1):
                result = self._execute(current)
                results.append(ExecutionResult(current, result[0], result[1], attempt + 1))
                if result[1] == 0 or debug is None or attempt >= self.settings.max_debug_retries:
                    break
                current = debug(current, result[0])
        return results

    @staticmethod
    def _execute(command: str) -> tuple[str, int]:
        try:
            completed = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            output = (completed.stdout + completed.stderr).strip()
            return output, completed.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            return str(exc), 1