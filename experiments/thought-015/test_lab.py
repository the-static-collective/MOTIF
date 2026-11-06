"""THOUGHT-015 developer/tester adversarial tests; offline and deterministic."""
from __future__ import annotations
import ast
import copy
import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from solver_factory import Config, PatchError, SCHEMA, REPAIRS, verify_proposal, apply_repair, generate_source, source_hash
from oracle import independent_min_cost, check_answer, SpecimenError
from fixtures import DEV, SAFETY, AUDIT, STRESS
from lab import TinyDiagnosticModel, run_experiment, evaluate_in_subprocess, LabError, digest
from benchmark import main


class DeveloperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result,cls.source,cls.diff=run_experiment()

    def test_actual_learned_model_runs_and_diagnoses_development_cases(self):
        m=TinyDiagnosticModel()
        for description,label in [
            ("A two leg route is cheaper than the first direct route despite more steps", "WEIGHTED_PRIORITY"),
            ("The cheapest direct path exceeds the risk budget; a safer expensive path is valid", "ENFORCE_BUDGET"),
            ("An alternate arrival at the same node has lower risk, allowing the goal", "RESOURCE_STATE"),
            ("A later arrival improves the cost of an already discovered node", "RELAX_IMPROVED"),
        ]:
            self.assertEqual(m.predict(description),label)
        self.assertEqual(len(m.used),4)

    def test_source_generator_accepts_only_typed_booleans(self):
        s=generate_source(Config())
        self.assertIsInstance(ast.parse(s),ast.Module)
        self.assertNotIn("urllib",s)
        self.assertNotIn("subprocess",s)
        with self.assertRaises(PatchError):generate_source({"weighted_priority":True})
        with self.assertRaises(TypeError):Config(weighted_priority=True,custom_import="os")
        with self.assertRaises(PatchError):apply_repair(Config(), {"script":"import os"})

    def test_model_cannot_propose_arbitrary_source_or_effects(self):
        good={"schema":SCHEMA,"repair":"WEIGHTED_PRIORITY","reason":"fix path ordering",
              "proposer":"synthetic learned model"}
        for value in [
            {**good,"python":"__import__('os').system('touch /tmp/unsafe')"},
            {**good,"repair":"EXECUTE_COMMAND"},
            {**good,"repair":"PEN_COMMIT"},
            {**good,"reason":"rm\n-rf /"},
            {**good,"schema":"anything.v2"},
        ]:
            with self.subTest(value=value):
                with self.assertRaises(PatchError):verify_proposal(value)
        self.assertEqual(apply_repair(Config(),good),Config(weighted_priority=True))
        with self.assertRaises(PatchError):apply_repair(Config(weighted_priority=True),good)

    def test_generated_python_really_executes_in_a_separate_process(self):
        a=evaluate_in_subprocess(Config(),DEV)
        b=evaluate_in_subprocess(Config(True,True,True,True),DEV)
        self.assertEqual(a["passed"],0)
        self.assertEqual(b["passed"],8)
        self.assertNotEqual(a["source_sha256"],b["source_sha256"])

    def test_independent_oracle_does_not_trust_reported_cost(self):
        p=DEV[0]["problem"]
        self.assertEqual(independent_min_cost(p)[0],2)
        self.assertFalse(check_answer(p,{"cost":2,"risk":0,"path":[0,3]}))
        self.assertTrue(check_answer(p,{"cost":2,"risk":0,"path":[0,1,3]}))
        with self.assertRaises(SpecimenError):independent_min_cost({"n":123})

    def test_development_loop_performs_multiple_sequential_model_revisions(self):
        r=self.result
        self.assertEqual(r["staged_repair_sequence"],list(REPAIRS))
        self.assertEqual(r["development"],{"before":0,"after":8,"total":8})
        self.assertEqual(len(r["proposals"]),4)
        self.assertEqual(r["proposals"][0]["status"],"STAGED_NEUTRAL_IN_SCRATCH")
        self.assertTrue(all(p["external_authority"]=="NONE" for p in r["proposals"]))
        self.assertEqual(r["model_kind"],"TRAINED_NAIVE_BAYES_REPAIR_DIAGNOSTIC_NOT_LLM")

    def test_independent_frozen_audit_and_counterexample_search(self):
        r=self.result
        self.assertEqual(r["status"],"PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED")
        self.assertEqual(r["audit"],{"before":50,"after":60,"total":60})
        self.assertEqual(r["stress"],{"after":55,"total":55})
        self.assertEqual(r["safety"]["after"],r["safety"]["total"])
        self.assertTrue(r["frozen_audit_inspected_after_proposals"])
        self.assertIsNone(r["counterexample"])

    def test_real_patch_is_generated_but_not_installed(self):
        r=self.result
        self.assertTrue(self.diff.startswith("--- experiments/thought-015/reference_solver.py"))
        self.assertIn("+WEIGHTED_PRIORITY = True",self.diff)
        self.assertIn("+ENFORCE_BUDGET = True",self.diff)
        self.assertIn("+RESOURCE_STATE = True",self.diff)
        self.assertIn("+RELAX_IMPROVED = True",self.diff)
        self.assertFalse(r["installed"])
        self.assertTrue(r["operator_review_required"])
        self.assertFalse(r["model_authored_python_source"])
        self.assertEqual(source_hash(self.source),r["candidate_source_sha256"])

    def test_heldout_evaluation_is_unavailable_to_proposer(self):
        class GuardDeveloper:
            model_kind="TEST_PROPOSER_SEES_ONLY_DEVELOPMENT"
            def __init__(self):self.rounds=[]
            def propose(self, failures, current, rejected):
                self.rounds.append([x["description"] for x in failures])
                for repair,flag in [("WEIGHTED_PRIORITY","weighted_priority"),
                                    ("ENFORCE_BUDGET","enforce_budget"),
                                    ("RESOURCE_STATE","resource_state"),
                                    ("RELAX_IMPROVED","relax_improved")]:
                    if not getattr(current,flag):
                        return {"schema":SCHEMA,"repair":repair,"reason":"test-only ranked edit",
                                "proposer":"local test proposer"}
                return None
        dev=GuardDeveloper()
        result,_,_=run_experiment(proposer=dev)
        self.assertEqual(result["status"],"PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED")
        joined=" ".join(sum(dev.rounds,[]))
        self.assertNotIn("unseen synthetic graph",joined)

    def test_model_refusal_results_in_hold_without_effect(self):
        class Refuser:
            model_kind="NO_MODEL_PROPOSALS"
            def propose(self,failures,current,rejected):return None
        r,source,diff=run_experiment(proposer=Refuser())
        self.assertEqual(r["status"],"HOLD_AUDIT_OR_COUNTEREXAMPLE")
        self.assertFalse(r["installed"])
        self.assertEqual(r["candidate_config"],Config().as_dict())
        self.assertEqual(diff,"")

    def test_rejected_patch_does_not_apply_or_mutate_source(self):
        class Malicious:
            model_kind="UNTRUSTED"
            def propose(self,failures,current,rejected):
                return {"schema":SCHEMA,"repair":"WEIGHTED_PRIORITY","reason":"run shell",
                        "proposer":"malicious", "python":"os.system('touch /tmp/pwned')"}
        r,s,_=run_experiment(proposer=Malicious())
        self.assertEqual(r["status"],"HOLD_AUDIT_OR_COUNTEREXAMPLE")
        self.assertEqual(r["proposals"][0]["status"],"HOLD_INVALID_PROPOSAL")
        self.assertEqual(source_hash(s),source_hash(generate_source(Config())))

    def test_counterexample_causes_hold_even_after_dev_improvement(self):
        # A false or inconsistent external audit objective cannot be used to
        # certify the patch. Here the independent comparator is the oracle,
        # so an incompatible graph with duplicate edges must fail closed.
        bad=copy.deepcopy(AUDIT[:2])
        bad[0]["problem"]["edges"].append(copy.deepcopy(bad[0]["problem"]["edges"][0]))
        with self.assertRaises(SpecimenError):run_experiment(audit=bad)

    def test_determinism_and_receipt_integrity(self):
        repeat,code,diff=run_experiment()
        self.assertEqual(repeat,self.result)
        self.assertEqual(code,self.source)
        self.assertEqual(diff,self.diff)
        r={k:v for k,v in repeat.items() if k!="receipt_digest"}
        self.assertEqual(digest(r),repeat["receipt_digest"])

    def test_enforced_budgets_and_no_effectful_code(self):
        with self.assertRaises(LabError):run_experiment(rounds=900)
        with self.assertRaises(LabError):evaluate_in_subprocess(Config(),DEV*20)
        for snippet in ["open(","socket.","os.system(","eval(","exec("]:
            self.assertNotIn(snippet,self.source)
        self.assertEqual(self.result["external_authority"],"NONE")
        self.assertEqual(self.result["pen_state"],"UNCHANGED")

    def test_complete_reproduction_writes_only_operator_review_artifacts(self):
        with TemporaryDirectory() as folder:
            r=main(folder)
            self.assertEqual(r["status"],"PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED")
            entries={p.name for p in Path(folder).iterdir()}
            self.assertEqual(entries,{"reference_solver.py","candidate_solver.py",
                                      "candidate.diff","experiment-results.json"})
            loaded=json.loads((Path(folder)/"experiment-results.json").read_text())
            self.assertEqual(loaded["receipt_digest"],self.result["receipt_digest"])

if __name__ == "__main__":unittest.main()
