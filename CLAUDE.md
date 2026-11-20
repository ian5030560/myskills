# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

"myskills" is a personal collection of Agent Skills, distributed via `npx skills add ian5030560/myskills --skill <name>`. Three independent skills live here:
- `pdf/` — five standalone PDF CLI tools (PyMuPDF/fitz + Tesseract OCR)
- `write-paper-notes/` — PDF → structured Markdown paper-notes pipeline
- `evaluate-paper/` — PDF paper appraisal: identity card, external assessment, content judgement, usage label

The repo root also contains an activated Python venv (`Include/`, `Lib/`, `Scripts/`, `pyvenv.cfg`) and a vendored `.agents/skills/skill-creator/` — both gitignored, not part of the project source.

## Commands

Install dependencies:
```
pip install PyMuPDF Pillow PyYAML
```
PyYAML is only needed by `tests/test_skill_files.py` (frontmatter parsing).
`pdf/` also requires the Tesseract system binary for OCR (per-OS install commands are in `pdf/SKILL.md`).

Run tests:
```
pytest tests/pdf/
pytest tests/write_paper_notes/
pytest tests/evaluate_paper/
pytest tests/test_skill_files.py
```
Run a single test with a pytest node id, e.g.:
```
pytest tests/pdf/test_manager.py::TestMerge::test_merge_two_files -q
```

Lint:
```
pylint pdf/scripts/*.py --rcfile=.pylintrc
pylint write-paper-notes/scripts/*.py --rcfile=.pylintrc
pylint evaluate-paper/scripts/*.py --rcfile=.pylintrc
pylint benchmarks/olmocr/*.py --rcfile=.pylintrc
```
Run lint from the repo root: `.pylintrc` resolves each skill's `scripts/` against the working directory.

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
   - `extract_text.py` → `text.md`: plain text in reading order with a `<!-- pN -->` marker per page. Running headers/footers are dropped (short blocks in the page margins or among the top/bottom two blocks whose digit-normalized text repeats on ≥30% of pages); full-width blocks split a page into bands, each read left column then right; numbered heading lines are split onto their own line; Latin ligature code points (U+FB00–FB06) are expanded to letters; a word hyphenated at a line end (`-`, U+2010, U+2011, soft hyphen) is rejoined when the next text starts lowercase, within a paragraph and between consecutive paragraphs of one page, never across pages. No heading markers, no table reconstruction, no OCR — pages with no text layer are flagged `此頁無文字層`. Stdout reports only the path, page count and pages with no text layer.
   - `render_pages.py` → `pages/pN.png` (110 dpi) with a faint 0.1-step grid labelled on the top/left edges, plus `pages/source.json` recording the source PDF path.
2. **Write (AI)** — reads `text.md`, infers headings from section numbering, rebuilds tables from page images (tables are never cropped), and crops figures with `crop_figure.py --page-image pages/pN.png --box x0,y0,x1,y1 --name <name>` (0–1 page fractions). The AI draws the box generously; the script peels captions, body paragraphs, section headings and running headers off the box edges (inward only — never through figure graphics or figure labels), drops thin slivers and white margins, and re-renders the final box from the PDF at 200 dpi to `images/<name>.png`, printing the final box. Notes use one fixed skeleton for every paper: Introduction (fixed subsections Background/Motivation/Research Questions/Contributions), Related Work, Method, Results, Conclusion (fixed subsections Key Findings/Limitations/Future Work), headings translated into the notes language; Related Work/Method/Results take subsections from the paper's own sections; empty sections are omitted. Notes are written in the user's language (asks when unclear).
3. **Self-check (AI)** — checks `notes.md` against every rule in `references/style-guide.md` (the style guide doubles as the checklist), fixing and re-checking until every rule passes.
4. **Clean up (AI)** — deletes `text.md` and `pages/`, leaving only `notes.md` and `images/`.

`crop_figure.py` and `render_pages.py` import shared helpers (running-header detection, PDF CLI parsing) from `extract_text.py`, so the header rule stays identical across scripts.

### `evaluate-paper/` skill
Appraises one PDF paper against the user's research question; steps are in `evaluate-paper/SKILL.md`. PDF only, no text-extraction script (the AI reads the PDF directly). Terms are in `GLOSSARY.md`; decisions are in ADRs 0002 (appraisal without scores) and 0003 (keyless script, keyed metrics via the user's own MCP); the spec is `.scratch/evaluate-paper/spec.md`.

