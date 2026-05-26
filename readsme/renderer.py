"""SVG spine-view renderer (Phase 1)."""
from __future__ import annotations

import math
from xml.sax.saxutils import escape

from .config import Book, Config

# --- layout constants (px) ---
SPINE_W = 32
SPINE_H = 130
SPINE_GAP = 4
SHELF_H = 16
SHELF_OVERHANG = 14
ROW_GAP = 20
SECTION_LABEL_H = 48
SECTION_GAP = 16
OUTER_PAD_X = 24
OUTER_PAD_TOP = 28
OUTER_PAD_BOT = 28

BG_COLOR = "#F4E8C1"

STATUS_ORDER = ["reading", "read", "want-to-read"]
STATUS_LABELS = {
    "reading": "Currently Reading",
    "read": "Read",
    "want-to-read": "Want to Read",
}


# --- colour helpers ---

def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def _lighten(color: str, factor: float = 0.35) -> str:
    r, g, b = _hex_to_rgb(color)
    return _rgb_to_hex(
        min(255, int(r + (255 - r) * factor)),
        min(255, int(g + (255 - g) * factor)),
        min(255, int(b + (255 - b) * factor)),
    )


def _darken(color: str, factor: float = 0.35) -> str:
    r, g, b = _hex_to_rgb(color)
    return _rgb_to_hex(
        max(0, int(r * (1 - factor))),
        max(0, int(g * (1 - factor))),
        max(0, int(b * (1 - factor))),
    )


def _truncate(text: str, max_chars: int = 20) -> str:
    return text if len(text) <= max_chars else text[: max_chars - 1] + "…"


# --- layout helpers ---

