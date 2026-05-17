---
name: write-paper-notes
version: 1.1.0
description: "Extract content from PDF papers and generate structured Markdown notes. Default: OCR enabled for text-only AIs. Use --no-ocr for image-input AIs."

metadata:
  starchild:
    emoji: "📄"
    skillKey: write-paper-notes
    requires:
      env: []
      bins: [python]
    install:
      - kind: system
        package: tesseract-ocr

user-invocable: true
---

Extract text, images, and tables from PDF academic papers and generate structured Markdown notes using pymupdf4llm with built-in Tesseract OCR.

**OCR Default**: Enabled (for text-only AIs that cannot view images)
**When to use `--no-ocr`**: ONLY when your AI supports image input (e.g., GPT-4V, Claude 3.5 Sonnet)

## Processing Flow

| Step | Action |
|------|--------|
| 0 | Install dependencies: `pip install pymupdf4llm` |
| 0.1 | Install Tesseract system-wide (see OS-specific commands below) |
| 1 | **Extraction**: Run the extraction script.<br>- **Image-input AI**: Use `--no-ocr` → `python scripts/extract.py --pdf <pdf> --no-ocr --output-dir <dir>`<br>- **Text-only AI**: Use default (requires Tesseract) → `python scripts/extract.py --pdf <pdf> [--output-dir <dir>]` |
| 2 | **Content Analysis**:<br>- **Image-input AI**: Examine and describe each extracted image in `images/` folder<br>- **Text-only AI**: Use provided OCR text to understand image content |
| 3 | **Organization**: **REQUIRED**: AI MUST reorganize content into `notes.md` (see **Organized Notes Example** below) |
| 4 | AI saves organized notes to `notes.md` in the output directory |

## OCR Configuration

**Default behavior**: OCR enabled via pymupdf4llm's built-in Tesseract plugin (for text-only AIs)

**Smart OCR**: pymupdf4llm automatically detects pages needing OCR and only processes those regions (Hybrid OCR strategy)

### When to use `--no-ocr`

**ONLY use `--no-ocr` when your AI supports image input** (e.g., GPT-4V, Claude 3.5 Sonnet):
- These AIs can view images directly, so OCR text is unnecessary
- Example: `python extract.py --pdf paper.pdf --no-ocr`

**Do NOT use `--no-ocr` when your AI is text-only** (e.g., GPT-3.5, Claude 3 Opus):
- These AIs need OCR text to understand image content
- Tesseract must be installed system-wide

### Dependencies

**System Tesseract installation (required):**

| OS | Install Command |
|----|----------------|
| **Windows** | `winget install -e --id UB-Mannheim.TesseractOCR` |
| **macOS** | `brew install tesseract` |
| **Ubuntu/Debian** | `sudo apt-get install tesseract-ocr` |
| **Fedora** | `sudo dnf install tesseract` |
| **Arch Linux** | `sudo pacman -S tesseract` |

Verify installation: `tesseract --version`

### Behavior Table

| --no-ocr | Tesseract Installed | AI Type | Result |
|----------|---------------------|---------|--------|
| ❌ No | ✅ Yes | Text-only AI | OCR runs via pymupdf4llm Tesseract plugin |
| ❌ No | ❌ No | Text-only AI | **Error: Tesseract not installed** |
| ✅ Yes | Any | Image-input AI | OCR disabled, no error |

## Heading Detection

