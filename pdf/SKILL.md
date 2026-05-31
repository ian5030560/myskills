---
name: pdf
version: 2.0.0
description: "Complete PDF lifecycle toolkit: extract text/images with OCR, merge/split/rotate pages, manage metadata, and encrypt/decrypt. All powered by PyMuPDF."

metadata:
  starchild:
    emoji: "📄"
    skillKey: pdf
    requires:
      env: []
      bins: [python]
    install:
      - kind: system
        package: tesseract-ocr

user-invocable: true
---

Extract, manipulate, and secure PDFs using PyMuPDF (fitz) with built-in Tesseract OCR.

**Five tools** cover the full PDF lifecycle:

| Tool | Category | Description |
|------|----------|-------------|
| `pdf_text_extractor.py` | **Extraction** | Text only (plain text). No images, no OCR. |
| `pdf_images_extractor.py` | **Extraction** | Images with optional OCR. No text formatting. |
| `pdf_table_extractor.py` | **Extraction** | Table detection and Markdown conversion. |
| `pdf_manager.py` | **Manipulation** | Merge, split, rotate pages, and manage metadata. |
| `pdf_security.py` | **Security** | Encrypt with AES-256 or decrypt PDFs. |

## Dependencies

```bash
pip install PyMuPDF
```

Tesseract system installation (required for OCR):

| OS | Install Command |
|----|----------------|
| **Windows** | `winget install -e --id UB-Mannheim.TesseractOCR` |
| **macOS** | `brew install tesseract` |
| **Ubuntu/Debian** | `sudo apt-get install tesseract-ocr` |

Verify installation: `tesseract --version`

## Tool 1: pdf_text_extractor.py

Extract PDF content as plain text without images or OCR.

### Usage
```bash
python pdf/scripts/pdf_text_extractor.py --pdf <path> [--output-dir <dir>]
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--pdf` | Yes | — | Input PDF file path |
| `--output-dir` | No | Current dir | Parent directory for output; creates `<pdf_stem>/` subfolder |


### Output

- **File**: `<output-dir>/<pdf_stem>/output.md`
- **Behavior**: No images written, no `![Image]` placeholders in output

## Tool 2: pdf_images_extractor.py

Extract embedded images from PDF with optional OCR using PyMuPDF's Tesseract integration.

### Usage

**Extract images with OCR (default):**
```bash
python pdf/scripts/pdf_images_extractor.py --pdf <path> [--output-dir <dir>]
```

**Extract images only (no OCR):**
```bash
python pdf/scripts/pdf_images_extractor.py --pdf <path> --no-ocr [--output-dir <dir>]
```

**Print OCR results to screen instead of saving:**
```bash
python pdf/scripts/pdf_images_extractor.py --pdf <path> --ocr-output stdout
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--pdf` | Yes | — | Input PDF file path |
| `--output-dir` | No | Current dir | Parent directory for output; creates `<pdf_stem>/` subfolder |
| `--lang` | No | `eng` | OCR language code |
| `--no-ocr` | No | — | Disable OCR; extract images only |
| `--ocr-output` | No | `file` | OCR output destination: `file` (save as `.txt`) or `stdout` (print to screen) |

### Output

- **Images**: `<output-dir>/<pdf_stem>/{pdf_stem}_{page:04d}_{idx:02d}.{ext}`
- **OCR text** (when `--ocr-output file`): `<output-dir>/<pdf_stem>/{pdf_stem}_{page:04d}_{idx:02d}.txt`
- No page chunking — flat extraction of all embedded images

## Tool 3: pdf_manager.py

Manipulate PDF structure: merge, split, rotate pages, and read/write metadata. All operations use PyMuPDF's native page-level APIs for maximum performance.

### Subcommands

#### merge — Combine multiple PDFs into one

```bash
python pdf/scripts/pdf_manager.py merge --inputs a.pdf b.pdf c.pdf -o combined.pdf
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--inputs` | Yes | Space-separated list of input PDF files |
| `--output` / `-o` | Yes | Output PDF file path |

#### split — Extract page ranges into separate files

```bash
# Split specific ranges
python pdf/scripts/pdf_manager.py split --pdf input.pdf --ranges "1-3,5,7-9"
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--pdf` | Yes | — | Input PDF file |
| `--ranges` | Yes | — | Page ranges, e.g. `"1-3,5,7-9"` |
| `--output-dir` | No | Current dir | Output directory |

