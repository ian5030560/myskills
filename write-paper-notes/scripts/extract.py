#!/usr/bin/env python3
"""CLI entry point for paper notes extraction."""

import argparse
import sys
from pathlib import Path

from extract_docx import DocxExtractor
from extract_pdf import PdfExtractor


def main():
    parser = argparse.ArgumentParser(
        description="Extract content from PDF papers or DOCX documents")
    parser.add_argument("--input", required=True,
                        help="Input file path (.pdf or .docx)")
    parser.add_argument("--output-dir", required=False,
                        help="Parent directory for output "
                             "(default: current dir; creates <stem> subfolder)")
    parser.add_argument("--no-ocr", action="store_true",
                        help="Disable OCR (for AI with image input capability)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        extractor_cls = PdfExtractor
    elif suffix == ".docx":
        extractor_cls = DocxExtractor
    else:
        print(f"Error: unsupported format: {suffix}", file=sys.stderr)
        sys.exit(1)

    base_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    output_dir = base_dir / input_path.stem

    extractor = extractor_cls(str(input_path), output_dir, use_ocr=not args.no_ocr)
    output = extractor.extract()

    print(output, flush=True)


if __name__ == "__main__":
    main()
