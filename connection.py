from sqlite3 import connect
import sqlite3

class MentoConnection(object):
    def __init__(self, path: str, **kwargs):
        self.connection: sqlite3.Connection = connect(path, **kwargs)
    
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