# 02: 外部指標腳本：用 DOI 查 OpenAlex 與 Crossref

**What to build:** 對一個 DOI 執行指標腳本，得到 JSON：OpenAlex 與 Crossref 兩個來源的文章引用數與期刊層級數據並列，以及撤稿狀態。任一來源回報撤稿即視為撤稿並標明來源；兩邊都沒有時輸出「查無撤稿紀錄」，不輸出「未撤稿」。測試用本機假 HTTP 伺服器，完全不連網、不需金鑰。規格見 `.scratch/evaluate-paper/spec.md` 的 Implementation Decisions「外部指標腳本」，API 欄位與限流行為見 `.scratch/evaluate-paper/research/appraisal-tools-and-metrics-apis.md`（實作前核對官方文件）。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 命令列接受 `--doi`；可用 `--api-base` 覆寫 API 位址供測試；只使用標準函式庫；JSON 輸出到標準輸出；腳本不讀寫任何檔案
- [ ] 輸出分文章、期刊兩個層級（不查作者）：OpenAlex 的引用數、`is_retracted`、期刊的 `2yr_mean_citedness`（標示為仿 JIF 指標，不是 JIF）；Crossref 的 `is-referenced-by-count` 與 `update-to`／`updated-by` 撤稿紀錄；兩來源並列、不合併
- [ ] 撤稿欄位：任一來源回報撤稿即輸出為撤稿並標明由哪個來源回報；兩邊皆無時輸出「查無撤稿紀錄」
- [ ] 每個來源記錄來源名稱、識別碼與查詢時間
- [ ] 環境變數 `CROSSREF_MAILTO` 可選，設了才帶入 Crossref 請求；腳本不處理任何金鑰，不呼叫申請金鑰的端點
- [ ] 請求有逾時，逾時值與重試次數為有說明的常數
- [ ] 以 subprocess 執行的命令列測試涵蓋以上行為；假伺服器回應的 JSON 在 `conftest.py` 執行時產生，沒有靜態檔案
- [ ] pylint 通過
