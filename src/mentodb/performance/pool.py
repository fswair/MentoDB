"""Connection pool for managing multiple database connections."""
import sqlite3
import threading
from queue import Queue, Empty
from typing import Any
from contextlib import contextmanager


class ConnectionPool:
    """
    Thread-safe connection pool for SQLite connections.

    Example:
        pool = ConnectionPool("mydb.db", max_connections=10)

        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
    """

    def __init__(
        self,
        database: str,
        max_connections: int = 5,
        timeout: float = 5.0,
        check_same_thread: bool = False,
    ):
        """
        Initialize connection pool.

        Args:
            database: Database file path
            max_connections: Maximum number of connections in pool
            timeout: Connection timeout in seconds
            check_same_thread: SQLite check_same_thread parameter
        """
        self.database = database
        self.max_connections = max_connections
        self.timeout = timeout
        self.check_same_thread = check_same_thread

        self._pool: Queue = Queue(maxsize=max_connections)
        self._lock = threading.Lock()
        self._created_connections = 0

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        conn = sqlite3.connect(
            self.database,
            timeout=self.timeout,
            check_same_thread=self.check_same_thread,
        )
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool (context manager).

        Yields:
            SQLite connection

        Example:
            with pool.get_connection() as conn:
                # Use connection
                pass
        """
        conn = None
        try:
            # Try to get existing connection from pool
            try:
                conn = self._pool.get_nowait()
            except Empty:
                # Create new connection if under limit
                with self._lock:
                    if self._created_connections < self.max_connections:
                        conn = self._create_connection()
                        self._created_connections += 1
                    else:
                        # Wait for available connection
                        conn = self._pool.get(timeout=self.timeout)

            yield conn

        finally:
            # Return connection to pool
            if conn:
                try:
                    # Rollback any uncommitted transactions
                    conn.rollback()
                    # Return to pool
                    self._pool.put_nowait(conn)
                except Exception:
                    # If pool is full, close connection
                    conn.close()
                    with self._lock:
                        self._created_connections -= 1

    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self._lock:
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                    self._created_connections -= 1
                except Empty:
                    break

    def size(self) -> int:
        """Get current number of connections in pool."""
        return self._pool.qsize()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close all connections."""
        self.close_all()
        return False

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close_all()
        except Exception:
            pass
