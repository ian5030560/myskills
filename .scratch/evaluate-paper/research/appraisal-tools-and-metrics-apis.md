# 評讀工具授權與引用指標 API 調查（evaluate-paper Stage 1）

調查日期：2026-11-13。只採用一手來源（工具官方網站、官方 PDF、原始論文全文、官方 API 文件），另以實際呼叫 API 驗證欄位。無法由一手來源確認的事項標為 **unconfirmed**。

## 摘要表

| 工具（版本） | 可逐字引用題目？ | 可改寫／轉述？ | 必要標註 | 官方整體評等 |
|---|---|---|---|---|
| CASP checklists（RCT／Cohort／Qualitative／Systematic Review，2024 版） | 可以，限非商業用途；授權為 CC BY-NC-SA 4.0 | 可以，但衍生內容必須同樣以 CC BY-NC-SA 4.0 釋出（ShareAlike） | 註明 CASP、附授權連結、標明是否修改；CASP 建議 Harvard 格式引用 | 無。CASP 不設計分制度，但 FAQ 表示依 CASP 分成 high/moderate/low「完全可以接受」 |
| AMSTAR 2（2017） | 可以；原始論文（BMJ 2017;358:j4008）以 CC BY 4.0 釋出，允許商業使用 | 可以（CC BY 允許 remix/adapt） | 適當引用原始論文（Shea et al. 2017），附授權連結、標明修改 | 有：整體信心 High／Moderate／Low／Critically low，依 7 個建議的 critical domains 判定；明確反對加總分數 |
| MMAT（2018 版） | **unconfirmed**：沒有找到 Creative Commons 或其他明示的轉載授權；作者已登記著作權，FAQ 只說可自由「使用」並引用 | **unconfirmed**（沒有明示條款）；轉述＋引用是風險最低的做法 | 引用 Hong et al. 2018，含著作權登記號 #1148552 | 無。使用手冊不鼓勵計算總分，建議逐條呈現；FAQ 說高／低品質分界是任意的 |

---

## Part A — 評讀工具

### A1. CASP checklists

**1. 授權與使用條款**

- CASP 官網的 Referencing 頁面寫明：「©CASP this work is licensed under the Creative Commons Attribution – Non-Commercial- Share A like」，並連到 CC BY-NC-SA 4.0。內容包括可以 adapt（remix、transform、build upon）、不得商業使用，衍生作品必須以相同授權發布。來源：https://casp-uk.net/referencing/ 、https://creativecommons.org/licenses/by-nc-sa/4.0/
- 四份 2024 版 checklist PDF（RCT、Cohort、Qualitative、Systematic Review）的最後一頁都有相同的聲明，連結也是 BY-NC-SA 4.0（以 PyMuPDF 抽取 PDF 文字核對）。來源：下方各 PDF。
- CASP FAQ 寫道「we have a creative commons license for these」，以及只要有標註來源就歡迎在工作中使用。來源：https://casp-uk.net/faqs/
- 版本差異：舊版（約 2018 年）checklist 引用的是 CC BY-NC-SA **3.0**；另有一份 2022 版 Systematic Review PDF 據搜尋摘要指向 CC BY-SA 4.0。我只核對了 2024 版的 PDF，2022 版的說法 **unconfirmed**。請以 2024 版為準。
- 必要標註：依 CC 條款，要「give appropriate credit, provide a link to the license, and indicate if changes were made」。CASP 建議 Harvard 格式，例如：Critical Appraisal Skills Programme (2024). CASP (checklist 名稱) Checklist. [online] Available at: URL. Accessed: 日期。來源：https://casp-uk.net/referencing/ ，以及 2024 RCT PDF 第 6 頁。
- 結論：在免費、非商業的公開 repo 中，**可以逐字引用，也可以改寫**。條件是：(a) 註明出處並附授權連結；(b) 標明修改處；(c) 含 CASP 內容或其改寫的檔案必須以 CC BY-NC-SA 4.0 釋出（ShareAlike）。注意：本 repo 根目錄目前沒有 LICENSE 檔，這些 reference 檔要另外標示授權。

