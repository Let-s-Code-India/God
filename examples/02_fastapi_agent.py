"""Fetch text, parse it into Pydantic records, and expose a FastAPI endpoint.

Run:
    python -m pip install fastapi uvicorn requests pydantic
    python examples/02_fastapi_agent.py
"""

from __future__ import annotations

import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from god_ai import aura


class Article(BaseModel):
    title: str
    summary: str
    source_url: str


app = FastAPI(title="God AI Structured Article API")
_articles: list[Article] = []


def fetch_text(url: str) -> str:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.text[:12000]


def structure_article(raw: str, source_url: str) -> Article:
    parsed = aura.parse(
        f"Extract a short title and summary from this web text:\n{raw}",
        Article,
    )
    return parsed.model_copy(update={"source_url": source_url})


@app.get("/articles", response_model=list[Article])
def articles() -> list[Article]:
    return _articles


@app.post("/articles/scrape", response_model=Article)
def scrape(url: str) -> Article:
    try:
        article = structure_article(fetch_text(url), url)
    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    _articles.append(article)
    return article


def main() -> None:
    import uvicorn

    aura.configure(
        provider=os.getenv("AURA_PROVIDER", "ollama"),
        model=os.getenv("AURA_MODEL", "llama3"),
        base_url=os.getenv("AURA_BASE_URL", "http://localhost:11434/v1"),
    )
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", "8001")))


if __name__ == "__main__":
    main()
