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

Extract content from PDF/DOCX academic papers and turn it into study notes with a fixed skeleton.

### Features

- **CLI extractor** — Python scripts powered by PyMuPDF (PDF) and python-docx (DOCX)
- **Figure extraction** — Images, tables, and vector graphics from PDFs; inline images from DOCX
- **Fixed skeleton** — Every paper gets the same sections: Introduction (background, motivation, research questions, contributions), Related Work, Method, Results, Conclusion (findings, limitations, future work); method and results follow the paper's own subsections
- **No fabrication** — Only content found in the paper; empty sections are omitted
- **Your language** — Notes are written in the language you use with the AI
- **Single style guide** — One rule list used for both writing and self-checking

### Pipeline (3 Steps)

1. **Extract** — `scripts/extract.py --input <file>` outputs Markdown text + `images/`
2. **Write** — AI fills the skeleton following the style guide and saves `notes.md`
3. **Self-check** — AI checks `notes.md` against the style guide and fixes issues until all rules pass

### Installation

```bash
npx skills add ian5030560/myskills --skill write-paper-notes
```


