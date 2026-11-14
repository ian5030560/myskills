# Agent Skills 官方規格研究（供通用 skill 驗證測試使用）

調查日期：2026-11-13。只採用一手來源：

- [S] Agent Skills Specification：https://agentskills.io/specification
- [O] Anthropic Agent Skills overview：https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- [B] Anthropic Skill authoring best practices：https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- [CC] Claude Code Skills 文件：https://code.claude.com/docs/en/skills
- [V] 官方參考驗證器 `skills-ref` 原始碼（spec 頁面 Validation 段落連結過去的 repo）：
  - https://github.com/agentskills/agentskills/tree/main/skills-ref
  - https://raw.githubusercontent.com/agentskills/agentskills/main/skills-ref/src/skills_ref/validator.py
  - https://raw.githubusercontent.com/agentskills/agentskills/main/skills-ref/src/skills_ref/parser.py
  - https://raw.githubusercontent.com/agentskills/agentskills/main/skills-ref/pyproject.toml

標示「unconfirmed」的項目是推論或沒有實際執行驗證。

---

## 1. 可機械化測試的規則清單（摘要）

「硬性」＝規格或驗證器會判定失敗；「建議」＝best practice，可做成 warning 或嚴格模式。

| # | 規則 | 等級 | 來源 | 測試方式 |
|---|------|------|------|----------|
| 1 | skill 目錄裡必須有 `SKILL.md` | 硬性 | [S] Directory structure；[V] `"Missing required file: SKILL.md"` | `(skill_dir / "SKILL.md").is_file()`。註：[V] 的 parser 也接受小寫 `skill.md`，但規格寫的是 `SKILL.md`，建議只認大寫 |
| 2 | 檔案開頭是 `---`，frontmatter 用 `---` 收尾 | 硬性 | [S] "must contain YAML frontmatter followed by Markdown content"；[V] parser 錯誤訊息 "SKILL.md must start with YAML frontmatter (---)" / "...not properly closed with ---"；[CC] "Frontmatter is read only when the opening `---` is the file's first line" | 第一行等於 `---`，而且後面還有另一行 `---` |
| 3 | frontmatter 是合法的 YAML mapping | 硬性 | [S]；[V] 用 `strictyaml.load` | `yaml.safe_load` 回傳 dict（若想跟 [V] 完全一致，就改用 strictyaml，見 §4） |
| 4 | 只能有這些欄位：`name`、`description`、`license`、`compatibility`、`metadata`、`allowed-tools` | 硬性（依 [V] 與 API／claude.ai） | [S] 欄位表；[V] `"Unexpected fields in frontmatter: ..."`；[CC]：claude.ai 上傳、Skills API 只接受這六個欄位，其他欄位會直接報錯 "Unexpected key(s) in SKILL.md frontmatter" | `set(fm) - ALLOWED == set()` |
| 5 | `name` 必填，而且是非空字串 | 硬性 | [S]、[O]、[V] | `isinstance(fm["name"], str) and fm["name"].strip()` |
| 6 | `name` 長度 1–64 | 硬性 | [S] "Must be 1-64 characters"；[O] "Maximum 64 characters" | `1 <= len(name) <= 64` |
| 7 | `name` 只能用小寫英數字和 `-` | 硬性 | [S]；[O] | `re.fullmatch(r"[a-z0-9-]+", name)`（[S] 的措詞是 "unicode lowercase alphanumeric"，[V] 也允許 Unicode 小寫字母；[O] 說的是 "lowercase letters, numbers, and hyphens"，用 ASCII 最保守） |
| 8 | `name` 開頭和結尾都不能是 `-` | 硬性 | [S]；[V] | `not name.startswith("-") and not name.endswith("-")` |
| 9 | `name` 不能有連續的 `--` | 硬性 | [S]；[V] | `"--" not in name` |
| 10 | `name` 要和上層目錄名稱一樣 | 硬性 | [S] "Must match the parent directory name"；[V] `"Directory name '...' must match skill name '...'"` | `name == skill_dir.name`（[V] 會先對兩邊做 NFKC） |
| 11 | `name` 不能含保留字 `anthropic`、`claude` | 硬性（Anthropic 平台） | [O]、[B] "Cannot contain reserved words: `anthropic`, `claude`" | `"anthropic" not in name and "claude" not in name`（[V] 不檢查這條） |
| 12 | `name` 不能含 XML tag | 硬性（Anthropic 平台） | [O]、[B] "Cannot contain XML tags" | `not re.search(r"<[^>]+>", name)`（只要 #7 通過，這條就自動成立） |
| 13 | `description` 必填，而且是非空字串 | 硬性 | [S]、[O]、[V] | `isinstance(desc, str) and desc.strip()` |
| 14 | `description` 長度 ≤ 1024 字元 | 硬性 | [S] "Must be 1-1024 characters"；[O] "Maximum 1,024 characters" | `len(desc) <= 1024` |
| 15 | `description` 不能含 XML tag | 硬性（Anthropic 平台） | [O]、[B] | `not re.search(r"<[^>]+>", desc)`（[V] 不檢查這條） |
| 16 | 有 `compatibility` 時，必須是 1–500 字元的字串 | 硬性 | [S]；[V] | `isinstance(c, str) and 1 <= len(c) <= 500` |
| 17 | `metadata` 是 string key 對 string value 的 map | 硬性（依規格措詞） | [S] "A map from string keys to string values" | `isinstance(m, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in m.items())`。注意：[V] 不會因為巢狀 map 報錯（它會把值 `str()` 化），但規格寫的是 string→string |
| 18 | 有 `allowed-tools` 時是以空白分隔的字串 | 硬性（規格） | [S] "A space-separated string"（Experimental） | `isinstance(v, str)`；[V] 不檢查型別。[CC] 另外接受 YAML list，但那是 Claude Code 的擴充 |
| 19 | 有 `license` 時建議簡短 | 建議 | [S] "We recommend keeping it short" | 可省略，或檢查是 `str` |
| 20 | `SKILL.md` 少於 500 行 | 建議 | [S] "Keep your main `SKILL.md` under 500 lines"；[B] "Keep the `SKILL.md` body under 500 lines"；[CC] 同樣寫法 | `len(body.splitlines()) < 500`（[S]、[CC] 說的是整個檔案，[B] 說的是 body；直接用整個檔案行數最保守） |
| 21 | `SKILL.md` body 建議少於 5000 tokens | 建議 | [S] "< 5000 tokens recommended"；[O] "Under 5k tokens" | 沒有官方 tokenizer，只能粗估（例如字元數 / 4 < 5000）——近似值，unconfirmed |
| 22 | `SKILL.md` 裡引用的 skill 內相對路徑都要存在 | 由規則推得 | [S] File references "use relative paths from the skill root" | 沿用 `test_skill_files.py` 的 regex，抽出 `scripts/…`、`references/…`、`assets/…` 等路徑後檢查存在（規格沒有明文要求「必須存在」，但引用斷掉的檔案就沒有意義） |
| 23 | 檔案引用從 `SKILL.md` 算起只能一層深（reference 檔不要再引用其他 reference 檔） | 建議 | [S] "Keep file references one level deep from `SKILL.md`"；[B] "Keep references one level deep from SKILL.md" | 對 `SKILL.md` 引用到的每個 `.md`，檢查裡面沒有再引用 skill 內其他 `.md` |
| 24 | 路徑一律用 `/`，不用 `\` | 建議 | [B] "Avoid Windows-style paths ... Always use forward slashes" | 在 `SKILL.md` 與 reference `.md` 搜尋 `scripts\`、`references\` 這類反斜線路徑 |
| 25 | 超過 100 行的 reference 檔，開頭要有目錄 | 建議 | [B] "For reference files longer than 100 lines, include a table of contents at the top" | 行數 > 100 時，前 N 行要有 `Contents` 標題或清單——判斷方式是啟發式的，unconfirmed |
| 26 | `description` 要寫「做什麼」和「何時使用」，並用第三人稱 | 建議（語意） | [S]、[O]、[B] "Always write in third person" | 只能做弱啟發：例如檢查有沒有 "Use when"／"when"，開頭不是 "I "／"You "。容易誤判，建議只當 warning |
| 27 | 選用目錄名稱慣例：`scripts/`、`references/`、`assets/` | 慣例（非強制） | [S] "A skill directory may contain any files and directories beyond the required `SKILL.md`" | 不建議做成硬性測試；規格明說可以放任何檔案 |

最小可行的通用 pytest：#1–#18（硬性）＋ #22。#20、#23、#24 成本很低，也值得加。#21、#25、#26 建議做成 `warnings.warn` 或預設 skip。

---

## 2. Frontmatter 細節

### 欄位表（[S]）

| 欄位 | 必填 | 限制 |
|------|------|------|
| `name` | 是 | 1–64 字元；只能用小寫英數字和 `-`；不能以 `-` 開頭或結尾；不能有 `--`；要和上層目錄名稱相同 |
| `description` | 是 | 1–1024 字元；非空；要寫做什麼和何時使用；最好包含關鍵字 |
| `license` | 否 | license 名稱，或附帶的 license 檔名；建議簡短 |
| `compatibility` | 否 | 1–500 字元；只在有環境需求時才加（"Most skills do not need the `compatibility` field."） |
| `metadata` | 否 | "A map from string keys to string values"；給 client 放規格沒定義的屬性；key 名稱最好取得夠獨特，避免衝突 |
| `allowed-tools` | 否 | 以空白分隔的字串；Experimental，各家 agent 支援程度不同 |

來源：https://agentskills.io/specification

### Anthropic 額外的限制（[O]、[B]）

- `name`：最多 64 字元、只能用小寫英數字和 `-`、**不能含 XML tag**、**不能含保留字 `anthropic`、`claude`**。
- `description`：非空、最多 1,024 字元、**不能含 XML tag**；"must include both what the Skill does and when Claude should use it"。
- [B]：description "Always write in third person"；name 建議用動名詞形式（如 `processing-pdfs`），名詞片語（如 `pdf-processing`）或動作導向（如 `process-pdfs`）也可以接受；避免 `helper`、`utils` 這類模糊名稱。

來源：https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure 、https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

### 規格以外的欄位可以用嗎？

- **agentskills.io 規格本身**：欄位表只列了六個欄位，規格沒有明文寫「禁止其他欄位」，但 `metadata` 的說明是 "Clients can use this to store additional properties not defined by the Agent Skills spec"，意思是額外屬性應該放進 `metadata`。（"禁止"沒有明文寫出 — 依措詞推論）
- **官方驗證器 [V]**：`ALLOWED_FIELDS = {name, description, license, allowed-tools, metadata, compatibility}`，其他欄位都會報 `"Unexpected fields in frontmatter: ... Only [...] are allowed."` → **算不合規**。
- **Claude Code [CC]**：額外支援 `when_to_use`、`argument-hint`、`arguments`、`disable-model-invocation`、`user-invocable`、`allowed-tools`、`disallowed-tools`、`model`、`effort`、`context`、`agent`、`background`、`hooks`、`paths`、`shell`；未知欄位會被靜默忽略。`name` 在 Claude Code 裡可以省略（預設用目錄名稱）。description＋when_to_use 在清單中會被截斷在 1,536 字元。**`version` 不是 Claude Code 的欄位。**
- **claude.ai 上傳／Skills API**（[CC] 的說法）：只接受上面六個欄位，其他欄位會直接報錯。

結論：如果目標是「符合官方規格、可以跨平台分發」（本 repo 透過 `npx skills add` 分發），就應該只允許這六個欄位；`user-invocable` 這類 Claude Code 專屬欄位會讓 `skills-ref validate` 失敗，也無法上傳到 claude.ai／API。

---

## 3. 目錄結構細節

（來源：https://agentskills.io/specification ，除非另外註明）

```
skill-name/
├── SKILL.md          # 必要
├── scripts/          # 選用：可執行程式碼
├── references/       # 選用：文件
├── assets/           # 選用：模板與資源
└── ...               # 任何其他檔案或目錄
```

- `scripts/`：agent 可以執行的程式碼；要能獨立執行，或清楚寫出相依套件；要有有用的錯誤訊息；要能處理邊界情況。支援哪些語言取決於 agent 實作（常見的是 Python、Bash、JavaScript）。
- `references/`：需要時才讀的文件（如 `REFERENCE.md`、`FORMS.md`、領域專屬檔案）；每個檔案都要聚焦，因為「smaller files mean less use of context」。
- `assets/`：靜態資源（模板、圖片、資料檔、schema）。
- 這些都只是建議慣例："A skill directory may contain any files and directories beyond the required `SKILL.md`."
- 漸進式揭露：metadata 約 100 tokens；instructions 建議少於 5000 tokens；resources 需要時才載入。"Keep your main `SKILL.md` under 500 lines."（[S]；[O] 的表格寫 "Under 5k tokens"）
- 檔案引用："use relative paths from the skill root"；"Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains."（[S]）
- [B] 補充：路徑用 `/`；超過 100 行的 reference 檔開頭要有目錄；檔名要能看出內容（如 `form_validation_rules.md`，不要用 `doc2.md`）；要講清楚 script 是「執行」還是「當參考讀」。
- 注意：[B] 的範例有把 `FORMS.md` 直接放在 skill 根目錄、也有用 `reference/`（單數）的，可見目錄名稱不是強制的。

---

## 4. 官方驗證器 `skills-ref`

- 出處：規格頁的 Validation 段落 —— "Use the skills-ref reference library to validate your skills: `skills-ref validate ./my-skill`. This checks that your `SKILL.md` frontmatter is valid and follows all naming conventions."（https://agentskills.io/specification#validation）
- Repo：https://github.com/agentskills/agentskills/tree/main/skills-ref 。README 聲明：「This library is intended for demonstration purposes only. It is not meant to be used in production.」
- 套件：`skills-ref` 0.1.0，Python >= 3.11，相依套件 `click>=8.0`、`strictyaml>=1.7.3`，CLI 進入點 `skills-ref = skills_ref.cli:main`（pyproject.toml）。
- 安裝：README 寫的是 clone 後執行 `pip install -e .` 或 `uv sync`（Windows 用 `.venv\Scripts\Activate.ps1`）。**有沒有發布到 PyPI：unconfirmed**（README 沒提到）。也可以用 `pip install "git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref"`，這是標準 pip 語法，但沒有實測，unconfirmed。
- CLI：`skills-ref validate <dir>`、`skills-ref read-properties <dir>`（輸出 JSON）、`skills-ref to-prompt <dirs...>`（產生 `<available_skills>` XML）。
- Python API：`from skills_ref import validate, read_properties, to_prompt`；`validate(Path)` 回傳錯誤字串的 list，空 list 代表合法。

### 驗證器會檢查的項目（validator.py / parser.py）

- 路徑存在而且是目錄；找得到 `SKILL.md`（也接受 `skill.md`）。
- frontmatter 以 `---` 開頭與收尾，用 **strictyaml** 解析。
- 只允許六個欄位，其他欄位會報 `Unexpected fields in frontmatter`。
- `name`：必填、非空字串、≤ 64、做 NFKC 後要是小寫、只能用字母數字和 `-`、不能以 `-` 開頭或結尾、不能有 `--`、要和目錄名稱（NFKC 後）相同。
- `description`：必填、非空字串、≤ 1024。
- `compatibility`：字串、≤ 500。
- **不檢查**：保留字 `anthropic`／`claude`、XML tag、`metadata` 的值是不是字串（parser 會把值 `str()` 化）、`allowed-tools` 型別、`license`、body 長度、檔案引用。

### 可以從 pytest 呼叫，或自己重寫嗎？

- 可以呼叫：`pytest.importorskip("skills_ref")` 之後 `assert validate(skill_dir) == []`；或用 subprocess 跑 `skills-ref validate`。缺點是要多裝 `click` + `strictyaml`、要 Python ≥ 3.11、作者自己也說這是 demo 用途。
- **建議自己重寫**：邏輯不到百行，而且需要補上 Anthropic 平台的額外規則（保留字、XML tag、metadata 必須 string→string）。用 PyYAML（`yaml.safe_load`）就夠了；本 repo venv 裡有沒有 PyYAML 要另外確認（unconfirmed）。
- 差異提醒：strictyaml 預設不接受 flow style（`[a, b]`、`{a: b}`）。所以 frontmatter 裡的 `bins: [python]` 在 `skills-ref` 下很可能直接解析失敗；用 PyYAML 則能通過。這是依 strictyaml 的預設行為推論，**unconfirmed，沒有實際執行**。如果自己重寫，可以加一條「frontmatter 不得用 flow style」來對齊。

---

## 5. 現有兩個 skill 是否符合

### `pdf/SKILL.md`

```yaml
name: pdf
version: 2.0.0
description: "Complete PDF lifecycle toolkit: ... All powered by PyMuPDF."   # 149 字元
metadata:
  starchild:
    emoji: "📄"
    skillKey: pdf
    requires: { env: [], bins: [python] }      # 實際是 block style
    install: [ {kind: system, package: tesseract-ocr} ]
