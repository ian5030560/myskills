Status: ready-for-agent

# write-paper-notes v2：簡化 skill 內容並重構筆記排版

## Problem Statement

`write-paper-notes` 產出的筆記結構不穩定、指示文件又多又互相矛盾：

- 共用風格指南要求「保留論文原本的標題階層」，但類型專屬 template 又強制套用固定章節（`3.2 Model Architecture` 之類），兩者無法同時滿足，AI 每次取捨不同。
- 品質檢查清單幾乎是風格指南逐條重寫，同一條規則要維護兩處。
- 類型專屬 checklist 要求 pseudocode、超參數表、ablation、「回顧的論文數量」等內容；論文沒有時，AI 為了通過檢查只能自己編。
- 擷取出的圖（含 logo、裝飾線條）被要求「全部」放進筆記。
- 沒有規定筆記語言。
- 總共 9 份指示文件、4 個 Phase，外加論文類型偵測，AI 要讀很多東西才能開始寫，維護者也要在多處同步修改。

## Solution

把 skill 收斂成一套固定骨架、一份風格指南、三步流程：

- **筆記**一律使用同一套**固定區塊**，不再區分論文類型：

  ```
  # <論文標題>
  > 作者 · 年份 · 出處（論文有寫才填）

  ## 介紹        ### 背景 / ### 動機 / ### 研究問題 / ### 貢獻（固定子章節）
  ## 相關研究    子章節照論文走，附比較表
  ## 方法        子章節照論文走
  ## 結果        子章節照論文走
  ## 結論        ### 主要發現 / ### 限制 / ### 未來方向（固定子章節）
  ```

- **風格指南**只有一份，同時是撰寫規則與自我檢查清單。
- 流程為「擷取 → 撰寫 → 自我檢查」。
- 論文沒有的內容一律不寫，對應的區塊或子章節連標題一起省略。
- 筆記語言跟著使用者，判斷不出來就先問。

## User Stories

