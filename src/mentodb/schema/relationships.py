"""Foreign key and relationship management."""
import sqlite3
from typing import Literal
from dataclasses import dataclass


RelationType = Literal["one_to_one", "one_to_many", "many_to_many"]
OnAction = Literal["CASCADE", "SET NULL", "SET DEFAULT", "RESTRICT", "NO ACTION"]


@dataclass
class ForeignKey:
    """
    Foreign key definition.

    Example:
        fk = ForeignKey(
            from_table="orders",
            from_column="user_id",
            to_table="users",
            to_column="id",
            on_delete="CASCADE"
        )
    """

    from_table: str
    from_column: str
    to_table: str
    to_column: str
    on_delete: OnAction = "NO ACTION"
    on_update: OnAction = "NO ACTION"
    name: str | None = None


class RelationshipManager:
    """
    Manage table relationships and foreign keys.

    Example:
        rm = RelationshipManager(connection)

        # Add foreign key
        rm.add_foreign_key(
            from_table="orders",
            from_column="user_id",
            to_table="users",
            to_column="id",
            on_delete="CASCADE"
        )

        # Query with JOIN
        results = rm.join(
            from_table="orders",
            join_table="users",
            on="orders.user_id = users.id"
        )
    """

    def __init__(self, connection: sqlite3.Connection):
        """
        Initialize relationship manager.

        Args:
            connection: SQLite connection
        """
        self.connection = connection

    def add_foreign_key(
        self,
        from_table: str,
        from_column: str,
        to_table: str,
        to_column: str,
        on_delete: OnAction = "NO ACTION",
        on_update: OnAction = "NO ACTION",
    ) -> None:
        """
        Add foreign key constraint to existing table.

        Note: SQLite doesn't support ALTER TABLE ADD CONSTRAINT for foreign keys.
        This method will recreate the table with the constraint.

        Args:
            from_table: Source table name
            from_column: Source column name
            to_table: Referenced table name
            to_column: Referenced column name
            on_delete: ON DELETE action
            on_update: ON UPDATE action
        """
        # Get current table schema
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{from_table}'")
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"Table '{from_table}' not found")

        # This is a simplified implementation
        # In production, you'd want to parse the CREATE TABLE statement
        # and add the FOREIGN KEY constraint
        print(f"⚠ Adding foreign keys to existing tables requires table recreation in SQLite")
        print(f"  Recommended: Define foreign keys in initial CREATE TABLE statement")

    def create_table_with_fk(
        self,
        table_name: str,
        columns: dict[str, str],
        foreign_keys: list[ForeignKey],
    ) -> None:
        """
        Create table with foreign key constraints.

        Args:
            table_name: Table name
            columns: Dictionary of column_name: column_type
            foreign_keys: List of ForeignKey definitions

        Example:
            rm.create_table_with_fk(
                "orders",
                {
                    "id": "INTEGER PRIMARY KEY",
                    "user_id": "INTEGER NOT NULL",
                    "total": "REAL"
                },
                [ForeignKey("orders", "user_id", "users", "id", "CASCADE")]
            )
        """
        # Build column definitions
        column_defs = [f"{name} {type_}" for name, type_ in columns.items()]

        # Build foreign key constraints
        fk_defs = []
        for fk in foreign_keys:
            fk_def = f"FOREIGN KEY ({fk.from_column}) REFERENCES {fk.to_table}({fk.to_column})"
            if fk.on_delete != "NO ACTION":
                fk_def += f" ON DELETE {fk.on_delete}"
            if fk.on_update != "NO ACTION":
                fk_def += f" ON UPDATE {fk.on_update}"
            fk_defs.append(fk_def)

        # Combine all definitions
        all_defs = column_defs + fk_defs
        definitions = ",\n    ".join(all_defs)

        # Create table
        query = f"CREATE TABLE {table_name} (\n    {definitions}\n)"
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

    def get_foreign_keys(self, table: str) -> list[dict]:
        """
        Get foreign key information for a table.

        Args:
            table: Table name

        Returns:
            List of foreign key info dictionaries
        """
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA foreign_key_list({table})")

        fks = []
        for row in cursor.fetchall():
            fks.append({
                "id": row[0],
                "seq": row[1],
                "table": row[2],  # Referenced table
                "from": row[3],   # Column in this table
                "to": row[4],     # Column in referenced table
                "on_update": row[5],
                "on_delete": row[6],
                "match": row[7],
            })

        return fks

    def join(
        self,
        from_table: str,
        join_table: str,
        on: str,
        join_type: str = "INNER",
        select_columns: list[str] | None = None,
        where: dict[str, any] | None = None,
    ) -> list[dict]:
        """
        Perform JOIN query.

        Args:
            from_table: First table
            join_table: Table to join with
            on: JOIN condition (e.g., "orders.user_id = users.id")
            join_type: Type of join (INNER, LEFT, RIGHT, FULL)
            select_columns: Columns to select (None = all)
            where: WHERE conditions

        Returns:
            List of result dictionaries

        Example:
            results = rm.join(
                from_table="orders",
                join_table="users",
                on="orders.user_id = users.id",
                select_columns=["orders.id", "users.name", "orders.total"]
            )
        """
        # Build SELECT clause
        if select_columns:
            columns = ", ".join(select_columns)
        else:
            columns = f"{from_table}.*, {join_table}.*"

        # Build query
        query = f"SELECT {columns} FROM {from_table} {join_type} JOIN {join_table} ON {on}"
        params = []

        # Add WHERE clause if provided
        if where:
            where_parts = []
            for key, value in where.items():
                where_parts.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(where_parts)

        # Execute query
        cursor = self.connection.cursor()
        cursor.execute(query, tuple(params))

        # Get column names
        column_names = [desc[0] for desc in cursor.description]

        # Format results
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(column_names, row)))

        return results

    def one_to_many(
        self,
        parent_table: str,
        child_table: str,
        parent_id_column: str = "id",
        foreign_key_column: str = None,
        parent_id: any = None,
    ) -> dict:
        """
        Query one-to-many relationship.

        Args:
            parent_table: Parent table name
            child_table: Child table name
            parent_id_column: ID column in parent table
            foreign_key_column: Foreign key column in child table
            parent_id: Specific parent ID to query

        Returns:
            Dictionary with parent and children

        Example:
            # Get user with all their orders
            result = rm.one_to_many(
                parent_table="users",
                child_table="orders",
                foreign_key_column="user_id",
                parent_id=1
            )
        """
        if foreign_key_column is None:
            foreign_key_column = f"{parent_table[:-1]}_id"  # users -> user_id

        cursor = self.connection.cursor()

        # Get parent
        cursor.execute(f"SELECT * FROM {parent_table} WHERE {parent_id_column} = ?", (parent_id,))
        parent_row = cursor.fetchone()

        if not parent_row:
            return None

        parent_columns = [desc[0] for desc in cursor.description]
        parent = dict(zip(parent_columns, parent_row))

        # Get children
        cursor.execute(
            f"SELECT * FROM {child_table} WHERE {foreign_key_column} = ?",
            (parent_id,)
        )
        child_rows = cursor.fetchall()
        child_columns = [desc[0] for desc in cursor.description]

        children = [dict(zip(child_columns, row)) for row in child_rows]
        parent[child_table] = children

        return parent

    def many_to_many(
        self,
        table1: str,
        table2: str,
        junction_table: str,
        table1_fk: str,
        table2_fk: str,
        table1_id: any = None,
    ) -> dict:
        """
        Query many-to-many relationship through junction table.

        Args:
            table1: First table name
            table2: Second table name
            junction_table: Junction/pivot table name
            table1_fk: Foreign key to table1 in junction table
            table2_fk: Foreign key to table2 in junction table
            table1_id: Specific ID from table1 to query

        Returns:
            Dictionary with table1 record and related table2 records

        Example:
            # Get student with all enrolled courses
            result = rm.many_to_many(
                table1="students",
                table2="courses",
                junction_table="enrollments",
                table1_fk="student_id",
                table2_fk="course_id",
                table1_id=1
            )
        """
        cursor = self.connection.cursor()

        # Get record from table1
        cursor.execute(f"SELECT * FROM {table1} WHERE id = ?", (table1_id,))
        record1 = cursor.fetchone()

        if not record1:
            return None

        columns1 = [desc[0] for desc in cursor.description]
        result = dict(zip(columns1, record1))

        # Get related records from table2 through junction table
        query = f"""
            SELECT {table2}.*
            FROM {table2}
            INNER JOIN {junction_table} ON {table2}.id = {junction_table}.{table2_fk}
            WHERE {junction_table}.{table1_fk} = ?
        """
        cursor.execute(query, (table1_id,))
        records2 = cursor.fetchall()

        if records2:
            columns2 = [desc[0] for desc in cursor.description]
            result[table2] = [dict(zip(columns2, row)) for row in records2]
        else:
            result[table2] = []

        return result