Headings are automatically detected by pymupdf4llm based on font size hierarchy:
- Larger fonts → Higher heading levels (##, ###, ####)
- No manual pattern matching required

## AI Organization Guidelines

When AI processes the extracted Markdown output, it must:

1. **Group content by heading levels**: Combine all paragraphs under the same heading (##, ###, ####)
2. **Preserve hierarchy**: Keep the original heading structure intact
3. **Insert images into appropriate sections**: Move `![Image](images/...)` references from page-end grouping into the subsection they belong to, based on OCR context and paper content
4. **Improve image alt text**: Use the image analysis from Step 2 to replace generic `Image` alt text with a precise descriptive phrase (e.g., `![Transformer architecture]`)
5. **OCR text is for AI reference only**: Read OCR text after each image to understand its content, but do NOT copy raw OCR output into notes.md
6. **Restructure content, don't just copy**: Transform original content into structured notes:
   - Extract key points → present as bullet/numbered lists
   - Organize comparative data → use tables (only when referencing Table X)
   - **Flexible element ordering**: Rearrange text, lists, tables, and images based on content logic
7. **Add summaries**: Add concise summaries for each section (##) and subsection (###, ####) ABOVE the content
8. **Remove redundancy**: Merge related text only, never remove images

## Organized Notes Example

After processing the extracted Markdown, `notes.md` should look like this:

```markdown
# Paper Title: Attention Is All You Need

## Summary
This paper introduces the Transformer architecture, replacing recurrent layers with attention mechanisms. Achieves parallelization and superior translation performance.

## 1. Introduction

### Summary
Recurrent models are sequential and hard to parallelize. Transformers solve this with attention-only architecture.

**Limitations of RNNs/LSTMs:**
- Sequential computation prevents parallelization
- Long-range dependencies are hard to learn
- Hidden state becomes information bottleneck

**Transformer advantages:**
- No recurrence → fully parallelizable
- Attention mechanism captures global dependencies directly
- Superior performance on WMT 2014 translation task

![Transformer vs RNN architecture comparison](images/paper_0001_01.png)

## 2. Related Work

### Summary
Previous approaches: CNNs (limited receptive field), RNNs (sequential), attention-based (still use RNN).

**Model comparison:**
| Approach | Parallelization | Long-range Dependencies | Limitations |
|----------|----------------|------------------------|-------------|
| RNN/LSTM | Low | Hard | Sequential, bottleneck |
| CNN | Medium | Limited | Receptive field size |
| Transformer | High | Direct | New architecture |

## 3. Model Architecture

### Summary
Encoder-decoder with multi-head self-attention, position-wise FFN, and residual connections.

**Encoder (6 layers):**
- Multi-head self-attention (h=8 heads, d_k=64)
- Position-wise feed-forward (d_ff=2048)
- Residual connection + layer normalization

![Transformer architecture with encoder-decoder stacks](images/paper_0003_01.png)

**Decoder (6 layers):**
- Masked multi-head self-attention (prevents future attending)
- Encoder-decoder attention
- Position-wise feed-forward network

**Key hyperparameters:**
| Parameter | Value | Description |
|-----------|-------|-------------|
| N (layers) | 6 | Encoder/decoder depth |
| d_model | 512 | Model dimension |
| d_ff | 2048 | Feed-forward inner dimension |
| h (heads) | 8 | Attention heads |
| d_k, d_v | 64 | Key/value dimensions |
```

**Key principles:**
- Summaries are added ABOVE each section/subsection
- **OCR text is for AI reference only** — read it to understand images, do NOT include in output
- Images are placed **within the relevant subsection**, not page-bottom grouping
- Alt text is improved from generic `Image` to descriptive text
- Content is **restructured, not copied**: use bullet points, lists, tables
- **Flexible ordering**: rearrange text, lists, tables, and images based on content logic
- Group content by headings, not page numbers
- Tables included only when referenced (not all tables preserved)

## Output Format (stdout)

### Raw extraction output
Images appear grouped at the end of each page's text, followed by OCR text (when enabled):

```markdown
## 1. Introduction

### 1.1 Background
Text from pymupdf4llm...

| Method | Accuracy |
|--------|----------|
| A      | 95%      |

![Image](images/paper_0001_01.png)
OCR reference text for AI only — not included in notes.md

![Image](images/paper_0001_02.png)
More OCR context for understanding image placement
```

## How It Works

pymupdf4llm handles text, heading, and table extraction.
Images are extracted directly via PyMuPDF (`fitz.Page.get_images`) for original-quality embedded images.

- **Text & Headings**: Font-size based detection
- **Images**: Extracted via `fitz.Page.get_images()` — original embedded format (JPEG/PNG), no re-encoding
- **Tables**: Automatic detection with GitHub-Flavored Markdown output
- **OCR**: Built-in Tesseract plugin for page text
- **Image OCR**: Each extracted image is OCR'd (when enabled); the OCR text is for AI reference only — AI reads it to understand image content and place it in the right section, but does NOT copy it into notes.md

## Script Usage

### Install Dependencies

```bash
pip install pymupdf4llm
```

### Windows UTF-8 Encoding (Required)

Windows console default encoding (cp950/Big5) cannot handle UTF-8 characters in PDFs. Set this before running:

**PowerShell:**
```powershell
$env:PYTHONIOENCODING="utf-8"
```

**CMD:**
```cmd
set PYTHONIOENCODING=utf-8
```

### Run Extraction

**For image-input AIs (e.g., GPT-4V, Claude 3.5 Sonnet) - Use `--no-ocr`:**
```bash
python scripts/extract.py --pdf <pdf_path> --no-ocr --output-dir <output_dir>
```

**For text-only AIs (e.g., GPT-3.5, Claude 3 Opus) - OCR enabled by default:**
```bash
# System: Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
python scripts/extract.py --pdf <pdf_path> [--output-dir <output_dir>]
```

Required parameters:
- `--pdf`: PDF file path

Optional parameters:
- `--output-dir`: Parent directory for output (default: current dir; creates `<pdf_stem>` subfolder)
- `--no-ocr`: **ONLY use when your AI supports image input** (AI can view images directly)

Outputs:
- Markdown content to stdout (redirect to file)
- `images/` - Image folder with extracted figures

### Save AI-Organized Notes

After organizing the content per **AI Organization Guidelines**, save the notes to `notes.md` in the output directory.
