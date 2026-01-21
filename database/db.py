## Removido SQLAlchemy do Flask, usando apenas SQLAlchemy puro
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker


def _get_data_dir() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "EcoverdeApp"
    return Path.cwd()


_DATA_DIR = _get_data_dir()
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_DB_PATH = _DATA_DIR / "ecoverde.db"

engine = create_engine(f"sqlite:///{_DB_PATH}", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


def ensure_cliente_columns():
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("PRAGMA table_info(cliente_fornecedor)")).fetchall()
            cols = {row[1] for row in rows}
            if "telefone" not in cols:
                conn.execute(text("ALTER TABLE cliente_fornecedor ADD COLUMN telefone VARCHAR(40)"))
    except Exception:
        # Ignore migration errors to avoid blocking the UI
        pass
