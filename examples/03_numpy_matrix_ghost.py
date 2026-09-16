from __future__ import annotations

import numpy as np

from god_ai import aura


context = {
    "matrix": np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float64),
    "vector": np.array([5.0, 6.0], dtype=np.float64),
}


result = aura.do(
    "Create a matrix transform that returns the dot product of matrix and vector, then normalizes it, and assigns it to result.",
    context=context,
)

print("matrix ghost result:", result)


@aura.benchmark
def matrix_transform(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    projected = matrix @ vector
    normalized = projected / np.linalg.norm(projected)
    return normalized


if __name__ == "__main__":
    sample = np.array([[2.0, 1.0], [0.5, 3.0]], dtype=np.float64)
    vector = np.array([1.0, -1.0], dtype=np.float64)
    print(matrix_transform(sample, vector))
