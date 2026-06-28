---
name: write-paper-notes
version: 1.2.0
description: "Turn academic papers into organized Markdown notes. Supports PDF and DOCX."

metadata:
  starchild:
    emoji: "📄"
    skillKey: write-paper-notes
    requires:
      env: []
      bins: [python]
user-invocable: true
---

Extract text, images, and tables from PDF papers or DOCX documents and generate structured Markdown notes. Follow the pipeline below — each phase must complete before the next begins.


## Setup

### 1. Install Packages for Your Document

Install based on your input file format:

- **.pdf**
  ```bash
  pip install PyMuPDF
  python -c "import fitz; print('PyMuPDF OK')"
  ```
- **.docx**
  ```bash
  pip install python-docx
  python -c "import docx; print('python-docx OK')"
  ```

### 2. Install OCR (Only when your AI does NOT support image input)

- **Python packages**
  ```bash
  pip install pytesseract Pillow
  python -c "import pytesseract; from PIL import Image; print('OCR packages OK')"
  ```
- **Tesseract system engine**
  - Windows: `winget install -e --id UB-Mannheim.TesseractOCR`
  - macOS: `brew install tesseract`
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
  - Fedora: `sudo dnf install tesseract`
  - Arch Linux: `sudo pacman -S tesseract`

  ```bash
  tesseract --version
  ```

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

**Supported formats:**
- `.pdf` — text, tables, images, vector graphics (via PyMuPDF)
- `.docx` — paragraphs, headings, tables, lists, inline images (via python-docx)

Run the extraction script:

1. **If your AI supports image input** — add `--no-ocr`:
   ```
   python scripts/extract.py --input <file> [--output-dir <dir>] --no-ocr
   ```
2. **Otherwise (text-only AI)** — ensure OCR is installed and omit `--no-ocr`:
   ```
   python scripts/extract.py --input <file> [--output-dir <dir>]
   ```

Parameters:
- `--input` (required): File path (.pdf or .docx)
- `--output-dir` (optional): Parent directory (default: current dir)
- `--no-ocr` (optional): Disable OCR — only when AI supports image input

Outputs:
- Extracted text in stdout
- `images/` — extracted figures (original quality, with OCR text if enabled)

Output directory structure (Phase 3 saves `notes.md` here):
  <output-dir>/<input-stem>/
  ├── images/
  └── (notes.md will be created here in Phase 3)

### Phase 2 — Content Analysis
- **Image-input AI**: Examine each image in `images/`, describe what it shows.
- **Text-only AI**: Read the OCR text to understand image content.

Identify the paper's structure: sections, figures, tables, and their relationships.

**Detect paper type:** Output the detected paper type as the first line of your analysis:
- `PaperType: cs-ai-ml` — for Computer Science / AI / Machine Learning papers
- `PaperType: survey-review` — for Survey / Review papers
- Omit this line if the type cannot be determined (falls back to generic template)

### Phase 3 — Organization
1. Look for `PaperType: <type>` at the start of Phase 2 output.
2. Load `references/style-guide/common.md` (always).
3. If a recognized PaperType was detected:
   - Load `references/style-guide/<type>.md`
   - Load `templates/<type>.md`
4. If no PaperType was detected:
   - Load `assets/report-template.md` (generic fallback)
5. Reorganize extracted content into structured Markdown and save it as `notes.md` inside the output directory (i.e., `<output-dir>/<input-stem>/notes.md` — the same directory that contains the `images/` folder). Generate Mermaid diagrams where the style guide indicates.

### Phase 4 — Quality Review
1. Load `references/quality-checklist/common.md` (always).
2. If a recognized PaperType was detected, also load `references/quality-checklist/<type>.md`.
3. Check `notes.md` against every item on all loaded checklists.
4. For each failure, explain the issue and fix it.
5. Re-check until all items pass.

Deliver the final `notes.md` to the user.


