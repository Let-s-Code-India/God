"""Parse unstructured text into a validated Pydantic record and serve it over FastAPI.

Run:
    python -m pip install fastapi uvicorn pydantic
    python examples/04_fastapi_unstructured_parser.py
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from god_ai import aura


class ExtractedRecord(BaseModel):
    title: str
    summary: str
    entities: list[str] = Field(default_factory=list)
    priority: str = "medium"


text_blob = """
Acme Launches Edge Router
The team completed beta testing for the new edge router in North America.
Key stakeholders: product, infra, and security. This is a high-priority rollout.
"""


try:
    from fastapi import FastAPI

    app = FastAPI(title="Aura Unstructured Parser API")

    @app.get("/parse")
    def parse_endpoint() -> dict[str, object]:
        parsed = aura.parse(text_blob, ExtractedRecord)
        return parsed.model_dump()
except ImportError:  # pragma: no cover
    app = None


if __name__ == "__main__":
    if app is None:
        print(aura.parse(text_blob, ExtractedRecord))
    else:
        import uvicorn

        uvicorn.run(app, host="127.0.0.1", port=8000)
