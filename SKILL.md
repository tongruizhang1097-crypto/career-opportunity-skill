---
name: find-career-opportunities
description: Turn an uploaded resume or CV into a personalized career-opportunity report using fresh web research at each invocation. Accept PDF, DOCX, or text resumes; extract evidenced capabilities, discover adjacent and emerging roles, and compare paid demand, qualified supply, entry costs, timing, and transferable skills. Use for resume-to-report career research, finding blue-ocean careers, market-informed study or research choices, and refreshing a prior report. Do not activate solely for resume editing, interview practice, or a single course recommendation.
---

# Find Career Opportunities

Find evidence-supported career opportunities that the person can realistically enter and benefit from. Treat a blue ocean as a hypothesis about a specific market and person, not a guarantee or a universal occupation label. Optimize relative entry advantage and durable options alongside demand growth.

## Resume-to-report default

When given only a resume, proceed from that file to a report without an onboarding questionnaire. Read `references/resume-intake.md` to extract capabilities, resolve missing preferences through explicit provisional scenarios, and avoid sending personal resume data into web searches. Accept attached/authorized PDF, DOCX, TXT, Markdown, or pasted resume text. Use available document parsing and OCR tools; flag unreadable or ambiguous sections instead of inventing facts.

Produce a short in-chat conclusion plus, when file creation is available, a Markdown report, claim-level evidence CSV, and run-manifest JSON. Follow the environment's persistence rules for those user deliverables. Keep case files outside the reusable skill. Offer PDF/DOCX only when requested or clearly useful and supported; do not let optional formatting block the report.

Treat current user instructions as authoritative; do not silently merge someone else's history into the supplied resume. If no resume was supplied for an actual report request, ask for the file or pasted text. Do not ask for a resume merely to update or explain this skill.

## Freshness is a required execution step

Read `references/live-research.md` for every resume-to-report run. Perform fresh searches and open relevant market sources during that invocation. Recheck the employer pages used for current-opportunity recommendations. Reuse older reports as baselines, not as fresh evidence. Keep publication date, data reference period, and inspection timestamp separate.

Describe realtime as a checked snapshot at report generation, not streaming or guaranteed instantaneous hiring data. Do not imply that public search covers every vacancy or grants access to proprietary data. Do not initiate recurring monitoring without a separate request.

Record run start/end timestamps, research status, source access status, source references, and resume extraction quality using `assets/run-manifest-template.json`. Use live / partial / offline honestly. If live search is unavailable, still provide the capability analysis and provisional hypotheses, but label the report as lacking live market verification; do not call it a realtime market report or assert current openings.

When Python execution is available, run `scripts/audit_run.py` on the completed manifest before delivery. Correct timestamp/reference/status errors. Explain unresolved coverage warnings in the report. Passing this metadata audit does not verify source content or prove market claims; inspect and cite the actual sources separately.

## Establish scope and capability evidence

1. Extract the objective, target entry date, candidate regions, career level, acceptable job conditions, learning budget, and hard constraints from available user context. Separate user statements, demonstrated evidence, assistant inferences, and unknowns. Use only relevant personal context. Do not embed a particular user's identity or profile in this skill.
2. Reuse information already provided. For resume-only runs, use the provisional-scenario defaults in `references/resume-intake.md` and continue to a report; reserve clarification for a missing/unreadable resume or conflicting identity/target instructions that prevent a meaningful analysis. If region or horizon is unknown, label the uncertainty rather than silently assuming the US or presenting a global ranking.
3. Inventory task-level capabilities, evidence, practical resources, and learning prerequisites. Distinguish exposed / assisted practice / independent delivery / complex problem-solving. Preserve self-reported skills as self-reported. Treat an omitted CV skill as unverified, not absent. Treat research interests as interests, not demonstrated expertise.
4. Separate a preparation horizon from a forecast horizon. Do not use current vacancies as a confident forecast of demand several years later. Use present hiring to identify capabilities and scenarios; express future conclusions conditionally.

Use `assets/profile-template.json` when a structured profile will help. Leave unknown values null; avoid making the user fill every field before work starts.

## Generate and screen opportunity hypotheses

Search in both directions:
- Map existing capabilities to adjacent business tasks and occupations.
- Identify structural changes creating paid problems, then find where existing or learnable capabilities overlap.

Start with roughly 8–12 hypotheses when the scope is broad; vary depth to the request and evidence. Include both close transitions and a few plausible longer moves when consistent with user constraints. Do not lock the person into their present research specialty or recommend the same specialty by default.

Define each comparison unit as **region + entry level + buyer/application + critical task**. Group equivalent job titles by their actual work. Keep nearby market variants visible so an excessively narrow definition does not manufacture a blue ocean.

For each hypothesis, identify the buyer, problem, funded work, relevant employers, plausible entry role, why demand might grow, why qualified supply might lag, personal advantage, missing prerequisites, and a falsifying observation. Treat cross-disciplinary combinations as valuable only when the same role benefits from integrating the skills.

Shortlist candidates for deeper research rather than treating the initial list as a recommendation.

## Research demand, supply, and capture of value

