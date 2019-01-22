"""Store and retrieve rhyming information using a SQLite DB."""
import contextlib
import definitions
import itertools
import sqlite3
from typing import List, Tuple
from datatypes import Rhyme


def find_datamuse_rhymes(conn, word: str) -> List[Rhyme]:
    """Returns a List of Rhymes for which word == Rhyme.word1."""
    c = conn.cursor()
    c.execute("SELECT word2, num_syllables, score FROM datamuse_rhymes WHERE word1 = ?", (word,))
    return [Rhyme(word1=word, word2=res[0], num_syllables=res[1], score=res[2]) for res in c.fetchall()]


def word_exists(conn, word: str) -> bool:
    """Returns True if the word exists in the database, False otherwise."""
    c = conn.cursor()
    c.execute("SELECT word FROM words where word = ?", (word,))
    return c.fetchone() is not None


def datamuse_rhymes_populated(conn, word: str) -> bool:
    """Returns True if the word exists in the database, False otherwise."""
    c = conn.cursor()
    c.execute("SELECT datamuse_rhymes_populated FROM words where word = ?", (word,))
    res = c.fetchone()
    return res and res[0]


def add_word(conn, word: str) -> None:
    with conn:
        conn.cursor().execute(
            "INSERT OR IGNORE INTO words (word) "
            "VALUES (?)",
            (word,))


def populate_datamuse_rhymes(conn, word: str, rhymes: List[Rhyme]) -> None:
    """Populates the datamuse_rhymes table with rhymes of the given word, marking that word's rhymes as populated.

    Args:
        :param conn: a shakespeare.db connection.
        :param word: the word whose rhymes are being added
        :param rhymes: the list of rhymes which are to be added to the database.
    """
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO words (word, datamuse_rhymes_populated) "
            "VALUES (?, ?)",
            (word, 1))
        if len(rhymes):
            cursor.execute(
                "INSERT OR IGNORE INTO WORDS (word, datamuse_rhymes_populated) "
                "VALUES " + ', '.join(["(?, ?)"]*len(rhymes)),
                _flatten_to_tuple([[rhyme.word1, 0] if rhyme.word1 != word else [rhyme.word2, 0] for rhyme in rhymes]))
            cursor.execute(
                "INSERT OR IGNORE INTO datamuse_rhymes (word1, word2, num_syllables, score) "
                "VALUES " + ', '.join(["(?, ?, ?, ?)"]*(2*len(rhymes))),
                _flatten_to_tuple(
                    [[rhyme.word1, rhyme.word2, rhyme.num_syllables, rhyme.score,
                      rhyme.word2, rhyme.word1, rhyme.num_syllables, rhyme.score] for rhyme in rhymes]))


def _flatten_to_tuple(list_of_lists: List[List[object]]) -> Tuple:
    return tuple(itertools.chain.from_iterable(list_of_lists))


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


