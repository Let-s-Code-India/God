from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from god_ai import aura


def clean_records(data: list[dict[str, object]]) -> list[dict[str, object]]:
    df = pd.DataFrame(data)
    for column in df.columns:
        if df[column].dtype == object:
            df[column] = df[column].astype(str).str.strip()
    df = df.replace({"": np.nan, None: np.nan})
    df = df.dropna(how="any")
    return df.to_dict(orient="records")


sample = [{
    "id": 1,
    "name": " Alpha ",
    "score": "88",
    "country": "US",
}, {
    "id": 2,
    "name": "Beta",
    "score": "",
    "country": "CA",
}, {
    "id": 3,
    "name": "Gamma",
    "score": "91",
    "country": "US",
}]

if __name__ == "__main__":
    cleaned = clean_records(sample)
    print(json.dumps(cleaned, indent=2))
    parsed = aura.parse(json.dumps(cleaned), None)
    print(parsed)
