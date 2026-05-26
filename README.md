# readsme

Generate a visual bookshelf SVG for your GitHub profile README. Books are defined in a YAML file; the shelf renders as SVG book spines coloured by category, grouped into *Currently Reading*, *Read*, and *Want to Read* sections.

<!-- readsme-start -->
![My bookshelf](shelf.svg)
<!-- readsme-end -->

---

## Quick start

```bash
pip install readsme
cp books.example.yaml books.yaml
# edit books.yaml with your books
readsme generate
```

This writes `shelf.svg` and updates the `<!-- readsme-start/end -->` block in `README.md`.

---

## books.yaml

```yaml
width: 800   # SVG width in pixels

# Optional: override the default warm-palette colour for any category
# categories:
#   Fantasy:
#     color: "#4A2040"

books:
  - title: "The Name of the Wind"
    author: "Patrick Rothfuss"
    category: Fantasy
    status: reading          # reading | read | want-to-read
    isbn: "9780756404079"    # optional — used for cover art in Phase 2
```

---

## GitHub Action

Push a `books.yaml` to your repository; the Action will regenerate `shelf.svg` and commit it automatically.

```yaml
# .github/workflows/readsme.yml  — see the file already included in this repo
```

Add the markers to your profile `README.md`:

```markdown
<!-- readsme-start -->
<!-- readsme-end -->
```

The Action will fill in the `![My bookshelf](shelf.svg)` reference on every push that changes `books.yaml`.

---

## CLI reference

```
readsme generate [OPTIONS]

Options:
  -c, --config PATH   books.yaml path       (default: books.yaml)
  -o, --output PATH   output SVG path       (default: shelf.svg)
  -r, --readme PATH   README.md to update   (default: README.md)
      --version
```

---

## Category colours

Built-in defaults cover most common genres (Fiction, Fantasy, Science Fiction, Non-fiction, History, Mystery, Programming, …). Override any of them in `books.yaml`:

```yaml
categories:
  Mystery:
    color: "#1A1A2E"
```

Unknown categories are assigned colours from the warm library palette automatically.

---

## Roadmap

- **Phase 1** ✅ — SVG spine view (colour-coded by category, grouped by status)
- **Phase 2** — Cover-art view: fetches JPEG covers from Open Library (fallback: Google Books), embeds as base64 in a self-contained SVG

---

## License

MIT
