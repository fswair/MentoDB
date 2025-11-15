"""Index management for MentoDB."""
from typing import Literal
import sqlite3


IndexType = Literal["btree", "unique"]


class IndexManager:
    """
    Manage database indexes for performance optimization.

    Example:
        idx = IndexManager(connection)
        idx.create_index("users", "idx_email", ["email"], unique=True)
        idx.list_indexes("users")
    """

    def __init__(self, connection: sqlite3.Connection):
        """
        Initialize index manager.

        Args:
            connection: SQLite connection
        """
        self.connection = connection

    def create_index(
        self,
        table: str,
        index_name: str,
        columns: list[str],
        unique: bool = False,
        if_not_exists: bool = True,
    ) -> None:
        """
        Create an index on specified columns.

        Args:
            table: Table name
            index_name: Index name
            columns: List of column names
            unique: Whether to create UNIQUE index
            if_not_exists: Whether to use IF NOT EXISTS clause

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate table name
        if not table or not table.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table}")

        # Validate index name
        if not index_name or not index_name.replace('_', '').isalnum():
            raise ValueError(f"Invalid index name: {index_name}")

        # Validate columns
        if not columns:
            raise ValueError("At least one column is required for index")

        for col in columns:
            if not col.replace('_', '').isalnum():
                raise ValueError(f"Invalid column name: {col}")

        # Build query
        unique_keyword = "UNIQUE " if unique else ""
        exists_clause = "IF NOT EXISTS " if if_not_exists else ""
        columns_str = ", ".join(columns)

        query = f"CREATE {unique_keyword}INDEX {exists_clause}{index_name} ON {table} ({columns_str})"

        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

    def drop_index(self, index_name: str, if_exists: bool = True) -> None:
        """
        Drop an index.

        Args:
            index_name: Index name
            if_exists: Whether to use IF EXISTS clause
        """
        # Validate index name
        if not index_name or not index_name.replace('_', '').isalnum():
            raise ValueError(f"Invalid index name: {index_name}")

        exists_clause = "IF EXISTS " if if_exists else ""
        query = f"DROP INDEX {exists_clause}{index_name}"

        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

    def list_indexes(self, table: str | None = None) -> list[dict[str, any]]:
        """
        List all indexes, optionally filtered by table.

        Args:
            table: Optional table name to filter indexes

        Returns:
            List of index information dictionaries
        """
        cursor = self.connection.cursor()

        if table:
            # Validate table name
            if not table.replace('_', '').isalnum():
                raise ValueError(f"Invalid table name: {table}")

            query = "SELECT name, tbl_name, sql FROM sqlite_master WHERE type = 'index' AND tbl_name = ?"
            cursor.execute(query, (table,))
        else:
            query = "SELECT name, tbl_name, sql FROM sqlite_master WHERE type = 'index'"
            cursor.execute(query)

        results = cursor.fetchall()
        return [
            {
                "name": row[0],
                "table": row[1],
                "sql": row[2],
            }
            for row in results
            if row[0] and not row[0].startswith("sqlite_")  # Filter out SQLite internal indexes
        ]

    def index_exists(self, index_name: str) -> bool:
        """
        Check if an index exists.

        Args:
            index_name: Index name

        Returns:
            True if index exists, False otherwise
        """
        cursor = self.connection.cursor()
        query = "SELECT COUNT(*) FROM sqlite_master WHERE type = 'index' AND name = ?"
        cursor.execute(query, (index_name,))
        count = cursor.fetchone()[0]
        return count > 0

    def analyze(self, table: str | None = None) -> None:
        """
        Run ANALYZE to update index statistics.

        Args:
            table: Optional table name to analyze (analyzes all if None)
        """
        cursor = self.connection.cursor()

        if table:
            # Validate table name
            if not table.replace('_', '').isalnum():
                raise ValueError(f"Invalid table name: {table}")
            cursor.execute(f"ANALYZE {table}")
        else:
            cursor.execute("ANALYZE")

        self.connection.commit()

    def get_index_info(self, index_name: str) -> dict[str, any] | None:
        """
        Get detailed information about an index.

        Args:
            index_name: Index name

        Returns:
            Dictionary with index information or None if not found
        """
        cursor = self.connection.cursor()

        # Get basic info
        query = "SELECT name, tbl_name, sql FROM sqlite_master WHERE type = 'index' AND name = ?"
        cursor.execute(query, (index_name,))
        result = cursor.fetchone()

        if not result:
            return None

        # Get column info
        cursor.execute(f"PRAGMA index_info({index_name})")
        columns = [row[2] for row in cursor.fetchall()]

        return {
            "name": result[0],
            "table": result[1],
            "sql": result[2],
            "columns": columns,
            "unique": "UNIQUE" in (result[2] or "").upper(),
        }
