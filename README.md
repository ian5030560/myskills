# myskills

Personal Agent Skills collection. Each skill installs on its own:

```bash
npx skills add ian5030560/myskills --skill <name>
```

| Skill | What it does |
|-------|--------------|
| [`pdf`](#pdf) | Extract, manipulate and secure PDFs |
| [`write-paper-notes`](#write-paper-notes) | Turn a PDF paper into structured study notes |

## pdf

Complete PDF toolkit with 5 Python scripts powered by PyMuPDF:

| Tool | Purpose |
|------|---------|
| `pdf_text_extractor.py` | Plain text extraction (no OCR) |
| `pdf_images_extractor.py` | Image extraction with optional Tesseract OCR |
| `pdf_table_extractor.py` | Table detection and Markdown conversion |
| `pdf_manager.py` | Merge, split, rotate pages, manage metadata |
| `pdf_security.py` | AES-256 encrypt/decrypt PDFs |

### Requirements

- `pip install PyMuPDF`
- Tesseract, only for OCR in `pdf_images_extractor.py` (per-OS install commands are in [`pdf/SKILL.md`](pdf/SKILL.md))

### Installation

```bash
npx skills add ian5030560/myskills --skill pdf
```

## write-paper-notes

Turn PDF academic papers into study notes with a fixed skeleton. Ask your AI to write notes for a paper and give it the PDF path.

### Features

- **PDF only** — DOCX and other formats must be saved as PDF first
- **Text extraction** — Plain text in reading order via PyMuPDF: two-column aware, running headers/footers and sidebar text removed, split paragraphs rejoined; no OCR
- **Page images** — Every page rendered with a faint coordinate grid; the AI reads figures, tables and scanned pages from them
- **Figure crops** — The AI draws a generous box; the script trims captions, body text and headers off the edges and re-renders the figure at 200 dpi
- **Tables as Markdown** — Tables are rebuilt from the page images, not cropped as pictures
- **Fixed skeleton** — Every paper gets the same sections: Introduction (background, motivation, research questions, contributions), Related Work, Method, Results, Conclusion (findings, limitations, future work); method and results follow the paper's own subsections
- **No fabrication** — Only content found in the paper; empty sections are omitted
- **Your language** — Notes are written in the language you use with the AI
- **Single style guide** — One rule list used for both writing and self-checking

### Pipeline (4 Steps)

1. **Extract** — `scripts/extract_text.py` writes `text.md`; `scripts/render_pages.py` writes gridded page images to `pages/`
2. **Write** — AI reads the text and page images, crops figures with `scripts/crop_figure.py`, rebuilds tables as Markdown, and saves `notes.md`
3. **Self-check** — AI checks `notes.md` against the style guide and fixes issues until all rules pass
4. **Clean up** — `text.md` and `pages/` are deleted

Output, in `<output-dir>/<pdf-stem>/`:

```
notes.md
images/      # cropped figures linked from notes.md
```

### Requirements

- `pip install PyMuPDF`
- An AI that can read images (it reads page images and checks its own crops)

### Installation

```bash
npx skills add ian5030560/myskills --skill write-paper-notes
```

## Development

```bash
pip install PyMuPDF Pillow pytest
pytest tests/pdf/
pytest tests/write_paper_notes/
```

All test PDFs are generated at runtime; no fixture files are stored in the repo. Shortcuts for the skills CLI:

```bash
make install skill=<name>
make uninstall skill=<name>
```
