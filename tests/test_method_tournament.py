"""MOTIF Method Tournament 003: boundaries and hard scientific falsifiers."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from unittest.mock import patch

from motif.branch_garden import HoldError, Pointer
from motif.method_tournament import (
    PROFILE, RECEIPT_SCHEMA, _digest, _verified_scorecard,
    assemble_held_receipt, run, verify_receipt, select_reviewed_source,
    FIXTURE, EVALUATOR,
)


class MethodTournamentTests(unittest.TestCase):
    def setUp(self):
        self.source = Pointer(PROFILE["source_branch"], "a" * 40)
        self.signals = {
            "document_terms_matched": ["reciprocal"],
            "source_witnesses": [{
                "path": PROFILE["source_docs"][0], "sha256": "b" * 64,
                "bytes": 120, "code_executed": False
            }]
        }
        self.score = {
            "schema": "motif.method-tournament-scorecard/v1",
            "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "original_native_algorithm_executed": True,
            "independent_future_separate_from_candidate_input": True,
            "independent_strong_baseline_implemented": True,
            "reliable_improvement_over_strong_classical": False,
            "disposition": "RETAIN_SOURCE_POINTER_HELD_NOT_INSTALL",
            "automatic_merge": False,
            "external_action": False,
            "real_human_reports": False,
            "cases": [{"case_id": f"synthetic-{i}"} for i in range(6)],
            "aggregate_on_proposed_only": {
                "candidate_minus_strong_correct": 0,
                "cases_regressing_vs_global": ["inverted-role-signal"],
            },
        }

    def test_fixture_is_originally_frozen_synthetic_and_contains_negative_cases(self):
        raw = json.loads(FIXTURE.read_text())
        self.assertEqual(raw["sample_kind"], "AUTHORED_SYNTHETIC_NO_HUMANS")
        self.assertEqual(len(raw["cases"]), 6)
        self.assertIn("inverted-role-signal", [c["id"] for c in raw["cases"]])
        self.assertIn("collapsed-context-signal", [c["id"] for c in raw["cases"]])
        self.assertIn("no-useful-role-signal", [c["id"] for c in raw["cases"]])
        self.assertIn("role", EVALUATOR.read_text())

    def test_retained_receipt_is_inert_and_source_scoped(self):
        receipt = assemble_held_receipt(
            self.source, self.signals, self.score, self.score["fixture_sha256"])
        data = verify_receipt(receipt)
        self.assertEqual(data["source_commit"], "a" * 40)
        self.assertEqual(data["retained_kind"], "HELD_CONTENT_ADDRESSED_SOURCE_LOCATOR")
        self.assertFalse(data["method_installed"])
        self.assertFalse(data["automatic_merge"])
        self.assertFalse(data["real_world_transfer_proven"])
        self.assertFalse(data["independent_strong_control_won"])
        self.assertTrue(data["operator_review_required"])

    def test_retention_detects_mutation_but_hash_is_not_an_authentic_signature(self):
        receipt = assemble_held_receipt(
            self.source, self.signals, self.score, self.score["fixture_sha256"])
        self.assertTrue(receipt["digest_is_not_authenticity"])
        bad = copy.deepcopy(receipt)
        bad["content"]["method_installed"] = True
        with self.assertRaises(HoldError):
            verify_receipt(bad)
        bad["content_sha256"] = _digest(bad["content"])
        with self.assertRaises(HoldError):
            verify_receipt(bad)

    def test_wrong_source_authority_rejected(self):
        receipt = assemble_held_receipt(
            self.source, self.signals, self.score, self.score["fixture_sha256"])
        for name, val in [
            ("automatic_merge", True), ("source_branch", "main"),
            ("real_world_transfer_proven", True),
            ("independent_strong_control_won", True),
        ]:
            bad = copy.deepcopy(receipt)
            bad["content"][name] = val
            bad["content_sha256"] = _digest(bad["content"])
            with self.assertRaises(HoldError, msg=name):
                verify_receipt(bad)

    def test_independent_score_must_include_adverse_transfer_and_strong_control(self):
        raw = "MOTIF_TOURNAMENT_RESULT " + json.dumps(self.score)
        self.assertEqual(
            _verified_scorecard(raw, self.score["fixture_sha256"])["schema"],
            self.score["schema"])
        for changed in [
            {"reliable_improvement_over_strong_classical": True},
            {"automatic_merge": True},
            {"real_human_reports": True},
            {"independent_future_separate_from_candidate_input": False},
        ]:
            payload = {**self.score, **changed}
            with self.assertRaises(HoldError):
                _verified_scorecard("MOTIF_TOURNAMENT_RESULT " + json.dumps(payload),
                                    self.score["fixture_sha256"])
        no_adverse = copy.deepcopy(self.score)
        no_adverse["aggregate_on_proposed_only"]["cases_regressing_vs_global"] = []
        with self.assertRaises(HoldError):
            _verified_scorecard("MOTIF_TOURNAMENT_RESULT " + json.dumps(no_adverse),
                                self.score["fixture_sha256"])

    def test_preview_does_not_launch_unmerged_experiment(self):
        with patch("motif.method_tournament.select_reviewed_source",
                   return_value=(self.source,self.signals)):
            with patch("motif.method_tournament._run_isolated") as runner:
                result = run(".", "reciprocal prediction", False)
        runner.assert_not_called()
        self.assertEqual(result["status"], "PREVIEW_NO_DONOR_EXECUTION")
        self.assertFalse(result["method_installed"])
        self.assertFalse(result["automatic_merge"])

    def test_retained_receipt_can_preview_same_source_without_merging(self):
        receipt = assemble_held_receipt(
            self.source, self.signals, self.score, self.score["fixture_sha256"])
        with patch("motif.method_tournament.select_reviewed_source",
                   return_value=(self.source,self.signals)):
            result = run(".", "reciprocal prediction", False, receipt)
        self.assertTrue(result["retained_receipt_reused"])
        self.assertFalse(result["execution_requested"])
        self.assertTrue(result["source_branch_compared_but_not_merged"])

    def test_moved_source_head_stops_retained_cartridge(self):
        receipt = assemble_held_receipt(
            self.source, self.signals, self.score, self.score["fixture_sha256"])
        changed = Pointer(self.source.ref,"c"*40)
        with patch("motif.method_tournament.select_reviewed_source",
                   return_value=(changed,self.signals)):
            with self.assertRaises(HoldError):
                run(".", "reciprocal prediction", True, receipt)

    def test_changed_live_donor_head_is_rejected_before_reading_source_files(self):
        self.assertEqual(PROFILE["reviewed_source_commit"],
                         "586be3530d2b5b4d41f810515f9c457d2a27a371")
        moved = Pointer(PROFILE["source_branch"], "c" * 40)
        with patch("motif.method_tournament.observe", return_value=moved):
            with patch("motif.method_tournament.read_text") as reader:
                with self.assertRaises(HoldError):
                    select_reviewed_source(".", "reciprocal role prediction")
                reader.assert_not_called()

    def test_reviewed_profile_accepts_only_one_original_fixed_source(self):
        self.assertEqual(PROFILE["module"],
                         "experiments/reciprocal-003/reason_loop.js")
        self.assertEqual(PROFILE["image"], "node:22-alpine")
        self.assertTrue(PROFILE["source_branch"].startswith("experiment/"))
        self.assertEqual(PROFILE["fixed_commands"][-1][1],
                         "evaluation/evaluate.cjs")


if __name__ == "__main__":
    unittest.main()
