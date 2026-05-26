"""SVG spine-view renderer (Phase 1)."""
from __future__ import annotations

import math
from xml.sax.saxutils import escape

from .config import Book, Config

# --- layout constants (px) ---
SPINE_W = 44        # wide enough for text to breathe
SPINE_H = 160       # tall enough for ~24 chars at 10 px when rotated
SPINE_GAP = 5
SHELF_H = 14
SHELF_OVERHANG = 16
ROW_GAP = 18
SECTION_LABEL_H = 40
SECTION_GAP = 14
OUTER_PAD_X = 20
OUTER_PAD_TOP = 20
OUTER_PAD_BOT = 22

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


def _text_params(title: str) -> tuple[int, int]:
    """Return (font_size_px, max_chars) scaled to title length."""
    n = len(title)
    avail = SPINE_H - 24
    fs = 12 if n <= 11 else (11 if n <= 18 else 10)
    max_chars = int(avail / (fs * 0.56))
    return fs, max_chars


# --- layout helpers ---

def _books_per_row(max_width: int) -> int:
    avail = max_width - 2 * OUTER_PAD_X
    return max(1, (avail + SPINE_GAP) // (SPINE_W + SPINE_GAP))


def _row_svg_width(n_books: int, book_w: int = SPINE_W, book_gap: int = SPINE_GAP) -> int:
    """Exact SVG width for a shelf row of n_books."""
    row = n_books * (book_w + book_gap) - book_gap + 2 * SHELF_OVERHANG
    return row + 2 * OUTER_PAD_X


def _svg_width(sections: dict[str, list], bpr: int) -> int:
    """Auto-size SVG to the widest row actually used."""
    max_row = max(min(len(b), bpr) for b in sections.values() if b)
    return _row_svg_width(max_row)


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
    <radialGradient id="bgVignette" cx="50%" cy="50%" r="70%">
      <stop offset="0%"   stop-color="#F4E8C1" stop-opacity="0"/>
      <stop offset="100%" stop-color="#C8A870" stop-opacity="0.25"/>
    </radialGradient>
    <filter id="shelfShadow" x="-2%" y="-10%" width="104%" height="200%">
      <feDropShadow dx="0" dy="3" stdDeviation="2" flood-color="#3A2000" flood-opacity="0.22"/>
    </filter>
    <filter id="spineShadow" x="-10%" y="-2%" width="130%" height="104%">
      <feDropShadow dx="1" dy="0" stdDeviation="1.5" flood-color="#000000" flood-opacity="0.25"/>
    </filter>
    <style>
      @keyframes bookRise {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
      }
      @keyframes readingPulse {
        0%, 100% { opacity: 0; }
        50%      { opacity: 0.55; }
      }
      .book { animation: bookRise 0.45s ease-out both; }
      .reading-glow { animation: readingPulse 2.8s ease-in-out infinite; }

      /* light mode (default) */
      .bg          { fill: #F4E8C1; }
      .section-label { fill: #5C3D2D; }
      .section-line  { stroke: #C4A265; }

      /* dark mode */
      @media (prefers-color-scheme: dark) {
        .bg            { fill: #1C1810; }
        .section-label { fill: #C8A07A; }
        .section-line  { stroke: #6A4A28; }
      }
    </style>
  </defs>"""


def _svg_spine(book: Book, x: float, y: float, color: str, book_idx: int = 0) -> str:
    light = _lighten(color, 0.42)
    dark = _darken(color, 0.32)
    fs, max_chars = _text_params(book.title)
    title = _truncate(book.title, max_chars)
    tooltip = escape(f"{book.title} — {book.author} ({book.category})")
    cx = x + SPINE_W / 2
    cy = y + SPINE_H / 2
    delay = f"{book_idx * 0.07:.2f}s"

    # Golden glow overlay for currently-reading books
    glow = ""
    if book.status == "reading":
        glow = (
            f'\n    <rect class="reading-glow" x="{x:.1f}" y="{y:.1f}"'
            f' width="{SPINE_W}" height="{SPINE_H}"'
            f' fill="none" stroke="#E8C84A" stroke-width="2.5" rx="2"/>'
        )

    return (
        f'  <g class="book" filter="url(#spineShadow)"'
        f' style="animation-delay:{delay}">\n'
        f"    <title>{tooltip}</title>\n"
        # main spine body
        f'    <rect x="{x:.1f}" y="{y:.1f}" width="{SPINE_W}" height="{SPINE_H}"'
        f' fill="{color}" rx="2" ry="2"/>\n'
        # top highlight (simulates page edges)
        f'    <rect x="{x + 1:.1f}" y="{y:.1f}" width="{SPINE_W - 2}" height="3"'
        f' fill="#EDE8DF" rx="1" opacity="0.75"/>\n'
        # right shadow strip (depth illusion)
        f'    <rect x="{x + SPINE_W - 4:.1f}" y="{y:.1f}" width="4" height="{SPINE_H}"'
        f' fill="{dark}" opacity="0.4" rx="0"/>\n'
        # subtle inner highlight on left edge
        f'    <rect x="{x:.1f}" y="{y:.1f}" width="2" height="{SPINE_H}"'
        f' fill="{light}" opacity="0.4" rx="0"/>\n'
        # vertical title text
        f'    <text\n'
        f'      transform="rotate(-90,{cx:.1f},{cy:.1f})"\n'
        f'      x="{cx:.1f}" y="{cy:.1f}"\n'
        f'      text-anchor="middle" dy="0.35em"\n'
        f'      font-family="Arial,Helvetica,sans-serif"\n'
        f'      font-size="{fs}" font-weight="500"\n'
        f'      fill="white" opacity="0.92"\n'
        f'      pointer-events="none"\n'
        f"    >{escape(title)}</text>"
        f"{glow}\n"
        f"  </g>"
    )


def _svg_shelf(x: float, y: float, width: float) -> str:
    return (
        f'  <rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{SHELF_H}"'
        f' fill="url(#woodGrad)" rx="1" filter="url(#shelfShadow)"/>\n'
        f'  <rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="2"'
        f' fill="#F5E090" rx="1" opacity="0.45"/>'
    )


def _svg_section_label(status: str, y: float, width: int) -> str:
    label = escape(STATUS_LABELS[status])
    cx = width / 2
    text_y = y + 18
    line_y = text_y + 8
    lx = float(OUTER_PAD_X + 4)
    rx = float(width - OUTER_PAD_X - 4)

    gap = 55
    lines = ""
    if cx - lx > gap + 10:
        lines = (
            f'\n  <line class="section-line" x1="{lx:.1f}" y1="{line_y:.1f}"'
            f' x2="{cx - gap:.1f}" y2="{line_y:.1f}" stroke-width="0.8" opacity="0.5"/>'
            f'\n  <line class="section-line" x1="{cx + gap:.1f}" y1="{line_y:.1f}"'
            f' x2="{rx:.1f}" y2="{line_y:.1f}" stroke-width="0.8" opacity="0.5"/>'
        )

    return (
        f'  <text class="section-label" x="{cx:.1f}" y="{text_y:.1f}" text-anchor="middle"\n'
        f'    font-family="Georgia,\'Times New Roman\',serif"\n'
        f'    font-size="12" letter-spacing="1.5"\n'
        f'    font-style="italic"\n'
        f"  >{label}</text>"
        + lines
    )


# --- public API ---

def render(config: Config) -> str:
    sections: dict[str, list[Book]] = {s: [] for s in STATUS_ORDER}
    for book in config.books:
        sections[book.status].append(book)

    bpr = _books_per_row(config.width)
    svg_w = _svg_width(sections, bpr)
    total_h = _total_height(sections, bpr)
    non_empty = [s for s in STATUS_ORDER if sections[s]]

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{svg_w}" height="{total_h}"'
        f' role="img" aria-label="My bookshelf">',
        _svg_defs(),
        # background (colour overridden in dark mode via .bg CSS class)
        f'  <rect class="bg" width="{svg_w}" height="{total_h}" rx="8" ry="8"/>',
        # warm vignette overlay
        f'  <rect width="{svg_w}" height="{total_h}"'
        f' fill="url(#bgVignette)" rx="8" ry="8"/>',
    ]

    book_idx = 0
    y = float(OUTER_PAD_TOP)
    for sec_idx, status in enumerate(non_empty):
        books = sections[status]
        parts.append(_svg_section_label(status, y, svg_w))
        y += SECTION_LABEL_H

        rows = [books[i : i + bpr] for i in range(0, len(books), bpr)]
        for row_idx, row_books in enumerate(rows):
            x = float(OUTER_PAD_X)
            for book in row_books:
                color = config.category_colors.get(book.category, "#4A4A4A")
                parts.append(_svg_spine(book, x, y, color, book_idx))
                x += SPINE_W + SPINE_GAP
                book_idx += 1

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
