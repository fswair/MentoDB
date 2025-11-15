"""Database migration system for schema versioning."""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Callable
import json


class Migration:
    """
    Single migration definition.

    Example:
        def upgrade(conn):
            conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY)")

        def downgrade(conn):
            conn.execute("DROP TABLE users")

        migration = Migration(
            version="001",
            name="create_users_table",
            upgrade=upgrade,
            downgrade=downgrade
        )
    """

    def __init__(
        self,
        version: str,
        name: str,
        upgrade: Callable[[sqlite3.Connection], None],
        downgrade: Callable[[sqlite3.Connection], None] | None = None,
    ):
        """
        Initialize migration.

        Args:
            version: Migration version (e.g., "001", "002")
            name: Migration name (descriptive)
            upgrade: Function to apply migration
            downgrade: Function to revert migration (optional)
        """
        self.version = version
        self.name = name
        self.upgrade = upgrade
        self.downgrade = downgrade
        self.created_at = datetime.now()

    def __repr__(self) -> str:
        return f"Migration({self.version}_{self.name})"


class MigrationManager:
    """
    Manage database migrations and schema versioning.

    Example:
        manager = MigrationManager(connection)
        manager.init()

        # Register migrations
        manager.register(Migration("001", "create_users", upgrade_fn))
        manager.register(Migration("002", "add_email_column", upgrade_fn))

        # Apply migrations
        manager.migrate()

        # Rollback
        manager.rollback(steps=1)
    """

    MIGRATIONS_TABLE = "_migrations"

    def __init__(self, connection: sqlite3.Connection):
        """
        Initialize migration manager.

        Args:
            connection: SQLite connection
        """
        self.connection = connection
        self.migrations: list[Migration] = []

    def init(self) -> None:
        """Initialize migrations table if it doesn't exist."""
        cursor = self.connection.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.MIGRATIONS_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()

    def register(self, migration: Migration) -> None:
        """
        Register a migration.

        Args:
            migration: Migration to register
        """
        self.migrations.append(migration)
        # Sort by version
        self.migrations.sort(key=lambda m: m.version)

    def get_applied_migrations(self) -> list[str]:
        """
        Get list of applied migration versions.

        Returns:
            List of version strings
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT version FROM {self.MIGRATIONS_TABLE} ORDER BY version")
        return [row[0] for row in cursor.fetchall()]

    def get_pending_migrations(self) -> list[Migration]:
        """
        Get list of pending (not yet applied) migrations.

        Returns:
            List of Migration objects
        """
        applied = set(self.get_applied_migrations())
        return [m for m in self.migrations if m.version not in applied]

    def migrate(self, target_version: str | None = None) -> int:
        """
        Apply pending migrations up to target version.

        Args:
            target_version: Version to migrate to (None = latest)

        Returns:
            Number of migrations applied

        Raises:
            ValueError: If target version not found
        """
        pending = self.get_pending_migrations()

        if target_version:
            # Find target in pending
            target_idx = None
            for i, m in enumerate(pending):
                if m.version == target_version:
                    target_idx = i
                    break

            if target_idx is None:
                raise ValueError(f"Target version {target_version} not found in pending migrations")

            pending = pending[:target_idx + 1]

        if not pending:
            return 0

        applied_count = 0
        for migration in pending:
            try:
                # Apply migration
                migration.upgrade(self.connection)

                # Record in migrations table
                cursor = self.connection.cursor()
                cursor.execute(
                    f"INSERT INTO {self.MIGRATIONS_TABLE} (version, name) VALUES (?, ?)",
                    (migration.version, migration.name)
                )
                self.connection.commit()

                applied_count += 1
                print(f"✓ Applied migration {migration.version}_{migration.name}")

            except Exception as e:
                self.connection.rollback()
                print(f"✗ Failed to apply migration {migration.version}_{migration.name}: {e}")
                raise

        return applied_count

    def rollback(self, steps: int = 1) -> int:
        """
        Rollback last N migrations.

        Args:
            steps: Number of migrations to rollback

        Returns:
            Number of migrations rolled back

        Raises:
            ValueError: If trying to rollback more than applied
        """
        applied = self.get_applied_migrations()

        if steps > len(applied):
            raise ValueError(f"Cannot rollback {steps} migrations, only {len(applied)} applied")

        # Get migrations to rollback (in reverse order)
        versions_to_rollback = applied[-steps:]
        versions_to_rollback.reverse()

        rolled_back = 0
        for version in versions_to_rollback:
            # Find migration
            migration = next((m for m in self.migrations if m.version == version), None)

            if not migration:
                print(f"⚠ Migration {version} not found in registered migrations, skipping")
                continue

            if not migration.downgrade:
                raise ValueError(f"Migration {version} has no downgrade function")

            try:
                # Apply downgrade
                migration.downgrade(self.connection)

                # Remove from migrations table
                cursor = self.connection.cursor()
                cursor.execute(
                    f"DELETE FROM {self.MIGRATIONS_TABLE} WHERE version = ?",
                    (version,)
                )
                self.connection.commit()

                rolled_back += 1
                print(f"✓ Rolled back migration {migration.version}_{migration.name}")

            except Exception as e:
                self.connection.rollback()
                print(f"✗ Failed to rollback migration {version}: {e}")
                raise

        return rolled_back

    def status(self) -> dict:
        """
        Get migration status.

        Returns:
            Dictionary with migration status information
        """
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()

        return {
            "total_migrations": len(self.migrations),
            "applied_count": len(applied),
            "pending_count": len(pending),
            "applied_versions": applied,
            "pending_versions": [m.version for m in pending],
            "current_version": applied[-1] if applied else None,
        }

    def reset(self) -> None:
        """
        Rollback all migrations (DESTRUCTIVE).

        Warning: This will drop all tables created by migrations!
        """
        applied = self.get_applied_migrations()
        if applied:
            self.rollback(steps=len(applied))

    def export_schema(self, output_path: str | Path) -> None:
        """
        Export current database schema to SQL file.

        Args:
            output_path: Path to output file
        """
        cursor = self.connection.cursor()

        # Get all CREATE statements
        cursor.execute("""
            SELECT sql FROM sqlite_master
            WHERE sql IS NOT NULL
            AND type IN ('table', 'index', 'trigger', 'view')
            ORDER BY type DESC, name
        """)

        schema_sql = "\n\n".join(row[0] + ";" for row in cursor.fetchall())

        # Write to file
        Path(output_path).write_text(schema_sql, encoding="utf-8")

    def import_schema(self, input_path: str | Path) -> None:
        """
        Import schema from SQL file.

        Args:
            input_path: Path to SQL file
        """
        schema_sql = Path(input_path).read_text(encoding="utf-8")
        self.connection.executescript(schema_sql)
        self.connection.commit()
