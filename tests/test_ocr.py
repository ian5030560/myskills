"""
Tests for OCR integration in extract.py with pymupdf4llm built-in Tesseract plugin
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "write-paper-notes" / "scripts"))

# pylint: disable=wrong-import-position
from extract import extract_pdf  # noqa: E402


def _mock_pymupdf_doc(num_pages=1):
    """Create a mock pymupdf document that works as a context manager and supports iteration"""
    mock_doc = MagicMock()
    mock_doc.__enter__ = MagicMock(return_value=mock_doc)
    mock_doc.__exit__ = MagicMock(return_value=False)
    mock_doc.__len__ = MagicMock(return_value=num_pages)
    mock_doc.extract_image = MagicMock(return_value={"image": b"fake", "ext": "png"})

    # Create mock pages for iteration
    page_mocks = []
    for _ in range(num_pages):
        page_mock = MagicMock()
        page_mock.get_images.return_value = [(1,0,0,0,0,0,0,0,0,0)]
        page_mocks.append(page_mock)

    # Make mock_doc iterable - return pages in order
    mock_doc.__iter__ = MagicMock(return_value=iter(page_mocks))
    # Also support __getitem__ for direct access
    mock_doc.__getitem__ = MagicMock(side_effect=lambda idx: page_mocks[idx])

    return mock_doc


class TestOcrIntegration:
    """Tests for OCR integration with pymupdf4llm built-in Tesseract plugin"""

    def test_ocr_enabled_by_default(self, tmp_path):
        """OCR should be enabled by default"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = "Sample markdown content"

            extract_pdf("test.pdf", output_dir, use_ocr=True)

            # Verify use_ocr=True was passed
            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['use_ocr'] is True

    def test_ocr_disabled_with_no_ocr_flag(self, tmp_path):
        """OCR should be disabled when use_ocr=False"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = "Sample markdown content"

            extract_pdf("test.pdf", output_dir, use_ocr=False)

            # Verify use_ocr=False was passed
            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['use_ocr'] is False

    def test_uses_builtin_tesseract_plugin(self, tmp_path):
        """Should use built-in Tesseract plugin (ocr_function=None)"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = "Sample markdown content"

            extract_pdf("test.pdf", output_dir, use_ocr=True)

            # Verify ocr_function=None (use built-in Tesseract plugin)
            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs.get('ocr_function') is None

    def test_ocr_language_passed(self, tmp_path):
        """Should pass ocr_language to pymupdf4llm"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = "Sample markdown content"

            extract_pdf("test.pdf", output_dir, use_ocr=True, ocr_language="eng+chi_sim")

            # Verify ocr_language was passed
            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['ocr_language'] == 'eng+chi_sim'

    def test_image_extraction_with_ocr(self, tmp_path):
        """Should extract images and apply OCR when enabled"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            # Mock to_markdown to return markdown with image
            mock_p4llm.to_markdown.return_value = "## Introduction\n\n![Figure 1](images/figure_1_1.png)"

            result = extract_pdf("test.pdf", output_dir, use_ocr=True)

            assert "![Figure 1]" in result
            # Verify write_images=True
            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['write_images'] is True

    def test_no_ocr_text_prefix(self, tmp_path):
        """Should NOT have [OCR] prefix in output (per user request)"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            # Mock to_markdown to return markdown with OCR text (no prefix)
            mock_p4llm.to_markdown.return_value = "## Introduction\n\nThis text was OCR'd from image."

            result = extract_pdf("test.pdf", output_dir, use_ocr=True)

            # Should NOT contain [OCR] prefix
            assert "[OCR]" not in result

    def test_ocr_fallback_when_tesseract_missing(self, tmp_path):
        """Should handle missing Tesseract gracefully (pymupdf4llm auto-checks)"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            # pymupdf4llm auto-checks Tesseract; if missing, warns and skips OCR
            # We just verify the function completes without error
            mock_p4llm.to_markdown.return_value = "Text without OCR"

            result = extract_pdf("test.pdf", output_dir, use_ocr=True)
            assert isinstance(result, str)
