Status: ready-for-agent

# write-paper-notes：以頁面圖重新設計 PDF 擷取

相關文件：`GLOSSARY.md`（頁面圖、裁切圖）、`docs/adr/0001-pdf-only-ai-cropped-figures.md`。取代 `.scratch/pdf-extraction-fixes/` 的問題清單。測試論文在 `test-papers/`（gitignored），文件中只能用 `cs.pdf` / `survey.pdf` 稱呼。

## Problem Statement

使用者用 write-paper-notes 把論文轉成筆記時，擷取步驟產出的素材品質很差，AI 只能拿殘缺的素材寫筆記：

- 圖被切成碎片（一張折線圖被切成 24 塊），有的是全黑遮罩圖，每頁還多一張只有頁碼和浮水印的假圖；向量圖、點陣加向量的混合圖常常抓不完整。
- 標題偵測失效，整篇只偵測到一個 `#`，章節變成條列。
- 表格被攤平，部分段落的閱讀順序錯亂。
- 擷取規則越疊越多，仍然無法涵蓋子圖、跨欄圖、無框表格等情況。
- DOCX 走另一套流程，抓不到 Word 裡直接畫的圖、原生圖表和嵌入物件，而能正確渲染 DOCX 的免費工具都依賴 Word 或 LibreOffice。

## Solution

擷取改成「腳本負責不漏、AI 負責判讀」：

- 只接受 PDF。其他格式（含 DOCX）直接報錯，提示使用者先另存成 PDF。
- 腳本從 PDF 文字層一次擷取依欄位排序的純文字（不做 OCR），刪掉頁首頁尾，每頁加上頁碼標記；不判斷標題層級、不還原表格。
- 腳本把每一頁渲染成疊有比例格線的**頁面圖**，給 AI 看圖、定位用。
- AI 依章節編號推斷標題層級；看到 `Table N` 時看頁面圖把表格重建成 Markdown；看到 `Figure N` / `Fig. N` 時在頁面圖上寬鬆框出圖的範圍，由腳本從範圍邊緣剝除圖說、內文、章節標題、頁首頁尾並裁掉白邊，從 PDF 重新渲染成**裁切圖**放進筆記。
- 沒有文字層的頁面（含掃描版）不報錯，標記出來由 AI 直接讀頁面圖。
- 筆記交付後清掉中間檔，輸出資料夾只留 `images/` 和 `notes.md`。

實測（原型，五個模型、兩篇論文）：章節大綱全部正確；表格重建只有一次多編一列；剝邊式裁切讓不同模型、不同鬆緊的範圍都收斂到同一張乾淨的圖。

## User Stories

1. As a paper reader, I want figures in my notes to be whole images, so that I don't see a chart split into dozens of fragments.
2. As a paper reader, I want no black mask images or watermark-only images in my notes, so that every image carries content.
3. As a paper reader, I want vector diagrams and mixed raster/vector figures captured exactly as they appear on the page, so that axis labels, arrows and annotations are not lost.
4. As a paper reader, I want figure crops that exclude the caption and surrounding body text, so that the image in my notes shows only the figure.
5. As a paper reader, I want crops rendered at a resolution high enough to read small labels, so that the figure is legible in my notes.
6. As a paper reader, I want my notes to follow the paper's section structure, including numbered subsections like 3.1.1, so that the notes map back to the paper.
7. As a paper reader, I want tables from the paper rebuilt as Markdown tables with every row and value, so that I can read and compare the data.
8. As a paper reader, I want borderless tables handled as well as ruled tables, so that no table is silently dropped.
9. As a paper reader, I want two-column papers read left column first, then right, so that paragraphs are not interleaved.
10. As a paper reader, I want running headers, footers and page numbers kept out of the text, so that they don't pollute the notes.
11. As a paper reader with a scanned PDF, I want the skill to still produce notes by reading the page images, so that I am not blocked by a missing text layer.
12. As a paper reader, I want pages without a text layer clearly flagged, so that the AI knows to read those pages from their images.
13. As a paper reader with a DOCX (or any non-PDF) file, I want a clear error telling me to save it as PDF first, so that I know exactly what to do.
14. As a paper reader, I want the output folder to contain only my notes and their images when done, so that intermediate files don't clutter it.
15. As a paper reader, I want intermediate files kept if the run fails midway, so that I can debug or resume.
16. As a paper reader, I want the skill to need no extra installs beyond PyMuPDF, so that setup stays simple and works on any OS.
17. As the AI running the skill, I want the extracted text written to a file instead of stdout, so that a long paper doesn't flood my context and I can read it in parts.
18. As the AI running the skill, I want stdout to report the text file path, page count and pages without a text layer, so that I know what to do next.
19. As the AI running the skill, I want a page marker at the start of each page in the text, so that I can tell which page image to open for a figure or table.
20. As the AI running the skill, I want numbered heading lines split onto their own line even when the PDF merges them into a paragraph block, so that I can find every section heading.
21. As the AI running the skill, I want every page rendered up front, so that I can open any page image directly without another command.
22. As the AI running the skill, I want a light grid with labelled tenths on each page image, so that I can estimate figure coordinates accurately.
23. As the AI running the skill, I want the grid to be faint, so that it doesn't hide figure details I need to read.
24. As the AI running the skill, I want to specify a crop by the page image I looked at plus a box in 0–1 page fractions, so that I never have to convert to PDF points or remember the source PDF path.
25. As the AI running the skill, I want to draw the crop box generously, so that I only need to make sure the whole figure is inside.
26. As the AI running the skill, I want the crop tool to strip captions, body paragraphs, section headings and running headers at the box edges, so that I don't need several tries to land exactly between figure and caption.
27. As the AI running the skill, I want the crop tool never to cut into the figure itself, so that trimming can't destroy content.
28. As the AI running the skill, I want text-only figures (boxes of short bullet lines) kept intact, so that taxonomy-style figures are not mistaken for body text.
29. As the AI running the skill, I want thin slivers of a neighbouring figure at the box edge removed, so that crops on pages with stacked figures stay clean.
30. As the AI running the skill, I want the crop tool to print the final box it used, so that I can see what was trimmed.
31. As the AI running the skill, I want a clear error when trimming leaves nothing, so that I know to redraw the box.
32. As the AI running the skill, I want to name each crop, so that image links in the notes are readable.
33. As the AI running the skill, I want SKILL.md to tell me to check that all four edges of a crop are complete, and to enlarge and retry if not, so that I catch boxes that were too small.
34. As the AI running the skill, I want SKILL.md to tell me to rebuild tables from page images and not crop them, so that tables stay as data.
35. As a skill maintainer, I want three small independent scripts instead of a class hierarchy, so that each is easy to read and change.
36. As a skill maintainer, I want the DOCX code, its dependency and its tests removed, so that there is only one pipeline to maintain.
37. As a skill maintainer, I want the crop-trimming behaviour testable through the CLI's printed final box, so that tests don't need image analysis.
38. As a skill maintainer, I want the version bumped to 3.0.0, so that users know the DOCX removal is a breaking change.