**2. 官方網址與版本**（2024 版；頁面本身沒寫版本號，年份取自下載檔名，PDF metadata 的建立日期為 2024-10-21）

- 總覽：https://casp-uk.net/casp-tools-checklists/
- RCT：https://casp-uk.net/casp-tools-checklists/randomised-controlled-trial-rct-checklist/ ，PDF：https://casp-uk.net/casp-checklists/CASP-checklist-randomised-controlled-trials-RCT-2024.pdf
- Cohort：https://casp-uk.net/casp-tools-checklists/cohort-study-checklist/ ，PDF：https://casp-uk.net/casp-checklists/CASP-checklist-cohort-study-2024.pdf
- Qualitative：https://casp-uk.net/casp-tools-checklists/qualitative-studies-checklist/ ，PDF：https://casp-uk.net/casp-checklists/CASP-checklist-qualitative-2024.pdf
- Systematic Review：https://casp-uk.net/casp-tools-checklists/systematic-review-checklist/ ，PDF：https://casp-uk.net/casp-checklists/CASP-checklist-systematic-reviews-checklist-2024.pdf
- 結構（由 2024 版 PDF 計數）：
  - RCT：11 題，第 4 題分為 (a)(b)(c)，分 Section A–D。2024 版新增「Was the study methodologically sound?」段落，與 How-to 頁提到的新增段落一致：https://casp-uk.net/how-to-use-checklist/
  - Cohort：12 題，Section A–C
  - Qualitative：10 題，Section A–C
  - Systematic Review：10 題，Section A–C
- 作答選項為 Yes／No／Can't tell，每題附 "CONSIDER" 提示。PDF 末尾有 Appraisal Summary（Positive／Negative／Unknowns）。來源：上列 PDF、https://casp-uk.net/how-to-use-checklist/

**3. 計分**

- FAQ：這些工具是為教學設計的，因此「we do not assign a scoring system」。如果前 2–3 題無法答 Yes，證據可能品質不佳。依 CASP 把品質分成 high、moderate 或 low「would be perfectly acceptable」。FAQ 也提到目前主流看法偏好報告具體有偏誤的面向，而不是分數。來源：https://casp-uk.net/faqs/
- 2024 PDF：如果 "Can't tell" 很多，就要考慮結果是否可信，並謹慎解讀。來源：RCT 2024 PDF 第 1 頁。
- 官方沒有定義整體評等的判定規則。

**4. 涵蓋設計**

CASP 另有 Case Control、Diagnostic、Economic Evaluation、Clinical Prediction Rule、Cross-Sectional，以及兩份 SR-with-meta-analysis（RCT／observational）checklist。本 skill 選定的四份分別對應 RCT、cohort、qualitative、systematic review。來源：https://casp-uk.net/casp-tools-checklists/

### A2. AMSTAR 2

**1. 授權與使用條款**

- 原始論文：Shea BJ, Reeves BC, Wells G, et al. AMSTAR 2: a critical appraisal tool for systematic reviews that include randomised or non-randomised studies of healthcare interventions, or both. BMJ 2017;358:j4008. doi:10.1136/bmj.j4008
- 授權：「This is an Open Access article distributed in accordance with the terms of the Creative Commons Attribution (CC BY 4.0) license」。依此授權可以 distribute、remix、adapt，含商業用途，條件是正確引用原作。版權聲明為 © BMJ 2017。來源：Europe PMC 全文 XML 的 `<permissions>`：https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5833365/fullTextXML （PMC 頁面 https://pmc.ncbi.nlm.nih.gov/articles/PMC5833365/ ；bmj.com 對抓取回 403，因此未直接核對）
- 16 題題目全文刊在論文內文中（已由全文 XML 核對），因此**題目的逐字引用與改寫都在 CC BY 4.0 範圍內**。帶 guidance 的完整表單是否放在 supplementary file，以及該檔案是否同樣是 CC BY，**unconfirmed**。
- 官網 https://amstar.ca/ 目前顯示網站暫停、重建中，只有登入連結與「Copyright © 2026 AMSTAR All Rights Reserved」字樣；原本的 https://amstar.ca/Amstar-2.php 回 404。因此**不要引用 amstar.ca 上的表單**，以 BMJ 論文為準。
- 作者鼓勵改編者回報經驗（「if they adapt the instrument for particular settings, to report their experience at www.amstar.ca」）。來源：同上全文 XML。

