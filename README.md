# myskills

Personal skills collection. Currently includes `write-paper-notes`.

## write-paper-notes

Extract content from PDF academic papers and generate structured Markdown notes.

### Features

- Extracts text, images, and tables via `pymupdf4llm`
- Built-in OCR via Tesseract (for text-only AIs)
- AI reorganizes raw extraction into structured notes (`notes.md`)
- Preserves all images, restructures text into bullet points, lists, and tables
- Flexible element ordering (except fixed images)
- Lists only key references, skips peripheral citations

### Installation

**Via npm skills:**
```bash
npx skills add ian5030560/myskills --skill write-paper-notes
```

**Manual setup:**
```bash
pip install pymupdf4llm

# Install Tesseract system-wide:
#   Windows: winget install -e --id UB-Mannheim.TesseractOCR
#   macOS: brew install tesseract
#   Ubuntu/Debian: sudo apt-get install tesseract-ocr
```

**Verify Tesseract:**
```bash
tesseract --version
```
