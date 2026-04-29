---
name: write-paper-notes
version: 2.0.0
description: "Extract content from PDF papers and generate structured Markdown notes. Use when user provides a PDF paper and wants to generate notes, summaries, or extract images/tables."

metadata:
  starchild:
    emoji: "📄"
    skillKey: write-paper-notes
    requires:
      env: []
      bins: [python]
    install:
      - kind: pip
        package: pypdf
      - kind: pip
        package: pypdf-table-extraction

user-invocable: true
---

Extract text, images, and tables from PDF academic papers and generate structured Markdown notes.

## Processing Flow

| Step | Action |
|------|--------|
| 0 | Install dependencies: `pip install pypdf pypdf-table-extraction` |
| 1 | Run `python scripts/extract.py --pdf <pdf> --output-dir <dir>` (output to stdout) |
| 2 | AI organizes content by sections and subsections |
| 3 | Run `python scripts/save_notes.py --content "<AI_output>" --output-dir <dir>` |
| 4 | Notes saved to `notes.md` in the same directory as images |

## Heading Level Detection

| Pattern | Level | Example |
|---------|-------|---------|
| `I.`, `1.` + text | 2 | "1. Introduction" |
| `1.1.` + text | 3 | "1.1. Methodology" |
| `1.1.1.` + text | 4 | "1.1.1. Data Collection" |
| `a.`, `(1)` + text | 4 | "a. First item" |
| No pattern detected | 4 | Regular paragraph |

## AI Organization Guidelines

When AI processes the extracted Markdown output, it must:

1. **Group content by heading levels**: Combine all paragraphs under the same heading (##, ###, ####)
2. **Preserve hierarchy**: Keep the original heading structure intact
3. **Summarize each section**: Provide a concise summary for each section (##) and subsection (###, ####)
4. **Link figures/tables**: When referencing Figure X or Table X, include the image or table content
5. **Remove redundancy**: Merge related content and eliminate duplicate information

## Output Format (stdout)

```markdown
--- Page 1 ---

## 章节标题（层级2）

### 子章节标题（层级3）

正文内容...

![Figure 1](images/figure_1_1.png)

**Table 1: 表格标题**
| Column 1 | Column 2 |
|----------|----------|
| ...      | ...      |

--- Page 2 ---

...
```

## Script Usage

### Install Dependencies

```bash
pip install pypdf pypdf-table-extraction
```

### Run Extraction

```bash
python scripts/extract.py --pdf <pdf_path> --output-dir <output_dir>
```

Required parameters:
- `--pdf`: PDF file path
- `--output-dir` (optional): Output directory (default: uses PDF filename)

Outputs:
- Markdown content to stdout (redirect to file)
- `images/` - Image folder with extracted figures

### Save AI-Organized Notes

```bash
python scripts/save_notes.py --content "<AI_organized_markdown>" --output-dir <output_dir>
```

Required parameters:
- `--content`: AI-organized notes content in Markdown format
- `--output-dir`: Output directory

Output:
- `notes.md` - Final structured notes (saved in the same directory as images)