**2. 官方網址與版本**

AMSTAR 2（2017），以 BMJ 論文為準：https://doi.org/10.1136/bmj.j4008 。amstar.ca 官網目前無法使用（見上）。

**3. 計分與整體評等**

- 反對總分：「We strongly recommend that individual item ratings are not combined to create an overall score」，以及「responses to AMSTAR 2 items should not be used to derive an overall score」。來源：全文 XML。
- 作答選項：Yes／Partial Yes／No（部分題目另有「No meta-analysis conducted」）。資訊不足時「should not be given the benefit of doubt」，應評為 No。來源：全文 XML。
- 建議的 7 個 critical domains（Box 1）：item 2（事前註冊 protocol）、4（文獻搜尋是否充分）、7（排除研究的理由）、9（納入研究的 RoB 評估）、11（統合分析方法）、13（詮釋結果時是否考慮 RoB）、15（發表偏誤）。作者說明這份清單「is a suggestion and appraisers may add or substitute other critical domains」。來源：全文 XML。
- 整體信心（Box 2）：
  - High：沒有或只有 1 個 non-critical weakness
  - Moderate：超過 1 個 non-critical weakness，但沒有 critical flaw
  - Low：1 個 critical flaw，有無 non-critical weakness 皆同
  - Critically low：超過 1 個 critical flaw，有無 non-critical weakness 皆同
  - 註：多個 non-critical weakness 可以把 Moderate 降為 Low。
  - 來源：全文 XML。

**4. 涵蓋設計**

AMSTAR 2 用於「systematic reviews that include randomised or non-randomised studies of healthcare interventions, or both」。來源：全文 XML。

### A3. MMAT（Mixed Methods Appraisal Tool）version 2018

**1. 授權與使用條款**

- 引用格式與著作權：Hong QN, Pluye P, Fàbregues S, Bartlett G, Boardman F, Cargo M, Dagenais P, Gagnon M-P, Griffiths F, Nicolau B, O'Cathain A, Rousseau M-C, Vedel I. Mixed Methods Appraisal Tool (MMAT), version 2018. Registration of Copyright (#1148552), Canadian Intellectual Property Office, Industry Canada。來源：User guide PDF 第 1 頁與 Download 頁。
  - User guide PDF：http://mixedmethodsappraisaltoolpublic.pbworks.com/w/file/fetch/127916259/MMAT_2018_criteria-manual_2018-08-01_ENG.pdf
  - Download 頁：http://mixedmethodsappraisaltoolpublic.pbworks.com/w/page/127425845/Download%20the%20MMAT
- 官方 FAQ 對「請求使用許可」的回答是：可以自由使用 MMAT 並引用相關文獻，它是公開的，供教育與研究免費使用；另一則回答說 MMAT 是 public resource，請引用最新版。來源：http://mixedmethodsappraisaltoolpublic.pbworks.com/w/page/71030694/FAQ
- 找不到 CC 或其他明示允許**重製／再散布題目文字**的條款，這部分 **unconfirmed**。wiki 頁首的「[licensed for non-commercial use only]」看起來是 PBworks 平台方案的標記，不是 MMAT 本身的授權，因此不能當作授權依據（推論，**unconfirmed**）。手冊寫明「For dissemination, application, and feedback: Please contact mixed.methods.appraisal.tool@gmail.com」。
- 結論：MMAT 在本 repo 的引用方式有兩種選擇：(a) 用自己的話轉述 criteria 並附正式引用（風險最低）；(b) 若要逐字收錄 S1–S2 和 5×5 題，先寫信到上列信箱取得書面同意。

