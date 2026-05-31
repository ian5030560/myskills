import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "write-paper-notes" / "scripts"
EXTRACT_SCRIPT = SCRIPTS_DIR / "extract.py"


def _run(args: list[str]):
    return subprocess.run(
        [sys.executable, str(EXTRACT_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8",
    )


def has_tesseract() -> bool:
    try:
        r = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
        return r.returncode == 0
    except FileNotFoundError:
        return False


class TestExtract:

    def test_simple_text_stdout_no_ocr(self, simple_pdf, output_dir):
        result = _run(["--pdf", str(simple_pdf), "--output-dir", str(output_dir), "--no-ocr"])
        assert result.returncode == 0
        assert "Hello World - Paper Notes" in result.stdout

    def test_default_ocr_creates_images_dir(self, simple_pdf, output_dir):
        if not has_tesseract():
            pytest.skip("Tesseract not installed")
        result = _run(["--pdf", str(simple_pdf), "--output-dir", str(output_dir)])
        assert result.returncode == 0
        assert (output_dir / "simple" / "images").is_dir()

    def test_no_ocr_flag_with_image_pdf(self, images_pdf, output_dir):
        result = _run(["--pdf", str(images_pdf), "--output-dir", str(output_dir), "--no-ocr"])
        assert result.returncode == 0
        assert "Paper with figures" in result.stdout
        img_dir = output_dir / "images" / "images"
        assert img_dir.is_dir()
        images = list(img_dir.iterdir())
        assert len(images) > 0

    def test_multi_page_stdout(self, multi_page_pdf, output_dir):
        result = _run(["--pdf", str(multi_page_pdf), "--output-dir", str(output_dir), "--no-ocr"])
        assert result.returncode == 0
        for i in range(1, 4):
            assert f"Section {i}" in result.stdout

    def test_file_not_found_exit_code(self):
        result = _run(["--pdf", "nonexistent.pdf"])
        assert result.returncode == 1

    def test_default_output_dir_creates_stem_subfolder(self, simple_pdf, tmp_path):
        result = subprocess.run(
            [sys.executable, str(EXTRACT_SCRIPT), "--pdf", str(simple_pdf), "--no-ocr"],
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(tmp_path),
        )
        assert result.returncode == 0
        assert "Hello World - Paper Notes" in result.stdout
        expected_dir = tmp_path / "simple"
        assert expected_dir.is_dir()
        assert (expected_dir / "images").is_dir()

    def test_output_dir_structure(self, simple_pdf, output_dir):
        _run(["--pdf", str(simple_pdf), "--output-dir", str(output_dir), "--no-ocr"])
        stem_dir = output_dir / "simple"
        assert stem_dir.is_dir()
        assert (stem_dir / "images").is_dir()

    def test_images_dir_empty_for_text_only_pdf(self, simple_pdf, output_dir):
        _run(["--pdf", str(simple_pdf), "--output-dir", str(output_dir), "--no-ocr"])
        img_dir = output_dir / "simple" / "images"
        assert img_dir.is_dir()
        assert len(list(img_dir.iterdir())) == 0
