# Style Guide — CS/AI/ML Papers

## Method Section
- Divide into numbered subsections: `### 3.1`, `### 3.2`, `### 3.3`, `### 3.4`.
- `### 3.2 Model Architecture`: insert the original paper's architecture figure first. Only use a Mermaid diagram if no architecture figure exists in the paper.
- Mathematical formulas: `$$...$$` display LaTeX.
- Include pseudocode for the core algorithm.
- Implementation details in a Parameter/Value table.

## Experiments Section
- Divide into: `### 4.1 Setup`, `### 4.2 Main Results`, `### 4.3 Ablation Studies`.
- Main results in a Markdown table. **Bold** the best result per column.
- Include `### 4.4 Qualitative Analysis` when visual results exist.

## Related Work
- Use a comparison table with at least Approach / Core Idea / Limitation columns.
- 3-5 rows; focus on the most relevant prior works.

## Conclusion
- Cover key findings, limitations, and future work.
