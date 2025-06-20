"""Web page fetching and parsing utilities.

This module defines the :class:`Scraper` class for downloading web pages,
extracting visible text and pulling out internal links.  It is designed
around static websites and uses Requests for HTTP and Beautiful Soup for
HTML parsing.  Dynamic pages that rely on JavaScript may require
additional tools such as Selenium【20†L133-L137】.
"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse
from typing import Optional, Set

import requests
from bs4 import BeautifulSoup


class Scraper:
    """Download and parse web pages.

    Parameters
    ----------
    user_agent : str, optional
        A custom User‑Agent header to send with each HTTP request.  If not
        provided a default identifying string is used.
    timeout : float, optional
        Number of seconds to wait for a server response before timing out.
    """

    def __init__(self, user_agent: Optional[str] = None, timeout: float = 10.0) -> None:
        default_agent = (
            "Mozilla/5.0 (compatible; InternetScraper/1.0;"
            " +https://example.com/bot)"
        )
        self.headers = {"User-Agent": user_agent or default_agent}
        self.timeout = timeout

    def fetch(self, url: str) -> Optional[str]:
        """Fetch a URL and return its HTML content as a string.

        If the request fails or returns a non‑200 status code, ``None``
        is returned and an error is printed to stderr.

        Parameters
        ----------
        url : str
            The page URL to download.

        Returns
        -------
        str or None
            The raw HTML response or ``None`` on error.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as exc:  # broad exception to catch network and HTTP errors
            print(f"Error fetching {url}: {exc}")
            return None

    def parse_text(self, html: str) -> str:
        """Extract visible text from an HTML document.

        The function removes ``<script>``, ``<style>`` and ``<noscript>`` tags,
        then returns all text separated by single spaces.  Multiple
        whitespace is collapsed into a single space and leading/trailing
        whitespace is stripped.

        Parameters
        ----------
        html : str
            The HTML document to parse.

        Returns
        -------
        str
            The cleaned text content of the page.
        """
        soup = BeautifulSoup(html, "html.parser")
        # Remove scripts, styles and noscript contents
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        # Collapse runs of whitespace to a single space
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_links(self, html: str, base_url: str) -> Set[str]:
        """Extract absolute links from an HTML document.

        Only links that point to the same domain as ``base_url`` are
        returned.  Fragment identifiers are removed and mailto/javascript
        links are ignored.

        Parameters
        ----------
        html : str
            The HTML document from which to extract links.
        base_url : str
            The URL of the page the HTML came from.  Used to resolve
            relative links and determine the domain.

        Returns
        -------
        set of str
            A set of absolute URLs pointing to the same domain.
        """
        soup = BeautifulSoup(html, "html.parser")
        links: Set[str] = set()
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            # Skip mailto or javascript links
            if href.startswith(("mailto:", "javascript:")):
                continue
            # Resolve relative links
            abs_url = urljoin(base_url, href)
            parsed_link = urlparse(abs_url)
            # Only follow links on the same domain
            if parsed_link.netloc == base_domain:
                abs_url_no_fragment = abs_url.split("#", 1)[0]
                links.add(abs_url_no_fragment)
        return links