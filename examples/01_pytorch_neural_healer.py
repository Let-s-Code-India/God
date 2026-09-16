from __future__ import annotations

import numpy as np
import torch
from torch import nn

from god_ai import aura


@aura.heal
@aura.trace_exceptions
def train_healer_example(batch_size: int = 8):
    x = np.random.randn(batch_size, 4).astype(np.float32)
    y = np.random.randn(batch_size, 2).astype(np.float32)
    model = nn.Sequential(
        nn.Linear(4, 8),
        nn.ReLU(),
        nn.Linear(8, 2),
    )
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    inputs = torch.tensor(x)
    target = torch.tensor(y)
    for _ in range(4):
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = loss_fn(outputs, target)
        loss.backward()
        optimizer.step()

    if outputs.shape != target.shape:
        raise ValueError(f"Tensor shape mismatch: {outputs.shape} vs {target.shape}")

    return {"loss": float(loss.item()), "shape": list(outputs.shape)}


if __name__ == "__main__":
    result = train_healer_example()
    print("pytorch neural healer:", result)
