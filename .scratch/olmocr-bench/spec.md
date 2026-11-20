Status: ready-for-agent

# write-paper-notes：用 olmOCR-Bench 評測 extract_text.py

相關文件：`GLOSSARY.md`、`docs/adr/0001-pdf-only-ai-cropped-figures.md`（不做 OCR、不重建表格與數學式）。本 spec 的決定來自一次 grilling；過程中以 80 份抽樣 PDF 量過現況（見 Further Notes）。

## Problem Statement

`extract_text.py` 決定了 AI 寫筆記時讀到的文字品質，但驗證手段只有兩種：

- conftest 產生的合成 PDF 單元測試，只涵蓋人工設計的版面。
- cs.pdf、survey.pdf 兩篇 e2e，樣本太少。

開發者改動擷取規則（欄位分帶、段落接合、頁首判斷）時：

- 無法知道在大量真實 PDF 上是變好還是變壞。
- 看不出哪一類失敗最值得修。
- 抽樣量測已經找到兩個可修的字元層問題：合字沒展開（`speciﬁcally`）、行尾斷字沒接回（`Sci- ence`），兩者都會讓文字比對失敗。但目前沒有可重跑的評測，能證明修正有效、沒有副作用。

## Solution

在 repo 內建立一套手動執行、可重跑的評測工具：

- 只用公開 olmOCR-Bench 中跟本 skill 有關的兩類：`multi_column`（閱讀順序）和 `long_tiny_text`（小字有沒有漏）。
- 用官方評分器計分，在獨立的 venv 執行，Windows 的路徑 bug 由 wrapper 繞過。
- 無文字層的 PDF 不計分，只報告數量；不做 OCR 是設計決定，不算擷取失敗。
- 結果存成 commit 進 repo 的 baseline。之後每次改 `extract_text.py`，重跑就能看到各類別的分數差值，以及新增失敗、新增通過的題目 ID。

工具完成、取得 baseline 後，修正合字和行尾斷字兩個問題，並用評測確認淨改善；若有個別題目退步，必須逐題說明原因。

抽樣實測（80 份單頁 PDF，排除無文字層）：multi_column 76.2%、long_tiny_text 87.1%。multi_column 的失敗全是字元層級的比對不到，沒有一題是順序錯。

## User Stories

1. As a skill developer, I want one setup command that creates an isolated venv for the official olmOCR scorer, so that its heavy dependencies never touch the repo's own venv.
2. As a skill developer, I want to pass the Python interpreter path to the setup command, so that it works whether Python 3.11+ comes from pyenv or elsewhere.
3. As a skill developer, I want the setup to pin the scorer to an exact released version and add its undeclared `numpy` dependency, so that rebuilding the venv never silently changes how tests are scored.
4. As a skill developer, I want the setup to fail with a clear message when the given Python is older than 3.11, so that I know what to fix.
5. As a skill developer, I want one fetch command that downloads only the `multi_column` and `long_tiny_text` test files and PDFs, so that I don't download categories we don't score.
6. As a skill developer, I want fetch to skip files that are already present, so that rerunning it is cheap.
7. As a skill developer, I want fetched data to live in a gitignored directory, so that PDFs with unclear licenses never enter the repo.
8. As a skill developer, I want one run command that extracts every bench PDF with the current `extract_text.py` and scores the output with the official scorer, so that a single command gives me the current score.
9. As a skill developer, I want the run to score the full set of both categories every time, so that two runs are always comparable.
10. As a skill developer, I want PDFs with no text layer excluded from scoring and their count reported, so that the score reflects extraction quality rather than the deliberate no-OCR design.
11. As a skill developer, I want the run to work on Windows despite the scorer's path-separator bug, so that I get real scores instead of 0%.
12. As a skill developer, I want the Windows workaround applied at run time without editing the installed package or the test files, so that reinstalling the scorer or refetching data doesn't break it.
13. As a skill developer, I want the run to print pass rates per category with test counts, so that I can read the result at a glance.
14. As a skill developer, I want the run to compare against a committed baseline and print the difference per category, so that I know whether my change helped.
15. As a skill developer, I want the run to list the test IDs that newly fail and newly pass versus the baseline, so that I can inspect exactly what my change did.
16. As a skill developer, I want flipped tests that belong to the known-bad set reported upstream flagged as such, so that I don't chase a wrong expected answer.
17. As a skill developer, I want the run never to fail just because the score dropped, so that the decision stays with me.
18. As a skill developer, I want an explicit flag that rewrites the baseline, so that updating it is always a deliberate act.
19. As a skill developer, I want the baseline to record the date, the commit of the extraction script, the scorer version, per-category pass rates, test counts, excluded PDF count and the per-test results, so that a later run can explain any difference.
20. As a skill developer, I want a README in the benchmark folder explaining what is scored, what is excluded and why (headers_footers single-page limit, no-text PDFs, math/tables/scans out of design scope, upstream issue on wrong expected answers), so that a future reader doesn't re-litigate these choices.
21. As a skill developer, I want the README to record the one-off headers_footers diagnosis (whole-original score and failure categories), so that the finding isn't lost even though it isn't rerunnable.
22. As a skill developer, I want the benchmark scripts to pass the repo's pylint config, so that they meet the same bar as skill scripts.
23. As a skill developer, I want the benchmark code kept outside every skill folder, so that installing a skill never ships benchmark tooling and the skill-file spec test stays green.
24. As a skill developer, I want ligature glyphs (ﬁ, ﬂ, ﬀ, ﬃ, ﬄ, ﬅ, ﬆ) expanded to plain letters in `text.md`, so that searching or quoting the paper's words works.
25. As a skill developer, I want a word broken across lines with a trailing hyphen rejoined when the next line continues in lowercase, so that `text.md` reads "science" rather than "sci- ence".
26. As a skill developer, I want genuine hyphenated compounds that happen to wrap at their hyphen kept recognisable, so that rejoining doesn't corrupt them more than it fixes.
27. As a note-writing AI, I want `text.md` free of ligature glyphs and mid-word line breaks, so that I quote the paper accurately in the notes.
28. As a skill developer, I want each extraction fix kept only if the bench shows a net improvement, any single regression is explained, and the existing unit and e2e results stay intact, so that a fix that helps the bench can't quietly harm real papers.
29. As a skill developer, I want the baseline updated after the fixes land, so that the next change is measured against the improved state.

