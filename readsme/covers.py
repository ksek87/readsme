"""Phase 2: fetch book cover art from Open Library (fallback: Google Books).

Returns a base64 data URI so the SVG is fully self-contained and renders
correctly on GitHub, which blocks external image requests inside SVG files.
"""
from __future__ import annotations

import base64
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_OPEN_LIBRARY = "https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
_GOOGLE_BOOKS = "https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

# Open Library returns a 1×1 GIF for missing covers (~807 bytes)
_MIN_COVER_BYTES = 2000


def fetch_cover_data_uri(isbn: str, timeout: float = 10.0) -> Optional[str]:
    """Return a base64 JPEG data URI for the book cover, or None if unavailable."""
    if not isbn:
        return None

    try:
        import httpx
    except ImportError:
        logger.warning("httpx is required for cover fetching: pip install readsme[covers]")
        return None

    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        # 1. Open Library
        try:
            resp = client.get(_OPEN_LIBRARY.format(isbn=isbn))
            if resp.status_code == 200 and len(resp.content) >= _MIN_COVER_BYTES:
                return _to_data_uri(resp.content, "image/jpeg")
        except Exception as exc:
            logger.debug("Open Library failed for %s: %s", isbn, exc)

        # 2. Google Books
        try:
            resp = client.get(_GOOGLE_BOOKS.format(isbn=isbn))
            if resp.status_code == 200:
                items = resp.json().get("items") or []
                if items:
                    links = items[0].get("volumeInfo", {}).get("imageLinks", {})
                    url = links.get("thumbnail") or links.get("smallThumbnail")
                    if url:
                        img = client.get(url)
                        if img.status_code == 200 and img.content:
                            return _to_data_uri(img.content, "image/jpeg")
        except Exception as exc:
            logger.debug("Google Books failed for %s: %s", isbn, exc)

    return None


def _to_data_uri(data: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"
