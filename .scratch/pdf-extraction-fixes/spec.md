Status: needs-triage

# write-paper-notes：PDF 擷取品質問題

來源：`.scratch/write-paper-notes-v2/issues/04-e2e-verification.md` 的 Comments，發現 6–9。測試論文在 `test-papers/`（gitignored），文件中只能用 `cs.pdf` / `survey.pdf` 稱呼。

## 問題

1. 點陣圖被切成碎片：cs.pdf 一張圖被切成約 4 塊，一張折線圖被切成 24 塊。
2. 假圖片：cs.pdf 每頁都有一張只含頁碼和浮水印的 `*_v01.png`；survey.pdf 約有 70 張全黑遮罩圖。
3. 標題偵測失效：每篇只偵測到 1 個 `#`，章節變成「- Introduction」這種條列，章節編號也不見。
4. 表格被攤平成文字；survey.pdf 有些段落的閱讀順序錯亂。

## 下一步

尚未整理成 spec。開始處理時，先用 `/grill-with-docs` 或 `/to-spec` 把這份筆記轉成正式 spec。

## Comments

- 已由 `.scratch/pdf-extraction-redesign/spec.md` 取代：改為只接受 PDF、文字層純文字加頁面圖、由 AI 寬鬆框選並由腳本剝邊裁切（見 `docs/adr/0001-pdf-only-ai-cropped-figures.md`）。
