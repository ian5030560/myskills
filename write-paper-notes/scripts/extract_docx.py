#!/usr/bin/env python3
"""DOCX extraction logic for paper notes."""

from pathlib import Path

from docx import Document as DocxDocument
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.table import Table as DocxTable

from base import DocumentExtractor, PageElement, clean_output, ocr_image_bytes


class DocxExtractor(DocumentExtractor):
    def __init__(self, file_path: str, output_dir,
                 use_ocr: bool = True, ocr_language: str = "eng"):
        super().__init__(file_path, output_dir, use_ocr=use_ocr, ocr_language=ocr_language)
        self._doc = None
        self._saved_images = {}

    def load(self):
        self._doc = DocxDocument(self.file_path)

    def close(self):
        self._doc = None

    def do_extract(self) -> str:
        self._save_images()
        elements = self._iter_body()
        return clean_output("\n\n".join(e.markdown for e in elements))

    def _save_images(self):
        for rel_id, rel in self._doc.part.rels.items():
            if "image" not in rel.reltype:
                continue
            image = rel.target_part
            ext = Path(image.partname).suffix.lstrip(".") or "png"
            idx = len(self._saved_images) + 1
            filename = f"docx_img_{idx:03d}.{ext}"
            (self.image_dir / filename).write_bytes(image.blob)
            self._saved_images[rel_id] = filename

    def _iter_body(self) -> list:
        elements = []
        for child in self._doc.element.body:
            tag = child.tag
            if tag == qn("w:p"):
                elem = self._process_paragraph(child)
                if elem:
                    elements.append(elem)
            elif tag == qn("w:tbl"):
                elem = self._process_table(child)
                if elem:
                    elements.append(elem)
        return elements

    def _process_paragraph(self, p_element) -> PageElement | None:
        para = Paragraph(p_element, self._doc)
        text = para.text.strip()
        inline_images = self._find_inline_images(p_element)

        if not text and not inline_images:
            return None

        style_name = para.style.name

        if style_name.startswith("Heading"):
            try:
                level = int(style_name.split()[-1])
                prefix = "#" * level + " "
                return PageElement(f"h{level}", (0, 0, 0, 0), prefix + text)
            except (ValueError, IndexError):
                pass

        if "List Bullet" in style_name:
            return PageElement("list", (0, 0, 0, 0), "- " + text)
        if "List Number" in style_name:
            return PageElement("list", (0, 0, 0, 0), "1. " + text)

        if inline_images:
            parts = [text] if text else []
            for img_id in inline_images:
                filename = self._saved_images.get(img_id)
                if not filename:
                    continue
                md = f"\n![Image](images/{filename})\n"
                if self.use_ocr:
                    img_bytes = self._get_image_bytes(img_id)
                    if img_bytes:
                        ext = Path(filename).suffix.lstrip(".")
                        ocr_text = ocr_image_bytes(img_bytes, ext, self.ocr_language)
                        if ocr_text:
                            md += ocr_text + "\n"
                parts.append(md)
            return PageElement("text", (0, 0, 0, 0), "\n".join(parts))

        return PageElement("text", (0, 0, 0, 0), text)

    def _find_inline_images(self, p_element) -> list:
        rel_ids = []
        for blip in p_element.iter(qn("a:blip")):
            embed = blip.get(qn("r:embed"))
            if embed and embed in self._saved_images:
                rel_ids.append(embed)
        return rel_ids

    def _get_image_bytes(self, rel_id: str) -> bytes | None:
        rel = self._doc.part.rels.get(rel_id)
        if rel and hasattr(rel, "target_part"):
            return rel.target_part.blob
        return None

    def _process_table(self, t_element) -> PageElement | None:
        table = DocxTable(t_element, self._doc)
        data = []
        for row in table.rows:
            data.append([cell.text.strip() for cell in row.cells])
        if not data or len(data) < 2:
            return None

        col_count = max(len(row) for row in data)
        lines = [
            "| " + " | ".join(data[0]) + " |",
            "| " + " | ".join(["---"] * col_count) + " |",
        ]
        for row in data[1:]:
            while len(row) < col_count:
                row.append("")
            lines.append("| " + " | ".join(row) + " |")
        return PageElement("table", (0, 0, 0, 0), "\n".join(lines) + "\n")
