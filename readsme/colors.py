"""Default warm library colour palette and category assignment."""
from __future__ import annotations

# Fallback pool cycled for uncategorised categories.
# Chosen to be visually distinct, rich, and readable against white text.
WARM_PALETTE = [
    "#8B1F1F",  # deep crimson
    "#1A5C3A",  # forest green
    "#0D2A42",  # deep navy
    "#5C2A10",  # dark burnt sienna
    "#3A1060",  # deep violet
    "#7A3A18",  # terracotta
    "#0D3D4A",  # dark teal
    "#8B1A4A",  # deep rose
    "#3A5C0A",  # dark moss
    "#6A3010",  # warm umber
    "#1E1A38",  # midnight indigo
    "#4A2C1E",  # dark warm brown
]

CATEGORY_DEFAULTS: dict[str, str] = {
    "Fiction":          "#8B1F1F",  # deep crimson
    "Fantasy":          "#5C2A10",  # dark burnt sienna
    "Science Fiction":  "#0D2A42",  # deep navy
    "Sci-Fi":           "#0D2A42",
    "Non-fiction":      "#1A5C3A",  # forest green
    "Nonfiction":       "#1A5C3A",
    "Biography":        "#4A2C1E",  # dark warm brown
    "History":          "#7A3A18",  # terracotta
    "Mystery":          "#1E1A38",  # midnight indigo
    "Thriller":         "#1A1A30",  # very dark blue
    "Romance":          "#8B1A4A",  # deep rose
    "Technology":       "#0D2A42",  # deep navy
    "Programming":      "#102A38",  # dark cyan-navy
    "Philosophy":       "#3A1060",  # deep violet
    "Poetry":           "#4A1048",  # deep plum
    "Self-help":        "#1A5C3A",  # forest green
    "Self Help":        "#1A5C3A",
    "Business":         "#8B2515",  # warm brick red
    "Science":          "#0D3D4A",  # dark teal
    "Art":              "#7A2E10",  # burnt sienna
    "Travel":           "#0D4040",  # dark teal-green
    "Horror":           "#1A0808",  # near black
    "Graphic Novel":    "#4A1A3A",  # dark magenta
    "Comics":           "#4A1A3A",
    "Children":         "#3A6010",  # bright moss green
    "Young Adult":      "#604A10",  # dark gold
    "YA":               "#604A10",
    "Cooking":          "#6A3010",  # warm umber
    "Psychology":       "#0D2A3A",  # dark blue
    "Memoir":           "#4A2C20",  # warm dark brown
    "Classics":         "#3A2818",  # very dark warm brown
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
