import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from trial import digest, evaluate, load_cohort, run, training_libraries
from world import F, case


class ReframeTrialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run()
        first, last, _ = training_libraries()
        cls.library = first | last

    def test_exact_control_and_motif_tie_on_actual_outcomes(self):
        results = self.report["summary"]
        for key in ("completed", "net_value", "execution_cost", "query_cost"):
            self.assertEqual(results["exact_primitive"][key], results["motif"][key])
        self.assertLess(results["motif"]["outer_plan_calls"],
                        results["exact_primitive"]["outer_plan_calls"])
        self.assertGreater(results["motif"]["primitive_guard_budget"],
                           results["exact_primitive"]["primitive_guard_budget"])

    def test_composed_probe_can_change_a_decision(self):
        task = case("test", "relevant", ("interface_fits", "reusable"))
        result = evaluate(task, self.library, "decision")
        self.assertEqual(result["commitment"]["question"], ("interface_fits", "reusable"))
        self.assertEqual(result["query_cost"], 2)
        self.assertEqual(result["execution_cost"], 5)
        self.assertTrue(result["completed"])

    def test_same_prior_commits_same_policy_before_owner_answer(self):
        good = case("test", "same-input", ("interface_fits", "reusable"))
        bad = case("test", "same-input", ("reusable",))
        positive, negative = (evaluate(task, self.library, "decision") for task in (good, bad))
        self.assertEqual(positive["commitment_digest"], negative["commitment_digest"])
        self.assertNotEqual(positive["reply"], negative["reply"])
        self.assertEqual(negative["primitive_calls"][0]["operator"], "use_alternative")

    def test_missing_permission_holds_without_buying_irrelevant_evidence(self):
        task = case("test", "denied", ("interface_fits", "reusable"),
                    release_allowed=False, alternative=False)
        self.assertNotIn(F("release_allowed", task.asset), task.truth)
        result = evaluate(task, self.library, "decision")
        self.assertEqual(result["outcome"], "HOLD")
        self.assertEqual(result["query_cost"], 0)
        self.assertEqual(result["primitive_calls"], [])

    def test_compounding_has_a_reusable_operator_and_preserves_negative_cost_result(self):
        rows = self.report["compounding"]
        self.assertEqual([rows[name]["routes"][0]["outer_calls"] for name in (
            "accumulated", "last_round_only", "frozen_start")], [3, 4, 5])
        self.assertEqual(rows["accumulated"]["new_case_checks"], {
            "new-binding": "DELIVERED",
            "wrong-interface": "REJECTED",
            "denied-permission": "REJECTED",
        })
        self.assertGreater(rows["accumulated"]["charged_guard_budget"],
                           rows["frozen_start"]["charged_guard_budget"])

    def test_owner_files_are_joined_by_id_and_reject_hidden_fields_in_inputs(self):
        entry = {"family": "blind", "label": "one", "release_allowed": True,
                 "alternative": True, "interface_unknown": False}
        with TemporaryDirectory() as directory:
            cases = Path(directory) / "cases.json"
            outcomes = Path(directory) / "outcomes.json"
            cases.write_text(json.dumps([entry]))
            outcomes.write_text(json.dumps({"blind:one": ["reusable"]}))
            report = run(load_cohort(cases, outcomes))
            self.assertEqual(report["scope"], "CALLER_SUPPLIED_SHARED_GRAMMAR")
            self.assertEqual(report["summary"]["motif"]["cases"], 1)
            cases.write_text(json.dumps([entry | {"truth": ["reusable"]}]))
            with self.assertRaises(ValueError):
                load_cohort(cases, outcomes)

    def test_receipt_replays_across_hash_seeds(self):
        script = str(Path(__file__).with_name("trial.py"))
        outputs = [subprocess.check_output(
            [sys.executable, script], env=dict(os.environ, PYTHONHASHSEED=seed))
            for seed in ("1", "2")]
        self.assertEqual(*outputs)
        report = json.loads(outputs[0])
        claimed = report.pop("digest")
        self.assertEqual(claimed, digest(report))


if __name__ == "__main__":
    unittest.main()
