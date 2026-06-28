# AGENTS.md

## Project
Two skills in one repo:
- `pdf/scripts/` — 5 CLI entrypoints (`pdf_text_extractor.py`, `pdf_images_extractor.py`, `pdf_table_extractor.py`, `pdf_manager.py`, `pdf_security.py`), all accepting `--pdf` + `--output-dir`, powered by PyMuPDF/fitz
- `write-paper-notes/scripts/` — 4 files: `base.py` (ABC + shared utilities), `extract_pdf.py` (PdfExtractor), `extract_docx.py` (DocxExtractor), `extract.py` (CLI entrypoint)
- `makefile` wraps `npx skills add/remove` — requires `skill=<name>` param

## Python Import Path
Each test suite's `conftest.py` adds its own `scripts/` dir to `sys.path`. `.pylintrc` adds `write-paper-notes/scripts` via `init-hook`.

## Dependencies
```
pip install PyMuPDF python-docx pytesseract
```
Tesseract OCR system install: see platform-specific commands in `pdf/SKILL.md` or `write-paper-notes/SKILL.md`.

## Commands
```
pytest tests/pdf/
pytest tests/write_paper_notes/
pylint pdf/scripts/*.py --rcfile=.pylintrc
pylint write-paper-notes/scripts/*.py --rcfile=.pylintrc
```

## Testing quirks
- All test fixtures generated at runtime via `conftest.py` helpers (`_create_simple_pdf`, `_create_multi_page_pdf`, `_create_simple_docx`, etc.)
- PDF tests invoke scripts via `subprocess.run([sys.executable, script, ...])` — never by Python import
- Write-paper-notes tests mix subprocess (CLI behavior) + direct imports (unit tests for `PdfExtractor`, `DocxExtractor`, `DocumentExtractor`, `ocr_image_bytes`)
- OCR tests (`test_images_extractor.py`) are `@pytest.mark.skipif(not tesseract_available())` — most tests work without Tesseract

## Workflow: write-paper-notes
Entrypoint: `python scripts/extract.py --input <path> [--output-dir <dir>] [--no-ocr]`
- Supports `.pdf` (PyMuPDF) and `.docx` (python-docx) — auto-detected by extension
- `--no-ocr` disables Tesseract OCR (pass when AI has image input capability)
- `--output-dir` defaults to current dir; creates `<stem>/` subfolder with `images/` and extraction text on stdout
- Full 4-phase pipeline (Extraction → Content Analysis → Organization → Quality Review) documented in `write-paper-notes/SKILL.md`

## Environment
- **Windows UTF-8**: `$env:PYTHONIOENCODING="utf-8"` before running tools
- Virtual env at repo root (`pyvenv.cfg`, `Include/`, `Lib/`, `Scripts/` — all gitignored)
