#!/usr/bin/env python3
"""Extract a PDF's text layer to <output-dir>/<stem>/text.md.

Plain text in reading order: running headers/footers removed, two-column pages read
left column then right, each page starting with a ``<!-- pN -->`` marker. No heading
markers and no table reconstruction: the AI infers those from the section numbering
and the page images. Pages with no text layer are flagged instead of OCR'd.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import fitz

NO_TEXT_FLAG = "此頁無文字層"
MARGIN = 0.12          # top/bottom fraction of the page where running headers live
EDGE_BLOCKS = 2        # topmost/bottommost blocks per page also checked for repetition
RUNNING_MAX_CHARS = 200  # running headers/footers are short; longer blocks are body text
REPEAT_RATIO = 0.3     # a margin text repeated on this share of pages is a running header
FULL_WIDTH = 0.6       # blocks wider than this share of the page span both columns
HEADING_MAX_CHARS = 80
JOIN_MAX_GAP = 0.8       # one-line blocks closer than this many line heights are joined
JOIN_X_TOLERANCE = 3     # ...when they start at the same x (an indent starts a new paragraph)
MAX_INDENT = 20          # a paragraph's indented first line may be followed by a flush line
JOIN_SIZE_TOLERANCE = 0.5
# Section numbers have at most two digits per level; headings never end in a digit
# (reference lines like "346. Springer, 2019. 3" do).
_HEADING_RE = re.compile(r"^(\d{1,2}\.(\d{1,2}\.?)*|\d{1,2})\s+[A-Z].*\D$")
_PAGE_NUMBER_RE = re.compile(r"\d+")
_CAPTION_RE = re.compile(r"^\s*(figure|fig\.?|table)\s*\d", re.I)
_BULLET_RE = re.compile(r"^\s*[•●▪◦·\-–—*]\s")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\d+", "#", text.strip().lower()))


def _line_text(line: dict) -> str:
    return "".join(span["text"] for span in line["spans"]).strip()


def block_text(block: dict) -> str:
    return " ".join(t for t in (_line_text(l) for l in block["lines"]) if t)


def text_blocks(page: fitz.Page) -> list:
    blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]
    return [b for b in blocks if b["type"] == 0 and block_text(b)]


def _edge_blocks(blocks: list, height: float) -> list:
    """Blocks that can be running headers/footers: inside the top/bottom margin band,
    or among the EDGE_BLOCKS topmost/bottommost blocks (templates whose footer sits
    well above the page edge)."""
    by_y = sorted(blocks, key=lambda b: b["bbox"][1])
    edge = by_y[:EDGE_BLOCKS] + by_y[-EDGE_BLOCKS:]
    return [b for b in blocks
            if len(block_text(b)) <= RUNNING_MAX_CHARS
            and (b in edge or b["bbox"][3] < height * MARGIN
                 or b["bbox"][1] > height * (1 - MARGIN))]


def running_texts(pages: list) -> set:
    counts = Counter()
    for page, blocks in pages:
        for block in _edge_blocks(blocks, page.rect.height):
            counts[_normalize(block_text(block))] += 1
    threshold = max(2, len(pages) * REPEAT_RATIO)
    return {text for text, n in counts.items() if n >= threshold}


def running_blocks(blocks: list, height: float, running: set) -> list:
    return [b for b in _edge_blocks(blocks, height)
            if _normalize(block_text(b)) in running
            or _PAGE_NUMBER_RE.fullmatch(block_text(b))]


def _reading_order(blocks: list, width: float) -> list:
    """Full-width blocks split the page into bands; each band is read left column first."""
    mid = width / 2
    ordered, band = [], []

    def flush():
        band.sort(key=lambda b: (0 if (b["bbox"][0] + b["bbox"][2]) / 2 < mid else 1,
                                 b["bbox"][1]))
        ordered.extend(band)
        band.clear()

    for block in sorted(blocks, key=lambda b: b["bbox"][1]):
        x0, _, x1, _ = block["bbox"]
        if x1 - x0 > width * FULL_WIDTH and x0 < mid < x1:
            flush()
            ordered.append(block)
        else:
            band.append(block)
    flush()
    return ordered


def _is_heading_line(text: str) -> bool:
    return len(text) <= HEADING_MAX_CHARS and bool(_HEADING_RE.match(text))


def _join_lines(lines: list) -> str:
    text = ""
    for line in lines:
        if not text:
            text = line
        elif text.endswith("-") and line[:1].islower():
            text = text[:-1] + line
        else:
            text += " " + line
    return text


def _block_paragraphs(block: dict) -> list:
    """Join a block's lines into paragraphs, putting numbered heading lines on their own."""
    paragraphs, current = [], []
    for line in (t for t in (_line_text(l) for l in block["lines"]) if t):
        if _is_heading_line(line):
            if current:
                paragraphs.append(_join_lines(current))
                current = []
            paragraphs.append(line)
        else:
            current.append(line)
    if current:
        paragraphs.append(_join_lines(current))
    return paragraphs


