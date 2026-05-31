# Style Guide for Organized Notes

## Structure
- Every `##` section MUST have a `### Summary` subsection at the top.
- Every `###` subsection MUST have a concise summary paragraph at the top.
- Group all content under the appropriate heading level. No orphan text outside sections.
- Preserve the original heading hierarchy from the paper.
- Paper-level `## Summary` must appear after the title.

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

## Summaries
- Every `##` section gets a `### Summary`.
- Every `###` subsection gets a summary paragraph.
- Summaries go ABOVE the section content, not below.

## Visualizations (Mermaid)

### When to generate
| Original content | Action |
|:---|:---|
| Simple flowchart image | Skip Mermaid — original image is sufficient |
| Complex architecture image | Generate high-level Mermaid `graph TD` for overview; keep original for detail |
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
