# myskills

Personal Agent Skills collection. Each skill installs on its own:

```bash
npx skills add ian5030560/myskills --skill <name>
```

| Skill | What it does |
|-------|--------------|
| [`pdf`](#pdf) | Extract, manipulate and secure PDFs |
| [`write-paper-notes`](#write-paper-notes) | Turn a PDF paper into structured study notes |
| [`evaluate-paper`](#evaluate-paper) | Appraise a PDF paper against your research question and say how to use it |

## pdf

Complete PDF toolkit with 5 Python scripts powered by PyMuPDF:

| Tool | Purpose |
|------|---------|
| `pdf_text_extractor.py` | Plain text extraction (no OCR) |
| `pdf_images_extractor.py` | Image extraction with optional Tesseract OCR |
| `pdf_table_extractor.py` | Table detection and Markdown conversion |
| `pdf_manager.py` | Merge, split, rotate pages, manage metadata |
| `pdf_security.py` | AES-256 encrypt/decrypt PDFs |

### Requirements

- `pip install PyMuPDF`
- Tesseract, only for OCR in `pdf_images_extractor.py` (per-OS install commands are in [`pdf/SKILL.md`](pdf/SKILL.md))

### Installation

```bash
npx skills add ian5030560/myskills --skill pdf
```

## write-paper-notes

Turn PDF academic papers into study notes with a fixed skeleton. Ask your AI to write notes for a paper and give it the PDF path.

### Features

- **PDF only** — DOCX and other formats must be saved as PDF first
- **Text extraction** — Plain text in reading order via PyMuPDF: two-column aware, running headers/footers and sidebar text removed, split paragraphs rejoined; no OCR
- **Page images** — Every page rendered with a faint coordinate grid; the AI reads figures, tables and scanned pages from them
- **Figure crops** — The AI draws a generous box; the script trims captions, body text and headers off the edges and re-renders the figure at 200 dpi
- **Tables as Markdown** — Tables are rebuilt from the page images, not cropped as pictures
- **Fixed skeleton** — Every paper gets the same sections: Introduction (background, motivation, research questions, contributions), Related Work, Method, Results, Conclusion (findings, limitations, future work); method and results follow the paper's own subsections
- **No fabrication** — Only content found in the paper; empty sections are omitted
- **Your language** — Notes are written in the language you use with the AI
- **Single style guide** — One rule list used for both writing and self-checking

### Pipeline (4 Steps)

1. **Extract** — `scripts/extract_text.py` writes `text.md`; `scripts/render_pages.py` writes gridded page images to `pages/`
2. **Write** — AI reads the text and page images, crops figures with `scripts/crop_figure.py`, rebuilds tables as Markdown, and saves `notes.md`
3. **Self-check** — AI checks `notes.md` against the style guide and fixes issues until all rules pass
4. **Clean up** — `text.md` and `pages/` are deleted

Output, in `<output-dir>/<pdf-stem>/`:

```
notes.md
images/      # cropped figures linked from notes.md
```

### Requirements

- `pip install PyMuPDF`
- An AI that can read images (it reads page images and checks its own crops)

### Installation

```bash
npx skills add ian5030560/myskills --skill write-paper-notes
```

## evaluate-paper

Appraise one PDF paper against your research question before you rely on it. Give the AI the PDF path and your research question. The report gives a **usage label** (main report, background, comparison, or not for now) with reasons. It never gives a score or a grade.

Suggested order: appraise first with `evaluate-paper`, then write notes with `write-paper-notes` for the papers worth keeping.

### What it does

1. **Article ID card** — bibliographic details, DOI, venue, article type, version read, review status
2. **External assessment** — a standard checklist chosen by study design (CASP, AMSTAR 2 or MMAT; none if no checklist fits), plus article and journal metrics from OpenAlex and Crossref and a retraction check
3. **Content judgement** — source and version, whether the content answers your question, whether the evidence supports the claims, measurement, and scope of inference
4. **Conclusion** — the usage label first, then what you still need to confirm yourself

Only a retraction can change the label on its own; citation counts and journal numbers are side clues.

### Metrics and MCP (optional)

The script queries OpenAlex and Crossref without a key. If your environment has MCP tools for OpenAlex, Scopus or Journal Citation Reports, the AI can use them to fill in more (for example JIF or CiteScore) and label those numbers with their source. Without them the appraisal is still complete: missing numbers are marked "not obtained" with where to look them up. The skill does not install, configure or recommend any MCP, and never asks for a key or an email address.

### Output

The report is written to a temporary folder and shown in the conversation. It is copied to `<output-dir>/<pdf-stem>/appraisal.md` only when you agree (or when you asked to save up front). Metrics fetched on the same day are reused.

### Requirements

- Python 3 (standard library only) and network access
- An AI that can read the PDF

### Installation

```bash
npx skills add ian5030560/myskills --skill evaluate-paper
```

## Development

```bash
pip install PyMuPDF Pillow PyYAML pytest
pytest tests/pdf/
pytest tests/write_paper_notes/
pytest tests/evaluate_paper/
pytest tests/test_skill_files.py
```

All test PDFs are generated at runtime; no fixture files are stored in the repo. Shortcuts for the skills CLI:

```bash
make install skill=<name>
make uninstall skill=<name>
```
