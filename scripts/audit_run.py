#!/usr/bin/env python3
"""Audit declared freshness and apply-list metadata; do not fetch sources."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

KINDS = {"employer_job", "official_statistics", "business_disclosure",
         "platform_report", "practitioner", "user_supplied", "methodology"}
RETRIEVALS = {"opened", "indexed_only", "closed", "blocked", "cached", "user_supplied"}
DECISIONS = {"prioritize", "explore", "watch", "deprioritize"}
FIRST_HAND = {"official", "ats", "primary_board", "campus"}
ELIGIBILITY_OK = {"eligible", "conditional"}
RUBRIC = [
    "first_hand_open_this_run",
    "fit_to_proven_work",
    "eligibility",
    "role_quality",
    "source_quality",
    "freshness_and_deadline",
    "retention_only_if_stated",
]
OPAQUE_SCORES = {"score", "weighted_score", "match_score", "total_score", "ranking_score"}


def read_time(value, label, errors):
    if not isinstance(value, str) or not value:
        errors.append(f"{label}: require an ISO 8601 timestamp with timezone")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("missing timezone")
        return parsed.astimezone(timezone.utc)
    except ValueError:
        errors.append(f"{label}: invalid or timezone-naive timestamp")
        return None


def audit(data):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return {"audit_status": "fail", "errors": ["manifest must be an object"],
                "warnings": [], "counts": {}, "limitation": "metadata audit only"}
    if not isinstance(data.get("run_id"), str) or not data["run_id"].strip():
        errors.append("run_id: require a nonempty identifier")
    start = read_time(data.get("started_at"), "started_at", errors)
    end = read_time(data.get("generated_at"), "generated_at", errors)
    if start and end and end < start:
        errors.append("generated_at precedes started_at")
    if not isinstance(data.get("client_timezone"), str) or not data["client_timezone"]:
        errors.append("client_timezone: require the displayed timezone")
    state = data.get("research_status")
    if state not in {"live", "partial", "offline"}:
        errors.append("research_status: expected live, partial, or offline")
    resume = data.get("resume_source")
    if not isinstance(resume, dict):
        errors.append("resume_source: require extraction metadata")
    else:
        if not resume.get("filename_or_reference"):
            errors.append("resume_source: missing authorized resume reference")
        if resume.get("extraction_status") not in {"complete", "partial", "unreadable"}:
            errors.append("resume_source: invalid extraction_status")
        elif resume["extraction_status"] != "complete":
            warnings.append("CV extraction is incomplete; disclose missing/uncertain evidence")
    sources = data.get("sources", [])
    recommendations = data.get("recommendations", [])
    if not isinstance(sources, list):
        errors.append("sources must be an array")
        sources = []
    if not isinstance(recommendations, list):
        errors.append("recommendations must be an array")
        recommendations = []
    registered, market_current, jobs_current = {}, set(), set()
    families = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"sources[{index}] must be an object")
            continue
        sid = source.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"sources[{index}]: missing source id")
            continue
        if sid in registered:
            errors.append(f"{sid}: duplicate source id")
            continue
        registered[sid] = source
        kind, retrieval = source.get("source_kind"), source.get("retrieval_status")
        if kind not in KINDS:
            errors.append(f"{sid}: invalid source_kind")
        if retrieval not in RETRIEVALS:
            errors.append(f"{sid}: invalid retrieval_status")
        checked = read_time(source.get("checked_at"), f"{sid}.checked_at", errors)
        in_run = bool(start and end and checked and start <= checked <= end)
        if checked and end and checked > end:
            errors.append(f"{sid}: checked_at is later than report generation")
        if retrieval in {"opened", "indexed_only", "closed", "blocked"} and not in_run:
            errors.append(f"{sid}: retrieval was not checked within this run; use cached if reused")
        if retrieval in {"opened", "indexed_only", "closed"}:
            url = urlparse(source.get("url") or "")
            if url.scheme not in {"http", "https"} or not url.netloc:
                errors.append(f"{sid}: inspected/indexed web source requires an http(s) URL")
        is_market = kind in KINDS - {"methodology", "user_supplied"}
        if in_run and retrieval in {"opened", "closed"} and is_market:
            market_current.add(sid)
            if source.get("source_family"):
                families.add(source["source_family"])
            else:
                warnings.append(f"{sid}: missing source family; independence is unverified")
        if kind == "employer_job":
            availability = source.get("advertised_status")
            if availability not in {"open", "closed", "unknown", "not_applicable"}:
                errors.append(f"{sid}: invalid advertised_status")
            if availability == "open" and retrieval == "closed":
                errors.append(f"{sid}: a closed retrieval cannot support advertised open status")
            if sid in market_current and retrieval == "opened" and availability == "open":
                jobs_current.add(sid)
                if not source.get("geography") or not source.get("career_level"):
                    warnings.append(f"{sid}: record job geography and level before using it for fit")
        if kind in {"official_statistics", "platform_report"} and not source.get("reference_period"):
            warnings.append(f"{sid}: data reference period unknown; do not imply fresh observations")
        if retrieval in {"indexed_only", "blocked", "cached"}:
            warnings.append(f"{sid}: {retrieval} evidence is not an inspected current source")
    if state in {"live", "partial"} and not market_current:
        errors.append("No freshly inspected market sources; research_status must be offline")
    if state == "offline":
        warnings.append("No realtime market report: keep market conclusions provisional")
    if market_current and len(families) < 2:
        warnings.append("Current market evidence lacks multiple identified source families")
    candidate_ids = set()
    for index, rec in enumerate(recommendations):
        if not isinstance(rec, dict):
            errors.append(f"recommendations[{index}] must be an object")
            continue
        cid = rec.get("candidate_id")
        if not isinstance(cid, str) or not cid.strip() or cid in candidate_ids:
            errors.append(f"recommendations[{index}]: missing or duplicate candidate_id")
        else:
            candidate_ids.add(cid)
        if rec.get("status") not in DECISIONS:
            errors.append(f"{cid}: invalid decision status")
        if rec.get("claim_kind") not in {"current_opportunity", "long_term_option"}:
            errors.append(f"{cid}: invalid claim_kind")
        if rec.get("confidence") not in {"low", "moderate", "high"}:
            errors.append(f"{cid}: invalid confidence")
        refs = rec.get("source_ids", [])
        if not isinstance(refs, list) or any(not isinstance(s, str) for s in refs):
            errors.append(f"{cid}: source_ids must be an array of strings")
            refs = []
        for sid in refs:
            if sid not in registered:
                errors.append(f"{cid}: unknown source id {sid}")
        if rec.get("status") == "prioritize" and rec.get("claim_kind") == "current_opportunity":
            if state == "offline" or not jobs_current.intersection(refs):
                errors.append(f"{cid}: current priority needs an inspected advertised-open employer job")
        if not refs:
            warnings.append(f"{cid}: no source links; label as a CV-based hypothesis")
        if rec.get("claim_kind") == "current_opportunity" and rec.get("status") in {"prioritize", "explore"}:
            opened = [registered.get(sid) for sid in refs]
            if not any(_opened_http_source(source, start, end) for source in opened):
                reprint_only = any(isinstance(source, dict) and source.get("source_quality") == "reprint"
                                   and source.get("retrieval_status") == "opened" for source in opened)
                if reprint_only:
                    errors.append(f"{cid}: a current-opportunity claim cannot rest on a reprint; open and cite the original")
                else:
                    errors.append(f"{cid}: a current-opportunity claim needs a source opened at an http(s) URL this run")
    flagged = _flagged_current_jobs(registered, start, end, errors)
    job_count, first_hand = audit_apply_list(
        data, errors, warnings, registered, start, end, state, jobs_current, flagged)
    return {"audit_status": "fail" if errors else "pass", "errors": errors,
            "warnings": warnings,
            "counts": {"sources": len(registered), "fresh_market_sources": len(market_current),
                       "fresh_advertised_open_jobs": len(jobs_current),
                       "identified_current_source_families": len(families),
                       "recommended_jobs": job_count,
                       "first_hand_recommended_jobs": first_hand},
            "limitation": "Checks declared metadata only; does not fetch sources, open postings, or verify claim truth"}


def _opened_http_source(source, start, end):
    if not isinstance(source, dict) or source.get("retrieval_status") != "opened":
        return False
    if source.get("source_quality") == "reprint":
        return False
    checked = read_time(source.get("checked_at"), "unused", [])
    if not (start and end and checked and start <= checked <= end):
        return False
    url = urlparse(source.get("url") or "")
    return url.scheme in {"http", "https"} and bool(url.netloc)


def _flagged_current_jobs(registered, start, end, errors):
    flagged = set()
    for sid, source in registered.items():
        if source.get("currently_recommended") is not True:
            continue
        flagged.add(sid)
        problems = []
        if source.get("retrieval_status") != "opened" or source.get("advertised_status") != "open":
            problems.append(f"{sid}: closed or unverified job is marked currently_recommended")
        checked = read_time(source.get("checked_at"), f"{sid}.checked_at", [])
        if not (start and end and checked and start <= checked <= end):
            problems.append(f"{sid}: currently recommended job lacks a check timestamp inside this run")
        url = urlparse(source.get("url") or "")
        if url.scheme not in {"http", "https"} or not url.netloc:
            problems.append(f"{sid}: currently recommended job lacks a first-hand http(s) URL")
        if source.get("source_quality") == "reprint":
            problems.append(f"{sid}: a reprint cannot be marked currently_recommended")
        errors.extend(problems)
    return flagged


def audit_apply_list(data, errors, warnings, registered, start, end, state, jobs_current, flagged):
    has_jobs = "recommended_jobs" in data
    has_search = "job_search" in data
    if not has_jobs:
        if state in {"live", "partial"}:
            if has_search:
                errors.append("job_search is present but recommended_jobs is missing")
            else:
                warnings.append(
                    "recommended_jobs is absent; declare the verified apply list or an explicit shortfall"
                )
        _missing_from_apply_list(flagged, set(), errors)
        return 0, 0
    jobs = data.get("recommended_jobs")
    if not isinstance(jobs, list):
        errors.append("recommended_jobs must be an array")
        _missing_from_apply_list(flagged, set(), errors)
        return 0, 0
    search = data.get("job_search")
    if search is None:
        search = {}
    elif not isinstance(search, dict):
        errors.append("job_search must be an object when provided")
        search = {}
    if state == "offline" and jobs:
        errors.append("offline run cannot mark jobs as currently recommended")
    if len(jobs) > 10:
        errors.append("recommended_jobs: at most 10 currently recommended postings; do not pad")
    if state in {"live", "partial"} and len(jobs) < 10:
        reason = search.get("shortfall_reason") if isinstance(search, dict) else None
        if not isinstance(reason, str) or not reason.strip():
            errors.append("recommended_jobs: fewer than 10 verified openings requires job_search.shortfall_reason")
    if isinstance(search, dict):
        if "target_count" in search and search.get("target_count") not in (None, 10):
            errors.append("job_search.target_count must be 10")
        count = search.get("verified_open_count") if "verified_open_count" in search else None
        if "verified_open_count" in search and count is not None and (isinstance(count, bool) or not isinstance(count, int)):
            errors.append("job_search.verified_open_count must be an integer or null")
        elif isinstance(count, int) and not isinstance(count, bool) and count != len(jobs):
            errors.append("job_search.verified_open_count must equal the number of recommended_jobs")
        rubric = search.get("ranking_rubric") if "ranking_rubric" in search else None
        if "ranking_rubric" in search and rubric != RUBRIC:
            errors.append("job_search.ranking_rubric must be the written rubric, in order, with no invented score")
        elif state in {"live", "partial"} and jobs and "ranking_rubric" not in search:
            warnings.append("job_search.ranking_rubric is absent; apply the written rubric rather than a new score")
        for key in OPAQUE_SCORES:
            if search.get(key) not in (None, False):
                errors.append(f"job_search: do not attach an opaque {key}")
        boards = search.get("boards_searched") if "boards_searched" in search else None
        if "boards_searched" in search and (not isinstance(boards, list) or not boards):
            warnings.append("job_search.boards_searched is empty; name the career sites and boards opened this run")
    excluded_ids = set()
    excluded = data.get("excluded_jobs", [])
    if excluded is None:
        excluded = []
    if "excluded_jobs" in data and not isinstance(excluded, list):
        errors.append("excluded_jobs must be an array")
        excluded = []
    for index, item in enumerate(excluded):
        if not isinstance(item, dict):
            errors.append(f"excluded_jobs[{index}] must be an object")
            continue
        sid = item.get("source_id")
        if isinstance(sid, str) and sid.strip():
            excluded_ids.add(sid)
        else:
            warnings.append(f"excluded_jobs[{index}]: missing source_id")
    seen_ranks, seen_ids, seen_urls, recommended_sources = set(), set(), set(), set()
    first_hand = 0
    for index, job in enumerate(jobs):
        problems = []
        label = f"recommended_jobs[{index}]"
        if not isinstance(job, dict):
            errors.append(f"{label} must be an object")
            continue
        jid = job.get("job_id")
        if not isinstance(jid, str) or not jid.strip() or jid in seen_ids:
            problems.append(f"{label}: missing or duplicate job_id")
        else:
            seen_ids.add(jid)
            label = jid
        rank = job.get("rank")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1 or rank > 10 or rank in seen_ranks:
            problems.append(f"{label}: rank must be a unique integer from 1 to 10")
        else:
            seen_ranks.add(rank)
        if job.get("currently_recommended") is False:
            problems.append(f"{label}: currently_recommended false does not belong in recommended_jobs")
        for field in ("employer", "title"):
            if not isinstance(job.get(field), str) or not job[field].strip():
                problems.append(f"{label}: require nonempty {field}")
        name = job.get("source_name")
        if not isinstance(name, str) or not name.strip():
            problems.append(f"{label}: require a source_name (publisher or board, not only a URL)")
        elif name.strip().lower().startswith(("http://", "https://")):
            problems.append(f"{label}: source_name must be a publisher or board name, not a URL")
        reason = job.get("rank_reason")
        if not isinstance(reason, str) or len(reason.strip()) < 12:
            problems.append(f"{label}: rank_reason must be one or two sentences specific to this person")
        quality = job.get("source_quality")
        if quality not in FIRST_HAND:
            problems.append(
                f"{label}: source_quality must be first-hand (official, ats, primary_board, campus); reprints are leads only"
            )
        eligibility = job.get("eligibility")
        if eligibility not in ELIGIBILITY_OK:
            problems.append(f"{label}: ineligible or class-year-mismatched postings cannot be currently recommended")
        for field in ("published_at", "deadline"):
            value = job.get(field, None)
            if field in job and value is not None and (not isinstance(value, str) or not value.strip()):
                problems.append(f"{label}: {field} must be a date string or null")
        for key in OPAQUE_SCORES:
            if key in job and job.get(key) is not None:
                problems.append(f"{label}: do not attach an opaque {key}; rank with the written rubric")
        checked = read_time(job.get("checked_at"), f"{label}.checked_at", problems)
        if checked and not (start and end and start <= checked <= end):
            problems.append(f"{label}: checked_at is outside this run")
        apply_url = job.get("apply_url")
        apply_url = apply_url.strip() if isinstance(apply_url, str) else ""
        parsed = urlparse(apply_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            problems.append(f"{label}: require a first-hand http(s) apply_url")
        elif apply_url in seen_urls:
            problems.append(f"{label}: duplicate apply_url in recommended_jobs")
        else:
            seen_urls.add(apply_url)
        if job.get("retrieval_status") not in (None, "opened"):
            problems.append(f"{label}: unverified retrieval cannot be currently recommended")
        if job.get("advertised_status") not in (None, "open"):
            problems.append(f"{label}: closed or unconfirmed postings cannot be currently recommended")
        sid = job.get("source_id")
        source = registered.get(sid) if isinstance(sid, str) else None
        if not isinstance(sid, str) or source is None:
            problems.append(f"{label}: source_id must reference a registered source")
        else:
            recommended_sources.add(sid)
            if sid in excluded_ids:
                problems.append(f"{label}: excluded, closed, unverified, or reprint-only sources cannot be currently recommended")
            if source.get("source_kind") != "employer_job":
                problems.append(f"{label}: recommended job must cite an employer_job source")
            if source.get("retrieval_status") != "opened":
                problems.append(f"{label}: unverified retrieval cannot be currently recommended")
            if source.get("advertised_status") != "open":
                problems.append(f"{label}: closed or unconfirmed postings cannot be currently recommended")
            if sid not in jobs_current:
                problems.append(f"{label}: source was not freshly inspected as advertised-open in this run")
            source_url = source.get("url") or ""
            source_url = source_url.strip() if isinstance(source_url, str) else ""
            if apply_url and source_url and apply_url != source_url:
                problems.append(f"{label}: apply_url must be the opened first-hand posting URL")
            source_quality = source.get("source_quality")
            if source_quality is not None and source_quality != quality:
                problems.append(f"{label}: source_quality contradicts the registered source")
            if source_quality == "reprint":
                problems.append(f"{label}: a reprint cannot be currently recommended")
        errors.extend(problems)
        if not problems:
            first_hand += 1
    if seen_ranks and seen_ranks != set(range(1, len(seen_ranks) + 1)):
        errors.append("recommended_jobs: ranks must be contiguous starting at 1")
    _missing_from_apply_list(flagged, recommended_sources, errors)
    return len(jobs), first_hand


def _missing_from_apply_list(flagged, recommended_sources, errors):
    for sid in flagged:
        if sid not in recommended_sources:
            errors.append(f"{sid}: marked currently_recommended but omitted from recommended_jobs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out", type=Path, help="Optional JSON audit output path")
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"audit_status": "fail", "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    result = audit(data)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
