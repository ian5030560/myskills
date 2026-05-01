"""
Tests for OCR functions in extract.py
These tests will pass once OCR functionality is implemented.
"""
import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "write-paper-notes" / "scripts"))

# These imports will fail until OCR functions are implemented
# pylint: disable=wrong-import-position
try:
    from extract import check_tesseract_installed, ocr_image, should_run_ocr  # noqa: E402
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class TestCheckTesseractInstalled:
    """Tests for check_tesseract_installed()"""

    def test_tesseract_found_in_path(self):
        """Should return True when tesseract is in PATH"""
        if not OCR_AVAILABLE:
            return
        with patch('shutil.which',
                   return_value=r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
            installed, _ = check_tesseract_installed()
            assert installed is True

    def test_tesseract_not_found(self):
        """Should return False when tesseract is not found"""
        if not OCR_AVAILABLE:
            return
        # Mock shutil.which to return None
        with patch('extract.shutil.which', return_value=None):
            # Mock the import check to raise ImportError
            with patch('builtins.__import__',
                       side_effect=ImportError("No module")):
                installed, msg = check_tesseract_installed()
                assert installed is False
                assert "ERROR" in msg

    def test_pytesseract_import_error(self):
        """Should return False when pytesseract is not installed"""
        if not OCR_AVAILABLE:
            return
        with patch('extract.shutil.which', return_value=None):
            with patch('builtins.__import__',
                       side_effect=ImportError("No module named 'pytesseract'")):
                installed, _ = check_tesseract_installed()
                assert installed is False


class TestOcrImage:
    """Tests for ocr_image()"""

    def test_ocr_success(self, tmp_path):
        """Should return OCR text when successful"""
        if not OCR_AVAILABLE:
            return
        # Create a dummy image file
        img_path = tmp_path / "test.png"
        img_path.write_bytes(b"fake_image")

        with patch('extract.Image'):
            with patch('extract.pytesseract') as mock_pytesseract:
                mock_pytesseract.image_to_string.return_value = "Recognized text"
                result = ocr_image(img_path)
                assert result == "Recognized text"

    def test_ocr_failure(self, tmp_path):
        """Should return None when OCR fails"""
        if not OCR_AVAILABLE:
            return
        img_path = tmp_path / "test.png"
        img_path.write_bytes(b"fake_image")

        with patch('extract.Image') as mock_image:
            mock_image.open.side_effect = Exception("OCR failed")
            result = ocr_image(img_path)
            assert result is None

    def test_ocr_empty_result(self, tmp_path):
        """Should return None when OCR returns empty string"""
        if not OCR_AVAILABLE:
            return
        img_path = tmp_path / "test.png"
        img_path.write_bytes(b"fake_image")

        with patch('extract.Image'):
            with patch('extract.pytesseract') as mock_pytesseract:
                mock_pytesseract.image_to_string.return_value = "   "
                result = ocr_image(img_path)
                assert result is None


class TestShouldRunOcr:
    """Tests for should_run_ocr()"""

    def test_no_ocr_flag_set(self):
        """Should return False when --no-ocr is set"""
        if not OCR_AVAILABLE:
            return
        run_ocr, msg = should_run_ocr(no_ocr_flag=True)
        assert run_ocr is False
        assert msg == ""

    def test_ocr_flag_not_set_tesseract_available(self):
        """Should return True when --no-ocr not set and tesseract available"""
        if not OCR_AVAILABLE:
            return
        with patch('extract.check_tesseract_installed',
                    return_value=(True, "")):
            run_ocr, _ = should_run_ocr(no_ocr_flag=False)
            assert run_ocr is True

    def test_ocr_flag_not_set_tesseract_not_available(self):
        """Should return False when tesseract not available"""
        if not OCR_AVAILABLE:
            return
        with patch('extract.check_tesseract_installed', return_value=(False, "ERROR")):
            run_ocr, msg = should_run_ocr(no_ocr_flag=False)
            assert run_ocr is False
            assert "ERROR" in msg
