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


def _extract_all_images(doc, image_dir: Path) -> int:
    """Extract ALL images from PDF using pymupdf directly"""
    image_count = 0
    for page_num, page in enumerate(doc):
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # Save with unique name: pageNum_imgIndex.ext
            img_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
            img_path = image_dir / img_filename

            # Skip if already exists (avoid duplicates)
            if not img_path.exists():
                with open(img_path, "wb") as img_file:
                    img_file.write(image_bytes)
                image_count += 1

    return image_count


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
        Markdown string with page separators
    """
    output_dir.mkdir(exist_ok=True, parents=True)
    image_dir = output_dir / "images"
    image_dir.mkdir(exist_ok=True, parents=True)

    # Extract ALL images from PDF (supplementary to pymupdf4llm)
    with pymupdf.open(pdf_path) as doc:
        image_count = _extract_all_images(doc, image_dir)
        if image_count > 0:
            print(f"[INFO] Extracted {image_count} images to {image_dir}")

    # Use page_chunks=True to get structured output per page
    page_chunks = pymupdf4llm.to_markdown(
        pdf_path,
        page_chunks=True,
        use_ocr=use_ocr,
        ocr_language=ocr_language,
        image_path=str(image_dir),
        write_images=True,
    )

    # Extract text from each page chunk and add custom page header
    md_pages = [
        f"--- Page {chunk['metadata']['page_number']} ---\n{chunk['text'].strip()}"
        for chunk in page_chunks
    ]

    return "\n\n".join(md_pages)


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
