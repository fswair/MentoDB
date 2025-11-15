import json
import logging
import sqlite3
from collections.abc import Iterable
from pandas import DataFrame
from typing import Any, TypeAlias
from re import search
import typing
from inspect import signature
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from .models import DefaultModel
from .connection import MentoConnection

Str: TypeAlias = str
Lambda: TypeAlias = "function"


class Column:
    def __init__(
        self, arg: str, is_primary: bool = False, unique_columns: list[str] = None
    ):
        """A statement to create and recognize columns."""
        match = search("(\w+)\s?\:(.+)", str(arg))
        self.has_unique_check = False
        self.unique_args = None
        if "UniqueMatch" in str(arg):
            self.unique_args = search("UniqueMatch\[(.+)\]", str(arg))[1].split("-")
            self.has_unique_check = bool(self.unique_args)
        if match:
            column, _type = match.groups()
            if search("PrimaryKey", _type):
                is_primary = True
                _type = search(".+?~PrimaryKey-(.+)", _type)[1]
            addition = "primary key" if is_primary else ""
            if unique_columns and column.lower().strip() in unique_columns:
                addition = "UNIQUE"
            if _type.strip() in ("int", "float"):
                self.arg = f"{column} int {addition}"
            else:
                self.arg = f"{column} text {addition}"

        else:
            self.arg = f"{self.alphanum(arg)} text"

        self.arg = self.arg.lower()

    def alphanum(self, arg: str):
        data = [letter for letter in arg if letter.isalnum()]
        return "".join(data)

class PrimaryKey:
    def __new__(self, _type: type) -> typing.TypeVar:
        """A PrimaryKey statement to set columns as PrimaryKey"""
        type_base: str = f"{PrimaryKey.__name__}-{_type.__name__}"
        return typing.TypeVar(f"{type_base}", _type, bytes)


class UniqueMatch:
    def __new__(self, *args: typing.Iterable) -> typing.TypeVar:
        """A matching tool to set one or many columns as unique. (Multiple Primary Key)"""
        args: typing.List[str]
        arg_text = "-".join([str(arg) for arg in args])
        type_base: str = f"{UniqueMatch.__name__}[{arg_text}]"
        return typing.TypeVar(f"{type_base}", str, str)


class Sequence:
    def __new__(self, seperators: str = ","):
        type_base = f"{Sequence.__name__}[seperators='{seperators}']"
        return typing.TypeVar(f"{type_base}", str, bytes)


class JsonString:
    def __new__(self):
        type_base = f"{JsonString.__name__}"
        return typing.TypeVar(f"{type_base}", str, bytes)


class Fetch:
    def __init__(self, cursor: "sqlite3.Cursor", table: str = None):
        """A fetcher can fetch datas from specified sqlite cursor."""
        self.cursor = cursor
        if table:
            query = cursor.execute(f"SELECT * FROM {table} WHERE 0")
            self.columns = list(map(lambda x: x[0], query.description))
        else:
            self.columns = list(map(lambda x: x[0], self.cursor.description))

    def first(self, reverse: bool = False):
        if reverse:
            data = self.cursor.fetchall()
            if data:
                return data[-1]
            return self.format(data)
        else:
            data = self.cursor.fetchone()
            if not data:
                return None
            return self.format(data)

    def all(self):
        data = self.cursor.fetchall()
        return self.format(data)

    def format(self, values: list[tuple]) -> list[dict]:
        multiple = (
            True
            if isinstance(values, Iterable)
            and len(values) > 0
            and isinstance(values[0], Iterable)
            and not isinstance(values[0], str)
            else False
        )
        if (
            isinstance(values, Iterable)
            and len(values) > 0
            and not isinstance(values[0], Iterable)
            and not len(self.columns) == len(values)
        ):
            raise ValueError(
                "Value list size must match column count"
            )

        else:
            if multiple:
                results = list()
                for fetch_data in values:
                    response = dict()
                    for index, value in enumerate(fetch_data):
                        response[self.columns[index]] = value
                    results.append(response)
                return results
            else:
                response = dict()
                for index, value in enumerate(values):
                    response[self.columns[index]] = value
                return response


class MentoExceptions:
    def __init__(self, logging: bool = True):
        self.logging = logging

        self.wrong_data_model = lambda: self.auto(
            "Given model and data (list[dict]) not matched with together.\nPlease check your data and model then try again."
        )

    def auto(self, message: str) -> "None | BaseException":
        if self.logging:
            logging.error(message)
        else:
            raise BaseException(message)