user-invocable: true
```

| 規則 | 結果 | 說明 |
|------|------|------|
| name 格式／長度／與目錄相同 | 通過 | `pdf` == 目錄 `pdf` |
| 保留字、XML | 通過 | |
| description 長度 ≤ 1024、非空、無 XML | 通過 | 149 字元 |
| **只能有六個欄位** | **失敗** | `version`、`user-invocable` 不在允許清單內 → [V] 會報 `Unexpected fields in frontmatter: user-invocable, version`；claude.ai／API 上傳也會報錯（[CC]） |
| **metadata 是 string→string** | **失敗** | `metadata.starchild` 是巢狀 map（裡面還有 list） |
| strictyaml 解析 | 很可能失敗（unconfirmed） | `env: []`、`bins: [python]` 是 flow style |
| SKILL.md < 500 行 | 通過 | 整個檔案 240 行（body 約 223 行） |
| body < 5000 tokens | 大概通過（unconfirmed） | body 約 8.1k 字元，粗估 2k tokens |
| 引用的路徑都存在 | 通過 | 只引用 `scripts/pdf_*.py`，五個都存在 |
| 反斜線路徑 | 通過 | 沒找到 |
| description 寫出「何時使用」 | 建議未達成 | 只寫了做什麼，沒有 "Use when …" 之類的觸發語句（[B]） |

### `write-paper-notes/SKILL.md`

```yaml
name: write-paper-notes
version: 3.0.0
description: "Turn academic papers (PDF) into organized Markdown notes."   # 57 字元
metadata:
  starchild: { emoji, skillKey, requires: { env: [], bins: [python] } }
