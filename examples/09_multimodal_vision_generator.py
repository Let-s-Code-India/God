from __future__ import annotations

import json
import os

from god_ai import aura


def build_boilerplate_from_image_description(prompt: str) -> dict[str, object]:
    payload = {
        "summary": prompt,
        "language": "python",
        "framework": "fastapi",
        "components": ["routes", "models", "tests"],
    }
    parsed = aura.parse(json.dumps(payload), None)
    return parsed if isinstance(parsed, dict) else {"summary": prompt}


if __name__ == "__main__":
    print(build_boilerplate_from_image_description("A dashboard with a sidebar, chart panel, and API route definitions."))
