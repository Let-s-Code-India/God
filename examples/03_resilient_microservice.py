"""Matrix service with model-provider fallback and NumPy processing.

Run:
    python -m pip install numpy
    python examples/03_resilient_microservice.py
"""

from __future__ import annotations

import logging
import os

import numpy as np

from god_ai import aura
from god_ai.llm import LLMClient, LLMError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def matrix_transform(matrix: np.ndarray) -> np.ndarray:
    """Use NumPy locally; the SDK remains available for model-assisted plans."""
    centered = matrix - matrix.mean(axis=0, keepdims=True)
    covariance = centered.T @ centered / max(1, matrix.shape[0] - 1)
    return covariance


def choose_provider() -> None:
    try:
        client = LLMClient()
        client.chat([{"role": "user", "content": "Reply with the active provider name only."}])
        logging.info("Cloud/local provider responded successfully")
    except LLMError as exc:
        logging.warning("All configured providers failed: %s", exc)


def main() -> None:
    aura.configure(
        provider=os.getenv("AURA_PROVIDER", "openrouter"),
        api_key=os.getenv("AURA_API_KEY", ""),
        model=os.getenv("AURA_MODEL", "openrouter/auto"),
        base_url=os.getenv("AURA_BASE_URL", ""),
    )
    choose_provider()
    data = np.arange(12, dtype=float).reshape(4, 3)
    covariance = matrix_transform(data)
    print("Input matrix:\n", data)
    print("Covariance matrix:\n", covariance)
    print("Configured fallback chain: primary -> OpenRouter -> Ollama")


if __name__ == "__main__":
    main()
