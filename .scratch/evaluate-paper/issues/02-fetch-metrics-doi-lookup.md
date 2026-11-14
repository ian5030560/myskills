# 02: 外部指標腳本：用 DOI 查 OpenAlex 與 Crossref

**What to build:** 對一個 DOI 執行指標腳本，得到 JSON：OpenAlex 與 Crossref 兩個來源的文章引用數與期刊層級數據並列，以及撤稿狀態。任一來源回報撤稿即視為撤稿並標明來源；兩邊都沒有時輸出「查無撤稿紀錄」，不輸出「未撤稿」。測試用本機假 HTTP 伺服器，完全不連網、不需金鑰。規格見 `.scratch/evaluate-paper/spec.md` 的 Implementation Decisions「外部指標腳本」，API 欄位與限流行為見 `.scratch/evaluate-paper/research/appraisal-tools-and-metrics-apis.md`（實作前核對官方文件）。

**Blocked by:** None (can start immediately)

**Status:** done (uncommitted)

- [x] 命令列接受 `--doi`；可用 `--api-base` 覆寫 API 位址供測試；只使用標準函式庫；JSON 輸出到標準輸出；腳本不讀寫任何檔案
- [x] 輸出分文章、期刊兩個層級（不查作者）：OpenAlex 的引用數、`is_retracted`、期刊的 `2yr_mean_citedness`（標示為仿 JIF 指標，不是 JIF）；Crossref 的 `is-referenced-by-count` 與 `update-to`／`updated-by` 撤稿紀錄；兩來源並列、不合併
- [x] 撤稿欄位：任一來源回報撤稿即輸出為撤稿並標明由哪個來源回報；兩邊皆無時輸出「查無撤稿紀錄」
- [x] 每個來源記錄來源名稱、識別碼與查詢時間
- [x] 環境變數 `CROSSREF_MAILTO` 可選，設了才帶入 Crossref 請求；腳本不處理任何金鑰，不呼叫申請金鑰的端點
- [x] 請求有逾時，逾時值與重試次數為有說明的常數
- [x] 以 subprocess 執行的命令列測試涵蓋以上行為；假伺服器回應的 JSON 在 `conftest.py` 執行時產生，沒有靜態檔案
- [x] pylint 通過

## Comments

- 實作：`evaluate-paper/scripts/fetch_metrics.py`（只用標準函式庫），命令列測試 28 個在 `tests/evaluate_paper/`，pylint 10.00。整套 `tests/` 138 個通過。
- `--api-base` 的約定：一個主機同時扮演兩個 API，OpenAlex 在 `<base>/openalex`、Crossref 在 `<base>/crossref`（兩邊的路徑都是 `/works/...`，需要前綴才分得開）。
- 測試用 `ThreadingHTTPServer` 假伺服器，記錄每個請求，用來斷言「沒有送出任何金鑰」「`mailto` 只送給 Crossref」。
- 突變驗證：拿掉「Crossref 的 `updated-by` 撤稿算數」後，兩個撤稿測試如預期失敗。
- 真實 API 實測（不帶金鑰、不帶 `mailto`）：`10.7717/peerj.4375` 兩邊都成功，OpenAlex 1514 次引用、Crossref 885 次引用，期刊 `2yr_mean_citedness` 4.67，撤稿為「查無撤稿紀錄」；Wakefield 1998（`10.1016/S0140-6736(97)11096-0`）被 OpenAlex 與 Crossref 同時回報撤稿。Windows 上要用 venv 的 `python.exe` 執行，pyenv 的 shim 會把括號弄壞。
- 範圍外但先做了基本款：單一來源失敗時（HTTP 錯誤、連線失敗、非 JSON）不崩潰，記錄 `ok: false` 與原因，全部失敗時結束碼為 1；`mailto` 也從錯誤訊息中刪除。ticket 03 要補的是 DOI 不一致、200 但形狀錯誤、額度用完標示、題名查詢，以及相應測試。
- 輸出形狀（給 03 與 04 沿用）：`article.openalex|crossref`、`journal.openalex`、`retraction{status, reported_by, text, checked_sources, failed_sources}`；每筆記錄都有 `source`、`identifier`、`url`、`queried_at`、`ok`。
- 結束碼：0 至少一個來源成功、1 全部失敗、2 參數錯誤。
