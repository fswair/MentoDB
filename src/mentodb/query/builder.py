"""Fluent query builder for MentoDB."""
from typing import Any, Self
from collections.abc import Callable


class QueryBuilder:
    """
    Fluent API query builder for constructing SQL queries.

    Example:
        query = (QueryBuilder("users")
            .select("id", "name", "email")
            .where("age", ">", 18)
            .where("active", "=", True)
            .order_by("name", "ASC")
            .limit(10)
            .build())
    """

    def __init__(self, table: str):
        """
        Initialize query builder.

        Args:
            table: Table name
        """
        self.table = table
        self._select_columns: list[str] = []
        self._where_conditions: list[tuple[str, str, Any]] = []
        self._order_by_columns: list[tuple[str, str]] = []
        self._limit_value: int | None = None
        self._offset_value: int | None = None
        self._join_clauses: list[str] = []
        self._group_by_columns: list[str] = []
        self._having_conditions: list[str] = []
        self._distinct: bool = False
        self._operation: str = "SELECT"  # SELECT, INSERT, UPDATE, DELETE
        self._update_data: dict[str, Any] = {}
        self._insert_data: dict[str, Any] = {}

    def select(self, *columns: str) -> Self:
        """
        Set columns to select.

        Args:
            *columns: Column names to select

        Returns:
            Self for chaining
        """
        self._operation = "SELECT"
        self._select_columns = list(columns) if columns else ["*"]
        return self

    def distinct(self) -> Self:
        """Add DISTINCT to SELECT."""
        self._distinct = True
        return self

    def where(self, column: str, operator: str, value: Any) -> Self:
        """
        Add WHERE condition.

        Args:
            column: Column name
            operator: Comparison operator (=, !=, >, <, >=, <=, LIKE, IN)
            value: Value to compare

        Returns:
            Self for chaining
        """
        self._where_conditions.append((column, operator, value))
        return self

    def where_in(self, column: str, values: list[Any]) -> Self:
        """
        Add WHERE IN condition.

        Args:
            column: Column name
            values: List of values

        Returns:
            Self for chaining
        """
        return self.where(column, "IN", values)

    def where_null(self, column: str) -> Self:
        """Add WHERE column IS NULL."""
        return self.where(column, "IS", None)

    def where_not_null(self, column: str) -> Self:
        """Add WHERE column IS NOT NULL."""
        return self.where(column, "IS NOT", None)

    def order_by(self, column: str, direction: str = "ASC") -> Self:
        """
        Add ORDER BY clause.

        Args:
            column: Column name
            direction: ASC or DESC

        Returns:
            Self for chaining
        """
        direction = direction.upper()
        if direction not in ("ASC", "DESC"):
            raise ValueError(f"Invalid direction: {direction}. Use ASC or DESC.")
        self._order_by_columns.append((column, direction))
        return self

    def limit(self, limit: int) -> Self:
        """
        Set LIMIT.

        Args:
            limit: Maximum number of rows

        Returns:
            Self for chaining
        """
        self._limit_value = limit
        return self

    def offset(self, offset: int) -> Self:
        """
        Set OFFSET.

        Args:
            offset: Number of rows to skip

        Returns:
            Self for chaining
        """
        self._offset_value = offset
        return self

    def join(self, table: str, on: str, join_type: str = "INNER") -> Self:
        """
        Add JOIN clause.

        Args:
            table: Table to join
            on: JOIN condition (e.g., "users.id = orders.user_id")
            join_type: Type of join (INNER, LEFT, RIGHT, FULL)

        Returns:
            Self for chaining
        """
        join_type = join_type.upper()
        if join_type not in ("INNER", "LEFT", "RIGHT", "FULL", "CROSS"):
            raise ValueError(f"Invalid join type: {join_type}")
        self._join_clauses.append(f"{join_type} JOIN {table} ON {on}")
        return self

    def left_join(self, table: str, on: str) -> Self:
        """Add LEFT JOIN."""
        return self.join(table, on, "LEFT")

    def right_join(self, table: str, on: str) -> Self:
        """Add RIGHT JOIN."""
        return self.join(table, on, "RIGHT")

    def group_by(self, *columns: str) -> Self:
        """
        Add GROUP BY clause.

        Args:
            *columns: Columns to group by

        Returns:
            Self for chaining
        """
        self._group_by_columns.extend(columns)
        return self

    def having(self, condition: str) -> Self:
        """
        Add HAVING clause.

        Args:
            condition: HAVING condition

        Returns:
            Self for chaining
        """
        self._having_conditions.append(condition)
        return self

    def insert(self, data: dict[str, Any]) -> Self:
        """
        Set INSERT operation.

        Args:
            data: Dictionary of column:value pairs

        Returns:
            Self for chaining
        """
        self._operation = "INSERT"
        self._insert_data = data
        return self

    def update(self, data: dict[str, Any]) -> Self:
        """
        Set UPDATE operation.

        Args:
            data: Dictionary of column:value pairs to update

        Returns:
            Self for chaining
        """
        self._operation = "UPDATE"
        self._update_data = data
        return self

    def delete(self) -> Self:
        """Set DELETE operation."""
        self._operation = "DELETE"
        return self

    def build(self) -> tuple[str, tuple]:
        """
        Build the SQL query and parameters.

        Returns:
            Tuple of (query_string, parameters)
        """
        if self._operation == "SELECT":
            return self._build_select()
        elif self._operation == "INSERT":
            return self._build_insert()
        elif self._operation == "UPDATE":
            return self._build_update()
        elif self._operation == "DELETE":
            return self._build_delete()
        else:
            raise ValueError(f"Unknown operation: {self._operation}")

    def _build_select(self) -> tuple[str, tuple]:
        """Build SELECT query."""
        # SELECT clause
        distinct = "DISTINCT " if self._distinct else ""
        columns = ", ".join(self._select_columns) if self._select_columns else "*"
        query = f"SELECT {distinct}{columns} FROM {self.table}"

        # JOIN clauses
        if self._join_clauses:
            query += " " + " ".join(self._join_clauses)

        # WHERE clause
        params = []
        if self._where_conditions:
            where_parts, params = self._build_where()
            query += f" WHERE {where_parts}"

        # GROUP BY clause
        if self._group_by_columns:
            query += f" GROUP BY {', '.join(self._group_by_columns)}"

        # HAVING clause
        if self._having_conditions:
            query += f" HAVING {' AND '.join(self._having_conditions)}"

        # ORDER BY clause
        if self._order_by_columns:
            order_parts = [f"{col} {direction}" for col, direction in self._order_by_columns]
            query += f" ORDER BY {', '.join(order_parts)}"

        # LIMIT clause
        if self._limit_value is not None:
            query += f" LIMIT {self._limit_value}"

        # OFFSET clause
        if self._offset_value is not None:
            query += f" OFFSET {self._offset_value}"

        return query, tuple(params)

    def _build_insert(self) -> tuple[str, tuple]:
        """Build INSERT query."""
        if not self._insert_data:
            raise ValueError("No data provided for INSERT")

        columns = ", ".join(self._insert_data.keys())
        placeholders = ", ".join("?" * len(self._insert_data))
        query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
        params = tuple(self._insert_data.values())

        return query, params

    def _build_update(self) -> tuple[str, tuple]:
        """Build UPDATE query."""
        if not self._update_data:
            raise ValueError("No data provided for UPDATE")

        set_parts = [f"{col} = ?" for col in self._update_data.keys()]
        query = f"UPDATE {self.table} SET {', '.join(set_parts)}"
        params = list(self._update_data.values())

        # WHERE clause
        if self._where_conditions:
            where_parts, where_params = self._build_where()
            query += f" WHERE {where_parts}"
            params.extend(where_params)

        return query, tuple(params)

    def _build_delete(self) -> tuple[str, tuple]:
        """Build DELETE query."""
        query = f"DELETE FROM {self.table}"
        params = []

        # WHERE clause
        if self._where_conditions:
            where_parts, params = self._build_where()
            query += f" WHERE {where_parts}"

        return query, tuple(params)

    def _build_where(self) -> tuple[str, list]:
        """Build WHERE clause."""
        parts = []
        params = []

        for column, operator, value in self._where_conditions:
            if operator.upper() == "IN":
                if not isinstance(value, (list, tuple)):
                    raise ValueError(f"IN operator requires list/tuple, got {type(value)}")
                placeholders = ", ".join("?" * len(value))
                parts.append(f"{column} IN ({placeholders})")
                params.extend(value)
            elif operator.upper() in ("IS", "IS NOT"):
                if value is None:
                    parts.append(f"{column} {operator.upper()} NULL")
                else:
                    raise ValueError(f"{operator} operator requires None value")
            else:
                parts.append(f"{column} {operator} ?")
                params.append(value)

        return " AND ".join(parts), params

    def __str__(self) -> str:
        """String representation."""
        query, params = self.build()
        return f"Query: {query}\nParams: {params}"
