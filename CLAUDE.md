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

## Commits

Before every commit, show the user the planned commit arrangement and wait for their confirmation: how the changes are split into commits, which files go in each, and each commit message. Never commit without that confirmation, even if a commit was approved earlier.

## Architecture

### `pdf/` skill
Five independent CLI entrypoints in `pdf/scripts/`, each self-contained (no shared base class), all taking `--pdf` + `--output-dir` and calling PyMuPDF (`fitz`) directly:
- `pdf_text_extractor.py` — plain text only, no OCR
- `pdf_images_extractor.py` — image extraction + optional Tesseract OCR via `fitz.Pixmap.pdfocr_tobytes()`; `--no-ocr` to skip
- `pdf_table_extractor.py` — `page.find_tables()` → Markdown tables
- `pdf_manager.py` — subcommands `merge` / `split` / `rotate` / `metadata` (`insert_pdf`, `set_rotation`)
- `pdf_security.py` — subcommands `encrypt` / `decrypt` (AES-256 via `doc.save(encryption=...)`)

### `write-paper-notes/` skill
A 3-step pipeline documented in `write-paper-notes/SKILL.md`. Only step 1 is executed by code; steps 2-3 are carried out by the invoking AI, driven by the skeleton and section mapping in `SKILL.md` plus the single style guide `references/style-guide.md`. Domain terms (筆記, 固定區塊, 子章節, 風格指南) are defined in the root `GLOSSARY.md`.

1. **Extraction (code)** — `write-paper-notes/scripts/extract.py --input <file> [--output-dir <dir>]` dispatches by file extension to `PdfExtractor` (PyMuPDF) or `DocxExtractor` (python-docx). Both subclass the template-method ABC `DocumentExtractor` in `base.py` (`load()` → `do_extract()` → `close()`, directories set up before, `close()` guaranteed via `finally`). Output: Markdown on stdout + images written to `<output-dir>/<input-stem>/images/`.
   - `extract_pdf.py` derives heading levels from a font-size histogram across the whole document (`_build_header_id_map`), and reconstructs two-column academic-paper reading order via `elements.sort(key=lambda e: (round(e.bbox[0], -1), e.bbox[1]))` — bucketing by x-coordinate first (column) then y (top-to-bottom within a column), so the left column is read fully before the right column. Vector drawings are grouped into figures with `page.cluster_drawings()` and filtered by `_is_significant_drawing` to drop decorative lines.
   - The skill assumes the invoking AI can read images directly — there is no OCR/text-only-AI fallback (it was deliberately removed).
2. **Write (AI)** — reads the extracted text and images, then writes `notes.md` next to `images/` using one fixed skeleton for every paper (no paper-type detection): 介紹 (fixed subsections 背景/動機/研究問題/貢獻), 相關研究, 方法, 結果, 結論 (fixed subsections 主要發現/限制/未來方向). 相關研究/方法/結果 take subsections from the paper's own sections; empty sections are omitted. Notes are written in the user's language (asks when unclear).
3. **Self-check (AI)** — checks `notes.md` against every rule in `references/style-guide.md` (the style guide doubles as the checklist), fixing and re-checking until every rule passes.

`tests/write_paper_notes/test_skill_files.py` guards the instruction files: every skill path referenced in `SKILL.md` must exist, and `SKILL.md` + `references/style-guide.md` must be the only `.md` files in the skill.

### Tests
- `tests/pdf/` drives the five scripts via `subprocess.run([sys.executable, script, ...])` — CLI behavior only, no direct imports. Its OCR tests (`test_images_extractor.py`) are `@pytest.mark.skipif(not tesseract_available())`, so most of the suite passes without a Tesseract system install.
- `tests/write_paper_notes/` mixes subprocess tests (CLI behavior) with direct `import extract_pdf, extract_docx, base` (unit tests for `PdfExtractor`/`DocxExtractor`/`DocumentExtractor`).
- Each suite's `conftest.py` prepends its own skill's `scripts/` dir to `sys.path` so the direct imports resolve; `.pylintrc` does the same for `write-paper-notes/scripts` via `init-hook` (only that skill is linted this way).
- All test fixtures (sample PDFs/DOCX) are generated at runtime inside `conftest.py` helpers (e.g. `_create_simple_pdf`, `_create_docx_with_image`) — there are no static fixture files on disk.

## Agent skills

### Issue tracker

Issues and specs live as local markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as a `Status:` line. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