1. As a 研究者, I want 每份筆記都有相同的頂層區塊, so that 我能用同一套閱讀習慣快速翻多篇筆記。
2. As a 研究者, I want 「方法」與「結果」的子章節照論文自己的章節走, so that 筆記保留作者切分內容的方式。
3. As a 研究者, I want 「介紹」固定分成背景、動機、研究問題、貢獻, so that 我能快速掌握一篇論文的定位。
4. As a 研究者, I want 「結論」固定分成主要發現、限制、未來方向, so that 我不用重讀整篇就能回想它的結論。
5. As a 研究者, I want 「主要發現」每點一句、不重貼表格, so that 結論與結果不重複。
6. As a 研究者, I want 結果區塊放數據、表格與分析, so that 我能回頭查證每個發現的依據。
7. As a 研究者, I want Related Work 獨立成「相關研究」區塊, so that 我能找出這篇站在哪些研究之上、接下來該讀什麼。
8. As a 研究者, I want 相關研究附「方法 / 核心概念 / 與本文差異」比較表, so that 我能一眼比較既有方法。
9. As a 研究者, I want 比較表每格都出自論文、論文沒說的格子留空, so that 我能信任表中內容。
10. As a 研究者, I want 動機只寫一兩句結論、不逐篇列文獻, so that 動機與相關研究不重複。
11. As a 研究者, I want 論文沒有明列研究問題時從問題陳述改寫, so that 大多數 CS 論文也有研究問題可看。
12. As a 研究者, I want 論文連問題陳述都沒有時省略研究問題, so that 筆記不出現捏造的問題。
13. As a 研究者, I want 論文沒有的內容（pseudocode、超參數、實驗）一律不寫, so that 筆記裡的每句話都能在論文中找到出處。
14. As a 研究者, I want 沒有內容的區塊或子章節連標題一起省略, so that 筆記沒有「論文未提及」之類的佔位雜訊。
15. As a 研究者, I want Abstract 不寫進筆記, so that 同一段內容不會出現兩次。
16. As a 研究者, I want Background / Preliminaries 併入「背景」, so that 領域背景集中在一處。
17. As a 研究者, I want Discussion / Analysis 放進「結果」並照論文章節成為子章節, so that 分析緊跟著數據。
18. As a 研究者, I want Limitations 與 Future Work / Open Challenges 分別放進「限制」與「未來方向」, so that 這些內容有固定位置。
19. As a 研究者, I want Appendix 只在正文引用且理解所需時才併入, so that 筆記不被附錄撐大。
20. As a 研究者, I want References 與 Acknowledgments 不進筆記, so that 筆記只留實質內容。
21. As a 研究者, I want 對應表沒涵蓋的章節放到內容最貼近的區塊, so that 任何論文都能套進骨架。
22. As a 研究者, I want survey 的 Taxonomy / Key Approaches 落在「方法」、Comparison / Benchmark 落在「結果」, so that survey 也用同一套骨架。
23. As a 研究者, I want 筆記用我對話時的語言撰寫, so that 我不必另外翻譯。
24. As a 研究者, I want 只給檔案路徑時 AI 先問我要用什麼語言, so that 不會產出錯誤語言的筆記。
25. As a 研究者, I want 非英文筆記的術語第一次出現時寫成「譯名（English）」, so that 我能對回原文術語。
26. As a 研究者, I want 骨架的區塊名稱跟著筆記語言翻譯, so that 不會出現中文標題配英文正文。
27. As a 研究者, I want 要點用條列而非大段散文, so that 筆記好掃讀。
28. As a 研究者, I want 只放跟內容有關的圖, so that logo 與裝飾線條不會混進筆記。
29. As a 研究者, I want 圖放在它說明的子章節、alt text 具體描述內容, so that 圖文對得上。
30. As a 研究者, I want 只在論文以純文字描述流程、而且沒有原圖時才畫 Mermaid, so that 不會出現多餘或不準確的圖。
31. As a 研究者, I want 比較表每欄最佳值加粗, so that 最佳結果一眼可見。
32. As a 研究者, I want 公式用 LaTeX、程式碼用 code block, so that 筆記在 Markdown 檢視器裡正確顯示。
33. As a 研究者, I want 標題下方有「作者 · 年份 · 出處」資訊列（論文有寫才填）, so that 我知道這篇是誰、何時、在哪發表的。
34. As a AI agent, I want 只讀 SKILL.md 和一份風格指南就能完成工作, so that 不用在多份檔案之間來回對照。
35. As a AI agent, I want 自我檢查直接逐條對照風格指南, so that 規則只有一個來源。
36. As a AI agent, I want 不再偵測論文類型, so that 不同論文不會因為類型判斷錯誤而走錯分支。
37. As a skill 維護者, I want 規則只寫在一處, so that 修改一條規則時不必同步兩份文件。
38. As a skill 維護者, I want 一個 pytest 檢查 SKILL.md 提到的路徑都存在, so that 改名或刪檔不會留下失效引用。
39. As a skill 維護者, I want CLAUDE.md 與 README 描述的是新流程, so that 下一個 agent 或使用者不會被舊架構誤導。
40. As a skill 使用者, I want Setup 只有一行安裝指令加上 Windows UTF-8 提示, so that 我能很快開始使用。

## Implementation Decisions

- **範圍只動指示文件**，擷取程式（`extract.py` 及其 extractor）的介面與行為完全不變；擷取的輸出（stdout Markdown + `<output-dir>/<stem>/images/`）以及 `notes.md` 的輸出位置都不變。
- **skill 只留兩份指示文件**：
  - **SKILL.md**：Setup、三步流程、骨架、論文章節對應表。
  - **風格指南**：唯一一份，放在 references 底下，同時也是自我檢查清單。
- **刪除**：兩份類型專屬 template、通用 report template、整個 quality-checklist 目錄、三份分散的 style guide。
- **流程**：
  1. 擷取：執行擷取程式。
  2. 撰寫：讀文字與圖片，依骨架與風格指南寫出 `notes.md`。
  3. 自我檢查：逐條對照風格指南，修正後再檢查一次，直到全部通過。
  - 移除 `PaperType` 偵測與「內容分析」Phase。
- **骨架**：見 Solution。SKILL.md 以中文名稱作為標準名稱，並註明依筆記語言翻譯。
- **論文章節對應表**（寫在 SKILL.md）：

  | 論文章節 | 放到 |
  |:---|:---|
  | Abstract | 不寫進筆記（撰寫時可讀，用來掌握全貌） |
  | Introduction | 介紹的四個固定子章節 |
  | Background / Preliminaries | 背景 |
  | Related Work / Literature Review | 相關研究 |
  | Method；survey 的 Taxonomy / Key Approaches | 方法 |
  | Experiments / Discussion / Analysis；survey 的 Comparison / Benchmark | 結果 |
  | Conclusion | 主要發現 |
  | Limitations | 限制 |
  | Future Work / Open Challenges | 未來方向 |
  | Appendix | 正文有引用、且理解方法或結果需要時，併進對應區塊；否則不放 |
  | References / Acknowledgments | 不放 |
  | 其他 | 內容最貼近的區塊，當作子章節 |

