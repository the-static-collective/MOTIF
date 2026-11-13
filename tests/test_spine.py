"""Reason Spine 001 regression and boundary tests: no network or live people."""
import copy
import unittest

from motif.branch_garden import (HoldError, Pointer, valid_ref, from_census, suggest,
                                 passport_lenses, merge_verdict, inspect_json)
from motif.reason_spine import analyze, comparison, information_gain, CaseError


CASE = {
    "question": "Which invented relation explains a discrepant drawing?",
    "goal": "Choose a cheap discriminating observation before revising a diagram.",
    "hypotheses": [
        {"id": "camera", "predictions": {"angle": "yes", "post": "no"}},
        {"id": "post", "predictions": {"angle": "no", "post": "yes"}},
        {"id": "corner", "predictions": {"angle": "no", "post": "no"}},
    ],
    "tests": [
        {"id": "angle", "cost": 0.04, "risk": 0.0},
        {"id": "post", "cost": 0.12, "risk": 0.1},
    ],
    "reports": [],
}


class BranchGardenTests(unittest.TestCase):
    def test_branch_ref_safety(self):
        for bad in ("../evil", "experiment/../../main", "-a", "/absolute",
                    ".hidden", "foo//bar", "a@{bad", "foo.lock"):
            self.assertFalse(valid_ref(bad), bad)
        self.assertTrue(valid_ref("experiment/reciprocal-004-ecosystem-crosswire-20261112"))

    def test_census_preserves_unmerged_without_promoting(self):
        census = {
            "schema": "motif.public-branch-census.v1",
            "repository": "the-static-collective/MOTIF",
            "all_pages_checked": True,
            "source_only_cartridges": 2,
            "passports": [
                {"ref": "experiment/alpha", "commit": "a" * 40, "executable": False, "authority": "NONE"},
                {"ref": "experiment/beta", "commit": "b" * 40, "executable": False, "authority": "NONE"},
            ],
        }
        rows = from_census(census)
        self.assertEqual(len(rows), 2)
        self.assertEqual(suggest("alpha", rows)[0]["ref"], "experiment/alpha")
        self.assertEqual(rows[0].status, "PENCIL_SOURCE_POINTER_NOT_ADMITTED")
        census["passports"][0]["executable"] = True
        with self.assertRaises(HoldError):
            from_census(census)

    def test_passport_does_not_grant_execution(self):
        snap = {
            "pointer": Pointer("experiment/reciprocal-004", "a" * 40).as_dict(),
            "blob_sha256": "b" * 64,
            "payload": {
                "schema": "motif.reciprocal-capability-passport/v1",
                "owner": "the-static-collective/MOTIF",
                "source": {"deployed": False, "realHumanData": False},
                "exchange": {"status": "PROPOSAL_ONLY"},
                "capabilities": [{"id": "two-doors"}, {"id": "reason-field"},
                                 {"id": "method-foundry"}],
                "gate": {"disposition": "HOLD_FOR_OWNER_REVIEW", "autoApproval": False},
            },
        }
        lens = passport_lenses(snap)
        self.assertEqual(lens["execution"], "NONE")
        result = analyze(CASE, [lens])
        self.assertEqual(result["next_voluntary_question"]["mode"], "LET_MOTIF_ASK")
        self.assertEqual(result["roles"]["architect"]["candidate_foundry"], True)
        self.assertEqual(result["external_action"], "NONE")
        snap["payload"]["gate"]["autoApproval"] = True
        with self.assertRaises(HoldError):
            passport_lenses(snap)

    def test_stale_offline_pointer_cannot_fetch(self):
        with self.assertRaises(HoldError):
            inspect_json(".", Pointer("experiment/a", "a" * 40, "dated-public-census"),
                         "foo.json")

    def test_merge_is_a_judgment_not_a_side_effect(self):
        held = merge_verdict({"pinned_source": True, "independent_tests": True})
        self.assertEqual(held["verdict"], "KEEP_UNMERGED_USE_AS_HELD_SOURCE")
        self.assertFalse(held["automatic_merge"])
        ready = merge_verdict({
            "pinned_source": True, "independent_tests": True,
            "strong_baseline_compared": True, "no_known_regressions": True,
            "owner_review": True, "measured_transfer_gain": 0.1,
        })
        self.assertEqual(ready["verdict"], "RECOMMEND_MERGE_REVIEW")
        self.assertFalse(ready["automatic_merge"])


