import sys
from pathlib import Path

import pytest
import fitz

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "write-paper-notes" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def _create_simple_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello World - Paper Notes", fontsize=12)
    page.insert_text((72, 100), "This is a test paper document.", fontsize=10)
    doc.save(str(path))
    doc.close()


def _create_multi_page_pdf(path):
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((72, 72), f"Section {i+1}: Paper content", fontsize=12)
    doc.save(str(path))
    doc.close()


def _create_images_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Paper with figures", fontsize=12)
    tmp = fitz.open()
    tp = tmp.new_page()
    tp.insert_text((50, 100), "Figure 1: Results chart", fontsize=24)
    pix = tp.get_pixmap(dpi=150)
    tmp.close()
    page.insert_image((72, 100, 372, 350), pixmap=pix)
    doc.save(str(path))
    doc.close()


def _create_vector_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Paper with vector diagrams", fontsize=12)

    page.draw_rect(fitz.Rect(100, 150, 250, 200), color=(0, 0, 1), width=1.5)
    page.insert_text((120, 175), "Step 1", fontsize=10)

    page.draw_line(fitz.Point(175, 200), fitz.Point(175, 240), color=(0, 0, 1))

    page.draw_rect(fitz.Rect(100, 240, 250, 290), color=(0, 0, 1), width=1.5)
    page.insert_text((120, 265), "Step 2", fontsize=10)

    page.draw_circle(fitz.Point(400, 200), 30, color=(1, 0, 0), width=1.5)
    page.insert_text((390, 200), "Y/N", fontsize=8)

    doc.save(str(path))
    doc.close()


@pytest.fixture(scope="session")
def fixtures_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("fixtures")
    _create_simple_pdf(d / "simple.pdf")
    _create_multi_page_pdf(d / "multi_page.pdf")
    _create_images_pdf(d / "images.pdf")
    _create_vector_pdf(d / "vector.pdf")
    return d


@pytest.fixture
def simple_pdf(fixtures_dir):
    return fixtures_dir / "simple.pdf"


@pytest.fixture
def multi_page_pdf(fixtures_dir):
    return fixtures_dir / "multi_page.pdf"


@pytest.fixture
def images_pdf(fixtures_dir):
    return fixtures_dir / "images.pdf"


@pytest.fixture
def vector_pdf(fixtures_dir):
    return fixtures_dir / "vector.pdf"


@pytest.fixture
def output_dir(tmp_path):
    d = tmp_path / "output"
    d.mkdir()
    return d
