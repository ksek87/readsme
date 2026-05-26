"""Update a README.md file between <!-- readsme-start --> / <!-- readsme-end --> markers."""
from __future__ import annotations

from pathlib import Path

START = "<!-- readsme-start -->"
END = "<!-- readsme-end -->"


def update_readme(readme_path: str | Path, svg_filename: str = "shelf.svg") -> bool:
    """
    Replace the content between readsme markers with an img tag pointing at svg_filename.
    If markers are absent, appends them at the end of the file.
    Returns True if the file was modified.
    """
    path = Path(readme_path)
    if not path.exists():
        return False

    content = path.read_text(encoding="utf-8")
    block = f"{START}\n![My bookshelf]({svg_filename})\n{END}"

    if START in content and END in content:
        start_idx = content.index(START)
        end_idx = content.index(END) + len(END)
        new_content = content[:start_idx] + block + content[end_idx:]
    else:
        sep = "\n\n" if content.strip() else ""
        new_content = content.rstrip() + sep + block + "\n"

    if new_content == content:
        return False

    path.write_text(new_content, encoding="utf-8")
    return True
