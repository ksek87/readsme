"""Fetch book cover images from Open Library (fallback: Google Books).

Covers are cached in .readsme-cache/ as JPEG files so subsequent runs are
instant. Returns base64 data URIs — GitHub blocks external URLs inside SVGs,
so embedding is the only way to guarantee the images render in a README.
"""
from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_OPEN_LIBRARY = "https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
_GOOGLE_BOOKS = "https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

# Open Library sends a 1×1 GIF (~807 bytes) when no cover exists
_MIN_COVER_BYTES = 2_000

DEFAULT_CACHE_DIR = Path(".readsme-cache") / "covers"


def get_cover_data_uri(
    isbn: str,
    *,
    cache_dir: Optional[Path] = DEFAULT_CACHE_DIR,
    force: bool = False,
    timeout: float = 10.0,
) -> Optional[str]:
    """Return a base64 JPEG data URI for the cover, or None if unavailable."""
    if not isbn:
        return None

    cached = _cache_get(isbn, cache_dir) if (cache_dir and not force) else None
    if cached:
        return _to_data_uri(cached)

    data = _fetch_bytes(isbn, timeout)
    if data and cache_dir:
        _cache_put(isbn, data, cache_dir)
    return _to_data_uri(data) if data else None


# --- cache helpers ---

def _cache_path(isbn: str, cache_dir: Path) -> Path:
    return cache_dir / f"{isbn}.jpg"


def _cache_get(isbn: str, cache_dir: Path) -> Optional[bytes]:
    path = _cache_path(isbn, cache_dir)
    if path.exists():
        return path.read_bytes()
    return None


def _cache_put(isbn: str, data: bytes, cache_dir: Path) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    _cache_path(isbn, cache_dir).write_bytes(data)


# --- network helpers ---

def _fetch_bytes(isbn: str, timeout: float) -> Optional[bytes]:
    try:
        import httpx
    except ImportError:
        logger.warning("httpx required for cover art: pip install readsme[covers]")
        return None

    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        data = _try_open_library(client, isbn)
        if data:
            return data
        return _try_google_books(client, isbn)


def _try_open_library(client, isbn: str) -> Optional[bytes]:
    try:
        resp = client.get(_OPEN_LIBRARY.format(isbn=isbn))
        if resp.status_code == 200 and len(resp.content) >= _MIN_COVER_BYTES:
            return resp.content
    except Exception as exc:
        logger.debug("Open Library failed for %s: %s", isbn, exc)
    return None


def _try_google_books(client, isbn: str) -> Optional[bytes]:
    try:
        resp = client.get(_GOOGLE_BOOKS.format(isbn=isbn))
        if resp.status_code != 200:
            return None
        items = resp.json().get("items") or []
        if not items:
            return None
        links = items[0].get("volumeInfo", {}).get("imageLinks", {})
        url = links.get("thumbnail") or links.get("smallThumbnail")
        if url:
            img = client.get(url)
            if img.status_code == 200 and img.content:
                return img.content
    except Exception as exc:
        logger.debug("Google Books failed for %s: %s", isbn, exc)
    return None


def _to_data_uri(data: bytes) -> str:
    return f"data:image/jpeg;base64,{base64.b64encode(data).decode()}"
