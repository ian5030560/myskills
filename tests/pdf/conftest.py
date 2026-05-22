import sys
from pathlib import Path

import pytest
import fitz

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "pdf" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def _create_simple_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello World - Simple PDF", fontsize=12)
    page.insert_text((72, 100), "This is a test document.", fontsize=10)
    doc.save(str(path))
    doc.close()


def _create_multi_page_pdf(path):
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {i+1} - Multi-page test", fontsize=12)
    doc.save(str(path))
    doc.close()


def _create_images_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Page with image", fontsize=12)
    # Create a page with text, render it to a pixmap, then embed as image
    # (so OCR has actual text to read)
    tmp = fitz.open()
    tp = tmp.new_page()
    tp.insert_text((50, 100), "OCR test text here", fontsize=24)
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
    doc = fitz.open(str(d / "simple.pdf"))
    doc.save(str(d / "secure.pdf"), encryption=fitz.PDF_ENCRYPT_AES_256,
             user_pw="user123", owner_pw="owner123")
    doc.close()
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
def secure_pdf(fixtures_dir):
    return fixtures_dir / "secure.pdf"


@pytest.fixture
def output_dir(tmp_path):
    d = tmp_path / "output"
    d.mkdir()
    return d