**2. 官方網址與版本**

Version 2018，User guide 最後更新為 2018-08-01（另有 2018-08-08 修訂檔）。首頁：http://mixedmethodsappraisaltoolpublic.pbworks.com/ （說明「The latest version of the MMAT was updated in 2018」）。

**3. 計分**

- 手冊的 "How to score?"：「It is discouraged to calculate an overall score from the ratings of each criterion」，建議逐條詳細呈現，並可做 sensitivity analysis；通常也不鼓勵排除低品質研究。來源：User guide PDF 第 1 頁。
- FAQ：
  - 不鼓勵用單一數字。若真的要用，不能只給數字而沒有描述。
  - 高／低品質的分界沒有研究依據，「The categories are arbitrary」。
  - 若要計分，「Can't tell」可以當作 0。
  - 另有一份 "Reporting the results of the MMAT" 文件（未讀，**unconfirmed** 內容）：http://mixedmethodsappraisaltoolpublic.pbworks.com/w/file/140056890/Reporting%20the%20results%20of%20the%20MMAT.pdf
  - 來源：上列 FAQ 頁。
- 官方沒有定義整體評等。

**4. 涵蓋設計**

- 5 個類別：(1) qualitative、(2) quantitative randomized controlled trials、(3) quantitative non-randomized、(4) quantitative descriptive、(5) mixed methods。每類 5 題。所有類型共用兩個 screening questions：S1 研究問題是否清楚；S2 收集的資料能否回答研究問題。來源：User guide PDF。
- 只適用於 empirical studies，不適用於 review 或理論文章，也不能評 economic 與 diagnostic accuracy 研究。來源：User guide PDF。
- Mixed methods 研究要評 3 個類別：category 1 ＋ 2/3/4 其中一個 ＋ category 5。來源：FAQ。

---

## Part B — API

### B1. OpenAlex

官方文件已從 docs.openalex.org 轉址到 https://help.openalex.org/ （每頁加上 `.md` 可取得 markdown 版）。

**查詢端點**

- 以 DOI 查 work：`GET https://api.openalex.org/works/https://doi.org/10.7717/peerj.4375`，或短格式 `/works/doi:10.7717/peerj.4375`。也支援 `pmid:`、`arxiv:`。來源：https://help.openalex.org/api/get-single-entities.md
- 批次查 DOI：`/works?filter=doi:A|B`，最多 100 個，1 credit。來源：https://help.openalex.org/api/filtering.md
- 以標題搜尋：
  - `/works?search.title=...`：scoped search parameter，另有 `.exact` 形式。
  - filter 形式為 `title.search:...`；`search=` 是廣泛搜尋。
  - 可以直接貼含 `?` 的標題。
  - 來源：https://help.openalex.org/api/searching.md
- 用 `select=` 只取需要的欄位。來源：https://help.openalex.org/api/authentication.md （Best practices）

**Work 欄位**（來源：https://help.openalex.org/data/works/attributes.md ）

