# Report format and self-check rules

The report is one Markdown file, `appraisal.md`. Check it against every rule below after writing; fix each failure and check again until all pass.

## Layout (this order)

```
# <Paper title> — <appraisal heading in the report language>
> <User's research question>

## <Conclusion>
**<Usage label>**: <one or two sentences of reason>

### <Still to confirm>
- ...

## <Article ID card>
## <External assessment>
### <Checklist>
### <External metrics>
## <Content judgement>
```

Translate every heading into the report language.

## Rules

1. **Conclusion first.** The first section after the title is the conclusion: one usage label (主報告 / 背景 / 比較 / 暫不使用 in the report language) plus one or two sentences of reason. The reason names the content-judgement items that decided the label (for example "item 2 and item 3") and does not contradict them: 主報告 needs item 2 ok and no concern in items 3 to 5 on a claim the user will rely on, and when two labels both fit the report names the more cautious one and says why the other did not apply.
2. **Retraction leads.** If any source reported a retraction, the label is 暫不使用 and the first sentence of the reason says so.
3. **Relative to the question.** The research question is quoted under the title, and the reason refers to it.
4. **No scores.** No numbers, grades, stars, rankings or percentages stand in for a judgement. Raw metric values from the metrics script may appear, labelled as clues.
5. **Still to confirm.** The conclusion has a "still to confirm" list. Every metric that was not obtained and every "not enough information" outcome appears in it. If there is nothing, write that explicitly.
6. **Every judgement has a location.** Each content-judgement item and each checklist answer cites the paper's location (section, page, table or figure).
7. **Metrics are traceable.** Each metric states its source, its identifier (DOI or journal ID) and its query date. When `metrics.json` from an earlier day was reused, the original query date is stated. Article-level numbers from OpenAlex and Crossref are shown side by side, not merged.
8. **Exact wording for metrics.** `2yr_mean_citedness` is called a JIF-style number, never "JIF" or "impact factor". "No record found" is written as 查無撤稿紀錄 (or its translation), never "not retracted". JIF and CiteScore appear only with year and subject category, or with the note that they are missing so no cross-journal comparison is possible.
9. **Failures are named.** Each failed or skipped source is listed with its reason. A missing value is "not obtained", never blank, and the report says what kind of capability would supply it.
10. **Sources of tool data.** Numbers from an MCP tool carry "來源：MCP〈server name〉" (translated into the report language), plus identifier and query date. When no MCP tool matched, the report says "未取得" for each missing value (quota-exhausted OpenAlex data, JIF, CiteScore), names the kind of capability that would supply it, and points to Clarivate Journal Citation Reports (JIF) and Scopus (CiteScore) as places the user can look, without recommending any product or tool. These numbers never change the label.
11. **Identity card only identifies.** It holds bibliographic details and DOI, venue, article type, version read, and review status, with no judgement. A preprint or unreviewed version is stated as such. When the PDF is not the version of the DOI whose metrics are reported (for example a submitted manuscript read against the published DOI), the card says so and the metrics section names which DOI the numbers belong to.
12. **Checklist section.** The report names the checklist used and why it was chosen. Every question of that checklist appears, in the checklist's own order and sections, in the CASP style: a numbered line with a short restatement of the question, and under it one indented line that starts with the answer in bold, then the paper's location and the basis. Do not use a table. Example:

    ```
    3. 是否納入所有重要研究？
       - **無法判斷。** 方法 3.2：六個資料庫與雙向滾雪球，但起始年份前後不一致。
    10. 好處是否值得代價？
        - **不適用：** 沒有介入，沒有好處與代價可比較（摘要）。
    ```

    Answers use the checklist's own options, with "can't tell" written in the report language, or "不適用：reason" (translated) as the checklist selection rules describe; none is left blank. The section ends with what the checklist asks for: the appraisal summary (CASP, with Positive, Negative and Unknowns), the overall confidence level with its critical flaws (AMSTAR 2), or the per-criterion answers (MMAT). No total, count or grade, and not-applicable answers are not counted either. If no checklist fits, the section says so and gives the reason; it does not invent questions.
13. **Language.** The whole report, including headings, is in the report language.
14. **Last line.** When shown in the conversation, the last line gives the work-folder path of `appraisal.md` and asks whether to save it to `<output-dir>/<pdf-stem>/appraisal.md`. When the user asked up front to save, the last line gives the saved path instead.
15. **Corrections and updates.** Correction or update records in the metrics output (`updates`) are named in the report, with the content-judgement item on source and version. If there are none, the report says none were found by the sources queried.
16. **No secrets.** The report contains no API key, no email address and no `mailto` value.
