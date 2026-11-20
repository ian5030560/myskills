# 03: 展開合字

**What to build:** `text.md` 不再含拉丁合字字元（ﬁ、ﬂ 等），`speciﬁcally` 輸出為 `specifically`，AI 引用或搜尋原文時不會落空。其他字元（全形標點、上標等）不受影響。

**Blocked by:** 02

**Status:** done (uncommitted)

- [x] 測試先行：conftest 產生含 U+FB00–FB06 合字的 PDF，`text.md` 展開成對應字母序列，且不含任何這些字元
- [x] 非合字的特殊字元（全形標點、上標、CJK）輸出不變
- [x] 不改變 CLI、stdout 約定、`<!-- pN -->` 標記與無文字層標記
- [x] 重跑 bench，報告差值與翻轉題目；若有退步要說明原因
- [x] `tests/write_paper_notes/` 全部通過；cs.pdf、survey.pdf 擷取結果無異常

## Comments

Done. multi_column 620→648/841 (77.1%), long_tiny_text 221→224/262 (85.5%): 31 newly passing, 0 newly failing. cs.pdf and survey.pdf extract with no ligature code points left.