- `cited_by_count`：引用此 work 的 works 數，也就是成功比對到的 reference 數。
- `counts_by_year`：最近十年每年的 `cited_by_count`。引用數為零的年份省略，十年以前的引用不計入。可能與即時計數有落差。
- `type`：每個 work 恰有一個，例如 `article`、`preprint`、`dataset`、`paratext`；完整詞彙見 https://help.openalex.org/data/work-types/
- `is_retracted`：以下任一成立即為 true：Retraction Watch 列為已撤回（且未恢復）、Crossref 或 PubMed 記錄了撤回、標題以 "Retracted" 開頭。OpenAlex 每天讀取 Crossref 發布的 Retraction Watch 資料，通常隔天就會反映。
- `primary_location`：最接近 version of record 的版本。其中的 `source` 為 dehydrated source，有 `id`、`display_name`、`issn_l`、`type` 等。filter 可用 `primary_location.source.summary_stats.2yr_mean_citedness` 等查詢期刊屬性，但 work 本身不存這些值；要取得數值，需再以 source id 查一次。
- 額外欄位 `study_designs`：自動標註，可能值有 RCT、Clinical Trial、Observational Study、Case Report、Systematic Review、Meta-Analysis、Study Protocol。空清單代表「沒標到」，不代表「不是研究」。可作為選 checklist 的輔助訊號，但不能當作定論。

**Source（期刊）`summary_stats`**

- `2yr_mean_citedness`：官方說明為「a journal impact factor-style measure: the mean `cited_by_count` of the source's works published this year or in the two years before, counting every work except peer reviews」。
- `h_index`、`i10_index`：以全部 works 計算。
- 共通說明：這些是 convenience metrics，嚴謹分析應自行從底層 works 計算。work 層級沒有 summary_stats。
- 來源：https://help.openalex.org/data/sources/attributes.md 、https://help.openalex.org/data/common-attributes.md
- 與 JIF 的差異：OpenAlex 只自稱「JIF-style」。它的分母包含 peer review 以外的全部 works，引用來源是 OpenAlex 自己的引用圖，時間窗口也依官方文字為「當年或前兩年發表」。Clarivate JIF 的定義是：前兩年 citable items 在 JCR 年度所得引用 ÷ 前兩年 citable items 數（Web of Science 資料）。JIF 的完整定義未在本次從 Clarivate 一手頁面核對，**unconfirmed**；兩者不可互換或直接比較。

**Author `summary_stats`**

同樣有 `2yr_mean_citedness`、`h_index`、`i10_index`，全部由 profile 內的 works 推算，可 filter/sort（例如 `summary_stats.h_index:>40`）。author profile 是推論出的 works 集合，可能誤併或缺漏。來源：https://help.openalex.org/data/authors.md

**驗證**

2026-11-13 不帶 key 呼叫 `/works/doi:10.7717/peerj.4375` 回 200，`X-RateLimit-Credits-Used: 0`。`/sources/issn:2167-8359?select=summary_stats` 回傳 `2yr_mean_citedness`、`h_index`、`i10_index`。`search.title` 查詢扣 10 credits。

**認證、價格、速率**（2025–2026 的變動）

- 2026-01 的公告（Jason Priem，openalex-users Google Group）宣布：自 **2026-02-13** 起 API 需要 key；polite pool 與 email 參數取消（「No more email parameter」）。當時方案是有 key 每天 100,000 credits，沒 key 只有 100 測試 credits，之後回 409。來源：https://groups.google.com/g/openalex-users/c/rI1GIAySpVQ
- **目前**官方文件（2026-11）的說法與上述公告不同：「you can make basic queries with no key at all」。改用美元計價：
  - 沒 key：每天 $0.10
  - 免費 key：每天 $1（10 倍）
  - 預算每天 UTC 午夜重置；新帳號的第一個 $1 有速度限制
  - 來源：https://help.openalex.org/api/authentication.md 、https://help.openalex.org/access/pricing.md
- 我實測不帶 key 的回應標頭為 `X-RateLimit-Limit-USD: 0.1` 與 `X-RateLimit-Limit: 1000`，與文件一致，也就是 1 credit = $0.0001。
- 注意：Deprecations 頁仍寫著「All users need an API key」與「The `mailto` parameter is ignored」，與 Authentication 頁互相矛盾。實測以 Authentication 頁的說法為準（keyless 可用），mailto 參數則已確定被忽略。來源：https://help.openalex.org/api/deprecations.md
- 每次操作的成本（來源：https://help.openalex.org/access/example-costs.md ）：

  | 操作 | 成本 |
  |---|---|
  | 單筆查詢（by ID／DOI） | 免費 |
  | list＋filter | 1 credit（$0.10／千次） |
  | search | 10 credits（$1／千次） |
  | content download | $10／千次 |

  沒 key 時每天約可做 100 次標題搜尋，DOI 查詢不限次數。
