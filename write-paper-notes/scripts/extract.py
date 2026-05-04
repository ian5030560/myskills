#!/usr/bin/env python3
"""
Paper Notes Extractor - Extract content from PDF papers and generate structured Markdown notes

Uses pymupdf4llm with built-in RapidOCR for automatic text, image, and table extraction.

Usage:
    python scripts/extract.py --pdf <pdf_path> --output-dir <output_dir>

Dependencies:
    pip install pymupdf4llm rapidocr-onnxruntime
"""

import argparse
import sys
from pathlib import Path

import pymupdf
import pymupdf4llm
from pymupdf4llm.ocr import rapidocr_api

def extract_pdf(pdf_path: str, output_dir: Path, use_ocr: bool = True,
               ocr_language: str = "eng") -> str:
    """
    Extract PDF content to Markdown using pymupdf4llm with built-in RapidOCR.

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

    ocr_function = rapidocr_api.exec_ocr if use_ocr else None

    pdf_markdown = pymupdf4llm.to_markdown(
        pdf_path,
        ocr_function=ocr_function,
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
    use_ocr = not args.no_ocr

    if not input_path.exists():
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else Path.cwd() / input_path.stem
    output_dir.mkdir(exist_ok=True, parents=True)

    output = extract_pdf(str(input_path), output_dir, use_ocr=use_ocr)

    print(output, flush=True)


if __name__ == "__main__":
    main()
