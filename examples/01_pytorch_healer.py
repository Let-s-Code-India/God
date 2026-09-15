"""Self-healing PyTorch shape-mismatch training example.

Run after installing the optional dependencies:
    python -m pip install torch numpy
    python examples/01_pytorch_healer.py
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import torch
from torch import nn

from god_ai import aura

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


class TinyCNN(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(nn.Conv2d(3, 8, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d((1, 1)))
        self.classifier = nn.Linear(8, 2)

    def forward(self, batch: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(batch).flatten(1))


_attempts = 0


@aura.heal
def train_step(model: nn.Module, batch: torch.Tensor, target: torch.Tensor) -> float:
    """Demonstrate diagnosis of NCHW versus NHWC input and a repaired retry."""
    global _attempts
    _attempts += 1
    if _attempts == 1:
        # Deliberately provide NHWC data to an NCHW convolution.
        model(batch.permute(0, 2, 3, 1))
    else:
        # The retry represents the fix identified by the model diagnosis.
        batch = batch.contiguous()
    prediction = model(batch)
    loss = nn.functional.cross_entropy(prediction, target)
    loss.backward()
    return float(loss.detach())


def main() -> None:
    aura.configure(provider="ollama", model="llama3", heal_retries=1)
    rng = np.random.default_rng(7)
    batch = torch.tensor(rng.normal(size=(4, 3, 16, 16)), dtype=torch.float32)
    target = torch.tensor([0, 1, 0, 1])
    model = TinyCNN()
    try:
        loss = train_step(model, batch, target)
    except RuntimeError as exc:
        print(f"The model diagnosis was logged, but the retry still needs a corrected batch: {exc}")
        fixed_batch = batch.contiguous()
        loss = float(nn.functional.cross_entropy(model(fixed_batch), target).detach())
    print(f"NCHW batch shape: {tuple(batch.shape)}; training loss: {loss:.4f}")


if __name__ == "__main__":
    main()
