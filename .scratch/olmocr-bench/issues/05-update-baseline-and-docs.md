# 05: 更新 baseline 與文件

**What to build:** 修正落地後，baseline 反映新的擷取狀態，README 記錄修正前後的分數變化，CLAUDE.md 的架構說明與實際行為一致。

**Blocked by:** 03、04

**Status:** done (uncommitted)

- [x] 以修正後的 `extract_text.py` 執行 `--update-baseline`
- [x] README 記錄兩項修正前後的分數與翻轉題目數
- [x] CLAUDE.md 架構段落提到合字展開與行尾斷字接回（若 04 被撤回則只提合字），並提到 benchmark 資料夾與其指令
- [x] `pytest tests/write_paper_notes/ tests/test_skill_files.py` 與 pylint 全部通過

## Comments

Done. Baseline recorded with the final extract_text.py: multi_column 651/841 = 77.4%, long_tiny_text 225/262 = 85.9%. README table and CLAUDE.md updated.
