# 01: 文字擷取腳本

**What to build:** 對一份 PDF 執行文字擷取腳本，得到可供 AI 分段閱讀的 `text.md`：依欄位排序的純文字、每頁有頁碼標記、頁首頁尾已去除、編號標題各自成行、沒有文字層的頁面被標出來。非 PDF 輸入直接報錯並提示另存成 PDF。規格見 `.scratch/pdf-extraction-redesign/spec.md` 的 Implementation Decisions「Text extraction script」。這是獨立的新腳本，現行擷取入口先保留不動。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 接受 `--input` 與選填 `--output-dir`，輸出到 `<output-dir>/<input-stem>/text.md`；只用 PyMuPDF
- [ ] 非 `.pdf` 副檔名（含 `.docx`）以非零狀態結束，訊息說明只支援 PDF、請先另存成 PDF；找不到檔案也以非零狀態結束
- [ ] stdout 只印 `text.md` 路徑、頁數、無文字層的頁碼
- [ ] 每頁以 `<!-- pN -->` 開頭
- [ ] 頁面上下 12% 內、數字正規化後在 ≥30% 頁面重複的文字區塊，以及邊緣的單獨頁碼，都被去除
- [ ] 雙欄頁面：跨欄區塊切出段落帶，帶內先左欄再右欄、欄內由上而下
- [ ] 合併斷行、接回行尾連字號斷開的字
- [ ] 被 PyMuPDF 併進段落區塊的編號標題（章節編號＋短標題）另起一行
- [ ] 沒有文字層的頁面在頁碼標記後加上「此頁無文字層」，即使全部頁面都如此也不報錯
- [ ] 不輸出標題記號、不重建表格（表格文字照閱讀順序攤平）
- [ ] 以 subprocess 執行的命令列測試涵蓋以上行為，測試 PDF 在 `conftest.py` 執行時產生
- [ ] pylint 通過
