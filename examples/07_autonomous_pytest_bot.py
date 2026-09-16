from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from god_ai import aura


def run_bot() -> None:
    workspace = Path(__file__).resolve().parent.parent
    result = aura.agent(
        "Fix any failing pytest issues in the workspace while keeping behavior stable.",
        root=workspace,
        max_iterations=2,
        allow_edits=False,
    )
    print(result.output)
    print(f"passed={result.passed} iterations={result.iterations}")


if __name__ == "__main__":
    run_bot()