- 每秒上限：沒 key 10 req/s；免費 key 或 prepaid 30 req/s；annual plan 50 req/s。每秒限速觸發的 429 不扣費。
- 使用 cursor paging 翻過第一頁需要 key。
- 傳 key 的方式：`api_key=` query 參數，或 `Authorization: Bearer`。
- 來源：https://help.openalex.org/api/authentication.md
- 付費方案有 prepaid（以 $1 為單位加值）與 annual plan（Member $5,000/年起）。資料本身是 CC0。來源：https://help.openalex.org/access/pricing.md
- 附帶：官方文件提供 `POST https://api.openalex.org/api-keys` 端點，代理程式可以替使用者以 email 申請 key（使用者需點擊 email 中的啟用連結）。這涉及使用者個資，skill 不應自動執行；要用的話，請使用者自己到 https://openalex.org/settings/api-key 申請 key，再設成環境變數 `OPENALEX_API_KEY`。

### B2. Crossref REST API

**DOI 查詢與標題搜尋**

- 以 DOI 查詢：`GET https://api.crossref.org/works/{DOI}`（文件中也寫作 `/v1/works/{DOI}`）。
- 標題／書目搜尋：`/works?query.bibliographic=...`，涵蓋 title、authors、ISSN、年份等，適合用來比對引用。
- 來源：https://api.crossref.org/swagger-docs 、https://www.crossref.org/blog/retraction-watch-retractions-now-in-the-crossref-api/

**`is-referenced-by-count`**

「Count of inbound references deposited with Crossref」，也就是只計入 Crossref 會員有存 reference 的引用，所以通常低於 OpenAlex 或 Google Scholar。來源：https://github.com/CrossRef/rest-api-doc/blob/master/api_format.md

**更正與撤回**

- `update-to`：出現在**更正／撤回通知本身**的記錄上，指向被更新的原文。`source` 為 `publisher` 或 `retraction-watch`，Retraction Watch 的條目另有 `record-id`，對應 RW CSV 的列，CSV 中有撤回原因。
- 篩選全部撤回：`filter=update-type:retraction`。同一筆撤回可能因來源不同而出現多次。
- 來源：https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/ （最後更新 2025-01-19）、https://www.crossref.org/blog/retraction-watch-retractions-now-in-the-crossref-api/ （2025-01-29）
- `updated-by`：出現在**原文**記錄上。官方 RW 文件頁只提到 `update-to`，但 swagger 欄位清單同時列出 `update-to`、`updated-by`、`update-policy`、`relation`。
  - 實測：在 production API 查 10.1016/S0140-6736(97)11096-0（Wakefield 1998），`updated-by` 有 `{"type":"retraction","source":"retraction-watch","record-id":"4036",...}`（另有一筆 correction）。
  - 查撤回通知 10.1016/s0140-6736(10)60175-4，則 `update-to` 指回原文。
  - 因此 CLI 判斷一篇文章是否被撤回，**應讀原文的 `updated-by`**，並檢查其中是否有 `type` 為 `retraction`（以及 `expression-of-concern` 等）的項目。
  - `updated-by` 的正式文件說明 **unconfirmed**，目前只有 swagger 欄位清單和實測可以佐證。
