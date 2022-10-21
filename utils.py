import json
import logging
import sqlite3
from pandas import DataFrame
from typing import Any, TypeAlias
from re import search
import typing
from numpy import iterable
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
            if iterable(values)
            and len(values) > 0
            and iterable(values[0])
            and not type(values[0]) == str
            else False
        )
        if (
            iterable(values)
            and len(values) > 0
            and not iterable(values[0])
            and not len(self.columns) == len(values)
        ):
            raise Exception(
                "You have to give a value list has size same with column size."
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


@dataclass
class AutoResponse:
    def __init__(self, model: BaseModel = None, datas: list[dict] = None):
        """A recognizer can convert inputs to specified data model."""
        self.status: bool = False
        if model and datas:
            self.model: type = model
            self.datas: list[dict] = datas
            self.status = (
                True
                if iterable(datas)
                and type(datas) == list
                and datas
                and type(datas[0]) == dict
                and datas[0]
                else False
            )
            self.err = MentoExceptions()
            if not self.status:
                self.err.wrong_data_model()
            self.sign: dict = self.model.__pydantic_model__.schema()
            self.properties: dict = self.sign.get("properties")
            self.attrs: list = sorted(list(self.properties.keys()))
            self.keys: list = sorted(list(datas[0].keys()))

    def get_response(self) -> list[object]:
        self.models: list[self.model] = list()
        if not self.status:
            self.err.auto(
                "Your data was wrong thats why i cant return any data response."
            )
        for i, data in enumerate(self.datas):
            data_keys = sorted(list(data.keys()))
            if not data_keys == self.attrs:
                self.err.auto(
                    f"The dict with id {i + 1} is incorrect. Please give just ``same type`` data dicts."
                )
            else:
                x = self.__class__()
                for k, v in data.items():
                    if not str(k)[0].isalpha():
                        k = str(f"attr{k}")
                    setattr(x, k, v)
                self.models.append(x)
        return self.models


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
        parameters = list(signature(model).parameters.values())
        columns = list()
        for param in parameters:
            column = Column(str(param), unique_columns=unique_columns)
            if not column.has_unique_check:
                columns.append(column.arg)
        create_query = ", ".join(columns)
        if exists_check:
            self.connection.execute(
                f"CREATE TABLE IF NOT EXISTS {table} ({create_query})"
            )
        else:
            try:
                self.connection.execute(f"CREATE TABLE  {table} ({create_query})")
            except:
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
        """Drop table you want."""
        if not table:
            table = self.default_table
        self.create(table, model=DefaultModel)
        self.connection.execute(f"DROP TABLE {table}")

    def insert(
        self, table: str = None, data: dict = dict(), check_model: BaseModel = None
    ):
        """Insert data to current table."""
        if not table:
            table = self.default_table

        if not check_model:
            check_model = self.check_model

        if check_model:
            conditions = []
            unique_args = []
            sign = signature(check_model)
            for param in sign.parameters.values():
                param_check = Column(param)
                if param_check.has_unique_check:
                    unique_args = param_check.unique_args

            for arg in unique_args:
                fetch = Fetch(self.connection.cursor(), table=table)
                if arg not in fetch.columns:
                    raise BaseException("Args are not same with your table.")
                value = (
                    f"{arg} = {data[arg]}"
                    if type(data[arg]) in (int, float)
                    else f"{arg} = '{data[arg]}'"
                )
                conditions.append(value)
            where_query = " and ".join(conditions)

            if conditions:
                cursor = self.connection.execute(
                    f"SELECT * FROM {table} where {where_query}"
                )

                fetch = Fetch(cursor)
                first_data = fetch.first()
                if first_data:
                    return first_data

        query = ""
        index = 0
        for k, v in data.items():
            if not type(v) == int:
                query += f"'{v}'{',' if index+1 < len(data.items()) else ''}"
            else:
                query += f"{v}{',' if index+1 < len(data.items()) else ''}"
            index += 1

        try:
            self.connection.execute(f"INSERT INTO {table} VALUES ({query})")
        except sqlite3.IntegrityError as e:
            logging.error("This content already posted.")

    def update(
        self,
        table: str = None,
        data: dict = None,
        where: dict = None,
        update_all: bool = False,
    ):
        """Update matched or all columns."""
        if not table:
            table = self.default_table

        if not update_all and not where:
            raise BaseException("Unexpected request. Please check your inputs.")

        if where:
            conditions = list()
            fetch = Fetch(self.connection.cursor(), table=table)
            for key, value in where.items():
                if key not in fetch.columns:
                    raise BaseException(f"Your table has no column named `{key}`")
                if type(value) == int:
                    value = value
                else:
                    value = f"'{value}'"
                conditions.append(f"{key} = {value}")
            if len(conditions) == 1:
                where_statement = conditions[0]
            else:
                where_statement = " and ".join(conditions).strip()

        if not table:
            table = self.default_table
        queries = list()
        for k, v in data.items():
            if not type(v) == int:
                v = f"'{v}'"
            queries.append(f"{k}={v}")
        update_query = ", ".join(queries)
        if update_all:
            self.connection.execute(f"UPDATE {table} SET {update_query}")
        else:
            data = self.connection.execute(
                f"UPDATE {table} SET {update_query} where {'' if not where_statement else where_statement}"
            )

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
        """Select matched or all columns as lists include Python dict or custom formats (Detailed in Tests)."""
        config = dict(
            model=model, as_model=as_model, as_json=as_json, as_dataframe=as_dataframe
        )
        if as_model and not model:
            raise self.exceptions.auto(
                "If you want to get models you have to specify data model."
            )
        additions = ""
        if not from_table:
            from_table = self.default_table
        if order_by:
            additions += f"ORDER BY {order_by}"

        if limit > 0:
            additions += f" LIMIT {limit}"

        if where:
            conditions = list()
            fetch = Fetch(self.connection.cursor(), table=from_table)
            for key, value in where.items():
                if key not in fetch.columns:
                    raise self.exceptions.auto(
                        f"Your table has no column named `{key}`"
                    )
                if type(value) in (int, float):
                    value = value
                else:
                    value = f"'{value}'"
                conditions.append(f"{key} = {value}")
            where_statement = " and ".join(conditions).strip()
            cursor = self.connection.execute(
                f"SELECT {'*' if select_all and not select_column else select_column} FROM {from_table} where {where_statement} {additions} "
            )
            fetch = Fetch(cursor)
            if select_all:
                response = Static(fetch.all(), **config)
                return response.data
            response = Static(fetch.first(), **config)
            return response.data
        if not regexp and not filter:
            query = self.connection.execute(
                f"SELECT {'*' if select_all and not select_column else select_column} FROM {from_table} {additions}"
            )
            fetch = Fetch(query)
            response = Static(fetch.all(), **config)
            return response.data
        else:
            if filter:
                if not callable(filter):
                    raise self.exceptions.auto(
                        "Filter must be lambda with one argument, also this filter is not callable."
                    )
                else:
                    query = self.connection.execute(
                        f"SELECT *  FROM {from_table} {additions}"
                    )
                    fetch = Fetch(query)
                    datas = fetch.all()
                    matches = list()
                    for data in datas:
                        filter_args = filter.__code__.co_varnames
                        data_index = (
                            filter_args[0]
                            if iterable(filter_args) and len(filter_args) > 0
                            else -1
                        )
                        if data_index == -1:
                            raise self.exceptions.auto(
                                "No argument supplied to filter. Please, specifiy column name as argument."
                            )
                        else:
                            if filter(data[data_index]):
                                matches.append(data)
                    response = Static(matches, **config)
                    return response.data
            elif regexp:
                query = self.connection.execute(
                    f"SELECT *  FROM {from_table} {additions}"
                )
                fetch = Fetch(query)
                datas = fetch.all()
                column = str(list(regexp.keys())[0]).lower()
                matches = list()
                if iterable(datas) and type(datas) == list:
                    for data in datas:
                        if iterable(regexp[column]):
                            for regex in regexp[column]:
                                if column not in fetch.columns:
                                    raise BaseException(
                                        f"Current table has no column named `{column}`."
                                    )
                                has_match = self.regexp(
                                    regex,
                                    str(
                                        data[fetch.columns[fetch.columns.index(column)]]
                                    ),
                                )
                                if has_match:
                                    matches.append(data)
                    response = Static(matches, **config)
                    return response.data
                else:
                    if iterable(regexp[column]):
                        for regex in regexp[column]:
                            data = datas[fetch.columns[fetch.columns.index(column)]]
                            has_match = self.regexp(regex, str(data))
                            if has_match:
                                matches.append(data)
                    response = Static(matches, **config)
                    return response.data

            if select_all:
                fetch = Fetch(f"SELECT * FROM {from_table}")
                response = Static(matches, **config)
                return response.data

    def delete(self, table: str, where: dict = dict(), delete_all: bool = False):
        """Delete matched or all columns."""
        if delete_all:
            self.connection.execute(f"DELETE FROM {table}")
        else:
            if where:
                conditions = list()
                fetch = Fetch(self.connection.cursor(), table=table)
                for key, value in where.items():
                    if key not in fetch.columns:
                        raise BaseException(f"Your table has no column named `{key}`")
                    if type(value) in (int, float):
                        value = value
                    else:
                        value = f"'{value}'"
                    conditions.append(f"{key} = {value}")
                where_statement = " and ".join(conditions).strip()
                self.connection.execute(f"DELETE FROM {table} where {where_statement}")
            else:
                raise BaseException(
                    "Please add where statement or set delete_all as true to delete all rows."
                )

    def regexp(self, pattern: str, string: str | bytes) -> bool:
        """If pattern has a match with given string, returns True, else return False."""
        match = search(pattern, str(string))
        return bool(match)


@dataclass
class AutoResponse:
    def __init__(self, model=None, datas: list[dict] = None):
        self.status: bool = False
        self.err = MentoExceptions()
        if model and datas:
            self.model: type = model
            self.datas: list[dict] = datas
            self.status = (
                True
                if iterable(datas)
                and type(datas) == list
                and datas
                and type(datas[0]) == dict
                and datas[0]
                else False
            )
            if not self.status:
                self.err.wrong_data_model()
            self.sign: dict = self.model.__pydantic_model__.schema()
            self.properties: dict = self.sign.get("properties")
            self.attrs: list = sorted(list(self.properties.keys()))
            self.keys: list = sorted(list(datas[0].keys()))

    def get_response(self) -> list[object]:
        self.models: list[self.model] = list()
        if not self.status:
            self.err.auto(
                "Your data was wrong thats why i cant return any data response."
            )
        for i, data in enumerate(self.datas):
            data_keys = sorted(list(data.keys()))
            if not data_keys == self.attrs:
                self.err.auto(
                    f"The dict with id {i + 1} is incorrect. Please give just ``same type`` data dicts."
                )
            else:
                x = self.__class__()
                for k, v in data.items():
                    if str(k[0]).isdigit():
                        k = str(f"w{k}")
                    setattr(x, k, v)
                self.models.append(x)
        return self.models
