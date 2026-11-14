# How other skills handle external tools (APIs, keys, MCP)

Survey date: 2026-11-14. Input for Q46–Q54 of the `evaluate-paper` grilling.

## Sources

| Source | What it shows |
|---|---|
| Anthropic, [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Official guidance on MCP references, scripts, dependencies |
| Anthropic, [knowledge-work-plugins `CONNECTORS.md`](https://github.com/anthropics/knowledge-work-plugins) | Category-based connectors (`~~CRM`), skills work with no connector |
| Anthropic `morning` skill (installed, synced) | Sort available tools into roles; a missing role is skipped |
| K-Dense [`paper-lookup`](https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/skills/paper-lookup/SKILL.md) | 18 scholarly APIs incl. OpenAlex/Crossref; optional env-var keys |
| K-Dense [`scholar-evaluation`](https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/skills/scholar-evaluation/SKILL.md) | Paper evaluation; explicit metric and prestige policy |
| Matt Pocock `wizard`, `handoff`, `tdd/mocking.md` (installed) | Human-only credential setup; redact keys; mock only at system boundaries |

## Findings

1. **Naming MCP tools: two official patterns.**
   - The best-practices page says to use fully qualified `ServerName:tool_name`. This applies when the skill depends on one known server.
   - Anthropic's own plugins and `morning` instead name a *category or role* ("CRM", "calendar") and let any connected tool fill it. A missing role is skipped, or the user supplies the data by hand.
   - **Fits Q48:** the providers here are interchangeable, so naming by capability is the established pattern, not an improvisation.
2. **Declare the external dependency in frontmatter.** `paper-lookup` uses the spec's `compatibility` field: "Needs network access … No credentials are required; … `OPENALEX_API_KEY` … raise rate limits".
3. **Keys are optional; never stall.**
   - In `paper-lookup`, a missing key means it continues at the lower rate and tells the user which key would help. Our Q46/Q49 swap the env var for "use an MCP if present".
   - `paper-lookup` reads only the named variables from `.env`, never the whole file.
4. **Redact credentials from provenance.** `paper-lookup`'s script strips `api_key`, `email` and `mailto` from the URLs it records. `handoff` gives the same rule.
5. **A 200 response is not success.**
   - Example: OpenCitations answers an unknown DOI with `count: 0`.
   - The rule is to check the shape of the response, not just the status code, and to report each failed source explicitly. A silent gap reads as "nothing exists".
6. **Treat API responses as untrusted data.** Titles and abstracts may contain injected instructions. Extract and validate single fields (such as a DOI) before reusing them.
7. **Provenance makes a result repeatable.** Record the endpoint, parameters, identifier and access date with each result.
8. **Metric policy (`scholar-evaluation`).**
   - Never infer quality from JIF, citation counts, h-index, or venue/institution prestige.
   - Check publisher retraction notices and Crossmark. Record an unresolved status instead of treating the absence of a notice as verification.
   - Freeze the evidence-access date.
   - **Matches Q26.** It adds the wording rule: "no retraction found" is not "not retracted".
9. **Testing.** Mock only at system boundaries, i.e. the external API (`tdd/mocking.md`). This matches the plan for a fake local HTTP server.
