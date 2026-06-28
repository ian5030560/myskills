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

Extract content from PDF/DOCX academic papers and generate structured Markdown notes with type-aware templates and automated quality review.

### Features

- **CLI extractor** — Python scripts powered by PyMuPDF (PDF) and python-docx (DOCX)
- **Type-aware templates** — CS/AI/ML and Survey/Review templates with section-specific guidance
- **Figure extraction** — Images, tables, and vector graphics from PDFs; inline images from DOCX
- **On-demand OCR** — Tesseract integration for text-only AIs; skip with `--no-ocr` for image-input AIs
- **Diagnostic diagrams** — Mermaid timeline, mindmap, state diagram generated per style guide
- **Modular style guide** — Common rules + type-specific rules for structure, formatting, and diagrams
- **Quality gate** — Common + type-specific checklist verification before delivery

### Pipeline (4 Phases)

1. **Extraction** — `scripts/extract.py --input <file>` outputs Markdown text + `images/`
2. **Content Analysis** — AI identifies paper structure and detects paper type
3. **Organization** — AI loads templates + style guides to produce `notes.md`
4. **Quality Review** — AI validates against checklists, fixes issues iteratively

### Installation

```bash
npx skills add ian5030560/myskills --skill write-paper-notes
```


