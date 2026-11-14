Status: ready-for-agent

# evaluate-paper：論文判讀 skill，並把 skill 檔案測試泛用化

相關文件：`GLOSSARY.md`（判讀、判讀報告、文章身分卡、外部評估、外部指標、內容判斷、用途標記）、`docs/adr/0002-appraisal-three-stages-no-score.md`、`docs/adr/0003-metrics-keyless-script-keyed-via-user-mcp.md`。研究資料在 `.scratch/evaluate-paper/research/`（檢查表授權與 API 事實、Agent Skills 規格 27 條規則、其他 skill 處理外部工具的做法）。

## Problem Statement

使用者寫論文報告前要先決定一篇論文「能不能用、怎麼用」。課程投影片（《學術文獻的來源、品質判讀與論文報告》）教的做法是看來源、看期刊指標、讀內容，但實際做起來有幾個困難：

- 判讀散在許多地方：要自己查撤稿、引用數、期刊指標，還要記得依研究設計挑對的檢查表，最後沒有一份能回頭核對的紀錄。
- 期刊指標容易被誤用：把 JIF 或 CiteScore 當成這篇文章的品質，卻忽略它們隨年份與學科分類而不可比。
- 判讀結論相對於研究問題：同一篇論文對某個問題是主報告、對另一個問題只是背景，但沒有固定的說法。
- 需要金鑰的資料（OpenAlex 額度用完後、JIF、CiteScore）無法由 skill 取得，也不該要求使用者把金鑰交給 skill。
- repo 現有的 skill 檔案測試只服務 `write-paper-notes`；新增第三個 skill 後，沒有東西保證各 skill 符合 Agent Skills 官方規格。實際上 `pdf/` 與 `write-paper-notes/` 的 frontmatter 目前就有不合規格的欄位。

## Solution

新增 `evaluate-paper` skill：使用者給一篇論文 PDF 和自己的研究問題，AI 依三階段產出**判讀報告**。

1. **文章身分卡**：記下書目與 DOI、發表來源、文章類型、所讀版本、審查狀態，只辨識不判斷。
2. **外部評估**：依研究設計選用 CASP、AMSTAR 2 或 MMAT 檢查表，並用腳本查**外部指標**（OpenAlex 與 Crossref）。需要金鑰的資料，只在使用者環境裡有對應 MCP 時才查。
3. **內容判斷**：依投影片整理的規則，檢查來源能否核對、是否回答研究問題、說法是否被證據支持、測量與推論範圍是否合適。
4. **結論**：給**用途標記**（主報告／背景／比較／暫不使用）、理由與「仍需確認」，不打分數；外部指標只當輔助線索，撤稿例外。

報告「結論在前」。報告先寫到暫存區並自我檢查，再完整顯示在對話中，使用者同意才複製到正式位置。同時，repo 的 skill 檔案測試泛用化，依官方規格檢查所有 skill，並把現有兩個 skill 修到符合規格。

## User Stories

