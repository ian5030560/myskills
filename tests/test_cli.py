"""
Tests for CLI argument parsing in extract.py
"""
import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "write-paper-notes" / "scripts"))

# pylint: disable=wrong-import-position
from extract import main  # noqa: E402


class TestArgumentParsing:
    """Tests for command line argument parsing"""

    def test_default_args(self, tmp_path):
        """Test parsing with only required --pdf argument"""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()

        argv = ['extract.py', '--pdf', str(pdf_path)]

        mock_doc = MagicMock()
        mock_doc.__enter__ = MagicMock(return_value=mock_doc)
        mock_doc.__exit__ = MagicMock(return_value=False)
        mock_doc.__len__ = MagicMock(return_value=5)

        # Calculate potential test directory in project root (prevent leakage)
        project_root = Path(__file__).parent.parent
        potential_test_dir = project_root / "test"

        try:
            with patch('sys.argv', argv), \
                 patch('extract.extract_pdf') as mock_extract_pdf, \
                 patch('extract.pymupdf.open') as mock_pymupdf_open:
                mock_extract_pdf.return_value = "Sample markdown"
                mock_pymupdf_open.return_value = mock_doc
                main()
                # Verify extract_pdf was called
                assert mock_extract_pdf.called
        finally:
            # Cleanup: remove test directory if it was created in project root
            if potential_test_dir.exists():
                import shutil
                shutil.rmtree(potential_test_dir, ignore_errors=True)

    def test_with_output_dir(self, tmp_path):
        """Test parsing with --output-dir"""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()
        output_dir = tmp_path / "output"

        argv = ['extract.py', '--pdf', str(pdf_path), '--output-dir', str(output_dir)]

        mock_doc = MagicMock()
        mock_doc.__enter__ = MagicMock(return_value=mock_doc)
        mock_doc.__exit__ = MagicMock(return_value=False)
        mock_doc.__len__ = MagicMock(return_value=5)

        with patch('sys.argv', argv), \
             patch('extract.extract_pdf') as mock_extract_pdf, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_extract_pdf.return_value = "Sample markdown"
            mock_pymupdf_open.return_value = mock_doc
            main()
            # Verify extract_pdf was called
            assert mock_extract_pdf.called

    def test_with_no_ocr(self, tmp_path):
        """Test parsing with --no-ocr flag"""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()
        output_dir = tmp_path / "output"

        argv = ['extract.py', '--pdf', str(pdf_path), '--no-ocr', '--output-dir', str(output_dir)]

        mock_doc = MagicMock()
        mock_doc.__enter__ = MagicMock(return_value=mock_doc)
        mock_doc.__exit__ = MagicMock(return_value=False)
        mock_doc.__len__ = MagicMock(return_value=5)

        with patch('sys.argv', argv), \
             patch('extract.extract_pdf') as mock_extract_pdf, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_extract_pdf.return_value = "Sample markdown"
            mock_pymupdf_open.return_value = mock_doc
            main()
            # Verify extract_pdf was called with use_ocr=False
            call_kwargs = mock_extract_pdf.call_args
            # Check that use_ocr is False (keyword argument)
            assert call_kwargs[1].get('use_ocr') is False

    def test_missing_pdf(self):
        """Test that missing --pdf raises error"""
        with patch('sys.argv', ['extract.py']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # argparse raises SystemExit with code 2 for errors
            assert exc_info.value.code == 2


class TestMainFunction:
    """Tests for main() function behavior"""

    def test_file_not_found(self):
        """Test handling of non-existent PDF file"""
        argv = ['extract.py', '--pdf', 'nonexistent.pdf', '--no-ocr']
        with patch('sys.argv', argv):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_output_dir_creation(self, tmp_path):
        """Test that output directory is created"""
        output_dir = tmp_path / "new_output"
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()

        argv = ['extract.py', '--pdf', str(pdf_path), '--output-dir',
                str(output_dir), '--no-ocr']

        mock_doc = MagicMock()
        mock_doc.__enter__ = MagicMock(return_value=mock_doc)
        mock_doc.__exit__ = MagicMock(return_value=False)
        mock_doc.__len__ = MagicMock(return_value=5)

        with patch('sys.argv', argv), \
             patch('extract.extract_pdf') as mock_extract_pdf, \
             patch('extract.pymupdf.open') as mock_pymupdf_open:
            mock_extract_pdf.return_value = "Sample markdown"
            mock_pymupdf_open.return_value = mock_doc
            main()
            # Verify output_dir was created
            assert output_dir.exists()
