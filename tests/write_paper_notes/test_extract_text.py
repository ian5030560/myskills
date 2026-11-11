"""CLI tests for extract_text.py: external behaviour only."""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "write-paper-notes" / "scripts"
SCRIPT = SCRIPTS_DIR / "extract_text.py"
NO_TEXT_FLAG = "此頁無文字層"


def _run(args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", cwd=cwd, check=False,
    )


def _extract(pdf, out_dir):
    result = _run(["--input", pdf, "--output-dir", out_dir])
    assert result.returncode == 0, result.stderr
    text_file = Path(out_dir) / Path(pdf).stem / "text.md"
    return result, text_file.read_text(encoding="utf-8")


class TestInput:
    @pytest.mark.parametrize("name", ["paper.docx", "notes.txt"])
    def test_non_pdf_is_rejected_with_save_as_pdf_hint(self, text_fixtures_dir, tmp_path, name):
        result = _run(["--input", text_fixtures_dir / name, "--output-dir", tmp_path])
        assert result.returncode != 0
        assert "PDF" in result.stderr
        assert not (tmp_path / Path(name).stem).exists()

    def test_missing_docx_still_gets_save_as_pdf_hint(self, tmp_path):
        result = _run(["--input", tmp_path / "missing.docx"])
        assert result.returncode != 0
        assert "PDF" in result.stderr

    def test_missing_pdf_fails(self, tmp_path):
        result = _run(["--input", tmp_path / "missing.pdf"])
        assert result.returncode != 0
        assert "not found" in result.stderr

    def test_default_output_dir_is_cwd_stem_folder(self, text_fixtures_dir, tmp_path):
        result = _run(["--input", text_fixtures_dir / "simple.pdf"], cwd=tmp_path)
        assert result.returncode == 0, result.stderr
        assert (tmp_path / "simple" / "text.md").is_file()


class TestStdout:
    def test_reports_path_and_page_count_not_the_text(self, text_fixtures_dir, tmp_path):
        result, text = _extract(text_fixtures_dir / "simple.pdf", tmp_path)
        assert str(tmp_path / "simple" / "text.md") in result.stdout
        assert "pages: 1" in result.stdout
        assert "Hello World" not in result.stdout
        assert "Hello World" in text

    def test_reports_pages_without_text_layer(self, text_fixtures_dir, tmp_path):
        result, _ = _extract(text_fixtures_dir / "partly_scanned.pdf", tmp_path)
        assert "no text layer: 2" in result.stdout

    def test_reports_none_when_every_page_has_text(self, text_fixtures_dir, tmp_path):
        result, _ = _extract(text_fixtures_dir / "simple.pdf", tmp_path)
        assert "no text layer: none" in result.stdout


class TestText:
    def test_page_markers(self, text_fixtures_dir, tmp_path):
        _, text = _extract(text_fixtures_dir / "running_header.pdf", tmp_path)
        for n in range(1, 5):
            assert f"<!-- p{n} -->" in text
        assert text.index("<!-- p1 -->") < text.index("PAGEBODY1") < text.index("<!-- p2 -->")

    def test_two_columns_read_left_then_right(self, text_fixtures_dir, tmp_path):
        _, text = _extract(text_fixtures_dir / "two_column.pdf", tmp_path)
        order = [text.index(w) for w in
                 ("SPANNING TITLE", "LEFTTOP", "LEFTBOTTOM", "RIGHTTOP", "RIGHTBOTTOM")]
        assert order == sorted(order)

    def test_running_headers_and_page_numbers_removed(self, text_fixtures_dir, tmp_path):
        _, text = _extract(text_fixtures_dir / "running_header.pdf", tmp_path)
        assert "Journal of Testing" not in text
        for n in range(1, 5):
            assert f"PAGEBODY{n}" in text
        assert not any(line.strip().isdigit() for line in text.splitlines())

    def test_merged_numbered_heading_gets_own_line(self, text_fixtures_dir, tmp_path):
        _, text = _extract(text_fixtures_dir / "merged_heading.pdf", tmp_path)
        assert "3.2. Method Details" in [line.strip() for line in text.splitlines()]

    def test_lines_joined_and_hyphenation_rejoined(self, text_fixtures_dir, tmp_path):
        _, text = _extract(text_fixtures_dir / "merged_heading.pdf", tmp_path)
        assert "We describe the experiment setup in this paragraph." in text

    def test_one_line_blocks_are_joined_into_paragraphs(self, text_fixtures_dir, tmp_path):
        _, text = _extract(text_fixtures_dir / "line_blocks.pdf", tmp_path)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        assert ("First paragraph line one continues across the page width here, "
                "and its second line keeps going with more words to read, "
                "ending the first paragraph here.") in lines
        assert ("Second paragraph starts with an indent and more words. "
                "It continues on a flush-left line.") in lines

    def test_captions_and_bullets_are_not_joined_to_paragraphs(self, text_fixtures_dir,
                                                               tmp_path):
        _, text = _extract(text_fixtures_dir / "line_blocks.pdf", tmp_path)
        lines = [line.strip() for line in text.splitlines()]
        assert "Figure 1. A caption right below the paragraph." in lines
        assert "- A bullet item on its own line." in lines

    def test_rotated_text_is_dropped(self, text_fixtures_dir, tmp_path):
        _, text = _extract(text_fixtures_dir / "line_blocks.pdf", tmp_path)
        assert "SIDEWAYS" not in text

    def test_reference_page_continuations_are_not_headings(self, text_fixtures_dir, tmp_path):
        _, text = _extract(text_fixtures_dir / "references.pdf", tmp_path)
        lines = [line.strip() for line in text.splitlines()]
        assert "346. Springer, 2019. 3" not in lines
        assert "14. SIAM, 2001. 4" not in lines
        assert "2 Background and Related Work" in lines

    def test_no_heading_markers(self, text_fixtures_dir, tmp_path):
        _, text = _extract(text_fixtures_dir / "merged_heading.pdf", tmp_path)
        assert not any(line.startswith("#") for line in text.splitlines())

    def test_page_without_text_layer_is_flagged(self, text_fixtures_dir, tmp_path):
        _, text = _extract(text_fixtures_dir / "partly_scanned.pdf", tmp_path)
        before, after = text.split("<!-- p2 -->", 1)
        assert NO_TEXT_FLAG in after
        assert NO_TEXT_FLAG not in before

    def test_fully_scanned_pdf_does_not_fail(self, text_fixtures_dir, tmp_path):
        _, text = _extract(text_fixtures_dir / "fully_scanned.pdf", tmp_path)
        assert text.count(NO_TEXT_FLAG) == 2