class ReasoningTests(unittest.TestCase):
    def test_information_gain_matches_classical_partition(self):
        gain = information_gain(CASE["hypotheses"], "angle")
        self.assertAlmostEqual(gain, 0.918295834, places=6)

    def test_five_roles_and_bounded_value(self):
        result = analyze(CASE)
        self.assertEqual(result["result"], "PROPOSE_PROBE")
        self.assertEqual(result["next_probe"]["id"], "angle")
        self.assertEqual(len(result["roles"]), 5)
        self.assertEqual(result["phases"],
                         ["OBSERVE", "HYPOTHESIZE", "PROBE", "REVISE", "PLAN", "VERIFY"])

    def test_a_report_is_not_truth(self):
        case = copy.deepcopy(CASE)
        case["reports"] = [{"source_root": "w1", "test": "angle",
                            "outcome": "yes", "status": "reported"}]
        result = analyze(case)
        self.assertEqual(len(result["remaining_hypotheses"]), 3)
        self.assertEqual(result["declared_reviewed_observations_not_authenticated_truth"], {})

    def test_source_revisions_not_multiple_votes(self):
        case = copy.deepcopy(CASE)
        case["reports"] = [
            {"source_root": "w1", "test": "angle", "outcome": "yes"},
            {"source_root": "w1", "test": "angle", "outcome": "no"},
        ]
        result = analyze(case)
        self.assertEqual(result["reported_source_claims"], 1)
        self.assertEqual(result["roles"]["historian"]["source_revisions"][0]["event"],
                         "SOURCE_REVISION")

    def test_conflict_holds_and_abstains(self):
        case = copy.deepcopy(CASE)
        case["reports"] = [
            {"source_root": "w1", "test": "angle", "outcome": "yes"},
            {"source_root": "w2", "test": "angle", "outcome": "no"},
        ]
        result = analyze(case)
        self.assertEqual(result["result"], "HOLD_CONTESTED_REPORTS")

    def test_declared_review_does_not_become_real_world_truth(self):
        case = copy.deepcopy(CASE)
        case["reports"] = [
            {"source_root": "w1", "test": "angle", "outcome": "yes",
             "status": "reviewed", "review_receipt": "synthetic-owner-check"}
        ]
        result = analyze(case)
        self.assertEqual(result["remaining_hypotheses"], ["camera"])
        self.assertEqual(result["result"], "VERIFY_HYPOTHESIS_NOT_TRUTH")
        self.assertEqual(result["truth_status"], "NO_REAL_WORLD_CAUSAL_VERIFICATION")

    def test_model_falsification(self):
        case = copy.deepcopy(CASE)
        case["reports"] = [
            {"source_root": "w1", "test": "angle", "outcome": "yes",
             "status": "reviewed", "review_receipt": "synthetic-1"},
            {"source_root": "w2", "test": "post", "outcome": "yes",
             "status": "reviewed", "review_receipt": "synthetic-2"},
        ]
        self.assertEqual(analyze(case)["result"], "HOLD_MODEL_FALSIFIED")

    def test_control_comparison_is_honest(self):
        matrix = comparison(CASE)
        self.assertEqual(matrix["real_pretrained_llm"]["status"],
                         "NOT_RUN_REQUIRES_REAL_MODEL_AND_MATCHED_INPUTS")
        self.assertNotEqual(matrix["motif_spine"]["policy"], "classical_ig")

    def test_invalid_hypothesis_fails_closed(self):
        case = copy.deepcopy(CASE)
        case["hypotheses"][0]["predictions"]["post"] = "definitely"
        with self.assertRaises(CaseError):
            analyze(case)

    def test_nonadmitted_lenses_only(self):
        with self.assertRaises(CaseError):
            analyze(CASE, [{"admission": "PRODUCTION", "execution": "YES"}])


if __name__ == "__main__":
    unittest.main()
