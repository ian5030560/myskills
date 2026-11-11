#!/usr/bin/env python3
"""Render every page of a PDF to <output-dir>/<stem>/pages/pN.png.

Each page image carries a faint grid at tenths of the page width and height,
labelled .1-.9 on the top and left edges, so the AI can read off a crop box in
0-1 page fractions. A source.json manifest records the PDF's absolute path so
the crop script needs only a page image to find the PDF again.
"""

import json
from pathlib import Path

import fitz

from extract_text import parse_pdf_cli

DPI = 110
GRID_COLOR = (1, 0, 0)
GRID_OPACITY = 0.2
GRID_WIDTH = 0.4
LABEL_SIZE = 6


def _draw_grid(page: fitz.Page):
    width, height = page.rect.width, page.rect.height
    shape = page.new_shape()
    for k in range(1, 10):
        shape.draw_line((width * k / 10, 0), (width * k / 10, height))
        shape.draw_line((0, height * k / 10), (width, height * k / 10))
    shape.finish(color=GRID_COLOR, width=GRID_WIDTH, stroke_opacity=GRID_OPACITY)
    shape.commit()
    for k in range(1, 10):
        page.insert_text((width * k / 10 + 1, LABEL_SIZE + 2), f".{k}",
                         fontsize=LABEL_SIZE, color=GRID_COLOR)
        page.insert_text((1, height * k / 10 - 1), f".{k}",
                         fontsize=LABEL_SIZE, color=GRID_COLOR)


def render(pdf_path: Path, pages_dir: Path) -> int:
    """Render all pages into pages_dir; returns the page count. The PDF on disk is untouched."""
    pages_dir.mkdir(parents=True, exist_ok=True)
    with fitz.open(pdf_path) as doc:
        for number, page in enumerate(doc, start=1):
            _draw_grid(page)
            page.get_pixmap(dpi=DPI).save(str(pages_dir / f"p{number}.png"))
        count = doc.page_count
    manifest = {"pdf": str(pdf_path.resolve())}
    (pages_dir / "source.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
    return count


def main():
    input_path, out_dir = parse_pdf_cli("Render PDF pages to gridded page images")
    pages_dir = out_dir / "pages"
    count = render(input_path, pages_dir)
    print(f"pages dir: {pages_dir}")
    print(f"pages: {count}")


if __name__ == "__main__":
    main()
