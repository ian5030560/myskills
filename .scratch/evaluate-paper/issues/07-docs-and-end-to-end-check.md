# 07: 文件與端到端驗證

**What to build:** 新使用者看 README 就知道何時用 `evaluate-paper`、如何搭配 `write-paper-notes`、MCP 是選配；維護者看 `CLAUDE.md` 就知道新 skill 的架構。最後在沒有 MCP 的環境用真實論文完整跑一次，證明整個流程可用。

**Blocked by:** 05、06

**Status:** done except pylint (not installed); uncommitted

- [x] README 補 `evaluate-paper` 的 skill 總覽、安裝方式，以及「先判讀再寫筆記」的建議
- [x] README 用一段話說明：若有 OpenAlex、Scopus 或 JCR 的 MCP 可取得更多指標，沒有也能完整判讀；不推薦任何第三方 MCP
- [x] `CLAUDE.md` 的 Repository overview 與 Architecture 補上 `evaluate-paper`（三階段、腳本、`references/`、暫存區與存檔流程、測試位置）
- [ ] 沒有 MCP 的環境下，用真實論文（`test-papers/` 內，文件中只用代稱）完整跑一次：身分卡、指標、檢查表、內容判斷、結論、暫存區、詢問存檔、同意後複製、同日重跑沿用快取
- [ ] 端到端結果記錄在本 ticket 的 Comments，包含發現的問題；需要的修正另開 ticket
- [ ] 全部測試與 pylint 通過

## Comments

- 文件：README 新增 `evaluate-paper` 總覽、「先判讀再寫筆記」、MCP 選配說明（不推薦任何 MCP）、安裝方式，Development 補上 `tests/evaluate_paper/`。`CLAUDE.md` 的 overview 改為三個 skill，並補上 Architecture 的 `evaluate-paper` 小節與測試位置。
- 端到端（`test-papers/survey.pdf`，一篇軟體工程系統性回顧，無 MCP 環境；文件中不寫檔名以外的辨識資訊）：
  - 走完：PDF 內 DOI 為佔位文字 → 題名查詢（只出候選）→ 選候選 → `--doi` → `metrics.json` → CASP 系統性回顧檢查表 → 內容判斷 → 結論 → 寫入暫存區 `appraisal.md`；撤稿查無紀錄、更新無紀錄、兩來源皆成功。
  - 存檔：報告末行詢問存檔，使用者同意後已複製到 `test-papers/output/survey/appraisal.md`（`<output-dir>` 預設是目前資料夾，這裡改用已被 gitignore 的 `test-papers/output`，避免弄髒 repo）。未走完：「同日重跑沿用快取」只在文字規則層面（`metrics.json` 已存在且為今日），沒有另外重跑驗證。
- 發現的問題（需另開 ticket 或補規則，尚未處理）：
  1. 題名查詢候選同時出現預印本與正式版，PDF 是投稿版；SKILL.md 沒說在這種情況下要選哪一筆。這次我選了正式版並在報告「所讀版本」與「仍需確認」註明，實際流程應讓使用者選。
  2. CASP Q7（結果多精確）對描述性回顧不適用，Q10 對無介入研究不適用；目前只能答 Can't tell，語意不精確。與 ticket 05 的待辦同一件：考慮加入「不適用」寫法。
  3. 報告把 PDF 首頁的佔位文字（年份 2018、DOI XXXX）當成版本警訊，這個判斷寫在內容判斷第 1 項，規則 1 已涵蓋，無需修改。
- 測試：`pytest tests` 全部 185 個通過。pylint 沒有安裝在這個環境，沒有執行；本 ticket 沒改 Python 腳本，但驗收項目「pylint 通過」仍未驗證。
