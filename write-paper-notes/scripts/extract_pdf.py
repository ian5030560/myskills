#!/usr/bin/env python3
"""
PDF extraction logic for paper notes.

Uses PyMuPDF (fitz) for text, table, image, and vector graphic extraction.
"""

from collections import defaultdict

import fitz

from base import DocumentExtractor, PageElement, clean_output, format_table, ocr_image_bytes


def _is_significant_drawing(cluster_rect, paths) -> bool:
    dim = cluster_rect.width if cluster_rect.width > cluster_rect.height else cluster_rect.height
    d = dim * 0.025
    inner = cluster_rect + (d, d, -d, -d)

    my_paths = [p for p in paths if p["rect"] in cluster_rect]
    if not my_paths:
        return False

    if len(my_paths) == 1:
        pr = my_paths[0]["rect"]
        return not pr.is_empty and not (pr & inner).is_empty

    widths = set(round(p["rect"].width) for p in my_paths) | {round(cluster_rect.width)}
    heights = set(round(p["rect"].height) for p in my_paths) | {round(cluster_rect.height)}
    if len(widths) == 1 or len(heights) == 1:
        return False

    for p in my_paths:
        pr = p["rect"]
        if not (pr.is_empty or (pr & inner).is_empty):
            return True
    return False


def _build_header_id_map(doc: fitz.Document, body_limit: float = 12,
                         max_levels: int = 6) -> tuple:
    fontsizes = defaultdict(int)
    for pno in range(doc.page_count):
        page = doc.load_page(pno)
        blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]
        for span in (
            s
            for b in blocks if b["type"] == 0
            for l in b["lines"]
            for s in l["spans"]
            if s["text"].strip()
        ):
            fontsz = round(span["size"])
            fontsizes[fontsz] += len(span["text"].strip())

    temp = sorted(fontsizes.items(), key=lambda i: (i[1], i[0]))
    if temp:
        body_limit = max(body_limit, temp[-1][0])

    sizes = sorted(
        [f for f in fontsizes if f > body_limit],
        reverse=True,
    )[:max_levels]

    header_id = {}
    for i, size in enumerate(sizes, start=1):
        header_id[size] = "#" * i + " "
    if header_id:
        body_limit = min(header_id) - 1

    return body_limit, header_id


def _get_header_id(span: dict, body_limit: float, header_id: dict) -> str:
    fontsize = round(span["size"])
    if fontsize <= body_limit:
        return ""
    return header_id.get(fontsize, "")


