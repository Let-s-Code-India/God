from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request

from god_ai import aura

app = Flask(__name__)

DEFAULT_ENDPOINT = os.getenv("OLLAMA_URL", "http://localhost:11434/v1/chat/completions")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "provider": "local-ollama", "endpoint": DEFAULT_ENDPOINT}


@app.post("/infer")
def infer() -> Any:
    payload = request.get_json(silent=True) or {}
    prompt = str(payload.get("prompt", "Explain the system health in one sentence."))
    try:
        result = aura.do(
            "Return a one-sentence summary of the requested prompt and store it in result.",
            context={"prompt": prompt},
        )
        return jsonify({"response": result, "fallback": False})
    except Exception:
        return jsonify({"response": f"Fall back: {prompt} is being processed by the resilience layer.", "fallback": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
