# 找岗可投岗位

Run this step on every live or partial career report, after resume intake and before strategy prose. The output is a ranked apply list of at most 10 postings, each one opened in this run. It is not a sample of job ads used as atmosphere around a career essay.

## What to search

Build queries from de-identified tasks, seniority, graduation timing, and cities the person can actually work. Do not paste the resume, name, contacts, or confidential project details into a query.

Cover both sides:

- Employers whose work matches proven experience. Open the employer careers site and the company ATS (Workday, Lever, Greenhouse, the employer's own `/careers` or `/jobs` page, and vendor hosts such as `*.zhiye.com` when that is the employer's system).
- Named primary boards for this market. Use Boss Zhipin (BOSS直聘) for mainland China searches. Use LinkedIn when the live posting is there. Use the school's official campus career site for a student. Add 前程无忧, 智联招聘, 猎聘, Handshake, Indeed, USAJobs, Seek, or another board only when employers in this market post there directly.

A news article, WeChat recap, aggregator blog, or screenshot mirror is a reprint. Use it only to find the original requisition. Open the original in this run and cite that URL. If the original will not open, record the reprint as `excluded_jobs` with `reason_code` `reprint_only` or `could_not_open`. Do not put it on the apply list.

Record `job_search.boards_searched` with the sites and boards actually opened, not the ones you intended to open.

## Open and record every candidate

A search snippet is `indexed_only`. For each posting you might recommend, open the page and store:

| Field | Rule |
| --- | --- |
| Employer, title, location, level | As shown on the page you opened. |
| Eligibility | Graduation year, degree, residency, or on-site rule as written. `eligible` or `conditional` only if this person can meet it. Otherwise exclude. |
| Tasks | What the hire will do. Use this for fit and for clerical-versus-substance, not the title alone. |
| Posting date | The date the page shows. Null if the page does not show one. Do not copy today's date into this field. |
| Deadline | As shown, or null. An expired deadline is closed. |
| Source name | Employer careers, the ATS name, Boss Zhipin, LinkedIn, the campus career site, or another named board. Not a raw URL. |
| URL | The page you opened. This becomes `apply_url` and the source `url`. They must match. |
| Checked at | ISO 8601 time with timezone, inside this run, when you opened the page. |
| Retrieval | `opened` only after the posting body was readable. `blocked` if it failed. `closed` if the page says closed, filled, or expired. |
| Advertised status | `open` only when that page shows the job as open or clearly accepting applications. Otherwise `closed` or `unknown`. |
| Source quality | `official` (employer site), `ats`, `primary_board`, or `campus`. Reprints are `reprint` and cannot be recommended. |

Deduplicate by employer requisition and description. Keep real separate requisitions. If two URLs are the same posting, cite the original once.

## Hard exclusions

Do not rank, and do not mark `currently_recommended`, when any of these is true:

- The posting was not opened in this run, or the body did not load.
- Advertised status is closed, expired, unknown, or only implied by a reprint.
- Graduation year, degree, citizenship, or work authorization on the page excludes this person.
- The location or on-site rule conflicts with a constraint the person has actually stated.
- The work is unrelated to proven experience and is not a deliberate, labeled stretch the person said they will consider.
- The only URL you can cite is a reprint, a news recap, or a search snippet.

Put dropped postings in `excluded_jobs` with a `source_id` and a `reason_code`: `closed`, `unverified`, `class_year_mismatch`, `reprint_only`, `ineligible`, `not_relevant`, `could_not_open`, `wrong_location`, `clerical`, or `duplicate`. An excluded source cannot also appear in `recommended_jobs`.

A short list is an acceptable result. Padding is not. If bank recruiting, campus boards, or a niche field simply has fewer than 10 open, relevant, first-hand postings, say what you searched, what you opened, and which exclusion removed the rest.

## Rank only the survivors

Apply the rubric in `SKILL.md`. Order of importance:

1. First-hand verified as currently open, or clearly accepting applications, in this run. Gate, not a tiebreaker.
2. Fit to proven work, not keywords.
3. Eligibility the person can actually meet.
4. Role quality: substance and a path toward the person's goal, versus clerical padding.
5. Source quality: official, ATS, or primary board over a reprint. A reprint should already be gone.
6. Freshness and deadline urgency.
7. Retention or conversion only if that posting states it. Do not infer return offers from employer prestige.

Write `rank` as 1..n with no gaps, `n` ≤ 10. Write `rank_reason` as one or two sentences that cite this person's evidence and a real constraint. Do not add `score`, `match_score`, or any weighted total.

`job_search.target_count` is 10. `verified_open_count` equals the length of `recommended_jobs`. When that length is under 10, `shortfall_reason` states why, in a way a reader can check against the excluded set.

## Then write the report

The HTML page is the primary artifact. Each recommended job card shows the rank, the reason, and a citation block with source name, clickable URL, posting date, deadline, and checked-at time. The same block appears in the Markdown. The CSV keeps the ledger row; it does not replace the visible citation.

Track-level advice comes after this list and points back to it. Do not lead with an industry overview and attach jobs at the end.