## Implementation Decisions

- **Input**: PDF only. Any other extension (including `.docx`) exits non-zero with a message saying only PDF is supported and to save the file as PDF first.
- **Three independent CLI scripts** replace the current extraction entrypoint, the `DocumentExtractor` base class and the PDF/DOCX extractor modules. Each is self-contained in the style of the `pdf/` skill, uses only PyMuPDF, and takes `--input` plus optional `--output-dir`, writing into `<output-dir>/<input-stem>/`.
- **Text extraction script**:
  - Writes the full text to a `text.md` file. Stdout reports only the file path, page count, and page numbers with no text layer.
  - Each page starts with a page marker (`<!-- pN -->`).
  - Running headers and footers are removed: text blocks in the top or bottom 12% of the page whose text, with digits normalized, repeats on at least 30% of pages; bare page numbers in those margins are removed too.
  - Reading order: blocks spanning both columns split the page into bands; within a band, the left column is read before the right, top to bottom within each column.
  - Lines are joined and words hyphenated at a line break are rejoined.
  - Numbered heading lines (a section number followed by a short title) start a new line even when PyMuPDF merged them into a paragraph block.
  - No heading markers and no table reconstruction. Table text is output flattened in reading order.
  - Pages with no text layer get "此頁無文字層" after their page marker. This never fails, even when every page is like that.
- **Page rendering script**:
  - Renders every page to `pages/pN.png` at 110 dpi.
  - Overlays a faint grid at tenths of page width and height, with labels `.1`–`.9` on the top and left edges. The grid is lighter than in the prototype, so it doesn't hide figure details.
  - Writes a small manifest in `pages/` recording the absolute path of the source PDF.
- **Crop script**:
  - Input: a page image path, a box `x0,y0,x1,y1` in 0–1 page fractions, and a name.
  - It derives the page number from the image file name and the PDF from the manifest, then re-renders the box from the PDF at 200 dpi without the grid to `images/<name>.png`.
  - It prints the final box used, in page fractions.
  - It exits non-zero if trimming leaves an empty or near-empty area.
- **Crop trimming rules** (from the prototype; trims inward only and never cuts through anything that is not one of these text blocks):
  1. **Side edges**: a body paragraph crossing the left or right edge, with less than half its width inside the box, moves that edge past the paragraph.
  2. **Top and bottom peeling**: repeat the following until it stops.
     - Take the item nearest the top edge and the item nearest the bottom edge. Items are text blocks, plus drawings and images that overlap the box by at least 4pt vertically.
     - If the nearest item is a caption, body paragraph, section heading or running header/footer, move that edge past it and repeat.
     - Stop when the nearest items on both edges are something else, such as figure graphics or figure labels.
  3. **Classification**:
     - Caption: text starting with `Figure N`, `Fig. N` or `Table N`.
     - Section heading: a numbered short line, at most 2 lines and 80 characters.
     - Body paragraph: dominant font size within 0.6pt of the document's most common font size, at least one line of 60 or more characters, and at least 35% of the page width wide. This keeps text-only figures with short bullet lines, and tables set in smaller type, from being peeled.
     - Running header/footer: the same rule as text extraction.
  4. **Whitespace trim**: at low resolution, remove white margins. Drop thin content runs under 5pt at the top or bottom edge that are separated from the rest by a gap of 6pt or more. Keep a 2pt pad.
