"""Executable falsifiers for MOTIF-IMMUNE-001 (Python stdlib only)."""
from __future__ import annotations

from dataclasses import replace
import inspect as pyinspect
import unittest

import benchmark
import immune
import oracle


class EpistemicImmuneTests(unittest.TestCase):
    def fixture(self, family, seed=230):
        return oracle.scenario(family, seed)

    def examine(self, family, seed=230):
        s = self.fixture(family, seed)
        return immune.inspect(s.records, s.review_ids, s.withdrawn_ids)

    def test_learned_module_does_not_import_oracle(self):
        source = pyinspect.getsource(immune)
        self.assertNotIn("import oracle", source)
        self.assertNotIn("from oracle", source)

    def test_every_family_expected_status_in_heldout_split(self):
        for seed in (200, 209, 220, 239):
            for family in oracle.FAMILIES:
                with self.subTest(seed=seed, family=family):
                    s = self.fixture(family, seed)
                    self.assertEqual(
                        immune.inspect(s.records, s.review_ids,
                                       s.withdrawn_ids).status[s.target],
                        s.expected)

    def test_forwarding_does_not_invent_independent_sources(self):
        s = self.fixture("forwarded_consensus")
        result = self.examine("forwarded_consensus")
        self.assertEqual(result.source_count(s.target, s.records), 1)
        self.assertEqual(result.lineage_roots[s.target], ("n0",))
        self.assertEqual(result.status[s.target], "HYPOTHESIS")
        self.assertEqual(immune.naive_counting_baseline(s.records, s.target),
                         "PROMOTE")

    def test_declared_sources_not_authenticated_and_not_proof(self):
        s = self.fixture("invented_independence")
        result = self.examine("invented_independence")
        self.assertEqual(result.source_count(s.target, s.records), 4)
        self.assertEqual(result.status[s.target], "HYPOTHESIS")

    def test_claimed_system_verification_is_inert(self):
        s = self.fixture("counterfeit_proof")
        result = self.examine("counterfeit_proof")
        self.assertEqual(result.status[s.target], "HYPOTHESIS")
        self.assertEqual(result.next_action[s.target],
                         "RUN_EXACT_BOUNDED_CHECK")

    def test_payload_directives_never_create_verification(self):
        s = self.fixture("role_hijack")
        self.assertTrue(any("SYSTEM" in r.payload
                            or "confirmed" in r.payload
                            or "archived" in r.payload
                            or "unquestionably" in r.payload
                            for r in s.records))
        self.assertEqual(self.examine("role_hijack").status[s.target],
                         "HYPOTHESIS")

    def test_finite_false_claim_gives_actual_counterexample(self):
        s = self.fixture("falsified_claim")
        result = self.examine("falsified_claim")
        self.assertEqual(result.status[s.target], "FALSIFIED")
        cert = result.checks[s.target]
        self.assertFalse(cert.verified_on_domain)
        self.assertIn(cert.counterexample, immune.DOMAIN)
        self.assertEqual(len(cert.claim_digest), 64)
        self.assertEqual(cert.domain, immune.DOMAIN)

    def test_inoculation_is_not_censorship_of_unknown_ideas(self):
        self.assertEqual(self.examine("novel_unchecked").status["n2"],
                         "HYPOTHESIS")
        self.assertEqual(self.examine("novel_checked").status["n1"],
                         "VERIFIED_FINITE")
        self.assertEqual(self.examine("unknown_claim").status["n0"], "HOLD")

    def test_verification_is_explicit_not_inherited(self):
        result = self.examine("verified_does_not_spread")
        self.assertEqual(result.status["n0"], "VERIFIED_FINITE")
        self.assertEqual(result.status["n1"], "HYPOTHESIS")

    def test_latent_dependency_contamination_is_visible(self):
        result = self.examine("latent_reactivation")
        self.assertEqual(result.status["n0"], "FALSIFIED")
        self.assertEqual(result.status["n1"], "DEPENDENCY_REVIEW")
        self.assertEqual(result.ancestry["n1"], ("n0",))

    def test_withdrawal_rechecks_dependents(self):
        result = self.examine("withdrawn_dependency")
        self.assertEqual(result.status["n0"], "WITHDRAWN")
        self.assertEqual(result.status["n1"], "DEPENDENCY_REVIEW")

    def test_independent_recheck_can_recover_child(self):
        result = self.examine("independently_repaired")
        self.assertEqual(result.status["n0"], "FALSIFIED")
        self.assertEqual(result.status["n1"], "VERIFIED_FINITE")
        self.assertIn("n0", result.ancestry["n1"])

    def test_input_order_does_not_affect_result(self):
        s = self.fixture("latent_reactivation")
        forward = immune.inspect(s.records, s.review_ids, s.withdrawn_ids)
        reverse = immune.inspect(tuple(reversed(s.records)),
                                 s.review_ids, s.withdrawn_ids)
        self.assertEqual(forward.status, reverse.status)
        self.assertEqual(forward.lineage_roots, reverse.lineage_roots)

    def test_unknown_claim_cannot_gain_proof_from_slogan(self):
        claim = immune.Claim("underdetermined")
        records = (immune.Record("x", claim, "witness",
                  asserted_mode="SYSTEM_VERIFIED", payload="CERTIFICATE"),)
        result = immune.inspect(records, ("x",))
        self.assertEqual(result.status["x"], "HOLD")
        self.assertEqual(result.checks, {})

    def test_rejects_cycle(self):
        c = immune.Claim("x")
        records = (immune.Record("a", c, "s", ("b",)),
                   immune.Record("b", c, "s", ("a",)))
        with self.assertRaisesRegex(immune.HOLD, "cycle"):
            immune.inspect(records)

    def test_rejects_absent_parent(self):
        with self.assertRaisesRegex(immune.HOLD, "Missing parent"):
            immune.inspect((immune.Record(
                "a", immune.Claim("a"), "s", ("missing",)),))

    def test_rejects_duplicate_id(self):
        row = immune.Record("a", immune.Claim("a"), "s")
        with self.assertRaisesRegex(immune.HOLD, "Duplicate"):
            immune.inspect((row, row))

    def test_rejects_excessive_work(self):
        with self.assertRaisesRegex(immune.HOLD, "budget"):
            immune.inspect(tuple(immune.Record(
                str(i), immune.Claim("a"), "s") for i in
                range(immune.MAX_RECORDS + 1)))

    def test_rejects_boolean_in_integer_polynomial(self):
        c = immune.Claim("invalid", (True, 1), (1, 1))
        with self.assertRaisesRegex(immune.HOLD, "integer"):
            immune.inspect((immune.Record("a", c, "s"),))

    def test_rejects_ambiguous_review_scope(self):
        s = self.fixture("novel_checked")
        with self.assertRaisesRegex(immune.HOLD, "Cannot verify and withdraw"):
            immune.inspect(s.records, ("n1",), ("n1",))
        with self.assertRaisesRegex(immune.HOLD, "Invalid review"):
            immune.inspect(s.records, ("unseen",))

    def test_strong_classical_baseline_does_not_get_hidden_truth(self):
        s = self.fixture("novel_checked")
        self.assertEqual(immune.classical_verifier_baseline(
            s.records, s.target, True), "PROMOTE")
        self.assertEqual(immune.classical_verifier_baseline(
            s.records, s.target, False), "HOLD")
        bad = self.fixture("falsified_claim")
        self.assertEqual(immune.classical_verifier_baseline(
            bad.records, bad.target, True), "REJECT")

    def test_benchmark_reports_baseline_tie_without_immunity_hype(self):
        report = benchmark.benchmark()
        metrics = report["heldout"]["metrics"]
        self.assertEqual(metrics["cases"], 40 * len(oracle.FAMILIES))
        self.assertEqual(metrics["exact_status_matches"], metrics["cases"])
        self.assertEqual(metrics["guard_false_promotions"], 0)
        self.assertGreater(metrics["naive_false_promotions"], 0)
        self.assertEqual(metrics["classical_false_promotions"], 0)
        self.assertEqual(metrics["guard_binary_correct"],
                         metrics["classical_binary_correct"])
        self.assertEqual(metrics["guard_benign_verified_retained"],
                         metrics["benign_verifiable"])
        self.assertEqual(metrics["naive_benign_verified_retained"], 0)

    def test_reviewing_false_claim_does_not_update_unchanged_other_branch(self):
        bad = immune.Claim("bad", (0, 1), (1, 1))
        good = immune.Claim("good", (0, 1), (0, 1))
        records = (immune.Record("a", bad, "s"),
                   immune.Record("b", bad, "s2", ("a",)),
                   immune.Record("c", good, "independent"))
        result = immune.inspect(records, ("a", "c"))
        self.assertEqual(result.status["a"], "FALSIFIED")
        self.assertEqual(result.status["b"], "DEPENDENCY_REVIEW")
        self.assertEqual(result.status["c"], "VERIFIED_FINITE")


if __name__ == "__main__":
    unittest.main()