1. As a 研究生, I want 給 AI 一篇論文 PDF 與我的研究問題就得到判讀報告, so that 我知道這篇能不能用在我的報告裡
2. As a 研究生, I want 報告最上方就是用途標記與一兩句理由, so that 我不用讀完整份報告才知道結論
3. As a 研究生, I want 用途標記相對於我的研究問題, so that 同一篇論文對不同問題可以有不同用途
4. As a 研究生, I want 沒有給研究問題時 AI 先推斷「我的研究問題」並請我確認, so that 判讀不會誤用論文自己的研究問題
5. As a 研究生, I want 報告不給分數或等級, so that 我不會把一個數字當成品質
6. As a 研究生, I want 每個判斷都附原文位置, so that 我能回到論文核對
7. As a 研究生, I want 報告開頭有文章身分卡, so that 我知道判讀的是哪個版本、是否經過審查
8. As a 研究生, I want 預印本或未審查的版本在身分卡中清楚標示, so that 我不會把它當正式發表的論文
9. As a 研究生, I want AI 依論文的研究設計挑選檢查表, so that 我不用自己判斷該用 CASP、AMSTAR 2 還是 MMAT
10. As a 研究生, I want 檢查表的每一題都附回答與原文位置, so that 外部評估可以被核對
11. As a 研究生, I want 系統性回顧用 AMSTAR 2 並依關鍵題決定整體信心, so that 結論不是單純加總題項
12. As a 研究生, I want 研究設計不符合任何檢查表時報告明說, so that 我知道這部分沒有標準工具可用
13. As a 研究生, I want 報告列出撤稿狀態, so that 我不會引用已被撤稿的論文
14. As a 研究生, I want OpenAlex 與 Crossref 的數字並列, so that 我看得到兩邊的差異
15. As a 研究生, I want 任一來源回報撤稿就視為撤稿, so that 單一資料庫的遺漏不會讓撤稿論文通過
16. As a 研究生, I want 沒查到撤稿時報告寫「查無撤稿紀錄」, so that 我不會誤以為已確認沒被撤稿
17. As a 研究生, I want 報告中每個指標都標明來源、識別碼和查詢日期, so that 我能自己重查
18. As a 研究生, I want 引用數、期刊指標只當輔助線索, so that 期刊名聲不會取代對這篇文章的判斷
19. As a 研究生, I want 用 DOI 查詢時 AI 確認回傳的 DOI 與我查的一致, so that 不會拿到另一篇論文的資料
20. As a 研究生, I want 論文沒有 DOI 時用題名查詢並只列出候選, so that AI 不會自己挑錯一篇
21. As a 研究生, I want 某個資料來源失敗時報告逐一寫明哪個來源失敗, so that 空白不會被當成「沒有紀錄」
22. As a 研究生, I want 查不到的指標在報告寫出「需要哪種功能才能取得」, so that 我知道怎麼補查
23. As a 研究生, I want 有 JCR 或 Scopus 的 MCP 時 AI 能查 JIF 或 CiteScore, so that 有訂閱的人可以得到更多資訊
24. As a 研究生, I want JIF 與 CiteScore 一定連同年份與學科分類, so that 我不會跨期刊或跨年份誤比
25. As a 研究生, I want 沒有那類 MCP 時只提供 JCR 與 Scopus 的查詢位置, so that 我仍知道去哪裡查
26. As a 研究生, I want 來自 MCP 的數字標明「來源：MCP〈伺服器名稱〉」, so that 我知道資料從哪裡來
27. As a 研究生, I want OpenAlex 免費額度用完時自動改用 OpenAlex 的 MCP（若有）, so that 判讀不會中斷
28. As a 研究生, I want 沒有 MCP 且額度用完時註記「未取得」, so that 報告不會因為缺一項指標而失敗
29. As a 研究生, I want skill 從不向我索取金鑰或 email, so that 我的憑證不經過 skill
30. As a 研究生, I want 自己決定要不要設定 MCP, so that 不設定也能完整判讀
31. As a 研究生, I want 報告內容包含來源能否核對、是否回答我的問題、說法是否被證據支持、測量與推論範圍是否合適, so that 我知道內容層面的風險
32. As a 研究生, I want 內容判斷不重複判斷研究設計是否嚴謹, so that 同一件事不會被判兩次
33. As a 研究生, I want 論文中有 AI 摘要時 AI 額外檢查摘要是否忠於原文, so that 我不被摘要誤導
34. As a 研究生, I want 結論附上「仍需確認」的項目, so that 我知道還要自己查什麼
35. As a 研究生, I want 報告用我使用的語言寫, so that 我讀起來沒有負擔
36. As a 研究生, I want 報告先存到暫存區再顯示, so that 對話中斷後報告還在
37. As a 研究生, I want 報告最後一行告訴我暫存檔位置並詢問是否存檔, so that 我能決定要不要留下
38. As a 研究生, I want 同意存檔時直接複製暫存檔, so that 正式檔和我剛讀的內容完全一致
39. As a 研究生, I want 一開始就要求存檔或指定輸出位置時判讀完直接存, so that 批次判讀很多篇時不用逐篇回答
40. As a 研究生, I want 同一篇論文同一天重跑時沿用指標快取, so that 不浪費 OpenAlex 的免費額度
41. As a 研究生, I want 快取的報告記錄原本的查詢日期, so that 日期不會誤導
42. As a 研究生, I want 判讀報告和 write-paper-notes 互相獨立, so that 我可以只用其中一個
43. As a 研究生, I want README 建議先判讀再寫筆記, so that 我不會花時間為不能用的論文寫筆記
44. As a 研究生, I want README 用一段話說明可以自行設定 MCP 取得更多指標, so that 我知道這是選配
45. As a skill 維護者, I want AI 輸出前依 `references/` 的規則自我檢查並修到全部通過, so that 報告格式與規則一致
46. As a skill 維護者, I want 外部指標腳本只用標準函式庫, so that 使用者不必安裝額外套件
47. As a skill 維護者, I want 腳本輸出的網址不含 `mailto`, so that 聯絡信箱不會寫進報告
48. As a skill 維護者, I want 腳本把回傳的題名與摘要只當資料, so that 外部文字無法對 AI 下指令
49. As a skill 維護者, I want 腳本可用參數指向測試用伺服器, so that 測試不需要真的連網
50. As a skill 維護者, I want 測試不依賴任何金鑰, so that 任何環境都能執行
51. As a skill 維護者, I want 一個測試檢查 repo 內每個 skill 資料夾是否符合官方規格, so that 新增或修改 skill 時違規會立刻被發現
52. As a skill 維護者, I want frontmatter 只允許規格列出的六個欄位, so that skill 能被官方工具與平台接受
53. As a skill 維護者, I want `name` 與資料夾同名且符合命名規則, so that 載入時不會出錯
54. As a skill 維護者, I want SKILL.md 少於 500 行且引用只有一層, so that 內容符合官方建議的漸進揭露
55. As a skill 維護者, I want SKILL.md 引用的每個路徑都存在, so that 不會指向不存在的檔案
56. As a skill 維護者, I want `references/`、`scripts/`、`assets/` 裡沒有未被引用的檔案, so that 孤兒檔案會被發現
57. As a skill 維護者, I want 現有的 `pdf/` 與 `write-paper-notes/` 修到符合規格, so that 新測試一開始就通過
58. As a skill 維護者, I want 版本資訊移到 `metadata.version` 並用字串, so that 保留版本又不違規
59. As a skill 維護者, I want `pylint` 設定自動納入所有 skill 的 `scripts/`, so that 新增 skill 不必再改設定
60. As a 檢查表授權的權利人, I want CASP 衍生的檔案單獨標示 CC BY-NC-SA 4.0 授權, so that 授權條件被遵守
61. As a 檢查表授權的權利人, I want MMAT 只以改寫呈現並註明出處, so that 沒有未經許可轉載原文

