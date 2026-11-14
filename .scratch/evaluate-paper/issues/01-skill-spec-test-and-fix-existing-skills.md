# 01: 全 repo 的 skill 規格測試，並修正現有兩個 skill

**What to build:** 維護者執行一個測試，就能確認 repo 內每個 skill 資料夾都符合 Agent Skills 官方規格；新增或修改 skill 時違規會立刻被發現。現有的 `pdf/` 與 `write-paper-notes/` 一併修到符合規格，讓測試一開始就全綠。規格見 `.scratch/evaluate-paper/spec.md` 的 Implementation Decisions「skill 檔案測試泛用化與現有 skill 修正」；規則來源與測法見 `.scratch/evaluate-paper/research/agent-skills-spec.md`（最低硬性集合為 #1–#18 加 #22）。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 一個涵蓋全 repo 的測試，對每個 skill 資料夾參數化；排除 `.agents/`、`.claude/` 與虛擬環境資料夾；舊的 `write-paper-notes` 專屬 skill 檔案測試刪除
- [ ] 檢查：`SKILL.md` 存在；frontmatter 起訖與合法 YAML；只含 `name`、`description`、`license`、`compatibility`、`metadata`、`allowed-tools`
- [ ] 檢查：`name` 必填、1–64 字元、僅小寫英數與連字號、首尾不為連字號、無連續連字號、與資料夾同名、不含 `anthropic` 或 `claude`
- [ ] 檢查：`description` 必填、不超過 1024 字元、不含 XML 標籤；有 `compatibility` 時 1–500 字元；`metadata` 為字串對字串
- [ ] 檢查：`SKILL.md` 少於 500 行；引用只有一層；引用的相對路徑都存在；`references/`、`scripts/`、`assets/` 內（不含 `__pycache__`）沒有未被引用的檔案
- [ ] 負向案例：用臨時目錄產生的假 skill，證明每項檢查在違規時確實失敗；不測寫作品質
- [ ] 以 PyYAML 解析 frontmatter；`CLAUDE.md` 的安裝指令加入 PyYAML
- [ ] `pdf/` 與 `write-paper-notes/` 的 frontmatter 修到符合規格：`version` 移到 `metadata.version` 並改成字串；刪除 `user-invocable` 與 `starchild` 區塊；現有 description 不改寫
- [ ] `.pylintrc` 的 `init-hook` 改為依檔案相對位置加入所有 skill 的 `scripts/`，不再寫死單一路徑
- [ ] `CLAUDE.md` 的測試與 lint 指令反映新的測試位置與 `evaluate-paper`（lint 指令可先寫入，待該 skill 出現後生效）
- [ ] 整套既有測試與 pylint 通過
