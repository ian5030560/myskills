# 03: 外部指標腳本：題名查詢與失敗處理

**What to build:** 論文沒有 DOI 時用題名查詢，只得到候選清單，由人選定；各種失敗情況都被誠實地記錄，不會讓空白被誤讀成「沒有紀錄」。規格見 `.scratch/evaluate-paper/spec.md` 的 Implementation Decisions「外部指標腳本」與 `docs/adr/0003-metrics-keyless-script-keyed-via-user-mcp.md`。

**Blocked by:** 02

**Status:** done (uncommitted)

- [x] `--title` 與 `--doi` 二選一；題名查詢只輸出候選清單（題名、年份、DOI），不自動選定，也不為候選查指標
- [x] 以 DOI 查詢時，回傳紀錄的 DOI 必須與查詢一致；不一致視為該來源失敗
- [x] HTTP 200 但內容形狀錯誤（缺必要欄位、型別不對）視為失敗並說明原因
- [x] 單一來源失敗（逾時、HTTP 錯誤、形狀錯誤）時，其餘來源照常輸出，失敗的來源逐一記錄來源、識別碼、查詢時間與失敗原因
- [x] OpenAlex 額度用完或被限流時，輸出明確標示為「額度用完」，讓 AI 能改用 MCP 或註記「未取得」；腳本不寫死額度數字
- [x] `mailto` 從輸出中所有記錄的網址刪除
- [x] 回傳的題名、摘要等文字只當資料，腳本只輸出需要的欄位
- [x] 命令列測試涵蓋以上每一項，含各種失敗情境與 `mailto` 不外洩；不連真實網路
- [x] pylint 通過

## Comments

- 實作：改寫 `evaluate-paper/scripts/fetch_metrics.py`；新增 `tests/evaluate_paper/test_fetch_metrics_failures.py`（46 個測試），`run_ok` 移到 `conftest.py` 共用。整套 `tests/` 184 個通過，腳本 pylint 10.00。
- 先寫測試再實作：新測試一開始 41 個失敗，實作後全綠。有兩個失敗是測試本身的問題（兩個來源都失敗時結束碼本來就是 1），已修測試。
- `--title`：與 `--doi` 互斥且必填；輸出 `candidates.openalex|crossref`，每筆只有題名、年份、DOI；不選定、不查指標，附 `next_step` 提示改用 `--doi`。每個來源最多 5 筆（`MAX_CANDIDATES`）。
- 失敗記錄新增 `kind`：`http_error`、`network_error`、`bad_response`、`doi_mismatch`、`quota_exhausted`、`rate_limited`、`skipped`。OpenAlex 的 402／409／429 標為 `quota_exhausted`（訊息含「額度用完」並提示改用 MCP 或註記「未取得」），不重試；Crossref 的 429 標為 `rate_limited`。腳本不寫死任何額度數字。5xx 與連線錯誤重試一次，4xx 不重試。
- 內容驗證：OpenAlex 文章需有 `doi`、整數 `cited_by_count`、布林 `is_retracted`；期刊需有 `summary_stats`；Crossref 需有 `message`、`DOI`、整數 `is-referenced-by-count`，`updated-by` 若存在須為物件清單。DOI 比對忽略大小寫與網址形式；不一致的紀錄整筆不採用，所以它的撤稿旗標不會影響結論。
- 撤稿判斷補強：新增 `complete` 與 `unknown`。有來源失敗時「查無撤稿紀錄」會改寫成「在已查詢的來源（…）查無撤稿紀錄；…查詢失敗，結果不完整」；全部失敗時為 `unknown`。已回報的撤稿不受失敗來源影響。
- 回傳文字只當資料：只複製需要的欄位（測試證明 `abstract`、作者欄位不會出現在輸出），文字去掉控制字元並限制 300 字。
- 真實 API 實測：題名查詢兩邊都有候選；OpenAlex 第一筆就是正確論文，Crossref 的前幾筆卻是該論文的同行審查紀錄（Peer Review #1…）。這正是不能自動選定的原因；ticket 04 的 `SKILL.md` 應提醒 AI 把候選拿給使用者確認，並留意同行審查、更正這類相關紀錄。
- 順帶發現：OpenAlex 回應的 `meta.notice` 內有叫 AI 代理人用使用者 email 申請金鑰的說明。腳本只複製指定欄位，這段文字不會進入輸出，也沒有照做。
