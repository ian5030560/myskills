# 05: 標準檢查表：AMSTAR 2、CASP、MMAT 與選擇規則

**What to build:** 判讀時 AI 依論文的研究設計挑選對應的標準檢查表，逐題回答並附原文位置，外部評估因此有標準工具可依循。研究設計不符任何檢查表時，報告明說並只做內容判斷。規格見 `.scratch/evaluate-paper/spec.md` 的 Implementation Decisions「判讀流程」「授權」；授權、題目結構與評等方法見 `.scratch/evaluate-paper/research/appraisal-tools-and-metrics-apis.md`。

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] 選擇規則檔：依研究設計對應 CASP（依設計分冊）、AMSTAR 2（系統性回顧）、MMAT（混合方法等）；不符任何檢查表時的處理
- [ ] AMSTAR 2 題目檔：回答為 Yes／Partial Yes／No，依 7 個關鍵領域（第 2、4、7、9、11、13、15 題）決定整體信心 High／Moderate／Low／Critically low；註明 BMJ 論文出處與 CC BY 4.0
- [ ] CASP 題目檔：檔案開頭單獨標示 CC BY-NC-SA 4.0 授權聲明與出處
- [ ] MMAT 題目檔：只用改寫並註明出處，不轉載原文
- [ ] 三者都不把題項加總成分數；報告中檢查表的每一題都有回答與原文位置，資訊不足寫「無法判斷」
- [ ] 04 中「待檢查表」的註記被替換為實際檢查表流程；報告格式規則與自我檢查涵蓋檢查表部分
- [ ] 全 repo 的 skill 規格測試通過（所有新檔案都被 `SKILL.md` 直接引用）
- [ ] 對一篇真實論文跑一次，確認檢查表被正確挑選與填寫，觀察記錄在本 ticket 的 Comments
