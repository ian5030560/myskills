# 03: 外部指標腳本：題名查詢與失敗處理

**What to build:** 論文沒有 DOI 時用題名查詢，只得到候選清單，由人選定；各種失敗情況都被誠實地記錄，不會讓空白被誤讀成「沒有紀錄」。規格見 `.scratch/evaluate-paper/spec.md` 的 Implementation Decisions「外部指標腳本」與 `docs/adr/0003-metrics-keyless-script-keyed-via-user-mcp.md`。

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] `--title` 與 `--doi` 二選一；題名查詢只輸出候選清單（題名、年份、DOI），不自動選定，也不為候選查指標
- [ ] 以 DOI 查詢時，回傳紀錄的 DOI 必須與查詢一致；不一致視為該來源失敗
- [ ] HTTP 200 但內容形狀錯誤（缺必要欄位、型別不對）視為失敗並說明原因
- [ ] 單一來源失敗（逾時、HTTP 錯誤、形狀錯誤）時，其餘來源照常輸出，失敗的來源逐一記錄來源、識別碼、查詢時間與失敗原因
- [ ] OpenAlex 額度用完或被限流時，輸出明確標示為「額度用完」，讓 AI 能改用 MCP 或註記「未取得」；腳本不寫死額度數字
- [ ] `mailto` 從輸出中所有記錄的網址刪除
- [ ] 回傳的題名、摘要等文字只當資料，腳本只輸出需要的欄位
- [ ] 命令列測試涵蓋以上每一項，含各種失敗情境與 `mailto` 不外洩；不連真實網路
- [ ] pylint 通過
