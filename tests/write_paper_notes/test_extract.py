import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import fitz

from extract import ocr_image_bytes, DocumentExtractor, PdfExtractor

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "write-paper-notes" / "scripts"
EXTRACT_SCRIPT = SCRIPTS_DIR / "extract.py"


def _run(args: list[str]):
    return subprocess.run(
        [sys.executable, str(EXTRACT_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8",
    )


# ── CLI integration tests ─────────────────────────────────────────────


class TestExtractCLI:
    """End-to-end tests via subprocess — CLI-specific behavior only."""

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

    def test_multi_page_stdout(self, multi_page_pdf, output_dir):
        result = _run(["--pdf", str(multi_page_pdf), "--output-dir", str(output_dir), "--no-ocr"])
        assert result.returncode == 0
        for i in range(1, 4):
            assert f"Section {i}" in result.stdout


# ── Module-level helper tests ─────────────────────────────────────────


class TestOcrImageBytes:
    """Unit tests for ocr_image_bytes()."""

    def test_skips_tiny_image(self):
        d = fitz.open()
        p = d.new_page(width=1, height=36)
        pix = p.get_pixmap()
        img_bytes = pix.tobytes("png")
        d.close()
        assert ocr_image_bytes(img_bytes, "png", "eng") is None

    def test_returns_none_on_tesseract_error(self):
        d = fitz.open()
        p = d.new_page()
        pix = p.get_pixmap()
        img_bytes = pix.tobytes("png")
        d.close()
        with patch.object(fitz.Pixmap, "pdfocr_tobytes", side_effect=RuntimeError("mock")):
            assert ocr_image_bytes(img_bytes, "png", "eng") is None


# ── ABC contract tests ────────────────────────────────────────────────


class TestDocumentExtractor:
    """Verify ABC contract and template method."""

    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            DocumentExtractor("dummy.pdf", Path("."))

    def test_extract_invokes_hooks_in_order(self, tmp_path):
        calls = []

        class SpyExtractor(DocumentExtractor):
            def load(self):
                calls.append("load")
            def close(self):
                calls.append("close")
            def do_extract(self):
                calls.append("do_extract")
                return "ok"

        ext = SpyExtractor("dummy", tmp_path / "out")
        result = ext.extract()
        assert result == "ok"
        assert calls == ["load", "do_extract", "close"]
        assert (tmp_path / "out" / "images").is_dir()

    def test_close_called_on_do_extract_error(self, tmp_path):
        calls = []

        class FailingExtractor(DocumentExtractor):
            def load(self):
                calls.append("load")
            def close(self):
                calls.append("close")
            def do_extract(self):
                calls.append("do_extract")
                raise ValueError("boom")

        ext = FailingExtractor("dummy", tmp_path / "out")
        with pytest.raises(ValueError):
            ext.extract()
        assert calls == ["load", "do_extract", "close"]


# ── PdfExtractor unit tests ───────────────────────────────────────────


class TestPdfExtractor:
    """Unit tests for PdfExtractor (direct import, no subprocess)."""

    def test_extract_returns_markdown_with_text(self, simple_pdf, tmp_path):
        ext = PdfExtractor(str(simple_pdf), tmp_path / "out", use_ocr=False)
        result = ext.extract()
        assert "Hello World - Paper Notes" in result

    def test_directories_created(self, simple_pdf, tmp_path):
        ext = PdfExtractor(str(simple_pdf), tmp_path / "out", use_ocr=False)
        ext.extract()
        assert (tmp_path / "out").is_dir()
        assert (tmp_path / "out" / "images").is_dir()

    def test_images_extracted_with_metadata(self, images_pdf, tmp_path):
        ext = PdfExtractor(str(images_pdf), tmp_path / "out", use_ocr=False)
        result = ext.extract()
        assert "Paper with figures" in result
        img_dir = tmp_path / "out" / "images"
        images = list(img_dir.iterdir())
        assert len(images) > 0

    def test_images_dir_empty_for_text_only(self, simple_pdf, tmp_path):
        ext = PdfExtractor(str(simple_pdf), tmp_path / "out", use_ocr=False)
        ext.extract()
        assert len(list((tmp_path / "out" / "images").iterdir())) == 0

    def test_vector_graphics_in_output(self, vector_pdf, tmp_path):
        ext = PdfExtractor(str(vector_pdf), tmp_path / "out", use_ocr=False)
        result = ext.extract()
        assert "Paper with vector diagrams" in result
        img_dir = tmp_path / "out" / "images"
        vg_files = [f for f in img_dir.iterdir() if "_v" in f.stem]
        assert len(vg_files) > 0
        for f in vg_files:
            assert f.stat().st_size > 100

    def test_tiny_image_no_crash(self, tiny_image_pdf, tmp_path):
        ext = PdfExtractor(str(tiny_image_pdf), tmp_path / "out", use_ocr=True)
        result = ext.extract()
        assert "Tiny images test" in result
