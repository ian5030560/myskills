"""
Tests for heading detection functions in extract.py
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "write-paper-notes" / "scripts"))

# pylint: disable=wrong-import-position
from extract import detect_heading_level, is_heading_line, level_to_markdown  # noqa: E402


class TestDetectHeadingLevel:
    """Tests for detect_heading_level()"""

    def test_roman_numeral_level2(self):
        """Roman numeral heading should return level 2"""
        assert detect_heading_level("I. Introduction") == 2
        assert detect_heading_level("IV. Methods") == 2

    def test_numeric_level2(self):
        """Numeric heading should return level 2"""
        assert detect_heading_level("1. Introduction") == 2
        assert detect_heading_level("10. Conclusion") == 2

    def test_subsection_level3(self):
        """Subsection heading should return level 3"""
        assert detect_heading_level("1.1. Methodology") == 3
        assert detect_heading_level("2.3. Results") == 3

    def test_subsubsection_level4(self):
        """Sub-subsection heading should return level 4"""
        assert detect_heading_level("1.1.1. Details") == 4
        assert detect_heading_level("2.3.1. Data Collection") == 4

    def test_lowercase_alpha_level4(self):
        """Lowercase alpha heading should return level 4"""
        assert detect_heading_level("a. First item") == 4
        assert detect_heading_level("b. Second item") == 4

    def test_parenthesized_level4(self):
        """Parenthesized number heading should return level 4"""
        assert detect_heading_level("(1) First") == 4
        assert detect_heading_level("(2) Second") == 4

    def test_bracketed_alpha_level4(self):
        """Bracketed alpha heading should return level 4"""
        assert detect_heading_level("[a] Item") == 4

    def test_bracketed_numeric_level4(self):
        """Bracketed numeric heading should return level 4"""
        assert detect_heading_level("[1] Reference") == 4

    def test_uppercase_short_level2(self):
        """Uppercase short line should return level 2"""
        assert detect_heading_level("Abstract") == 2
        assert detect_heading_level("Introduction") == 2

    def test_regular_text_level4(self):
        """Regular paragraph text should return level 4"""
        assert detect_heading_level("This is a paragraph of text.") == 4
        assert detect_heading_level("The results show that...") == 4

    def test_empty_line(self):
        """Empty line should return level 0"""
        assert detect_heading_level("") == 0
        assert detect_heading_level("   ") == 0


class TestLevelToMarkdown:
    """Tests for level_to_markdown()"""

    def test_level_1(self):
        """Level 1 should return #"""
        assert level_to_markdown(1) == "#"

    def test_level_2(self):
        """Level 2 should return ##"""
        assert level_to_markdown(2) == "##"

    def test_level_3(self):
        """Level 3 should return ###"""
        assert level_to_markdown(3) == "###"

    def test_level_4(self):
        """Level 4 should return ####"""
        assert level_to_markdown(4) == "####"

    def test_invalid_level(self):
        """Invalid level should return #"""
        assert level_to_markdown(99) == "#"


class TestIsHeadingLine:
    """Tests for is_heading_line()"""

    def test_roman_numeral_true(self):
        """Roman numeral heading should be True"""
        assert is_heading_line("I. Introduction") is True

    def test_numeric_heading_true(self):
        """Numeric heading should be True"""
        assert is_heading_line("1. Introduction") is True

    def test_subsection_true(self):
        """Subsection heading should be True"""
        assert is_heading_line("1.1. Methodology") is True

    def test_uppercase_title_true(self):
        """Uppercase title should be True"""
        assert is_heading_line("Abstract") is True
        assert is_heading_line("Introduction") is True

    def test_body_text_false(self):
        """Body text should be False"""
        assert is_heading_line("This is a paragraph of text.") is False

    def test_long_line_false(self):
        """Long lines should not be headings"""
        long_line = "A" * 201
        assert is_heading_line(long_line) is False

    def test_empty_line_false(self):
        """Empty line should be False"""
        assert is_heading_line("") is False
        assert is_heading_line("   ") is False