- Crossmark 機制：撤回關係原本只記在撤回通知的 Crossmark deposit 中，由 Crossmark 把兩筆記錄連起來，讓原文顯示「updated by」。`update-policy` 是 Crossmark 更新政策的 URL。來源：https://www.crossref.org/documentation/register-maintain-records/maintaining-your-metadata/registering-updates/ 、api_format.md
- Retraction Watch 資料庫在 2023 年 9 月由 Crossref 取得並公開，每個工作日更新。Crossref 要求在出版物中使用 RW 資料時註明來源。來源：同上 RW 文件頁與部落格。

**認證、速率與 polite pool**

- 不需註冊。三種存取方式：
  - Public：不需識別
  - Polite：在 `mailto` 參數或 User-Agent 加 email
  - Metadata Plus：付費，header 帶 `crossref-api-key: Bearer ...`
- 速率與並行上限：

  | Pool | 速率 | 並行 |
  |---|---|---|
  | Public | 5 req/s | 1 |
  | Polite | 10 req/s | 3 |
  | Plus | 150 req/s | 無限制 |

  超過會回 429，被人工封鎖會回 403。官方強烈建議所有請求都帶 mailto，並設定可識別的 User-Agent、做快取。
- 來源：https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/ （最後更新 2025-10-16）
- 實測不帶 mailto 時，回應標頭為 `x-rate-limit-limit: 5`、`x-rate-limit-interval: 1s`、`x-concurrency-limit: 1`、`x-api-pool: public-single`，與文件一致。

### B3. JIF 與 CiteScore 的程式化存取

- **JIF（Clarivate JCR）**：沒有免費 API。Web of Science Journals API 寫明「Access to this API requires a paid license」，是 JCR 或 InCites 的 add-on subscription，上限 5 req/s。來源：https://developer.clarivate.com/apis/wos-journal
- **CiteScore（Scopus）**：Elsevier 的 Scopus APIs「available for no charge, for non-commercial use」，需要先註冊 Elsevier 帳號並申請 API key。來源：https://dev.elsevier.com/sc_apis.html
  - Serial Title API 有 `CITESCORE` view，配額為每週 20,000 次、6 req/s。來源：https://dev.elsevier.com/documentation/SerialTitleAPI.wadl 、https://dev.elsevier.com/api_key_settings.html
  - 但新 key「do not provide data or content access by default」，存取權取決於 entitlement。在非訂閱機構網路下，CiteScore view 能否用免費 key 取得 **unconfirmed**。
  - 因為需要個人 key，且使用條款限制多（未詳讀，**unconfirmed**），不適合放進 stdlib-only、零設定的 CLI。

---

## Implications for the skill

1. **CASP 內容獨立成檔並標註 CC BY-NC-SA 4.0。**
   - 可以逐字收錄 2024 版題目與 CONSIDER 提示，但要把 CASP 的四份 reference 檔（例如 `references/casp-rct.md`）的檔頭寫明：出處（Harvard 格式、URL、存取日期）、CC BY-NC-SA 4.0 連結、相對於原版做了哪些修改。
   - 這些檔案本身以 BY-NC-SA 4.0 釋出。
   - repo 目前沒有 LICENSE。若日後整個 repo 採用寬鬆授權（MIT 等），要在 README 或 LICENSE 中把 CASP 衍生檔列為例外。
2. **AMSTAR 2 以 BMJ 2017 論文為唯一來源（CC BY 4.0）。**
   - 可以逐字收錄 16 題、Yes／Partial Yes／No 選項、7 個 critical domains 與 Box 2 的四級整體信心。
   - 引用 Shea et al. 2017，並附 DOI 與 CC BY 4.0 連結。
   - 不要連到 amstar.ca（目前停站）。
3. **MMAT 先用轉述，或寄信取得同意。**
   - 沒有明示的再散布授權，建議 reference 檔用自己的話描述 5 類各 5 個 criteria 的要點，附正式引用（含著作權登記號 #1148552）和官方 PDF 連結，由使用者自行查閱原文。
   - 若要逐字收錄，先寄信到 mixed.methods.appraisal.tool@gmail.com 取得書面同意。這需要使用者本人寄送。
