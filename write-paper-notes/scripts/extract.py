#!/usr/bin/env python3
"""
Paper Notes Extractor - Extract content from PDF papers and generate structured Markdown notes

Uses pymupdf4llm for text extraction and PyMuPDF (fitz) for image and vector graphic extraction.
Optional Tesseract OCR via pdfocr_tobytes for embedded image content.

Usage:
    python scripts/extract.py --pdf <pdf_path> --output-dir <output_dir>

Dependencies:
    pip install pymupdf4llm
"""

import argparse
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import fitz
import pymupdf4llm


# ── Module-level helpers ─────────────────────────────────────────────


def ocr_image_bytes(img_bytes: bytes, ext: str, ocr_language: str = "eng") -> Optional[str]:
    """Run Tesseract OCR on a single image.

    Args:
        img_bytes: Raw image file bytes.
        ext: File extension (e.g. "png", "jpg") for fitz decoding.
        ocr_language: Tesseract language code (default "eng").

    Returns:
        OCR text string, or None if the image is too small or OCR fails.
    """
    img_doc = fitz.open(stream=img_bytes, filetype=ext)
    pix = img_doc[0].get_pixmap()
    img_doc.close()
    if pix.width < 3 or pix.height < 3:
        return None
    try:
        ocr_pdf_bytes = pix.pdfocr_tobytes(language=ocr_language)
        ocr_pdf = fitz.open("pdf", ocr_pdf_bytes)
        text = ocr_pdf[0].get_text().strip()
        ocr_pdf.close()
        return text or None
    except RuntimeError:
        return None


def _is_significant_drawing(cluster_rect, paths) -> bool:
    """Filter out trivial vector clusters (e.g. full-page underlines, single thin lines)."""
    dim = cluster_rect.width if cluster_rect.width > cluster_rect.height else cluster_rect.height
    d = dim * 0.025
    inner = cluster_rect + (d, d, -d, -d)

    my_paths = [p for p in paths if p["rect"] in cluster_rect]
    if not my_paths:
        return False

    if len(my_paths) == 1:
        pr = my_paths[0]["rect"]
        return not pr.is_empty and not (pr & inner).is_empty

    widths = set(round(p["rect"].width) for p in my_paths) | {round(cluster_rect.width)}
    heights = set(round(p["rect"].height) for p in my_paths) | {round(cluster_rect.height)}
    if len(widths) == 1 or len(heights) == 1:
        return False

    for p in my_paths:
        pr = p["rect"]
        if not (pr.is_empty or (pr & inner).is_empty):
            return True
    return False


# ── Abstract base ────────────────────────────────────────────────────


class DocumentExtractor(ABC):
    """Abstract base for document content extraction.

    Subclasses must implement load(), close(), and do_extract().
    Call extract() to run the full pipeline.
    """

    def __init__(self, file_path: str, output_dir: Path,
                 use_ocr: bool = True, ocr_language: str = "eng"):
        self.file_path = file_path
        self.output_dir = output_dir
        self.image_dir = output_dir / "images"
        self.use_ocr = use_ocr
        self.ocr_language = ocr_language

    def extract(self) -> str:
        self._setup_directories()
        self.load()
        try:
            return self.do_extract()
        finally:
            self.close()

    def _setup_directories(self):
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.image_dir.mkdir(exist_ok=True, parents=True)

    @abstractmethod
    def load(self):
        """Open the document."""

    @abstractmethod
    def close(self):
        """Close the document."""

    @abstractmethod
    def do_extract(self) -> str:
        """Extract content and return a Markdown string."""


# ── PDF implementation ───────────────────────────────────────────────


class PdfExtractor(DocumentExtractor):
    """Extract content from PDF files using PyMuPDF + pymupdf4llm."""

    def __init__(self, file_path: str, output_dir: Path,
                 use_ocr: bool = True, ocr_language: str = "eng"):
        super().__init__(file_path, output_dir, use_ocr=use_ocr, ocr_language=ocr_language)
        self._doc = None

    def load(self):
        self._doc = fitz.open(self.file_path)

    def close(self):
        if self._doc:
            self._doc.close()

    def _extract_embedded_images(self, page, page_md, pdf_stem, page_num):
        for img_idx, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base = self._doc.extract_image(xref)
            img_bytes = base["image"]
            ext = base["ext"] or "png"
            img_filename = f"{pdf_stem}_{page_num+1:04d}_{img_idx+1:02d}.{ext}"
            (self.image_dir / img_filename).write_bytes(img_bytes)
            page_md += f"\n![Image](images/{img_filename})\n"
            if self.use_ocr:
                ocr_text = ocr_image_bytes(img_bytes, ext, self.ocr_language)
                if ocr_text:
                    page_md += ocr_text + "\n"
        return page_md

    def _extract_vector_graphics(self, page, page_md, pdf_stem, page_num):
        paths = page.get_drawings()
        if not paths:
            return page_md
        page_rect = page.rect
        filtered_paths = [
            p for p in paths
            if p["rect"].width < page_rect.width * 0.95
            and p["rect"].height < page_rect.height * 0.95
            and p["rect"].width > 5
            and p["rect"].height > 5
        ]
        if not filtered_paths:
            return page_md
        clusters = page.cluster_drawings(
            drawings=filtered_paths,
            x_tolerance=20,
            y_tolerance=20,
        )
        for vg_idx, cluster_rect in enumerate(clusters):
            if _is_significant_drawing(cluster_rect, filtered_paths):
                pix = page.get_pixmap(clip=cluster_rect, dpi=150)
                img_filename = f"{pdf_stem}_{page_num+1:04d}_v{vg_idx+1:02d}.png"
                pix.save(str(self.image_dir / img_filename))
                page_md += f"\n![Vector Graphic](images/{img_filename})\n"
        return page_md

    def do_extract(self) -> str:
        pdf_stem = Path(self.file_path).stem
        page_chunks = pymupdf4llm.to_markdown(
            self.file_path,
            page_chunks=True,
            force_text=True,
            use_ocr=False,
        )
        full_md_pages = []
        for page_num, page in enumerate(self._doc):
            page_md = page_chunks[page_num]["text"] if page_num < len(page_chunks) else ""
            page_md = self._extract_embedded_images(page, page_md, pdf_stem, page_num)
            page_md = self._extract_vector_graphics(page, page_md, pdf_stem, page_num)
            full_md_pages.append(page_md)
        return "\n\n".join(full_md_pages)


# ── CLI ──────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Extract content from PDF papers using pymupdf4llm")
    parser.add_argument("--pdf", required=True,
                        help="Input PDF file path")
    parser.add_argument("--output-dir", required=False,
                        help="Parent directory for output "
                             "(default: current dir; creates <pdf_stem> subfolder)")
    parser.add_argument("--no-ocr", action="store_true",
                        help="Disable OCR (for AI with image input capability)")
    args = parser.parse_args()

    input_path = Path(args.pdf)
    use_ocr = not args.no_ocr

    if not input_path.exists():
        sys.exit(1)

    base_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    output_dir = base_dir / input_path.stem

    output = PdfExtractor(str(input_path), output_dir, use_ocr=use_ocr).extract()

    print(output, flush=True)


if __name__ == "__main__":
    main()
