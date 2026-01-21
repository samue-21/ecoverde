from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import request, error
import zipfile
import io


def _data_dir() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        data_dir = base / "EcoverdeApp"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    return Path.cwd()


@dataclass
class BackupConfig:
    api_url: str = ""
    api_token: str = ""
    backup_key: str = ""
    enabled: bool = False
    auto_interval_sec: int = 300
    last_hash: str = ""
    last_backup_at: str = ""


class BackupClient:
    def __init__(self) -> None:
        self._config_path = _data_dir() / "backup_config.json"

    def load_config(self) -> BackupConfig:
        if not self._config_path.exists():
            return BackupConfig()
        try:
            data = json.loads(self._config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return BackupConfig()
        cfg = BackupConfig()
        for key, value in data.items():
            if hasattr(cfg, key):
                setattr(cfg, key, value)
        return cfg

    def save_config(self, cfg: BackupConfig) -> None:
        self._config_path.write_text(
            json.dumps(asdict(cfg), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def auto_backup_if_changed(self) -> bool:
        cfg = self.load_config()
        if not cfg.enabled:
            return False
        if not cfg.api_url or not cfg.backup_key:
            return False
        payload = self._build_payload()
        payload_hash = self._hash_payload(payload)
        if payload_hash == cfg.last_hash:
            return False
        ok = self.send_backup(cfg, payload)
        if ok:
            cfg.last_hash = payload_hash
            cfg.last_backup_at = datetime.now(timezone.utc).isoformat()
            self.save_config(cfg)
        return ok

    def send_backup(self, cfg: BackupConfig, payload: dict[str, Any] | None = None) -> bool:
        if payload is None:
            payload = self._build_payload()
        body = json.dumps(
            {
                "backup_key": cfg.backup_key,
                "payload": payload,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        url = cfg.api_url.rstrip("/") + "/backup"
        req = request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        if cfg.api_token:
            req.add_header("Authorization", f"Bearer {cfg.api_token}")
        try:
            with request.urlopen(req, timeout=20) as resp:
                return 200 <= resp.status < 300
        except error.URLError:
            return False

    def test_connection(self, cfg: BackupConfig) -> bool:
        url = cfg.api_url.rstrip("/") + "/health"
        req = request.Request(url, method="GET")
        if cfg.api_token:
            req.add_header("Authorization", f"Bearer {cfg.api_token}")
        try:
            with request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except error.URLError:
            return False

    def restore_backup(self, cfg: BackupConfig) -> bool:
        url = cfg.api_url.rstrip("/") + f"/backup/{cfg.backup_key}"
        req = request.Request(url, method="GET")
        if cfg.api_token:
            req.add_header("Authorization", f"Bearer {cfg.api_token}")
        try:
            with request.urlopen(req, timeout=20) as resp:
                if resp.status != 200:
                    return False
                data = json.loads(resp.read().decode("utf-8"))
        except (error.URLError, json.JSONDecodeError):
            return False
        payload = data.get("payload")
        if not isinstance(payload, dict):
            return False
        return self._apply_payload(payload)

    def _build_payload(self) -> dict[str, Any]:
        data_dir = _data_dir()
        payload = {
            "app": "EcoverdeApp",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files": {},
        }

        def add_file(name: str, path: Path) -> None:
            if not path.exists():
                return
            raw = path.read_bytes()
            payload["files"][name] = {
                "encoding": "base64",
                "content": base64.b64encode(raw).decode("ascii"),
            }

        add_file("ecoverde.db", data_dir / "ecoverde.db")
        add_file("planilha_gastos.json", data_dir / "planilha_gastos.json")
        add_file("planilha_templates.json", data_dir / "planilha_templates.json")

        contracts_dir = Path.cwd() / "contracts"
        if contracts_dir.exists() and contracts_dir.is_dir():
            zipped = self._zip_folder(contracts_dir)
            payload["files"]["contracts.zip"] = {
                "encoding": "base64",
                "content": base64.b64encode(zipped).decode("ascii"),
            }
        return payload

    def _apply_payload(self, payload: dict[str, Any]) -> bool:
        files = payload.get("files")
        if not isinstance(files, dict):
            return False
        data_dir = _data_dir()
        for name, entry in files.items():
            if not isinstance(entry, dict):
                continue
            if entry.get("encoding") != "base64":
                continue
            content = entry.get("content")
            if not content:
                continue
            raw = base64.b64decode(content.encode("ascii"))
            if name == "contracts.zip":
                self._extract_zip(raw, Path.cwd() / "contracts")
                continue
            target = data_dir / name
            target.write_bytes(raw)
        return True

    def _zip_folder(self, folder: Path) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in folder.rglob("*"):
                if path.is_file():
                    zf.write(path, path.relative_to(folder))
        return buffer.getvalue()

    def _extract_zip(self, raw: bytes, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(raw), "r") as zf:
            zf.extractall(dest)

    def _hash_payload(self, payload: dict[str, Any]) -> str:
        hasher = hashlib.sha256()
        files = payload.get("files", {})
        for key in sorted(files.keys()):
            entry = files[key]
            if not isinstance(entry, dict):
                continue
            content = entry.get("content", "")
            if isinstance(content, str):
                hasher.update(content.encode("utf-8"))
        return hasher.hexdigest()
