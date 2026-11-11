# 02: 頁面圖渲染腳本

**What to build:** 對一份 PDF 執行頁面渲染腳本，得到每一頁的**頁面圖**：疊有淡色比例格線、可供 AI 看圖定位；並留下記錄原始 PDF 位置的 manifest，讓之後的裁切只需要頁面圖就能找回 PDF。規格見 spec 的「Page rendering script」。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 接受 `--input` 與選填 `--output-dir`，輸出到 `<output-dir>/<input-stem>/pages/`；只用 PyMuPDF
- [ ] 非 PDF 輸入與找不到檔案的處理和 01 一致
- [ ] 每頁一張 `pN.png`，110 dpi
- [ ] 疊十分之一格線，上緣與左緣標 `.1`–`.9`；格線比原型更淡，不遮住圖中細節
- [ ] `pages/` 內寫入 manifest，記錄原始 PDF 的絕對路徑
- [ ] 命令列測試：頁數與圖檔數一致、圖檔尺寸符合 110 dpi、manifest 存在且指向輸入 PDF
- [ ] pylint 通過
