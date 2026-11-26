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


if __name__ == "__main__":
    unittest.main()
