"""Vercel serverless entry point — readsme shelf API."""
from __future__ import annotations

import re
import sys
import os

# Ensure repo root is on sys.path when running inside Vercel's sandboxed env.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Query, Response
from fastapi.responses import HTMLResponse

from server.github import fetch_books_yaml
from server.fallbacks import not_found_svg, empty_shelf_svg, error_svg
from readsme.config import load_config_from_string
from readsme.renderer import render

app = FastAPI(title="readsme", docs_url=None, redoc_url=None)

_SVG = "image/svg+xml; charset=utf-8"
_CACHE_HIT = "public, max-age=300, stale-while-revalidate=60"
_CACHE_MISS = "public, max-age=60"

# GitHub usernames: 1–39 alphanumeric / hyphen chars, no leading/trailing hyphen.
_VALID_USERNAME = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$")


def _svg_response(svg: str, cache: str = _CACHE_HIT) -> Response:
    return Response(
        content=svg,
        media_type=_SVG,
        headers={"Cache-Control": cache, "X-Content-Type-Options": "nosniff"},
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/shelf/{username}")
async def shelf(
    username: str,
    width: int = Query(default=None, ge=200, le=2000),
) -> Response:
    if not _VALID_USERNAME.match(username):
        return _svg_response(error_svg("Invalid GitHub username."), _CACHE_MISS)

    yaml_text = await fetch_books_yaml(username)
    if yaml_text is None:
        return _svg_response(not_found_svg(username), _CACHE_MISS)

    try:
        config = load_config_from_string(yaml_text, width_override=width)
    except Exception as exc:
        return _svg_response(error_svg(str(exc)), _CACHE_MISS)

    if not config.books:
        return _svg_response(empty_shelf_svg(username), _CACHE_MISS)

    return _svg_response(render(config))


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    return _LANDING_HTML


_LANDING_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>readsme — your bookshelf in your README</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #F4E8C1; --ink: #3D2A1A; --accent: #8B1F1F;
      --card: #EDE0B0; --border: #C4A265; --mono: #5C3D2D;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #1C1810; --ink: #E8D8B0; --accent: #C8906A;
        --card: #2A2018; --border: #6A4A28; --mono: #B8985A;
      }
    }
    body {
      background: var(--bg); color: var(--ink);
      font-family: Georgia, "Times New Roman", serif;
      line-height: 1.65; padding: 0 1rem;
    }
    header {
      max-width: 680px; margin: 3rem auto 2rem;
      border-bottom: 1px solid var(--border); padding-bottom: 1.5rem;
    }
    header h1 { font-size: 2rem; letter-spacing: 0.04em; color: var(--accent); }
    header p  { margin-top: 0.5rem; font-style: italic; opacity: 0.8; }
    main  { max-width: 680px; margin: 0 auto 4rem; }
    h2    { font-size: 1.1rem; letter-spacing: 0.08em; text-transform: uppercase;
            margin: 2rem 0 0.75rem; color: var(--accent); }
    p     { margin-bottom: 1rem; }
    code  {
      font-family: "SFMono-Regular", Consolas, monospace;
      background: var(--card); border: 1px solid var(--border);
      border-radius: 4px; padding: 0.15em 0.4em;
      font-size: 0.88em; color: var(--mono);
    }
    pre   {
      background: var(--card); border: 1px solid var(--border);
      border-radius: 6px; padding: 1rem 1.25rem; overflow-x: auto;
      font-family: "SFMono-Regular", Consolas, monospace;
      font-size: 0.85rem; line-height: 1.55; margin-bottom: 1rem;
      color: var(--mono);
    }
    .shelf-preview { text-align: center; margin: 2rem 0; }
    .shelf-preview img { max-width: 100%; border-radius: 8px; }
    footer {
      max-width: 680px; margin: 0 auto 2rem;
      border-top: 1px solid var(--border); padding-top: 1rem;
      font-size: 0.85rem; opacity: 0.65; font-style: italic;
    }
    a { color: var(--accent); }
  </style>
</head>
<body>
<header>
  <h1>readsme</h1>
  <p>A living bookshelf for your GitHub profile README — no commits required.</p>
</header>
<main>

  <h2>Embed your shelf</h2>
  <p>Add one line to your README:</p>
  <pre>![My bookshelf](https://readsme.vercel.app/shelf/YOUR_USERNAME)</pre>
  <p>The shelf renders live from a <code>books.yaml</code> file in your profile repository
     (<code>username/username</code>). Every push updates the image automatically.</p>

  <h2>books.yaml format</h2>
  <pre>width: 800   # optional, controls max shelf width

books:
  - title: "The Lean Startup"
    author: "Eric Ries"
    category: Business
    status: read        # read | reading | want-to-read
    isbn: "9780307887894"   # optional — used for cover art

  - title: "Designing Your Life"
    author: "Bill Burnett &amp; Dave Evans"
    category: Self-help
    status: reading

categories:             # optional colour overrides
  Business:
    color: "#8B2515"</pre>

  <h2>Status values</h2>
  <p>
    <code>reading</code> — shown first, with a gold pulsing border<br/>
    <code>read</code> — your finished shelf<br/>
    <code>want-to-read</code> — your to-read pile
  </p>

  <h2>Width parameter</h2>
  <p>Override the shelf width via query string:</p>
  <pre>![shelf](https://readsme.vercel.app/shelf/username?width=600)</pre>

  <h2>Self-hosted / CLI</h2>
  <p>Generate the SVG locally and commit it to your repo:</p>
  <pre>pip install readsme
readsme generate --config books.yaml --output shelf.svg --readme README.md</pre>
  <p>See <a href="https://github.com/ksek87/readsme">github.com/ksek87/readsme</a> for full docs and the GitHub Actions workflow.</p>

</main>
<footer>
  Open source &mdash; <a href="https://github.com/ksek87/readsme">ksek87/readsme</a>
</footer>
</body>
</html>
"""
