"""Phase 2: SVG shelf renderer with real book cover images.

Generates the same warm-shelf aesthetic as the spine view, but each book
slot shows the actual cover art fetched from Open Library. Books without
a cover (missing ISBN or failed fetch) fall back to a wider spine tile so
the shelf stays visually complete.
"""
from __future__ import annotations

import math
from xml.sax.saxutils import escape

from .config import Book, Config
from .renderer import (
    BG_COLOR,
    OUTER_PAD_BOT,
    OUTER_PAD_TOP,
    OUTER_PAD_X,
    ROW_GAP,
    SECTION_GAP,
    SECTION_LABEL_H,
    SHELF_H,
    SHELF_OVERHANG,
    STATUS_LABELS,
    STATUS_ORDER,
    _darken,
    _lighten,
    _svg_defs,
    _svg_section_label,
    _svg_shelf,
    _truncate,
)

COVER_W = 90
COVER_H = 130
COVER_GAP = 8
COVER_RADIUS = 3


def _books_per_row_covers(width: int) -> int:
    avail = width - 2 * OUTER_PAD_X
    return max(1, (avail + COVER_GAP) // (COVER_W + COVER_GAP))


def _total_height_covers(sections: dict[str, list], bpr: int) -> int:
    h = OUTER_PAD_TOP
    non_empty = [s for s in STATUS_ORDER if sections.get(s)]
    for idx, status in enumerate(non_empty):
        n_rows = math.ceil(len(sections[status]) / bpr)
        h += SECTION_LABEL_H
        h += n_rows * (COVER_H + SHELF_H)
        h += (n_rows - 1) * ROW_GAP
        if idx < len(non_empty) - 1:
            h += SECTION_GAP
    h += OUTER_PAD_BOT
    return h


def _svg_cover_book(
    book: Book,
    x: float,
    y: float,
    color: str,
    data_uri: str | None,
    clip_id: str,
) -> tuple[str, str]:
    """Return (clip_def, book_element) SVG strings."""
    tooltip = escape(f"{book.title} — {book.author} ({book.category})")
    clip_def = (
        f'    <clipPath id="{clip_id}">'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{COVER_W}" height="{COVER_H}"'
        f' rx="{COVER_RADIUS}"/>'
        f"</clipPath>"
    )

    if data_uri:
        body = (
            # drop shadow
            f'    <rect x="{x + 3:.1f}" y="{y + 3:.1f}" width="{COVER_W}" height="{COVER_H}"'
            f' fill="#000" opacity="0.18" rx="{COVER_RADIUS}"/>\n'
            # cover image, clipped to rounded rect
            f'    <image x="{x:.1f}" y="{y:.1f}" width="{COVER_W}" height="{COVER_H}"\n'
            f'           href="{data_uri}"\n'
            f'           clip-path="url(#{clip_id})"\n'
            f'           preserveAspectRatio="xMidYMid slice"/>\n'
            # subtle border overlay
            f'    <rect x="{x:.1f}" y="{y:.1f}" width="{COVER_W}" height="{COVER_H}"'
            f' fill="none" stroke="#00000028" stroke-width="1" rx="{COVER_RADIUS}"/>'
        )
    else:
        # Spine fallback at cover width
        light = _lighten(color, 0.4)
        dark = _darken(color, 0.32)
        title = _truncate(book.title, 28)
        cx = x + COVER_W / 2
        cy = y + COVER_H / 2
        body = (
            f'    <rect x="{x:.1f}" y="{y:.1f}" width="{COVER_W}" height="{COVER_H}"'
            f' fill="{color}" rx="{COVER_RADIUS}"/>\n'
            f'    <rect x="{x:.1f}" y="{y:.1f}" width="{COVER_W}" height="4"'
            f' fill="{light}" rx="{COVER_RADIUS}" opacity="0.65"/>\n'
            f'    <rect x="{x + COVER_W - 4:.1f}" y="{y:.1f}" width="4" height="{COVER_H}"'
            f' fill="{dark}" opacity="0.5"/>\n'
            f'    <text\n'
            f'      transform="rotate(-90,{cx:.1f},{cy:.1f})"\n'
            f'      x="{cx:.1f}" y="{cy:.1f}"\n'
            f'      text-anchor="middle" dy="0.35em"\n'
            f'      font-family="Arial,Helvetica,sans-serif"\n'
            f'      font-size="11" font-weight="500"\n'
            f'      fill="white" opacity="0.93"\n'
            f'      pointer-events="none"\n'
            f"    >{escape(title)}</text>"
        )

    element = (
        f'  <g class="book">\n'
        f"    <title>{tooltip}</title>\n"
        f"{body}\n"
        f"  </g>"
    )
    return clip_def, element


def render_covers(config: Config, cover_data: dict[str, str | None]) -> str:
    """
    Render an SVG shelf using real cover images.

    cover_data maps isbn → base64 data URI (or None if unavailable).
    Books without ISBNs or with None values fall back to a wide spine tile.
    """
    sections: dict[str, list[Book]] = {s: [] for s in STATUS_ORDER}
    for book in config.books:
        sections[book.status].append(book)

    bpr = _books_per_row_covers(config.width)
    total_h = _total_height_covers(sections, bpr)
    non_empty = [s for s in STATUS_ORDER if sections[s]]

    clip_defs: list[str] = []
    body_parts: list[str] = []
    clip_counter = 0

    y = float(OUTER_PAD_TOP)
    for sec_idx, status in enumerate(non_empty):
        books = sections[status]
        body_parts.append(_svg_section_label(status, y, config.width))
        y += SECTION_LABEL_H

        rows = [books[i : i + bpr] for i in range(0, len(books), bpr)]
        for row_idx, row_books in enumerate(rows):
            x = float(OUTER_PAD_X)
            for book in row_books:
                color = config.category_colors.get(book.category, "#4A4A4A")
                uri = cover_data.get(book.isbn) if book.isbn else None
                clip_id = f"cc{clip_counter}"
                clip_counter += 1
                clip_def, element = _svg_cover_book(book, x, y, color, uri, clip_id)
                clip_defs.append(clip_def)
                body_parts.append(element)
                x += COVER_W + COVER_GAP

            shelf_x = OUTER_PAD_X - SHELF_OVERHANG
            shelf_w = len(row_books) * (COVER_W + COVER_GAP) - COVER_GAP + 2 * SHELF_OVERHANG
            body_parts.append(_svg_shelf(shelf_x, y + COVER_H, shelf_w))

            y += COVER_H + SHELF_H
            if row_idx < len(rows) - 1:
                y += ROW_GAP

        if sec_idx < len(non_empty) - 1:
            y += SECTION_GAP

    clip_block = ""
    if clip_defs:
        clip_block = "  <defs>\n" + "\n".join(clip_defs) + "\n  </defs>\n"

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{config.width}" height="{total_h}"'
        f' role="img" aria-label="My bookshelf">',
        _svg_defs(),
        clip_block,
        f'  <rect width="{config.width}" height="{total_h}"'
        f' fill="{BG_COLOR}" rx="8" ry="8"/>',
        *body_parts,
        "</svg>",
    ])
