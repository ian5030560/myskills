# Quality Checklist

Before saving the final `notes.md`, verify every item below. Fix any violations before presenting the result.

## Structure
- [ ] Every section from the original paper is represented
- [ ] Heading hierarchy is logical (## → ### → ####)
- [ ] Summaries appear ABOVE each section/subsection

## Images
- [ ] All extracted images are referenced in the notes
- [ ] Image alt text is descriptive (not generic "Image")
- [ ] Images are placed within the relevant subsection, not at page bottom

## Content
- [ ] LaTeX is used for all math formulas (inline `$...$` and display `$$...$$`)
- [ ] Code blocks are properly formatted (``` for multi-line, `` ` `` for inline)
- [ ] Tables are used for comparative/reference data only
- [ ] OCR text is NOT copied verbatim into the output
- [ ] Redundant/merged text does not repeat information
- [ ] Content is restructured (bullet points, lists), not copied verbatim

## Diagrams
- [ ] Mermaid syntax is correct and renders properly (valid ```` ```mermaid ```` blocks)
- [ ] Diagrams use terminology directly from the paper (no invented concepts)
- [ ] Each diagram is focused on a single concept (≤ 12 nodes)
- [ ] Diagrams are only present where they add clarity (no overuse)
- [ ] No Mermaid diagram duplicates the information of an extracted image (redundant diagrams are removed)
- [ ] When both a diagram and an image exist for the same concept, each provides a distinct perspective (complementary, not identical)

## Final
- [ ] File is named `notes.md`
- [ ] File is placed in the output directory
