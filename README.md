# myskills

Personal skills collection. Built with [Star Child Skill Creator](https://skills.sh/starchild-ai-agent/official-skills/skill-creator).

## write-paper-notes

Extract content from PDF academic papers and generate structured Markdown notes. Default: OCR enabled for text-only AIs. Use `--no-ocr` for image-input AIs.

### Features

- Extracts text, images, and tables via `pymupdf4llm`
- Built-in OCR via Tesseract (for text-only AIs)
- AI reorganizes raw extraction into structured notes (`notes.md`)
- Preserves all images, restructures text into bullet points, lists, and tables
- Flexible element ordering (except fixed images)
- Lists only key references, skips peripheral citations

### Installation

```bash
npx skills add ian5030560/myskills --skill write-paper-notes
```
