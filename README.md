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

7-step pipeline that analyzes PDF academic papers and generates structured Markdown notes. Requires an installed PDF extraction skill (any skill capable of text, image, and table extraction).

### Features

- **3 extraction roles** — Text, Images, Tables; auto-discovers available tools per session
- **AI type auto-detection** — Image-input AI skips OCR; Text-only AI uses a 3-tier OCR fallback
- **Plain text extraction** — AI infers heading structure from content cues (numbering, spacing, paper structure)
- **Table alignment** — Tables inserted at their contextual position, not grouped at end
- **Modular style guide** — 17 rules in 5 modules (Structural, Synthesis, Table Integration, Formatting, Visuals)
- **Quality gate** — Automated checklist verification before final delivery

### Pipeline (7 Steps)

1. Capability Discovery → 2. Content Extraction → 3. Extraction Gate → 4. Content Analysis → 5. Structural Organization → 6. Quality Review → 7. Final Delivery

### Installation

```bash
npx skills add ian5030560/myskills --skill write-paper-notes
```


