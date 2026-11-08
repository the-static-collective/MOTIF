"""RING-014: tests must actually run reviewed Python inside Docker, never host.

Unit test correctness refers to intentional, author-controlled source bugs.
Does not establish general software correctness, secure arbitrary-code
execution, or independently evaluated economic benefit of action.
"""
from __future__ import annotations
import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

import adapter,fixtures,runner


class ActualSandboxSourceContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo=Path(__file__).resolve().parents[2]
        cls.temp=tempfile.TemporaryDirectory(
            prefix="motif-ring014-contracts-")
        cls.root=Path(cls.temp.name)
        cls.root.chmod(0o755)
        cls.specs=(
            ("test-clean",()),
            ("test-syntax",("invalid_import",)),
            ("test-stop",("stop_when_negative",)),
            ("test-posterior",("posterior_signal",)),
            ("test-danger",("forbidden_ranking",)),
        )
        cls.cases=fixtures.make(cls.root,cls.repo,cls.specs)
        cls.preflight=runner.preflight(cls.repo)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_actual_reviewed_code_is_used_without_mutating_original(self):
        originals=self.preflight["source_files"]
        value_file=self.repo/"experiments"/"cartridge-ring-013"/"value.py"
        self.assertEqual(
            sha256(value_file.read_bytes()).hexdigest(),
            originals["value.py"])
        self.assertEqual(self.cases[0]["source_copy_sha256"],
                         originals["value.py"])
        self.assertNotEqual(self.cases[2]["source_copy_sha256"],
                            originals["value.py"])

    def test_clean_source_runs_actual_ast_smoke_and_deep(self):
        counts=[]
        for phase in runner.PHASES:
            result=runner.observe(
                self.root,"test-clean",phase,self.repo)
            self.assertTrue(result["actual_source_tests_passed"],
                            result["observed_test_failure"])
            self.assertEqual(result["phase"],phase)
            self.assertTrue(all(result["isolation_controls"].values()))
            self.assertEqual(result["outside_actions_executed"],0)
            counts.append(result["real_source_assertions_executed"])
        self.assertEqual(counts[0],2)
        self.assertEqual(counts[1],2)
        self.assertGreaterEqual(counts[2],15)

    def test_syntax_break_detected_by_real_interpreter_parser(self):
        output=runner.observe(
            self.root,"test-syntax","AST",self.repo)
        self.assertFalse(output["actual_source_tests_passed"])
        self.assertIn("SyntaxError",output["observed_test_failure"])
        self.assertEqual(output["outside_actions_executed"],0)

    def test_negative_value_stop_regression_detected_by_real_smoke(self):
        output=runner.observe(
            self.root,"test-stop","SMOKE",self.repo)
        self.assertFalse(output["actual_source_tests_passed"])
        self.assertIn("Unproductive",output["observed_test_failure"])
        self.assertTrue(output["isolation_controls"]["docker_network_disabled"])

    def test_posterior_math_bug_escapes_smoke_but_fails_deep(self):
        shallow=runner.observe(
            self.root,"test-posterior","SMOKE",self.repo)
        deep=runner.observe(
            self.root,"test-posterior","DEEP",self.repo)
        self.assertTrue(shallow["actual_source_tests_passed"],
                        shallow["observed_test_failure"])
        self.assertFalse(deep["actual_source_tests_passed"])
        self.assertIn("posterior",deep["observed_test_failure"].lower())

    def test_mutated_permission_gate_fails_smoke_not_effectful_work(self):
        output=runner.observe(
            self.root,"test-danger","SMOKE",self.repo)
        self.assertFalse(output["actual_source_tests_passed"])
        self.assertIn("Forbidden",output["observed_test_failure"])
        self.assertEqual(output["outside_actions_executed"],0)

    def test_refuse_unregistered_method_or_case_identifier(self):
        for case,phase in (
            ("../../private","AST"),
            ("test-clean","DEPLOY"),
            ("test-clean","GIT_PUSH"),
        ):
            with self.assertRaises(runner.SandboxError):
                runner.observe(self.root,case,phase,self.repo)

    def test_inherited_bellman_planner_keeps_forbidden_external_commit(self):
        source={
            "source_case_count":8,
            "seeded_bug_count":5,
            "clean_copy_count":3,
            "prior_defect_fraction":0.625,
            "phases":{
                p:{
                    "smoothed_p_fail_given_defect":0.6,
                    "smoothed_p_fail_given_clean":0.1,
                    "observed_mean_wall_seconds":0.3,
                } for p in runner.PHASES},
        }
        settings={
            "detection_benefit":16.0,
            "time_weight":0.5,
            "false_alarm_penalty":12.0,
        }
        public=adapter.public_option_model(
            "source-diagnostic",source,settings)
        self.assertEqual(public["actions"]["EXTERNAL_COMMIT"][
            "permission"],"FORBIDDEN_EXTERNAL_EFFECT")
        belief=public["proposed_prior"]
        phase,choice=adapter.decide(
            public,belief,adapter.DEFAULT_PARAMS,[],3)
        self.assertNotEqual(phase,"EXTERNAL_COMMIT")
        self.assertNotIn("EXTERNAL_COMMIT",
                         [x["action"] for x in choice["ranked"]])

    def test_source_future_work_is_a_choice_and_stop_is_possible(self):
        known={
            "source_case_count":8,
            "seeded_bug_count":5,
            "clean_copy_count":3,
            "prior_defect_fraction":0.625,
            "phases":{stage:{
                "smoothed_p_fail_given_defect":0.6,
                "smoothed_p_fail_given_clean":0.1,
                "observed_mean_wall_seconds":0.4}
                for stage in runner.PHASES},
        }
        settings={
            "detection_benefit":16.0,"time_weight":0.5,
            "false_alarm_penalty":12.0,
        }
        p=adapter.public_option_model("reviewed-case",known,settings)
        belief=p["proposed_prior"]
        phase,choice=adapter.decide(p,belief,
                                    adapter.DEFAULT_PARAMS,[],3)
        self.assertIn(phase,(*runner.PHASES,"STOP"))
        self.assertTrue(choice["ranked"])
        # Explicitly spent all the action budget => no smashes just for
        # their own sake, and no action inserted by rhetorical enthusiasm.
        stop,result=adapter.decide(
            p,belief,adapter.DEFAULT_PARAMS,
            ["INSPECT","SMASH_A","SMASH_B"],0)
        self.assertEqual(stop,"STOP")

    def test_source_tool_selection_cannot_import_sealed_test_during_calibration(self):
        root=Path(__file__).resolve().parent
        names=[]
        for name in ("fixtures.py","runner.py","worker.py","adapter.py",
                     "learn.py"):
            tree=ast.parse((root/name).read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):
                    names.extend(a.name for a in node.names)
                elif isinstance(node,ast.ImportFrom):
                    names.append(node.module)
        self.assertNotIn("sealed",names)
        self.assertNotIn("trial",names)


if __name__=="__main__":
    unittest.main()
