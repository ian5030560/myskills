# Style Guide

This guide defines how the AI must transform extracted PDF content into structured Markdown notes.

## Structural Framework

1. **Preserve structural hierarchy**: Keep the original heading structure intact and organize all synthesized content under its corresponding heading level (##, ###, ####).
2. **Align elements with context**: Rearrange text, lists, tables, and images based on content logic — not page layout. Move extracted images and tables from end-of-page grouping into the subsection they belong to.
3. **Improve image alt text**: Use the image analysis to replace generic `Image` alt text with a precise descriptive phrase (e.g., `![Transformer architecture]`).
4. **Use OCR as internal reference only**: Read OCR text to understand image content, but do NOT copy raw OCR output into `notes.md`.

## Content Synthesis

5. **Structure as compression pyramid**: For each section present content hierarchically:
   - **Summary**: A concise summary of the section ABOVE all content.
   - **Key points**: Main information extracted as bullet/numbered lists — never verbatim copies.
   - **Supporting data**: Embedded tables and detailed commentary following the key points.
6. **Remove redundancy**: Merge related text only; never remove images or structural elements.

## Structured Table Integration

7. **Align tables with their context**: Position each extracted table immediately after the paragraph that first references it (e.g., after "as shown in Table 1"). Do not group tables at the end of the document.
8. **Use extraction markers**: If the table extraction tool annotates tables with page or position markers, use them to locate the correct insertion point in the text.
9. **Tables are authoritative**: When text commentary and an extracted table describe the same data, keep the analytical writing but let the table carry the raw numbers. Replace basic textual "see Table X" references with the actual table block.
10. **Prefer extracted tables**: Do not reconstruct tables from plain text when a dedicated extraction tool already produced them. Insert the extracted table directly.

## Formatting Rules

11. **Math formulas**: Use LaTeX syntax for all mathematical expressions:
    - Inline: `$a^2 + b^2 = c^2$`
    - Display: `$$\dots$$`
12. **Code formatting**: Use Markdown code blocks for multi-line code and inline code (`` ` ``) for variables, function names, or short commands

## Visual Representations

### Mermaid Diagrams

13. **Mermaid diagrams**: Use Mermaid syntax to visually represent complex structures described in the paper:
    - **Architecture/Model**: `graph TD` (flowchart) for model pipelines and processing steps
    - **Relationships**: `classDiagram` for module hierarchies and relationships
    - **Process/Time**: `sequenceDiagram` for interactions, training loops, or data flow
14. **Trigger conditions**: Only generate diagrams when the paper explicitly describes:
    - A multi-step algorithm or pipeline (`graph TD`)
    - Component/module interactions (`classDiagram`)
    - A sequential protocol or interaction (`sequenceDiagram`)
15. **Accuracy rules**:
    - Nodes and labels must use terminology **directly from the paper**
    - Do NOT infer connections or modules that are not explicitly stated
    - Keep each diagram focused on a single concept (max 10-12 nodes)
    - Wrap diagrams in ```` ```mermaid ```` blocks

### Image vs. Diagram Policy

16. **Image first, diagram fallback**: The extracted image is the definitive source. Only generate a Mermaid diagram for concepts if:
    - No clear image exists for the described concept (text-only description in the paper)
    - Multiple fragmented images need to be synthesized into a single cohesive view
    - The original image is too complex and a simplified abstraction adds clarity
    If the diagram would simply replicate information already conveyed by an extracted image, omit the diagram entirely.
17. **Complementary use is allowed**: If the Mermaid diagram provides a *different* perspective (e.g., simplified overview vs. detailed schematic, or a sequence timeline vs. a static architecture), both may coexist.
