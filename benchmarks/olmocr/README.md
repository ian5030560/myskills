# olmOCR-Bench for `extract_text.py`

Scores `write-paper-notes/scripts/extract_text.py` on part of [olmOCR-Bench](https://huggingface.co/datasets/allenai/olmOCR-bench) with the official scorer, and compares each run with a committed baseline. It is a development tool: manual, not part of pytest, and not shipped with any skill.

## Usage

Run from the repo root (or this folder). The scorer needs Python 3.11+ and about 660 MB of packages, so it gets its own venv here; everything else runs with the repo's Python.

```bash
python benchmarks/olmocr/setup_venv.py --python <path to Python 3.11+>   # once
python benchmarks/olmocr/fetch.py                                          # once, ~88 MB
python benchmarks/olmocr/run.py                                            # about a minute
python benchmarks/olmocr/run.py --update-baseline                          # accept this run as the new baseline
```

`run.py` extracts every PDF with the current `extract_text.py`, scores the output, and prints the pass rate per category plus the difference from `baseline.json`: the tests that newly fail and newly pass. It never exits with an error because a score dropped; deciding whether a change is acceptable is up to you. Flipped tests that upstream reports as wrong (`known_bad_tests.txt`) are annotated.

`data/` and `.venv/` are gitignored.

## What is scored

| Category | Test type | What it checks |
|---|---|---|
| `multi_column` | order | Reading order in multi-column pages, at the character level. |
| `long_tiny_text` | present | That small text is not dropped or garbled. |

Scoring is the official `olmocr` scorer, pinned to `olmocr[bench]==0.4.27` plus `numpy`, which the bench extra forgets to declare ([allenai/olmocr#452](https://github.com/allenai/olmocr/issues/452)). The scorer's automatic per-PDF baseline test (which only checks that a page has some text) is skipped. Each run scores the full sets; there is no sampling, so two runs are always comparable.

## What is left out, and why

- **PDFs with no text layer.** `write-paper-notes` does no OCR by design ([ADR 0001](../../docs/adr/0001-pdf-only-ai-cropped-figures.md)): such pages are flagged and the AI reads their page image. Scoring them would measure that design choice, not extraction quality. They are removed from the scored set and counted in the report (`excluded no-text PDFs`).
- **`headers_footers`.** Every bench PDF is a single page, while the running-header rule needs the same text on at least two pages, so these tests can never exercise it. The numbers below are a one-off diagnosis, not a rerunnable test (see the next section).
- **`arxiv_math`, `table_tests`, `old_scans`, `old_scans_math`.** The skill does not rebuild math or tables (the AI does that from page images) and does not OCR scans.

The `order` and `present` tests judge text with character-level fuzzy matching, so a failure usually means a changed character or missing word, not a wrong order. Known causes the extractor cannot fix: errors in a PDF's own OCR text layer, broken font encodings (en dashes or digits mapped to other glyphs), PDFs that store words without spaces, and drop caps or captions interleaved with body text.

### One-off diagnosis of `headers_footers`

Each bench test names the original document its page came from. Of the 266 sources, 102 (38%) could still be downloaded; the rest are dead links, bot walls or changed. On 90 of those originals, running `extract_text.py` on the whole document and scoring the matching page passed **79.1%** of the absent tests (201/254), against **39.4%** on the single-page bench PDFs. The 53 remaining failures were mostly cases the rule deliberately ignores:

- documents shorter than 3 pages (22);
- text that repeats but varies page to page, sits inside a longer block, or is not at the page edge (16);
- banners that appear only on one page (10);
- odd/even headers, each repeating on fewer than 30% of pages (5).

A rerunnable multi-page test set is not practical: the links rot, access depends on the visitor's IP, and the bench gives no license for the original documents.

## Baseline

`baseline.json` holds the date, the commit of `extract_text.py` it was recorded with, the scorer version, per-category counts, and the IDs of passing and failing tests. Update it with `--update-baseline` only after a change you accept.

| Date | `extract_text.py` | multi_column (order) | long_tiny_text (present) |
|---|---|---|---|
| 2026-11-18 | `f5755d8` (before the ligature and hyphenation fixes) | 620/841 = 73.7% | 221/262 = 84.4% |
| 2026-11-20 | ligatures expanded | 648/841 = 77.1% (+31 pass, 0 fail) | 224/262 = 85.5% |
| 2026-11-20 | + hyphenation rejoined (current baseline) | 651/841 = 77.4% | 225/262 = 85.9% |

Against the first row, the current state has 36 newly passing tests and 1 newly failing: `03b953c18a4f7d2bbe390940dec839395cdd_page_30.pdf_order_35288b10`, whose expected text keeps a column-end `occa-` (a bench transcription convention, not an extraction error).

## Windows notes

Three problems of the official scorer are worked around without editing the installed package or the data:

- **Path separators.** The scorer keys candidate files by `os.path.relpath` (backslashes) but looks tests up by the jsonl `pdf` field (forward slashes), so every test reports missing output and scores 0%. `scorer_wrapper.py` normalises the separators at run time; on other platforms it changes nothing. No upstream report exists for this.
- **Encoding.** The scorer reads the jsonl files without an encoding, which fails under a legacy code page such as cp950. `run.py` starts it with `PYTHONUTF8=1`.
- **Path length.** pip can hit the 260-character MAX_PATH limit while unpacking some packages. Keep this repo near the drive root, or enable long paths.

## Upstream issues that matter

- [allenai/olmocr#452](https://github.com/allenai/olmocr/issues/452): `numpy` missing from the bench extra (worked around in `setup_venv.py`).
- [allenai/olmocr#461](https://github.com/allenai/olmocr/issues/461): `partial_ratio` makes `present` tests pass on near-empty output. It does not affect these runs, because pages without text are excluded and flagged rather than left empty.
- [allenai/olmocr#485](https://github.com/allenai/olmocr/issues/485): some tests marked verified expect text that differs from the page. The 32 order and present tests among them are listed in `known_bad_tests.txt`. They are scored as-is, so scores stay comparable with the official ones; they fail before and after any change, so they do not distort deltas.

## License

The dataset is ODC-BY-1.0 and the scorer Apache-2.0. The individual bench PDFs carry no stated license, so they are downloaded into the gitignored `data/` folder and never committed.
