# myskills

Personal Agent Skills collection.

## pdf

Complete PDF toolkit with 5 Python scripts powered by PyMuPDF:

| Tool | Purpose |
|------|---------|
| `pdf_text_extractor.py` | Text extraction (plain text or Markdown) |
| `pdf_images_extractor.py` | Image extraction with optional Tesseract OCR |
| `pdf_table_extractor.py` | Table detection and Markdown conversion |
| `pdf_manager.py` | Merge, split, rotate pages, manage metadata |
| `pdf_security.py` | AES-256 encrypt/decrypt PDFs |

### Installation

```bash
npx skills add ian5030560/myskills --skill pdf
```

## write-paper-notes

Turn PDF academic papers into study notes with a fixed skeleton.

### Features

- **PDF only** — DOCX and other formats must be saved as PDF first
- **Text extraction** — Plain text in reading order (two-column aware, running headers/footers removed) via PyMuPDF; no OCR
- **Page images** — Every page rendered with a faint coordinate grid; the AI reads figures, tables and scanned pages from them
- **Figure crops** — The AI draws a generous box; the script trims captions, body text and headers off the edges and re-renders the figure at 200 dpi
- **Fixed skeleton** — Every paper gets the same sections: Introduction (background, motivation, research questions, contributions), Related Work, Method, Results, Conclusion (findings, limitations, future work); method and results follow the paper's own subsections
- **No fabrication** — Only content found in the paper; empty sections are omitted
- **Your language** — Notes are written in the language you use with the AI
- **Single style guide** — One rule list used for both writing and self-checking

### Pipeline (4 Steps)

1. **Extract** — `scripts/extract_text.py` writes `text.md`; `scripts/render_pages.py` writes gridded page images to `pages/`
2. **Write** — AI reads the text and page images, crops figures with `scripts/crop_figure.py`, rebuilds tables as Markdown, and saves `notes.md`
3. **Self-check** — AI checks `notes.md` against the style guide and fixes issues until all rules pass
4. **Clean up** — `text.md` and `pages/` are deleted, leaving `notes.md` and `images/`

### Installation

```bash
npx skills add ian5030560/myskills --skill write-paper-notes
```


