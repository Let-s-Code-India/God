"""Bounded autonomous test-and-repair loop."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..llm import LLMClient, LLMError


@dataclass(frozen=True)
class AgentResult:
    goal: str
    passed: bool
    iterations: int
    output: str


def agent(goal: str, root: Optional[Path] = None, max_iterations: int = 3, allow_edits: bool = False) -> AgentResult:
    """Run tests, ask the model for diagnostics, and optionally apply fenced patches.

    Editing is opt-in because generated file changes require human review.
    """
    workspace = Path(root or Path.cwd()).resolve()
    last_output = ""
    for iteration in range(1, max_iterations + 1):
        try:
            completed = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=workspace, capture_output=True, text=True, timeout=300)
            last_output = (completed.stdout + completed.stderr).strip()
        except (OSError, subprocess.SubprocessError) as exc:
            last_output = str(exc)
            return AgentResult(goal, False, iteration, last_output)
        if completed.returncode == 0:
            return AgentResult(goal, True, iteration, last_output)
        try:
            advice = LLMClient().chat([{"role": "user", "content": f"Goal: {goal}\nTest failure:\n{last_output}\nReturn a unified diff only if a fix is certain."}]).text
        except LLMError as exc:
            return AgentResult(goal, False, iteration, f"{last_output}\nModel error: {exc}")
        if allow_edits:
            if not _apply_unified_diff(advice, workspace):
                return AgentResult(goal, False, iteration, last_output + "\nNo applicable unified diff was returned.")
        else:
            return AgentResult(goal, False, iteration, last_output + "\nSuggested fix:\n" + advice)
    return AgentResult(goal, False, max_iterations, last_output)


def _apply_unified_diff(text: str, workspace: Path) -> bool:
    patch = text[text.find("--- "):] if "--- " in text else ""
    if not patch:
        return False
    patch_file = workspace / ".god-ai.patch"
    patch_file.write_text(patch, encoding="utf-8")
    try:
        result = subprocess.run(["patch", "-p1", "--forward", "--batch", "-i", str(patch_file)], cwd=workspace, check=False, capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    finally:
        patch_file.unlink(missing_ok=True)