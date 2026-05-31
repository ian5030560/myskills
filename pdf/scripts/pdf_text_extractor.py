import argparse
import sys
from pathlib import Path

import fitz


def extract_text(pdf_path: str, output_dir: Path) -> str:
    output_dir.mkdir(exist_ok=True, parents=True)

    with fitz.open(pdf_path) as doc:
        pages = []
        for page in doc:
            pages.append(page.get_text())
    return "\n\n".join(pages)


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF")
    parser.add_argument("--pdf", required=True, help="Input PDF file path")
    parser.add_argument("--output-dir", help="Parent directory for output (default: current dir)")
    args = parser.parse_args()

    input_path = Path(args.pdf)
    if not input_path.exists():
        print(f"Error: file not found: {args.pdf}", file=sys.stderr)
        sys.exit(1)

    base_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    output_dir = base_dir / input_path.stem
    output_dir.mkdir(exist_ok=True, parents=True)

    output = extract_text(str(input_path), output_dir)

    output_file = output_dir / "output.md"
    output_file.write_text(output, encoding="utf-8")

    print(f"Output saved to {output_file}", flush=True)


if __name__ == "__main__":
    main()
