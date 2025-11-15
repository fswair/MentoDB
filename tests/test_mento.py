"""Tests for Mento ORM class."""
import tempfile
from pathlib import Path
import pytest
from pydantic import BaseModel
from connection import MentoConnection
from utils import Mento, PrimaryKey


class TestModel(BaseModel):
    """Test model for database operations."""

    id: int
    name: str
    age: int


class TestMento:
    """Test suite for Mento ORM."""

    def test_create_table(self):
        """Test table creation from Pydantic model."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            conn = MentoConnection(db_path)
            mento = Mento(conn, default_table="users")
            mento.create("users", model=TestModel)

            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            assert ("users",) in tables
            conn.close()
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_insert_and_select(self):
        """Test inserting and selecting data."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            conn = MentoConnection(db_path)
            mento = Mento(conn, default_table="users")
            mento.create("users", model=TestModel)

            # Insert data
            mento.insert("users", data={"id": 1, "name": "Alice", "age": 30})

            # Select data
            results = mento.select(from_table="users")
            assert len(results) == 1
            assert results[0]["name"] == "Alice"
            assert results[0]["age"] == 30

            conn.close()
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_update(self):
        """Test updating data."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            conn = MentoConnection(db_path)
            mento = Mento(conn, default_table="users")
            mento.create("users", model=TestModel)
            mento.insert("users", data={"id": 1, "name": "Alice", "age": 30})

            # Update data
            mento.update("users", data={"age": 31}, where={"id": 1})

            # Verify update
            results = mento.select(from_table="users", where={"id": 1})
            assert results[0]["age"] == 31

            conn.close()
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_delete(self):
        """Test deleting data."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            conn = MentoConnection(db_path)
            mento = Mento(conn, default_table="users")
            mento.create("users", model=TestModel)
            mento.insert("users", data={"id": 1, "name": "Alice", "age": 30})

            # Delete data
            mento.delete("users", where={"id": 1})

            # Verify deletion
            results = mento.select(from_table="users")
            assert len(results) == 0

            conn.close()
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_sql_injection_protection(self):
        """Test that SQL injection is prevented."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            conn = MentoConnection(db_path)
            mento = Mento(conn, default_table="users")
            mento.create("users", model=TestModel)

            # Try SQL injection in table name
            with pytest.raises(ValueError, match="Invalid table name"):
                mento.create("users; DROP TABLE users--", model=TestModel)

            # Verify table still exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            assert ("users",) in tables

            conn.close()
        finally:
            Path(db_path).unlink(missing_ok=True)
