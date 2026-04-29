#!/usr/bin/env python3
"""
Paper Notes Extractor - Extract content from PDF papers and generate structured Markdown notes

Usage:
    python scripts/extract.py --pdf <pdf_path> --image-dir <output_dir>

Dependencies:
    pip install pypdf pypdf-table-extract
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from pypdf import PdfReader
except ImportError:
    print("[ERROR] pypdf not installed. Run: pip install pypdf")
    sys.exit(1)

try:
    import pypdf_table_extraction
except ImportError:
    print("[ERROR] pypdf-table-extract not installed. Run: pip install pypdf-table-extract")
    sys.exit(1)


def detect_heading_level(line: str) -> int:
    """Detect heading level, returns 1-4"""
    line = line.strip()
    if not line:
        return 0

    patterns = [
        (r'^[IVX]+\.\s+', 2),
        (r'^\d+\.\s+', 2),
        (r'^\d+\.\d+\.\s+', 3),
        (r'^\d+\.\d+\.\d+\.\s+', 4),
        (r'^[a-z]\.\s+', 4),
        (r'^\(\d+\)\s+', 4),
        (r'^\[a-z\]\s+', 4),
        (r'^\[\d+\]\s+', 4),
    ]

    for pattern, level in patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return level

    if line[0].isupper() and len(line) < 100 and not line[0].isdigit():
        return 2

    return 4


def level_to_markdown(level: int) -> str:
    """Convert level to Markdown heading prefix"""
    levels = {1: "#", 2: "##", 3: "###", 4: "####"}
    return levels.get(level, "#")


def is_heading_line(line: str) -> bool:
    """Check if line is a heading (not body text)"""
    line = line.strip()
    if not line:
        return False

    if len(line) > 200:
        return False

    patterns = [
        r'^[IVX]+\.\s+',
        r'^\d+\.\s+',
        r'^\d+\.\d+\.\s+',
        r'^[A-Z][a-z]+(\s[A-Z][a-z]+)*\s*$',
    ]

    for pattern in patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return True

    return False


def clean_text(text: str) -> str:
    """Clean extracted text"""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def extract_page_text(reader: PdfReader, page_num: int) -> list:
    """Extract text from single page, return paragraphs with heading levels"""
    page = reader.pages[page_num - 1]
    text = page.extract_text()
    lines = text.split('\n')

    paragraphs = []
    current_paragraph = []
    current_level = 4

    for line in lines:
        line = line.strip()
        if not line:
            if current_paragraph:
                text_content = ' '.join(current_paragraph)
                if text_content:
                    paragraphs.append({
                        'level': current_level,
                        'text': clean_text(text_content)
                    })
                current_paragraph = []
            continue

        level = detect_heading_level(line)

        if level <= 3 and is_heading_line(line):
            if current_paragraph:
                text_content = ' '.join(current_paragraph)
                if text_content:
                    paragraphs.append({
                        'level': 4,
                        'text': clean_text(text_content)
                    })
                current_paragraph = []
            paragraphs.append({
                'level': level,
                'text': line
            })
        else:
            current_paragraph.append(line)
            if level < current_level:
                current_level = level

    if current_paragraph:
        text_content = ' '.join(current_paragraph)
        if text_content:
            paragraphs.append({
                'level': 4,
                'text': clean_text(text_content)
            })

    return paragraphs


def extract_images(reader: PdfReader, output_dir: Path) -> dict:
    """Extract images from PDF"""
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)

    extracted_images = {}
    for page_num, page in enumerate(reader.pages, 1):
        page_images = []
        for img_index, img in enumerate(page.images, 1):
            img_name = f"figure_{page_num}_{img_index}.png"
            img_path = images_dir / img_name
            with open(img_path, "wb") as f:
                f.write(img.data)
            page_images.append({
                'filename': img_name,
                'page': page_num,
                'index': img_index
            })
        if page_images:
            extracted_images[page_num] = page_images

    return extracted_images


def extract_tables(reader: PdfReader, input_path: str) -> dict:
    """Extract tables from PDF"""
    tables_by_page = {}

    tables = pypdf_table_extraction.read_pdf(input_path)

    for table in tables:
        page_number = table.page_numbers[0] if table.page_numbers else 1
        page_text = reader.pages[page_number - 1].extract_text()
        text_lines = page_text.split('\n')

        table_md = table.to_markdown()

        caption = f"Table {table.order + 1}"
        for line in text_lines:
            if re.search(rf'\bTable\s*{table.order + 1}\b', line, re.IGNORECASE):
                caption = line.strip()
                break

        if page_number not in tables_by_page:
            tables_by_page[page_number] = []

        tables_by_page[page_number].append({
            'index': table.order + 1,
            'caption': caption,
            'markdown': table_md
        })

    return tables_by_page


def format_output(reader: PdfReader, images: dict, tables: dict) -> str:
    """Format all content as Markdown output"""
    lines = []
    total_pages = len(reader.pages)

    for page_num in range(1, total_pages + 1):
        lines.append(f"--- Page {page_num} ---")
        lines.append("")

        paragraphs = extract_page_text(reader, page_num)

        for para in paragraphs:
            level = para['level']
            text = para['text']
            prefix = level_to_markdown(level)
            lines.append(f"{prefix} {text}")
            lines.append("")

        if page_num in images:
            for img in images[page_num]:
                img_path = f"images/{img['filename']}"
                lines.append(f"![Figure {img['index']}]({img_path})")
                lines.append("")

        if page_num in tables:
            for table in tables[page_num]:
                lines.append(f"**{table['caption']}**")
                lines.append(table['markdown'])
                lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Extract content from PDF papers")
    parser.add_argument("--pdf", required=True, help="Input PDF file path")
    parser.add_argument("--output-dir", required=False, help="Output directory (default: <pdf_filename>)")
    args = parser.parse_args()

    input_path = Path(args.pdf)

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        paper_name = input_path.stem
        output_dir = Path.cwd() / paper_name

    if not input_path.exists():
        print(f"[ERROR] File not found: {input_path}")
        sys.exit(1)

    output_dir.mkdir(exist_ok=True, parents=True)

    print(f"[INFO] Reading PDF: {input_path}")
    reader = PdfReader(str(input_path))

    print(f"[INFO] Total pages: {len(reader.pages)}")

    print("[INFO] Extracting images...")
    images = extract_images(reader, output_dir)
    print(f"[INFO] Extracted {sum(len(v) for v in images.values())} images")

    print("[INFO] Extracting tables...")
    tables = extract_tables(reader, str(input_path))
    total_tables = sum(len(v) for v in tables.values())
    print(f"[INFO] Extracted {total_tables} tables")

    print("[INFO] Generating Markdown...")
    output = format_output(reader, images, tables)

    print(output, flush=True)


if __name__ == "__main__":
    main()