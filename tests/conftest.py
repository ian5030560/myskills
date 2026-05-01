"""
Pytest configuration and fixtures for write-paper-notes tests
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "write-paper-notes" / "scripts"))


@pytest.fixture
def sample_pdf_path():
    """Return path to test PDF"""
    return Path(__file__).parent / "fixtures" / "sample.pdf"


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_pdf_reader():
    """Mock PdfReader object"""
    reader = MagicMock()
    reader.pages = [MagicMock(), MagicMock()]
    reader.__len__ = MagicMock(return_value=2)
    return reader


@pytest.fixture
def sample_images_dict():
    """Mock extracted images data"""
    return {
        1: [
            {'filename': 'figure_1_1.png', 'page': 1, 'index': 1,
             'ocr_text': None}
        ]
    }


@pytest.fixture
def sample_tables_dict():
    """Mock extracted tables data"""
    return {
        1: [
            {'index': 1, 'caption': 'Table 1: Results',
             'markdown': '| A | B |\n|---|---|\n| 1 | 2 |'}
        ]
    }


@pytest.fixture
def mock_extract_deps():
    """Unified mock for extract module dependencies"""
    with patch('extract.PdfReader') as mock_reader, \
         patch('extract.extract_images', return_value={}) as mock_img, \
         patch('extract.extract_tables', return_value={}) as mock_tbl, \
         patch('extract.format_output', return_value="") as mock_fmt:
        mock_reader.return_value.pages = []
        mock_reader.return_value.__len__ = MagicMock(return_value=0)
        yield {
            'reader': mock_reader,
            'extract_images': mock_img,
            'extract_tables': mock_tbl,
            'format_output': mock_fmt
        }


@pytest.fixture
def mock_extract_deps_with_pages():
    """Unified mock for extract module dependencies with mock pages"""
    with patch('extract.PdfReader') as mock_reader, \
         patch('extract.extract_images', return_value={}) as mock_img, \
         patch('extract.extract_tables', return_value={}) as mock_tbl, \
         patch('extract.format_output', return_value="") as mock_fmt:
        mock_page = MagicMock()
        mock_reader.return_value.pages = [mock_page, mock_page]
        mock_reader.return_value.__len__ = MagicMock(return_value=2)
        yield {
            'reader': mock_reader,
            'extract_images': mock_img,
            'extract_tables': mock_tbl,
            'format_output': mock_fmt
        }