class PdfExtractor(DocumentExtractor):
    def __init__(self, file_path: str, output_dir, use_ocr: bool = True, ocr_language: str = "eng"):
        super().__init__(file_path, output_dir, use_ocr=use_ocr, ocr_language=ocr_language)
        self._doc = None

    def load(self):
        self._doc = fitz.open(self.file_path)

    def close(self):
        if self._doc:
            self._doc.close()

    def do_extract(self) -> str:
        body_limit, header_id = _build_header_id_map(self._doc)

        pages_md = []
        for page_num, page in enumerate(self._doc):
            dict_blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]

            table_elements, table_bboxes = self._page_tables(page)

            text_elems = self._page_text(dict_blocks, body_limit, header_id, table_bboxes)
            image_elems = self._page_images(page, dict_blocks, page_num, table_bboxes)
            vector_elems = self._page_vectors(page, page_num)

            elements = table_elements + text_elems + image_elems + vector_elems
            elements.sort(key=lambda e: (round(e.bbox[0], -1), e.bbox[1]))

            merged = self._merge_heading_blocks(elements)

            pages_md.append("\n\n".join(e.markdown for e in merged))

        return clean_output("\n\n".join(pages_md))

    def _page_text(self, blocks: list, body_limit: float,
                   header_id: dict, skip_bboxes: list) -> list:
        elements = []
        for block in blocks:
            if block["type"] != 0:
                continue

            bbox = block["bbox"]
            if self._overlaps_any(bbox, skip_bboxes):
                continue

            spans = [s for line in block["lines"] for s in line["spans"]]
            if not spans:
                continue

            first = spans[0]
            full_text = " ".join(s["text"] for s in spans).strip()
            if not full_text:
                continue

            hdr = _get_header_id(first, body_limit, header_id)
            if hdr:
                elements.append(PageElement(f"h{len(hdr.strip())}", bbox, hdr + full_text))
                continue

            if self._is_list_item(full_text):
                cleaned = full_text.lstrip("•-*·0123456789.)(（").strip()
                elements.append(PageElement("list", bbox, "- " + cleaned))
                continue

            elements.append(PageElement("text", bbox, full_text))

        return elements

    def _page_tables(self, page: fitz.Page) -> tuple:
        tables = page.find_tables()
        elements = []
        bboxes = []
        for table in tables.tables:
            if table.row_count < 2 or table.col_count < 2:
                continue
            bbox = tuple(table.bbox)
            md = format_table(table)
            elements.append(PageElement("table", bbox, md))
            bboxes.append(bbox)
        return elements, bboxes

    def _page_images(self, page: fitz.Page, blocks: list,
                     page_num: int, skip_bboxes: list) -> list:
        img_dict_blocks = [b for b in blocks if b["type"] == 1]
        all_xrefs = [img[0] for img in page.get_images(full=True) if img[0] != 0]
        if not all_xrefs:
            return []

        elements = []
        for idx, xref in enumerate(all_xrefs):
            try:
                base = self._doc.extract_image(xref)
            except (RuntimeError, ValueError):
                continue

            bbox = (0, 0, 0, 0)
            if idx < len(img_dict_blocks):
                bbox = img_dict_blocks[idx]["bbox"]

            if self._overlaps_any(bbox, skip_bboxes):
                continue

            ext = base["ext"] or "png"
            img_filename = f"{page_num + 1:04d}_{idx + 1:02d}.{ext}"

            (self.image_dir / img_filename).write_bytes(base["image"])

            md = f"\n![Image](images/{img_filename})\n"
            if self.use_ocr:
                ocr_text = ocr_image_bytes(base["image"], ext, self.ocr_language)
                if ocr_text:
                    md += ocr_text + "\n"

            elements.append(PageElement("image", bbox, md))

        return elements

    def _page_vectors(self, page: fitz.Page, page_num: int) -> list:
        paths = page.get_drawings()
        if not paths:
            return []

        page_rect = page.rect
        filtered_paths = [
            p for p in paths
            if p["rect"].width < page_rect.width * 0.95
            and p["rect"].height < page_rect.height * 0.95
            and p["rect"].width > 5
            and p["rect"].height > 5
        ]
        if not filtered_paths:
            return []

        clusters = page.cluster_drawings(
            drawings=filtered_paths,
            x_tolerance=20,
            y_tolerance=20,
        )

        elements = []
        for vg_idx, cluster_rect in enumerate(clusters):
            if _is_significant_drawing(cluster_rect, filtered_paths):
                pix = page.get_pixmap(clip=cluster_rect, dpi=150)
                img_filename = f"{page_num + 1:04d}_v{vg_idx + 1:02d}.png"
                pix.save(str(self.image_dir / img_filename))
                md = f"\n![Vector Graphic](images/{img_filename})\n"
                elements.append(PageElement("vector", tuple(cluster_rect), md))

        return elements

    @staticmethod
    def _overlaps_any(rect, bbox_list) -> bool:
        for b in bbox_list:
            if (rect[0] < b[2] and rect[2] > b[0]
                    and rect[1] < b[3] and rect[3] > b[1]):
                return True
        return False

    @staticmethod
    def _is_list_item(text: str) -> bool:
        if not text:
            return False
        s = text.strip()
        if not s:
            return False
        if s[0] in ("•", "-", "*", "·"):
            return True
        if len(s) > 1 and s[0].isdigit() and s[1] in (".", ")", "．"):
            return True
        if len(s) > 1 and s[0] in ("(", "（") and len(s) > 2 and s[1].isdigit():
            return True
        return False

    @staticmethod
    def _merge_heading_blocks(elements: list) -> list:
        if not elements:
            return []

        result = []
        prev = None
        for elem in elements:
            if (prev and elem.kind.startswith("h") and prev.kind.startswith("h")
                    and elem.kind == prev.kind):
                prev.markdown = prev.markdown.rstrip("\n") + " " + elem.markdown.lstrip("# ")
                continue
            result.append(elem)
            prev = elem
        return result
