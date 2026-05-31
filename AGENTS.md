# AGENTS.md

## Project
Two skills in one repo:
- `pdf/scripts/` — 5 CLI entrypoints, each accepting `--pdf` and `--output-dir` (all powered by PyMuPDF/fitz)
- `write-paper-notes/scripts/extract.py` — paper notes pipeline, accepts `--pdf`, `--output-dir`, and optional `--no-ocr`
- `makefile` wraps `npx skills add/remove` for local install/uninstall

## Python Import Path
Tests and linting add `pdf/scripts` to `sys.path` via `conftest.py` and `.pylintrc` respectively.

## Commands
```
# Run all PDF tests
pytest tests/pdf/

# Run all write-paper-notes tests
pytest tests/write_paper_notes/

# Lint (uses .pylintrc which also adds write-paper-notes/scripts to path)
pylint pdf/scripts/*.py --rcfile=.pylintrc

# Dependencies
pip install PyMuPDF pymupdf4llm

# OCR (Tesseract):
#   Windows: winget install -e --id UB-Mannheim.TesseractOCR
#   macOS: brew install tesseract
#   Ubuntu/Debian: sudo apt-get install tesseract-ocr
```

## Testing Quirks
- All test fixtures are generated at runtime (no static fixture files). See `tests/pdf/conftest.py` for `_create_simple_pdf`, `_create_multi_page_pdf`, etc.
- Tests invoke scripts via `subprocess.run([sys.executable, script, ...])`, not via Python import.

## Workflow: write-paper-notes
Follow the 4-phase pipeline in `write-paper-notes/SKILL.md`:
1. **Extraction** — `python scripts/extract.py --pdf <pdf>` (OCR by default; `--no-ocr` for image-input AIs)
2. **Content Analysis** — AI examines images/OCR text; user must confirm before proceeding
3. **Organization** — loads `references/style-guide.md` + `assets/report-template.md`, generates `notes.md`
4. **Quality Review** — loads `references/quality-checklist.md`, self-checks and fixes before delivery

`--output-dir` is optional (defaults to current dir, creates `<pdf_stem>/` subfolder with `images/` and `notes.md`).

## Environment
- **Windows UTF-8**: `$env:PYTHONIOENCODING="utf-8"` before running tools.
- Virtual env at repo root (`pyvenv.cfg`, `Include/`, `Lib/`, `Scripts/` — all gitignored).
