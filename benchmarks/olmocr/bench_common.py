"""Shared constants and helpers for the olmOCR-Bench scripts."""

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DATA = HERE / "data"
BENCH_DIR = DATA / "bench_data"        # downloaded dataset, same layout as the HF repo
WORK = DATA / "work"                   # per-run extraction output and the scored copy
VENV = HERE / ".venv"
EXTRACT_SCRIPT = REPO / "write-paper-notes" / "scripts" / "extract_text.py"
BASELINE = HERE / "baseline.json"
KNOWN_BAD = HERE / "known_bad_tests.txt"

SCORER_REQUIREMENTS = ["olmocr[bench]==0.4.27", "numpy"]   # numpy: undeclared upstream (#452)
SCORER_VERSION = "olmocr 0.4.27"
MIN_PYTHON = (3, 11)
HF_BASE = "https://huggingface.co/datasets/allenai/olmOCR-bench/resolve/main/bench_data"
# multi_column: reading order; long_tiny_text: small text kept. See README for what is excluded.
CATEGORIES = ("multi_column", "long_tiny_text")


def venv_python() -> Path:
    sub = "Scripts/python.exe" if os.name == "nt" else "bin/python"
    return VENV / sub


def read_jsonl(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def die(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)