Read `references/evidence-protocol.md` before making market comparisons. Fresh web research is required for a live market report; use relevant connected sources when available. Keep a source ledger using `assets/evidence-ledger.csv`; cite claims in the final response using the environment's supported citation format. Label unavailable live retrieval as a degraded run rather than silently substituting model memory.

For each serious candidate, trace:
**business change → paying customer or funded obligation → employer investment → required tasks → hiring at the target level.**

Evaluate these dimensions separately:

| Dimension | Evaluate |
| --- | --- |
| Demand level and growth | Distinct employers, suitable openings, absolute additions, growth rate, repeated periods, and business evidence. Separate net expansion from replacement hiring. |
| Qualified supply | Existing practitioners, adjacent entrants, graduates, geographic mobility, and employer substitutes. Triangulate scarcity; do not infer it from applicants or vacancies alone. |
| Value capture | Whether employers pay for the capability, role responsibility, conditions, bargaining position, and employer concentration. Industry growth need not create good jobs. |
| Personal entry | Critical skills and prerequisites, formal eligibility, credible proof, data/equipment access, practical experience, and a plausible route to the target level. |
| Timing | Preparation time, adoption timing, and time for competitors or tools to fill the gap. State uncertain ranges and assumptions instead of inventing dates. |
| Durability and options | Capability transfer across employers, tasks, locations, and changing tools or models; automation, outsourcing, and standardization exposure. |

Count job advertisements as advertisements unless the source establishes headcount. Distinguish an industry, occupation, task, and skill. Do not apply industry growth or an aggregate shortage ratio to a narrow specialty or individual offer odds.

Label source status precisely: inspected live employer description, indexed description only, archived/closed position, aggregate report, interview, or user-supplied material. Use senior-role requirements to study future capability needs, not as evidence that entry-level vacancies exist. Treat an umbrella new-graduate posting as several possible work streams rather than requiring every listed specialization.

When historical or supply data are unavailable, deliver a qualitative, conditional shortlist and a data-collection plan. Do not manufacture growth rates, scarcity, salaries, applicant quality, or population estimates from a convenience sample. Do not claim access to proprietary labor-market databases unless access actually exists.

## Decide with gates and explicit uncertainty

Apply necessary conditions before any ranking:
- Identify paid demand or a credible funded path.
- Establish a feasible entry route within the person's preparation constraints.
- Check that formal and practical barriers are satisfiable in time.
- Check that job conditions meet the person's stated minimums.

Mark every gate pass / fail / unknown with an explanation. A remediable skill gap is not an automatic failure. A failed hard gate cannot be compensated by high growth. A critical unknown prevents a high-confidence recommendation; keep the option under observation or give a clearly conditional exploration recommendation.

Compare market attractiveness and personal entry advantage separately. Use justified ordinal judgments, not arbitrary weighted totals or invented probabilities. Keep evidence confidence separate from attractiveness. Do not treat missing evidence as a low measured value.

Assign one of:
- **Prioritize / 优先验证:** credible relevant demand, plausible personal advantage, no unresolved hard blocker; specify what still needs testing.
- **Explore / 小规模探索:** promising but important evidence, timing, or capability assumptions remain unresolved.
- **Watch / 观察:** potential demand or fit exists but an essential entry or market condition is unverified or premature.
- **Deprioritize / 暂缓:** a demonstrated constraint or unfavorable tradeoff dominates; state what would change the decision.

Do not promise the single easiest, fastest-growing, or permanently uncontested career. Explain which alternatives the evidence supports, for whom, where, at what level, and over what horizon. Preserve multiple options when the evidence cannot discriminate reliably.

## Verify through low-cost experiments

For the most promising 1–3 candidates, propose a proportionate experiment with:
1. A concrete business task and observable deliverable.
2. Missing skills, dependencies, and an estimated effort range grounded in prerequisites.
3. Feedback from a relevant practitioner or recruiter, or an appropriate internship/application when the person is ready.
4. A success signal, a result that would weaken the hypothesis, and a next decision.

Use employer conversations and projects to test hypotheses, not to retroactively justify a favorite field. Draft outreach if useful, but do not send messages, apply for jobs, buy services, subscribe to paid data, or schedule ongoing monitoring without authorization for that action. Do not create artificial urgency.

## Deliver and update

For a full investigation, adapt `assets/report-template.md` to produce:
- A direct, conditional conclusion, scope, as-of date, and material assumptions.
- A freshness summary with live / partial / offline status, checked-at timestamps, source data periods, and resume extraction limitations.
- A capability/resource assessment distinguishing evidence from interest.
- Candidate comparison with market attractiveness, entry advantage, timing, confidence, and decision status.
- Evidence, counterevidence, unresolved questions, and source links for shortlisted options.
- Prioritized learning/project experiments tied to employer-valued tasks.
- Falsification and revisit triggers; compare changed evidence on updates instead of rerunning a fixed career recommendation.

Use the user's language. Explain implications rather than listing keywords or broad warnings. Show a research-based shortlist when research is requested, not merely instructions for the user to research it. Label incomplete work honestly. Say when evidence supports existence of jobs but not a market-wide ranking or shortage.

Use existing report artifacts as the baseline when updating. Do not replace user preferences with earlier assistant suggestions. Follow the environment's persistence rules for reports or datasets; keep private case data separate from this reusable skill.
