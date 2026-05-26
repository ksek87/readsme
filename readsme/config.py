from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from .colors import assign_colors

VALID_STATUSES = {"reading", "read", "want-to-read"}


@dataclass
class Book:
    title: str
    author: str
    category: str
    status: str
    isbn: Optional[str] = None


@dataclass
class Config:
    books: list[Book]
    width: int
    category_colors: dict[str, str]


def _parse_config(data: dict, width_override: Optional[int] = None) -> Config:
    width = width_override if width_override is not None else int(data.get("width", 800))

    category_overrides: dict[str, str] = {}
    for cat, attrs in (data.get("categories") or {}).items():
        if isinstance(attrs, dict) and "color" in attrs:
            category_overrides[str(cat)] = str(attrs["color"])

    books: list[Book] = []
    for i, raw in enumerate(data.get("books") or []):
        for field in ("title", "author", "category", "status"):
            if field not in raw:
                raise ValueError(f"Book #{i + 1} is missing required field '{field}'")

        status = str(raw["status"]).lower().strip()
        if status not in VALID_STATUSES:
            raise ValueError(
                f"Book '{raw['title']}' has invalid status '{status}'. "
                f"Valid values: {', '.join(sorted(VALID_STATUSES))}"
            )

        books.append(
            Book(
                title=str(raw["title"]),
                author=str(raw["author"]),
                category=str(raw["category"]),
                status=status,
                isbn=str(raw["isbn"]) if "isbn" in raw else None,
            )
        )

    all_categories = list(dict.fromkeys(b.category for b in books))
    category_colors = assign_colors(all_categories, category_overrides)

    return Config(books=books, width=width, category_colors=category_colors)


def load_config(path: str | Path) -> Config:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return _parse_config(data)


def load_config_from_string(text: str, width_override: Optional[int] = None) -> Config:
    data = yaml.safe_load(text) or {}
    return _parse_config(data, width_override=width_override)
