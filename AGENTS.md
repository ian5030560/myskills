# AGENTS.md

## Project
Collection of skills:
- `pdf`: Core PDF extraction tools in `pdf/scripts/`.
- `write-paper-notes`: Orchestration pipeline for academic paper notes (`write-paper-notes/SKILL.md`).

## Python Import Path
Tests and linting require `pdf/scripts` in `sys.path` (configured in `tests/pdf/conftest.py`).

## Commands
```bash
# Run PDF tests
pytest tests/pdf/

# Install dependencies
pip install pymupdf4llm

# Install Tesseract (OCR):
#   Windows: winget install -e --id UB-Mannheim.TesseractOCR
#   macOS: brew install tesseract
#   Ubuntu/Debian: sudo apt-get install tesseract-ocr

# Lint PDF scripts
pylint pdf/scripts/*.py --rcfile=.pylintrc
```

## OCR & Environment
- **OCR**: Requires Tesseract. If not installed, `pymupdf4llm` will raise an error.
- **Windows UTF-8**: Set `PYTHONIOENCODING=utf-8` before running Python PDF tools to avoid encoding errors.

## Workflow: write-paper-notes
This skill is a pipeline. Follow the 7-step process defined in `write-paper-notes/SKILL.md` strictly.
