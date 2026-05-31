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


@pytest.fixture(scope="session")
def fixtures_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("fixtures")
    _create_simple_pdf(d / "simple.pdf")
    _create_multi_page_pdf(d / "multi_page.pdf")
    _create_images_pdf(d / "images.pdf")
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
def output_dir(tmp_path):
    d = tmp_path / "output"
    d.mkdir()
    return d
