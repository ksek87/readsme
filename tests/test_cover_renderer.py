"""Tests for the Phase 2 cover renderer."""
from readsme.config import Book, Config
from readsme.colors import assign_colors
from readsme.cover_renderer import render_covers, _books_per_row_covers


def _cfg(books, width=800):
    cats = list(dict.fromkeys(b.category for b in books))
    return Config(books=books, width=width, category_colors=assign_colors(cats, {}))


def test_render_covers_produces_svg():
    books = [
        Book("Dune", "Frank Herbert", "Sci-Fi", "reading", "9780441013593"),
        Book("1984", "George Orwell", "Fiction", "read"),
    ]
    svg = render_covers(_cfg(books), {})
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert "Currently Reading" in svg
    assert "Read" in svg


def test_render_covers_embeds_data_uri():
    books = [Book("Dune", "Frank Herbert", "Sci-Fi", "read", "9780441013593")]
    fake_uri = "data:image/jpeg;base64,/9j/FAKE"
    svg = render_covers(_cfg(books), {"9780441013593": fake_uri})
    assert fake_uri in svg
    assert '<image' in svg


def test_render_covers_fallback_spine_when_no_uri():
    books = [Book("1984", "Orwell", "Fiction", "read", "9780000000001")]
    svg = render_covers(_cfg(books), {"9780000000001": None})
    # No <image> element — should use spine fallback
    assert "<image" not in svg
    assert "1984" in svg


def test_render_covers_no_isbn_uses_spine():
    books = [Book("No ISBN Book", "Author", "Fiction", "read")]
    svg = render_covers(_cfg(books), {})
    assert "<image" not in svg
    assert "No ISBN Book" in svg


def test_books_per_row_covers_less_than_spines():
    from readsme.renderer import _books_per_row
    assert _books_per_row_covers(800) < _books_per_row(800)


def test_render_covers_clip_paths_generated():
    books = [
        Book("Book A", "A", "Fiction", "read", "1111111111111"),
        Book("Book B", "B", "Fiction", "read", "2222222222222"),
    ]
    cover_data = {
        "1111111111111": "data:image/jpeg;base64,AAAA",
        "2222222222222": "data:image/jpeg;base64,BBBB",
    }
    svg = render_covers(_cfg(books), cover_data)
    assert "clipPath" in svg
    assert "cc0" in svg
    assert "cc1" in svg


def test_render_covers_skips_empty_sections():
    books = [Book("Only Read", "A", "Fiction", "read")]
    svg = render_covers(_cfg(books), {})
    assert "Currently Reading" not in svg
    assert "Want to Read" not in svg
    assert "Read" in svg