**Output**: Files named `<pdf_stem>_<start>-<end>.pdf`.

#### rotate — Rotate specific pages

```bash
# Rotate pages 1, 3, 5 by 90 degrees clockwise
python pdf/scripts/pdf_manager.py rotate --pdf input.pdf --pages 1,3,5 --angle 90
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--pdf` | Yes | — | Input PDF file |
| `--pages` | No | All pages | Page numbers to rotate, e.g. `"1,3,5"` |
| `--angle` | Yes | — | Rotation angle: `0`, `90`, `180`, or `270` |
| `--output` / `-o` | No | Overwrite input | Output file path |

#### metadata — Read or write PDF metadata

```bash
# Read metadata
python pdf/scripts/pdf_manager.py metadata --pdf input.pdf --get

# Write metadata
python pdf/scripts/pdf_manager.py metadata --pdf input.pdf --set "title=My Document" "author=Me"
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--pdf` | Yes | — | Input PDF file |
| `--get` | No | — | Print all metadata fields (title, author, subject, etc.) |
| `--set` | No | — | Set metadata as `key=value` pairs, e.g. `"title=New Title"` |
| `--output` / `-o` | No | Overwrite input | Output file path |

## Tool 4: pdf_security.py

Encrypt or decrypt PDFs using PyMuPDF's built-in AES-256 encryption. Supports granular permission control for user access.

### Subcommands

#### encrypt — Apply password protection

```bash
# Basic encryption
python pdf/scripts/pdf_security.py encrypt --pdf input.pdf --user-pw secret123

# With owner password and restricted permissions
python pdf/scripts/pdf_security.py encrypt --pdf input.pdf --user-pw user123 --owner-pw admin456 --permit print copy
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--pdf` | Yes | — | Input PDF file |
| `--user-pw` | No | — | User password (required to open) |
| `--owner-pw` | No | — | Owner password (full access) |
| `--output` / `-o` | No | Overwrite input | Output file path |
| `--permit` | No | None | User permissions: `print`, `modify`, `copy`, `annotate`, `forms`, `extract`, `assemble`, `print-hq` |

#### decrypt — Remove password protection

```bash
python pdf/scripts/pdf_security.py decrypt --pdf encrypted.pdf --password admin456
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--pdf` | Yes | — | Input PDF file |
| `--password` | No | — | Owner password to unlock |
| `--output` / `-o` | No | Overwrite input | Output file path |

## Tool 5: pdf_table_extractor.py

Detect and extract tables from PDF pages as structured Markdown tables using PyMuPDF's built-in `find_tables()` engine.

### Usage

```bash
python pdf/scripts/pdf_table_extractor.py --pdf <path> [--output-dir <dir>]
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--pdf` | Yes | — | Input PDF file path |
| `--output-dir` | No | Current dir | Parent directory for output; creates `<pdf_stem>/` subfolder |

### Output

- **File**: `<output-dir>/<pdf_stem>/tables.md`
- **Structure**: Each detected table is prefixed with `## Page X — Table Y`, followed by a GFM-formatted Markdown table
- **Empty PDF**: Produces a file containing only the `# Extracted Tables` header

## How It Works

- **Text**: `pdf_text_extractor.py` uses `fitz.Page.get_text()` for plain text extraction
- **Images**: Via `fitz.Page.get_images()` — original embedded format (JPEG/PNG), no re-encoding
- **OCR**: `fitz.Pixmap.pdfocr_tobytes()` — native PyMuPDF Tesseract integration
- **Tables**: `pdf_table_extractor.py` uses `page.find_tables().extract()` — native PyMuPDF table detection with automated Markdown formatting.
- **Merge**: `fitz.open().insert_pdf()` — zero-copy page insertion for high-speed merging
- **Split**: `fitz.open().insert_pdf(src, from_page=..., to_page=...)` — exact page-range extraction
- **Rotate**: `page.set_rotation()` — native page-level rotation without re-encoding
- **Metadata**: `doc.metadata` / `doc.set_metadata()` — direct dict access to PDF info fields
- **Encrypt**: `doc.save(encryption=fitz.PDFEncryption.ENCRYPT_AES_256, user_pw=..., owner_pw=...)` — built-in AES-256 encryption
- **Decrypt**: `doc.authenticate()` + `doc.save()` — strip encryption after authentication
