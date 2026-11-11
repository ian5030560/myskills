# 02: 頁面圖渲染腳本

**What to build:** 對一份 PDF 執行頁面渲染腳本，得到每一頁的**頁面圖**：疊有淡色比例格線、可供 AI 看圖定位；並留下記錄原始 PDF 位置的 manifest，讓之後的裁切只需要頁面圖就能找回 PDF。規格見 spec 的「Page rendering script」。

**Blocked by:** None (can start immediately)

**Status:** done (uncommitted)

- [x] 接受 `--input` 與選填 `--output-dir`，輸出到 `<output-dir>/<input-stem>/pages/`；只用 PyMuPDF
- [x] 非 PDF 輸入與找不到檔案的處理和 01 一致
- [x] 每頁一張 `pN.png`，110 dpi
- [x] 疊十分之一格線，上緣與左緣標 `.1`–`.9`；格線比原型更淡，不遮住圖中細節
- [x] `pages/` 內寫入 manifest，記錄原始 PDF 的絕對路徑
- [x] 命令列測試：頁數與圖檔數一致、圖檔尺寸符合 110 dpi、manifest 存在且指向輸入 PDF
- [x] pylint 通過

## Comments

- 實作：獨立腳本 `render_pages.py`，命令列測試 10 個（`test_render_pages.py`），fixture `blank_pages.pdf`（letter 與 A4 混合）加在 `conftest.py`。整套 `tests/write_paper_notes/` 55 個通過，pylint 10/10。
- 格線透明度從原型的 0.35 降到 0.2（線寬 0.4pt）；測試確認格線存在且淺色（RGB 各分量 ≥150）、格線之外為純白。
- manifest 為 `pages/source.json`，內容 `{"pdf": "<絕對路徑>"}`；格線只畫在記憶體中的頁面上，原始 PDF 不被修改（有測試）。
- stdout：`pages dir: <路徑>`、`pages: <頁數>`。
- 實測：cs.pdf 10 頁、survey.pdf 51 頁都正常輸出；格線比原型淡，圖中數字仍可辨識。
