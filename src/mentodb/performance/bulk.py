"""Bulk operations for efficient batch processing."""
from typing import Any
from pydantic import BaseModel
import sqlite3


class BulkOperations:
    """
    Bulk operations for efficient batch insert/update/delete.

    Example:
        bulk = BulkOperations(connection)
        bulk.bulk_insert("users", [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ])
    """

    def __init__(self, connection: "sqlite3.Connection"):
        """
        Initialize bulk operations.

        Args:
            connection: SQLite connection
        """
        self.connection = connection

    def bulk_insert(
        self,
        table: str,
        data: list[dict[str, Any]],
        batch_size: int = 1000,
    ) -> int:
        """
        Bulk insert multiple rows efficiently.

        Args:
            table: Table name
            data: List of dictionaries with row data
            batch_size: Number of rows per batch

        Returns:
            Number of rows inserted

        Raises:
            ValueError: If data is empty or inconsistent
        """
        if not data:
            raise ValueError("No data provided for bulk insert")

        # Validate table name
        if not table or not table.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table}")

        # Validate all dicts have same keys
        keys = set(data[0].keys())
        for row in data[1:]:
            if set(row.keys()) != keys:
                raise ValueError("All rows must have the same columns")

        columns = list(keys)
        placeholders = ', '.join('?' * len(columns))
        column_names = ', '.join(columns)
        query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

        cursor = self.connection.cursor()
        total_inserted = 0

        # Insert in batches
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            values = [tuple(row[col] for col in columns) for row in batch]

            cursor.executemany(query, values)
            total_inserted += cursor.rowcount

        self.connection.commit()
        return total_inserted

    def bulk_update(
        self,
        table: str,
        data: list[dict[str, Any]],
        key_column: str = "id",
        batch_size: int = 1000,
    ) -> int:
        """
        Bulk update multiple rows efficiently.

        Args:
            table: Table name
            data: List of dictionaries with row data
            key_column: Column to use as key for WHERE clause
            batch_size: Number of rows per batch

        Returns:
            Number of rows updated

        Raises:
            ValueError: If data is empty or key_column not found
        """
        if not data:
            raise ValueError("No data provided for bulk update")

        # Validate table name
        if not table or not table.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table}")

        # Validate key column exists in data
        if key_column not in data[0]:
            raise ValueError(f"Key column '{key_column}' not found in data")

        # Build update query
        columns = [col for col in data[0].keys() if col != key_column]
        set_parts = [f"{col} = ?" for col in columns]
        query = f"UPDATE {table} SET {', '.join(set_parts)} WHERE {key_column} = ?"

        cursor = self.connection.cursor()
        total_updated = 0

        # Update in batches
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            values = [
                tuple([row[col] for col in columns] + [row[key_column]])
                for row in batch
            ]

            cursor.executemany(query, values)
            total_updated += cursor.rowcount

        self.connection.commit()
        return total_updated

    def bulk_delete(
        self,
        table: str,
        ids: list[Any],
        key_column: str = "id",
        batch_size: int = 1000,
    ) -> int:
        """
        Bulk delete multiple rows efficiently.

        Args:
            table: Table name
            ids: List of IDs to delete
            key_column: Column to use for WHERE clause
            batch_size: Number of rows per batch

        Returns:
            Number of rows deleted
        """
        if not ids:
            raise ValueError("No IDs provided for bulk delete")

        # Validate table name
        if not table or not table.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table}")

        cursor = self.connection.cursor()
        total_deleted = 0

        # Delete in batches
        for i in range(0, len(ids), batch_size):
            batch = ids[i:i + batch_size]
            placeholders = ', '.join('?' * len(batch))
            query = f"DELETE FROM {table} WHERE {key_column} IN ({placeholders})"

            cursor.execute(query, batch)
            total_deleted += cursor.rowcount

        self.connection.commit()
        return total_deleted

    def bulk_upsert(
        self,
        table: str,
        data: list[dict[str, Any]],
        conflict_columns: list[str],
        batch_size: int = 1000,
    ) -> int:
        """
        Bulk upsert (INSERT or UPDATE on conflict).

        Args:
            table: Table name
            data: List of dictionaries with row data
            conflict_columns: Columns that define uniqueness
            batch_size: Number of rows per batch

        Returns:
            Number of rows affected

        Note:
            Uses SQLite's INSERT OR REPLACE syntax
        """
        if not data:
            raise ValueError("No data provided for bulk upsert")

        # Validate table name
        if not table or not table.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table}")

        columns = list(data[0].keys())
        placeholders = ', '.join('?' * len(columns))
        column_names = ', '.join(columns)

        # Build UPSERT query using INSERT OR REPLACE
        query = f"INSERT OR REPLACE INTO {table} ({column_names}) VALUES ({placeholders})"

        cursor = self.connection.cursor()
        total_affected = 0

        # Upsert in batches
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            values = [tuple(row[col] for col in columns) for row in batch]

            cursor.executemany(query, values)
            total_affected += cursor.rowcount

        self.connection.commit()
        return total_affected