class AutoResponse:
    """Converts list of dictionaries to Pydantic model instances."""

    def __init__(self, model: type[BaseModel] | None = None, datas: list[dict] | None = None):
        """
        Initialize AutoResponse converter.

        Args:
            model: Pydantic model class to convert data to
            datas: List of dictionaries to convert
        """
        self.status: bool = False
        if model and datas:
            self.model: type[BaseModel] = model
            self.datas: list[dict] = datas
            self.status = (
                isinstance(datas, list)
                and len(datas) > 0
                and isinstance(datas[0], dict)
            )
            self.err = MentoExceptions()
            if not self.status:
                self.err.wrong_data_model()

            # Pydantic v2: Use model_fields instead of schema()
            self.attrs: list[str] = sorted(list(self.model.model_fields.keys()))
            self.keys: list[str] = sorted(list(datas[0].keys()))

    def get_response(self) -> list[BaseModel]:
        """
        Convert dictionaries to model instances.

        Returns:
            List of model instances

        Raises:
            ValueError: If data validation fails
        """
        if not self.status:
            raise ValueError(
                "Invalid data: expected list of dictionaries"
            )

        models: list[BaseModel] = []
        for i, data in enumerate(self.datas):
            data_keys = sorted(list(data.keys()))
            if data_keys != self.attrs:
                raise ValueError(
                    f"Data at index {i} has mismatched keys. "
                    f"Expected {self.attrs}, got {data_keys}"
                )

            # Pydantic v2: Use model validation
            try:
                model_instance = self.model(**data)
                models.append(model_instance)
            except Exception as e:
                raise ValueError(
                    f"Failed to create model instance at index {i}: {e}"
                ) from e

        return models


class Static:
    def __init__(
        self,
        datas: list[dict],
        model: BaseModel = None,
        as_model: bool = False,
        as_json: bool = False,
        as_dataframe: bool = False,
    ) -> None:
        """A data formatting tool that converts data into desired type of output."""
        self.datas = datas
        self.basemodel = model
        self.as_model = as_model
        self.as_json = as_json
        self.as_dataframe = as_dataframe
        self.data = self.set()

    def set(self, value: Any = None):
        if self.as_model:
            return self.model()
        elif self.as_json:
            return self.json()
        elif self.as_dataframe:
            return self.dataframe()
        return self.datas

    def model(self):
        response = AutoResponse(model=self.basemodel, datas=self.datas)
        return response.get_response()

    def json(self):
        return json.dumps(self.datas)

    def dataframe(self, data_dict: dict = dict()):
        if not self.datas:
            return
        for k in self.datas[0].keys():
            data_dict[k] = [data.get(k) for data in self.datas]
        if not data_dict:
            return
        return DataFrame(data_dict)