user-invocable: true
```

| 規則 | 結果 | 說明 |
|------|------|------|
| name 格式／長度／與目錄相同 | 通過 | |
| 保留字、XML | 通過 | |
| description 長度、非空、無 XML | 通過 | 57 字元 |
| **只能有六個欄位** | **失敗** | `version`、`user-invocable` |
| **metadata 是 string→string** | **失敗** | `metadata.starchild` 是巢狀結構 |
| strictyaml 解析 | 很可能失敗（unconfirmed） | `env: []`、`bins: [python]` 是 flow style |
| SKILL.md < 500 行 | 通過 | 119 行 |
| 引用的路徑都存在 | 通過 | `references/style-guide.md`、`scripts/{crop_figure,extract_text,render_pages}.py` |
| 只有一層深的引用 | 通過 | `references/style-guide.md`（16 行）沒有再引用 skill 內其他檔案 |
| 反斜線路徑 | 通過 | |
| description 寫出「何時使用」 | 建議未達成 | 沒有觸發語句；內容也偏短，可以補關鍵字 |
| 額外雜物 | 注意 | `scripts/__pycache__/` 存在於工作目錄（應已被 gitignore；通用測試若掃描整個目錄，要記得排除它） |

### 符合規格的修正方向（兩個 skill 都適用）

1. 刪掉頂層的 `version`、`user-invocable`。`user-invocable` 預設就是 `true`（[CC]），刪掉不影響 Claude Code 的行為。版本號如果要保留，可以照規格範例改成 `metadata: { version: "2.0.0" }`（[S] 的範例就是 `metadata.version: "1.0"`）。
2. `metadata.starchild` 的巢狀結構不符合 string→string：攤平成字串值（如 `starchild-emoji: "📄"`），或整個拿掉。tesseract 這類系統需求，規格建議放進 `compatibility`（如 `compatibility: Requires Python and the tesseract-ocr system binary`）。
3. description 補上 "Use when …"，並維持第三人稱。
