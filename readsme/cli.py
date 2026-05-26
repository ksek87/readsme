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
    except (ValueError, KeyError, Exception) as exc:
        print(f"Error reading config: {exc}", file=sys.stderr)
        return 1

    if not config.books:
        print("No books in config. Add some entries to books.yaml.", file=sys.stderr)
        return 1

    svg = render(config)

    output = Path(args.output)
    output.write_text(svg, encoding="utf-8")
    print(f"✓ Wrote {output}  ({len(config.books)} book{'s' if len(config.books) != 1 else ''})")

    if args.readme:
        readme = Path(args.readme)
        if update_readme(readme, output.name):
            print(f"✓ Updated {readme}")
        else:
            if readme.exists():
                print(
                    f"  {readme}: add <!-- readsme-start --> and <!-- readsme-end --> markers "
                    "to auto-embed the shelf."
                )

    return 0


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

    args = parser.parse_args()

    if args.command in ("generate", "gen"):
        sys.exit(_cmd_generate(args))
    else:
        parser.print_help()
        sys.exit(0)