1. **Article ID card (AI)** — bibliographic details, DOI, venue, article type judged from content, version read, review status; identifies only.
2. **External assessment** — two parts:
   - *Checklist (AI):* `references/checklist-selection.md` picks one by study design — CASP RCT/cohort/qualitative/systematic review (verbatim, CC BY-NC-SA 4.0), AMSTAR 2 (systematic reviews of healthcare interventions), MMAT (paraphrased, registered copyright) — or none, in which case the report says so. Answers carry a paper location and are never summed.
   - *Metrics (code):* `scripts/fetch_metrics.py` (stdlib only, keyless) takes `--doi` or `--title` (candidates only) and prints OpenAlex and Crossref article numbers side by side, OpenAlex journal `2yr_mean_citedness` (JIF-style, not JIF), a `retraction` verdict (retracted / no_record_found / unknown), and `updates`; failures are named per source. Keyed data (OpenAlex after quota exhaustion, JIF, CiteScore) comes only from the user's own MCP, matched by capability and never named or recommended; without one the report writes 未取得.
3. **Content judgement (AI)** — the five rules in `references/content-judgement.md`; each outcome is ok / concern / not enough information with a location.
4. **Conclusion** — usage label 主報告 / 背景 / 比較 / 暫不使用 first, then 仍需確認. No scores; only retraction can change the label.
5. **Write and save** — the report is written to `<temp>/evaluate-paper/<pdf-stem>/appraisal.md` (with `metrics.json`, reused if queried the same day), self-checked against `references/report-format.md` and `content-judgement.md`, shown in full, and copied to `<output-dir>/<pdf-stem>/appraisal.md` only when the user agrees.

`tests/test_skill_files.py` checks every skill folder (a top-level, non-hidden directory with a `SKILL.md`) against the Agent Skills spec: frontmatter limited to `name`/`description`/`license`/`compatibility`/`metadata`/`allowed-tools` (`metadata` values must be strings, so `version` lives at `metadata.version`), `name` rules and folder match, description limits, `SKILL.md` under 500 lines, references one level deep, referenced paths exist, and no file under `references/`, `scripts/` or `assets/` that `SKILL.md` doesn't mention. Writing quality is not tested. Rule sources are in `.scratch/evaluate-paper/research/agent-skills-spec.md`.

### `benchmarks/olmocr/`
A manual development tool (not a skill, not pytest) that scores `extract_text.py` on the `multi_column` (order) and `long_tiny_text` (present) categories of olmOCR-Bench with the official scorer, and compares each run with the committed `baseline.json`. `setup_venv.py --python <3.11+>` builds the scorer's own gitignored `.venv`, `fetch.py` downloads the data into the gitignored `data/`, `run.py` extracts, scores and prints the delta (newly failing/passing test IDs); `run.py --update-baseline` accepts a run. PDFs with no text layer are excluded and counted. Details, exclusions and Windows workarounds are in `benchmarks/olmocr/README.md`; the spec is `.scratch/olmocr-bench/spec.md`.

### Tests
- `tests/pdf/` drives the five scripts via `subprocess.run([sys.executable, script, ...])` — CLI behavior only, no direct imports. Its OCR tests (`test_images_extractor.py`) are `@pytest.mark.skipif(not tesseract_available())`, so most of the suite passes without a Tesseract system install.
- `tests/write_paper_notes/` also drives its three scripts via subprocess only. Crop trimming is asserted through the final box `crop_figure.py` prints, compared with the known layout of a generated PDF (`CROP_LAYOUT` in `conftest.py`) — no image analysis.
- `tests/evaluate_paper/` runs `fetch_metrics.py` as a subprocess against a fake local HTTP server that plays OpenAlex (`/openalex`) and Crossref (`/crossref`) via `--api-base`; tests never touch the real network. Only the script is tested; the checklists, content rules and report format are written guidance and are checked by `tests/test_skill_files.py` for structure only.
- Each suite's `conftest.py` prepends its own skill's `scripts/` dir to `sys.path`; `.pylintrc` adds every `*/scripts` dir (relative to the working directory) via `init-hook`.
- `tests/test_skill_files.py` is repo-wide rather than per-skill; its negative cases build throwaway skill folders in `tmp_path` to prove each check fails on a violation.
- All test fixtures (sample PDFs) are generated at runtime inside `conftest.py` helpers (e.g. `_create_simple_pdf`, `_create_crop_pdf`) — there are no static fixture files on disk.

## Agent skills

### Issue tracker

Issues and specs live as local markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as a `Status:` line. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
