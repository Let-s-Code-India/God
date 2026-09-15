"""Localhost web API and static UI for AURA."""

from __future__ import annotations

import json
from pathlib import Path

from command_executor import CommandExecutor
from config import Settings
from llm_handler import LLMHandler
from memory_manager import MemoryManager
from system_detector import system_prompt

ROOT = Path(__file__).resolve().parent


def create_app(settings: Settings):
    try:
        from fastapi import FastAPI
        from fastapi.responses import FileResponse
        from pydantic import BaseModel
    except ImportError as exc:
        raise RuntimeError("Web mode requires fastapi and uvicorn. Run: pip install -r requirements.txt") from exc

    class ChatRequest(BaseModel):
        message: str
        session_id: str = "web"
        execute: bool = True

    app = FastAPI(title=settings.assistant_name)
    llm = LLMHandler(settings)
    memory = MemoryManager(settings.memory_backend)
    executor = CommandExecutor(settings)

    @app.get("/")
    def index():
        return FileResponse(ROOT / "static" / "index.html")

    @app.get("/api/health")
    def health():
        return {"name": settings.assistant_name, "provider": settings.provider, "security": settings.security_mode}

    @app.post("/api/chat")
    def chat(request: ChatRequest):
        memory.add(request.session_id, "user", request.message)
        messages = [{"role": "user", "content": request.message}]
        context = memory.context_text(request.session_id)
        system = f"You are {settings.assistant_name}. {system_prompt()}\nPrior context:\n{context}"
        response = llm.chat(messages, system)
        def debug_command(command: str, error: str) -> str:
            repair = llm.chat([{"role": "user", "content": f"The command failed. Fix it and return only one fenced shell command.\nCommand:\n{command}\nError:\n{error}"}], system)
            repaired = executor.extract(repair.text)
            return repaired[0] if repaired else command

        results = executor.run(response.text, debug_command) if request.execute else []
        memory.add(request.session_id, "assistant", response.text)
        return {"response": response.text, "executions": [{"command": item.command, "output": item.output, "returncode": item.returncode, "attempts": item.attempts} for item in results]}

    return app


def serve(settings: Settings) -> None:
    import uvicorn
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port)