4. **不要產生總分。**
   - 三種工具的作者都反對或不鼓勵加總。skill 的輸出應逐題列出 Yes／No／Can't tell（AMSTAR 2 加 Partial Yes），每題附依據（頁碼或引文）。
   - 只有 AMSTAR 2 可以輸出官方的四級整體信心，並明列觸發的 critical flaws。
   - CASP 與 MMAT 只能給出敘述性摘要（CASP 的 Positive／Negative／Unknowns）。如果一定要給 high/moderate/low，必須寫明那是 skill 自己定義的規則（CASP FAQ 允許這樣做，MMAT FAQ 說分界是任意的），而不是官方評等。
5. **Checklist 的選擇規則**
   - RCT → CASP RCT；cohort → CASP Cohort；qualitative → CASP Qualitative；systematic review（醫療介入）→ AMSTAR 2，另可搭配 CASP SR；mixed methods 或不易歸類的 empirical study → MMAT（mixed methods 要評 1＋{2,3,4}＋5 三個類別）。
   - 可用 OpenAlex 的 `study_designs` 與 `type` 輔助判斷，但以 AI 閱讀全文的結果為準。
   - 非 empirical 的論文（review、理論）不要套用 MMAT 或 CASP 的 primary-study checklist。
6. **OpenAlex CLI 設計（stdlib `urllib`）**
   - 優先用 DOI 單筆查詢（免費），流程為 work → `primary_location.source.id` → `/sources/{id}?select=display_name,summary_stats` → 必要時查第一作者 `/authors/{id}?select=summary_stats`。
   - 一律使用 `select=` 只取需要的欄位。
   - 沒有 DOI 時才用 `search.title`（每次 10 credits，沒 key 每天約 100 次）。
   - 選填讀取環境變數 `OPENALEX_API_KEY`，以 `Authorization: Bearer` 傳送。沒 key 也能運作。
   - **不要傳 `mailto`**（已被忽略），也不要替使用者呼叫 `/api-keys`。
   - 處理 429（讀 `Retry-After`）與 403 `key_not_activated`，並把 `X-RateLimit-Remaining-USD` 顯示在 stderr。
7. **Crossref CLI 設計**
   - `GET /works/{DOI}`，讀取 `is-referenced-by-count`、`updated-by`（以 `type` 判斷 retraction／correction／expression-of-concern，記錄 `source` 與 `record-id`）、`update-policy`、`relation`。
   - 撤回狀態要交叉比對 OpenAlex 的 `is_retracted` 和 Crossref 的 `updated-by`，任一方報告撤回就標紅。
   - 建議讓使用者以環境變數（例如 `CROSSREF_MAILTO`）提供 email 進入 polite pool。沒提供就走 public pool（5 req/s、並行 1），CLI 以序列方式送出請求即可。
   - 設定可識別的 User-Agent，但不要放入使用者個資，除非使用者主動提供 mailto。
8. **指標呈現的措辭**
   - 報告中寫成「OpenAlex 2-year mean citedness（JIF-style，非 JIF）」。註明它與 JIF 的定義和資料來源不同；h-index 與 i10 的計算基準是 OpenAlex 的全部 works。
   - 不承諾提供 JIF 或 CiteScore（沒有免費 API）。若使用者想看，請他自己到 JCR 或 Scopus Sources 網頁查詢。
   - 三個來源的引用數（OpenAlex `cited_by_count`、Crossref `is-referenced-by-count`、Google Scholar）基準不同，報告時要並列並說明，不要只挑一個數字。
9. **之後需要補查的 unconfirmed 項目**
   - MMAT 是否有明確的再散布許可（直接詢問作者）
   - AMSTAR 2 supplementary 表單的授權
   - Crossref `updated-by` 的正式文件說明
   - Scopus Serial Title API 的 CiteScore view 對免費 key 的 entitlement
   - CASP 2022 版的授權
   - Clarivate JIF 的一手定義頁
