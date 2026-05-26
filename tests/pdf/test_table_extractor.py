import subprocess
import sys
from pathlib import Path

import fitz
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "pdf" / "scripts"
TABLE_SCRIPT = SCRIPTS_DIR / "pdf_table_extractor.py"


def _create_table_pdf(path):
    doc = fitz.open()
    page = doc.new_page()

    data = [
        ["Name", "Score", "Grade"],
        ["Alice", "95", "A"],
        ["Bob", "82", "B"],
        ["Charlie", "67", "C"],
    ]

    x0, y0, row_h, col_w = 50, 100, 30, 120

    page.draw_rect((x0, y0, x0 + col_w * 3, y0 + row_h * len(data)),
                   width=1, color=(0, 0, 0), fill=None)
    for i in range(1, len(data)):
        y = y0 + i * row_h
        page.draw_line((x0, y), (x0 + col_w * 3, y), width=1, color=(0, 0, 0))
    for i in range(1, 3):
        x = x0 + i * col_w
        page.draw_line((x, y0), (x, y0 + row_h * len(data)),
                       width=1, color=(0, 0, 0))

    for r, row in enumerate(data):
        for c, val in enumerate(row):
            page.insert_text((x0 + c * col_w + 4, y0 + r * row_h + 20),
                             val, fontsize=11)

    doc.save(str(path))
    doc.close()


def _create_borderless_pdf(path):
    doc = fitz.open()
    page = doc.new_page()

    lines = [
        "Feature  Free  Pro  Enterprise",
        "Users    1    10   Unlimited",
        "Storage  1GB  100GB  Unlimited",
    ]

    page.insert_text((72, 100), "Pricing Table", fontsize=14)
    for i, line in enumerate(lines):
        page.insert_text((72, 130 + i * 20), line, fontsize=10)

    doc.save(str(path))
    doc.close()


def _run(args):
    return subprocess.run(
        [sys.executable, str(TABLE_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8",
    )


class TestTableExtractor:

    @pytest.fixture
    def table_pdf(self, tmp_path):
        path = tmp_path / "table.pdf"
        _create_table_pdf(path)
        return path

    @pytest.fixture
    def borderless_pdf(self, tmp_path):
        path = tmp_path / "borderless.pdf"
        _create_borderless_pdf(path)
        return path

    def test_extracts_tables_from_grid_pdf(self, table_pdf, output_dir):
        result = _run(["--pdf", str(table_pdf), "--output-dir", str(output_dir)])
        assert result.returncode == 0

        out_file = output_dir / table_pdf.stem / "tables.md"
        assert out_file.exists()

        content = out_file.read_text("utf-8")
        assert "Name" in content
        assert "Score" in content
        assert "Grade" in content
        assert "Alice" in content
        assert "Bob" in content
        assert "Charlie" in content

    def test_table_markdown_format(self, table_pdf, output_dir):
        result = _run(["--pdf", str(table_pdf), "--output-dir", str(output_dir)])
        assert result.returncode == 0

        content = (output_dir / table_pdf.stem / "tables.md").read_text("utf-8")
        assert "| Name " in content
        assert "| --- " in content
        assert "| Alice " in content
        assert "# Extracted Tables" in content
        assert "Page 1" in content

    def test_file_not_found(self):
        result = _run(["--pdf", "nonexistent.pdf"])
        assert result.returncode == 1
        assert "file not found" in result.stderr

    def test_empty_pdf_no_crash(self, output_dir):
        doc = fitz.open()
        doc.new_page()
        empty_path = output_dir / "empty.pdf"
        doc.save(str(empty_path))
        doc.close()

        result = _run(["--pdf", str(empty_path), "--output-dir", str(output_dir)])
        assert result.returncode == 0

        out_file = output_dir / "empty" / "tables.md"
        assert out_file.exists()
        assert (output_dir / "empty" / "tables.md").read_text("utf-8").startswith("# Extracted Tables")

    def test_borderless_table_fallback(self, borderless_pdf, output_dir):
        result = _run(["--pdf", str(borderless_pdf), "--output-dir", str(output_dir)])
        assert result.returncode == 0

        out_file = output_dir / borderless_pdf.stem / "tables.md"
        assert out_file.exists()
        content = out_file.read_text("utf-8")
        assert "# Extracted Tables" in content
