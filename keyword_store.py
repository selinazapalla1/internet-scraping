"""Persistent storage for scraped keywords.

This module encapsulates a very simple SQLite data store for associating
keywords with the URL from which they were extracted.  Using SQLite makes
it easy to persist results across runs without requiring an external
database.  The table schema is straightforward: one row per keyword per
URL.  Additional metadata could be added as needed (e.g. timestamp or
page title).
"""

from __future__ import annotations

import sqlite3
from typing import Iterable, List


class KeywordStore:
    """A lightweight SQLite-based store for keywords.

    Parameters
    ----------
    db_path : str, optional
        Path to the SQLite file.  Defaults to ``keywords.db`` in the
        current working directory.
    """

    def __init__(self, db_path: str = "keywords.db") -> None:
        self._db_path = db_path
        self._conn: sqlite3.Connection = sqlite3.connect(self._db_path)
        self._create_table()

    def _create_table(self) -> None:
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS keywords (
                url TEXT NOT NULL,
                keyword TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def add_keywords(self, url: str, keywords: Iterable[str]) -> None:
        """Insert a list of keywords associated with a URL into the store.

        Duplicate keywords for the same URL are permitted; consider
        deduplicating the list before calling this method if you want one
        record per keyword.

        Parameters
        ----------
        url : str
            The URL the keywords came from.
        keywords : iterable of str
            The keywords to store.
        """
        cur = self._conn.cursor()
        cur.executemany(
            "INSERT INTO keywords (url, keyword) VALUES (?, ?)",
            [(url, kw) for kw in keywords],
        )
        self._conn.commit()

    def get_keywords(self, url: str) -> List[str]:
        """Retrieve all keywords stored for a given URL.

        Parameters
        ----------
        url : str
            The URL whose keywords to retrieve.

        Returns
        -------
        list of str
            The list of keywords stored for that URL.  If no keywords
            exist, an empty list is returned.
        """
        cur = self._conn.cursor()
        cur.execute("SELECT keyword FROM keywords WHERE url = ?", (url,))
        return [row[0] for row in cur.fetchall()]

    def list_urls(self) -> List[str]:
        """Return all distinct URLs that have stored keywords."""
        cur = self._conn.cursor()
        cur.execute("SELECT DISTINCT url FROM keywords ORDER BY url")
        return [row[0] for row in cur.fetchall()]

    def close(self) -> None:
        """Close the underlying database connection."""
        self._conn.close()