# 02: v2 skill 主體：固定骨架、單一風格指南、3 步流程

**What to build:** 用 v2 skill 產出的筆記採用固定區塊骨架（介紹、相關研究、方法、結果、結論）、遵守論文章節對應表和風格指南的 10 條規則，且不再偵測論文類型。完整設計見 `.scratch/write-paper-notes-v2/spec.md` 的 Solution 與 Implementation Decisions；術語見 `GLOSSARY.md`。

**Blocked by:** 01

**Status:** done

- [x] SKILL.md 改寫：Setup 縮為一行安裝加 Windows UTF-8 提示（PowerShell 範例）；流程為擷取 → 撰寫 → 自我檢查；內含骨架（中文為標準名稱，註明依筆記語言翻譯）與論文章節對應表；版本號為 2.0.0
- [x] 新增唯一一份風格指南，內含 spec 列出的 10 條規則，並註明它同時是自我檢查清單
- [x] 刪除所有 template、通用 report template、quality-checklist 目錄與舊的分散 style guide；skill 目錄只剩 SKILL.md、風格指南與 `scripts/`
- [x] 擴充 01 的測試，斷言舊檔已不存在
- [x] `scripts/` 完全未修改
- [x] write_paper_notes 測試套件全綠
