from __future__ import annotations

import numpy as np

try:
    import tensorflow as tf
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install the aura extra: pip install 'god-ai[aura]' or install tensorflow") from exc

from god_ai import aura


@aura.optimize
@aura.cost_profiler
def build_and_train_classifier():
    (x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
    x_train = x_train.astype("float32") / 255.0
    y_train = tf.keras.utils.to_categorical(y_train, 10)

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input((28, 28)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(10, activation="softmax"),
        ]
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    history = model.fit(x_train[:2048], y_train[:2048], epochs=2, batch_size=64, verbose=0)
    return {"accuracy": float(np.max(history.history["accuracy"])), "loss": float(np.min(history.history["loss"]))}


if __name__ == "__main__":
    print(build_and_train_classifier())
