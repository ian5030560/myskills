# 09: 檢查表題目不適用時的回答方式

**What to build:** 有些檢查表題目對特定研究不適用（例如 CASP 系統性回顧第 10 題「好處是否值得代價」對沒有介入的關聯或描述性回顧）。目前規則只允許 Yes／No／Can't tell，不適用的題目只能答 Can't tell，語意不精確，會讓使用者誤以為是論文沒寫清楚。來源：ticket 05 待辦與 ticket 07 端到端驗證的發現 2。

**Blocked by:** none

**Status:** done (uncommitted); last item partly done

- [x] 決定做法並寫進 `references/checklist-selection.md` 的「Filling in」：例如新增「不適用」作答，並要求寫出不適用的理由
- [x] 說明「不適用」與「無法判斷」的差別：不適用是題目不適合這個設計；無法判斷是論文沒提供資訊
- [x] `references/report-format.md` 第 12 條配合調整：答案可為檢查表原有選項或「不適用」；仍不得計數或加總
- [x] 範圍：CASP 四份、MMAT 都檢視一次，列出哪些題目常不適用；AMSTAR 2 已有「No meta-analysis conducted」選項，不需另加
- [x] 全 repo 的 skill 規格測試通過
- [ ] 用一篇描述性或關聯性的系統性回顧重跑一次，觀察記錄在本 ticket 的 Comments（見 Comments：只重寫了報告的檢查表段落，沒有重跑整個流程）

## Comments

- 背景：AF 統合分析（關聯研究）第 10 題與 `survey.pdf`（描述性回顧）第 7、10 題都只能答 Can't tell。
- 待決定：是否容許修改 CASP 逐字題目檔的作答選項。CASP 授權為 CC BY-NC-SA 4.0，改動需在檔案標示修改，規則放在 `checklist-selection.md` 而不改題目檔較單純。
- 決定（使用者）：「不適用」規則寫在 `checklist-selection.md`，不改 CASP 逐字題目檔，並保留「常不適用題目」清單（目前只列 CASP 系統性回顧第 7、10 題，皆有實例）。
- 追加（使用者）：檢查表段落不用表格，改為 CASP 風格（編號題目、下一行縮排粗體答案加位置與依據）。`report-format.md` 第 12 條已改並附範例；答案可為檢查表選項或「不適用：理由」，不適用也不計數。
- MMAT 依類別選題，AMSTAR 2 有自己的「No meta-analysis conducted」，所以沒有列入常不適用清單。CASP RCT、世代、質性是否有常不適用的題目，沒有實例，沒有列。
- 驗證：把 `survey` 報告的檢查表段落改為新版面（第 7、10 題為不適用），存到 `test-papers/output/survey/appraisal.md`。只改了該段，沒有重跑整個流程。AF 報告仍是舊的表格版，沒有重寫。