- **風格指南的 10 條規則**：
  1. **不捏造**：只寫論文中有的內容；沒有內容的區塊或子章節連標題一起省略。
  2. **語言**：使用使用者對話的語言；判斷不出來就先問。非英文筆記的術語第一次出現時寫成「譯名（English）」，之後用英文。
  3. **條列**：要點用條列，不寫大段散文，不逐字照抄原文。
  4. **圖片**：只放跟內容有關的圖，放在它說明的子章節，alt text 具體描述內容。
  5. **Mermaid**：只在論文以純文字描述流程、而且沒有對應原圖時才畫；圖上方加粗體標題。
  6. **表格**：比較數據用 Markdown 表格，每欄最佳值加粗。
  7. **公式與程式碼**：公式用 LaTeX（`$...$` / `$$...$$`）；程式碼用 code block，變數用行內反引號。
  8. **分工**：結果放證據，結論放「代表什麼」且不重貼表格；動機只寫一兩句結論，逐篇比較放在相關研究。
  9. **研究問題**：論文沒有明列時，從問題陳述改寫；連問題陳述都沒有就省略。
  10. **相關研究比較表**：欄位為「方法 / 核心概念 / 與本文差異」，每格都要出自論文。
- **Setup**：縮成 `pip install PyMuPDF python-docx` 一行，加上「Windows：在同一個指令裡設定 `PYTHONIOENCODING=utf-8`」與 PowerShell 範例；移除 CMD 寫法與 import 驗證指令。
- **版本**：SKILL.md 的版本號從 1.2.0 升到 2.0.0。
- **同步文件**：
  - CLAUDE.md 的 write-paper-notes 架構段落改成三步流程與單一風格指南，刪掉「新增論文類型只要加三個檔案」的說明。
  - README 的 write-paper-notes 段落改寫：拿掉 type-aware templates、4 Phases、quality gate 等描述，另外拿掉早已不存在的 OCR 描述。
- 領域用語以 `GLOSSARY.md` 為準：筆記、固定區塊、子章節、風格指南。

## Testing Decisions

- 好的測試只驗證外部行為：skill 對外呈現的檔案一致性，以及實際產出的筆記，不驗證文件的措辭。
- **Seam A：端到端執行（手動驗證）**。用新版 skill 處理一篇 CS/ML 論文和一篇 survey，逐項確認：
  - 骨架與固定子章節正確，沒有內容的區塊有省略。
  - Abstract 沒有被寫進筆記。
  - 相關研究附有比較表，而且每格都有出處。
  - 筆記語言跟著使用者。
  - 沒有捏造內容（例如論文沒有 pseudocode，筆記就不出現）。
  - 只放與內容有關的圖。
- **Seam B：新增 skill 一致性 pytest**，放在 write_paper_notes 測試套件中。檢查項目：
  - SKILL.md 引用的每個相對路徑都存在。
  - 舊的 template、checklist 與分散的 style guide 都已不存在。
  - 參考既有測試的寫法：它們以 `Path(__file__)` 定位 skill 目錄，不需要 fixture 檔。
- **既有測試**：`tests/write_paper_notes/` 的擷取測試不受影響，必須維持全綠。

## Out of Scope

- 擷取程式的任何修改，包括雙欄排序、標題階層推斷、向量圖分群與過濾。
- 自動評估筆記品質，例如用 LLM-as-judge 或 eval 套件。
- `pdf/` skill。
- 已經產出的舊版筆記的遷移。

## Further Notes

- 設計是在 `/grill-with-docs` 中逐題定案的，術語記錄在 repo 根目錄的 `GLOSSARY.md`。
- 「骨架固定、子章節照論文走」延續 commit `0d69c36`（固定內容章節）的方向，並解決它與「保留原標題階層」規則的衝突。
- 只有「介紹」與「結論」的子章節是固定的，原因是論文的 Introduction 與 Conclusion 通常本身沒有子章節。