- **Output layout during a run**: `text.md`, `pages/` (page images plus manifest), `images/`, `notes.md`. At the end only `images/` and `notes.md` remain.
- **SKILL.md** becomes four steps:
  1. **Extract**: run the text and page-rendering scripts.
  2. **Write**: read `text.md`.
     - Infer heading levels from section numbering.
     - For pages flagged as having no text layer, read the page images.
     - For each `Table N`, open its page image and rebuild the table as Markdown; never crop a table.
     - For each figure to include, open its page image and draw a generous box around the whole figure; the tool strips captions and text. Look at the crop, and if any edge of the figure is cut off, enlarge the box and retry.
  3. **Self-check**: unchanged.
  4. **Clean up**: after delivering `notes.md`, delete `text.md` and `pages/` only.
- **Setup and metadata**:
  - Setup lists only `pip install PyMuPDF`, and notes that DOCX and other formats must be saved as PDF first.
  - The skill description says PDF only.
  - Version 3.0.0.
- **Removals**:
  - The current entrypoint, base class, PDF extractor and DOCX extractor modules.
  - The `python-docx` dependency.
  - DOCX fixtures and tests.
  - The lint `init-hook` entries that only served those modules, if no longer needed.
  - `README.md` and `CLAUDE.md` text describing DOCX or the old extraction.
  - `.gitignore` keeps `*.docx`.
- **Unchanged**: the notes skeleton, section mapping and `references/style-guide.md`.

## Testing Decisions

- **Good tests** check external behaviour only: exit codes, files created, stdout content, and the final box the crop script prints. They do not import the scripts' internals.
- **Seam 1: the three CLIs**, run via `subprocess`. Test PDFs are generated at runtime in `conftest.py`; there are no static fixtures. Prior art is `tests/pdf/` and the CLI tests in `tests/write_paper_notes/test_extract.py`.
  - **Text script**:
    - Rejects `.docx` and other non-PDF extensions with the "save as PDF" message.
    - Writes `text.md` with page markers.
    - Stdout reports the path, page count and pages with no text layer.
    - Two-column ordering is correct.
    - Repeated header and footer text and page numbers are removed.
    - A numbered heading merged into a paragraph block gets its own line.
    - An image-only page is flagged with "此頁無文字層" and does not fail.
  - **Page script**:
    - Writes one `pN.png` per page, sized for 110 dpi.
    - Writes the manifest.
  - **Crop script**:
    - Uses a generated page with a drawn figure, its caption below, a body paragraph, a running header, and a second figure stacked below. Given a generous box, the printed final box excludes the caption, paragraph and header, and still fully contains the figure's drawing bounds.
    - A text-only figure made of short bullet lines is not peeled.
    - A body paragraph crossing a side edge is cut.
    - A box that trims to nothing exits non-zero.
    - The output image exists at 200 dpi scale.
- **Seam 2: `test_skill_files.py`**. Keep it, and update it for the new script names referenced in SKILL.md. `SKILL.md` and `references/style-guide.md` remain the only `.md` files in the skill.
- **Removed**: unit tests for `DocumentExtractor`, `PdfExtractor` and `DocxExtractor`, and all DOCX CLI tests.
- **Manual e2e**: run the full skill on `test-papers/cs.pdf` and `survey.pdf`, check against the style guide, and record findings in a ticket's Comments without naming the papers.

## Out of Scope

- OCR of any kind, including for scanned PDFs. The AI reads page images instead.
- DOCX or any non-PDF input, and converting it automatically via Word or LibreOffice.
- Automatic figure detection or automatic table structure recognition (`find_tables`, pymupdf4llm, layout models).
- Cropping tables as images.
- Rewriting the notes skeleton, section mapping or style guide.
- Changes to the separate `pdf/` skill.

## Further Notes

- Prototype scripts and outputs live outside the repo (scratchpad and `test-papers/proto/`, gitignored). Use the trimming rules above as the reference behaviour.
- **Known risk**: a weak model may draw a box that cuts the figure and not notice. Trimming can't recover lost content. The SKILL.md instruction to check all four edges is the mitigation.
- **Known limitation**: short non-caption text at a box edge, such as author emails above a figure, is not peeled. The AI tightens the box itself.
- Measured cost: rendering 51 pages takes about 6 seconds. Viewing a page image costs about 1.5k tokens, so the AI should open only pages with figures, tables, no text layer, or text that looks wrong.
