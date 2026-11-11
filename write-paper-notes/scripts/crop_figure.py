#!/usr/bin/env python3
"""Crop a figure out of a PDF page, given a page image and a generous box.

The AI looks at a page image (pages/pN.png from render_pages.py), draws a box around
the whole figure in 0-1 page fractions, and this script:

1. finds the PDF through pages/source.json and the page number through the file name;
2. trims the box inward only, peeling captions, body paragraphs, section headings and
   running headers/footers off its edges (never cutting through anything else);
3. trims white margins and thin slivers of neighbouring content;
4. re-renders the final box from the PDF at 200 dpi without the grid to
   <stem>/images/<name>.png, and prints the final box.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import fitz

from extract_text import block_text, running_blocks, running_texts, text_blocks

DPI = 200
PAD = 2                    # points kept around the trimmed content
MIN_GRAPHIC_OVERLAP = 4    # graphics overlapping the box less than this (pt) are ignored
SLIVER_HEIGHT = 5          # content runs thinner than this at the top/bottom are dropped...
SLIVER_GAP = 6             # ...when separated from the rest by at least this gap (pt)
WHITE = 240                # gray level above which a pixel counts as background
MIN_SIZE = 5               # a final box smaller than this (pt) counts as empty
BODY_SIZE_TOLERANCE = 0.6
BODY_MIN_LINE_CHARS = 40
BODY_MIN_WIDTH = 0.3
HEADING_MAX_CHARS = 80

_CAPTION_RE = re.compile(r"^\s*(figure|fig\.?|table)\s*\d", re.I)
_HEADING_RE = re.compile(r"^\d+(\.\d+)*\.?\s+\S")
_PAGE_FILE_RE = re.compile(r"^p(\d+)\.png$", re.I)


class CropError(Exception):
    pass


def _body_font_size(doc: fitz.Document) -> float:
    sizes = Counter()
    for page in doc:
        for block in text_blocks(page):
            for line in block["lines"]:
                for span in line["spans"]:
                    sizes[round(span["size"], 1)] += len(span["text"].strip())
    return sizes.most_common(1)[0][0] if sizes else 0.0


class _Classifier:
    """Decides which text blocks may be peeled off a box edge."""

    def __init__(self, doc: fitz.Document, page: fitz.Page):
        self.page = page
        self.body_size = _body_font_size(doc)
        pages = [(p, text_blocks(p)) for p in doc]
        self.running = running_blocks(pages[page.number][1], page.rect.height,
                                      running_texts(pages))

    def kind(self, block: dict):
        if block in self.running:
            return "running"
        text = block_text(block)
        if _CAPTION_RE.match(text):
            return "caption"
        lines = [t for t in ("".join(s["text"] for s in l["spans"]).strip()
                             for l in block["lines"]) if t]
        if len(lines) <= 2 and len(text) <= HEADING_MAX_CHARS and _HEADING_RE.match(text):
            return "heading"
        if self.is_paragraph(block, lines):
            return "paragraph"
        return None

    def is_paragraph(self, block: dict, lines: list) -> bool:
        """Body text: body font size, at least one long line, and a wide block."""
        sizes = [s["size"] for l in block["lines"] for s in l["spans"] if s["text"].strip()]
        if not sizes or not lines:
            return False
        dominant = max(set(sizes), key=sizes.count)
        width = block["bbox"][2] - block["bbox"][0]
        return (abs(dominant - self.body_size) <= BODY_SIZE_TOLERANCE
                and max(map(len, lines)) >= BODY_MIN_LINE_CHARS
                and width >= self.page.rect.width * BODY_MIN_WIDTH)


def _overlap(a0, a1, b0, b1) -> float:
    return min(a1, b1) - max(a0, b0)


def _peel(page: fitz.Page, box: fitz.Rect, classify: _Classifier) -> fitz.Rect:
    """Trim the box inward, removing peelable text blocks from its edges."""
    blocks = [(fitz.Rect(b["bbox"]), classify.kind(b)) for b in text_blocks(page)]
    graphics = ([fitz.Rect(d["rect"]) for d in page.get_drawings()]
                + [fitz.Rect(i["bbox"]) for i in page.get_image_info()])
    graphics = [g for g in graphics if g.width < page.rect.width * 0.95]

    # Side edges: a body paragraph mostly outside the box, crossing its left/right edge.
    for rect, kind in blocks:
        if kind != "paragraph" or not rect.intersects(box):
            continue
        if _overlap(rect.x0, rect.x1, box.x0, box.x1) >= 0.5 * rect.width:
            continue
        if rect.x0 < box.x0 < rect.x1:
            box.x0 = rect.x1 + PAD
        elif rect.x0 < box.x1 < rect.x1:
            box.x1 = rect.x0 - PAD

    # Top/bottom edges: peel the outermost item while it is a peelable text block.
    while not box.is_empty and box.height >= MIN_SIZE:
        items = [(r, k) for r, k in blocks if r.intersects(box)]
        items += [(g, None) for g in graphics
                  if _overlap(g.y0, g.y1, box.y0, box.y1) >= MIN_GRAPHIC_OVERLAP
                  and _overlap(g.x0, g.x1, box.x0, box.x1) > 0]
        if not items:
            break
        top = min(items, key=lambda it: max(it[0].y0, box.y0))
        bottom = max(items, key=lambda it: min(it[0].y1, box.y1))
        if top[1]:
            box.y0 = top[0].y1 + PAD
        elif bottom[1]:
            box.y1 = bottom[0].y0 - PAD
        else:
            break
    return box


def _content_runs(rows: list) -> list:
    runs = []
    for y in rows:
        if runs and y - runs[-1][1] <= SLIVER_GAP:
            runs[-1][1] = y
        else:
            runs.append([y, y])
    return runs


def _trim_whitespace(page: fitz.Page, box: fitz.Rect) -> fitz.Rect:
    """Shrink the box to its non-white content, dropping thin slivers at top/bottom.
    Rendered at 72 dpi, so one pixel is one point."""
    pix = page.get_pixmap(clip=box, dpi=72, colorspace=fitz.csGRAY)
    w, h, s = pix.width, pix.height, pix.samples
    rows = [y for y in range(h) if min(s[y * w:(y + 1) * w]) < WHITE]
    runs = _content_runs(rows)
    while len(runs) > 1 and runs[0][1] - runs[0][0] < SLIVER_HEIGHT:
        runs.pop(0)
    while len(runs) > 1 and runs[-1][1] - runs[-1][0] < SLIVER_HEIGHT:
        runs.pop()
    if not runs:
        return fitz.Rect()
    top, bottom = runs[0][0], runs[-1][1]
    cols = [x for x in range(w) if min(s[x + top * w:(bottom + 1) * w:w]) < WHITE]
    if not cols:
        return fitz.Rect()
    sx, sy = box.width / w, box.height / h
    return fitz.Rect(box.x0 + cols[0] * sx - PAD, box.y0 + top * sy - PAD,
                     box.x0 + (cols[-1] + 1) * sx + PAD,
                     box.y0 + (bottom + 1) * sy + PAD) & box


def _parse_box(text: str) -> tuple:
    try:
        x0, y0, x1, y1 = (float(v) for v in text.split(","))
    except ValueError as exc:
        raise CropError(f"invalid --box '{text}': expected x0,y0,x1,y1 "
                        "as page fractions between 0 and 1") from exc
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise CropError(f"invalid --box '{text}': need 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1")
    return x0, y0, x1, y1


def _locate(page_image: Path) -> tuple:
    """Return (pdf_path, page_index) for a pages/pN.png image."""
    if not page_image.is_file():
        raise CropError(f"page image not found: {page_image}")
    match = _PAGE_FILE_RE.match(page_image.name)
    if not match:
        raise CropError(f"page image must be named pN.png (got {page_image.name})")
    manifest = page_image.parent / "source.json"
    if not manifest.is_file():
        raise CropError(f"{manifest} not found; run render_pages.py first")
    pdf = Path(json.loads(manifest.read_text(encoding="utf-8"))["pdf"])
    if not pdf.is_file():
        raise CropError(f"source PDF not found: {pdf} (listed in {manifest})")
    return pdf, int(match.group(1)) - 1


def _final_box(doc: fitz.Document, page: fitz.Page, fractions: tuple) -> fitz.Rect:
    width, height = page.rect.width, page.rect.height
    x0, y0, x1, y1 = fractions
    box = _peel(page, fitz.Rect(x0 * width, y0 * height, x1 * width, y1 * height),
                _Classifier(doc, page))
    if not box.is_empty and box.height >= MIN_SIZE:
        box = _trim_whitespace(page, box)
    if box.is_empty or box.width < MIN_SIZE or box.height < MIN_SIZE:
        raise CropError("nothing left in the box after removing captions, body text and "
                        "headers; redraw the box around the figure")
    return box


def crop(page_image: Path, box_text: str, name: str) -> tuple:
    """Crop and save; returns (output_path, final box as page fractions)."""
    fractions = _parse_box(box_text)
    pdf, index = _locate(page_image)
    out = page_image.parent.parent / "images" / (Path(name).stem + ".png")
    with fitz.open(pdf) as doc:
        if not 0 <= index < doc.page_count:
            raise CropError(f"{page_image.name} is beyond the PDF's {doc.page_count} pages")
        page = doc[index]
        box = _final_box(doc, page, fractions)
        out.parent.mkdir(parents=True, exist_ok=True)
        page.get_pixmap(dpi=DPI, clip=box).save(str(out))
        rect = page.rect
        final = (box.x0 / rect.width, box.y0 / rect.height,
                 box.x1 / rect.width, box.y1 / rect.height)
    return out, final


def main():
    parser = argparse.ArgumentParser(description="Crop a figure from a PDF page")
    parser.add_argument("--page-image", required=True, help="Page image (pages/pN.png)")
    parser.add_argument("--box", required=True,
                        help="x0,y0,x1,y1 as 0-1 page fractions; draw it generously")
    parser.add_argument("--name", required=True, help="Output name (saved as images/<name>.png)")
    args = parser.parse_args()
    try:
        out, final = crop(Path(args.page_image), args.box, args.name)
    except CropError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"image: {out}")
    print("box: " + ",".join(f"{v:.3f}" for v in final))


if __name__ == "__main__":
    main()
