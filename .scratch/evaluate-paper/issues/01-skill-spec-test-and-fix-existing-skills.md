# 01: 全 repo 的 skill 規格測試，並修正現有兩個 skill

**What to build:** 維護者執行一個測試，就能確認 repo 內每個 skill 資料夾都符合 Agent Skills 官方規格；新增或修改 skill 時違規會立刻被發現。現有的 `pdf/` 與 `write-paper-notes/` 一併修到符合規格，讓測試一開始就全綠。規格見 `.scratch/evaluate-paper/spec.md` 的 Implementation Decisions「skill 檔案測試泛用化與現有 skill 修正」；規則來源與測法見 `.scratch/evaluate-paper/research/agent-skills-spec.md`（最低硬性集合為 #1–#18 加 #22）。

**Blocked by:** None (can start immediately)

**Status:** done (uncommitted)

- [x] 一個涵蓋全 repo 的測試，對每個 skill 資料夾參數化；排除 `.agents/`、`.claude/` 與虛擬環境資料夾；舊的 `write-paper-notes` 專屬 skill 檔案測試刪除
- [x] 檢查：`SKILL.md` 存在；frontmatter 起訖與合法 YAML；只含 `name`、`description`、`license`、`compatibility`、`metadata`、`allowed-tools`
- [x] 檢查：`name` 必填、1–64 字元、僅小寫英數與連字號、首尾不為連字號、無連續連字號、與資料夾同名、不含 `anthropic` 或 `claude`
- [x] 檢查：`description` 必填、不超過 1024 字元、不含 XML 標籤；有 `compatibility` 時 1–500 字元；`metadata` 為字串對字串
- [x] 檢查：`SKILL.md` 少於 500 行；引用只有一層；引用的相對路徑都存在；`references/`、`scripts/`、`assets/` 內（不含 `__pycache__`）沒有未被引用的檔案
- [x] 負向案例：用臨時目錄產生的假 skill，證明每項檢查在違規時確實失敗；不測寫作品質
- [x] 以 PyYAML 解析 frontmatter；`CLAUDE.md` 的安裝指令加入 PyYAML
- [x] `pdf/` 與 `write-paper-notes/` 的 frontmatter 修到符合規格：`version` 移到 `metadata.version` 並改成字串；刪除 `user-invocable` 與 `starchild` 區塊；現有 description 不改寫
- [x] `.pylintrc` 的 `init-hook` 改為依檔案相對位置加入所有 skill 的 `scripts/`，不再寫死單一路徑
- [x] `CLAUDE.md` 的測試與 lint 指令反映新的測試位置與 `evaluate-paper`（lint 指令可先寫入，待該 skill 出現後生效）
- [x] 整套既有測試與 pylint 通過

## Comments

- 實作：`tests/test_skill_files.py`（43 個測試）。`check_skill()` 回傳違規清單；真實 skill 逐一參數化驗證通過，另用 `tmp_path` 假 skill 為每項檢查寫負向案例。整套 `tests/` 138 個通過。
- skill 發現規則：根目錄下、非隱藏、含 `SKILL.md` 的資料夾。`.agents/`、`.claude/` 是隱藏資料夾，`Lib/`、`Scripts/`、`Include/` 沒有 `SKILL.md`，不需要排除清單。
- 引用規則：`pdf/SKILL.md` 寫的是 repo 相對路徑（`pdf/scripts/x.py`），所以路徑 regex 允許 skill 自己的資料夾名當選用前綴；舊測試的 regex 其實抓不到這種寫法。另外也檢查 markdown 連結 `[x](FILE.md)` 是否指向存在的檔案。
- 孤兒規則取代舊的「只剩兩份 .md」測試：`references/`、`scripts/`、`assets/`（不含 `__pycache__`）內每個檔案都要被 `SKILL.md` 提到。
- `.pylintrc`：`init-hook` 內沒有 `__file__`，所以改成相對**工作目錄**取 `*/scripts`（`glob` 不含隱藏資料夾）；`CLAUDE.md` 已註明要從 repo 根目錄執行 lint。另外 `exec` 作用域下推導式看不到 `os`，改用 `map`。
- 用 venv 的 pylint（`Scripts/python.exe -m pylint`）驗證：`write-paper-notes` 10.00；`pdf` 9.96（既有的 R0801 重複程式碼警告，與本次無關）。
- `pdf` 的 `starchild.install`（tesseract-ocr）依 Q41 一併移除；系統相依仍寫在 `pdf/SKILL.md` 內文。
- 未處理：`CLAUDE.md` 的「Two independent skills」總覽等 `evaluate-paper` 出現後才有意義，留給 ticket 07。
