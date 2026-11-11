"""Focused falsifiers; test the adapter, not claimed external benchmark gains."""
import json
import unittest
from pathlib import Path
from mesh import (HERE, FACTS, EVENTS, POLICIES, WORLDS, Owner, benchmark,
                  filter_worlds, native003, pick_mesh, run, safe_action)


class Void001Tests(unittest.TestCase):
    def test_frozen_source_catalog_is_not_deceptive(self):
        sources = json.loads((HERE / "sources.json").read_text())["sources"]
        cards = json.loads((HERE / "challenges.json").read_text())["cards"]
        self.assertGreaterEqual(len(sources), 10)
        self.assertGreaterEqual(len(cards), 12)
        self.assertTrue({"osworld2", "traverse_failure", "aide2", "g2_distrust_tax",
                         "tau2", "webarena", "alfworld", "behavior1k", "movingai",
                         "crafter", "atlas"}.issubset({s["id"] for s in sources}))
        self.assertTrue(all("primary" in source and "local_state" in source
                            for source in sources))
        self.assertEqual("GATED_TASK_CLASSES_AND_ASSETS",
                         next(s["access"] for s in sources if s["id"] == "osworld2"))
        self.assertEqual("survey_report_not_benchmark",
                         next(s["kind"] for s in sources if s["id"] == "g2_distrust_tax"))

    def test_actual_native_003_import_and_analysis(self):
        native = native003()
        self.assertTrue(hasattr(native, "analyze_first_moves"))
        self.assertIn(pick_mesh(WORLDS, FACTS, {}), FACTS)

    def test_permission_is_necessary_in_all_hypotheses(self):
        self.assertIsNone(safe_action(WORLDS))
        self.assertIsNone(safe_action(filter_worlds({"primary": 1})))
        self.assertEqual("use_primary", safe_action(filter_worlds({"permission": 1,
                                                                     "primary": 1})))

    def test_policy_never_reads_hidden_truth_for_first_question(self):
        first = {p: [] for p in POLICIES}
        for policy in POLICIES:
            for world in WORLDS:
                result = run(world, "steady", policy, budget=1)
                first[policy].append(result["ledger"][0]["sensor"])
            self.assertEqual(1, len(set(first[policy])))

    def test_unsealed_tampering_is_rejected(self):
        owner = Owner((1, 1, 0), "forged_report")
        forged = owner.observe("permission")
        self.assertFalse(owner.verify(forged))
        self.assertFalse(forged["value"] == owner.truth[0])
        self.assertFalse(any(r["accepted"] for r in
                             run((1, 1, 0), "forged_report", "exact_dp")["ledger"]
                             if r["sensor"] == "permission"))

    def test_old_ink_kept_but_not_used_as_current_after_epoch_change(self):
        owner = Owner((1, 1, 0), "source_drift")
        old = owner.observe("primary")
        new = owner.observe("permission")
        self.assertEqual(0, old["epoch"])
        self.assertEqual(1, new["epoch"])
        self.assertTrue(owner.verify(old) and owner.verify(new))
        self.assertEqual(0, owner.truth[1])

    def test_revocation_and_noop_do_not_forge_goal_receipts(self):
        for event in ("revoked_permission", "actuator_noop"):
            for policy in POLICIES:
                outcome = run((1, 1, 1), event, policy, budget=3)
                self.assertFalse(outcome["verified_success"])
                self.assertNotEqual("VERIFIED_GOAL", outcome["status"])

    def test_denied_permission_never_causes_action(self):
        for policy in POLICIES:
            for alt in (0, 1):
                outcome = run((0, 1, alt), "steady", policy, budget=3)
                self.assertIsNone(outcome["plan"])
                self.assertEqual(0, outcome["external_actions"])

    def test_clean_success_is_observed_not_assumed(self):
        for policy in POLICIES:
            outcome = run((1, 1, 1), "steady", policy, budget=3)
            self.assertTrue(outcome["verified_success"])
            self.assertTrue(outcome["outcome"]["success"])
            self.assertEqual("VERIFIED_GOAL", outcome["status"])

    def test_all_policies_share_budget_and_fixed_cases(self):
        result = benchmark()
        self.assertEqual(40, result["cases_per_policy"])
        self.assertEqual(120, len(result["rows"]))
        self.assertEqual(set(POLICIES), set(result["policy_metrics"]))
        self.assertEqual(0, result["external_benchmark_cases_executed"])
        self.assertTrue(all(r["source_is_independent"] is False
                            and r["external_actions"] == 0 for r in result["rows"]))
        self.assertEqual(result["sha256"], benchmark()["sha256"])


if __name__ == "__main__":
    unittest.main()
