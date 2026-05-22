---
name: write-paper-notes
version: 2.2.0
description: "Analyze PDF academic papers and generate structured Markdown notes. Requires a PDF extraction capability (e.g., @pdf skill)."

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
- **Text Extraction Role**: Convert PDF to text (Markdown preferred; plain text fallback)
- **Image Extraction Role**: Extract embedded images. Built-in OCR is a bonus; if absent, the pipeline handles it via fallback logic.

## Prerequisites

Ensure at least one PDF extraction skill is installed (e.g., the **@pdf** skill). The AI will automatically discover and map available tools during the workflow.

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

Locate an installed PDF skill, read its `SKILL.md`, and identify the specific commands for:
- **Image Extraction**: Command + flags for extracting images, and identify if built-in OCR is supported
- **Text Extraction**: Command + flags for extracting text (Markdown support optional)

If a role cannot be mapped to any available tool, mark it as **"Not Available"** in the report instead of searching further.

Present the discovered capabilities to the user. Example:
- ✅ Text Extraction: `python pdf_text_extractor.py ...` (supports Markdown)
- ❌ Image Extraction: **Not Available** (no image-extraction tool found)

Ask: "Is this the correct tool mapping?" Do NOT proceed to Step 2 until the user confirms.

### Step 2 — Content Extraction

Run extraction commands based on Step 1's mapping:
- **Image Extraction**: If mapped to a valid command, run it to extract all embedded images. If marked as **"Not Available"**, skip this step.
- **Text Extraction**: If mapped to a valid command, run it. Determine the output format by applying the logic defined in the [Text Extraction Logic](#text-extraction-logic) section below.

### Step 3 — Extraction Gate

Present the extraction results to the user:
- Location of extracted images
- Location of extracted text
- Any errors or warnings

Confirm with the user that the extracted content looks correct before proceeding. If extraction failed, ask for guidance and potentially return to Step 1.

Do NOT skip this gate. Do NOT proceed to Step 4 until the user confirms.

### Step 4 — Content Analysis

First, determine the available data:
- **No images extracted** (Image Extraction marked as "Not Available" in Step 1) → Skip all image-related analysis. Proceed with text-only analysis.
- **Images extracted** → Check the discovery results from Step 1 to determine if the image extraction tool has built-in OCR:

  - **Built-in OCR available** → Use its integrated OCR output
  - **No built-in OCR** → Apply the [OCR Fallback Strategy](#ocr-fallback-strategy) (Tier 2: external OCR skill, or Tier 3: skip)

Then process the extracted content:
- **Image-input AI** (and images available): Examine each extracted image in the `images/` folder directly
- **Text-only AI** (and images available): Use the resolved OCR text to understand image content
- **No OCR available** (and images available): Show image file paths as visual reference
- **No images available**: Analyze the extracted text alone

Analyze the extracted text alongside any available image content to build a comprehensive understanding of the paper.

### Step 5 — Structural Organization

1. **Load the Style Guide**: Read `references/style-guide.md` for all formatting rules (headings, images, math, code, summaries, restructuring).
2. **Load the Template**: Read `assets/notes-template.md` for the required output skeleton.
3. **Fill the Template**: Every section in the template must be present in the output. Do not add or omit sections unless user preferences dictate.

Reorganize extracted content into `notes.md` following the style guide rules and template structure.

### Step 6 — Quality Review

Load `references/quality-checklist.md`. Verify every item on the checklist. Fix any violations before proceeding.

Report results to the user. Do NOT proceed to Step 7 until all checklist items pass.

### Step 7 — Final Delivery

Save the organized notes to `notes.md` in the output directory.

The final output must pass every item in `references/quality-checklist.md` before it is presented to the user.

## Logic Specifications

### Text Extraction Logic

The format of extracted text depends on the discovered tool's capabilities:

| Tool Capability | Action |
|---|---|
| ✅ Supports Markdown (via parameter, default output, or library behavior) | Use Markdown output |
| ❌ No Markdown support | Fall back to Plain Text |

The AI must verify Markdown support by examining the tool's documentation, help output, or source code — do not assume Markdown is available without confirmation.

### OCR Fallback Strategy

OCR resolution follows a three-tier fallback:

| Tier | Check | Action |
|------|-------|--------|
| 1 | Does the chosen PDF skill have built-in OCR? | Use its integrated OCR |
| 2 | Is an external OCR skill or system tool available? (e.g., `@ocr-document-processor`, `tesseract` CLI) | Pipe extracted images through the external OCR tool |
| 3 | No OCR capability found anywhere | **Skip OCR**. Show image file paths to AI as visual reference |

#### OCR Behavior Summary

| OCR Available | AI Type | Result |
|---|---|---|
| ✅ Yes | Text-only AI | OCR text available for understanding image content |
| ✅ Yes | Image-input AI | OCR optional; AI can read images directly |
| ❌ No | Text-only AI | Images noted as "available at path" — AI cannot inspect them |
| ❌ No | Image-input AI | AI reads images directly from file paths |

### Heading Detection

When Markdown mode is available, headings are automatically detected by the Markdown converter based on font size hierarchy:
- Larger fonts → Higher heading levels (##, ###, ####)
- No manual pattern matching required

When only plain text is available, the AI must infer heading structure from content cues (e.g., numbering, line gaps, font size indicators if present).
