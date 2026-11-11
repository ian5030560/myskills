# 01: SKILL.md 路徑一致性測試

**What to build:** 在 write_paper_notes 測試套件新增一個 pytest：解析 SKILL.md 中引用的每個相對路徑，確認都存在於 skill 目錄。在現行 v1 上就應該通過，作為後續刪檔前的保護網（prefactor）。

**Blocked by:** None (can start immediately)

**Status:** done

- [x] 新測試以 `Path(__file__)` 定位 skill 目錄，沿用既有測試慣例，不需要 fixture 檔
- [x] SKILL.md 裡任何一個引用路徑不存在時，測試會失敗（可暫時改壞一個路徑確認）
- [x] 在目前的 v1 上執行，整個 write_paper_notes 測試套件全綠
