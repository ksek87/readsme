# readsme

**Your GitHub profile deserves a bookshelf.**

Not a reading stats card. Not a data table with star ratings and progress bars. A shelf — the kind that actually says something about who you are.

`readsme` reads a plain YAML file of your books and renders a warm, shelf-style SVG that lives directly in your `README.md`. Books are grouped into *Currently Reading*, *Read*, and *Want to Read* sections. They're coloured by category — dark red for fiction, forest green for non-fiction, navy for sci-fi — using a warm library palette that feels like it belongs on a real shelf, not a dashboard.

<!-- readsme-start -->
![My bookshelf](shelf.svg)
<!-- readsme-end -->

---

## Install

```bash
pip install readsme
```

---

## Get started in three steps

**1. Describe your books** — copy the example and fill it in:

```bash
cp books.example.yaml books.yaml
```

```yaml
# books.yaml
width: 800

books:
  - title: "The Name of the Wind"
    author: "Patrick Rothfuss"
    category: Fantasy
    status: reading
    isbn: "9780756404079"

  - title: "Sapiens"
    author: "Yuval Noah Harari"
    category: History
    status: read

  - title: "Dune"
    author: "Frank Herbert"
    category: Science Fiction
    status: want-to-read
    isbn: "9780441013593"
```

**2. Add the embed markers** to your `README.md`:

```markdown
<!-- readsme-start -->
<!-- readsme-end -->
```

**3. Generate:**

```bash
readsme generate
```

That's it. `shelf.svg` is written and the markers in `README.md` are filled in. Commit both and your profile has a bookshelf.

---

## Keep it up to date automatically

Drop the included GitHub Action into your profile repository. It re-generates `shelf.svg` and commits it whenever you push a change to `books.yaml` — so adding a new book is just editing a YAML file.

```bash
# from this repo, copy to yours:
cp .github/workflows/readsme.yml /path/to/your-profile-repo/.github/workflows/
```

Or add it manually — the full file is `.github/workflows/readsme.yml` in this repository.

---

## books.yaml reference

```yaml
width: 800          # SVG width in pixels (default: 800)

# Override the default colour for any category (optional)
categories:
  Mystery:
    color: "#1A1A2E"
  Poetry:
    color: "#5C4A6E"

books:
  - title: "..."
    author: "..."
    category: "..."       # any string — unknown categories get a palette colour automatically
    status: reading        # reading | read | want-to-read
    isbn: "..."            # optional 13-digit ISBN — used for cover art in --mode covers
```

### Status values

| Value | Section on shelf |
|---|---|
| `reading` | Currently Reading |
| `read` | Read |
| `want-to-read` | Want to Read |

Sections with no books are hidden automatically.

---

## Colour palette

readsme ships with a warm library palette — deep red, forest green, navy, dark brown — mapped to common genres. Any category not in the defaults cycles through the same palette automatically, so you never need to pick colours unless you want to.

Built-in mappings include: Fiction, Fantasy, Science Fiction, Non-fiction, Biography, History, Mystery, Thriller, Romance, Technology, Programming, Philosophy, Poetry, Classics, Horror, Memoir, Psychology, and more.

---

## Phase 2: real cover art

Pass `--mode covers` to fetch cover thumbnails from Open Library (falling back to Google Books) and render a visual shelf with actual book cover images. Covers are cached in `.readsme-cache/` so subsequent runs are fast. Books without an ISBN, or where no cover is found, fall back to the spine tile automatically — the shelf never has gaps.

```bash
pip install readsme[covers]   # adds httpx
readsme generate --mode covers
```

Force a cache refresh:

```bash
readsme generate --mode covers --no-cache
```

---

## CLI reference

```
readsme generate [OPTIONS]

  -c, --config PATH    books.yaml path         (default: books.yaml)
  -o, --output PATH    output SVG path          (default: shelf.svg)
  -r, --readme PATH    README.md to update      (default: README.md)
      --mode MODE      spines | covers           (default: spines)
      --no-cache       bypass local cover cache
      --version
```

---

## Why not a stats card?

Stats cards show aggregate data — "reads 40 books a year", "4.1 average rating". A shelf shows *taste*. It's the difference between a résumé line item and a conversation starter. No one ever asked a stranger about their Goodreads wrapped. People do ask "oh, you're reading Bulgakov?"

readsme is deliberately minimal: no ratings, no progress bars, no charts. Just books, the way they look on a shelf — because that's the part that's actually interesting.

---

## Contributing

Open an issue or PR on [GitHub](https://github.com/ksek87/readsme). The project is small by design — keep it that way.

---

## License

MIT
