# 01: 在 olmOCR-Bench 上跑出 extract_text.py 的分數

**What to build:** 開發者執行三個指令（setup、fetch、run），就能看到目前 `extract_text.py` 在 `multi_column` 與 `long_tiny_text` 全量 PDF 上的官方評分結果：各類別通過率、測試數、被排除的無文字層 PDF 數量。這是整條評測的 tracer bullet，其他 tickets 都建立在它上面。

**Blocked by:** None (can start immediately).

**Status:** done (uncommitted)

- [x] setup 指令用參數指定的 Python（≥3.11）在 benchmark 資料夾內建立獨立 venv，安裝釘死版本 `olmocr[bench]==0.4.27` 加 `numpy`；Python 版本過舊時以明確訊息結束；不安裝 chromium
- [x] fetch 指令只下載 `multi_column`、`long_tiny_text` 的 jsonl 與 PDF 到 gitignored 資料夾，保留 `bench_data/` 版面，已存在的檔案跳過
- [x] run 指令對兩類全部 PDF 執行 `extract_text.py`，以 `<stem>_pg1_repeat1.md` 命名候選檔，排除回報無文字層的 PDF（jsonl 與 PDF 都過濾）並記下數量
- [x] 計分走官方評分器，透過 wrapper 在 Windows 上把路徑分隔符統一成 `/`；不修改已安裝套件或 jsonl；非 Windows 上 wrapper 不改動任何行為
- [x] 印出各類別通過率、測試數與排除數量；全量結果落在抽樣量測範圍（multi_column order 約 76%、long_tiny_text present 約 87%，排除無文字層後）
- [x] 資料與 venv 資料夾已加入 `.gitignore`；benchmark 腳本通過 `pylint --rcfile=.pylintrc`；CLAUDE.md 的 Lint 指令補上 benchmark 腳本
- [x] 腳本位於 repo 根目錄的 benchmark 資料夾，不在任何 skill 資料夾內，`tests/test_skill_files.py` 仍然全綠

## Comments

Done. Full run at the time: multi_column 620/841 = 73.7%, long_tiny_text 221/262 = 84.4% (excluded no-text PDFs: 11 and 23), a few points under the 80-PDF sample (≈76% / ≈87%) because the full set is larger. Extra finding: the official scorer reads the jsonl without an encoding and fails under cp950, so `run.py` sets `PYTHONUTF8=1`.
