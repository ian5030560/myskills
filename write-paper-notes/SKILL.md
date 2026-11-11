---
name: write-paper-notes
version: 2.0.0
description: "Turn academic papers into organized Markdown notes. Supports PDF and DOCX."

metadata:
  starchild:
    emoji: "📄"
    skillKey: write-paper-notes
    requires:
      env: []
      bins: [python]
user-invocable: true
---

Turn a PDF or DOCX paper into study notes (`notes.md`) with a fixed skeleton. Run the three steps in order.

## Setup

```bash
pip install PyMuPDF python-docx
```

**Windows:** set `PYTHONIOENCODING=utf-8` in the *same* command as the script, since env vars don't persist across tool calls:

```powershell
$env:PYTHONIOENCODING="utf-8"; python scripts/extract.py --input <file> [--output-dir <dir>]
```

## Steps

### 1. Extract

```
python scripts/extract.py --input <file> [--output-dir <dir>]
```

- `--input` (required): a `.pdf` or `.docx` file.
- `--output-dir` (optional): parent directory, default the current directory.

The extracted text is printed to stdout; figures are written to `<output-dir>/<input-stem>/images/`.

### 2. Write

Read the extracted text and look at every image in `images/`. Then write `<output-dir>/<input-stem>/notes.md` (next to `images/`) using the skeleton and section mapping below, following every rule in `references/style-guide.md`.

Decide the notes language first: the language the user is talking to you in. If you can't tell (e.g. they only gave a file path), ask before writing.

### 3. Self-check

Check `notes.md` against every rule in `references/style-guide.md`. Fix each failure, then check again until every rule passes. Deliver `notes.md` to the user.

## Skeleton

The Chinese names are canonical; translate every heading into the notes language.

```
# <論文標題>
> 作者 · 年份 · 出處

## 介紹
### 背景
### 動機
### 研究問題
### 貢獻
## 相關研究
## 方法
## 結果
## 結論
### 主要發現
### 限制
### 未來方向
```

- The metadata line holds only what the paper states.
- 介紹 and 結論 always use the fixed subsections above.
- 相關研究, 方法 and 結果 take their subsections from the paper's own sections.
- A section or subsection with nothing from the paper to put in it is omitted entirely, heading included.

## Section mapping

Where each part of the paper goes:

| Paper section | Goes to |
|:---|:---|
| Abstract | Not written into the notes (read it for an overview) |
| Introduction | The four 介紹 subsections |
| Background / Preliminaries | 背景 |
| Related Work / Literature Review | 相關研究 |
| Method; for surveys, Research Methodology / Taxonomy / Key Approaches | 方法 |
| Experiments / Discussion / Analysis; for surveys, Comparison / Benchmark | 結果 |
| Conclusion | 主要發現 |
| Limitations / Threats to Validity | 限制 |
| Future Work / Open Challenges | 未來方向 |
| Appendix | Only when the main text cites it and it's needed to understand the method or results; merged into that section |
| References / Acknowledgments | Not included |
| Anything else | The closest section, as a subsection |
