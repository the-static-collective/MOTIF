"""FIRE-003 proof-bound, replay, and adversarial source-lineage guard tests."""
import unittest

from smoke import (
    Attestation, Learner, Report, REGIMES, POLICIES,
    forecast, world, run, fixed_forecast_audit
)


def copies(answers):
    return tuple(Report("Q0", f"claim-{i}", a)
                 for i, a in enumerate(answers))


class SmokeTests(unittest.TestCase):
    def test_identical_claims_not_independent_sources(self):
        reports = copies((False, False, False, True, True))
        naive = forecast(reports, None, .8)
        grounded = forecast(reports, Attestation("VERIFIED", ("a","a","a","b","c")), .8)
        self.assertGreater(naive["claimed"], grounded["effective_roots"])
        self.assertEqual(grounded["effective_roots"], 3)
        self.assertEqual(grounded["signal"], "DEPENDENCE_DISCOVERED")
        self.assertLess(naive["p_true"], .5)
        self.assertGreater(grounded["p_true"], .5)
        self.assertTrue(grounded["eligible"])

    def test_all_copies_cannot_fake_quorum(self):
        rows = copies((True,) * 5)
        audit = Attestation("VERIFIED", ("same",) * 5)
        state = forecast(rows, audit, .8)
        self.assertEqual(state["effective_roots"], 1)
        self.assertFalse(state["eligible"])
        self.assertEqual(state["signal"], "DEPENDENCE_DISCOVERED")

    def test_inadequate_provenance_abstains_without_oracle(self):
        rows = copies((True,) * 5)
        state = forecast(rows, Attestation("UNVERIFIABLE"), .8)
        self.assertFalse(state["eligible"])
        self.assertEqual(state["p_true"], .5)
        self.assertEqual(state["signal"], "UNVERIFIABLE_LINEAGE")

    def test_report_id_forgery_not_proof_of_independence(self):
        owner = world(53001, "copied")
        reports = owner.reports["Q0"]
        self.assertEqual(len({r.claim_id for r in reports}), 5)
        audit = owner.attest("Q0", reports)
        self.assertEqual(len(set(audit.origins)), 3)
        self.assertEqual(len({r.claim_id for r in reports}), 5)

    def test_compromised_auditor_inherently_unobservable(self):
        hidden = world(53001, "compromised")
        reports = hidden.reports["Q0"]
        claimed_roots = hidden.attest("Q0", reports).origins
        self.assertEqual(len(set(claimed_roots)), 5)
        self.assertEqual(len(set(hidden.origins["Q0"])), 3)
        state = forecast(reports, hidden.attest("Q0", reports), .8)
        self.assertEqual(state["signal"], "CLEAR")
        # No algorithm with these identical public receipts can infer the private
        # true root ancestry; this is an intentional honest boundary.

    def test_only_verified_feedback_changes_learning(self):
        learner = Learner()
        before = learner.reliability
        with self.assertRaises(ValueError):
            learner.accept({"task":"Q0", "guess":True, "actual":False,
                            "certified":False, "authority":"unverified-rumor"},
                           .99, {"source_votes":(True,)}, True)
        self.assertEqual(before, learner.reliability)
        self.assertEqual(learner.verified_events, 0)

    def test_online_dedup_restricts_feedback_count(self):
        same_receipt = {"task":"Q0", "guess":False, "certified":False,
                        "actual":True, "authority":"synthetic-verification-only"}
        copies_learner = Learner()
        sources_learner = Learner()
        copies_learner.accept(same_receipt, .001, {"source_votes":(False,) * 5}, True)
        sources_learner.accept(same_receipt, .2, {"source_votes":(False,)}, True)
        self.assertEqual(copies_learner.incorrect - 1, 5)
        self.assertEqual(sources_learner.incorrect - 1, 1)
        self.assertEqual(copies_learner.verified_events, 1)
        self.assertEqual(sources_learner.verified_events, 1)

    def test_no_hidden_truth_in_public_reports_or_tasks(self):
        w = world(53002, "copied")
        r = w.observe("Q0", 0)
        self.assertNotIn("truth", r.__dataclass_fields__)
        self.assertNotIn("origins", r.__dataclass_fields__)
        self.assertNotIn("truth", w.tasks["Q0"].__dataclass_fields__)
        self.assertNotEqual(w.attest("Q0", w.reports["Q0"]).origins,
                            tuple(x.claim_id for x in w.reports["Q0"]))

    def test_unknown_cannot_update(self):
        case = run(53003, "unverifiable", "guarded_online")
        self.assertEqual(case["verified_learning_events"], 0)
        self.assertGreater(case["holds"], 0)
        self.assertEqual(case["failed_verifications"], 0)
        self.assertEqual(case["certified_value"], 0)

    def test_limits_and_replay(self):
        for regime in REGIMES:
            for policy in POLICIES:
                result = run(53004, regime, policy)
                self.assertLessEqual(result["operations_spent"], 32)
                self.assertEqual(result, run(53004, regime, policy))
                self.assertLessEqual(result["verified_learning_events"],
                                     result["certified_count"] + result["failed_verifications"])
                if policy.endswith("frozen"):
                    self.assertEqual(result["verified_learning_events"], 0)

    def test_all_eight_exposures(self):
        for regime in REGIMES:
            summary = fixed_forecast_audit(53008, regime)
            for method in ("naive", "guarded", "oracle_roots"):
                self.assertGreaterEqual(summary[method]["brier"], 0)
                self.assertLessEqual(summary[method]["brier"], 1)
                self.assertLessEqual(summary[method]["held"], 8)


if __name__ == "__main__":
    unittest.main()
