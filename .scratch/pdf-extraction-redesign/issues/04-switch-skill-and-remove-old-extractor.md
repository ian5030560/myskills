# 04: 切換 skill 到新流程並移除舊擷取程式

**What to build:** write-paper-notes 改用 01–03 的三個腳本，SKILL.md 變成四步驟（擷取、撰寫、自我檢查、清理），只接受 PDF；舊的擷取入口、基底類別、PDF/DOCX 擷取模組、DOCX 相依與測試全部移除，文件同步更新，版本 3.0.0。規格見 spec 的「SKILL.md」「Setup and metadata」「Removals」。

**Blocked by:** 01、02、03

**Status:** ready-for-agent

- [ ] SKILL.md 步驟 1：執行文字擷取與頁面渲染兩個腳本
- [ ] SKILL.md 步驟 2：讀 `text.md`；依章節編號推斷標題層級；無文字層的頁面讀頁面圖；`Table N` 看頁面圖重建成 Markdown、不裁切；要放的圖在頁面圖上寬鬆框選後用裁切腳本，裁完檢查圖的四邊是否完整，不完整就放大重裁；只開需要的頁面圖
- [ ] SKILL.md 步驟 3：自我檢查不變
- [ ] SKILL.md 步驟 4：交付 `notes.md` 後只刪除 `text.md` 與 `pages/`，最後只剩 `images/` 與 `notes.md`
- [ ] Setup 只剩 `pip install PyMuPDF`，註明 DOCX 與其他格式需先另存成 PDF；description 改為只支援 PDF；version 3.0.0
- [ ] 移除現行擷取入口、基底類別、PDF 與 DOCX 擷取模組、`python-docx` 相依、DOCX fixture 與測試、舊擷取器的單元測試
- [ ] `test_skill_files.py` 對應新腳本名稱仍通過；skill 內 `.md` 仍只有 SKILL.md 與 style guide
- [ ] `.pylintrc` 的 init-hook 若只為舊模組服務則移除或調整
- [ ] README.md 與 CLAUDE.md 中關於 DOCX 與舊擷取流程的描述更新；`.gitignore` 保留 `*.docx`
- [ ] 筆記骨架、章節對應、`references/style-guide.md` 不變
- [ ] `pytest tests/write_paper_notes/` 與 `pytest tests/pdf/` 全數通過，兩個 skill 的 pylint 通過
