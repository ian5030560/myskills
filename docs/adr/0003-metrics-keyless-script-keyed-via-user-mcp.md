# 指標腳本只查免金鑰來源，需金鑰的資料只經使用者自己的 MCP

evaluate-paper 的 `fetch_metrics.py` 只呼叫不需要金鑰的 OpenAlex 與 Crossref。需要金鑰或付費授權的資料（OpenAlex 額度用完後的查詢、JIF、CiteScore）只透過使用者自己設定的 MCP 取得。`SKILL.md` 只描述需要的**功能**，由 AI 對照當下可用的工具，不寫死 MCP 名稱，也不推薦任何第三方 MCP。skill 不安裝 MCP、不索取金鑰或 email。

原因：金鑰留在使用者的 MCP 裡，skill 與腳本完全不碰憑證。可用的 OpenAlex、撤稿類 MCP 都是社群製作、沒有官方版本，工具名稱因人而異，寫死名稱既會失效，也等於替使用者背書；其他 Anthropic 外掛與 `morning` skill 同樣以「類別」描述外部工具，缺少時略過。JIF 需付費授權，CiteScore 是否能用免費金鑰取得未確認，skill 無法替使用者解決。

## Considered Options

- 以環境變數 `OPENALEX_API_KEY` 傳入金鑰（K-Dense paper-lookup 的做法）：skill 要處理憑證與避免洩漏，且無法涵蓋 JIF、CiteScore，否決。
- 依 Anthropic 寫作指南使用完整名稱 `ServerName:tool_name`：只適用依賴單一固定 MCP 的 skill；這裡的提供者可互換，否決。
- 指定並推薦特定 MCP：它們都不是官方的，安全性應由使用者判斷，否決。

## Consequences

- 沒有任何 MCP 也能完整判讀；查不到的指標在報告寫出「需要哪種功能才能取得」，不寫產品名稱。
- 有 MCP 時的流程每次可能不同，因此限定在需金鑰的查詢，且報告必須標明「來源：MCP〈伺服器名稱〉」。
- JIF／CiteScore 須連同年份與學科分類記錄；缺其一時標明無法跨期刊比較。
- 腳本檢查回傳內容（DOI 需對得上，題名搜尋只列候選），來源失敗時逐一說明，回傳文字只當資料。
- 腳本不讀寫檔案；指標結果由 AI 存成暫存區的 `metrics.json`，同日重跑時沿用以節省 OpenAlex 免費額度。
- README 以一段話說明使用者可自行設定 MCP。