## Implementation Decisions

**evaluate-paper skill 的組成**
- 新增獨立 skill `evaluate-paper`：一份 `SKILL.md`、`references/`（投影片規則、CASP／AMSTAR 2／MMAT 題目檔、報告格式與自我檢查規則）、`scripts/` 下一支外部指標腳本。
- `SKILL.md` 小於 500 行，所有 `references/` 檔案由 `SKILL.md` 直接引用（一層）。
- frontmatter 只用規格允許的欄位；`compatibility` 寫明需要網路、不需要金鑰，有相關 MCP 時可多查到哪些指標。版本放 `metadata.version`（字串）。
- 與 `write-paper-notes` 互相獨立，不共用程式；README 建議先判讀再寫筆記。
- 輸入限定 PDF，沿用 `write-paper-notes` 的方式：PDF 以 AI 直接閱讀；不另外建立文字擷取腳本。

**判讀流程（寫在 SKILL.md）**
- 順序：身分卡 → 外部評估 → 內容判斷 → 結論 → 自我檢查 → 顯示與存檔。
- 研究問題：使用者有給就用；沒給時 AI 先推斷「使用者的研究問題」（不是論文自己的研究問題），請使用者確認後再往下做。
- 檢查表選擇：依研究設計選用 CASP（依設計分冊）、AMSTAR 2（系統性回顧）、MMAT（混合方法等）；不符合任何檢查表時，報告明說並只做內容判斷。
- 檢查表不加總成分數。AMSTAR 2 依 7 個關鍵領域（第 2、4、7、9、11、13、15 題）決定整體信心：High／Moderate／Low／Critically low。
- 每一題的回答與每個判斷都附原文位置；「沒有足夠資訊」要明寫，不猜。
- 內容判斷涵蓋：來源能否核對、是否回答研究問題、說法是否被證據支持、測量是否合適、推論範圍與單位是否合適；論文含 AI 摘要時加做摘要忠實度檢查。研究設計嚴謹度不屬於此階段。
- 結論給用途標記（主報告／背景／比較／暫不使用）、理由與「仍需確認」。外部指標只當輔助線索；撤稿是唯一可改變結論的指標。
- 報告語言跟隨使用者；語言不明時詢問。