def _books_per_row(width: int) -> int:
    avail = width - 2 * OUTER_PAD_X
    return max(1, (avail + SPINE_GAP) // (SPINE_W + SPINE_GAP))


def _total_height(sections: dict[str, list], bpr: int) -> int:
    h = OUTER_PAD_TOP
    non_empty = [s for s in STATUS_ORDER if sections.get(s)]
    for idx, status in enumerate(non_empty):
        n_rows = math.ceil(len(sections[status]) / bpr)
        h += SECTION_LABEL_H
        h += n_rows * (SPINE_H + SHELF_H)
        h += (n_rows - 1) * ROW_GAP
        if idx < len(non_empty) - 1:
            h += SECTION_GAP
    h += OUTER_PAD_BOT
    return h


# --- SVG fragment builders ---

def _svg_defs() -> str:
    return """\
  <defs>
    <linearGradient id="woodGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#EDD080"/>
      <stop offset="20%"  stop-color="#C8A050"/>
      <stop offset="100%" stop-color="#8A6228"/>
    </linearGradient>
    <filter id="shelfShadow" x="-2%" y="-10%" width="104%" height="200%">
      <feDropShadow dx="0" dy="3" stdDeviation="2" flood-color="#3A2000" flood-opacity="0.22"/>
    </filter>
    <filter id="spineShadow" x="-10%" y="-2%" width="130%" height="104%">
      <feDropShadow dx="1" dy="0" stdDeviation="1.5" flood-color="#000000" flood-opacity="0.25"/>
    </filter>
  </defs>"""


def _svg_spine(book: Book, x: float, y: float, color: str) -> str:
    light = _lighten(color, 0.4)
    dark = _darken(color, 0.32)
    title = _truncate(book.title, 20)
    tooltip = escape(f"{book.title} — {book.author} ({book.category})")
    cx = x + SPINE_W / 2
    cy = y + SPINE_H / 2

    return (
        f'  <g class="book" filter="url(#spineShadow)">\n'
        f"    <title>{tooltip}</title>\n"
        f'    <rect x="{x:.1f}" y="{y:.1f}" width="{SPINE_W}" height="{SPINE_H}"'
        f' fill="{color}" rx="2" ry="2"/>\n'
        # top highlight strip
        f'    <rect x="{x:.1f}" y="{y:.1f}" width="{SPINE_W}" height="4"'
        f' fill="{light}" rx="2" ry="2" opacity="0.65"/>\n'
        # right shadow strip
        f'    <rect x="{x + SPINE_W - 4:.1f}" y="{y:.1f}" width="4" height="{SPINE_H}"'
        f' fill="{dark}" opacity="0.5" rx="0"/>\n'
        # vertical title
        f'    <text\n'
        f'      transform="rotate(-90,{cx:.1f},{cy:.1f})"\n'
        f'      x="{cx:.1f}" y="{cy:.1f}"\n'
        f'      text-anchor="middle" dy="0.35em"\n'
        f'      font-family="Arial,Helvetica,sans-serif"\n'
        f'      font-size="10" font-weight="500"\n'
        f'      fill="white" opacity="0.93"\n'
        f'      pointer-events="none"\n'
        f"    >{escape(title)}</text>\n"
        f"  </g>"
    )


def _svg_shelf(x: float, y: float, width: float) -> str:
    return (
        f'  <rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{SHELF_H}"'
        f' fill="url(#woodGrad)" rx="1" filter="url(#shelfShadow)"/>\n'
        # top sheen
        f'  <rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="2"'
        f' fill="#F5E090" rx="1" opacity="0.45"/>'
    )


def _svg_section_label(status: str, y: float, width: int) -> str:
    label = escape(STATUS_LABELS[status])
    cx = width / 2
    text_y = y + 22
    line_y = text_y + 9
    lx = float(OUTER_PAD_X + 4)
    rx = float(width - OUTER_PAD_X - 4)

    return (
        f'  <text x="{cx:.1f}" y="{text_y:.1f}" text-anchor="middle"\n'
        f'    font-family="Georgia,\'Times New Roman\',serif"\n'
        f'    font-size="13" fill="#5C3D2D" letter-spacing="1.5"\n'
        f"    font-style=\"italic\"\n"
        f"  >{label}</text>\n"
        f'  <line x1="{lx:.1f}" y1="{line_y:.1f}" x2="{cx - 72:.1f}" y2="{line_y:.1f}"'
        f' stroke="#C4A265" stroke-width="0.8" opacity="0.5"/>\n'
        f'  <line x1="{cx + 72:.1f}" y1="{line_y:.1f}" x2="{rx:.1f}" y2="{line_y:.1f}"'
        f' stroke="#C4A265" stroke-width="0.8" opacity="0.5"/>'
    )


# --- public API ---

def render(config: Config) -> str:
    sections: dict[str, list[Book]] = {s: [] for s in STATUS_ORDER}
    for book in config.books:
        sections[book.status].append(book)

    bpr = _books_per_row(config.width)
    total_h = _total_height(sections, bpr)
    non_empty = [s for s in STATUS_ORDER if sections[s]]

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{config.width}" height="{total_h}"'
        f' role="img" aria-label="My bookshelf">',
        _svg_defs(),
        f'  <rect width="{config.width}" height="{total_h}"'
        f' fill="{BG_COLOR}" rx="8" ry="8"/>',
    ]

    y = float(OUTER_PAD_TOP)
    for sec_idx, status in enumerate(non_empty):
        books = sections[status]
        parts.append(_svg_section_label(status, y, config.width))
        y += SECTION_LABEL_H

        rows = [books[i : i + bpr] for i in range(0, len(books), bpr)]
        for row_idx, row_books in enumerate(rows):
            x = float(OUTER_PAD_X)
            for book in row_books:
                color = config.category_colors.get(book.category, "#4A4A4A")
                parts.append(_svg_spine(book, x, y, color))
                x += SPINE_W + SPINE_GAP

            shelf_x = OUTER_PAD_X - SHELF_OVERHANG
            shelf_w = len(row_books) * (SPINE_W + SPINE_GAP) - SPINE_GAP + 2 * SHELF_OVERHANG
            parts.append(_svg_shelf(shelf_x, y + SPINE_H, shelf_w))

            y += SPINE_H + SHELF_H
            if row_idx < len(rows) - 1:
                y += ROW_GAP

        if sec_idx < len(non_empty) - 1:
            y += SECTION_GAP

    parts.append("</svg>")
    return "\n".join(parts)
