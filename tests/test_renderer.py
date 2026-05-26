"""Basic smoke tests for the SVG renderer."""
import pytest
from readsme.config import load_config, Book, Config
from readsme.renderer import render, _books_per_row, _truncate
from readsme.readme import update_readme, START, END
import tempfile
from pathlib import Path


def _make_config(books, width=800):
    from readsme.colors import assign_colors
    categories = list(dict.fromkeys(b.category for b in books))
    return Config(books=books, width=width, category_colors=assign_colors(categories, {}))


def test_render_produces_svg():
    books = [
        Book("Dune", "Frank Herbert", "Sci-Fi", "reading", "9780441013593"),
        Book("1984", "George Orwell", "Fiction", "read"),
        Book("Neuromancer", "William Gibson", "Sci-Fi", "want-to-read"),
    ]
    svg = render(_make_config(books))
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert "Currently Reading" in svg
    assert "Read" in svg
    assert "Want to Read" in svg


def test_render_escapes_ampersand():
    books = [Book("Hunt & Thomas", "Authors", "Programming", "read")]
    svg = render(_make_config(books))
    assert "&amp;" in svg
    # raw unescaped ampersand must not appear in attribute or text content
    assert " & " not in svg.replace("&amp;", "")


def test_render_skips_empty_sections():
    books = [Book("Dune", "Frank Herbert", "Sci-Fi", "read")]
    svg = render(_make_config(books))
    assert "Currently Reading" not in svg
    assert "Want to Read" not in svg


def test_truncate():
    assert _truncate("Short", 20) == "Short"
    assert _truncate("A" * 25, 20) == "A" * 19 + "…"
    assert len(_truncate("X" * 30, 20)) == 20


def test_books_per_row():
    assert _books_per_row(800) > 0
    assert _books_per_row(400) < _books_per_row(800)


def test_load_config(tmp_path):
    yaml_content = """\
width: 600
books:
  - title: Dune
    author: Frank Herbert
    category: Sci-Fi
    status: reading
    isbn: "9780441013593"
  - title: "1984"
    author: George Orwell
    category: Fiction
    status: read
"""
    p = tmp_path / "books.yaml"
    p.write_text(yaml_content)
    config = load_config(p)
    assert config.width == 600
    assert len(config.books) == 2
    assert config.books[0].isbn == "9780441013593"
    assert config.books[1].isbn is None


def test_load_config_invalid_status(tmp_path):
    p = tmp_path / "books.yaml"
    p.write_text("books:\n  - title: X\n    author: Y\n    category: Z\n    status: invalid\n")
    with pytest.raises(ValueError, match="invalid status"):
        load_config(p)


def test_readme_update_with_markers(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(f"# Hello\n\n{START}\nold content\n{END}\n\nfooter\n")
    changed = update_readme(readme, "shelf.svg")
    assert changed
    content = readme.read_text()
    assert "![My bookshelf](shelf.svg)" in content
    assert "old content" not in content
    assert "footer" in content


def test_readme_update_appends_when_no_markers(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Hello\n")
    changed = update_readme(readme, "shelf.svg")
    assert changed
    content = readme.read_text()
    assert START in content
    assert END in content
    assert "![My bookshelf](shelf.svg)" in content


def test_readme_update_no_change(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(f"{START}\n![My bookshelf](shelf.svg)\n{END}\n")
    changed = update_readme(readme, "shelf.svg")
    assert not changed
