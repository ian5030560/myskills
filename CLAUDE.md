# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

"myskills" is a personal collection of Agent Skills, distributed via `npx skills add ian5030560/myskills --skill <name>`. Two independent skills live here:
- `pdf/` — five standalone PDF CLI tools (PyMuPDF/fitz + Tesseract OCR)
- `write-paper-notes/` — PDF → structured Markdown paper-notes pipeline

The repo root also contains an activated Python venv (`Include/`, `Lib/`, `Scripts/`, `pyvenv.cfg`) and a vendored `.agents/skills/skill-creator/` — both gitignored, not part of the project source.

## Commands

Install dependencies:
```
pip install PyMuPDF Pillow
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

**Windows UTF-8:** PDFs often contain non-ASCII text, and the Windows console default (cp950/Big5) can't handle it. Set `PYTHONIOENCODING` in the *same* command as the `python` invocation — env vars don't persist across separate shell/tool calls:
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
A 4-step pipeline documented in `write-paper-notes/SKILL.md`, PDF only (any other format is rejected with a "save as PDF first" message). Scripts extract the text and render page images; the invoking AI reads them, crops figures, and writes the notes, driven by the skeleton and section mapping in `SKILL.md` plus the single style guide `references/style-guide.md`. Domain terms (筆記, 固定區塊, 子章節, 風格指南, 頁面圖, 裁切圖) are defined in the root `GLOSSARY.md`; the design decision is `docs/adr/0001-pdf-only-ai-cropped-figures.md`.

1. **Extract (code)** — two CLIs, both `--input <pdf> [--output-dir <dir>]`, writing into `<output-dir>/<input-stem>/`:
   - `extract_text.py` → `text.md`: plain text in reading order with a `<!-- pN -->` marker per page. Running headers/footers are dropped (short blocks in the page margins or among the top/bottom two blocks whose digit-normalized text repeats on ≥30% of pages); full-width blocks split a page into bands, each read left column then right; numbered heading lines are split onto their own line. No heading markers, no table reconstruction, no OCR — pages with no text layer are flagged `此頁無文字層`. Stdout reports only the path, page count and pages with no text layer.
   - `render_pages.py` → `pages/pN.png` (110 dpi) with a faint 0.1-step grid labelled on the top/left edges, plus `pages/source.json` recording the source PDF path.
2. **Write (AI)** — reads `text.md`, infers headings from section numbering, rebuilds tables from page images (tables are never cropped), and crops figures with `crop_figure.py --page-image pages/pN.png --box x0,y0,x1,y1 --name <name>` (0–1 page fractions). The AI draws the box generously; the script peels captions, body paragraphs, section headings and running headers off the box edges (inward only — never through figure graphics or figure labels), drops thin slivers and white margins, and re-renders the final box from the PDF at 200 dpi to `images/<name>.png`, printing the final box. Notes use one fixed skeleton for every paper: 介紹 (fixed subsections 背景/動機/研究問題/貢獻), 相關研究, 方法, 結果, 結論 (fixed subsections 主要發現/限制/未來方向); 相關研究/方法/結果 take subsections from the paper's own sections; empty sections are omitted. Notes are written in the user's language (asks when unclear).
3. **Self-check (AI)** — checks `notes.md` against every rule in `references/style-guide.md` (the style guide doubles as the checklist), fixing and re-checking until every rule passes.
4. **Clean up (AI)** — deletes `text.md` and `pages/`, leaving only `notes.md` and `images/`.

`crop_figure.py` and `render_pages.py` import shared helpers (running-header detection, PDF CLI parsing) from `extract_text.py`, so the header rule stays identical across scripts.

`tests/write_paper_notes/test_skill_files.py` guards the instruction files: every skill path referenced in `SKILL.md` must exist, and `SKILL.md` + `references/style-guide.md` must be the only `.md` files in the skill.

### Tests
- `tests/pdf/` drives the five scripts via `subprocess.run([sys.executable, script, ...])` — CLI behavior only, no direct imports. Its OCR tests (`test_images_extractor.py`) are `@pytest.mark.skipif(not tesseract_available())`, so most of the suite passes without a Tesseract system install.
- `tests/write_paper_notes/` also drives its three scripts via subprocess only. Crop trimming is asserted through the final box `crop_figure.py` prints, compared with the known layout of a generated PDF (`CROP_LAYOUT` in `conftest.py`) — no image analysis.
- Each suite's `conftest.py` prepends its own skill's `scripts/` dir to `sys.path`; `.pylintrc` does the same for `write-paper-notes/scripts` via `init-hook` (only that skill is linted this way).
- All test fixtures (sample PDFs) are generated at runtime inside `conftest.py` helpers (e.g. `_create_simple_pdf`, `_create_crop_pdf`) — there are no static fixture files on disk.

## Agent skills

### Issue tracker

Issues and specs live as local markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as a `Status:` line. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
