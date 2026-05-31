---
name: write-paper-notes
version: 1.1.0
description: "Extract content from PDF papers and generate structured Markdown notes. Default: OCR enabled for text-only AIs. Use --no-ocr for image-input AIs."

metadata:
  starchild:
    emoji: "📄"
    skillKey: write-paper-notes
    requires:
      env: []
      bins: [python]
    install:
      - kind: system
        package: tesseract-ocr

user-invocable: true
---

Extract text, images, and tables from PDF academic papers and generate structured Markdown notes. Follow the pipeline below — each phase must complete before the next begins.


## Setup

### Install Python Dependencies

```bash
pip install pymupdf4llm
```

### Install Tesseract OCR (Required for text-only AIs)

| OS | Install Command |
|----|----------------|
| **Windows** | `winget install -e --id UB-Mannheim.TesseractOCR` |
| **macOS** | `brew install tesseract` |
| **Ubuntu/Debian** | `sudo apt-get install tesseract-ocr` |
| **Fedora** | `sudo dnf install tesseract` |
| **Arch Linux** | `sudo pacman -S tesseract` |

Verify: `tesseract --version`

### Windows UTF-8 Encoding (Required)

Windows console default encoding (cp950/Big5) cannot handle UTF-8 characters in PDFs. Set this before running:

**PowerShell:**
```powershell
$env:PYTHONIOENCODING="utf-8"
```

**CMD:**
```cmd
set PYTHONIOENCODING=utf-8
```

## Pipeline

### Phase 1 — Extraction
Run the extraction script based on your AI type:

| `--no-ocr` | Tesseract Installed | AI Type | Action |
|------------|-------------------|---------|--------|
| ❌ No | ✅ Yes | Text-only AI | `python scripts/extract.py --pdf <pdf> [--output-dir <dir>]` |
| ❌ No | ❌ No | Text-only AI | **Error**: install Tesseract first |
| ✅ Yes | Any | Image-input AI | `python scripts/extract.py --pdf <pdf> --no-ocr --output-dir <dir>` |

Parameters:
- `--pdf` (required): PDF file path
- `--output-dir` (optional): Parent directory (default: current dir; creates `<pdf_stem>` subfolder)
- `--no-ocr` (optional): Disable OCR — only when AI supports image input

Outputs:
- Extracted text in stdout
- `images/` — extracted figures (original quality)

### Phase 2 — Content Analysis
- **Image-input AI**: Examine each image in `images/`, describe what it shows.
- **Text-only AI**: Read the OCR text to understand image content.

Identify the paper's structure: sections, figures, tables, and their relationships.

### Phase 3 — Organization
1. Load `references/style-guide.md` and `assets/report-template.md`.
2. Reorganize extracted content into structured Markdown and save as `notes.md`. Generate Mermaid diagrams where the style guide's decision matrix indicates.

### Phase 4 — Quality Review
1. Load `references/quality-checklist.md`.
2. Check `notes.md` against every item on the checklist.
3. For each failure, explain the issue and fix it.
4. Re-check until all items pass.

Deliver the final `notes.md` to the user.


