"""Create the project database and tables from sql/schema.sql."""

from __future__ import annotations

from pathlib import Path

from placement_system.config import load_settings
from placement_system.database import connect_database


def initialize_database() -> None:
    settings = load_settings()
    project_root = Path(__file__).resolve().parents[2]
    schema_path = project_root / "sql" / "schema.sql"
    statements = [part.strip() for part in schema_path.read_text(encoding="utf-8").split(";")]

    connection = connect_database(settings, include_database=False)
    try:
        with connection.cursor() as cursor:
            for statement in statements:
                if statement:
                    cursor.execute(statement)
        connection.commit()
    finally:
        connection.close()

    print(f"Database '{settings.db_name}' and its tables are ready.")


if __name__ == "__main__":
    initialize_database()
