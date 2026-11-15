# 05: 標準檢查表：AMSTAR 2、CASP、MMAT 與選擇規則

**What to build:** 判讀時 AI 依論文的研究設計挑選對應的標準檢查表，逐題回答並附原文位置，外部評估因此有標準工具可依循。研究設計不符任何檢查表時，報告明說並只做內容判斷。規格見 `.scratch/evaluate-paper/spec.md` 的 Implementation Decisions「判讀流程」「授權」；授權、題目結構與評等方法見 `.scratch/evaluate-paper/research/appraisal-tools-and-metrics-apis.md`。

**Blocked by:** 04

**Status:** done (uncommitted)

- [x] 選擇規則檔：依研究設計對應 CASP（依設計分冊）、AMSTAR 2（系統性回顧）、MMAT（混合方法等）；不符任何檢查表時的處理
- [x] AMSTAR 2 題目檔：回答為 Yes／Partial Yes／No，依 7 個關鍵領域（第 2、4、7、9、11、13、15 題）決定整體信心 High／Moderate／Low／Critically low；註明 BMJ 論文出處與 CC BY 4.0
- [x] CASP 題目檔：檔案開頭單獨標示 CC BY-NC-SA 4.0 授權聲明與出處
- [x] MMAT 題目檔：只用改寫並註明出處，不轉載原文
- [x] 三者都不把題項加總成分數；報告中檢查表的每一題都有回答與原文位置，資訊不足寫「無法判斷」
- [x] 04 中「待檢查表」的註記被替換為實際檢查表流程；報告格式規則與自我檢查涵蓋檢查表部分
- [x] 全 repo 的 skill 規格測試通過（所有新檔案都被 `SKILL.md` 直接引用）
- [x] 對一篇真實論文跑一次，確認檢查表被正確挑選與填寫，觀察記錄在本 ticket 的 Comments

## Comments

- 新增 7 個檔案：`references/checklist-selection.md`（選擇與填寫規則）、`casp-rct.md`、`casp-cohort.md`、`casp-qualitative.md`、`casp-systematic-review.md`、`amstar2.md`、`mmat.md`；`SKILL.md` 第 2 步改為指向它們（101 行內），`report-format.md` 第 12 條改為檢查表段落的規則。全 repo 規格測試 44 項通過。
- **CASP**：2024 版四份 PDF 以 PyMuPDF 抽文字後逐字收錄問題與 CONSIDER 提示，檔頭單獨標示 CC BY-NC-SA 4.0、出處、存取日期與修改處（去掉表單欄位、訓練宣傳；系統性回顧第 4 題提示中的莎士比亞引文也刪除）。
- **AMSTAR 2**：16 題、7 個關鍵領域與整體信心四級依 BMJ 論文。已核對三份資料：(1) 使用者提供的論文 PDF（正文）；(2) 經使用者的 Chrome 開啟 BMJ 頁面，逐頁讀補充圖「AMSTAR 2 instrument」（3 頁，截圖閱讀）；(3) 補充附錄 1 指引文件（8 頁，只讀第 1 頁與最後一頁，其餘未讀）。結果：Partial Yes 僅限第 2、4、7、8、9 題，以及第 11、12、15 題有 No meta-analysis conducted，兩點都證實；另發現第 9 題多 Includes only NRSI／RCTs 選項、第 11 與 9 題要分 RCT 與非隨機研究判斷，已加進 `amstar2.md` 的逐題選項表。「缺陷＝關鍵題答 No、Partial Yes 不算缺陷」表單與指引開頭都沒有逐題定義，仍是我們的解讀，檔案已明寫。**授權疑點**：論文 PDF 與 Europe PMC 寫 CC BY 4.0，但 BMJ 頁面「Request permissions」連結的參數是 CC-BY-NC-4.0，未能判定；補充檔未標授權。`amstar2.md` 目前沒有逐字收錄補充圖的細部準則，只收選項，所以不受影響；若日後要收錄準則，需先確認授權。
- **MMAT**：5 類各 5 題與 S1、S2 最初是依我對 2018 版的了解改寫；使用者提供官方使用手冊（2018-08-01 版，11 頁）後已逐條核對，27 條準則意思全部吻合。核對時補上手冊中漏寫的規則：篩選題答 No 或 Can't tell 的意義、依研究設計選類別的演算法（含分析性橫斷研究與病例對照屬第 3 類、描述性研究屬第 4 類）、Can't tell 的意思、5.4 沒有差異時答 Yes、5.5 不得高於最弱的成分，並註明第二部分有各準則的選用指標。
- **選擇規則的決定**：AMSTAR 2 只用於醫療介入的系統性回顧；其他主題的系統性回顧（例如風險因子的關聯）用 CASP 系統性回顧。方法加基準實驗的論文（如前一次測試的電腦視覺論文）、文獻計量、內容分析都歸為「無適用檢查表」，報告明說並只做內容判斷。
- **真實論文測試**：對一篇開放取用的 AF 與失智症統合分析（投影片第 10 頁出現的文章，不在 `test-papers/`，由 Europe PMC 全文文字閱讀）跑完整流程。選擇規則挑出 CASP 系統性回顧；10 題都有回答與原文位置，其中 4 題為 Can't tell。觀察：
  - 檢查表之外，內容判斷還抓出全文內的不一致（摘要與方法對資料庫、日期的說法矛盾；討論提到亞洲但結果沒有亞洲分區）。
  - CASP 第 10 題「好處是否值得代價」不適用關聯研究，回答 Can't tell 並說明理由；之後可考慮在規則中加一句「不適用時寫不適用」。
  - 此論文的全文引用位置只能到章節層級（讀的是 XML 文字版，沒有頁碼）。
- 未做：RCT 與 MMAT 的實際填寫測試；它們的規則與 CASP 系統性回顧相同，由規格測試守住檔案結構。