**報告格式與儲存**
- 報告順序：結論在前（用途標記加一兩句理由），接著是身分卡、外部評估、內容判斷。
- 先寫到暫存區：`<暫存區>/evaluate-paper/<pdf-stem>/appraisal.md`。環境有提供本次對話專用暫存資料夾就用它，沒有則用系統暫存資料夾；同名直接覆蓋，skill 不負責清理。
- 對暫存檔做自我檢查（對照 `references/` 的規則，修到全部通過）後，在對話中完整顯示。
- 報告最後一行列出暫存檔路徑，並詢問是否存到 `<output-dir>/<pdf-stem>/appraisal.md`；同意就複製檔案，不重新產生。使用者一開始就要求存檔或指定輸出位置時，判讀完直接複製。
- 指標快取：AI 把腳本的輸出存成同一暫存資料夾的 `metrics.json`；同一篇論文同一天重跑時沿用，報告記錄原始查詢日期。

**外部指標腳本**
- 命令列介面：`--doi <doi>` 或 `--title <title>`，二選一；JSON 輸出到標準輸出；`--api-base` 可覆寫 API 位址，供測試指向本機假伺服器。只使用標準函式庫。
- 只呼叫不需要金鑰的 OpenAlex 與 Crossref；環境變數 `CROSSREF_MAILTO` 可選，設了才帶入 Crossref 請求，輸出前從所有記錄的網址中刪除。腳本不處理任何金鑰，不呼叫任何申請金鑰的端點。
- 輸出分文章、期刊兩個層級（作者層級不查）：OpenAlex 的引用數、`is_retracted`、期刊的仿 JIF 指標（標示為 `2yr_mean_citedness`，不是 JIF）；Crossref 的 `is-referenced-by-count` 與 `update-to`／`updated-by` 撤稿紀錄。兩來源並列，不合併。
- 撤稿欄位：任一來源回報撤稿即輸出為撤稿，並標明由哪個來源回報；兩邊都沒有時輸出「查無撤稿紀錄」，不輸出「未撤稿」。
- 驗證回傳內容：以 DOI 查詢時，回傳紀錄的 DOI 必須與查詢一致，不一致視為失敗；以題名查詢時只輸出候選清單（題名、年份、DOI），不自動選定，也不為候選查指標。HTTP 200 也要檢查內容形狀。
- 失敗處理：每個來源各自成功或失敗，輸出中逐一記錄來源、識別碼、查詢時間與失敗原因；OpenAlex 額度用完或被限流時，輸出標明為「額度用完」以便 AI 改用 MCP 或註記「未取得」。請求有逾時；重試次數與逾時值要有說明的常數。
- 回傳的題名、摘要等文字一律只當資料，不執行；腳本只輸出需要的欄位。
- 腳本不讀寫任何檔案（除標準輸出入）。

**需要金鑰的資料（寫在 SKILL.md，不寫腳本）**
- 只描述需要的功能，例如「用 DOI 查 OpenAlex 的文章或期刊」、「用 ISSN 或 DOI 查期刊的 JIF 或 CiteScore」，由 AI 對照當下可用的工具；不寫死、不推薦任何 MCP 名稱。
- OpenAlex 額度用完且有對應 MCP 時改用 MCP；JIF／CiteScore 只在有對應 MCP 時查，連同年份與學科分類記錄，缺其一時標明「缺年份或分類，無法跨期刊比較」。
- 報告標示「來源：MCP〈伺服器名稱〉」。沒有 MCP 時，報告寫出「需要哪種功能才能取得」並附 JCR、Scopus 的查詢位置，不寫產品推薦。
- skill 不安裝、不設定 MCP，不向使用者索取金鑰或 email；README 用一段話說明使用者可自行設定。

**授權**
- MMAT 題目檔只用改寫並註明出處，不轉載原文，不另外取得許可。
- CASP 衍生的檔案開頭單獨標示 CC BY-NC-SA 4.0 授權聲明。
- AMSTAR 2 依其 BMJ 論文的 CC BY 4.0 授權，註明出處。

**skill 檔案測試泛用化與現有 skill 修正**
- 以涵蓋全 repo 的測試取代只針對 `write-paper-notes` 的測試：對每個 skill 資料夾（含 `pdf/`、`write-paper-notes/`、`evaluate-paper/`；排除 `.agents/`、`.claude/`、虛擬環境資料夾）逐一檢查。
- 檢查項目（失敗即測試不過）：`SKILL.md` 存在；frontmatter 起訖與合法 YAML；只含六個允許欄位；`name` 必填、1–64 字元、僅小寫英數與連字號、首尾不為連字號、無連續連字號、與資料夾同名、不含 `anthropic` 或 `claude`；`description` 必填、不超過 1024 字元、不含 XML 標籤；有 `compatibility` 時 1–500 字元；`metadata` 為字串對字串；`SKILL.md` 少於 500 行；引用只有一層；`SKILL.md` 引用的相對路徑都存在；`references/`、`scripts/`、`assets/` 內（不含 `__pycache__`）沒有未被引用的檔案。
- 不測寫作品質（例如 description 是否第三人稱）。
- frontmatter 用 PyYAML 解析，不依賴官方 `skills-ref`；PyYAML 加進 `CLAUDE.md` 的安裝指令。
- 現有 `pdf/` 與 `write-paper-notes/` 的 frontmatter 修到符合規格：`version` 移到 `metadata.version` 並改成字串；刪除 `user-invocable` 與 `starchild` 區塊；現有 description 不改寫。`write-paper-notes` 原有的「只剩兩份 .md」測試，其意圖由新的孤兒檔案規則取代，舊測試檔刪除。
- `.pylintrc` 的 `init-hook` 改為依檔案相對位置加入所有 skill 的 `scripts/`，不再寫死單一路徑；`CLAUDE.md` 的 lint 指令與測試指令加入 `evaluate-paper`。

