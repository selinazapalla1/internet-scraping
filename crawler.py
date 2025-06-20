"""Web crawler that builds on :class:`~internet_scraping.scraper.Scraper`.

The crawler recursively visits pages on a given domain up to a configurable
number of pages.  For each page it extracts the visible text, derives
keywords using :func:`~internet_scraping.keyword_extractor.extract_keywords`
and stores them via :class:`~internet_scraping.keyword_store.KeywordStore`.

The crawl depth is controlled by a simple counter; it does not follow a
depth‑first or breadth‑first depth limit but stops as soon as the maximum
page count is reached.  A delay between requests can be configured to
avoid bombarding servers.  Error handling is minimal; pages that fail to
fetch are skipped.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Iterable, Set

from .scraper import Scraper
from .keyword_extractor import extract_keywords
from .keyword_store import KeywordStore


class Crawler:
    """A simple domain‑restricted web crawler.

    Parameters
    ----------
    max_pages : int, optional
        Maximum number of pages to visit before stopping.  Defaults to 10.
    delay : float, optional
        Number of seconds to wait between successive page fetches.  Defaults to 1.0.
    scraper : Scraper, optional
        The scraper instance used to fetch pages.  If not provided a
        default :class:`Scraper` is created.
    """

    def __init__(self, max_pages: int = 10, delay: float = 1.0, scraper: Scraper | None = None) -> None:
        self.max_pages = max(1, max_pages)
        self.delay = max(0.0, delay)
        self.scraper = scraper or Scraper()

    def crawl(self, start_url: str, store_path: str = "keywords.db", top_n: int = 10) -> Set[str]:
        """Crawl pages starting from ``start_url`` and store their keywords.

        The crawler only visits pages on the same domain as the starting URL.
        Keywords from each page are extracted using the simple extractor in
        :mod:`internet_scraping.keyword_extractor` and stored in a SQLite
        database at ``store_path``.  Duplicate URLs are skipped.  The crawl
        stops after ``max_pages`` pages or when no more links remain.

        Parameters
        ----------
        start_url : str
            The initial URL to start crawling from.
        store_path : str, optional
            Path to the SQLite database file for storing keywords.  Defaults
            to ``keywords.db``.
        top_n : int, optional
            Number of keywords to extract per page.  Defaults to 10.

        Returns
        -------
        set of str
            The set of URLs visited during the crawl.
        """
        store = KeywordStore(store_path)
        visited: Set[str] = set()
        queue: deque[str] = deque([start_url])

        pages_crawled = 0
        while queue and pages_crawled < self.max_pages:
            url = queue.popleft()
            if url in visited:
                continue
            visited.add(url)
            html = self.scraper.fetch(url)
            if not html:
                continue
            text = self.scraper.parse_text(html)
            keywords = extract_keywords(text, top_n=top_n)
            if keywords:
                store.add_keywords(url, keywords)
            # Extract links and add new ones to the queue
            links = self.scraper.extract_links(html, url)
            for link in links:
                if link not in visited and link not in queue:
                    queue.append(link)
            pages_crawled += 1
            if self.delay:
                time.sleep(self.delay)
        store.close()
        return visited