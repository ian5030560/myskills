# Style Guide — Common Rules

## Structure
- Group all content under the appropriate heading level. No orphan text outside sections.
- Preserve the original heading hierarchy from the paper.
- Begin each `##` section with a concise introductory paragraph.

## Content Transformation
- Restructure: extract key points into bullet/numbered lists (not prose paragraphs).
- Comparative data: organize into Markdown tables — only when the paper references that table.
- Insert images into the subsection they belong to (do not keep page-end grouping).
- Improve image alt text: replace generic `Image` with a precise descriptive phrase.
- Flexible ordering: rearrange text, lists, tables, and images based on content logic, not original page order.

## OCR Rules
- OCR text is for AI reference only. Read it to understand image content.
- Do NOT copy raw OCR output into `notes.md`.

## Formatting
- Math formulas: use LaTeX (`$...$` inline, `$$...$$` display).
- Code: Markdown code blocks for multi-line code; backticks (`` ` ``) for variables, function names, or short commands.
- Remove redundancy: merge related text, but never remove images.

## Architecture / Flow Diagrams
- **Priority 1:** Use the original figure from the paper (`images/filename.png`).
- **Priority 2:** Only generate a Mermaid diagram if the paper has NO architecture or flow figure.
- Mermaid diagrams must be fenced with ```` ```mermaid ````.

## Visualizations (Mermaid)

### When to generate
| Original content | Action |
|:---|:---|
| Simple flowchart image | Skip Mermaid — original image is sufficient |
| Text-only logic/process | Generate Mermaid to visualize the implicit flow |
| Data table (parameters, metrics) | Keep Markdown table — do NOT convert to Mermaid |
| Classification / hierarchy table | Transform to `mindmap` |
| State / logic transition table | Transform to `stateDiagram` |
| Timeline / milestone table | Transform to `timeline` |

### Syntax rules
- Wrap all diagrams inside a fenced code block with `mermaid` language tag.
- Use descriptive titles above each diagram as a bold heading.
- Keep node labels concise (1-5 words). Prefer `graph TD` (top-down) for most processes.
- Ensure the diagram represents a clear logical relationship — do not generate decorative diagrams.
- Reference: https://mermaid.js.org/syntax/