class Mento:
    def __init__(
        self,
        connection: "MentoConnection" = None,
        default_table: str = None,
        check_model: BaseModel = None,
        error_logging: bool = False,
    ):
        """MentoDB is powerful database engine for sqlite3. You have many options to use, specially basic things, also lambda filters, regular expressions included."""
        self.connection: "MentoConnection" = connection
        self.default_table: str = default_table
        self.check_model: BaseModel = check_model
        self.exceptions = MentoExceptions(error_logging)

    def create(
        self,
        table: str = None,
        model: BaseModel = DefaultModel,
        exists_check: bool = True,
        unique_columns: list = [],
    ):
        """Create a table with your BaseModel."""
        if not table:
            table = self.default_table
        if not model:
            model = self.check_model

        # Validate table name to prevent SQL injection
        if not table or not table.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table}")

        parameters = list(signature(model).parameters.values())
        columns = list()
        for param in parameters:
            column = Column(str(param), unique_columns=unique_columns)
            if not column.has_unique_check:
                columns.append(column.arg)
        create_query = ", ".join(columns)
        if exists_check:
            # Table name validation already done above
            self.connection.execute(
                f"CREATE TABLE IF NOT EXISTS {table} ({create_query})"
            )
        else:
            try:
                self.connection.execute(f"CREATE TABLE {table} ({create_query})")
            except Exception as e:
                logging.warning(f"Table creation failed: {e}, dropping and recreating")
                self.drop(table)
                self.create(table, model, exists_check)

    def create_many(
        self, datas: dict = dict(user=DefaultModel), exists_check: bool = True
    ):
        """Create many table with BaseModels."""
        tables = list(datas.keys())
        models = list(datas.values())

        for i, table in enumerate(tables):
            self.create(table=table, model=models[i], exists_check=exists_check)

    def drop(self, table: str = None):
        """Drop specified table."""
        if not table:
            table = self.default_table

        # Validate table name
        if not table or not table.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table}")

        query = f"DROP TABLE IF EXISTS {table}"
        cursor = self.connection.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

    def insert(
        self, table: str = None, data: dict = dict(), check_model: BaseModel = None
    ):
        """Insert data to current table using parameterized queries."""
        if not table:
            table = self.default_table

        # Validate table name
        if not table or not table.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table}")

        if not check_model:
            check_model = self.check_model

        if check_model:
            unique_args = []
            sign = signature(check_model)
            for param in sign.parameters.values():
                param_check = Column(param)
                if param_check.has_unique_check:
                    unique_args = param_check.unique_args

            if unique_args:
                fetch = Fetch(self.connection.cursor(), table=table)
                for arg in unique_args:
                    if arg not in fetch.columns:
                        raise ValueError(f"Column '{arg}' not found in table '{table}'")

                # Use parameterized query for WHERE clause
                conditions = [f"{arg} = ?" for arg in unique_args]
                where_query = " AND ".join(conditions)
                params = tuple(data[arg] for arg in unique_args)

                cursor = self.connection.connection.cursor()
                cursor.execute(f"SELECT * FROM {table} WHERE {where_query}", params)
                fetch = Fetch(cursor)
                first_data = fetch.first()
                if first_data:
                    return first_data

        # Use parameterized INSERT query
        columns = list(data.keys())
        placeholders = ', '.join('?' * len(columns))
        column_names = ', '.join(columns)
        values = tuple(data.values())

        try:
            query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
            cursor = self.connection.connection.cursor()
            cursor.execute(query, values)
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            logging.error(f"Integrity constraint violation: {e}")

    def update(
        self,
        table: str = None,
        data: dict = None,
        where: dict = None,
        update_all: bool = False,
    ):
        """Update matched or all columns using parameterized queries."""
        if not table:
            table = self.default_table

        # Validate table name
        if not table or not table.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table}")

        if not update_all and not where:
            raise ValueError("Must provide WHERE clause or set update_all=True")

        if not data:
            raise ValueError("No data provided for update")

        # Validate column names
        fetch = Fetch(self.connection.cursor(), table=table)

        # Build SET clause with parameterized query
        set_parts = [f"{key} = ?" for key in data.keys()]
        set_clause = ", ".join(set_parts)
        params = list(data.values())

        if update_all:
            query = f"UPDATE {table} SET {set_clause}"
            cursor = self.connection.connection.cursor()
            cursor.execute(query, tuple(params))
            self.connection.commit()
        else:
            # Validate WHERE columns
            for key in where.keys():
                if key not in fetch.columns:
                    raise ValueError(f"Column '{key}' not found in table '{table}'")

            # Build WHERE clause
            where_parts = [f"{key} = ?" for key in where.keys()]
            where_clause = " AND ".join(where_parts)
            where_params = list(where.values())

            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            all_params = params + where_params

            cursor = self.connection.connection.cursor()
            cursor.execute(query, tuple(all_params))
            self.connection.commit()

    def select(
        self,
        from_table: str = None,
        model: BaseModel = None,
        where: dict = None,
        order_by: Column = None,
        limit: int = 0,
        filter: Lambda = None,
        regexp: dict[str, str | list[str]] = None,
        select_all: bool = True,
        select_column: str = None,
        as_model: bool = False,
        as_dataframe: bool = False,
        as_json: bool = False,
    ):
        """Select matched or all columns using parameterized queries."""
        config = dict(
            model=model, as_model=as_model, as_json=as_json, as_dataframe=as_dataframe
        )
        if as_model and not model:
            raise ValueError("Model must be specified when as_model=True")

        if not from_table:
            from_table = self.default_table

        # Validate table name
        if not from_table or not from_table.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {from_table}")

        # Validate column names for fetching available columns
        fetch = Fetch(self.connection.cursor(), table=from_table)

        # Build ORDER BY and LIMIT clauses
        additions = ""
        if order_by:
            # Validate order_by column name
            order_col = str(order_by).strip().lower()
            if order_col not in fetch.columns:
                raise ValueError(f"Column '{order_by}' not found for ORDER BY")
            additions += f" ORDER BY {order_col}"

        if limit > 0:
            additions += f" LIMIT {int(limit)}"

        # Determine SELECT columns
        if select_all and not select_column:
            select_cols = "*"
        elif select_column:
            # Validate select_column
            if select_column not in fetch.columns:
                raise ValueError(f"Column '{select_column}' not found")
            select_cols = select_column
        else:
            select_cols = "*"

        # Handle WHERE clause with parameterized queries
        if where:
            # Validate WHERE columns
            for key in where.keys():
                if key not in fetch.columns:
                    raise ValueError(f"Column '{key}' not found in table '{from_table}'")

            # Build parameterized WHERE clause
            where_parts = [f"{key} = ?" for key in where.keys()]
            where_statement = " AND ".join(where_parts)
            where_params = tuple(where.values())

            query = f"SELECT {select_cols} FROM {from_table} WHERE {where_statement}{additions}"
            cursor = self.connection.connection.cursor()
            cursor.execute(query, where_params)
            fetch = Fetch(cursor)

            if select_all:
                response = Static(fetch.all(), **config)
                return response.data
            response = Static(fetch.first(), **config)
            return response.data

        if not regexp and not filter:
            query = f"SELECT {select_cols} FROM {from_table}{additions}"
            cursor = self.connection.connection.cursor()
            cursor.execute(query)
            fetch = Fetch(cursor)
            response = Static(fetch.all(), **config)
            return response.data
        else:
            if filter:
                if not callable(filter):
                    raise ValueError(
                        "Filter must be a callable (lambda) with one argument"
                    )

                query = f"SELECT * FROM {from_table}{additions}"
                cursor = self.connection.connection.cursor()
                cursor.execute(query)
                fetch = Fetch(cursor)
                datas = fetch.all()
                matches = []

                for data in datas:
                    filter_args = filter.__code__.co_varnames
                    if not filter_args:
                        raise ValueError(
                            "Filter function must have at least one argument (column name)"
                        )

                    data_index = filter_args[0]
                    if filter(data[data_index]):
                        matches.append(data)

                response = Static(matches, **config)
                return response.data

            elif regexp:
                query = f"SELECT * FROM {from_table}{additions}"
                cursor = self.connection.connection.cursor()
                cursor.execute(query)
                fetch = Fetch(cursor)
                datas = fetch.all()

                if not regexp:
                    return []

                column = str(list(regexp.keys())[0]).lower()
                if column not in fetch.columns:
                    raise ValueError(
                        f"Column '{column}' not found in table '{from_table}'"
                    )

                matches = []
                patterns = regexp[column]
                if not isinstance(patterns, list):
                    patterns = [patterns]

                if isinstance(datas, list):
                    for data in datas:
                        for regex in patterns:
                            col_idx = fetch.columns.index(column)
                            has_match = self.regexp(regex, str(data[col_idx]))
                            if has_match:
                                matches.append(data)
                                break  # No need to check other patterns for this row
                    response = Static(matches, **config)
                    return response.data
                else:
                    for regex in patterns:
                        col_idx = fetch.columns.index(column)
                        has_match = self.regexp(regex, str(datas[col_idx]))
                        if has_match:
                            matches.append(datas)
                            break
                    response = Static(matches, **config)
                    return response.data

            return []

    def delete(self, table: str, where: dict = None, delete_all: bool = False):
        """Delete matched or all rows using parameterized queries."""
        # Validate table name
        if not table or not table.replace('_', '').isalnum():
            raise ValueError(f"Invalid table name: {table}")

        if delete_all:
            query = f"DELETE FROM {table}"
            cursor = self.connection.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
        else:
            if not where:
                raise ValueError(
                    "Must provide WHERE clause or set delete_all=True"
                )

            # Validate column names
            fetch = Fetch(self.connection.cursor(), table=table)
            for key in where.keys():
                if key not in fetch.columns:
                    raise ValueError(f"Column '{key}' not found in table '{table}'")

            # Build parameterized WHERE clause
            where_parts = [f"{key} = ?" for key in where.keys()]
            where_statement = " AND ".join(where_parts)
            where_params = tuple(where.values())

            query = f"DELETE FROM {table} WHERE {where_statement}"
            cursor = self.connection.connection.cursor()
            cursor.execute(query, where_params)
            self.connection.commit()

    def regexp(self, pattern: str, string: str | bytes) -> bool:
        """If pattern has a match with given string, returns True, else return False."""
        match = search(pattern, str(string))
        return bool(match)
