# 06: 需要金鑰的指標：用使用者自己的 MCP 補查

**What to build:** 使用者環境中有對應的 MCP 時，判讀能在 OpenAlex 免費額度用完後繼續查詢，也能取得 JIF 或 CiteScore；沒有 MCP 時，判讀仍然完整，報告只是誠實註明查不到什麼、需要哪種功能。規格見 `.scratch/evaluate-paper/spec.md` 的 Implementation Decisions「需要金鑰的資料」；決定與理由見 `docs/adr/0003-metrics-keyless-script-keyed-via-user-mcp.md`。

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] `SKILL.md` 只用功能描述需要的工具（例如「用 DOI 查 OpenAlex 的文章或期刊」「用 ISSN 或 DOI 查期刊的 JIF 或 CiteScore」），由 AI 對照當下可用的工具；不寫死、不推薦任何 MCP 名稱
- [ ] OpenAlex 額度用完（腳本標示「額度用完」）且有對應 MCP 時改用 MCP；沒有時註記「未取得」
- [ ] JIF／CiteScore 只在有對應 MCP 時查；一定連同年份與學科分類記錄，缺其一時標明「缺年份或分類，無法跨期刊比較」；這些數字不影響結論
- [ ] 報告標示「來源：MCP〈伺服器名稱〉」；沒有 MCP 時寫出「需要哪種功能才能取得」，並附 JCR、Scopus 的查詢位置，不寫產品推薦
- [ ] skill 不安裝、不設定 MCP，不向使用者索取金鑰或 email，不呼叫申請金鑰的端點
- [ ] 報告格式規則與自我檢查涵蓋 MCP 來源標示與缺漏註記
- [ ] 全 repo 的 skill 規格測試通過
- [ ] 在沒有任何 MCP 的環境跑一次，確認報告完整且缺漏的註記正確，觀察記錄在本 ticket 的 Comments
