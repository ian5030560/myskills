#!/usr/bin/env python3
"""
Paper Notes Extractor - Extract content from PDF papers and generate structured Markdown notes

Uses pymupdf4llm with built-in Tesseract OCR for automatic text and table extraction.
Images are extracted directly via PyMuPDF (fitz.Page.get_images) for reliable results,
with optional OCR of image content.

Usage:
    python scripts/extract.py --pdf <pdf_path> --output-dir <output_dir>

Dependencies:
    pip install pymupdf4llm
"""

import argparse
import sys
from pathlib import Path

import fitz
import pymupdf4llm
from pymupdf4llm.ocr import tesseract_api


def extract_pdf(pdf_path: str, output_dir: Path, use_ocr: bool = True,
                ocr_language: str = "eng") -> str:
    output_dir.mkdir(exist_ok=True, parents=True)
    image_dir = output_dir / "images"
    image_dir.mkdir(exist_ok=True, parents=True)

    ocr_function = tesseract_api.exec_ocr if use_ocr else None

    page_chunks = pymupdf4llm.to_markdown(
        pdf_path,
        ocr_function=ocr_function,
        ocr_language=ocr_language,
        page_chunks=True,
        force_text=True,
    )

    with fitz.open(pdf_path) as doc:
        pdf_stem = Path(pdf_path).stem

        full_md_pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_md = page_chunks[page_num]["text"] if page_num < len(page_chunks) else ""

            images = page.get_images(full=True)
            for img_idx, img in enumerate(images):
                xref = img[0]
                base = doc.extract_image(xref)
                img_bytes = base["image"]
                ext = base["ext"] or "png"

                img_filename = f"{pdf_stem}_{page_num+1:04d}_{img_idx+1:02d}.{ext}"
                (image_dir / img_filename).write_bytes(img_bytes)

                page_md += f"\n![Image](images/{img_filename})\n"

                if use_ocr:
                    img_doc = fitz.open(stream=img_bytes, filetype=ext)
                    pix = img_doc[0].get_pixmap()
                    img_doc.close()
                    ocr_pdf_bytes = pix.pdfocr_tobytes(language=ocr_language)
                    ocr_pdf = fitz.open("pdf", ocr_pdf_bytes)
                    ocr_text = ocr_pdf[0].get_text()
                    ocr_pdf.close()
                    if ocr_text and ocr_text.strip():
                        page_md += ocr_text.strip() + "\n"

            full_md_pages.append(page_md)

    return "\n\n".join(full_md_pages)


def main():
    parser = argparse.ArgumentParser(
        description="Extract content from PDF papers using pymupdf4llm")
    parser.add_argument("--pdf", required=True,
                        help="Input PDF file path")
    parser.add_argument("--output-dir", required=False,
                        help="Parent directory for output (default: current dir; creates <pdf_stem> subfolder)")
    parser.add_argument("--no-ocr", action="store_true",
                       help="Disable OCR (for AI with image input capability)")
    args = parser.parse_args()

    input_path = Path(args.pdf)

    use_ocr = not args.no_ocr

    if not input_path.exists():
        sys.exit(1)

    base_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    output_dir = base_dir / input_path.stem
    output_dir.mkdir(exist_ok=True, parents=True)

    output = extract_pdf(str(input_path), output_dir, use_ocr=use_ocr)

    print(output, flush=True)


if __name__ == "__main__":
    main()
