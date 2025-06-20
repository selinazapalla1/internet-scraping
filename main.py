"""Command‑line interface for the internet scraping project.

Run this module as a script to scrape a single page, crawl a site or
inspect stored keywords.  It relies on the underlying modules in this
package to perform network operations, parse HTML and store data.  Use
`python -m internet_scraping.main --help` to see available commands.
"""

from __future__ import annotations

import argparse
import sys

from .scraper import Scraper
from .keyword_extractor import extract_keywords
from .keyword_store import KeywordStore
from .crawler import Crawler


def _scrape(url: str, top_n: int, store_path: str | None) -> None:
    scraper = Scraper()
    html = scraper.fetch(url)
    if not html:
        print(f"Failed to fetch {url}")
        return
    text = scraper.parse_text(html)
    keywords = extract_keywords(text, top_n)
    print(f"Top {top_n} keywords for {url}:")
    print(", ".join(keywords) or "<no keywords>")
    if store_path:
        store = KeywordStore(store_path)
        store.add_keywords(url, keywords)
        store.close()
        print(f"Keywords stored to {store_path}")


def _crawl(start_url: str, max_pages: int, delay: float, store_path: str, top_n: int) -> None:
    crawler = Crawler(max_pages=max_pages, delay=delay)
    visited = crawler.crawl(start_url, store_path=store_path, top_n=top_n)
    print(f"Crawled {len(visited)} pages.\nStored keywords in {store_path}.")


def _list(store_path: str) -> None:
    store = KeywordStore(store_path)
    urls = store.list_urls()
    if not urls:
        print(f"No keywords stored in {store_path}")
        store.close()
        return
    for url in urls:
        keywords = store.get_keywords(url)
        print(f"{url}:")
        print("  " + ", ".join(keywords))
    store.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Internet scraping utility for extracting keywords from web pages.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # scrape command
    sp_scrape = subparsers.add_parser(
        "scrape",
        help="Scrape a single URL and optionally store its keywords",
    )
    sp_scrape.add_argument("url", help="URL of the page to scrape")
    sp_scrape.add_argument("--top", dest="top", type=int, default=10, help="Number of keywords to display")
    sp_scrape.add_argument("--store", dest="store", default=None, help="Path to keyword database (optional)")

    # crawl command
    sp_crawl = subparsers.add_parser(
        "crawl",
        help="Recursively crawl pages starting from a URL",
    )
    sp_crawl.add_argument("start_url", help="URL to start crawling from")
    sp_crawl.add_argument("--max-pages", dest="max_pages", type=int, default=10, help="Maximum pages to crawl")
    sp_crawl.add_argument("--delay", dest="delay", type=float, default=1.0, help="Delay between requests (seconds)")
    sp_crawl.add_argument("--store", dest="store", default="keywords.db", help="Path to keyword database")
    sp_crawl.add_argument("--top", dest="top", type=int, default=10, help="Number of keywords to extract per page")

    # list command
    sp_list = subparsers.add_parser(
        "list",
        help="List all stored URLs and their keywords",
    )
    sp_list.add_argument("--store", dest="store", default="keywords.db", help="Path to keyword database")

    args = parser.parse_args(argv)
    if args.command == "scrape":
        _scrape(args.url, args.top, args.store)
    elif args.command == "crawl":
        _crawl(args.start_url, args.max_pages, args.delay, args.store, args.top)
    elif args.command == "list":
        _list(args.store)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())