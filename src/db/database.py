"""Database connection management for Oil Well Time Series API."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from src.config import DATABASE_PATH


def init_database() -> None:
    """Initialize the database by executing schema.sql.

    Creates tables and indexes if they don't exist.
    """
    schema_path = Path(__file__).parent / "schema.sql"

    with sqlite3.connect(DATABASE_PATH) as conn:
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Get a database connection context manager.

    Yields:
        sqlite3.Connection: Database connection with row factory enabled.

    Example:
        ```python
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM wells")
            results = cursor.fetchall()
        ```
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()


def get_db_connection_for_fastapi() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency for database connections.

    This function is used with FastAPI's Depends() to inject database connections
    into route handlers.

    Yields:
        sqlite3.Connection: Database connection.

    Example:
        ```python
        @app.get("/wells")
        def get_wells(db: sqlite3.Connection = Depends(get_db_connection_for_fastapi)):
            cursor = db.cursor()
            cursor.execute("SELECT * FROM wells")
            return cursor.fetchall()
        ```
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
