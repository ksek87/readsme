"""Default warm library colour palette and category assignment."""
from __future__ import annotations

# Fallback pool cycled for uncategorised categories
WARM_PALETTE = [
    "#7B2D2D",  # dark red
    "#2C4A1E",  # forest green
    "#1B3A5C",  # navy
    "#5C3317",  # brown
    "#2D2744",  # dark purple
    "#6B4226",  # medium brown
    "#3D5A47",  # dark sage
    "#8B3A62",  # burgundy rose
    "#1A4A4A",  # dark teal
    "#5C4A1E",  # warm olive
    "#4A1E5C",  # deep plum
    "#3D4A1E",  # dark lime
]

CATEGORY_DEFAULTS: dict[str, str] = {
    "Fiction": "#7B2D2D",
    "Fantasy": "#5C3317",
    "Science Fiction": "#1B3A5C",
    "Sci-Fi": "#1B3A5C",
    "Non-fiction": "#2C4A1E",
    "Nonfiction": "#2C4A1E",
    "Biography": "#4A3728",
    "History": "#6B4226",
    "Mystery": "#2D2744",
    "Thriller": "#2D2D44",
    "Romance": "#8B3A62",
    "Technology": "#1A3A5C",
    "Programming": "#1A3A5C",
    "Philosophy": "#4A3F35",
    "Poetry": "#5C4A6E",
    "Self-help": "#3D5A47",
    "Self Help": "#3D5A47",
    "Business": "#5C4A1E",
    "Science": "#1A4A4A",
    "Art": "#8B4A1E",
    "Travel": "#2C5C5C",
    "Horror": "#2D1A1A",
    "Graphic Novel": "#6B3A5C",
    "Comics": "#6B3A5C",
    "Children": "#5C7A1E",
    "Young Adult": "#7A5C1E",
    "YA": "#7A5C1E",
    "Cooking": "#7A4A1E",
    "Psychology": "#1E3A5C",
    "Memoir": "#5C3D2D",
    "Classics": "#5C4A3D",
}


def assign_colors(categories: list[str], overrides: dict[str, str]) -> dict[str, str]:
    """Return a colour for every category: overrides > defaults > palette."""
    result: dict[str, str] = {}
    palette_index = 0
    for cat in categories:
        if cat in overrides:
            result[cat] = overrides[cat]
        elif cat in CATEGORY_DEFAULTS:
            result[cat] = CATEGORY_DEFAULTS[cat]
        else:
            result[cat] = WARM_PALETTE[palette_index % len(WARM_PALETTE)]
            palette_index += 1
    return result
