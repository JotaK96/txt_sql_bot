import os
from typing import List, Any
import sqlite3
from pathlib import Path


class DatabaseManager:
    def __init__(self):
        self.endpoint_url = os.getenv("DB_ENDPOINT_URL")
        self.APP_HOME = Path(
            os.getenv("APP_HOME", Path(__file__).parent.parent.parent))
        self.DATA_DIR = self.APP_HOME / "sqlite_server/uploads"
        self.DATABASE_PATH = self.DATA_DIR / os.getenv("DB_NAME")

    def get_schema(self):
        print(f"db_name:{self.DATABASE_PATH}")
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()

        schema = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f'PRAGMA table_info("{table_name}");')
            columns = cursor.fetchall()

            schema[table_name] = [
                {
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "default_value": col[4],
                    "primary_key": bool(col[5])
                }
                for col in columns
            ]

        conn.close()
        return schema

    def execute_query(self, query: str) -> List[Any]:
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            results = cursor.fetchall()
            conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Error executing query: {str(e)}")
        finally:
            conn.close()

        return results
