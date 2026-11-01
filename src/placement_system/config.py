"""Application configuration loaded from environment variables or a local .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # Friendly message when dependencies have not been installed yet.
    load_dotenv = None


@dataclass(frozen=True)
class Settings:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[2]
    env_file = project_root / ".env"
    if load_dotenv is not None:
        load_dotenv(env_file)

    required = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise ValueError(
            f"Missing configuration: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in your MySQL settings."
        )

    return Settings(
        db_host=os.environ["DB_HOST"],
        db_port=int(os.getenv("DB_PORT", "3306")),
        db_name=os.environ["DB_NAME"],
        db_user=os.environ["DB_USER"],
        db_password=os.environ["DB_PASSWORD"],
    )
