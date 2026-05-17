import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "write-paper-notes" / "scripts"))

from extract import extract_pdf


def _mock_pymupdf_doc(num_pages=1):
    mock_doc = MagicMock()
    mock_doc.__enter__ = MagicMock(return_value=mock_doc)
    mock_doc.__exit__ = MagicMock(return_value=False)
    mock_doc.__len__ = MagicMock(return_value=num_pages)
    mock_doc.extract_image = MagicMock(return_value={"image": b"fake", "ext": "png"})

    page_mocks = []
    for _ in range(num_pages):
        page_mock = MagicMock()
        page_mock.get_images.return_value = [(1, 0, 0, 0, 0, 0, 0, 0, 0, 0)]
        page_mocks.append(page_mock)

    mock_doc.__iter__ = MagicMock(return_value=iter(page_mocks))
    mock_doc.__getitem__ = MagicMock(side_effect=lambda idx: page_mocks[idx])

    return mock_doc


class TestOcrIntegration:

    def test_ocr_enabled_by_default(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [{"text": "Sample markdown content"}]

            pixmap_mock = MagicMock()
            pixmap_mock.pdfocr_tobytes.return_value = b"mock pdf bytes"
            mock_doc[0].get_pixmap.return_value = pixmap_mock
            mock_doc[0].get_text.return_value = ""

            extract_pdf("test.pdf", output_dir, use_ocr=True)

            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['ocr_function'] is not None

    def test_ocr_disabled_with_no_ocr_flag(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [{"text": "Sample markdown content"}]

            extract_pdf("test.pdf", output_dir, use_ocr=False)

            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['ocr_function'] is None

    def test_uses_builtin_tesseract_plugin(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [{"text": "Sample markdown content"}]

            pixmap_mock = MagicMock()
            pixmap_mock.pdfocr_tobytes.return_value = b"mock pdf bytes"
            mock_doc[0].get_pixmap.return_value = pixmap_mock
            mock_doc[0].get_text.return_value = ""

            extract_pdf("test.pdf", output_dir, use_ocr=True)

            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            from pymupdf4llm.ocr import tesseract_api
            assert call_kwargs['ocr_function'] == tesseract_api.exec_ocr

    def test_ocr_language_passed(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [{"text": "Sample markdown content"}]

            pixmap_mock = MagicMock()
            pixmap_mock.pdfocr_tobytes.return_value = b"mock pdf bytes"
            mock_doc[0].get_pixmap.return_value = pixmap_mock
            mock_doc[0].get_text.return_value = ""

            extract_pdf("test.pdf", output_dir, use_ocr=True, ocr_language="eng+chi_sim")

            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['ocr_language'] == 'eng+chi_sim'

    def test_image_extraction_with_ocr(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [{"text": "## Introduction"}]

            pixmap_mock = MagicMock()
            pixmap_mock.pdfocr_tobytes.return_value = b"mock pdf bytes"
            mock_doc[0].get_pixmap.return_value = pixmap_mock
            mock_doc[0].get_text.return_value = "OCR text from image"

            result = extract_pdf("test.pdf", output_dir, use_ocr=True)

            assert "![Image](images/" in result
            assert "OCR text from image" in result

    def test_no_ocr_text_prefix(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [{"text": "## Introduction\n\nThis text was OCR'd from image."}]

            pixmap_mock = MagicMock()
            pixmap_mock.pdfocr_tobytes.return_value = b"mock pdf bytes"
            mock_doc[0].get_pixmap.return_value = pixmap_mock
            mock_doc[0].get_text.return_value = "OCR text from image"

            result = extract_pdf("test.pdf", output_dir, use_ocr=True)

            assert "[OCR]" not in result

    def test_ocr_fallback_when_tesseract_missing(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [{"text": "Text without OCR"}]

            pixmap_mock = MagicMock()
            pixmap_mock.pdfocr_tobytes.return_value = b"mock pdf bytes"
            mock_doc[0].get_pixmap.return_value = pixmap_mock
            mock_doc[0].get_text.return_value = ""

            result = extract_pdf("test.pdf", output_dir, use_ocr=True)
            assert isinstance(result, str)
