---
name: write-paper-notes
version: 2.2.0
description: "Analyze PDF academic papers and generate structured Markdown notes. Requires a PDF extraction capability (any installed PDF skill)."

metadata:
  pattern: pipeline
  steps: "7"
  starchild:
    emoji: "📄"
    skillKey: write-paper-notes
    requires:
      env: []
      bins: [python]
    install: []

user-invocable: true
---

Analyze PDF academic papers and generate structured Markdown notes using a PDF extraction skill for content extraction and AI for content organization.

This skill does **not** bundle its own extraction logic. Instead, it requires a **PDF extraction capability** — any skill or tool that can fulfill the following roles:
- **Text Extraction Role**: Convert PDF to text.
- **Image Extraction Role**: Extract embedded images. Built-in OCR is a bonus; if absent, the pipeline handles it via fallback logic.
- **Table Extraction Role**: Detect and extract tables as structured Markdown.

## Prerequisites

Ensure at least one PDF extraction skill is installed. The AI will automatically discover and map available tools during the workflow.

OCR may require Tesseract system-wide installation depending on the chosen tool (see the respective skill's documentation).

### Windows UTF-8 Encoding

Windows console default encoding (cp950/Big5) cannot handle UTF-8 characters in PDFs. Set the following environment variable before running Python-based PDF tools:

**PowerShell:**
```powershell
$env:PYTHONIOENCODING="utf-8"
```

**CMD:**
```cmd
set PYTHONIOENCODING=utf-8
```

## Pipeline

You are running a document analysis pipeline. Execute each step in order. Do NOT skip steps or proceed if a step fails.

### Step 1 — Capability Discovery

First, determine your own AI type: are you an **Image-input AI** (can directly see images) or a **Text-only AI** (cannot see images)?

Then, locate an installed PDF skill, read its `SKILL.md`, and identify the specific commands for:
- **Image Extraction**: Command + flags for extracting images.
  - If you are a **Text-only AI**, also identify if built-in OCR is supported.
  - If you are an **Image-input AI**, ignore OCR capabilities entirely — they are not needed.
- **Text Extraction**: Command + flags for extracting text.
- **Table Extraction**: Command + flags for extracting tables as structured Markdown.

If a role cannot be mapped to any available tool, mark it as **"Not Available"**.

Perform a self-check on the mapping: are the discovered commands reasonable for the identified tool? If yes, proceed to Step 2 automatically.

**Intervention trigger**: Only ask the user for guidance if:
- No tool can be found for the **Text Extraction** role (critical failure)
- No tool can be found for the **Table Extraction** role (critical failure)
- The mapping is ambiguous (e.g., multiple tools with conflicting capabilities)

### Step 2 — Content Extraction

Run extraction commands based on Step 1's mapping. **Order matters**: run text extraction last so the AI inspects tables before the text to better match tables to their context.

1. **Image Extraction**: If mapped to a valid command, run it to extract all embedded images. If marked as **"Not Available"**, skip this step.
2. **Table Extraction**: If mapped to a valid command, run it to extract all tables. If marked as **"Not Available"**, skip this step. The output is typically a file containing structured tables; note any page or position markers provided by the tool for later alignment with text context.
3. **Text Extraction**: Run the text extraction command.

**After extraction, reorganize the images**: The Image Extraction tool may output images in a `<pdf_stem>/` subfolder. Move all extracted image files into a dedicated `images/` directory at the root of the notes output folder. This ensures the final path is `images/<filename>`, matching the notes template.

### Step 3 — Extraction Gate

Perform an automated quality check on the extraction results:
- **Text**: Verify output is non-empty, has no obvious encoding corruption, and matches expected format
- **Images**: Confirm the `images/` directory exists and contains the expected files

If the results pass all checks, proceed to Step 4 automatically.

**Intervention trigger**: Only ask the user for guidance if:
- Text output is empty, corrupted, or far shorter than expected
- No images were found but Step 1 confirmed the tool supports extraction
- The extraction tool reported errors or warnings

### Step 4 — Content Analysis

First, determine what data is available from Step 2:
- **Text**: Always available (critical path; extraction must succeed).
- **Tables**: Available if a Table Extraction tool was found and ran successfully.
- **Images**: Available if an Image Extraction tool was found and ran successfully.

**Tables alignment**: Read the table extraction output if present. Tables are typically annotated with page numbers or position references by the tool. Use these markers to locate the corresponding section in the plain text, then insert each table at its contextually relevant position in the final notes — not grouped at the end.

For images, use the AI type you already determined in Step 1 to decide whether OCR is needed:

#### If you are an Image-input AI (can directly see images):

Skip OCR entirely. Examine each extracted image in the `images/` folder directly. OCR is redundant and should not be triggered.

#### If you are a Text-only AI (cannot see images):

Trigger the [OCR Fallback Strategy](#ocr-fallback-strategy) to obtain text descriptions of the images. Use the resolved OCR text to understand image content.

---

Synthesize all available data streams (text + tables + images/OCR) into a comprehensive understanding of the paper before proceeding to Step 5.

### Step 5 — Structural Organization

1. **Load the Style Guide**: Read `references/style-guide.md` for all formatting rules (headings, images, math, code, summaries, restructuring).
2. **Load the Template**: Read `assets/notes-template.md` for the required output skeleton.
3. **Fill the Template**: Every section in the template must be present in the output. Do not add or omit sections unless user preferences dictate.

Reorganize extracted content into `notes.md` following the style guide rules and template structure.

### Step 6 — Quality Review

Load `references/quality-checklist.md`. Verify every item on the checklist. Auto-fix any violations found.

After fixing, re-check until all items pass. If a violation cannot be auto-fixed (e.g., ambiguous image placement), note it and continue.

Proceed to Step 7 automatically once the checklist passes.

**Intervention trigger**: Only report to the user if a critical violation (e.g., missing LaTeX formatting, broken image paths) cannot be resolved after multiple attempts.

### Step 7 — Final Delivery

Save the organized notes to `notes.md` in the output directory.

The final output must pass every item in `references/quality-checklist.md` before it is presented to the user.

## Logic Specifications

### OCR Fallback Strategy

This strategy is only invoked when the AI is **Text-only** (cannot directly analyze images). Image-input AIs skip OCR entirely.

When triggered, OCR resolution follows a three-tier fallback:

| Tier | Check | Action |
|------|-------|--------|
| 1 | Does the chosen PDF skill have built-in OCR? | Use its integrated OCR |
| 2 | Is an external OCR skill or system tool available? (e.g., `@ocr-document-processor`, `tesseract` CLI) | Pipe extracted images through the external OCR tool |
| 3 | No OCR capability found anywhere | **Skip OCR**. Show image file paths as visual reference |

#### OCR Behavior Summary

| OCR Available | AI Type | Result |
|---|---|---|
| ✅ Yes | Text-only | OCR text available for understanding image content |
| ❌ No | Text-only | Images noted as "available at path" — AI cannot inspect them |

### Heading Detection

The AI must infer heading structure from the extracted content. Use these cues:

- **Numbering patterns**: Sections with consistent numbering (1., 1.1, 1.1.1 or I., A., 1.) indicate headings
- **Line gaps**: A blank line followed by a short block of text often indicates a heading
- **Font size indicators**: If the PDF tool outputs font-size metadata, use it to determine heading hierarchy
- **Paper structure**: Academic papers follow a standard structure (Abstract → Introduction → Related Work → Method → Experiments → Conclusion) — use this structural knowledge as a fallback
