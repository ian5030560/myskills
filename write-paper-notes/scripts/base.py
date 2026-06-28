#!/usr/bin/env python3
"""Abstract base class for document extractors."""

import io
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytesseract
from PIL import Image


@dataclass
class PageElement:
    kind: str
    bbox: tuple
    markdown: str


def ocr_image_bytes(img_bytes: bytes, _ext: str = "", ocr_language: str = "eng") -> Optional[str]:
    try:
        image = Image.open(io.BytesIO(img_bytes))
        if image.width < 3 or image.height < 3:
            return None
        text = pytesseract.image_to_string(image, lang=ocr_language).strip()
        return text or None
    except (OSError, pytesseract.TesseractError, RuntimeError):
        return None


def format_table(table) -> str:
    data = table.extract()
    if not data or not data[0]:
        return "*Empty table*"

    col_count = max(len(row) for row in data)

    lines = []
    lines.append("| " + " | ".join(str(c) if c else "" for c in data[0]) + " |")
    lines.append("| " + " | ".join(["---"] * col_count) + " |")
    for row in data[1:]:
        while len(row) < col_count:
            row.append("")
        lines.append("| " + " | ".join(str(c) if c else "" for c in row) + " |")

    return "\n".join(lines) + "\n"


def clean_output(text: str) -> str:
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()


class DocumentExtractor(ABC):
    def __init__(self, file_path: str, output_dir: Path,
                 use_ocr: bool = True, ocr_language: str = "eng"):
        self.file_path = file_path
        self.output_dir = output_dir
        self.image_dir = output_dir / "images"
        self.use_ocr = use_ocr
        self.ocr_language = ocr_language

    def extract(self) -> str:
        self._setup_directories()
        self.load()
        try:
            return self.do_extract()
        finally:
            self.close()

    def _setup_directories(self):
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.image_dir.mkdir(exist_ok=True, parents=True)

    @abstractmethod
    def load(self):
        """Open the document."""

    @abstractmethod
    def close(self):
        """Close the document."""

    @abstractmethod
    def do_extract(self) -> str:
        """Extract content and return a Markdown string."""
