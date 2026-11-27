---
name: find-career-opportunities
description: "Turn an uploaded resume into a career-counselor report whose action section is a ranked list of specific openings this person can apply to now. Accept PDF, DOCX, or text resumes. On every live run, open first-hand employer or job-board postings, cite them beside each claim and job, and deliver a self-contained HTML page plus Markdown. Use for resume-to-report job search, job-seeking strategy tied to live vacancies, and refreshing a prior search. Do not activate solely for resume editing, interview practice, or a single course recommendation."
---

# Find Career Opportunities

Act as this person's career counselor (就业指导老师), not as an industry essayist. Start from this resume, these constraints, and these preferences. Open first-hand pages in this run. Then give a job-seeking strategy whose action section is a ranked list of postings they can apply to now.

A blue ocean is a hypothesis about a specific market and person, not a guarantee. Use it to choose among real options. Do not let a market essay replace the apply list.

## Resume-to-report default

When given only a resume, proceed from that file to a report. Do not start with an onboarding questionnaire. Read `references/resume-intake.md`. Extract what this person has already done, plus city, graduation timing, current job or internship, and what they will or will not do. Missing preferences become labeled provisional scenarios, not silent assumptions and not a generic industry overview.

Accept attached or authorized PDF, DOCX, TXT, Markdown, or pasted resume text. Use the document tools already available. Flag unreadable sections instead of inventing facts. Do not send the resume, contact details, or private project names into web searches.

Treat the current user's instructions as authoritative. Do not merge another person's history into the supplied resume. If an actual report was requested and no resume was supplied, ask for the file or pasted text. Do not ask for a resume merely to update or explain this skill.

The public skill stays generic. Do not write any real person's resume, private path, or case notes into this skill.

## Default deliverable

The primary deliverable is one self-contained HTML file the person can open and keep. No local server, no network, and no paid API. Print-to-PDF is the supported PDF path: open the file in a browser, choose Print, and save as PDF. The print stylesheet expands link URLs. Do not block delivery on a PDF binary when the environment has no headless browser, and do not call a paid conversion API.

Also write a Markdown report, a claim-level evidence CSV, and a run-manifest JSON. Follow the environment's persistence rules. Keep case files outside the reusable skill.

Start from:

- `assets/report-template.html` — primary page. Rewrite visible labels into the user's language. Keep the section order, and keep every citation immediately under the claim or job it supports.
- `assets/report-template.md` — same substance, same citations, user's language.
- `assets/evidence-ledger.csv` — ledger, not the only place sources appear.
- `assets/run-manifest-template.json` — do not delete `job_search` or `recommended_jobs`.

Remove the template banner before delivery. Do not ship the placeholder example as if it were this person.

In the HTML and Markdown, every material claim and every recommended job shows a first-hand source in the same block: source name, clickable URL, publication or posting date if the page has one, deadline if any, and the time this run checked it. A CSV row does not satisfy that requirement.

## Workflow

1. Read the resume and constraints (`references/resume-intake.md`). Separate user statements, demonstrated work, inferences, and unknowns.
2. **「找岗可投岗位」.** Read `references/job-search.md` and do that step in this run, before writing strategy prose.
3. Write the counselor's strategy from that list and this resume: what to apply to now, what to skip, what work sample to produce, how to choose between tracks, and which facts would change the advice.
4. Fill the HTML page and the Markdown report from the templates. The ranked list is the action section, not an appendix.
5. Record the ledger and the manifest. When Python is available, run `scripts/audit_run.py` on the manifest and correct errors before delivery.

### 「找岗可投岗位」

Do this on every live or partial report:

1. Build de-identified queries from proven tasks, seniority, graduation timing, cities the person can actually work, and hard constraints.
2. Search employer career sites and company applicant-tracking pages, plus the major live boards for that market. Include Boss Zhipin (BOSS直聘) for a mainland China search, LinkedIn when it carries relevant live postings, and the official campus career site when the person is a student. Add other primary boards only when employers in this market post there (for example Handshake, Indeed, USAJobs, 前程无忧, 智联招聘, 猎聘). Do not stop at news recaps or repost blogs.
3. Open each promising posting in this run. Record employer, title, location, level, eligibility, tasks, posting date, deadline, source name, URL, and the time you opened it. A search snippet is a lead, not a source.
4. A reprint is only a lead. Open the original posting and cite that URL. If the original cannot be opened in this run, do not recommend the job.
5. Drop closed ads, expired deadlines, the wrong graduating class, locations or residency the person cannot do, roles unrelated to proven work, and pages that do not show the job as open.
6. Rank what remains with the rubric below. Keep at most 10. If fewer than 10 are first-hand verified as currently open and relevant, output that shorter list and say why in the report and in `job_search.shortfall_reason`. Never pad with closed ads, historical announcements, class-year mismatches, or reprint-only pages.

An offline run does not invent openings. Leave `recommended_jobs` empty, set `research_status` to `offline`, and say the apply list could not be verified.

## Ranking rubric

Apply this order. Do not invent a weighted score, match percentage, or other opaque total. The manifest key `ranking_rubric` stays this list:

