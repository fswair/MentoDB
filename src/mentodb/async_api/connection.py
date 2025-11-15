"""Async SQLite connection wrapper for MentoDB."""
import aiosqlite
from typing import Self


class AsyncConnection:
    """
    Async SQLite connection wrapper with context manager support.

    Example:
        async with AsyncConnection("mydb.db") as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM users")
    """

    def __init__(
        self,
        database: str = "./database.db",
        timeout: float = 5.0,
    ):
        """
        Initialize async database connection.

        Args:
            database: Path to SQLite database file
            timeout: Connection timeout in seconds
        """
        self.database = database
        self.timeout = timeout
        self.connection: aiosqlite.Connection | None = None

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        self.connection = await aiosqlite.connect(
            self.database,
            timeout=self.timeout,
        )
        # Enable foreign key support
        await self.connection.execute("PRAGMA foreign_keys = ON")
        await self.connection.commit()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Async context manager exit - commits or rolls back based on exception."""
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.close()
        return False  # Don't suppress exceptions

    async def cursor(self) -> aiosqlite.Cursor:
        """Get a new async cursor."""
        if not self.connection:
            raise RuntimeError("Connection not initialized. Use 'async with' context manager.")
        return await self.connection.cursor()

    async def commit(self) -> None:
        """Commit current transaction."""
        if self.connection:
            await self.connection.commit()

    async def rollback(self) -> None:
        """Rollback current transaction."""
        if self.connection:
            await self.connection.rollback()

    async def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            await self.connection.close()

    async def execute(
        self, query: str, params: tuple = (), auto_commit: bool = True
    ) -> aiosqlite.Cursor:
        """
        Execute a query with optional parameters.

        Args:
            query: SQL query to execute
            params: Query parameters (for parameterized queries)
            auto_commit: Whether to auto-commit after execution

        Returns:
            Cursor with query results
        """
        if not self.connection:
            raise RuntimeError("Connection not initialized. Use 'async with' context manager.")

        cursor = await self.cursor()
        await cursor.execute(query, params)
        if auto_commit:
            await self.commit()
        return cursor
