#!/usr/bin/env python3
"""
Paper Notes Extractor - Extract content from PDF papers and generate structured Markdown notes

Uses pymupdf4llm with built-in Tesseract OCR for automatic text, image, and table extraction.

Usage:
    python scripts/extract.py --pdf <pdf_path> --output-dir <output_dir>

Dependencies:
    pip install pymupdf4llm
    System: Tesseract-OCR (for OCR support)
"""

import argparse
import sys
from pathlib import Path

import pymupdf
import pymupdf4llm

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def extract_pdf(pdf_path: str, output_dir: Path, use_ocr: bool = True,
               ocr_language: str = "eng") -> str:
    """
    Extract PDF content to Markdown using pymupdf4llm with built-in Tesseract OCR.

    Args:
        pdf_path: Path to input PDF file
        output_dir: Output directory for images
        use_ocr: Whether to enable OCR (default: True)
        ocr_language: OCR language code (default: "eng")

    Returns:
        Markdown string
    """
    output_dir.mkdir(exist_ok=True, parents=True)
    image_dir = output_dir / "images"
    image_dir.mkdir(exist_ok=True, parents=True)

    pdf_markdown = pymupdf4llm.to_markdown(
        pdf_path,
        use_ocr=use_ocr,
        ocr_language=ocr_language,
        image_path=str(image_dir),
        write_images=True,
    )
    
    return pdf_markdown


def main():
    parser = argparse.ArgumentParser(
        description="Extract content from PDF papers using pymupdf4llm")
    parser.add_argument("--pdf", required=True,
                        help="Input PDF file path")
    parser.add_argument("--output-dir", required=False,
                        help="Output directory (default: <pdf_filename>)")
    parser.add_argument("--no-ocr", action="store_true",
                       help="Disable OCR (for AI with image input capability)")
    args = parser.parse_args()

    input_path = Path(args.pdf)

    # Check OCR configuration
    if args.no_ocr:
        print("[INFO] OCR disabled (--no-ocr specified)")
        print("[INFO] Assumes AI can view images directly (e.g., GPT-4V, Claude 3.5 Sonnet)")
        use_ocr = False
    else:
        print("[INFO] OCR enabled (requires Tesseract OCR installed system-wide)")
        use_ocr = True

    if not input_path.exists():
        print(f"[ERROR] File not found: {input_path}")
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else Path.cwd() / input_path.stem
    output_dir.mkdir(exist_ok=True, parents=True)

    print(f"[INFO] Reading PDF: {input_path}")
    # Get page count for info
    with pymupdf.open(str(input_path)) as doc:
        print(f"[INFO] Total pages: {len(doc)}")

    print("[INFO] Extracting content...")
    output = extract_pdf(str(input_path), output_dir, use_ocr=use_ocr)

    print(output, flush=True)


if __name__ == "__main__":
    main()
