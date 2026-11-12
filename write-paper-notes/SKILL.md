---
name: write-paper-notes
version: 3.0.0
description: "Turn academic papers (PDF) into organized Markdown notes."

metadata:
  starchild:
    emoji: "📄"
    skillKey: write-paper-notes
    requires:
      env: []
      bins: [python]
user-invocable: true
---

Turn a PDF paper into study notes (`notes.md`) with a fixed skeleton. Run the four steps in order.

## Setup

```bash
pip install PyMuPDF
```

Only PDF is supported. If the user has a DOCX or any other format, ask them to save it as PDF first.

**Windows:** set `PYTHONIOENCODING=utf-8` in the *same* command as the script, since env vars don't persist across tool calls:

```powershell
$env:PYTHONIOENCODING="utf-8"; python scripts/extract_text.py --input <file.pdf> [--output-dir <dir>]
```

All output goes to `<output-dir>/<input-stem>/` (`<output-dir>` defaults to the current directory); below, `<out>` means that folder.

## Steps

### 1. Extract

```
python scripts/extract_text.py --input <file.pdf> [--output-dir <dir>]
python scripts/render_pages.py --input <file.pdf> [--output-dir <dir>]
```

- `extract_text.py` writes `<out>/text.md`: the paper's text in reading order, each page starting with `<!-- pN -->`. Headings carry no `#` and tables are flattened. Stdout lists pages with no text layer.
- `render_pages.py` writes one page image per page to `<out>/pages/pN.png`, with a faint grid labelled `.1`–`.9` along the top and left edges (fractions of page width and height).

### 2. Write

Decide the notes language first: the language the user is talking to you in. If you can't tell (e.g. they only gave a file path), ask before writing.

Read `<out>/text.md` (in parts if it is long). Then write `<out>/notes.md` using the skeleton and section mapping below, following every rule in `references/style-guide.md`:

- **Headings:** infer the paper's sections from their numbering (`3.`, `3.1`, `3.1.2`); the text has no heading markers.
- **Pages with no text layer** (listed by `extract_text.py`, flagged `此頁無文字層` ("no text layer on this page") in `text.md`): read those pages from their page images.
- **Tables:** for each table you use, open the page image of the page where its `Table N` caption appears and rebuild the table as a Markdown table. Use the flattened text to double-check values. Never crop a table as an image.
- **Figures:** for each figure worth including, open its page image and crop it:

  ```
  python scripts/crop_figure.py --page-image <out>/pages/pN.png --box x0,y0,x1,y1 --name <name>
  ```

  - Draw the box **generously** around the whole figure, using the grid; including the caption and some surrounding text is fine. The script removes captions, body text, section headings and running headers at the box edges, trims white margins, and saves `<out>/images/<name>.png`.
  - Look at the saved crop and check all four edges. If any part of the figure is cut off, enlarge the box on that side and crop again. Text that belongs to the figure (labels, legends) stays; if a caption or paragraph is still in the crop, tighten that side and crop again.
  - If the script says nothing is left, the box missed the figure: look at the page image again and redraw it.
  - Link the crop from `notes.md` as `images/<name>.png`.
- Open only the page images you need (figures, tables, pages with no text layer, or text that looks garbled); each one costs context.

### 3. Self-check

Check `notes.md` against every rule in `references/style-guide.md`. Fix each failure, then check again until every rule passes. Deliver `notes.md` to the user.

### 4. Clean up

After delivering `notes.md`, delete `<out>/text.md` and the `<out>/pages/` folder. Delete nothing else. `<out>` should end with only `notes.md` and `images/`.

## Skeleton

Translate every heading into the notes language.

```
# <Paper title>
> Authors · Year · Venue

## Introduction
### Background
### Motivation
### Research Questions
### Contributions
## Related Work
## Method
## Results
## Conclusion
### Key Findings
### Limitations
### Future Work
```

- The metadata line holds only what the paper states.
- Introduction and Conclusion always use the fixed subsections above.
- Related Work, Method and Results take their subsections from the paper's own sections.
- A section or subsection with nothing from the paper to put in it is omitted entirely, heading included.

## Section mapping

Where each part of the paper goes:

| Paper section | Goes to |
|:---|:---|
| Abstract | Not written into the notes (read it for an overview) |
| Introduction | The four Introduction subsections |
| Background / Preliminaries | Background |
| Related Work / Literature Review | Related Work |
| Method; for surveys, Research Methodology / Taxonomy / Key Approaches | Method |
| Experiments / Discussion / Analysis; for surveys, Comparison / Benchmark | Results |
| Conclusion | Key Findings |
| Limitations / Threats to Validity | Limitations |
| Future Work / Open Challenges | Future Work |
| Appendix | Only when the main text cites it and it's needed to understand the method or results; merged into that section |
| References / Acknowledgments | Not included |
| Anything else | The closest section, as a subsection |
