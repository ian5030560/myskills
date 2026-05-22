import argparse
import sys
from pathlib import Path

import fitz
# pylint: disable=no-member


def cmd_merge(args):
    out = Path(args.output)
    out.parent.mkdir(exist_ok=True, parents=True)

    doc = fitz.open()
    for path in args.inputs:
        src = fitz.open(path)
        doc.insert_pdf(src)
        src.close()
    doc.save(str(out))
    doc.close()
    print(f"Merged {len(args.inputs)} PDFs into {out}", flush=True)


def cmd_split(args):
    base_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    src = fitz.open(args.pdf)
    pdf_stem = Path(args.pdf).stem
    total = len(src)

    ranges = args.ranges.split(",")
    for part in ranges:
        if "-" in part:
            a, b = part.split("-", 1)
            a, b = int(a.strip()), int(b.strip())
        else:
            a = b = int(part.strip())
        if a < 1 or b > total or a > b:
            print(f"Invalid range: {part}", file=sys.stderr)
            src.close()
            sys.exit(1)
        doc = fitz.open()
        doc.insert_pdf(src, from_page=a - 1, to_page=b - 1)
        name = f"{pdf_stem}_{a:04d}-{b:04d}.pdf" if a != b else f"{pdf_stem}_{a:04d}.pdf"
        out = base_dir / name
        doc.save(str(out))
        doc.close()
        print(f"  -> {out}", flush=True)
    src.close()
    print("Done.", flush=True)


def cmd_rotate(args):
    src = fitz.open(args.pdf)
    pages = set()
    for p in (args.pages or "").split(","):
        p = p.strip()
        if p:
            pages.add(int(p))
    target = range(len(src)) if not pages else [p - 1 for p in pages if 1 <= p <= len(src)]
    for i in target:
        src[i].set_rotation(args.angle)
    out = Path(args.output) if args.output else Path(args.pdf)
    src.save(str(out))
    src.close()
    print(f"Rotated to {out}", flush=True)


def cmd_metadata(args):
    src = fitz.open(args.pdf)
    meta = dict(src.metadata)
    if args.get:
        for k, v in meta.items():
            print(f"{k}: {v}", flush=True)
    elif args.set:
        updates = dict(kv.split("=", 1) for kv in args.set)
        meta.update(updates)
        src.set_metadata(meta)
        out = Path(args.output) if args.output else Path(args.pdf)
        out.parent.mkdir(exist_ok=True, parents=True)
        src.save(str(out))
        print("Metadata updated.", flush=True)
    src.close()


def main():
    parser = argparse.ArgumentParser(description="PDF structure manipulation")
    sub = parser.add_subparsers(dest="command", required=True)

    # merge
    m = sub.add_parser("merge", help="Merge multiple PDFs into one")
    m.add_argument("--inputs", nargs="+", required=True, help="Input PDF files")
    m.add_argument("--output", "-o", required=True, help="Output PDF file")
    m.set_defaults(func=cmd_merge)

    # split
    s = sub.add_parser("split", help="Split PDF by page ranges")
    s.add_argument("--pdf", required=True, help="Input PDF file")
    s.add_argument("--ranges", required=True, help='Page ranges, e.g. "1-3,5,7-9"')
    s.add_argument("--output-dir", help="Output directory")
    s.set_defaults(func=cmd_split)

    # rotate
    r = sub.add_parser("rotate", help="Rotate pages")
    r.add_argument("--pdf", required=True, help="Input PDF file")
    r.add_argument("--pages", help='Page numbers to rotate, e.g. "1,3,5" (omit for all)')
    r.add_argument("--angle", type=int, required=True, choices=[0, 90, 180, 270],
                   help="Rotation angle")
    r.add_argument("--output", "-o", help="Output file (default: overwrite input)")
    r.set_defaults(func=cmd_rotate)

    # metadata
    md = sub.add_parser("metadata", help="Get or set PDF metadata")
    md.add_argument("--pdf", required=True, help="Input PDF file")
    md.add_argument("--get", action="store_true", help="Print current metadata")
    md.add_argument("--set", nargs="+", help='Set metadata, e.g. "title=My Doc" "author=Me"')
    md.add_argument("--output", "-o", help="Output file (default: overwrite input)")
    md.set_defaults(func=cmd_metadata)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