## Implementation Decisions

**Benchmark tooling (new, repo root, outside any skill)**

- A new top-level benchmark folder for olmOCR-Bench holds the scripts, a README and the committed baseline. Data and the scorer venv live in gitignored subfolders inside it.
- **Setup**: creates a venv with a user-supplied Python ≥3.11 interpreter and installs the official scorer from PyPI, pinned to `olmocr[bench]==0.4.27` (the latest release when this was written), plus `numpy`, which the bench extra fails to declare (upstream allenai/olmocr#452). Chromium/playwright browsers are not installed: they are only needed for math tests, which we don't score. The venv path must stay short enough for Windows MAX_PATH; the folder inside the repo was judged short enough and must be confirmed on first setup.
- **Fetch**: downloads from the Hugging Face dataset `allenai/olmOCR-bench` without authentication: the two category jsonl files and their PDFs (≈88 MB), into the gitignored data folder, keeping the dataset's `bench_data/` layout. Existing files are skipped.
- **Run** (executed with the repo's own Python):
  1. Runs `extract_text.py` on every PDF of both categories.
  2. Writes each `text.md` as the candidate file the scorer expects (`<pdf-stem>_pg1_repeat1.md`, one candidate folder).
  3. Excludes every PDF the extractor reports as having no text layer, by building a filtered copy of the bench layout (jsonl lines and PDFs) that omits them, and records the excluded count.
  4. Scores with the official scorer by invoking the scorer venv's Python through a small wrapper module.
  5. Collects per-test results, compares with the baseline, prints the report.
- **Windows wrapper**: the scorer keys candidate PDFs by `os.path.relpath` (backslashes on Windows) but looks them up by the jsonl `pdf` field (forward slashes), so every test reports missing output and scores 0%. The wrapper normalises the keys to forward slashes at run time and only on Windows. No upstream report exists; filing one is deferred and is the user's call.
- **Scoring**: the official jsonl is scored as-is. The 38 tests reported wrong in upstream allenai/olmocr#485 (28 multi_column, 4 long_tiny_text in our scope) are not removed; their IDs are kept as a list so that flipped tests among them are annotated in the report.
- **Baseline**: a committed JSON file with the date, the git commit of the extraction script, the scorer version, per-category pass rate and test counts, the excluded no-text PDF count, and the set of passing test IDs. The run reports per-category deltas and the newly failing / newly passing test IDs; it never exits non-zero for a lower score. A `--update-baseline` flag rewrites the file.
- **Scope of scoring**: only `multi_column` (order tests) and `long_tiny_text` (present tests). `headers_footers` is excluded because every bench PDF is a single page and the running-header rule needs the text repeated on ≥2 pages; `arxiv_math`, `table_tests`, `old_scans`, `old_scans_math` are excluded because math, tables and OCR are outside the skill's design (ADR 0001).

**Extraction fixes (`extract_text.py`), after the baseline exists**

- **Ligatures**: expand the Latin ligature code points (U+FB00–U+FB06) to their letter sequences in the extracted text. Use an explicit mapping rather than full NFKC, so that other characters (full-width CJK punctuation, superscripts) are not altered.
- **Line-break hyphenation**: a line ending with a hyphen (`-`, U+2010, U+2011 or the soft hyphen U+00AD) directly after a letter, followed by text that starts with a lowercase letter, is joined without the hyphen or space. This applies inside a joined paragraph and, within one page, between consecutive paragraphs (the bench showed that the extractor often splits one paragraph into two blocks because of noisy OCR font sizes, which leaves the hyphen at the boundary). It never crosses pages. Compounds that wrap at their own hyphen (e.g. "state-of-the-" + "art") will lose the hyphen. The trade-off is accepted because the bench shows a net improvement and the one regression is explained (its expected text keeps a column-end hyphen); the fix is dropped if it regresses without such an explanation.
- Neither fix changes the CLI, the stdout contract, the `<!-- pN -->` markers or the no-text-layer flag.

## Testing Decisions

- Good tests assert external behaviour only: the CLI's output files and stdout, not internal helpers.
- **Extraction fixes**: tested through the existing seam: `extract_text.py` run via subprocess in `tests/write_paper_notes/`, asserting on `text.md`. New PDFs are generated at runtime by `conftest.py` helpers (prior art: `_create_simple_pdf`, `line_blocks`, `two_column` generators):
  - a page whose text contains ligature glyphs;
  - a paragraph with a word hyphenated across a line break;
  - a hyphen at the end of a line followed by an uppercase word or a number, which must stay as is;
  - a hyphen at the end of a page, which must not be joined across.
  Built test-first.
- **Benchmark tooling**: no pytest (it needs downloaded data and a second Python). It is verified by a full run whose scores fall in the range of the earlier sample measurement (multi_column order ≈76%, long_tiny_text present ≈87% excluding no-text PDFs) and match the reimplementation's per-test result where the sample overlaps, and by pylint with the repo config. Lint must include the benchmark scripts.
- **Fix acceptance**: after each extraction fix, rerun the bench and report the deltas and flipped tests. Also rerun the existing `tests/write_paper_notes/` suite, and the cs.pdf / survey.pdf extraction, to confirm no visible damage.

## Out of Scope

- Scoring `headers_footers`, `arxiv_math`, `table_tests`, `old_scans`, `old_scans_math`.
- Building a rerunnable multi-page header benchmark from the bench's original documents (62% of source links are dead and licenses are unclear); only the one-off diagnosis is recorded.
- Changing the running-header rule to work on single pages.
- OCR for pages with no text layer.
- Running the benchmark in pytest or CI, or failing a build on a score drop.
- Reporting the Windows path bug or anything else upstream (deferred, the user's decision).
- Fixing other causes found in the sample: errors in PDFs' own OCR text layers, broken font encodings, PDFs that store no spaces, drop caps, captions or sidebars interleaved with body text.
- Evaluating notes content (faithfulness, structure) or figure crops.

## Further Notes

- **Sample measurement before this spec**: 80 single-page PDFs, scored with a verbatim reimplementation of the scorer; on the 60 multi_column + long_tiny_text PDFs the official scorer gave identical per-test results.
  - multi_column order: 71.7% overall, 76.2% excluding no-text PDFs. Every failure was "text not found"; none was a wrong order.
  - long_tiny_text present: 34.4% overall, 87.1% excluding no-text PDFs (9 of the 20 had no text layer).
  - headers_footers absent: 38.5% on single pages vs 79.1% on 90 whole original documents. The remaining failures are mostly cases the rule deliberately ignores: documents under 3 pages, first-page-only banners, alternating odd/even headers, headers whose text varies.
- **Official scorer on Windows needed**: Python 3.12 (pyenv has 3.10 and 3.12 here), a short venv path, a manual `numpy` install, and the path wrapper. The venv is about 661 MB; chromium is not needed.
- **Related upstream issues**: allenai/olmocr#452 (missing numpy), allenai/olmocr#461 (`partial_ratio` passes present tests on near-empty output; irrelevant once no-text PDFs are excluded), allenai/olmocr#485 (38 wrong verified tests).
- **Licenses**: dataset ODC-BY-1.0; scorer Apache 2.0; individual bench PDFs carry no stated license, so they are never committed.
