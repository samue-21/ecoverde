from __future__ import annotations

import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from datetime import datetime, timezone


DB_PATH = os.environ.get("BACKUP_DB", "backup_server.db")
API_TOKEN = os.environ.get("BACKUP_API_TOKEN", "")


def _init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_key TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS backups_key_unique ON backups(backup_key)"
        )
        conn.commit()


class Handler(BaseHTTPRequestHandler):
    def _unauthorized(self) -> None:
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "unauthorized"}).encode("utf-8"))

    def _bad_request(self, message: str) -> None:
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode("utf-8"))

    def _ok(self, data: dict) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _auth_ok(self) -> bool:
        if not API_TOKEN:
            return True
        auth = self.headers.get("Authorization", "")
        return auth == f"Bearer {API_TOKEN}"

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/backup":
            self.send_response(404)
            self.end_headers()
            return
        if not self._auth_ok():
            self._unauthorized()
            return
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length or 0).decode("utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._bad_request("invalid json")
            return
        backup_key = data.get("backup_key")
        payload = data.get("payload")
        if not backup_key or not isinstance(payload, dict):
            self._bad_request("missing backup_key or payload")
            return
        created_at = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                """
                INSERT INTO backups (backup_key, payload_json, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(backup_key)
                DO UPDATE SET payload_json = excluded.payload_json,
                              created_at = excluded.created_at
                """,
                (backup_key, json.dumps(payload), created_at),
            )
            conn.commit()
            backup_id = cur.lastrowid
        self._ok({"status": "ok", "backup_id": backup_id})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            if not self._auth_ok():
                self._unauthorized()
                return
            self._ok({"status": "ok"})
            return
        if not parsed.path.startswith("/backup/"):
            self.send_response(404)
            self.end_headers()
            return
        if not self._auth_ok():
            self._unauthorized()
            return
        backup_key = parsed.path.split("/backup/")[-1]
        if not backup_key:
            self._bad_request("missing backup_key")
            return
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                "SELECT payload_json, created_at FROM backups WHERE backup_key = ? ORDER BY id DESC LIMIT 1",
                (backup_key,),
            ).fetchone()
        if not row:
            self.send_response(404)
            self.end_headers()
            return
        payload_json, created_at = row
        self._ok({"backup_key": backup_key, "created_at": created_at, "payload": json.loads(payload_json)})


def main():
    _init_db()
    host = os.environ.get("BACKUP_HOST", "0.0.0.0")
    port = int(os.environ.get("BACKUP_PORT", "8080"))
    server = HTTPServer((host, port), Handler)
    print(f"Backup server listening on {host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