def _horizontal(block: dict):
    """The block with rotated lines (side-bar publisher/arXiv marks) removed, or None."""
    lines = [l for l in block["lines"] if abs(l["dir"][1]) < 0.1]
    return dict(block, lines=lines) if lines and block_text(dict(block, lines=lines)) else None


def _dominant_size(block: dict) -> float:
    sizes = [round(s["size"], 1) for l in block["lines"] for s in l["spans"] if s["text"].strip()]
    return max(set(sizes), key=sizes.count) if sizes else 0.0


def _continues(prev: dict, block: dict) -> bool:
    """Whether block continues prev's paragraph: not indented relative to prev (an
    indented first line may be followed by flush-left lines), tight vertical gap, same
    font size, and not starting a caption, bullet or numbered heading."""
    px0, py0, _, py1 = prev["bbox"]
    bx0, by0, _, _ = block["bbox"]
    line_height = (py1 - py0) / max(1, len(prev["lines"]))
    first = _line_text(block["lines"][0])
    return (-MAX_INDENT <= bx0 - px0 <= JOIN_X_TOLERANCE
            and 0 <= by0 - py1 <= JOIN_MAX_GAP * line_height
            and abs(_dominant_size(block) - _dominant_size(prev)) <= JOIN_SIZE_TOLERANCE
            and not _CAPTION_RE.match(first) and not _BULLET_RE.match(first)
            and not _is_heading_line(first))


def _join_blocks(blocks: list) -> list:
    """Merge consecutive blocks of one paragraph (PDFs that put every line in its own block)."""
    merged = []
    for block in blocks:
        if merged and _continues(merged[-1]["last"], block):
            merged[-1]["lines"].extend(block["lines"])
            merged[-1]["last"] = block
        else:
            merged.append({"lines": list(block["lines"]), "last": block})
    return merged


def extract(pdf_path: Path) -> tuple:
    """Return (text, page_count, pages_without_text_layer)."""
    with fitz.open(pdf_path) as doc:
        pages = [(page, text_blocks(page)) for page in doc]
        running = running_texts(pages)
        out, no_text = [], []
        for number, (page, blocks) in enumerate(pages, start=1):
            out.append(f"<!-- p{number} -->")
            if not blocks:
                no_text.append(number)
                out.append(NO_TEXT_FLAG)
                continue
            drop = running_blocks(blocks, page.rect.height, running)
            body = [h for h in (_horizontal(b) for b in blocks if b not in drop) if h]
            for paragraph in _join_blocks(_reading_order(body, page.rect.width)):
                out.extend(_block_paragraphs(paragraph))
        return "\n\n".join(out) + "\n", len(pages), no_text


def parse_pdf_cli(description: str) -> tuple:
    """Shared CLI for scripts taking --input <pdf> [--output-dir <dir>].

    Rejects non-PDF input (asking the user to save it as PDF first) and missing files,
    exiting with status 1. Returns (input_path, out_dir) where out_dir is
    <output-dir or cwd>/<input stem>.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--input", required=True, help="Input PDF path")
    parser.add_argument("--output-dir",
                        help="Parent directory for output (default: current dir; "
                             "creates a <stem> subfolder)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.suffix.lower() != ".pdf":
        print(f"Error: only PDF is supported (got '{input_path.suffix or input_path.name}'). "
              "Save the file as PDF first, then run this again.", file=sys.stderr)
        sys.exit(1)
    if not input_path.is_file():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    out_dir = (Path(args.output_dir) if args.output_dir else Path.cwd()) / input_path.stem
    return input_path, out_dir


def main():
    input_path, out_dir = parse_pdf_cli("Extract a PDF's text layer to text.md")
    out_dir.mkdir(parents=True, exist_ok=True)
    text, page_count, no_text = extract(input_path)
    text_file = out_dir / "text.md"
    text_file.write_text(text, encoding="utf-8")

    print(f"text: {text_file}")
    print(f"pages: {page_count}")
    print(f"no text layer: {', '.join(map(str, no_text)) if no_text else 'none'}")


if __name__ == "__main__":
    main()
