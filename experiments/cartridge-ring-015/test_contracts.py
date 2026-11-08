"""RING-015: real-source differentiated diagnostics and conditional value tests."""
from __future__ import annotations
import ast,json
from pathlib import Path
import tempfile
import unittest

import fixtures,policy,runner


def illustrative_measurements():
    """Handwritten only for unit-testing decision math, NOT claimed evidence."""
    cues=policy.CUES
    counts={c:0 for c in cues}
    bugs={c:0 for c in cues}
    counts.update({"MATH":8,"CONTROL":8,"UNCHANGED":5,"MIXED":1})
    bugs.update({"MATH":6,"CONTROL":5,"UNCHANGED":0,"MIXED":1})
    observations={}
    for cue in cues:
        observations[cue]={}
        for phase in runner.PHASES:
            n=counts[cue]
            b=bugs[cue]
            good=n-b
            is_target=(
                phase=="FULL" or
                (phase=="MATH" and cue=="MATH") or
                (phase=="CONTROL" and cue=="CONTROL"))
            observations[cue][phase]={
                "bug_total":b,"bug_fail":b if is_target else 0,
                "clean_total":good,"clean_fail":0,
            }
    return {
        "cases":sum(counts.values()),
        "seeded_defects":sum(bugs.values()),
        "cue_frequencies":{
            k:counts[k]/sum(counts.values()) for k in cues},
        "cue_totals":counts,"cue_bugs":bugs,
        "mean_wall_seconds":{
            "TRIAGE":0.1,"MATH":0.15,"CONTROL":0.15,"FULL":2.8},
        "actual_source_detection_observations":observations,
    }


class RealSecondExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo=Path(__file__).resolve().parents[2]
        cls.folder=tempfile.TemporaryDirectory(prefix="motif-ring015-tests-")
        cls.root=Path(cls.folder.name)
        cls.root.chmod(0o755)
        cls.specs=(
            ("test-clean",()),
            ("test-math",("posterior_uninformed",)),
            ("test-control",("budget_nonconservation",)),
            ("test-benign-math",("benign_math",)),
            ("test-benign-control",("benign_control",)),
            ("test-mixed",("gain_zero","stop_when_negative")),
            ("test-syntax",("invalid_import",)),
        )
        cls.cases=fixtures.make(cls.root,cls.repo,cls.specs)
        cls.pre=runner.preflight(cls.repo)

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def observed(self,case,phase):
        return runner.observe(self.root,case,phase,self.repo)

    def test_trusted_source_and_image_hash_available(self):
        self.assertEqual(set(self.pre["source_files"]),set(fixtures.SOURCE))
        self.assertTrue(self.pre["image_id"].startswith("sha256:"))
        self.assertTrue(self.pre["network_disabled_for_every_actual_test"])
        self.assertTrue(self.pre["read_only_inputs"])

    def test_real_triage_identifies_changed_region_not_bug_label(self):
        expect={
            "test-clean":"UNCHANGED",
            "test-math":"MATH",
            "test-control":"CONTROL",
            "test-benign-math":"MATH",
            "test-benign-control":"CONTROL",
            "test-mixed":"MIXED",
        }
        for case,cue in expect.items():
            receipt=self.observed(case,"TRIAGE")
            self.assertTrue(receipt["actual_source_tests_passed"],case)
            self.assertEqual(receipt["source_cue"],cue)
            self.assertTrue(receipt["source_labels_not_supplied_to_planner"])
            self.assertEqual(receipt["external_effects_executed"],0)

    def test_actual_syntax_failure_is_caught_by_triage(self):
        r=self.observed("test-syntax","TRIAGE")
        self.assertFalse(r["actual_source_tests_passed"])
        self.assertEqual(r["source_cue"],"SYNTAX_ERROR")
        self.assertIn("invalid syntax",r["observed_test_failure"])
        self.assertEqual(r["authority"],"NONE")

    def test_real_focused_math_test_distinguishes_fault_and_benign_change(self):
        corrupted=self.observed("test-math","MATH")
        benign=self.observed("test-benign-math","MATH")
        self.assertFalse(corrupted["actual_source_tests_passed"])
        self.assertTrue(benign["actual_source_tests_passed"],
                        benign["observed_test_failure"])
        self.assertGreater(benign["real_source_assertions_executed"],2)

    def test_real_focused_control_test_distinguishes_bug_and_benign(self):
        corrupted=self.observed("test-control","CONTROL")
        benign=self.observed("test-benign-control","CONTROL")
        self.assertFalse(corrupted["actual_source_tests_passed"])
        self.assertTrue(benign["actual_source_tests_passed"],
                        benign["observed_test_failure"])
        self.assertIn("budget",corrupted["observed_test_failure"].lower())

    def test_broad_real_test_is_different_bounded_work(self):
        clean=self.observed("test-clean","FULL")
        self.assertTrue(clean["actual_source_tests_passed"],
                        clean["observed_test_failure"])
        self.assertGreaterEqual(clean["real_source_assertions_executed"],150)
        self.assertGreater(clean["measured_wall_seconds"],0)
        self.assertTrue(all(clean["isolation"].values()))

    def test_conditional_followup_depends_on_observed_source_cue(self):
        estimates=illustrative_measurements()
        params={
            "detection_benefit":24.0,
            "time_weight":1.5,
            "false_alarm_penalty":10.0,
        }
        math_choice=policy.choose_after_cue(estimates,params,"MATH")
        control_choice=policy.choose_after_cue(
            estimates,params,"CONTROL")
        self.assertEqual(math_choice["action"],"MATH")
        self.assertEqual(control_choice["action"],"CONTROL")
        self.assertNotEqual(
            math_choice["action"],control_choice["action"])
        self.assertEqual(
            policy.choose_after_cue(
                estimates,params,"SYNTAX_ERROR")["action"],"STOP")

    def test_real_first_probe_can_choose_two_step_in_unit_model(self):
        estimate=illustrative_measurements()
        params={
            "detection_benefit":24.0,
            "time_weight":1.5,
            "false_alarm_penalty":10.0,
        }
        chosen=policy.choose_first(estimate,params)
        self.assertEqual(chosen["action"],"TRIAGE")
        self.assertGreater(
            chosen["ranked"]["TRIAGE"],chosen["ranked"]["FULL"])
        events=[]
        def measured_phase(phase):
            events.append(phase)
            if phase=="TRIAGE":
                return {
                    "phase":phase,"source_cue":"MATH",
                    "actual_source_tests_passed":True,
                    "measured_wall_seconds":0.12,
                    "real_source_assertions_executed":2,
                }
            return {
                "phase":phase,"source_cue":None,
                "actual_source_tests_passed":False,
                "measured_wall_seconds":0.15,
                "real_source_assertions_executed":3,
            }
        trace=policy.route(estimate,params,measured_phase)
        self.assertEqual(events,["TRIAGE","MATH"])
        self.assertTrue(trace["saw_actual_failure"])
        self.assertEqual(trace["number_source_tests"],2)

    def test_no_value_does_not_require_interesting_action(self):
        estimate=illustrative_measurements()
        params={
            "detection_benefit":6.0,
            "time_weight":3.0,
            "false_alarm_penalty":10.0,
        }
        x=policy.choose_after_cue(estimate,params,"UNCHANGED")
        self.assertEqual(x["action"],"STOP")

    def test_unknown_or_effectful_tool_phase_never_executes(self):
        for phase in ("DEPLOY","GIT_PUSH","DELETE","EXTERNAL_COMMIT"):
            with self.assertRaises(runner.SandboxError):
                self.observed("test-clean",phase)

    def test_sealed_test_not_imported_during_model_selection(self):
        root=Path(__file__).resolve().parent
        uses=[]
        for name in ("policy.py","learn.py","worker.py","runner.py",
                     "fixtures.py"):
            source=ast.parse((root/name).read_text())
            for node in ast.walk(source):
                if isinstance(node,ast.Import):
                    uses.extend(a.name for a in node.names)
                if isinstance(node,ast.ImportFrom):
                    uses.append(node.module)
        self.assertNotIn("sealed",uses)
        self.assertNotIn("trial",uses)


if __name__=="__main__":unittest.main()
