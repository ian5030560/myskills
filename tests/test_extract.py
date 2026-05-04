"""
Tests for extraction functions in extract.py
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


class TestExtractPdf:
    """Tests for extract_pdf() function"""

    def test_returns_string(self, tmp_path):
        """Should return a string"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=0)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = "Sample markdown content"

            result = extract_pdf("test.pdf", output_dir, use_ocr=False)
            assert isinstance(result, str)

    def test_calls_pymupdf4llm_correctly(self, tmp_path):
        """Should call pymupdf4llm.to_markdown with correct parameters"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = "Sample markdown content"

            extract_pdf("test.pdf", output_dir, use_ocr=True, ocr_language="eng")

            # Check that to_markdown was called
            assert mock_p4llm.to_markdown.called

            # Check parameters
            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['ocr_function'] is not None  # RapidOCR enabled
            assert call_kwargs['ocr_language'] == 'eng'
            assert call_kwargs['write_images'] is True
            assert 'image_path' in call_kwargs

    def test_ocr_disabled(self, tmp_path):
        """Should disable OCR when use_ocr=False"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = "Sample markdown content"

            extract_pdf("test.pdf", output_dir, use_ocr=False)

            # Check ocr_function=None (OCR disabled)
            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['ocr_function'] is None

    def test_creates_image_dir(self, tmp_path):
        """Should create images directory"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=0)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = "Sample markdown content"

            extract_pdf("test.pdf", output_dir, use_ocr=False)

            # Verify images dir was created
            assert (output_dir / "images").exists()

    def test_writes_images(self, tmp_path):
        """Should set write_images=True"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=1)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = "Sample markdown content"

            extract_pdf("test.pdf", output_dir, use_ocr=False)

            # Verify write_images=True
            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['write_images'] is True
            assert 'image_path' in call_kwargs

    def test_page_count_correct(self, tmp_path):
        """Should process correct number of pages"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=3)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = "Page 1 content\n\nPage 2 content\n\nPage 3 content"

            result = extract_pdf("test.pdf", output_dir, use_ocr=False)

            # to_markdown should be called once (not per page)
            assert mock_p4llm.to_markdown.call_count == 1
            assert isinstance(result, str)

    def test_extracts_all_images(self, tmp_path):
        """Should extract images via pymupdf4llm write_images=True"""
        output_dir = tmp_path / "output"
        mock_doc = _mock_pymupdf_doc(num_pages=2)

        with patch('extract.pymupdf4llm') as mock_p4llm, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_pymupdf_open.return_value = mock_doc
            mock_p4llm.to_markdown.return_value = "Sample markdown with ![image](images/img.png)"

            extract_pdf("test.pdf", output_dir, use_ocr=False)

            # Verify pymupdf4llm.to_markdown was called with write_images=True
            call_kwargs = mock_p4llm.to_markdown.call_args[1]
            assert call_kwargs['write_images'] is True
            assert 'image_path' in call_kwargs
            # Verify images dir exists
            image_dir = output_dir / "images"
            assert image_dir.exists()
