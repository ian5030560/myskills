import subprocess
import sys
from pathlib import Path

import fitz
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "pdf" / "scripts"
MGR_SCRIPT = SCRIPTS_DIR / "pdf_manager.py"


def _run(args: list[str]):
    return subprocess.run(
        [sys.executable, str(MGR_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8",
    )


class TestManager:

    def test_merge(self, simple_pdf, output_dir):
        out = output_dir / "merged.pdf"
        result = _run(["merge", "--inputs", str(simple_pdf), str(simple_pdf),
                       "--output", str(out)])
        assert result.returncode == 0
        doc = fitz.open(str(out))
        assert len(doc) == 2, "Merged doc should have 2 pages"
        doc.close()

    def test_split(self, multi_page_pdf, output_dir):
        result = _run(["split", "--pdf", str(multi_page_pdf),
                       "--ranges", "1-2", "--output-dir", str(output_dir)])
        assert result.returncode == 0
        out_file = output_dir / f"{multi_page_pdf.stem}_0001-0002.pdf"
        assert out_file.exists()
        doc = fitz.open(str(out_file))
        assert len(doc) == 2
        doc.close()

    def test_split_single_page(self, multi_page_pdf, output_dir):
        result = _run(["split", "--pdf", str(multi_page_pdf),
                       "--ranges", "2", "--output-dir", str(output_dir)])
        assert result.returncode == 0
        out_file = output_dir / f"{multi_page_pdf.stem}_0002.pdf"
        assert out_file.exists()
        doc = fitz.open(str(out_file))
        assert len(doc) == 1
        doc.close()

    def test_rotate(self, simple_pdf, output_dir):
        out = output_dir / "rotated.pdf"
        result = _run(["rotate", "--pdf", str(simple_pdf),
                       "--pages", "1", "--angle", "90", "--output", str(out)])
        assert result.returncode == 0
        doc = fitz.open(str(out))
        assert doc[0].rotation == 90
        doc.close()

    def test_metadata_read(self, simple_pdf):
        result = _run(["metadata", "--pdf", str(simple_pdf), "--get"])
        assert result.returncode == 0

    def test_metadata_write(self, simple_pdf, output_dir):
        out = output_dir / "updated.pdf"
        result = _run(["metadata", "--pdf", str(simple_pdf),
                       "--set", "title=Test Title", "author=Tester",
                       "--output", str(out)])
        assert result.returncode == 0
        doc = fitz.open(str(out))
        assert doc.metadata.get("title") == "Test Title"
        assert doc.metadata.get("author") == "Tester"
        doc.close()
