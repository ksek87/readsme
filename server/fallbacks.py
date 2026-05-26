"""Styled SVG responses for not-found and error states."""
from __future__ import annotations

_W, _H = 420, 140
_BG = "#F4E8C1"
_DARK_BG = "#1C1810"


def _base(body: str) -> str:
    return f"""\
<svg xmlns="http://www.w3.org/2000/svg" width="{_W}" height="{_H}" role="img">
  <defs>
    <style>
      .bg           {{ fill: {_BG}; }}
      .heading      {{ fill: #5C3D2D; font-family: Georgia,serif; font-size:15px; font-style:italic; }}
      .sub          {{ fill: #8B6A4A; font-family: Arial,sans-serif; font-size:11px; }}
      .mono         {{ fill: #3D2A1A; font-family: monospace; font-size:10px; }}
      .rule         {{ stroke: #C4A265; stroke-width: 0.8; opacity: 0.6; }}
      @media (prefers-color-scheme: dark) {{
        .bg      {{ fill: {_DARK_BG}; }}
        .heading {{ fill: #C8A07A; }}
        .sub     {{ fill: #8A6A4A; }}
        .mono    {{ fill: #C8A870; }}
        .rule    {{ stroke: #6A4A28; }}
      }}
    </style>
  </defs>
  <rect class="bg" width="{_W}" height="{_H}" rx="8"/>
  <line class="rule" x1="20" y1="24" x2="{_W-20}" y2="24"/>
  <line class="rule" x1="20" y1="{_H-18}" x2="{_W-20}" y2="{_H-18}"/>
  {body}
</svg>"""


def not_found_svg(username: str) -> str:
    body = f"""\
  <text class="heading" x="{_W//2}" y="50" text-anchor="middle">no bookshelf found</text>
  <text class="sub" x="{_W//2}" y="72" text-anchor="middle">
    Create a books.yaml in your profile repository:
  </text>
  <text class="mono" x="{_W//2}" y="90" text-anchor="middle">{username}/{username}/books.yaml</text>
  <text class="sub" x="{_W//2}" y="112" text-anchor="middle">
    See github.com/ksek87/readsme for the format.
  </text>"""
    return _base(body)


def empty_shelf_svg(username: str) -> str:
    body = f"""\
  <text class="heading" x="{_W//2}" y="50" text-anchor="middle">shelf is empty</text>
  <text class="sub" x="{_W//2}" y="72" text-anchor="middle">
    {username}/books.yaml exists but contains no books yet.
  </text>
  <text class="sub" x="{_W//2}" y="95" text-anchor="middle">
    Add some entries and push — the shelf updates automatically.
  </text>"""
    return _base(body)


def error_svg(message: str) -> str:
    safe = message[:80].replace("<", "&lt;").replace(">", "&gt;")
    body = f"""\
  <text class="heading" x="{_W//2}" y="50" text-anchor="middle">something went wrong</text>
  <text class="sub" x="{_W//2}" y="75" text-anchor="middle">{safe}</text>
  <text class="sub" x="{_W//2}" y="95" text-anchor="middle">
    Check your books.yaml syntax at github.com/ksek87/readsme.
  </text>"""
    return _base(body)
