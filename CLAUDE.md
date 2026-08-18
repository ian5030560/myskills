# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

"myskills" is a personal collection of Agent Skills, distributed via `npx skills add ian5030560/myskills --skill <name>`. Two independent skills live here:
- `pdf/` — five standalone PDF CLI tools (PyMuPDF/fitz + Tesseract OCR)
- `write-paper-notes/` — PDF/DOCX → structured Markdown paper-notes pipeline

The repo root also contains an activated Python venv (`Include/`, `Lib/`, `Scripts/`, `pyvenv.cfg`) and a vendored `.agents/skills/skill-creator/` — both gitignored, not part of the project source.

## Commands

Install dependencies:
```
pip install PyMuPDF python-docx pytesseract
```
`pdf/` also requires the Tesseract system binary for OCR (per-OS install commands are in `pdf/SKILL.md`).

Run tests:
```
pytest tests/pdf/
pytest tests/write_paper_notes/
```
Run a single test with a pytest node id, e.g.:
```
pytest tests/pdf/test_manager.py::TestMerge::test_merge_two_files -q
```

Lint:
```
pylint pdf/scripts/*.py --rcfile=.pylintrc
pylint write-paper-notes/scripts/*.py --rcfile=.pylintrc
```

Install/uninstall a skill via the skills CLI:
```
make install skill=<name>
make uninstall skill=<name>
```

**Windows UTF-8:** PDFs/DOCX often contain non-ASCII text, and the Windows console default (cp950/Big5) can't handle it. Set `PYTHONIOENCODING` in the *same* command as the `python` invocation — env vars don't persist across separate shell/tool calls:
```powershell
$env:PYTHONIOENCODING="utf-8"; python <script> ...
```

## Architecture

### `pdf/` skill
Five independent CLI entrypoints in `pdf/scripts/`, each self-contained (no shared base class), all taking `--pdf` + `--output-dir` and calling PyMuPDF (`fitz`) directly:
- `pdf_text_extractor.py` — plain text only, no OCR
- `pdf_images_extractor.py` — image extraction + optional Tesseract OCR via `fitz.Pixmap.pdfocr_tobytes()`; `--no-ocr` to skip
- `pdf_table_extractor.py` — `page.find_tables()` → Markdown tables
- `pdf_manager.py` — subcommands `merge` / `split` / `rotate` / `metadata` (`insert_pdf`, `set_rotation`)
- `pdf_security.py` — subcommands `encrypt` / `decrypt` (AES-256 via `doc.save(encryption=...)`)

### `write-paper-notes/` skill
A 4-phase pipeline documented in `write-paper-notes/SKILL.md`. Only Phase 1 is executed by code; Phases 2-4 are carried out by the invoking AI, driven by files under `references/` and `templates/`.

1. **Extraction (code)** — `write-paper-notes/scripts/extract.py --input <file> [--output-dir <dir>]` dispatches by file extension to `PdfExtractor` (PyMuPDF) or `DocxExtractor` (python-docx). Both subclass the template-method ABC `DocumentExtractor` in `base.py` (`load()` → `do_extract()` → `close()`, directories set up before, `close()` guaranteed via `finally`). Output: Markdown on stdout + images written to `<output-dir>/<input-stem>/images/`.
   - `extract_pdf.py` derives heading levels from a font-size histogram across the whole document (`_build_header_id_map`), and reconstructs two-column academic-paper reading order via `elements.sort(key=lambda e: (round(e.bbox[0], -1), e.bbox[1]))` — bucketing by x-coordinate first (column) then y (top-to-bottom within a column), so the left column is read fully before the right column. Vector drawings are grouped into figures with `page.cluster_drawings()` and filtered by `_is_significant_drawing` to drop decorative lines.
   - The skill assumes the invoking AI can read images directly — there is no OCR/text-only-AI fallback (it was deliberately removed).
2. **Content Analysis (AI)** — reads extracted images/text, detects paper type by emitting `PaperType: cs-ai-ml`, `PaperType: survey-review`, or omitting the line.
3. **Organization (AI)** — loads `references/style-guide/common.md` plus `references/style-guide/<type>.md` and `templates/<type>.md` (or `assets/report-template.md` as a generic fallback when no type was detected), and writes `notes.md` into the same directory as `images/`.
4. **Quality Review (AI)** — checks `notes.md` against `references/quality-checklist/common.md` plus the type-specific checklist, fixing and re-checking until every item passes.

Style guides and checklists are additive (`common.md` + `<type>.md`), so adding a new paper type only requires new `references/style-guide/<type>.md`, `references/quality-checklist/<type>.md`, and `templates/<type>.md` files.

### Tests
- `tests/pdf/` drives the five scripts via `subprocess.run([sys.executable, script, ...])` — CLI behavior only, no direct imports. Its OCR tests (`test_images_extractor.py`) are `@pytest.mark.skipif(not tesseract_available())`, so most of the suite passes without a Tesseract system install.
- `tests/write_paper_notes/` mixes subprocess tests (CLI behavior) with direct `import extract_pdf, extract_docx, base` (unit tests for `PdfExtractor`/`DocxExtractor`/`DocumentExtractor`).
- Each suite's `conftest.py` prepends its own skill's `scripts/` dir to `sys.path` so the direct imports resolve; `.pylintrc` does the same for `write-paper-notes/scripts` via `init-hook` (only that skill is linted this way).
- All test fixtures (sample PDFs/DOCX) are generated at runtime inside `conftest.py` helpers (e.g. `_create_simple_pdf`, `_create_docx_with_image`) — there are no static fixture files on disk.
