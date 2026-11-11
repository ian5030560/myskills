# 01: 修正 PDF 擷取的圖片與結構問題

**What to build:** `extract.py` 處理學術論文 PDF 時，輸出完整的圖、沒有假圖片、抓得到章節標題，表格保留表格結構，讓 write-paper-notes 寫筆記時有可用的素材。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

來源：`.scratch/write-paper-notes-v2/issues/04-e2e-verification.md` 的 Comments，發現 6–9。重現用的論文放在 `test-papers/cs.pdf`（雙欄 CS 論文）和 `test-papers/survey.pdf`（單欄 survey）。這個資料夾已 gitignore，不可以 commit，文件中也不可以寫出論文標題。

- [ ] 點陣圖以整張輸出，不再被切成碎片（目前一張圖會變成 4 塊，一張折線圖變成 24 塊）
- [ ] 不再輸出頁碼或頁尾浮水印的向量「圖」（每頁一張 85x115 的 `*_v01.png`），也不再輸出全黑的遮罩圖
- [ ] 偵測得到章節標題，章節編號保留
- [ ] 表格不再被攤平成連續文字；單欄論文的段落順序正確
- [ ] 每項修正都有回歸測試，測試用的 PDF 在 `conftest.py` 執行時產生
- [ ] `pytest tests/write_paper_notes` 全綠
