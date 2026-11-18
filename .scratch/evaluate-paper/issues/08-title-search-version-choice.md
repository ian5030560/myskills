# 08: 題名查詢的候選含預印本與正式版時如何選

**What to build:** 論文沒有可用的 DOI（例如 PDF 內是佔位文字）而改用題名查詢時，候選中常同時有預印本與正式版。SKILL.md 要說清楚怎麼處理：讓使用者選，並在報告記錄所讀 PDF 與所選 DOI 是否為同一版本。來源：ticket 07 端到端驗證的發現 1。

**Blocked by:** none

**Status:** done (uncommitted)

- [x] SKILL.md 步驟 2 說明：候選含預印本與正式版時，列出各自的年份與 DOI，請使用者選；不由 AI 自行決定
- [x] 說明選定後如何對照所讀 PDF 的版本（例如 PDF 標示 "Manuscript submitted"、預印本字樣、頁數）與所選 DOI 的版本，並寫在報告的「所讀版本」與「仍需確認」
- [x] 預印本與正式版指標分開查、分開寫，不合併
- [x] 全 repo 的 skill 規格測試通過
- [ ] 用 `test-papers/survey.pdf`（有預印本與正式版兩筆）重跑一次，觀察記錄在本 ticket 的 Comments

## Comments

- 背景：ticket 07 的端到端測試中，OpenAlex 只回正式版，Crossref 回預印本與正式版。當時我自行選了正式版並在報告註明，實際流程應讓使用者選。
- 做法：SKILL.md 步驟 2 在 `--title` 說明後新增「Preprint and formal version」一條（列出各候選與年份、DOI，說明 PDF 像哪一版，讓使用者選，不自行決定；PDF 與所選 DOI 版本不同時寫在身分卡與「仍需確認」；另一版另跑 `--doi`、數字分開）。`report-format.md` 第 11 條補上版本不一致時身分卡與指標段落要寫明數字屬於哪個 DOI。規格測試 44 個通過。
- 未做：用 `survey.pdf` 重跑一次。需要使用者在對話中從候選選一筆，我沒有代替使用者選；目前的 survey 報告是修改前產生的（那次由我自行選了正式版）。
- 重跑（2026-11-18，`survey.pdf`）：題名查詢回預印本與正式版兩筆；我列出兩筆、說明 PDF 是 ACM 模板投稿版（佔位文字、"Manuscript submitted to ACM"），使用者選正式版；`--doi` 取得指標並更新報告：身分卡「所讀版本」與「DOI」寫明選擇，指標段落寫明數字屬於正式版 DOI，「仍需確認」寫明 PDF 與正式版是否一致未核對、預印本未查。報告已複製到 `test-papers/output/survey/appraisal.md`。
- 發現：同一個 DOI 隔三天再查，OpenAlex 被引次數由 18 變 21、`2yr_mean_citedness` 由 19.54 變 14.91。符合「指標是查詢當日數字」的規則，報告與 metrics.json 都要寫查詢日期；不需修改。
- 限制：這次沒有比對 PDF 與預印本或正式版的內容，所以「PDF 屬哪一版」只是依首頁線索判斷。
