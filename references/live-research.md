# Live market research and freshness

## Start each run

Record a new run ID, start timestamp, and client timezone. Use ISO 8601 timestamps with explicit UTC offsets in the manifest; show the user's timezone in the report. Search during this invocation, even when a previous report is available. Do not copy an old search reference into a new report and label it freshly checked.

If the user explicitly requests an offline analysis, honor that instruction and use the offline status. Never override a no-browsing request to satisfy a freshness badge.

Perform research after extracting a de-identified capability/task profile. The mandatory next step is 「找岗可投岗位」 in `references/job-search.md`: search employer sites and primary boards, open postings, exclude closed or unverified ones, then rank at most 10. Use user-provided job links and authorized sources where relevant. Inspect primary employer pages and original reports where accessible. Record blocked, indexed-only, closed, and cached sources accurately. A reprint is only a lead. Open the original posting in this run and cite that URL. Do not cite the reprint as the apply link.

## Freshness by evidence type

| Type | Execution rule |
| --- | --- |
| Current job examples | Open the employer site, company ATS, or named primary board in this run. Record requisition, location, level, eligibility, posting date, deadline, and availability. `open` means that page shows the job as open or accepting applications. A readable page is not proof of funded headcount. A closed, expired, indexed-only, or reprint-only page is counterevidence, not a current recommendation. |
| News, investment, product or business changes | Search recent windows, normally the last 30–90 days, and inspect the material events. Expand the window when needed and state it. Separate event date, publication date, and inspection date. |
| Official statistics and recruiting reports | Retrieve the latest relevant release that is actually available. State its publication date and data period, including any lag. A report opened today can still describe an older market. Do not replace a relevant official series with a promotional forecast merely because the forecast is newer. |
| Historical comparisons | Preserve cohort, definitions, period, units, and coverage. Recheck the original baseline when feasible. Mark stale or inaccessible history as such; do not manufacture a baseline from a current snapshot. |
| Methodological references | Use for reasoning only. Reopening a methods paper does not establish fresh market coverage. |

The apply list is the current-opening product. Search widely enough to find real vacancies, then keep every posting that is first-hand verified as open and relevant, up to 10. If fewer than 10 survive, report the shorter list and the exclusions. Never invent or reopen closed ads to fill the quota. A thin verified list supports a conditional strategy, not a padded top 10. Direction comparisons may cite those same opened postings; they do not replace the list.

Check the matching region and career level. If search results are empty, broaden synonyms and task terms before concluding that evidence is missing. Do not infer an absent market from a limited search or infer national trends from a convenience sample.

## Report status

- `live`: Fresh market retrieval occurred, material current claims were checked in this run, and limitations are disclosed. This means a current checked snapshot, not complete market coverage or proven scarcity.
- `partial`: Some market evidence was freshly inspected, but a material source, job status, comparison, or dataset remains unavailable or stale. State which conclusions are current and which are provisional.
- `offline`: No live market sources were inspected. Provide CV-based analysis, explicitly dated supplied evidence, and a verification plan; withhold assertions of current openings, fastest growth, or confirmed scarcity. Do not badge the report as realtime.

A `prioritize` recommendation about current opportunities needs freshly inspected employer-job evidence at the relevant level and region. If that cannot be established, use a conditional `explore`/`watch` decision or change the claim to a long-term capability option. Even verified current job examples do not establish demand growth or a shortage without separate evidence.

Every job in `recommended_jobs` needs `source_quality` of `official`, `ats`, `primary_board`, or `campus`, an `apply_url` equal to the opened source URL, and `checked_at` inside this run. Set `eligibility` to `eligible` or `conditional`. Do not mark a closed, unknown, indexed-only, blocked, cached, ineligible, or reprint source as `currently_recommended`. When the verified list is shorter than 10, set `job_search.shortfall_reason`. Keep `ranking_rubric` in the manifest exactly as:

`first_hand_open_this_run`, `fit_to_proven_work`, `eligibility`, `role_quality`, `source_quality`, `freshness_and_deadline`, `retention_only_if_stated`.

Do not add a numeric match score. On the HTML page and in Markdown, put the source name, URL, posting date, deadline, and checked-at time directly under the claim or job.

## Manifest and audit

Use `assets/run-manifest-template.json`. Register each source ID, source kind, source family, URL, publication date, reference period, checked timestamp, retrieval status, and status note. Unknown publication dates are null; explain unknown/lagged periods for statistical claims. Use `cached` when material was not re-opened in this run.

Link candidate decisions to source IDs. Distinguish `current_opportunity` from `long_term_option`. Record any current job status limitations in the report and the evidence CSV. Finalize the generation timestamp after research. Before the audit, fill the manifest as follows.

Populate source records with `id`, `url`, `source_kind`, `source_family`, `published_at`, `reference_period`, `checked_at`, `retrieval_status`, `advertised_status`, `geography`, `career_level`, and `note`. For a job, also set `source_quality` to `official`, `ats`, `primary_board`, `campus`, or `reprint`. Use source kinds `employer_job`, `official_statistics`, `business_disclosure`, `platform_report`, `practitioner`, `user_supplied`, or `methodology`. Use retrieval states `opened`, `indexed_only`, `closed`, `blocked`, `cached`, or `user_supplied`; use advertised states `open`, `closed`, `unknown`, or `not_applicable`. Only mark a job `open` when the inspected source actually advertises it as open or accepting applications.

Populate recommendation records with `candidate_id`, `status` (`prioritize`, `explore`, `watch`, or `deprioritize`), `claim_kind` (`current_opportunity` or `long_term_option`), `confidence` (`low`, `moderate`, or `high`), and `source_ids`. A `current_opportunity` claim marked `prioritize` or `explore` needs at least one source opened at an `http(s)` URL in this run.

Populate each recommended job with `rank`, `job_id`, `employer`, `title`, `source_id`, `source_name`, `source_quality`, `apply_url`, `published_at`, `deadline`, `checked_at`, `eligibility`, and `rank_reason`. The audit checks declared links, timestamps, and status, not the wording of the posting; verify location, class year, and tasks on the page you opened.

```bash
python3 scripts/audit_run.py /path/to/run-manifest.json
```

Treat audit errors as metadata contradictions to correct before delivery. Explain coverage warnings rather than pretending they are cleared. The audit checks dates, references, status, and declared current evidence; it does not fetch sources, parse a CV, assess claim truth, or verify actual hiring.

When refreshing, check recommended employer sources again, find newer releases, and distinguish changed market evidence from changed profile or preferences. Do not silently redate the old report. No background polling or scheduled updates are created by this skill.