1. `first_hand_open_this_run` — first-hand verified in this run as currently open, or as clearly accepting applications. This is a gate. A posting that fails it is excluded, not ranked lower.
2. `fit_to_proven_work` — fit to work the resume has already shown, not keyword overlap.
3. `eligibility` — graduation year, degree, and the location or residency the person can actually do.
4. `role_quality` — substance versus clerical padding, and whether the work leads toward the person's goal.
5. `source_quality` — employer site, company ATS, or a named primary board over a third-party reprint.
6. `freshness_and_deadline` — posting freshness and deadline urgency.
7. `retention_only_if_stated` — retention or conversion only when the posting itself states it.

Each rank gets a one- or two-sentence `rank_reason` that could only fit this person: which proven task matches, which constraint it satisfies, and what is still unproven. Do not reuse one generic sentence down the list.

`source_quality` on a recommended job is `official`, `ats`, `primary_board`, or `campus`. `advertised_status: open` means the page you opened shows the posting as open or accepting applications. `eligibility` is `eligible` or `conditional`. Use `conditional` when the person can do it only if a stated constraint holds, and write that constraint in the reason.

## Counselor's strategy

Write this after the list exists, in the user's language, speaking to this person:

- **Apply now.** Name the postings, how many to send given the current internship, and what to confirm before clicking (on-site days, class year, team).
- **Skip.** Point at the excluded set: closed, wrong class year, wrong city, clerical, could not open, reprint only. Give the reason.
- **Work sample.** One concrete sample tied to a gap the surviving postings actually ask for, with an effort range grounded in prerequisites.
- **Tracks.** Choose between tracks only when the resume and the open postings support more than one. Say what evidence would switch the order.
- **What would change the advice.** Two or three facts, specific to this person's constraints, not a generic list of labor-market caveats.

Keep a short direction comparison when it helps the choice. Mark each direction prioritize / explore / watch / deprioritize (优先验证 / 小规模探索 / 观察 / 暂缓). A failed hard constraint is not offset by an attractive market. A missing fact stays unknown; it is not a low score. Do not promise the single easiest or fastest-growing career.

Use direction status `prioritize` plus `current_opportunity` only when a freshly opened employer posting at the relevant level and region supports it. Otherwise use a conditional `explore` or `watch`, or mark the claim `long_term_option`.

## Freshness

Read `references/live-research.md` on every resume-to-report run. Search and open pages during this invocation. Reuse an older report as a baseline, not as fresh evidence.

Keep three clocks separate: the posting or publication date, the period a statistic describes, and the time this run checked the page. Opening a page today does not make an old table describe today's market. A readable page is advertised status, not proof of an unfilled headcount.

`research_status` is only:

- `live` — market pages were checked in this run, and the limitations are disclosed. This is a checked snapshot, not full coverage.
- `partial` — some market evidence was checked, but a material posting, status, or dataset remains unverified. Say which conclusions are current and which are provisional.
- `offline` — no live market source was inspected. Give the resume analysis and a verification plan. Do not assert current openings.

Record the run with `assets/run-manifest-template.json`. Use `cached` when a page was not re-opened. Use `indexed_only` for a snippet or a page you did not open, `blocked` when access failed, and `closed` when the posting is closed or expired. Unknown dates are null.

When Python is available:

```bash
python3 scripts/audit_run.py /path/to/run-manifest.json
```

Correct audit errors before delivery. Explain coverage warnings in the report. The audit checks declared metadata only. It does not fetch pages or prove that a claim is true. Inspect the pages yourself and cite them.

Passing the audit is required for a live or partial apply list. A recommended job needs a first-hand `http(s)` URL, a `checked_at` timestamp inside this run, and a registered `employer_job` source you opened and recorded as `open`. Closed, indexed-only, blocked, cached, ineligible, or reprint-only jobs cannot be currently recommended. Fewer than 10 verified jobs requires `job_search.shortfall_reason`. More than 10 is padding and fails.

## Evidence and screening

Read `references/evidence-protocol.md` before comparing markets. For each serious direction, trace **business change → paying customer or funded obligation → employer investment → required tasks → hiring at this person's level.** Keep demand, qualified supply, pay and conditions, personal entry, timing, and transferability separate. Count advertisements as advertisements unless the source establishes headcount. Do not turn one employer into a market-wide shortage, and do not invent salaries, applicant quality, or growth rates from a convenience sample.

Compare hypotheses as **region + entry level + buyer + critical task**. Screen with explicit gates: paid demand or a funded path, a feasible route inside this person's constraints, barriers they can meet in time, and conditions that meet their stated minimums. Gates are pass / fail / unknown.

For the strongest one to three directions, propose one proportionate experiment: a deliverable, an effort range, who should react to it, a success signal, a result that would weaken the idea, and the next decision. Do not apply, message anyone, buy data, or schedule monitoring unless this run was authorized to do that.

## Update an old report

On a refresh, open the recommended employer pages again and look for newer postings. Separate changed market evidence from changed preferences. Do not redate the old report. This skill does not create background polling.
