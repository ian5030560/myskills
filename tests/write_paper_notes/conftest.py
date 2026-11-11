"""Fixtures for write-paper-notes tests. Every PDF is generated at runtime."""

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


# ── extract_text.py fixtures ──────────────────────────────────────────


def _body_paragraph(n):
    return f"Body paragraph {n} explains the method in enough words to fill a line. " * 3


def _create_two_column_pdf(path):
    doc = fitz.open()
    page = doc.new_page()  # 595 x 842
    page.insert_textbox((60, 60, 535, 90), "SPANNING TITLE ACROSS BOTH COLUMNS", fontsize=14)
    page.insert_textbox((60, 120, 285, 300), "LEFTTOP " + _body_paragraph(1), fontsize=9)
    page.insert_textbox((60, 320, 285, 500), "LEFTBOTTOM " + _body_paragraph(2), fontsize=9)
    page.insert_textbox((310, 120, 535, 300), "RIGHTTOP " + _body_paragraph(3), fontsize=9)
    page.insert_textbox((310, 320, 535, 500), "RIGHTBOTTOM " + _body_paragraph(4), fontsize=9)
    doc.save(str(path))
    doc.close()


def _create_running_header_pdf(path):
    doc = fitz.open()
    for i in range(4):
        page = doc.new_page()
        page.insert_text((60, 40), f"Journal of Testing Vol. {i + 3}", fontsize=8)
        page.insert_textbox((60, 120, 535, 400), f"PAGEBODY{i + 1} " + _body_paragraph(i),
                            fontsize=10)
        page.insert_text((290, 815), str(i + 1), fontsize=8)
    doc.save(str(path))
    doc.close()


def _create_merged_heading_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    text = ("the previous section ends with this sentence about results.\n"
            "3.2. Method Details\n"
            "We describe the experi-\n"
            "ment setup in this paragraph.")
    page.insert_textbox((60, 100, 535, 300), text, fontsize=10)
    doc.save(str(path))
    doc.close()


def _create_line_blocks_pdf(path):
    """Widely spaced lines, so PyMuPDF puts every line in its own block."""
    doc = fitz.open()
    page = doc.new_page()
    y = 100
    for x, text in (
            (72, "First paragraph line one continues across the page width here,"),
            (72, "and its second line keeps going with more words to read,"),
            (72, "ending the first paragraph here."),
            (86, "Second paragraph starts with an indent and more words."),
            (72, "It continues on a flush-left line."),
            (72, "Figure 1. A caption right below the paragraph."),
            (72, "- A bullet item on its own line.")):
        page.insert_text((x, y), text, fontsize=10)
        y += 21
    page.insert_text((30, 600), "SIDEWAYS publisher marker", fontsize=10, rotate=90)
    doc.save(str(path))
    doc.close()


def _create_references_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    text = ("[30] Some Author and Another Author. A paper title. In Proceedings, pages 1-\n"
            "346. Springer, 2019. 3\n"
            "14. SIAM, 2001. 4\n"
            "2 Background and Related Work\n"
            "Body text after the heading.")
    page.insert_textbox((60, 100, 535, 300), text, fontsize=10)
    doc.save(str(path))
    doc.close()


def _add_image_only_page(doc):
    page = doc.new_page()
    tmp = fitz.open()
    tp = tmp.new_page()
    tp.insert_text((50, 100), "Scanned words", fontsize=24)
    pix = tp.get_pixmap(dpi=72)
    tmp.close()
    page.insert_image(page.rect, pixmap=pix)


def _create_partly_scanned_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Real text on page one.", fontsize=10)
    _add_image_only_page(doc)
    doc.save(str(path))
    doc.close()


def _create_fully_scanned_pdf(path):
    doc = fitz.open()
    _add_image_only_page(doc)
    _add_image_only_page(doc)
    doc.save(str(path))
    doc.close()


@pytest.fixture(scope="session")
def text_fixtures_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("text_fixtures")
    _create_two_column_pdf(d / "two_column.pdf")
    _create_running_header_pdf(d / "running_header.pdf")
    _create_merged_heading_pdf(d / "merged_heading.pdf")
    _create_line_blocks_pdf(d / "line_blocks.pdf")
    _create_references_pdf(d / "references.pdf")
    _create_partly_scanned_pdf(d / "partly_scanned.pdf")
    _create_fully_scanned_pdf(d / "fully_scanned.pdf")
    _create_simple_pdf(d / "simple.pdf")
    (d / "paper.docx").write_bytes(b"not really a docx")
    (d / "notes.txt").write_text("plain text", encoding="utf-8")
    _create_blank_pages_pdf(d / "blank_pages.pdf")
    return d


# ── crop_figure.py fixtures ───────────────────────────────────────────
# A4 pages (595 x 842 pt). Coordinates below are exported so tests can check the
# printed final box against the real figure/caption/paragraph positions.

