# AGENTS.md

## Project

OpenCode skill: extracts PDF academic papers to Markdown via `write-paper-notes/scripts/extract.py`.

## Python Import Path

Tests and pylint require `write-paper-notes/scripts` in `sys.path`. This is configured in:
- `tests/conftest.py` (sets path for pytest)
- `.pylintrc` (init-hook)

## Commands

```bash
# Run all tests
pytest tests/

# Run single test file
pytest tests/test_extract.py

# Run single test class or method
pytest tests/test_extract.py::TestExtractPdf
pytest tests/test_extract.py::TestExtractPdf::test_returns_string

# Install dependencies
pip install pymupdf4llm

# Install Tesseract system-wide (required for OCR):
#   Windows: winget install -e --id UB-Mannheim.TesseractOCR
#   macOS: brew install tesseract
#   Ubuntu/Debian: sudo apt-get install tesseract-ocr

# Run extraction
python write-paper-notes/scripts/extract.py --pdf <path> [--no-ocr] [--output-dir <dir>]
```

## OCR Behavior

- **Default**: OCR enabled via pymupdf4llm's built-in Tesseract plugin
- **`--no-ocr`**: disables OCR; use when AI supports image input (GPT-4V, Claude 3.5)
- **Tesseract not installed + no `--no-ocr`**: pymupdf4llm raises error
- **Dependencies**: 
  - System: Install Tesseract:
    - **Windows**: `winget install -e --id UB-Mannheim.TesseractOCR`
    - **macOS**: `brew install tesseract`
    - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`

## Quirks

- **Windows UTF-8**: Set `PYTHONIOENCODING=utf-8` before running `extract.py` (Windows console uses cp950)
- **Output dir default**: uses `<pdf_stem>` in cwd when `--output-dir` omitted
- **Images**: extracted to `<output_dir>/images/` automatically via `write_images=True`
- **Dependency**: formerly used `pypdf`, migrated to `pymupdf4llm` (see git `9cb6a1a`)

## Lint

```bash
pylint write-paper-notes/scripts/extract.py --rcfile=.pylintrc
```
