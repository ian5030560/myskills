# Style Guide

This guide defines how the AI must transform extracted PDF content into structured Markdown notes.

## Core Principles

1. **Group content by heading levels**: Combine all paragraphs under the same heading (##, ###, ####)
2. **Preserve hierarchy**: Keep the original heading structure intact
3. **Insert images into appropriate sections**: Move `![Image](images/...)` references from page-end grouping into the subsection they belong to, based on OCR context and paper content
4. **Improve image alt text**: Use the image analysis to replace generic `Image` alt text with a precise descriptive phrase (e.g., `![Transformer architecture]`)
5. **OCR text is for AI reference only**: Read OCR text after each image to understand its content, but do NOT copy raw OCR output into notes.md

## Content Restructuring

6. **Restructure content, don't just copy**: Transform original content into structured notes:
   - Extract key points → present as bullet/numbered lists
   - Organize comparative data → use tables (only when referencing Table X)
   - **Flexible element ordering**: Rearrange text, lists, tables, and images based on content logic
7. **Add summaries**: Add concise summaries for each section (##) and subsection (###, ####) ABOVE the content
8. **Remove redundancy**: Merge related text only, never remove images

## Formatting Rules

9. **Math formulas**: Use LaTeX syntax for all mathematical expressions:
   - Inline: `$a^2 + b^2 = c^2$`
   - Display: `$$\dots$$`
10. **Code formatting**: Use Markdown code blocks for multi-line code and inline code (`` ` ``) for variables, function names, or short commands

## Diagram Synthesis

11. **Mermaid diagrams**: Use Mermaid syntax to visually represent complex structures described in the paper:
    - **Architecture/Model**: `graph TD` (flowchart) for model pipelines and processing steps
    - **Relationships**: `classDiagram` for module hierarchies and relationships
    - **Process/Time**: `sequenceDiagram` for interactions, training loops, or data flow
12. **Trigger conditions**: Only generate diagrams when the paper explicitly describes:
    - A multi-step algorithm or pipeline (`graph TD`)
    - Component/module interactions (`classDiagram`)
    - A sequential protocol or interaction (`sequenceDiagram`)
13. **Accuracy rules**:
    - Nodes and labels must use terminology **directly from the paper**
    - Do NOT infer connections or modules that are not explicitly stated
    - Keep each diagram focused on a single concept (max 10-12 nodes)
    - Wrap diagrams in ```` ```mermaid ```` blocks
