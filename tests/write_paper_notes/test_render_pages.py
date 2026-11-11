"""CLI tests for render_pages.py: external behaviour only."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "write-paper-notes" / "scripts"
SCRIPT = SCRIPTS_DIR / "render_pages.py"
DPI = 110
PAGE_SIZES = [(612, 792), (595, 842), (612, 792)]  # blank_pages.pdf, in points


def _run(args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", cwd=cwd, check=False,
    )


@pytest.fixture(name="rendered")
def rendered_fixture(text_fixtures_dir, tmp_path):
    result = _run(["--input", text_fixtures_dir / "blank_pages.pdf", "--output-dir", tmp_path])
    assert result.returncode == 0, result.stderr
    return result, tmp_path / "blank_pages" / "pages"


class TestInput:
    @pytest.mark.parametrize("name", ["paper.docx", "notes.txt"])
    def test_non_pdf_is_rejected_with_save_as_pdf_hint(self, text_fixtures_dir, tmp_path, name):
        result = _run(["--input", text_fixtures_dir / name, "--output-dir", tmp_path])
        assert result.returncode != 0
        assert "PDF" in result.stderr
        assert not (tmp_path / Path(name).stem).exists()

    def test_missing_pdf_fails(self, tmp_path):
        result = _run(["--input", tmp_path / "missing.pdf"])
        assert result.returncode != 0
        assert "not found" in result.stderr

    def test_default_output_dir_is_cwd_stem_folder(self, text_fixtures_dir, tmp_path):
        result = _run(["--input", text_fixtures_dir / "simple.pdf"], cwd=tmp_path)
        assert result.returncode == 0, result.stderr
        assert (tmp_path / "simple" / "pages" / "p1.png").is_file()


class TestPages:
    def test_one_image_per_page(self, rendered):
        _, pages = rendered
        assert sorted(p.name for p in pages.glob("*.png")) == ["p1.png", "p2.png", "p3.png"]

    def test_images_are_rendered_at_110_dpi(self, rendered):
        _, pages = rendered
        for n, (w, h) in enumerate(PAGE_SIZES, start=1):
            with Image.open(pages / f"p{n}.png") as img:
                assert abs(img.width - w * DPI / 72) <= 1
                assert abs(img.height - h * DPI / 72) <= 1

    def test_faint_grid_is_drawn(self, rendered):
        _, pages = rendered
        w, h = PAGE_SIZES[0]
        y = round(h * 0.55 * DPI / 72)
        line_x = round(w * 0.5 * DPI / 72)
        with Image.open(pages / "p1.png") as img:
            img = img.convert("RGB")
            near_line = [img.getpixel((x, y)) for x in range(line_x - 2, line_x + 3)]
            off_line = img.getpixel((round(w * 0.55 * DPI / 72), y))
        assert off_line == (255, 255, 255)
        drawn = [px for px in near_line if px != (255, 255, 255)]
        assert drawn, "a grid line should cross the middle of the page"
        assert all(min(px) >= 150 for px in drawn), "grid line should be faint, not solid"

    def test_manifest_points_at_source_pdf(self, rendered, text_fixtures_dir):
        _, pages = rendered
        manifest = json.loads((pages / "source.json").read_text(encoding="utf-8"))
        source = Path(manifest["pdf"])
        assert source.is_absolute()
        assert source.samefile(text_fixtures_dir / "blank_pages.pdf")

    def test_stdout_reports_folder_and_page_count(self, rendered):
        result, pages = rendered
        assert str(pages) in result.stdout
        assert "pages: 3" in result.stdout

    def test_source_pdf_is_not_modified(self, text_fixtures_dir, tmp_path):
        pdf = text_fixtures_dir / "simple.pdf"
        before = pdf.read_bytes()
        assert _run(["--input", pdf, "--output-dir", tmp_path]).returncode == 0
        assert pdf.read_bytes() == before
