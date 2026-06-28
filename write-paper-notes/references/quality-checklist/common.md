# Quality Checklist — Common

Check each item before final delivery. All must pass.

## Structure
- [ ] Title is present as `# <name>` at top of the document
- [ ] Original heading hierarchy preserved
- [ ] All content grouped under headings (no orphan text)
- [ ] Each `##` section begins with a concise introductory paragraph

## Content
- [ ] Key points formatted as bullet/numbered lists (not prose blocks)
- [ ] Comparative data organized in Markdown tables
- [ ] Tables included only when the paper references them
- [ ] No raw OCR text copied into notes.md
- [ ] Redundancy removed (related text merged)

## Images
- [ ] Images placed in correct subsection (not page-end grouped)
- [ ] Alt text is descriptive (no generic `Image` labels)
- [ ] All extracted images present in notes.md

## Architecture / Flow
- [ ] Original paper figure used when available
- [ ] Mermaid diagram only used when no architecture/flow figure exists

## Formatting
- [ ] Math expressions use LaTeX (`$...$` or `$$...$$`)
- [ ] Code uses Markdown code blocks or inline backticks

## Diagrams (Mermaid)
- [ ] Diagrams only generated when they add value (no simple flowchart duplication)
- [ ] Data tables kept as Markdown tables (not converted to Mermaid)
- [ ] Mermaid syntax is valid (correct type, matching braces/brackets)
- [ ] Diagram title present as bold heading above each block
- [ ] Labels are concise and accurate to the paper content
- [ ] Logic in diagram matches the paper description (no hallucinated flows)

## Final
- [ ] Content is restructured, not copied verbatim
- [ ] Element ordering follows content logic, not original page order
