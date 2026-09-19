# Code-quality review — G001

## Verdict

- **codeQualityStatus:** WATCH
- **recommendation:** APPROVE
- **Scope:** `.omo/ulw-research/20260918-231935/{REPORT.md,SYNTHESIS.md,render_report.py,final-audit.txt,claim-graph.md,source-link-audit.tsv}` and generated `REPORT.{html,pdf,docx}`.

The delivery is coherent enough to approve as public-document research, not legal advice.  It explicitly rejects an unsupported single-template analogy (`REPORT.md:8`; `claim-graph.md:18`) and instead describes a bounded, sourced combination.  The claim graph distinguishes six supported synthesis claims from two unresolved claims, and the report repeats jurisdiction and legal-counsel limitations.

I independently confirmed the final-audit claims that the PDF is a tagged, unencrypted, seven-page A4 file and the DOCX ZIP is structurally valid.  `REPORT.md` has 47 citation occurrences over 30 unique URLs; the audit covers exactly those 30 unique URLs.  The DOCX has 30 external hyperlink relations, and the generated HTML has 47 anchors.  The renderer parses as Python AST without syntax error.  No production tests were added or deleted, so there are no deletion-only, tautological, prompt, or implementation-mirroring tests to flag.

## Findings

### CRITICAL

None.

### HIGH

None.

### MEDIUM

1. **The synthesis misstates the documented source-audit count.** `SYNTHESIS.md:43` says 20 URLs opened directly and 10 had errors, while both `final-audit.txt:11-15` and the 30 TSV rows establish 21 `open:200` and 9 non-open results.  This does not invalidate the report's caveats, but the summary should reproduce the audit accurately.

2. **Nine cited URLs were non-open at audit time, including sources supporting several concrete examples.** `source-link-audit.tsv` records five 404s, two inaccessible HTTP errors, one timeout, and one 500.  Examples include the Book I canon-law link used at `REPORT.md:19`, the Carl Zeiss statute at `REPORT.md:100`, and the St. Joseph bylaw at `REPORT.md:66`.  The audit and `SYNTHESIS.md:41-43` disclose this rather than concealing it, and the central synthesis has alternative primary support, but future revisions should replace or archive these sources before treating those individual examples as independently reproducible.

3. **The renderer is over the applicable source-size ceiling and mixes rendering with network auditing.** `render_report.py:1-302` has 268 nonblank, noncomment lines and owns HTML rendering, DOCX construction, and source URL checks.  This is a maintainability issue, not evidence that the current artifacts are invalid.  It should be split by responsibility or given a documented standalone-script size exception before substantive extension.

### LOW

1. `render_report.py:276,279` uses broad `except Exception` at the external-network boundary.  The fallback is contained and intentionally converts failures to audit statuses, but narrower expected network exceptions would make unexpected renderer defects visible.

2. `render_report.py:11` imports `WD_SECTION` without use.

## Required skill-perspective check

Ran.  The `remove-ai-slops` perspective found no behavioral tests to assess and no needless production parsing/normalization in the report pipeline beyond the small Markdown-to-output renderer needed for the requested artifacts.  It does identify the oversized, multi-responsibility renderer as maintenance slop (MEDIUM).  The `programming` perspective likewise finds the renderer's size/responsibility boundary and broad catches non-ideal; no untyped escape hatch, brittle prompt test, or implementation-mirroring test is present.  These are not blockers for the already-generated research artifacts.

## Residual risks

The report is explicitly a public-source synthesis, not jurisdiction-specific legal advice.  Its recommendations must be validated against the eventual country, entities, ownership, regulatory constraints, and current primary documents.  The non-open citations are the main reproducibility risk.
