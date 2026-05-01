"""
Tests for extraction functions in extract.py
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "write-paper-notes" / "scripts"))

# pylint: disable=wrong-import-position
from extract import (clean_text, extract_page_text, format_output,  # noqa: E402
                    extract_images, extract_tables)  # noqa: E402


class TestCleanText:
    """Tests for clean_text()"""

    def test_removes_extra_newlines(self):
        """Should reduce multiple newlines to max 2"""
        result = clean_text("a\n\n\nb")
        assert "\n\n" in result
        assert "\n\n\n" not in result

    def test_removes_extra_spaces(self):
        """Should reduce multiple spaces to single space"""
        result = clean_text("a   b")
        assert "a b" == result

    def test_strips_whitespace(self):
        """Should strip leading/trailing whitespace"""
        result = clean_text("  hello  ")
        assert result == "hello"

    def test_normal_text_unchanged(self):
        """Normal text should remain unchanged"""
        text = "This is a normal paragraph."
        assert clean_text(text) == text


class TestExtractPageText:
    """Tests for extract_page_text()"""

    def test_returns_list(self, mock_pdf_reader):
        """Should return a list of paragraphs"""
        page = mock_pdf_reader.pages[0]
        page.extract_text.return_value = "1. Introduction\n\nThis is intro."

        result = extract_page_text(mock_pdf_reader, 1)
        assert isinstance(result, list)

    def test_detects_heading(self, mock_pdf_reader):
        """Should detect heading and return correct level"""
        page = mock_pdf_reader.pages[0]
        page.extract_text.return_value = "1. Introduction\n\nThis is intro."

        result = extract_page_text(mock_pdf_reader, 1)
        assert len(result) > 0
        # First item should be a heading
        assert result[0]['level'] <= 3

    def test_paragraph_has_text(self, mock_pdf_reader):
        """Each paragraph should have text content"""
        page = mock_pdf_reader.pages[0]
        page.extract_text.return_value = "1. Introduction\n\nThis is intro."

        result = extract_page_text(mock_pdf_reader, 1)
        for para in result:
            assert 'text' in para
            assert para['text']

    def test_page_out_of_range(self, mock_pdf_reader):
        """Should handle invalid page numbers"""
        with patch.object(mock_pdf_reader, 'pages', []):
            result = extract_page_text(mock_pdf_reader, 1)
            assert result == []


class TestFormatOutput:
    """Tests for format_output()"""

    def test_includes_page_separator(self, mock_pdf_reader, sample_images_dict,
                                   sample_tables_dict):
        """Output should have page separators"""
        result = format_output(mock_pdf_reader, sample_images_dict,
                              sample_tables_dict)
        assert "--- Page 1 ---" in result

    def test_includes_images(self, mock_pdf_reader, sample_images_dict,
                            sample_tables_dict):
        """Output should include image markdown"""
        result = format_output(mock_pdf_reader, sample_images_dict,
                              sample_tables_dict)
        assert "![Figure" in result

    def test_includes_tables(self, mock_pdf_reader, sample_images_dict,
                             sample_tables_dict):
        """Output should include table markdown"""
        result = format_output(mock_pdf_reader, sample_images_dict,
                              sample_tables_dict)
        assert "Table 1" in result

    def test_empty_images_tables(self, mock_pdf_reader):
        """Should handle empty images and tables"""
        result = format_output(mock_pdf_reader, {}, {})
        assert "--- Page 1 ---" in result


class TestExtractImages:
    """Tests for extract_images()"""

    def test_creates_images_dir(self, mock_pdf_reader, temp_output_dir):
        """Should create images directory"""
        extract_images(mock_pdf_reader, temp_output_dir, run_ocr=False)
        assert (temp_output_dir / "images").exists()

    def test_returns_dict(self, mock_pdf_reader, temp_output_dir):
        """Should return a dictionary"""
        # Mock page.images with proper data
        mock_img = MagicMock()
        mock_img.data = b"fake_image_data"
        mock_pdf_reader.pages[0].images = [mock_img]
        mock_pdf_reader.pages[1].images = []

        result = extract_images(mock_pdf_reader, temp_output_dir,
                               run_ocr=False)
        assert isinstance(result, dict)

    def test_no_images(self, mock_pdf_reader, temp_output_dir):
        """Should handle pages with no images"""
        mock_pdf_reader.pages[0].images = []
        mock_pdf_reader.pages[1].images = []

        result = extract_images(mock_pdf_reader, temp_output_dir,
                               run_ocr=False)
        assert result == {}


class TestExtractTables:
    """Tests for extract_tables()"""

    @patch('extract.pypdf_table_extraction')
    def test_returns_dict(self, mock_pypdf_table_extraction,
                          mock_pdf_reader, tmp_path):
        """Should return a dictionary"""
        # Mock table extraction
        mock_table = MagicMock()
        mock_table.page_numbers = [1]
        mock_table.order = 0
        mock_table.to_markdown.return_value = "| A |\n|---|\n| 1 |"
        mock_pypdf_table_extraction.read_pdf.return_value = [mock_table]

        pdf_path = str(tmp_path / "test.pdf")
        Path(pdf_path).touch()

        result = extract_tables(mock_pdf_reader, pdf_path)
        assert isinstance(result, dict)
