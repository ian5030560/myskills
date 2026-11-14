# 07: 文件與端到端驗證

**What to build:** 新使用者看 README 就知道何時用 `evaluate-paper`、如何搭配 `write-paper-notes`、MCP 是選配；維護者看 `CLAUDE.md` 就知道新 skill 的架構。最後在沒有 MCP 的環境用真實論文完整跑一次，證明整個流程可用。

**Blocked by:** 05、06

**Status:** ready-for-agent

- [ ] README 補 `evaluate-paper` 的 skill 總覽、安裝方式，以及「先判讀再寫筆記」的建議
- [ ] README 用一段話說明：若有 OpenAlex、Scopus 或 JCR 的 MCP 可取得更多指標，沒有也能完整判讀；不推薦任何第三方 MCP
- [ ] `CLAUDE.md` 的 Repository overview 與 Architecture 補上 `evaluate-paper`（三階段、腳本、`references/`、暫存區與存檔流程、測試位置）
- [ ] 沒有 MCP 的環境下，用真實論文（`test-papers/` 內，文件中只用代稱）完整跑一次：身分卡、指標、檢查表、內容判斷、結論、暫存區、詢問存檔、同意後複製、同日重跑沿用快取
- [ ] 端到端結果記錄在本 ticket 的 Comments，包含發現的問題；需要的修正另開 ticket
- [ ] 全部測試與 pylint 通過
