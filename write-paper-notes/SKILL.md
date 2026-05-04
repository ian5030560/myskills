---
name: write-paper-notes
version: 1.0.0
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
        package: pymupdf4llm
      - kind: pip
        package: rapidocr-onnxruntime

user-invocable: true
---

Extract text, images, and tables from PDF academic papers and generate structured Markdown notes using pymupdf4llm with built-in Tesseract OCR.

**OCR Default**: Enabled (for text-only AIs that cannot view images)
**When to use `--no-ocr`**: ONLY when your AI supports image input (e.g., GPT-4V, Claude 3.5 Sonnet)

## Processing Flow

| Step | Action |
|------|--------|
| 0 | Install dependencies: `pip install pymupdf4llm` |
| 0.1 | Install RapidOCR: `pip install rapidocr-onnxruntime` |
| 1 | **If your AI supports image input (e.g., GPT-4V)**: Run with `--no-ocr` |
|   | `python scripts/extract.py --pdf <pdf> --no-ocr --output-dir <dir>` |
|   | **If your AI is text-only**: Run without `--no-ocr` (requires RapidOCR) |
|   | `python scripts/extract.py --pdf <pdf> [--output-dir <dir>]` (output to stdout) |
| 2 | **REQUIRED**: AI MUST reorganize content into `notes.md` (see **Organized Notes Example** below) |
| 3 | AI saves organized notes to `notes.md` in the output directory |

## OCR Configuration

**Default behavior**: OCR enabled via pymupdf4llm's built-in RapidOCR plugin (for text-only AIs)

**Smart OCR**: pymupdf4llm automatically detects pages needing OCR and only processes those regions (Hybrid OCR strategy)

### When to use `--no-ocr`

**ONLY use `--no-ocr` when your AI supports image input** (e.g., GPT-4V, Claude 3.5 Sonnet):
- These AIs can view images directly, so OCR text is unnecessary
- Example: `python extract.py --pdf paper.pdf --no-ocr`

**Do NOT use `--no-ocr` when your AI is text-only** (e.g., GPT-3.5, Claude 3 Opus):
- These AIs need OCR text to understand image content
- RapidOCR is a Python package, no system install needed

### Behavior Table

| --no-ocr | RapidOCR Installed | AI Type | Result |
|----------|---------------------|---------|--------|
| ❌ No | ✅ Yes | Text-only AI | OCR runs via pymupdf4llm RapidOCR plugin |
| ❌ No | ❌ No | Text-only AI | **Warning + Continue (OCR skipped)** |
| ✅ Yes | Any | Image-input AI | OCR disabled, no error |
| ❌ No | ❌ No | Image-input AI | **Use `--no-ocr`** |

### Warning (RapidOCR not installed + no --no-ocr)

```
[WARNING] RapidOCR is not installed. Install with: pip install rapidocr-onnxruntime

If your AI supports image input (e.g., GPT-4V, Claude 3.5 Sonnet):
    → Use --no-ocr flag (AI can view images directly, no OCR needed)
    Example: python extract.py --pdf file.pdf --no-ocr

If your AI is text-only (e.g., GPT-3.5, Claude 3 Opus):
    → Install RapidOCR: pip install rapidocr-onnxruntime

Continuing without OCR (images will be extracted without OCR text)...
```

### AI Decision Guide

1. **You support image input (e.g., GPT-4V, Claude 3.5 Sonnet)**:
   - Use `--no-ocr` to skip OCR
   - You can view images directly, no OCR text needed
2. **You only process text (e.g., GPT-3.5, Claude 3 Opus)**:
   - Install RapidOCR: `pip install rapidocr-onnxruntime`
   - You need OCR text to understand image content
3. **RapidOCR not installed**:
   - If you support images: Use `--no-ocr`
   - If you're text-only: Install RapidOCR first

## Heading Detection

