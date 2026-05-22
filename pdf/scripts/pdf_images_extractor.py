import argparse
import sys
from pathlib import Path

import fitz


def _ocr_image(img_bytes: bytes, ext: str, lang: str) -> str:
    img_doc = fitz.open(stream=img_bytes, filetype=ext)
    pix = img_doc[0].get_pixmap()
    img_doc.close()
    ocr_pdf_bytes = pix.pdfocr_tobytes(language=lang)
    ocr_pdf = fitz.open("pdf", ocr_pdf_bytes)
    text = ocr_pdf[0].get_text().strip()
    ocr_pdf.close()
    return text


def extract_images(pdf_path: str, output_dir: Path, use_ocr: bool = True,
                   ocr_language: str = "eng", ocr_output: str = "file"):
    output_dir.mkdir(exist_ok=True, parents=True)
    pdf_stem = Path(pdf_path).stem

    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc):
            for img_idx, img in enumerate(page.get_images(full=True)):
                base = doc.extract_image(img[0])
                ext = base["ext"] or "png"
                name = f"{pdf_stem}_{page_num+1:04d}_{img_idx+1:02d}"
                (output_dir / f"{name}.{ext}").write_bytes(base["image"])

                if not use_ocr:
                    continue
                ocr_text = _ocr_image(base["image"], ext, ocr_language)
                if not ocr_text:
                    continue
                if ocr_output == "file":
                    (output_dir / f"{name}.txt").write_text(ocr_text, encoding="utf-8")
                else:
                    print(f"--- {name} OCR ---", flush=True)
                    print(ocr_text, flush=True)
                    print(flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="Extract images from PDF with optional OCR")
    parser.add_argument("--pdf", required=True, help="Input PDF file path")
    parser.add_argument("--output-dir", help="Parent directory for output (default: current dir)")
    parser.add_argument("--lang", default="eng", help="OCR language (default: eng)")
    parser.add_argument("--no-ocr", action="store_true",
                        help="Disable OCR (only extract images)")
    parser.add_argument("--ocr-output", default="file", choices=["file", "stdout"],
                        help="OCR output destination: file (default) or stdout")
    args = parser.parse_args()

    input_path = Path(args.pdf)
    if not input_path.exists():
        print(f"Error: file not found: {args.pdf}", file=sys.stderr)
        sys.exit(1)

    base_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    output_dir = base_dir / input_path.stem
    output_dir.mkdir(exist_ok=True, parents=True)

    extract_images(
        str(input_path), output_dir,
        use_ocr=not args.no_ocr,
        ocr_language=args.lang,
        ocr_output=args.ocr_output,
    )

    print(f"Images saved to {output_dir}", flush=True)


if __name__ == "__main__":
    main()
