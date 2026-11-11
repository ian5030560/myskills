"""CLI tests for crop_figure.py: external behaviour only.

Trimming is checked through the final box the script prints (page fractions),
compared against the known layout of the generated PDF; no image analysis.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "write-paper-notes" / "scripts"
SCRIPT = SCRIPTS_DIR / "crop_figure.py"
DPI = 200
TOL = 0.004  # page-fraction tolerance (a few points)


def _run(args):
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + [str(a) for a in args],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )


def _crop(pages_dir, page, box, name):
    result = _run(["--page-image", pages_dir / f"p{page}.png", "--box", box, "--name", name])
    assert result.returncode == 0, result.stderr + result.stdout
    match = re.search(r"box: ([\d.]+),([\d.]+),([\d.]+),([\d.]+)", result.stdout)
    assert match, result.stdout
    return result, tuple(float(v) for v in match.groups())


def _contains(final, rect_pt, size):
    (w, h), (x0, y0, x1, y1) = size, rect_pt
    return (final[0] <= x0 / w + TOL and final[1] <= y0 / h + TOL
            and final[2] >= x1 / w - TOL and final[3] >= y1 / h - TOL)


class TestTrimming:
    def test_generous_box_keeps_figure_and_drops_header_caption_and_body(self, crop_pages_dir,
                                                                         layout):
        (w, h), lay = layout
        _, final = _crop(crop_pages_dir, 1, "0.05,0.0,0.95,0.52", "fig1")
        assert _contains(final, lay["fig1"], (w, h))
        assert final[1] > lay["header_bottom"] / h
        assert final[3] < lay["caption1_top"] / h

    def test_stacked_figure_drops_previous_caption_and_paragraph(self, crop_pages_dir, layout):
        (w, h), lay = layout
        _, final = _crop(crop_pages_dir, 1, "0.05,0.36,0.95,0.80", "fig2")
        assert _contains(final, lay["fig2"], (w, h))
        assert final[1] > lay["para1"][3] / h
        assert final[3] < lay["caption2_top"] / h

    def test_text_only_figure_is_not_peeled(self, crop_pages_dir, layout):
        size, lay = layout
        _, final = _crop(crop_pages_dir, 2, "0.1,0.08,0.9,0.5", "fig3")
        assert _contains(final, lay["text_fig"], size)

    def test_body_paragraph_crossing_side_edge_is_cut(self, crop_pages_dir, layout):
        (w, h), lay = layout
        _, final = _crop(crop_pages_dir, 3, "0.3,0.08,0.95,0.40", "fig4")
        assert final[0] > lay["left_para"][2] / w
        assert _contains(final, lay["right_fig"], (w, h))

    def test_box_with_only_body_text_fails(self, crop_pages_dir):
        result = _run(["--page-image", crop_pages_dir / "p1.png",
                       "--box", "0.1,0.40,0.9,0.49", "--name", "nothing"])
        assert result.returncode != 0
        assert "box" in result.stderr.lower()
        assert not (crop_pages_dir.parent / "images" / "nothing.png").exists()


class TestOutput:
    def test_image_written_to_images_at_200_dpi(self, crop_pages_dir, layout):
        (w, h), _ = layout
        result, final = _crop(crop_pages_dir, 1, "0.05,0.0,0.95,0.52", "size_check")
        out = crop_pages_dir.parent / "images" / "size_check.png"
        assert str(out) in result.stdout
        with Image.open(out) as img:
            assert abs(img.width - (final[2] - final[0]) * w * DPI / 72) <= 3
            assert abs(img.height - (final[3] - final[1]) * h * DPI / 72) <= 3

    def test_crop_has_no_grid(self, crop_pages_dir):
        # The page image has red grid lines crossing Fig. 1; the crop is re-rendered from
        # the PDF, so no red grid pixels may appear.
        _crop(crop_pages_dir, 1, "0.05,0.0,0.95,0.52", "grid_check")
        out = crop_pages_dir.parent / "images" / "grid_check.png"
        with Image.open(out) as img:
            img = img.convert("RGB")
            raw = img.tobytes()
            pixels = zip(raw[0::3], raw[1::3], raw[2::3])
            reds = [px for px in pixels if px[0] > 200 and px[1] < 120 and px[2] < 120]
        assert not reds

    def test_png_suffix_in_name_is_not_doubled(self, crop_pages_dir):
        _crop(crop_pages_dir, 1, "0.05,0.0,0.95,0.52", "named.png")
        assert (crop_pages_dir.parent / "images" / "named.png").is_file()


class TestErrors:
    @pytest.mark.parametrize("box", ["0.1,0.2,0.3", "a,b,c,d", "0.5,0.1,0.4,0.9", "0,0,1.2,1"])
    def test_invalid_box(self, crop_pages_dir, box):
        result = _run(["--page-image", crop_pages_dir / "p1.png", "--box", box, "--name", "x"])
        assert result.returncode != 0
        assert "box" in result.stderr.lower()

    def test_page_image_not_found(self, crop_pages_dir):
        result = _run(["--page-image", crop_pages_dir / "p99.png",
                       "--box", "0,0,1,1", "--name", "x"])
        assert result.returncode != 0
        assert "not found" in result.stderr

    def test_missing_manifest(self, crop_pages_dir, tmp_path):
        pages = tmp_path / "copy" / "pages"
        pages.mkdir(parents=True)
        shutil.copy(crop_pages_dir / "p1.png", pages / "p1.png")
        result = _run(["--page-image", pages / "p1.png", "--box", "0,0,1,1", "--name", "x"])
        assert result.returncode != 0
        assert "source.json" in result.stderr

    def test_manifest_points_at_missing_pdf(self, crop_pages_dir, tmp_path):
        pages = tmp_path / "moved" / "pages"
        pages.mkdir(parents=True)
        shutil.copy(crop_pages_dir / "p1.png", pages / "p1.png")
        (pages / "source.json").write_text(json.dumps({"pdf": str(tmp_path / "gone.pdf")}),
                                           encoding="utf-8")
        result = _run(["--page-image", pages / "p1.png", "--box", "0,0,1,1", "--name", "x"])
        assert result.returncode != 0
        assert "gone.pdf" in result.stderr
