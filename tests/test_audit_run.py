"""Regression scenarios using synthetic metadata, not real market evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_run", ROOT / "scripts" / "audit_run.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    return {
        "run_id": "synthetic-test",
        "started_at": "2026-11-26T10:00:00Z",
        "generated_at": "2026-11-26T10:20:00Z",
        "client_timezone": "Asia/Shanghai",
        "research_status": "live",
        "resume_source": {"filename_or_reference": "synthetic-cv.txt",
                          "extraction_status": "complete", "unreadable_sections": []},
        "sources": [{"id": "S1", "source_kind": "employer_job",
                     "source_family": "synthetic-employer",
                     "url": "https://example.invalid/jobs/123",
                     "published_at": "2024-01-01", "reference_period": None,
                     "checked_at": "2026-11-26T18:05:00+08:00",
                     "retrieval_status": "opened", "advertised_status": "open",
                     "geography": "Example region", "career_level": "early"}],
        "recommendations": [{"candidate_id": "C1", "status": "prioritize",
                             "claim_kind": "current_opportunity", "confidence": "moderate",
                             "source_ids": ["S1"]}],
    }


class FreshnessAuditTests(unittest.TestCase):
    def test_old_publication_can_be_rechecked_as_open(self):
        result = MODULE.audit(fixture())
        self.assertEqual(result["audit_status"], "pass")
        self.assertEqual(result["counts"]["fresh_advertised_open_jobs"], 1)

    def test_equivalent_timezone_instants(self):
        data = fixture()
        data["sources"][0]["checked_at"] = "2026-11-26T10:05:00Z"
        self.assertEqual(MODULE.audit(data)["audit_status"], "pass")

    def test_old_inspection_cannot_be_relabelled_current(self):
        data = fixture()
        data["sources"][0]["checked_at"] = "2026-11-26T09:59:59Z"
        self.assertEqual(MODULE.audit(data)["audit_status"], "fail")

    def test_search_index_is_not_live_inspection(self):
        data = fixture()
        data["sources"][0]["retrieval_status"] = "indexed_only"
        self.assertEqual(MODULE.audit(data)["audit_status"], "fail")

    def test_unregistered_source_reference(self):
        data = fixture()
        data["recommendations"][0]["source_ids"] = ["missing-source"]
        self.assertEqual(MODULE.audit(data)["audit_status"], "fail")

    def test_closed_job_cannot_support_current_priority(self):
        data = fixture()
        data["sources"][0].update(retrieval_status="closed", advertised_status="closed")
        self.assertEqual(MODULE.audit(data)["audit_status"], "fail")

    def test_methods_paper_is_not_market_coverage(self):
        data = fixture()
        data["sources"][0]["source_kind"] = "methodology"
        data["recommendations"] = []
        self.assertEqual(MODULE.audit(data)["audit_status"], "fail")

    def test_offline_hypothesis_and_partial_resume_are_honest(self):
        data = fixture()
        data.update(research_status="offline", sources=[])
        data["resume_source"]["extraction_status"] = "partial"
        data["recommendations"][0].update(status="explore", claim_kind="long_term_option",
                                          confidence="low", source_ids=[])
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "pass")
        self.assertGreater(len(result["warnings"]), 0)

    def test_duplicate_source_ids(self):
        data = fixture()
        data["sources"].append(copy.deepcopy(data["sources"][0]))
        self.assertEqual(MODULE.audit(data)["audit_status"], "fail")

    def test_timezone_required(self):
        data = fixture()
        data["sources"][0]["checked_at"] = "2026-11-26T10:05:00"
        self.assertEqual(MODULE.audit(data)["audit_status"], "fail")

    def test_inspection_cannot_follow_report_generation(self):
        data = fixture()
        data["sources"][0]["checked_at"] = "2026-11-26T10:25:00Z"
        self.assertEqual(MODULE.audit(data)["audit_status"], "fail")

    def test_lagged_statistics_can_be_inspected_now(self):
        data = fixture()
        data.update(research_status="partial", recommendations=[])
        data["sources"][0].update(source_kind="official_statistics", reference_period="2025 H1")
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "pass")
        self.assertEqual(result["counts"]["fresh_advertised_open_jobs"], 0)

    def test_cli_outputs_parseable_audit(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "manifest.json"
            manifest.write_text(json.dumps(fixture()), encoding="utf-8")
            run = subprocess.run([sys.executable, str(ROOT / "scripts" / "audit_run.py"),
                                  str(manifest)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["audit_status"], "pass")


RUBRIC = [
    "first_hand_open_this_run",
    "fit_to_proven_work",
    "eligibility",
    "role_quality",
    "source_quality",
    "freshness_and_deadline",
    "retention_only_if_stated",
]


def recommended_job(**overrides):
    item = {
        "rank": 1,
        "job_id": "J1",
        "employer": "Example Employer",
        "title": "Example analyst",
        "source_id": "S1",
        "source_name": "Example Employer careers",
        "source_quality": "official",
        "apply_url": "https://example.invalid/jobs/123",
        "published_at": "2026-11-01",
        "deadline": "2026-12-15",
        "checked_at": "2026-11-26T18:05:00+08:00",
        "eligibility": "eligible",
        "rank_reason": "The resume already shows the task this posting asks an early hire to do.",
    }
    item.update(overrides)
    return item


def with_job(**overrides):
    data = fixture()
    data["recommendations"] = [{
        "candidate_id": "C1", "status": "explore", "claim_kind": "long_term_option",
        "confidence": "low", "source_ids": ["S1"],
    }]
    data["job_search"] = {
        "target_count": 10,
        "verified_open_count": 1,
        "shortfall_reason": "Only one posting was first-hand verified as open and relevant in this run.",
        "ranking_rubric": list(RUBRIC),
        "boards_searched": ["Example Employer careers"],
    }
    data["recommended_jobs"] = [recommended_job(**overrides)]
    return data


class ApplyListAuditTests(unittest.TestCase):
    def test_first_hand_open_job_passes(self):
        result = MODULE.audit(with_job())
        self.assertEqual(result["audit_status"], "pass", result["errors"])
        self.assertEqual(result["counts"]["first_hand_recommended_jobs"], 1)

    def test_named_primary_channels_pass(self):
        for quality, name in (
            ("ats", "Example ATS"),
            ("primary_board", "Example job board"),
            ("campus", "Example campus careers"),
        ):
            result = MODULE.audit(with_job(source_quality=quality, source_name=name))
            self.assertEqual(result["audit_status"], "pass", result["errors"])

    def test_missing_apply_url_fails(self):
        result = MODULE.audit(with_job(apply_url=""))
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("apply_url" in item for item in result["errors"]))

    def test_missing_check_timestamp_fails(self):
        result = MODULE.audit(with_job(checked_at=None))
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("checked_at" in item for item in result["errors"]))

    def test_check_timestamp_outside_run_fails(self):
        result = MODULE.audit(with_job(checked_at="2026-11-26T09:00:00Z"))
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("outside this run" in item for item in result["errors"]))

    def test_closed_job_cannot_be_currently_recommended(self):
        data = with_job()
        data["sources"][0].update(retrieval_status="closed", advertised_status="closed")
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("cannot be currently recommended" in item for item in result["errors"]))

    def test_indexed_job_cannot_be_currently_recommended(self):
        data = with_job()
        data["sources"].append({
            "id": "S2", "source_kind": "official_statistics", "source_family": "synthetic-stats",
            "url": "https://example.invalid/stats", "reference_period": "2025",
            "checked_at": "2026-11-26T10:05:00Z", "retrieval_status": "opened",
        })
        data["sources"][0].update(retrieval_status="indexed_only", advertised_status="unknown")
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("unverified" in item or "unconfirmed" in item for item in result["errors"]))

    def test_current_claim_cannot_rest_on_a_reprint(self):
        data = fixture()
        data["sources"][0]["source_quality"] = "reprint"
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("reprint" in item for item in result["errors"]))

    def test_reprint_cannot_be_recommended(self):
        result = MODULE.audit(with_job(source_quality="reprint", source_name="Example reprint"))
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("reprint" in item.lower() or "first-hand" in item for item in result["errors"]))

    def test_reprint_flag_on_source_fails_even_if_job_says_official(self):
        data = with_job()
        data["sources"][0]["source_quality"] = "reprint"
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "fail")

    def test_class_year_mismatch_cannot_be_recommended(self):
        result = MODULE.audit(with_job(eligibility="ineligible"))
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("cannot be currently recommended" in item for item in result["errors"]))

    def test_short_list_without_reason_fails(self):
        data = with_job()
        data["job_search"]["shortfall_reason"] = " "
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("shortfall_reason" in item for item in result["errors"]))

    def test_empty_verified_list_with_reason_passes(self):
        data = fixture()
        data.update(research_status="partial", recommendations=[])
        data["sources"][0].update(source_kind="official_statistics", reference_period="2025 H1")
        data["recommended_jobs"] = []
        data["job_search"] = {
            "target_count": 10, "verified_open_count": 0,
            "shortfall_reason": "No posting could be opened as currently accepting applications.",
            "ranking_rubric": list(RUBRIC),
        }
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "pass", result["errors"])
        self.assertEqual(result["counts"]["recommended_jobs"], 0)

    def test_more_than_ten_is_padding(self):
        data = with_job()
        data["recommended_jobs"] = [
            recommended_job(rank=index, job_id="J{}".format(index),
                            apply_url="https://example.invalid/jobs/{}".format(index))
            for index in range(1, 12)
        ]
        data["job_search"]["verified_open_count"] = 11
        data["job_search"]["shortfall_reason"] = None
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("at most 10" in item for item in result["errors"]))

    def test_offline_cannot_recommend_current_jobs(self):
        data = with_job()
        data["research_status"] = "offline"
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("offline" in item for item in result["errors"]))

    def test_apply_url_must_match_opened_source(self):
        result = MODULE.audit(with_job(apply_url="https://example.invalid/other"))
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("opened first-hand" in item for item in result["errors"]))

    def test_gap_in_ranks_fails(self):
        data = with_job()
        data["sources"].append(copy.deepcopy(data["sources"][0]))
        data["sources"][1].update(id="S2", url="https://example.invalid/jobs/456",
                                  source_family="synthetic-employer-b")
        data["recommended_jobs"].append(recommended_job(
            rank=3, job_id="J3", source_id="S2", apply_url="https://example.invalid/jobs/456"))
        data["job_search"]["verified_open_count"] = 2
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("contiguous" in item for item in result["errors"]))

    def test_missing_source_name_and_reason_fail(self):
        result = MODULE.audit(with_job(source_name=" ", rank_reason="good"))
        self.assertEqual(result["audit_status"], "fail")
        text = "\n".join(result["errors"])
        self.assertIn("source_name", text)
        self.assertIn("rank_reason", text)

    def test_opaque_score_fails(self):
        result = MODULE.audit(with_job(score=91))
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("opaque" in item for item in result["errors"]))

    def test_changed_rubric_fails(self):
        data = with_job()
        data["job_search"]["ranking_rubric"] = ["vibes"]
        self.assertEqual(MODULE.audit(data)["audit_status"], "fail")

    def test_excluded_source_cannot_also_be_recommended(self):
        data = with_job()
        data["excluded_jobs"] = [{"source_id": "S1", "reason_code": "closed", "note": "filled"}]
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("excluded" in item for item in result["errors"]))

    def test_flagged_closed_source_fails_without_apply_list(self):
        data = fixture()
        data["sources"][0]["currently_recommended"] = True
        data["sources"][0].update(retrieval_status="closed", advertised_status="closed")
        data["recommendations"] = [{
            "candidate_id": "C1", "status": "explore", "claim_kind": "long_term_option",
            "confidence": "low", "source_ids": ["S1"],
        }]
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("currently_recommended" in item for item in result["errors"]))

    def test_live_manifest_without_apply_keys_still_passes_with_warning(self):
        result = MODULE.audit(fixture())
        self.assertEqual(result["audit_status"], "pass")
        self.assertTrue(any("recommended_jobs is absent" in item for item in result["warnings"]))

    def test_job_search_without_list_fails(self):
        data = fixture()
        data["job_search"] = {"target_count": 10}
        result = MODULE.audit(data)
        self.assertEqual(result["audit_status"], "fail")
        self.assertTrue(any("recommended_jobs is missing" in item for item in result["errors"]))


class TemplateContractTests(unittest.TestCase):
    def test_html_is_self_contained_and_print_ready(self):
        html = (ROOT / "assets" / "report-template.html").read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn('id="apply-list"', html)
        self.assertIn("@media print", html)
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("<link", html.lower())
        self.assertNotIn("南开", html)
        self.assertNotIn("国泰海通", html)

    def test_skill_keeps_name_search_step_and_rubric(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: find-career-opportunities", skill)
        self.assertIn("「找岗可投岗位」", skill)
        self.assertIn("first_hand_open_this_run", skill)
        self.assertNotIn("南开大学", skill)

    def test_readme_states_html_top10_and_sources(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("单文件 HTML", readme)
        self.assertIn("10", readme)
        self.assertIn("一手", readme)
        self.assertIn("English overview", readme)


if __name__ == "__main__":
    unittest.main()