CROP_PAGE = (595, 842)
CROP_LAYOUT = {
    "header_bottom": 46,
    "fig1": (100, 100, 495, 300),
    "caption1_top": 312,
    "para1": (60, 335, 535, 420),
    "fig2": (100, 450, 495, 600),
    "caption2_top": 612,
    "text_fig": (100, 100, 495, 330),
    "left_para": (60, 100, 285, 700),
    "right_fig": (310, 100, 535, 300),
}


def _body_lines(n):
    return " ".join(["This body paragraph explains the experimental setup in plain words."] * n)


def _running_header(page, number):
    page.insert_text((60, 40), "Journal of Testing Vol. 3", fontsize=8)
    page.insert_text((290, 815), str(number), fontsize=8)


def _drawn_figure(page, rect, label):
    x0, y0, x1, y1 = rect
    page.draw_rect(fitz.Rect(x0, y0, x1, y1), color=(0, 0, 0), width=1)
    page.draw_rect(fitz.Rect(x0 + 20, y0 + 20, x0 + 120, y1 - 20), color=(0.2, 0.3, 0.8),
                   fill=(0.6, 0.7, 0.9))
    page.draw_rect(fitz.Rect(x1 - 120, y0 + 20, x1 - 20, y1 - 20), color=(0.2, 0.6, 0.3),
                   fill=(0.7, 0.9, 0.7))
    page.draw_line((x0 + 120, (y0 + y1) / 2), (x1 - 120, (y0 + y1) / 2), color=(0, 0, 0), width=2)
    page.insert_text((x0 + 30, y0 + 15), f"{label} input", fontsize=7)
    page.insert_text((x1 - 110, y0 + 15), f"{label} output", fontsize=7)


def _create_crop_pdf(path):
    lay = CROP_LAYOUT
    doc = fitz.open()

    # Page 1: two stacked drawn figures, each with a caption below and a body paragraph.
    page = doc.new_page(width=CROP_PAGE[0], height=CROP_PAGE[1])
    _running_header(page, 1)
    _drawn_figure(page, lay["fig1"], "Stage")
    page.insert_text((100, lay["caption1_top"] + 8), "Figure 1. Overview of the pipeline.",
                     fontsize=9)
    page.insert_textbox(lay["para1"], _body_lines(6), fontsize=10)
    _drawn_figure(page, lay["fig2"], "Step")
    page.insert_text((100, lay["caption2_top"] + 8), "Figure 2. A second stacked figure.",
                     fontsize=9)
    page.insert_textbox((60, 640, 535, 760), _body_lines(8), fontsize=10)

    # Page 2: a text-only figure (bordered boxes of short bullet lines).
    page = doc.new_page(width=CROP_PAGE[0], height=CROP_PAGE[1])
    _running_header(page, 2)
    x0, y0, x1, y1 = lay["text_fig"]
    mid = (x0 + x1) / 2
    for box, title in (((x0, y0, mid - 10, y1), "Requirement Types"),
                       ((mid + 10, y0, x1, y1), "Requirement Formats")):
        page.draw_rect(fitz.Rect(box), color=(0, 0, 0), width=1)
        bullets = "\n".join(["- Functional requirements", "- Non-functional requirements",
                             "- User requirements", "- Constraint requirements",
                             "- Business requirements", "- Other"])
        page.insert_textbox((box[0] + 8, box[1] + 8, box[2] - 8, box[3] - 8),
                            title + "\n" + bullets, fontsize=8)
    page.insert_text((100, 350), "Figure 3. Taxonomy of requirement inputs.", fontsize=9)
    page.insert_textbox((60, 380, 535, 700), _body_lines(14), fontsize=10)

    # Page 3: two columns; a figure in the right column next to a left-column paragraph.
    page = doc.new_page(width=CROP_PAGE[0], height=CROP_PAGE[1])
    _running_header(page, 3)
    page.insert_textbox(lay["left_para"], _body_lines(20), fontsize=10)
    _drawn_figure(page, lay["right_fig"], "Col")
    page.insert_text((320, 318), "Figure 4. Right column figure.", fontsize=9)
    page.insert_textbox((310, 340, 535, 700), _body_lines(12), fontsize=10)

    doc.save(str(path))
    doc.close()


@pytest.fixture(name="layout")
def layout_fixture():
    """(page size, CROP_LAYOUT) of the generated crop.pdf, in points."""
    return CROP_PAGE, CROP_LAYOUT


@pytest.fixture(scope="session")
def crop_pages_dir(tmp_path_factory):
    """crop.pdf rendered with render_pages.py; returns <out>/crop/pages."""
    import subprocess  # pylint: disable=import-outside-toplevel
    d = tmp_path_factory.mktemp("crop_fixture")
    pdf = d / "crop.pdf"
    _create_crop_pdf(pdf)
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "render_pages.py"), "--input", str(pdf),
         "--output-dir", str(d / "out")],
        capture_output=True, text=True, encoding="utf-8", check=False)
    assert result.returncode == 0, result.stderr
    return d / "out" / "crop" / "pages"


def _create_blank_pages_pdf(path):
    doc = fitz.open()
    doc.new_page(width=612, height=792)  # letter
    doc.new_page(width=595, height=842)  # A4
    doc.new_page(width=612, height=792)
    doc.save(str(path))
    doc.close()
