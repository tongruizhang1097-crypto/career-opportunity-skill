#!/usr/bin/env python3
"""Audit declared freshness metadata; do not fetch or validate source content."""
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
    return {"audit_status": "fail" if errors else "pass", "errors": errors,
            "warnings": warnings,
            "counts": {"sources": len(registered), "fresh_market_sources": len(market_current),
                       "fresh_advertised_open_jobs": len(jobs_current),
                       "identified_current_source_families": len(families)},
            "limitation": "Checks declared metadata only; does not fetch sources or verify claim truth"}


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
