# Style Guide

Follow every rule while writing `notes.md`. In the self-check step, this same list is the checklist: every rule must pass.

1. **No fabrication.** Write only what the paper contains; don't fill gaps from general knowledge. A section or subsection with nothing from the paper is omitted, heading included. No placeholders like "not mentioned".
2. **Language.** Write in the language the user is talking to you in; if unclear, ask first. In non-English notes, write a technical term as `譯名（English）` on first use, then use the English term. Names the paper itself coins (its method, components, benchmarks) stay in English with no translation.
3. **Bullets.** Put key points in bullet or numbered lists, not long prose. Restructure; don't copy the paper verbatim.
4. **Images.** Include only figures that carry content (skip logos, decorative lines, publisher marks). Place each in the subsection it illustrates, with alt text that says what it shows.
5. **Mermaid.** Draw a Mermaid diagram only when the paper describes a process in text alone and has no matching figure. Put a bold title above it.
6. **Tables.** Put comparative data in Markdown tables. Bold the best value only in columns where higher or lower is better (e.g. accuracy, success rate); columns or tables with no better/worse (counts, settings, frame numbers) get no bold.
7. **Math and code.** Math in LaTeX (`$...$` inline, `$$...$$` display). Code in fenced code blocks; variable and function names in inline backticks.
8. **Division of labour.**
   - 結果 holds the evidence: numbers, tables, analysis. 主要發現 holds one line per finding saying what it means; it may cite a key number once but never repeats tables or analysis.
   - 動機 is one or two sentences on why the work is needed; the paper-by-paper comparison belongs in 相關研究.
9. **研究問題.** If the paper doesn't list explicit research questions, rephrase its own problem statement ("this paper aims to…", "we address…"). If it has no problem statement either, omit the subsection.
10. **相關研究 comparison table.** Include a table with the columns 方法 / 核心概念 / 與本文差異 (translated into the notes language). Every cell must come from the paper; leave a cell empty when the paper doesn't say.
