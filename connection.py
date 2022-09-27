from sqlite3 import connect
import sqlite3


class MentoConnection:
    def __init__(self, database: str = "./database.db", check_same_thread=False):
        self.connection: sqlite3.Connection = connect(
            database=database, check_same_thread=check_same_thread
        )

    def cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def execute(self, query: str, auto_commit: bool = True) -> "sqlite3.Cursor":
        _exec_query = self.cursor().execute(query)
        if auto_commit:
            self.commit()
        return _exec_query
