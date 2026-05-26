# readsme

> *Show what you read, not just what you build.*

A visual bookshelf for your GitHub profile README — books spine-out, coloured by category, grouped into *Currently Reading*, *Read*, and *Want to Read*. Embed it with one line of Markdown. No server setup needed.

<!-- readsme-start -->
![My bookshelf](shelf.svg)
<!-- readsme-end -->

---

## Hosted service (no install)

Add one line to your GitHub profile README:

```markdown
![My bookshelf](https://readsme.vercel.app/shelf/YOUR_USERNAME)
```

That's it. The shelf renders live from a `books.yaml` file in your profile repository (`username/username`). Every push refreshes it automatically — no CI, no tokens, no workflow needed.

---

## books.yaml

Create `books.yaml` in your profile repo (`username/username/books.yaml`):

```yaml
width: 800   # optional, controls max shelf width

books:
  - title: "Meditations"
    author: "Marcus Aurelius"
    category: Philosophy
    status: read
    isbn: "9780140441406"   # optional — used for cover art mode

  - title: "Designing Your Life"
    author: "Bill Burnett & Dave Evans"
    category: Self-help
    status: reading

  - title: "The Lean Startup"
    author: "Eric Ries"
    category: Business
    status: want-to-read

# Optional: override a category's spine colour
categories:
  Philosophy:
    color: "#3A1060"
```

| Status | Section |
|---|---|
| `reading` | Currently Reading — shown first, with a gold pulsing border |
| `read` | Read |
| `want-to-read` | Want to Read |

Sections with no books are hidden automatically.

---

## Self-hosted / CLI

If you'd rather commit the SVG to your repo and not depend on the hosted service:

```bash
pip install readsme
readsme generate --config books.yaml --output shelf.svg --readme README.md
```

Then add markers to your `README.md`:

```markdown
<!-- readsme-start -->
<!-- readsme-end -->
```

`readsme generate` fills in the block. Commit `shelf.svg` and `README.md`.

### Auto-update with GitHub Actions

Copy `.github/workflows/readsme.yml` from this repo into your profile repository. It regenerates `shelf.svg` and commits it whenever you push a change to `books.yaml`:

```bash
git add books.yaml && git commit -m "read: Meditations" && git push
# shelf updates itself
```

### Cover art mode

Fetch real cover thumbnails from Open Library (with Google Books fallback). Covers are embedded as base64 so they render correctly through GitHub's image proxy. Books without an ISBN fall back to the spine style — no gaps.

```bash
pip install "readsme[covers]"
readsme generate --mode covers
```

Covers are cached in `.readsme-cache/` after the first fetch. Use `--no-cache` to force a refresh.

---

## Colour palette

The default palette is warm and library-like: burgundy, forest green, navy, dark brown. Common genres (Fiction, Fantasy, Science Fiction, History, Philosophy, Technology, and [many more](readsme/colors.py)) have named defaults. Anything else cycles through the palette automatically.

Override any category colour in `books.yaml` under `categories:`.

---

## CLI reference

```
readsme generate [OPTIONS]

  -c, --config PATH   books.yaml path        (default: books.yaml)
  -o, --output PATH   output SVG             (default: shelf.svg)
  -r, --readme PATH   README.md to update    (default: README.md)
      --mode MODE     spines | covers         (default: spines)
      --no-cache      bypass local cover cache
      --version
```

---

## Why a shelf?

Stats cards tell you *how much* someone reads. A shelf tells you *what* they read — which is the interesting part. No ratings, no progress bars, no charts. Just the books, the way they look on a shelf.

---

MIT · [github.com/ksek87/readsme](https://github.com/ksek87/readsme)
