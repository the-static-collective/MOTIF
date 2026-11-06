"""LEGIT-013 adversarial tests: actual previous code -> profiler -> learner ->
third-party Z3 UNSAT -> source emission -> held-out exact/strong comparisons.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit012"))
from graph_reference import cases,all_states,make_graph,check_graph,scan

from formal_oracle import (
    prove_rule,independent_recurrence_proof,GUARDS,ANSWERS
)
from examiner import (
    HOLD,PARENT_SHA,actual_parent,catalog,_make_columns,
    training_graphs,trace,profile,discover,construct,
    emit,limited_load,reverify,guard_eval,answer_eval,digest
)
from classical_control import StrongClassicalDP,UnoptimizedClassicalDP
from importlib.util import spec_from_file_location, module_from_spec
_spec=spec_from_file_location("legit013_benchmark",HERE/"benchmark.py")
_benchmark=module_from_spec(_spec)
_spec.loader.exec_module(_benchmark)
evaluate=_benchmark.evaluate
heldout=_benchmark.heldout


class AlgorithmExaminerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=catalog()
        cls.parent=actual_parent()
        cls.artifact=construct()

    def test_real_previous_MOTIF_generated_source_not_a_fake_copy(self):
        self.assertTrue(callable(self.parent.solve))
        self.assertEqual(len(self.rows),152)
        self.assertEqual(self.artifact["manifest"]["parent_generated_source_sha256"],
                         PARENT_SHA)

    def test_untrusted_parent_source_hash_must_hold(self):
        # Exact pinned source is required, never trust filename alone.
        source=(HERE.parent/"legit012"/"generated"/"search_dag_v3.py").read_bytes()
        import hashlib
        self.assertEqual(hashlib.sha256(source).hexdigest(),PARENT_SHA)

    def test_training_profiler_uses_actual_previous_solver(self):
        recorded=profile()
        summary=recorded["summary"]
        self.assertEqual(summary["training_graphs"],32)
        self.assertGreater(summary["training_transitions"],0)
        self.assertGreater(summary["zero_parent_transitions"],0)
        self.assertFalse(summary["benchmark_test_cases_accessed"])
        self.assertEqual(summary["source"],"ACTUAL_GENERATED_MOTIF012_DAG_PYTHON")

    def test_training_and_heldout_seeds_do_not_overlap(self):
        self.assertEqual(profile()["summary"]["training_seeds_range"],[41000,41031])
        self.assertEqual(len(heldout()),80)
        self.assertTrue(all(len(x)>0 for x in heldout()))

    def test_generator_discovers_proved_guarded_rules(self):
        manifest=self.artifact["manifest"]
        self.assertIn(len(manifest["rules"]),(1,2))
        self.assertGreater(manifest["external_smt_proved_hypotheses"],0)
        for rule in manifest["rules"]:
            self.assertIn(rule["guard"],GUARDS)
            self.assertIn(rule["answer"],ANSWERS)
            self.assertEqual(rule["externally_verified_widths"],[8,152,256])
            for width in (8,152,256):
                self.assertEqual(prove_rule(rule["guard"],rule["answer"],width)["result"],
                                 "UNSAT")

    def test_SMT_actually_refutes_unsound_shortcut(self):
        for proposal in (("P_ZERO","COLUMN"),("ALWAYS","ZERO"),
                         ("P_FULL","PARENT"),("C_ZERO","PARENT")):
            counterexample=prove_rule(*proposal,152)
            self.assertEqual(counterexample["result"],"SAT")
            x=counterexample["counterexample"]
            self.assertNotEqual(x["incorrect"],x["reference"])

    def test_external_SMT_proves_sound_shortcut_for_all_BitVec_masks(self):
        for proposal in (("P_ZERO","ZERO"),("P_ZERO","PARENT"),
                         ("P_FULL","COLUMN"),("C_ZERO","ZERO"),
                         ("C_FULL","PARENT"),("P_EQUALS_C","PARENT")):
            receipt=prove_rule(*proposal,152)
            self.assertEqual(receipt["result"],"UNSAT",proposal)
            self.assertTrue(receipt["valid_all_masks"])

    def test_independent_SMT_proves_parent_monotonicity(self):
        p=independent_recurrence_proof()
        self.assertTrue(p["external_formal_checker_actually_invoked"])
        self.assertEqual(p["bitvector_width"],152)
        self.assertTrue(all(x=="UNSAT" for x in p["properties"].values()))

    def test_counterexample_transcript_is_real_and_verifiable(self):
        m=self.artifact["manifest"]
        self.assertEqual(m["genuine_smt_counterexamples"],
                         sum(x["external_smt_result"]=="SAT"
                             for x in m["examiner_transcript"]))
        for entry in m["examiner_transcript"]:
            if entry["external_smt_result"]!="SAT":
                continue
            bad=entry["counterexample"]
            rule=entry["hypothesis"]
            self.assertTrue(guard_eval(rule["guard"],bad["parent"],
                                       bad["column"],(1<<152)-1))
            self.assertNotEqual(
                answer_eval(rule["answer"],bad["parent"],bad["column"],(1<<152)-1),
                bad["parent"]&bad["column"])

    def test_generated_python_contains_actual_guard_logic(self):
        code=self.artifact["source"]
        self.assertIn("def solve(columns,size,ordered):",code)
        self.assertIn("intersections",code)
        self.assertIn("skips",code)
        self.assertIn("bits = p & c",code)

    def test_generated_source_requires_byte_identical_template(self):
        with self.assertRaises(HOLD):
            limited_load(self.artifact["source"]+"\n# hostile append\n",
                         self.artifact["manifest"]["rules"])

    def test_generated_source_cannot_gain_python_import_or_shell(self):
        with self.assertRaises(HOLD):
            limited_load(self.artifact["source"]+"\nimport subprocess\n",
                         self.artifact["manifest"]["rules"])

    def test_unknown_dangerous_rule_rejected(self):
        with self.assertRaises(HOLD):
            emit([{"guard":"ANY_PYTHON","answer":"PARENT"}])

    def test_manifest_hash_mutation_holds(self):
        bad=deepcopy(self.artifact)
        bad["manifest"]["source_sha256"]="0"*64
        with self.assertRaises(HOLD):
            reverify(bad)

    def test_rehashed_live_permission_mutation_holds(self):
        bad=deepcopy(self.artifact)
        bad["manifest"]["generated_python_source_in_production"]=True
        raw={k:v for k,v in bad["manifest"].items() if k!="sha256"}
        bad["manifest"]["sha256"]=digest(raw)
        with self.assertRaises(HOLD):
            reverify(bad)

    def test_altered_rule_cannot_pass_rehashed_manifest(self):
        bad=deepcopy(self.artifact)
        bad["manifest"]["rules"][0]["answer"]="FULL"
        raw={k:v for k,v in bad["manifest"].items() if k!="sha256"}
        bad["manifest"]["sha256"]=digest(raw)
        with self.assertRaises(HOLD):
            reverify(bad)

    def test_proof_gate_mandatory_before_real_execution(self):
        receipt=reverify(self.artifact)
        self.assertTrue(receipt["external_formal_solver_actually_invoked"])
        self.assertFalse(receipt["automatic_promotion_permitted"])
        self.assertEqual(receipt["z3_widths_checked"],[8,152,256])

    def test_generated_solver_preserves_full_finite_lattice(self):
        full=check_graph(make_graph("Complete",all_states()))
        cols=_make_columns(self.rows)
        old,_=self.parent.solve(cols,len(self.rows),full)
        current,_=self.artifact["solver"](cols,len(self.rows),full)
        strong,_=StrongClassicalDP(self.rows).solve(full)
        self.assertEqual(old,strong)
        self.assertEqual(current,strong)
        self.assertEqual(len(strong),6561)

    def test_all_80_heldout_graphs_match_strong_optimized_DP(self):
        cols=_make_columns(self.rows)
        strong=StrongClassicalDP(self.rows)
        for graph in heldout():
            old,_=self.parent.solve(cols,len(self.rows),graph)
            current,_=self.artifact["solver"](cols,len(self.rows),graph)
            control,_=strong.solve(graph)
            self.assertEqual(old,control)
            self.assertEqual(current,control)

    def test_committed_generated_source_matches_fresh_generator(self):
        committed=(HERE/"generated"/"optimized_search_v4.py").read_text(
            encoding="utf-8")
        self.assertEqual(committed,self.artifact["source"])
        self.assertEqual(reverify({"source":committed,
                                   "manifest":self.artifact["manifest"]})
                         ["status"],"EXTERNAL_SMT_VERIFIED_TYPED_REWRITE")

    def test_committed_formal_certificate_matches_new_Z3_replay(self):
        committed=json.loads((HERE/"generated"/"formal_certificate.json").read_text(
            encoding="utf-8"))
        # SMT SAT models are valid counterexamples, not unique canonical
        # assignments. A future Z3 replay can choose a different model.
        # Recheck stored counterexamples and match the PROVED semantics.
        archive=committed["source_manifest"]
        latest=self.artifact["manifest"]
        self.assertEqual(archive["rules"],latest["rules"])
        self.assertEqual(archive["source_sha256"],latest["source_sha256"])
        self.assertEqual(archive["genuine_smt_counterexamples"],
                         latest["genuine_smt_counterexamples"])
        for event in archive["examiner_transcript"]:
            if event["external_smt_result"]!="SAT":
                continue
            cex=event["counterexample"]
            rule=event["hypothesis"]
            self.assertTrue(guard_eval(rule["guard"],cex["parent"],
                                       cex["column"],(1<<152)-1))
            self.assertEqual(cex["reference"],cex["parent"]&cex["column"])
            self.assertNotEqual(cex["incorrect"],cex["reference"])
        verified=reverify({"source":self.artifact["source"],
                           "manifest":archive})
        self.assertEqual(committed["formal_verification"],verified)
        self.assertEqual(committed["source_sha256"],latest["source_sha256"])
        self.assertFalse(committed["production_write_permitted"])
        self.assertFalse(committed["automatic_algorithm_promotion"])

    def test_current_generation_has_no_production_write_permission(self):
        m=self.artifact["manifest"]
        self.assertEqual(m["status"],"PROOF_GATED_DRAFT_ONLY")
        self.assertFalse(m["generated_python_source_in_production"])
        self.assertFalse(m["proof_independent_specification_authorship"])
        self.assertFalse(m["real_world_authority"])

    def test_end_to_end_verified_and_classical_controls(self):
        receipt,outputs=evaluate()
        self.assertEqual(receipt["experiment"],"MOTIF-LEGIT-013")
        self.assertEqual(receipt["heldout_graphs"],80)
        self.assertEqual(receipt["heldout_disagreements"],0)
        self.assertEqual(receipt["full_finite_search_cases_checked"],6561)
        self.assertGreater(receipt["heldout_state_outputs_verified"],10000)
        self.assertFalse(receipt["algorithmic_superiority_over_optimized_classical_proved"])
        self.assertFalse(outputs["receipt"]["production_write_permitted"])
        self.assertFalse(outputs["receipt"]["automatic_algorithm_promotion"])
        self.assertEqual(outputs["source"],self.artifact["source"])

if __name__=="__main__":
    unittest.main()
