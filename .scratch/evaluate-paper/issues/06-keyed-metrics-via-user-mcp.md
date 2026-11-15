# 06: 需要金鑰的指標：用使用者自己的 MCP 補查

**What to build:** 使用者環境中有對應的 MCP 時，判讀能在 OpenAlex 免費額度用完後繼續查詢，也能取得 JIF 或 CiteScore；沒有 MCP 時，判讀仍然完整，報告只是誠實註明查不到什麼、需要哪種功能。規格見 `.scratch/evaluate-paper/spec.md` 的 Implementation Decisions「需要金鑰的資料」；決定與理由見 `docs/adr/0003-metrics-keyless-script-keyed-via-user-mcp.md`。

**Blocked by:** 04

**Status:** done (uncommitted)

- [x] `SKILL.md` 只用功能描述需要的工具（例如「用 DOI 查 OpenAlex 的文章或期刊」「用 ISSN 或 DOI 查期刊的 JIF 或 CiteScore」），由 AI 對照當下可用的工具；不寫死、不推薦任何 MCP 名稱
- [x] OpenAlex 額度用完（腳本標示「額度用完」）且有對應 MCP 時改用 MCP；沒有時註記「未取得」
- [x] JIF／CiteScore 只在有對應 MCP 時查；一定連同年份與學科分類記錄，缺其一時標明「缺年份或分類，無法跨期刊比較」；這些數字不影響結論
- [x] 報告標示「來源：MCP〈伺服器名稱〉」；沒有 MCP 時寫出「需要哪種功能才能取得」，並附 JCR、Scopus 的查詢位置，不寫產品推薦
- [x] skill 不安裝、不設定 MCP，不向使用者索取金鑰或 email，不呼叫申請金鑰的端點
- [x] 報告格式規則與自我檢查涵蓋 MCP 來源標示與缺漏註記
- [x] 全 repo 的 skill 規格測試通過
- [x] 在沒有任何 MCP 的環境跑一次，確認報告完整且缺漏的註記正確，觀察記錄在本 ticket 的 Comments

## Comments

- SKILL.md 步驟 2「Metrics that need a key」原本已涵蓋功能描述、額度用完改用 MCP、年份與分類、不安裝不推薦不索取金鑰。本次補上：MCP 取代腳本結果時也要附識別碼與查詢日期、不呼叫申請金鑰的端點。report-format 第 10 條擴充為涵蓋 MCP 來源標示與缺漏註記（未取得、所需功能種類、JCR／Scopus 查詢位置、不影響標記）。
- 沒有 MCP 的觀察：本環境沒有 OpenAlex 或期刊指標類的 MCP。ticket 05 測試時對 CVPR 論文與 AF 統合分析各跑一次完整流程，報告都寫「未取得：JIF、CiteScore」並說明需要「用 ISSN 或 DOI 查期刊 JIF 或 CiteScore」的功能與查詢位置，報告完整。這不是為本 ticket 另跑的一次；修改後的措辭（第 10 條）尚未重跑。
- 未做：沒有 MCP 的情況下無法測試「有 MCP 時」的路徑（額度用完改用 MCP、JIF 取得），該路徑只有文字規則，未實測。
