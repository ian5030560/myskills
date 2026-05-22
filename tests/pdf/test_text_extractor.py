import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "pdf" / "scripts"
TEXT_SCRIPT = SCRIPTS_DIR / "pdf_text_extractor.py"


def _run(args: list[str]):
    return subprocess.run(
        [sys.executable, str(TEXT_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8",
    )


class TestTextExtractor:

    def test_plain_text_extraction(self, simple_pdf, output_dir):
        result = _run(["--pdf", str(simple_pdf), "--output-dir", str(output_dir)])
        assert result.returncode == 0
        out_file = output_dir / simple_pdf.stem / "output.md"
        assert out_file.exists()
        content = out_file.read_text(encoding="utf-8")
        assert "Hello World - Simple PDF" in content
        assert "This is a test document." in content

    def test_file_not_found(self):
        result = _run(["--pdf", "nonexistent.pdf"])
        assert result.returncode == 1
        assert "file not found" in result.stderr

    def test_markdown_format(self, simple_pdf, output_dir):
        result = _run(["--pdf", str(simple_pdf), "--format", "markdown",
                       "--output-dir", str(output_dir)])
        assert result.returncode == 0
        out_file = output_dir / simple_pdf.stem / "output.md"
        assert out_file.exists()
        content = out_file.read_text(encoding="utf-8")
        assert len(content) > 0
