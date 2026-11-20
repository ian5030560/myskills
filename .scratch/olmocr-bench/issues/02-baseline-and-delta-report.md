# 02: baseline 與差值報告

**What to build:** run 把結果與 commit 進 repo 的 baseline 比較，印出各類別分數差值，以及新增失敗、新增通過的測試 ID；翻轉的題目若屬於 upstream 已回報的錯題清單就加註。第一份 baseline 用目前的 `extract_text.py` 記錄。README 說明評測範圍與排除原因。

**Blocked by:** 01

**Status:** done (uncommitted)

- [x] baseline 檔記錄日期、`extract_text.py` 所在 commit、評分器版本、各類別通過率與測試數、排除 PDF 數、通過的測試 ID
- [x] run 預設只讀取 baseline 並印出：各類別差值、新增失敗與新增通過的測試 ID；分數下降時不以失敗結束
- [x] `--update-baseline` 旗標才會改寫 baseline
- [x] upstream allenai/olmocr#485 的錯題 ID 清單保存在 benchmark 資料夾；翻轉題目落在清單內時，報告標註「已知錯題」
- [x] 沒有 baseline 時 run 仍能正常印出分數，並提示可用 `--update-baseline` 建立
- [x] 以目前的 `extract_text.py` 建立並 commit 第一份 baseline
- [x] README 寫明：評測範圍、排除 `headers_footers`（單頁限制）、無文字層 PDF、數學／表格／掃描不在設計範圍、一次性的 headers_footers 全文件診斷結果（79.1% 與失敗類型）、相關 upstream issues（#452、#461、#485）、授權
- [x] 文件中不出現測試論文（cs.pdf、survey.pdf）的標題、作者或來源

## Comments

Done. Rerunning without changes gives a zero delta. Editing the baseline by hand made the newly-failing/newly-passing lists and the #485 annotation appear as expected. The first baseline was recorded with extract_text.py `f5755d8` (before the fixes).
