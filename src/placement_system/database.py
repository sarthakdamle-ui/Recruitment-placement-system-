"""Database connection helpers for the placement system."""

from __future__ import annotations

import mysql.connector
from mysql.connector import MySQLConnection

from placement_system.config import Settings


def connect_database(settings: Settings, *, include_database: bool = True) -> MySQLConnection:
    """Open a MySQL connection using settings loaded from the local environment."""
    options: dict[str, object] = {
        "host": settings.db_host,
        "port": settings.db_port,
        "user": settings.db_user,
        "password": settings.db_password,
        "connection_timeout": 5,
    }
    if include_database:
        options["database"] = settings.db_name
    return mysql.connector.connect(**options)
