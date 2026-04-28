#!/usr/bin/env python3
"""
Save Notes - Save AI-organized notes to file

Usage:
    python scripts/save_notes.py --content <content> --output-dir <output_dir>

Dependencies:
    pip install pypdf pypdf-table-extract
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Save AI-organized notes to file")
    parser.add_argument("--content", required=True, help="AI-organized notes content (markdown)")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    notes_path = output_dir / "notes.md"
    content = args.content

    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] Notes saved to: {notes_path}")


if __name__ == "__main__":
    main()