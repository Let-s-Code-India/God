"""Optional FastAPI localhost interface."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from .config import configure
from .executor import run_commands
from .llm import LLMClient
from .memory import Memory
from .system import system_prompt


def create_app():
    try:
        from fastapi import FastAPI
        from fastapi.responses import FileResponse
        from pydantic import BaseModel
    except ImportError as exc:
        raise RuntimeError("Web mode requires fastapi and uvicorn") from exc
    config = configure()
    client, memory = LLMClient(config), Memory("json")

    class ChatRequest(BaseModel):
        message: str
        session_id: str = "web"
        execute: bool = True

    app = FastAPI(title="God AI")

    @app.get("/")
    def index():
        return FileResponse(Path(__file__).parent / "static" / "index.html")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "provider": config.provider, "model": config.model}

    @app.post("/api/chat")
    def chat(request: ChatRequest):
        memory.add(request.session_id, "user", request.message)
        response = client.chat([{"role": "user", "content": request.message}], f"You are a practical assistant. {system_prompt()}\n{memory.context(request.session_id)}")
        results = run_commands(response.text, safe=True) if request.execute else []
        memory.add(request.session_id, "assistant", response.text)
        return {"response": response.text, "executions": [asdict(result) for result in results]}
    return app


def serve() -> None:
    import uvicorn
    configure()
    uvicorn.run(create_app(), host="127.0.0.1", port=8000)