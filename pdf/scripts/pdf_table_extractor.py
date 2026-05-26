import argparse
import sys
from pathlib import Path

import fitz


def _table_to_markdown(table) -> str:
    data = table.extract()
    if not data or not data[0]:
        return "*Empty table*"

    def fmt_row(cells):
        return "| " + " | ".join(str(c) if c else "" for c in cells) + " |"

    col_count = max(len(row) for row in data)
    lines = [fmt_row(data[0])]
    lines.append("| " + " | ".join(["---"] * col_count) + " |")
    for row in data[1:]:
        while len(row) < col_count:
            row.append("")
        lines.append(fmt_row(row))
    return "\n".join(lines)


def extract_tables(pdf_path: str, output_dir: Path):
    output_dir.mkdir(exist_ok=True, parents=True)

    md_lines = ["# Extracted Tables", ""]

    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc):
            tables = page.find_tables()
            if not tables.tables:
                continue
            for idx, table in enumerate(tables.tables):
                md_lines.append(f"## Page {page_num + 1} — Table {idx + 1}")
                md_lines.append("")
                md_lines.append(_table_to_markdown(table))
                md_lines.append("")

    return "\n".join(md_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Extract tables from PDF as formatted Markdown")
    parser.add_argument("--pdf", required=True, help="Input PDF file path")
    parser.add_argument("--output-dir",
                        help="Parent directory for output (default: current dir)")
    args = parser.parse_args()

    input_path = Path(args.pdf)
    if not input_path.exists():
        print(f"Error: file not found: {args.pdf}", file=sys.stderr)
        sys.exit(1)

    base_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    output_dir = base_dir / input_path.stem
    output_dir.mkdir(exist_ok=True, parents=True)

    output = extract_tables(str(input_path), output_dir)

    output_file = output_dir / "tables.md"
    output_file.write_text(output, encoding="utf-8")
    print(f"Tables saved to {output_file}", flush=True)


if __name__ == "__main__":
    main()
