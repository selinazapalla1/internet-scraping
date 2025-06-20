"""Simple keyword extraction based on term frequency.

This module defines a function to extract the most frequent non‑trivial words
from a block of text.  It uses a list of stopwords to filter common English
words and then ranks the remaining words by frequency.  The algorithm is
deliberately simple to avoid heavy NLP dependencies and to work on small
projects without external resources.
"""

from __future__ import annotations

import collections
import re
from typing import Iterable, List, Set

# A minimal set of common English stopwords.  Feel free to extend this list
# or install nltk and use its stopword corpus for better results.
_STOPWORDS: Set[str] = {
    "the", "and", "for", "that", "with", "this", "from", "which", "your",
    "have", "will", "are", "not", "you", "but", "can", "all", "about",
    "their", "there", "when", "what", "where", "who", "why", "been",
    "here", "such", "into", "they", "them", "then", "were", "also", "more",
    "most", "some", "does", "than", "other", "these", "those", "like",
    "just", "make", "made", "each", "many", "much", "because", "could",
    "would", "should", "very", "within", "without", "still", "over",
    "under", "again", "where", "after", "before", "while", "being", "else",
    "ever", "every", "upon", "once", "said", "tell", "told", "good",
    "bad", "another", "few", "own", "use", "used", "using", "uses",
}


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract the top N keywords from a block of text.

    The function lowercases the text, removes non‑alphanumeric characters and
    splits on whitespace.  Words shorter than four characters or present in
    the stopword list are ignored.  The remaining words are counted and
    sorted by frequency.  Ties are broken arbitrarily based on hash order.

    Parameters
    ----------
    text : str
        The input text from which to extract keywords.
    top_n : int, optional
        The number of keywords to return.  Defaults to 10.

    Returns
    -------
    list of str
        A list containing up to ``top_n`` keywords ordered by frequency.
    """
    # Normalize case and remove punctuation
    text = text.lower()
    # Replace non alphanumeric characters with spaces
    cleaned = re.sub(r"[^a-z0-9]+", " ", text)
    tokens = cleaned.split()
    # Filter tokens
    words = [w for w in tokens if len(w) > 3 and w not in _STOPWORDS]
    counter = collections.Counter(words)
    most_common = counter.most_common(top_n)
    return [word for word, count in most_common]