---
name: write-paper-notes
version: 2.2.0
description: "Extract content from PDF papers and generate structured Markdown notes. Default: OCR enabled for text-only AIs. Use --no-ocr for image-input AIs."

metadata:
  starchild:
    emoji: "📄"
    skillKey: write-paper-notes
    requires:
      env: []
      bins: [python]
    install:
      - kind: pip
        package: pypdf
      - kind: pip
        package: pypdf-table-extraction
      - kind: pip
        package: pytesseract
      - kind: pip
        package: Pillow
      - kind: system
        name: tesseract-ocr
        url: https://github.com/UB-Mannheim/tesseract/wiki

user-invocable: true
---

Extract text, images, and tables from PDF academic papers and generate structured Markdown notes. 

**OCR Default**: Enabled (for text-only AIs that cannot view images)
**When to use `--no-ocr`**: ONLY when your AI supports image input (e.g., GPT-4V, Claude 3.5 Sonnet)

## Processing Flow

| Step | Action |
|------|--------|
| 0 | Install dependencies: `pip install pypdf pypdf-table-extraction pytesseract Pillow` |
| 0.1 | Install Tesseract OCR (see OCR Configuration below) |
| 1 | **If your AI supports image input (e.g., GPT-4V)**: Run with `--no-ocr` |
|   | `python scripts/extract.py --pdf <pdf> --no-ocr --output-dir <dir>` |
|   | **If your AI is text-only**: Run without `--no-ocr` (requires Tesseract) |
|   | `python scripts/extract.py --pdf <pdf> [--output-dir <dir>]` (output to stdout) |
| 2 | AI organizes content by sections and subsections |
| 3 | Run `python scripts/save_notes.py --content "<AI_output>" --output-dir <dir>` |
| 4 | Notes saved to `notes.md` in the same directory as images |

## OCR Configuration

**Default behavior**: OCR enabled (for text-only AIs that cannot view images)

### When to use `--no-ocr`

**ONLY use `--no-ocr` when your AI supports image input** (e.g., GPT-4V, Claude 3.5 Sonnet):
- These AIs can view images directly, so OCR text is unnecessary
- Example: `python extract.py --pdf paper.pdf --no-ocr`

**Do NOT use `--no-ocr` when your AI is text-only** (e.g., GPT-3.5, Claude 3 Opus):
- These AIs need OCR text to understand image content
- You must install Tesseract OCR instead

### Behavior Table

| --no-ocr | Tesseract Installed | AI Type | Result |
|----------|-------------------|---------|--------|
| ❌ No | ✅ Yes | Text-only AI | OCR runs normally |
| ❌ No | ❌ No | Text-only AI | **Error + Warning (see below)** |
| ✅ Yes | Any | Image-input AI | OCR skipped, no error |
| ❌ No | ❌ No | Image-input AI | **Use `--no-ocr`** |

### Error + Warning (Tesseract not installed + no --no-ocr)

```
[ERROR] Tesseract OCR is not installed, but --no-ocr was not specified.

If your AI supports image input (e.g., GPT-4V, Claude 3.5 Sonnet):
    → Use --no-ocr flag (AI can view images directly, no OCR needed)
    Example: python extract.py --pdf file.pdf --no-ocr

If your AI is text-only (e.g., GPT-3.5, Claude 3 Opus):
    → Install Tesseract for OCR:
    1. Download: https://github.com/UB-Mannheim/tesseract/wiki
    2. Install to: C:\Program Files\Tesseract-OCR
    3. Add to PATH: C:\Program Files\Tesseract-OCR
```

### AI Decision Guide

1. **You support image input (e.g., GPT-4V, Claude 3.5 Sonnet)**: 
   - Use `--no-ocr` to skip OCR
   - You can view images directly, no OCR text needed
2. **You only process text (e.g., GPT-3.5, Claude 3 Opus)**: 
   - Ensure Tesseract is installed before running
   - You need OCR text to understand image content
3. **Tesseract not installed**: 
   - If you support images: Use `--no-ocr`
   - If you're text-only: Install Tesseract first

### Windows Tesseract Installation

1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer, check "Add to PATH" option
3. Verify: `tesseract --version`

## Heading Level Detection

| Pattern | Level | Example |
|---------|-------|---------|
| `I.`, `1.` + text | 2 | "1. Introduction" |
| `1.1.` + text | 3 | "1.1. Methodology" |
| `1.1.1.` + text | 4 | "1.1.1. Data Collection" |
| `a.`, `(1)` + text | 4 | "a. First item" |
| No pattern detected | 4 | Regular paragraph |

## AI Organization Guidelines

When AI processes the extracted Markdown output, it must:

1. **Group content by heading levels**: Combine all paragraphs under the same heading (##, ###, ####)
2. **Preserve hierarchy**: Keep the original heading structure intact
3. **Summarize each section**: Provide a concise summary for each section (##) and subsection (###, ####)
4. **Link figures/tables**: When referencing Figure X or Table X, include the image or table content
5. **Remove redundancy**: Merge related content and eliminate duplicate information

## Output Format (stdout)

### When OCR is enabled (text-only AI)
```markdown
--- Page 1 ---

## 1. Introduction

### 1.1 Background

![Figure 1](images/figure_1_1.png)
**[OCR]** This graph shows the comparison between...

**Table 1: Results**
| Method | Accuracy |
|--------|----------|
| A      | 95%      |

--- Page 2 ---

...
```

### When OCR is disabled (AI supports image input, using `--no-ocr`)
```markdown
--- Page 1 ---

## 1. Introduction

### 1.1 Background

![Figure 1](images/figure_1_1.png)
(AI can view this image directly, no OCR text needed)

**Table 1: Results**
...

--- Page 2 ---

...
```

If OCR is disabled or unavailable:
```markdown
--- Page 1 ---

## 1. Introduction

![Figure 1](images/figure_1_1.png)

**Table 1: Results**
...
```

## Script Usage

### Install Dependencies

```bash
pip install pypdf pypdf-table-extraction pytesseract Pillow
```

### Run Extraction

**For image-input AIs (e.g., GPT-4V, Claude 3.5 Sonnet) - Use `--no-ocr`:**
```bash
python scripts/extract.py --pdf <pdf_path> --no-ocr --output-dir <output_dir>
```

**For text-only AIs (e.g., GPT-3.5, Claude 3 Opus) - OCR enabled by default:**
```bash
# Requires Tesseract installed
python scripts/extract.py --pdf <pdf_path> [--output-dir <output_dir>]
```

Required parameters:
- `--pdf`: PDF file path

Optional parameters:
- `--output-dir`: Output directory (default: uses PDF filename)
- `--no-ocr`: **ONLY use when your AI supports image input** (AI can view images directly)

Outputs:
- Markdown content to stdout (redirect to file)
- `images/` - Image folder with extracted figures (with OCR text if enabled, or without if `--no-ocr`)

### Save AI-Organized Notes

```bash
python scripts/save_notes.py --content "<AI_organized_markdown>" --output-dir <output_dir>
```

Required parameters:
- `--content`: AI-organized notes content in Markdown format
- `--output-dir`: Output directory

Output:
- `notes.md` - Final structured notes (saved in the same directory as images)
