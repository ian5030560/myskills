# 05: 用測試論文手動跑 e2e

**What to build:** 以新版 skill 對 `test-papers/` 中的 cs.pdf 與 survey.pdf 各完整跑一次（擷取 → 撰寫 → 自我檢查 → 清理），確認筆記品質與清理行為，把發現記錄下來。測試論文與輸出都已 gitignored；記錄中只能用 cs.pdf / survey.pdf 稱呼，不得出現論文標題、作者或出處。

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] 兩篇都產出 `notes.md`，並逐條通過 `references/style-guide.md`
- [ ] 筆記中的章節結構對應論文章節編號
- [ ] 筆記中的圖都是完整、乾淨的裁切圖（無碎片、無黑圖、無圖說殘留、四邊完整）
- [ ] 論文中的表格以 Markdown 重建，數值與頁面圖一致
- [ ] 結束後輸出資料夾只剩 `images/` 與 `notes.md`
- [ ] 發現的問題記在本檔 `## Comments`（不提論文名稱）；需要修改的另開 ticket
