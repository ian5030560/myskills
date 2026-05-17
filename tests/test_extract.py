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


class TestExtractPdf:

    def test_returns_string(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=0)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [{"text": "Sample markdown content"}]

            result = extract_pdf("test.pdf", output_dir, use_ocr=False)
            assert isinstance(result, str)

    def test_calls_pymupdf4llm_correctly(self, tmp_path):
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

            extract_pdf("test.pdf", output_dir, use_ocr=True, ocr_language="eng")

            assert mock_p4llm.to_markdown.called
            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['ocr_function'] is not None
            assert call_kwargs['ocr_language'] == 'eng'
            assert call_kwargs['page_chunks'] is True
            assert call_kwargs['force_text'] is True
            assert 'write_images' not in call_kwargs
            assert 'image_path' not in call_kwargs

    def test_ocr_disabled(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [{"text": "Sample markdown content"}]

            extract_pdf("test.pdf", output_dir, use_ocr=False)

            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['ocr_function'] is None

    def test_creates_image_dir(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=0)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [{"text": "Sample markdown content"}]

            extract_pdf("test.pdf", output_dir, use_ocr=False)

            assert (output_dir / "images").exists()

    def test_extracts_images_via_fitz(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=2)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [
                {"text": "Page 1 content"},
                {"text": "Page 2 content"},
            ]

            result = extract_pdf("test.pdf", output_dir, use_ocr=False)

            assert mock_doc.extract_image.called
            image_dir = output_dir / "images"
            image_files = list(image_dir.iterdir())
            assert len(image_files) > 0

            assert "![Image](images/" in result

    def test_page_count_correct(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=3)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [
                {"text": "Page 1"},
                {"text": "Page 2"},
                {"text": "Page 3"},
            ]

            result = extract_pdf("test.pdf", output_dir, use_ocr=False)

            assert mock_p4llm.to_markdown.call_count == 1
            assert isinstance(result, str)

    def test_get_images_called_per_page(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=2)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [
                {"text": "Page 1"},
                {"text": "Page 2"},
            ]

            extract_pdf("test.pdf", output_dir, use_ocr=False)

            pages = [mock_doc.__getitem__(i) for i in range(2)]
            for page in pages:
                page.get_images.assert_called_with(full=True)

    def test_ocr_text_appended_after_image(self, tmp_path):
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.fitz.open') as mock_fitz_open:
            mock_fitz_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = [{"text": "Page content"}]

            pixmap_mock = MagicMock()
            pixmap_mock.pdfocr_tobytes.return_value = b"mock pdf bytes"
            mock_doc[0].get_pixmap.return_value = pixmap_mock
            mock_doc[0].get_text.return_value = "OCR extracted text"

            result = extract_pdf("test.pdf", output_dir, use_ocr=True)

            assert "![Image](images/" in result
            assert "OCR extracted text" in result
