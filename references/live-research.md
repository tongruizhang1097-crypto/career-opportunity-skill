# Live market research and freshness

## Start each run

Record a new run ID, start timestamp, and client timezone. Use ISO 8601 timestamps with explicit UTC offsets in the manifest; show the user's timezone in the report. Search during this invocation, even when a previous report is available. Do not copy an old search reference into a new report and label it freshly checked.

If the user explicitly requests an offline analysis, honor that instruction and use the offline status. Never override a no-browsing request to satisfy a freshness badge.

Perform research after extracting a de-identified capability/task profile. Use user-provided job links and authorized sources where relevant. Inspect primary employer pages and original reports where accessible. Record blocked, indexed-only, closed, and cached sources accurately.

## Freshness by evidence type

| Type | Execution rule |
| --- | --- |
| Current job examples | Open and inspect the relevant employer/ATS pages in this run. Record requisition, location, level, and availability evidence. A readable page is not proof of funded headcount; an open/accepting-applications indication supports only the advertised status. A closed page is current counterevidence, not a current vacancy. |
| News, investment, product or business changes | Search recent windows, normally the last 30–90 days, and inspect the material events. Expand the window when needed and state it. Separate event date, publication date, and inspection date. |
| Official statistics and recruiting reports | Retrieve the latest relevant release that is actually available. State its publication date and data period, including any lag. A report opened today can still describe an older market. Do not replace a relevant official series with a promotional forecast merely because the forecast is newer. |
| Historical comparisons | Preserve cohort, definitions, period, units, and coverage. Recheck the original baseline when feasible. Mark stale or inaccessible history as such; do not manufacture a baseline from a current snapshot. |
| Methodological references | Use for reasoning only. Reopening a methods paper does not establish fresh market coverage. |

For shortlisted directions, seek several relevant descriptions across multiple employers plus independent business/trend context when available. As an effort guide, inspect roughly 2–4 suitable descriptions per shortlisted direction; expand for ambiguity and never invent examples to satisfy a quota. Record the actual sample and employer counts. An unavailable or tiny sample may justify an exploration hypothesis rather than a current-opportunity recommendation.

Check the matching region and career level. If search results are empty, broaden synonyms and task terms before concluding that evidence is missing. Do not infer an absent market from a limited search or infer national trends from a convenience sample.

## Report status

- `live`: Fresh market retrieval occurred, material current claims were checked in this run, and limitations are disclosed. This means a current checked snapshot, not complete market coverage or proven scarcity.
- `partial`: Some market evidence was freshly inspected, but a material source, job status, comparison, or dataset remains unavailable or stale. State which conclusions are current and which are provisional.
- `offline`: No live market sources were inspected. Provide CV-based analysis, explicitly dated supplied evidence, and a verification plan; withhold assertions of current openings, fastest growth, or confirmed scarcity. Do not badge the report as realtime.

A `prioritize` recommendation about current opportunities needs freshly inspected employer-job evidence at the relevant level and region. If that cannot be established, use a conditional `explore`/`watch` decision or change the claim to a long-term capability option. Even verified current job examples do not establish demand growth or a shortage without separate evidence.

## Manifest and audit

Use `assets/run-manifest-template.json`. Register each source ID, source kind, source family, URL, publication date, reference period, checked timestamp, retrieval status, and status note. Unknown publication dates are null; explain unknown/lagged periods for statistical claims. Use `cached` when material was not re-opened in this run.

Link candidate decisions to source IDs. Distinguish `current_opportunity` from `long_term_option`. Record any current job status limitations in the report and the evidence CSV. Finalize the generation timestamp after research, then run:

Populate source records with `id`, `url`, `source_kind`, `source_family`, `published_at`, `reference_period`, `checked_at`, `retrieval_status`, `advertised_status`, `geography`, `career_level`, and `note`. Use source kinds `employer_job`, `official_statistics`, `business_disclosure`, `platform_report`, `practitioner`, `user_supplied`, or `methodology`. Use retrieval states `opened`, `indexed_only`, `closed`, `blocked`, `cached`, or `user_supplied`; use advertised states `open`, `closed`, `unknown`, or `not_applicable`. Only mark a job `open` when the inspected source actually advertises it as open or accepting applications.

Populate recommendation records with `candidate_id`, `status` (`prioritize`, `explore`, `watch`, or `deprioritize`), `claim_kind` (`current_opportunity` or `long_term_option`), `confidence` (`low`, `moderate`, or `high`), and `source_ids`. The audit checks declared source links, not semantic agreement of location, seniority, and content; verify those manually.

```bash
python scripts/audit_run.py /path/to/run-manifest.json
```

Treat audit errors as metadata contradictions to correct before delivery. Explain coverage warnings rather than pretending they are cleared. The audit checks dates, references, status, and declared current evidence; it does not fetch sources, parse a CV, assess claim truth, or verify actual hiring.

When refreshing, check recommended employer sources again, find newer releases, and distinguish changed market evidence from changed profile or preferences. Do not silently redate the old report. No background polling or scheduled updates are created by this skill.
