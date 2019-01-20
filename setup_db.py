import definitions
import sqlite3


def create_db():
    with open(definitions.DB_SCHEMA_PATH) as schema_file:
        schema = schema_file.read()
        with sqlite3.connect(definitions.DB_PATH) as conn:
            conn.cursor().executescript(schema)


if __name__ == '__main__':
    create_db()
