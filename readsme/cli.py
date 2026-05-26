from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import load_config
from .renderer import render
from .readme import update_readme


def _cmd_generate(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: '{config_path}' not found.", file=sys.stderr)
        print("Create a books.yaml — see books.example.yaml for the format.", file=sys.stderr)
        return 1

    try:
        config = load_config(config_path)
    except Exception as exc:
        print(f"Error reading config: {exc}", file=sys.stderr)
        return 1

    if not config.books:
        print("No books in config. Add some entries to books.yaml.", file=sys.stderr)
        return 1

    if args.mode == "covers":
        svg = _generate_covers(config, args)
    else:
        svg = render(config)

    if svg is None:
        return 1

    output = Path(args.output)
    output.write_text(svg, encoding="utf-8")
    print(f"✓ Wrote {output}  ({len(config.books)} book{'s' if len(config.books) != 1 else ''})")

    if args.readme:
        readme = Path(args.readme)
        if update_readme(readme, output.name):
            print(f"✓ Updated {readme}")
        elif readme.exists():
            from .readme import START
            has_markers = START in readme.read_text(encoding="utf-8")
            if has_markers:
                print(f"  {readme}: already up to date")
            else:
                print(
                    f"  {readme}: add <!-- readsme-start --> / <!-- readsme-end --> markers "
                    "to auto-embed the shelf."
                )

    return 0


def _generate_covers(config, args: argparse.Namespace):
    try:
        from .covers import get_cover_data_uri, DEFAULT_CACHE_DIR
        from .cover_renderer import render_covers
    except ImportError:
        pass  # covers.py always importable; httpx checked inside

    cache_dir = None if args.no_cache else DEFAULT_CACHE_DIR
    force = args.no_cache

    books_with_isbn = [(b, b.isbn) for b in config.books if b.isbn]
    total = len(books_with_isbn)
    print(f"Fetching covers for {total} book{'s' if total != 1 else ''} with ISBNs...")

    cover_data: dict[str, str | None] = {}
    for idx, (book, isbn) in enumerate(books_with_isbn, 1):
        label = _truncate_label(book.title, 35)
        print(f"  [{idx}/{total}] {label} ({isbn})", end=" ... ", flush=True)
        uri = get_cover_data_uri(isbn, cache_dir=cache_dir, force=force)
        cover_data[isbn] = uri
        print("ok" if uri else "no cover, using spine")

    no_isbn = sum(1 for b in config.books if not b.isbn)
    if no_isbn:
        print(f"  {no_isbn} book{'s' if no_isbn != 1 else ''} without ISBN → spine fallback")

    from .cover_renderer import render_covers
    return render_covers(config, cover_data)


def _truncate_label(text: str, n: int) -> str:
    return text if len(text) <= n else text[: n - 1] + "…"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="readsme",
        description="Generate a visual bookshelf SVG for your GitHub profile README.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", aliases=["gen"], help="Render the bookshelf SVG")
    gen.add_argument(
        "--config", "-c",
        default="books.yaml",
        metavar="PATH",
        help="Path to books.yaml (default: books.yaml)",
    )
    gen.add_argument(
        "--output", "-o",
        default="shelf.svg",
        metavar="PATH",
        help="Output SVG path (default: shelf.svg)",
    )
    gen.add_argument(
        "--readme", "-r",
        default="README.md",
        metavar="PATH",
        help="README.md to update (default: README.md; pass '' to skip)",
    )
    gen.add_argument(
        "--mode",
        choices=["spines", "covers"],
        default="spines",
        help="Render mode: spines (Phase 1, default) or covers (Phase 2, fetches cover art)",
    )
    gen.add_argument(
        "--no-cache",
        action="store_true",
        default=False,
        help="Skip the local cover cache and re-fetch all images",
    )

    args = parser.parse_args()

    if args.command in ("generate", "gen"):
        sys.exit(_cmd_generate(args))
    else:
        parser.print_help()
        sys.exit(0)
