# 04: 接回行尾斷字

**What to build:** 段落內因換行而被連字號切開的字（`Sci-` / `ence`）在 `text.md` 中接回成 `science`。範圍後來放寬為同一頁內的相鄰段落也接回，不跨頁（見 Comments）。

**Blocked by:** 03（同一支腳本，且要以 03 之後的狀態當比較基準）

**Status:** done (uncommitted)

- [x] 測試先行：段落內字母後接行尾連字號、下一行小寫開頭 → 接回，無連字號與空格
- [x] 連字號後下一行以大寫字母或數字開頭 → 保持原樣
- [x] 頁結尾的連字號 → 不跨頁接
- [x] 不改變 CLI、stdout 約定、`<!-- pN -->` 標記與無文字層標記
- [x] 重跑 bench 與 `tests/write_paper_notes/`，只有在 bench 淨進步且退步已說明、既有測試全綠時才保留；否則撤回並在 Comments 記錄原因與數據
- [x] 已知取捨（原本就帶連字號的複合詞在換行處會失去連字號）寫進 Comments，附 bench 數據

## Comments

Done, with a changed scope (decided with the user). Hyphenation inside one paragraph already worked; the 164 remaining `X-` / `y` cases in the bench sit across paragraph boundaries, where noisy OCR font sizes make the extractor split one paragraph into two blocks. So the rule also joins consecutive paragraphs of the same page (never across pages), and handles U+2010, U+2011 and the soft hyphen.

Bench against the baseline of ticket 03: multi_column 648→651/841 (77.4%), long_tiny_text 224→225/262 (85.9%). Against the original baseline: 36 newly passing, 1 newly failing (`03b953c18a4f7d2bbe390940dec839395cdd_page_30.pdf_order_35288b10`): its expected text keeps the column-end `occa-`, a transcription convention of the bench, not an extraction error. Without the paragraph-level join there is no regression but 4 tests fewer pass.

Known trade-off: a compound that wraps at its own hyphen (`state-of-the-` + `art`) loses the hyphen. The acceptance rule was relaxed from "no regression" to "net improvement, regression explained" in the spec.
