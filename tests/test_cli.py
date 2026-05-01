"""
Tests for CLI argument parsing in extract.py
"""
import sys
from pathlib import Path
import pytest
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "write-paper-notes" / "scripts"))

# pylint: disable=wrong-import-position
from extract import main  # noqa: E402


class TestArgumentParsing:
    """Tests for command line argument parsing"""

    def test_default_args(self, mock_extract_deps):
        """Test parsing with only required --pdf argument"""
        argv = ['extract.py', '--pdf', 'test.pdf']
        with patch('sys.argv', argv):
            # Expect exit when OCR not installed and no --no-ocr flag
            with patch('extract.should_run_ocr', return_value=(False, "ERROR")):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

    def test_with_output_dir(self, mock_extract_deps):
        """Test parsing with --output-dir"""
        argv = ['extract.py', '--pdf', 'test.pdf', '--output-dir', 'output']
        with patch('sys.argv', argv):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # Should exit because no --no-ocr and tesseract not installed
            assert exc_info.value.code == 1

    def test_with_no_ocr(self, tmp_path, mock_extract_deps):
        """Test parsing with --no-ocr flag"""
        # Create a temporary PDF file
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()

        output_dir = tmp_path / "output"
        argv = ['extract.py', '--pdf', str(pdf_path), '--no-ocr', '--output-dir', str(output_dir)]
        with patch('sys.argv', argv):
            main()  # Should not exit because --no-ocr is set and file exists
            # Verify extract_images called with run_ocr=False (3rd argument)
            mock_extract_deps['extract_images'].assert_called_once()
            call_args = mock_extract_deps['extract_images'].call_args
            # extract_images(reader, output_dir, run_ocr)
            assert call_args[0][2] is False  # 3rd positional argument is run_ocr

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
        with patch('sys.argv', argv):
            with patch('extract.PdfReader') as mock_reader:
                mock_reader.return_value.pages = []
                with patch('extract.extract_images', return_value={}):
                    with patch('extract.extract_tables', return_value={}):
                        with patch('extract.format_output', return_value=""):
                            main()
                            assert output_dir.exists()
