"""Store and retrieve rhyming information using a SQLite DB."""
import contextlib
import definitions
import sqlite3


def find_rhymes(conn, word):
    c = conn.cursor()
    c.execute("SELECT word2 FROM rhymes WHERE word1 = ?", (word,))
    return [res[0] for res in c.fetchall()]


def find_words(conn):
    c = conn.cursor()
    c.execute("SELECT word FROM words")
    return [res[0] for res in c.fetchall()]


def add_word(conn, word):
    with conn:
        conn.cursor().execute(
            "INSERT OR IGNORE INTO words (word) "
            "VALUES (?)",
            (word,))


def add_rhyme(conn, word1, word2):
    with conn:
        conn.cursor().execute(
            "INSERT OR IGNORE INTO rhymes (word1, word2) "
            "VALUES (?, ?), (?, ?)",
            (word1, word2, word2, word1))


@contextlib.contextmanager
def create_db_connection():
    """Convenience method to wrap database connections. Handles auto-closing connections.

    Example:
        with create_db_connection() as conn:
            c = conn.cursor()
            conn.cursor().execute("SELECT * FROM rhymes")
            results = [res[0] for res in c.fetchall()]
    """
    conn = None
    try:
        conn = sqlite3.connect(definitions.DB_PATH)
        yield conn
    finally:
        if conn:
            conn.close()


