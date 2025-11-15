"""Tests for MentoConnection class."""
import tempfile
import sqlite3
from pathlib import Path
import pytest
from connection import MentoConnection


class TestMentoConnection:
    """Test suite for MentoConnection."""

    def test_connection_creation(self):
        """Test basic connection creation."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            conn = MentoConnection(db_path)
            assert conn.connection is not None
            assert isinstance(conn.connection, sqlite3.Connection)
            conn.close()
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_context_manager(self):
        """Test context manager functionality."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            with MentoConnection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
                conn.commit()

            # Verify table was created and connection closed
            with MentoConnection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                assert ("test",) in tables
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_execute_with_params(self):
        """Test parameterized query execution."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            with MentoConnection(db_path) as conn:
                conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
                conn.execute(
                    "INSERT INTO users VALUES (?, ?)",
                    params=(1, "Alice"),
                )

                cursor = conn.execute("SELECT * FROM users WHERE id = ?", params=(1,))
                result = cursor.fetchone()
                assert result == (1, "Alice")
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_rollback_on_exception(self):
        """Test that transactions rollback on exceptions."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            # Create initial table
            with MentoConnection(db_path) as conn:
                conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
                conn.execute("INSERT INTO test VALUES (1)")

            # Try to insert duplicate (should rollback)
            try:
                with MentoConnection(db_path) as conn:
                    conn.execute("INSERT INTO test VALUES (2)")
                    conn.execute("INSERT INTO test VALUES (1)")  # Duplicate!
            except sqlite3.IntegrityError:
                pass

            # Verify rollback happened
            with MentoConnection(db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM test")
                count = cursor.fetchone()[0]
                assert count == 1  # Only original row should exist
        finally:
            Path(db_path).unlink(missing_ok=True)