Headings are automatically detected by pymupdf4llm based on font size hierarchy:
- Larger fonts → Higher heading levels (##, ###, ####)
- No manual pattern matching required

## AI Organization Guidelines

When AI processes the extracted Markdown output, it must:

1. **Group content by heading levels**: Combine all paragraphs under the same heading (##, ###, ####)
2. **Preserve hierarchy**: Keep the original heading structure intact
3. **Preserve ALL images**: Keep every `![...](images/...)` markdown EXACTLY as-is, never delete or skip images
4. **Restructure content, don't just copy**: Transform original content into structured notes:
   - Extract key points → present as bullet/numbered lists
   - Organize comparative data → use tables (only when referencing Table X)
   - **Flexible element ordering**: Except images (which stay fixed), rearrange text, lists, and tables based on content logic
5. **Add summaries**: Add concise summaries for each section (##) and subsection (###, ####) ABOVE the content
6. **Remove redundancy**: Merge related text only, never remove images

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

![Figure 1: Comparison of RNN vs Transformer](images/figure_1_1.png)

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

![Figure 2: Transformer Architecture](images/figure_2_1.png)

**Encoder (6 layers):**
- Multi-head self-attention (h=8 heads, d_k=64)
- Position-wise feed-forward (d_ff=2048)
- Residual connection + layer normalization

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
- ALL images preserved exactly as extracted (`![...](images/...)`)
- Content is **restructured, not copied**: use bullet points, lists, tables
- **Flexible ordering**: Except images, rearrange text/lists/tables based on content logic
- Group content by headings, not page numbers
- Tables included only when referenced (not all tables preserved)

## Output Format (stdout)

### When OCR is enabled (text-only AI)
```markdown
## 1. Introduction

### 1.1 Background

![Figure 1](images/figure_1_1.png)

| Method | Accuracy |
|--------|----------|
| A      | 95%      |

## 2. Related Work
...
```

### When OCR is disabled (AI supports image input, using `--no-ocr`)
```markdown
## 1. Introduction

### 1.1 Background

![Figure 1](images/figure_1_1.png)
(AI can view this image directly, no OCR text needed)

**Table 1: Results**
...

## 2. Related Work
...
```

If OCR is disabled or unavailable:
```markdown
## 1. Introduction

![Figure 1](images/figure_1_1.png)

**Table 1: Results**
...

## 2. Related Work
...
```

### When OCR is disabled (AI supports image input, using `--no-ocr`)
```markdown
## 1. Introduction

### 1.1 Background

![Figure 1](images/figure_1_1.png)
(AI can view this image directly, no OCR text needed)

**Table 1: Results**
...

## 2. Related Work
...
```

If OCR is disabled or unavailable:
```markdown
## 1. Introduction

![Figure 1](images/figure_1_1.png)

**Table 1: Results**
...

## 2. Related Work
...
```

If OCR is disabled or unavailable:
```markdown
## 1. Introduction

![Figure 1](images/figure_1_1.png)

**Table 1: Results**
...

## 2. Related Work
...
```

## How It Works

pymupdf4llm handles all extraction automatically:
- **Text & Headings**: Font-size based detection, no regex patterns needed
- **Images**: Automatic extraction with smask handling (no black backgrounds)
- **Tables**: Automatic detection with GitHub-Flavored Markdown output
- **OCR**: Built-in RapidOCR plugin, smart hybrid strategy (only OCR regions that need it)

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
# Requires: pip install rapidocr-onnxruntime
python scripts/extract.py --pdf <pdf_path> [--output-dir <output_dir>]
```

Required parameters:
- `--pdf`: PDF file path

Optional parameters:
- `--output-dir`: Output directory (default: uses PDF filename)
- `--no-ocr`: **ONLY use when your AI supports image input** (AI can view images directly)

Outputs:
- Markdown content to stdout (redirect to file)
- `images/` - Image folder with extracted figures

### Save AI-Organized Notes

After organizing the content per **AI Organization Guidelines**, save the notes to `notes.md` in the output directory.
