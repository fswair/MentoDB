from sqlite3 import connect
import sqlite3
from typing import Self


class Connection:
    """
    Modern SQLite connection wrapper with context manager support.

    Example:
        with Connection("mydb.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
    """

    def __init__(
        self,
        database: str = "./database.db",
        check_same_thread: bool = False,
        timeout: float = 5.0,
    ):
        """
        Initialize database connection.

        Args:
            database: Path to SQLite database file
            check_same_thread: Whether to check thread safety
            timeout: Connection timeout in seconds
        """
        self.database = database
        self.connection: sqlite3.Connection = connect(
            database=database,
            check_same_thread=check_same_thread,
            timeout=timeout,
        )
        # Enable foreign key support
        self.connection.execute("PRAGMA foreign_keys = ON")

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit - commits or rolls back based on exception."""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
        return False  # Don't suppress exceptions

    def cursor(self) -> sqlite3.Cursor:
        """Get a new cursor."""
        return self.connection.cursor()

    def commit(self) -> None:
        """Commit current transaction."""
        self.connection.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        self.connection.rollback()

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()

    def execute(
        self, query: str, params: tuple = (), auto_commit: bool = True
    ) -> sqlite3.Cursor:
        """
        Execute a query with optional parameters.

        Args:
            query: SQL query to execute
            params: Query parameters (for parameterized queries)
            auto_commit: Whether to auto-commit after execution

        Returns:
            Cursor with query results
        """
        cursor = self.cursor()
        cursor.execute(query, params)
        if auto_commit:
            self.commit()
        return cursor
