"""Small persistent conversation store with SQLite and JSON fallback."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MemoryManager:
    def __init__(self, backend: str = "sqlite", root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parent / "memory"
        self.root.mkdir(parents=True, exist_ok=True)
        self.backend = backend if backend in {"sqlite", "json"} else "sqlite"
        self.db_path = self.root / "aura.sqlite3"
        self.json_path = self.root / "conversations.json"
        if self.backend == "sqlite":
            with self._connect() as db:
                db.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, session_id TEXT, role TEXT, content TEXT, created_at TEXT)")
                db.commit()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path, timeout=10)

    def add(self, session_id: str, role: str, content: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        if self.backend == "sqlite":
            with self._connect() as db:
                db.execute("INSERT INTO messages(session_id, role, content, created_at) VALUES (?, ?, ?, ?)", (session_id, role, content, timestamp))
                db.commit()
            return
        records = self._read_json()
        records.append({"session_id": session_id, "role": role, "content": content, "created_at": timestamp})
        self._write_json(records)

    def recent(self, session_id: str, limit: int = 12) -> list[dict[str, Any]]:
        if self.backend == "sqlite":
            with self._connect() as db:
                rows = db.execute("SELECT role, content, created_at FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?", (session_id, limit)).fetchall()
            return [{"role": row[0], "content": row[1], "created_at": row[2]} for row in reversed(rows)]
        return [record for record in self._read_json() if record["session_id"] == session_id][-limit:]

    def context_text(self, session_id: str, limit: int = 12) -> str:
        return "\n".join(f"{item['role']}: {item['content']}" for item in self.recent(session_id, limit))

    def add_fact(self, fact: str) -> None:
        facts_path = self.root / "facts.json"
        facts = []
        if facts_path.exists():
            try:
                loaded = json.loads(facts_path.read_text(encoding="utf-8"))
                facts = loaded if isinstance(loaded, list) else []
            except (OSError, json.JSONDecodeError):
                facts = []
        if fact and fact not in facts:
            facts.append(fact)
            facts_path.write_text(json.dumps(facts[-100:], indent=2), encoding="utf-8")

    def facts_text(self) -> str:
        facts_path = self.root / "facts.json"
        if not facts_path.exists():
            return ""
        try:
            facts = json.loads(facts_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return ""
        return "\n".join(f"- {fact}" for fact in facts if isinstance(fact, str))

    def _read_json(self) -> list[dict[str, Any]]:
        if not self.json_path.exists():
            return []
        try:
            data = json.loads(self.json_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def _write_json(self, records: list[dict[str, Any]]) -> None:
        payload = json.dumps(records, indent=2) + "\n"
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.root, delete=False) as temporary:
                temporary.write(payload)
                temporary_path = Path(temporary.name)
            temporary_path.replace(self.json_path)
        except OSError as exc:
            raise RuntimeError(f"Could not write memory file {self.json_path}: {exc}") from exc
