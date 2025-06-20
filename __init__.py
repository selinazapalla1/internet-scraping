"""Top level package for the internet scraping project.

This package provides modules for fetching web pages, extracting visible
text, deriving keywords and crawling websites.  The CLI entrypoint lives
in :mod:`internet_scraping.main`.
"""

__all__ = [
    "Scraper",
    "extract_keywords",
    "KeywordStore",
    "Crawler",
]

from .scraper import Scraper  # noqa: F401
from .keyword_extractor import extract_keywords  # noqa: F401
from .keyword_store import KeywordStore  # noqa: F401
from .crawler import Crawler  # noqa: F401