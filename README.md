# myskills

OpenCode skill collection. Currently includes `write-paper-notes`.

## write-paper-notes

Extract content from PDF academic papers and generate structured Markdown notes.

### Features

- Extracts text, images, and tables via `pymupdf4llm`
- Built-in OCR via RapidOCR (for text-only AIs)
- AI reorganizes raw extraction into structured notes (`notes.md`)
- Preserves all images, restructures text into bullet points, lists, and tables
- Flexible element ordering (except fixed images)
- Lists only key references, skips peripheral citations
