# 01: 文字擷取腳本

**What to build:** 對一份 PDF 執行文字擷取腳本，得到可供 AI 分段閱讀的 `text.md`：依欄位排序的純文字、每頁有頁碼標記、頁首頁尾已去除、編號標題各自成行、沒有文字層的頁面被標出來。非 PDF 輸入直接報錯並提示另存成 PDF。規格見 `.scratch/pdf-extraction-redesign/spec.md` 的 Implementation Decisions「Text extraction script」。這是獨立的新腳本，現行擷取入口先保留不動。

**Blocked by:** None (can start immediately)

**Status:** done (uncommitted)

- [x] 接受 `--input` 與選填 `--output-dir`，輸出到 `<output-dir>/<input-stem>/text.md`；只用 PyMuPDF
- [x] 非 `.pdf` 副檔名（含 `.docx`）以非零狀態結束，訊息說明只支援 PDF、請先另存成 PDF；找不到檔案也以非零狀態結束
- [x] stdout 只印 `text.md` 路徑、頁數、無文字層的頁碼
- [x] 每頁以 `<!-- pN -->` 開頭
- [x] 頁面上下 12% 內、數字正規化後在 ≥30% 頁面重複的文字區塊，以及邊緣的單獨頁碼，都被去除
- [x] 雙欄頁面：跨欄區塊切出段落帶，帶內先左欄再右欄、欄內由上而下
- [x] 合併斷行、接回行尾連字號斷開的字
- [x] 被 PyMuPDF 併進段落區塊的編號標題（章節編號＋短標題）另起一行
- [x] 沒有文字層的頁面在頁碼標記後加上「此頁無文字層」，即使全部頁面都如此也不報錯
- [x] 不輸出標題記號、不重建表格（表格文字照閱讀順序攤平）
- [x] 以 subprocess 執行的命令列測試涵蓋以上行為，測試 PDF 在 `conftest.py` 執行時產生
- [x] pylint 通過

## Comments

- 實作：獨立腳本 `extract_text.py`，命令列測試 16 個（`test_extract_text.py`），fixture 加在 `conftest.py`。整套 `tests/write_paper_notes/` 45 個通過，pylint 10/10。
- 頁首頁尾規則比 spec 寬：除了上下 12% 範圍，每頁最上、最下各 2 個文字區塊也列入候選（有的版型頁尾離頁緣很遠，survey.pdf 的頁尾在約 83% 高度）；候選區塊限 200 字以內，避免數字以外都相同的內文被當成頁首。03 的頁首頁尾判定應沿用同一規則。
- 實測：cs.pdf 的 4.2、4.3 標題各自成行；survey.pdf 的重複頁首頁尾只剩第 1 頁兩處（版權聲明與第 1 頁頁尾，版型和其他頁不同）；cs.pdf 每頁的下載授權聲明已去除。
- 已知未處理：cs.pdf 第 1 頁左側直排的出版資訊仍留在文字中（spec 沒有要求過濾直排文字）。
