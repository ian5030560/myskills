import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "pdf" / "scripts"
IMG_SCRIPT = SCRIPTS_DIR / "pdf_images_extractor.py"


def _run(args: list[str]):
    return subprocess.run(
        [sys.executable, str(IMG_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8",
    )


def tesseract_available():
    return shutil.which("tesseract") is not None


class TestImagesExtractor:

    def test_extract_images(self, images_pdf, output_dir):
        result = _run(["--pdf", str(images_pdf), "--no-ocr",
                       "--output-dir", str(output_dir)])
        assert result.returncode == 0
        img_dir = output_dir / images_pdf.stem
        images = list(img_dir.glob("*"))
        assert len(images) > 0
        assert any(f.suffix.lower() in (".png", ".jpg", ".jpeg") for f in images)

    def test_no_images_in_text_pdf(self, simple_pdf, output_dir):
        result = _run(["--pdf", str(simple_pdf), "--no-ocr",
                       "--output-dir", str(output_dir)])
        assert result.returncode == 0
        img_dir = output_dir / simple_pdf.stem
        images = list(img_dir.glob("*"))
        assert len(images) == 0

    def test_file_not_found(self):
        result = _run(["--pdf", "nonexistent.pdf"])
        assert result.returncode == 1
        assert "file not found" in result.stderr

    @pytest.mark.skipif(not tesseract_available(), reason="Tesseract not installed")
    def test_ocr_output_file(self, images_pdf, output_dir):
        result = _run(["--pdf", str(images_pdf), "--ocr-output", "file",
                       "--output-dir", str(output_dir)])
        assert result.returncode == 0
        img_dir = output_dir / images_pdf.stem
        txt_files = list(img_dir.glob("*.txt"))
        assert len(txt_files) > 0

    def test_no_ocr_flag(self, images_pdf, output_dir):
        result = _run(["--pdf", str(images_pdf), "--no-ocr",
                       "--output-dir", str(output_dir)])
        assert result.returncode == 0
        img_dir = output_dir / images_pdf.stem
        txt_files = list(img_dir.glob("*.txt"))
        assert len(txt_files) == 0
