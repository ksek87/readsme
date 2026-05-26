"""Basic smoke tests for the API endpoints."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.index import app

SAMPLE_YAML = """\
books:
  - title: "Meditations"
    author: "Marcus Aurelius"
    category: Philosophy
    status: read
"""


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_landing_page():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/")
    assert resp.status_code == 200
    assert "readsme" in resp.text
    assert "books.yaml" in resp.text


@pytest.mark.asyncio
async def test_shelf_renders_svg():
    with patch("api.index.fetch_books_yaml", new=AsyncMock(return_value=SAMPLE_YAML)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.get("/shelf/someuser")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("image/svg+xml")
    assert "<svg" in resp.text
    assert "Meditations" in resp.text


@pytest.mark.asyncio
async def test_shelf_not_found():
    with patch("api.index.fetch_books_yaml", new=AsyncMock(return_value=None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.get("/shelf/ghost")
    assert resp.status_code == 200
    assert "<svg" in resp.text
    assert "no bookshelf found" in resp.text


@pytest.mark.asyncio
async def test_shelf_empty():
    with patch("api.index.fetch_books_yaml", new=AsyncMock(return_value="books: []")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.get("/shelf/emptyuser")
    assert resp.status_code == 200
    assert "shelf is empty" in resp.text


@pytest.mark.asyncio
async def test_shelf_invalid_username():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/shelf/bad--user..name!")
    assert resp.status_code == 200
    assert "something went wrong" in resp.text or "Invalid" in resp.text


@pytest.mark.asyncio
async def test_shelf_bad_yaml():
    with patch("api.index.fetch_books_yaml", new=AsyncMock(return_value="books:\n  - title: oops\n")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.get("/shelf/badyaml")
    assert resp.status_code == 200
    assert "something went wrong" in resp.text


@pytest.mark.asyncio
async def test_shelf_width_override():
    with patch("api.index.fetch_books_yaml", new=AsyncMock(return_value=SAMPLE_YAML)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.get("/shelf/someuser?width=400")
    assert resp.status_code == 200
    assert "<svg" in resp.text


@pytest.mark.asyncio
async def test_shelf_cache_headers_hit():
    with patch("api.index.fetch_books_yaml", new=AsyncMock(return_value=SAMPLE_YAML)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.get("/shelf/someuser")
    assert "max-age=300" in resp.headers.get("cache-control", "")


@pytest.mark.asyncio
async def test_shelf_cache_headers_miss():
    with patch("api.index.fetch_books_yaml", new=AsyncMock(return_value=None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.get("/shelf/ghost")
    assert "max-age=60" in resp.headers.get("cache-control", "")