**文件**
- `GLOSSARY.md` 與兩份 ADR 已完成；`CLAUDE.md` 增加 `evaluate-paper` 的架構說明；README 補 skill 總覽、MCP 一段說明與「先判讀再寫筆記」的建議。

## Testing Decisions

- 好測試只驗證外部行為：命令列的輸出 JSON 與結束碼，或 skill 資料夾對規格的符合度；不測內部函式。
- **接縫一：外部指標腳本的命令列介面。** 沿用 `tests/pdf/`、`tests/write_paper_notes/` 以 `subprocess.run([sys.executable, script, ...])` 驅動的做法。啟動測試用本機假 HTTP 伺服器，以 `--api-base` 指向它；回應的 JSON 全在 `conftest.py` 產生，不放靜態檔案。涵蓋：兩來源並列；任一方回報撤稿即撤稿並標明來源；兩方皆無時輸出「查無撤稿紀錄」；DOI 不一致視為失敗；題名查詢只列候選；單一來源失敗時其餘來源照常輸出且逐一記錄；OpenAlex 額度用完的標示；輸出的網址不含 `mailto`；200 但內容形狀錯誤的處理。測試不連真實網路、不需要任何金鑰。
- **接縫二：全 repo 的 skill 規格測試。** 對每個 skill 資料夾參數化，涵蓋上列所有檢查項目。測試所需的違規情境用臨時目錄產生的假 skill 驗證檢查本身會失敗（負向案例），真實 skill 資料夾則驗證通過。這個接縫同時守住 `evaluate-paper` 的 `SKILL.md` 與 `references/`，不另外為它寫指令檔測試。
- **不測的部分：** 判讀報告的內容品質（AI 讀論文後寫出的內容）沒有決定性的測法，只靠 SKILL.md 的自我檢查步驟；題目檔與規則檔只受接縫二檢查，不單獨測。
- **前例：** `tests/write_paper_notes/test_skill_files.py`（被取代的舊測試）、`tests/write_paper_notes/conftest.py` 以執行時產生 fixture 的方式。

## Out of Scope

- 作者層級的外部指標（h-index 等）。
- 為 JIF 或 CiteScore 寫呼叫付費或需金鑰服務的腳本，或讓腳本處理任何金鑰。
- 推薦、內建或安裝任何第三方 MCP。
- 對多篇論文做彙整比較或排序。
- 把判讀整合進 `write-paper-notes`，或讓兩者共用程式。
- 非 PDF 輸入（DOCX 等）。
- 重寫 `pdf/` 與 `write-paper-notes/` 現有的 description。
- 以官方 `skills-ref` 驗證器作為測試依賴。
- 測試判讀報告的內容品質或寫作風格。
- 自動清理暫存區。

## Further Notes

- 兩份 ADR 記錄了不容易回頭的決定：判讀不打分數、指標只有撤稿能影響結論（0002）；金鑰類資料只經使用者自己的 MCP、SKILL.md 只描述功能（0003）。後者與 Anthropic 寫作指南「寫完整 `伺服器名:工具名`」的建議相反，原因寫在 ADR。
- 已知的不確定：Scopus 免費金鑰是否能取得 CiteScore 尚未確認，因此 skill 不假設可取得；OpenAlex 免費額度的每日上限與計費方式可能變動，腳本不寫死額度數字，只辨識被限流的回應。
- 各 API 的欄位名稱與限流行為以 `.scratch/evaluate-paper/research/appraisal-tools-and-metrics-apis.md` 為準，實作前應再核對一次官方文件。
- 提交前依 `CLAUDE.md` 的規定，要先給使用者看提交分組並等確認。
