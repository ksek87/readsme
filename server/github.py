"""Fetch books.yaml from a user's GitHub profile repository."""
from __future__ import annotations

import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_RAW = "https://raw.githubusercontent.com/{user}/{user}/{branch}/books.yaml"
_BRANCHES = ("main", "master")


def _auth_headers() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN")
    return {"Authorization": f"Bearer {token}"} if token else {}


async def fetch_books_yaml(username: str, timeout: float = 8.0) -> Optional[str]:
    """
    Try main then master branch of {username}/{username}.
    Returns the raw YAML text, or None if not found.
    """
    headers = _auth_headers()
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        for branch in _BRANCHES:
            url = _RAW.format(user=username, branch=branch)
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.text
                if resp.status_code not in (404, 302):
                    logger.warning("Unexpected %s from %s", resp.status_code, url)
            except httpx.RequestError as exc:
                logger.warning("Request error fetching %s: %s", url, exc)
    return None
