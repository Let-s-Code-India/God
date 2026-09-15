"""Small SQLite/JSON conversation store used by the CLI and web API."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class Memory:
    def __init__(self, backend: str = "sqlite", root: Optional[Path] = None) -> None:
        self.root = root or Path.cwd() / "memory"
        self.root.mkdir(parents=True, exist_ok=True)
        self.backend = backend if backend in {"sqlite", "json"} else "sqlite"
        self.db_path = self.root / "god_ai.sqlite3"
        self.json_path = self.root / "conversations.json"
        if self.backend == "sqlite":
            with sqlite3.connect(self.db_path) as db:
                db.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, session TEXT, role TEXT, content TEXT, created_at TEXT)")

    def add(self, session: str, role: str, content: str) -> None:
        stamp = datetime.now(timezone.utc).isoformat()
        if self.backend == "sqlite":
            with sqlite3.connect(self.db_path) as db:
                db.execute("INSERT INTO messages(session, role, content, created_at) VALUES (?, ?, ?, ?)", (session, role, content, stamp))
            return
        records = self._read()
        records.append({"session": session, "role": role, "content": content, "created_at": stamp})
        self.json_path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")

    def recent(self, session: str, limit: int = 12) -> list[dict[str, Any]]:
        if self.backend == "sqlite":
            with sqlite3.connect(self.db_path) as db:
                rows = db.execute("SELECT role, content, created_at FROM messages WHERE session = ? ORDER BY id DESC LIMIT ?", (session, limit)).fetchall()
            return [{"role": row[0], "content": row[1], "created_at": row[2]} for row in reversed(rows)]
        return [item for item in self._read() if item.get("session") == session][-limit:]

    def context(self, session: str) -> str:
        return "\n".join(f"{item['role']}: {item['content']}" for item in self.recent(session))

    def _read(self) -> list[dict[str, Any]]:
        if not self.json_path.exists():
            return []
        try:
            data = json.loads(self.json_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []