"""LEGIT-012 falsifiers for counterexample-generated solver transformation.

Most important: this tests actual LEGIT-011 source input, not a rewritten
toy copy. A separate conventional oracle examines every one of the 6561
possible eight-row partial truth specifications. Strong optimized DP is
compared on unseen seeded graph workloads.

Every program remains review-only. Exact finite verification here does not
establish general-purpose SMT proof or independent third-party validation.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit010"))
from bootstrap import invent_successor_search,_compressed_candidates
from graph_reference import (
    SCHEMA,all_states,make_graph,check_graph,scan,classical_dp,StrongCachedDP,cases
)
from transform import (
    HOLD,RECIPE_OPERATORS,OLD_SHA,prior_search,recipes,interpreter,
    learn_transform,emit_source,static_source_review,load_source,produce,verify,
    _independent_local_proof,digest
)
from importlib.util import spec_from_file_location,module_from_spec
_spec=spec_from_file_location("legit012_benchmark",HERE/"benchmark.py")
_bench=module_from_spec(_spec)
_spec.loader.exec_module(_bench)
execute=_bench.execute


class CertifiedTransformerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=_compressed_candidates(invent_successor_search()["algorithm"])
        cls.artifact=produce(cls.rows)
        cls.previous=prior_search()
        cls.columns=cls.previous.build_index(cls.rows)
        cls.solver=staticmethod(cls.artifact["generated_solver"])

    def test_real_previous_source_loaded_and_fingerprinted(self):
        self.assertEqual(len(self.rows),152)
        self.assertTrue(callable(self.previous.choose))
        self.assertTrue(callable(self.previous.build_index))
        self.assertTrue(hasattr(self.previous,"IncrementalSearch"))
        self.assertEqual(self.artifact["manifest"]["parent_legit011_sha256"],OLD_SHA)

    def test_exact_twenty_four_transformations_not_free_python(self):
        self.assertEqual(len(tuple(recipes())),24)
        self.assertEqual(set(RECIPE_OPERATORS),
                         {"join","mode","pick","on_empty"})

    def test_real_semantic_counterexample_learning(self):
        meta=self.artifact["manifest"]
        self.assertGreater(meta["cegis_counterexamples"],0)
        self.assertEqual(meta["partial_truth_states_verified"],6561)
        records=meta["counterexample_transcript"]
        self.assertEqual(len(records),meta["cegis_counterexamples"]+1)
        self.assertIsNone(records[-1]["counterexample"])
        for earlier in records[:-1]:
            self.assertIsNotNone(earlier["counterexample"])
            self.assertNotEqual(earlier["counterexample"]["actual"],
                                earlier["counterexample"]["expected"])

    def test_selected_rewrite_is_parent_caching_with_intersection(self):
        self.assertEqual(self.artifact["manifest"]["transformation_recipe"],
                         {"join":"AND","mode":"REUSE_PARENT",
                          "pick":"FIRST","on_empty":"HOLD"})

    def test_generated_python_is_actually_written(self):
        code=self.artifact["source"]
        self.assertIn("def solve(columns,size,ordered):",code)
        self.assertIn("memo[before] & columns[added]",code)
        self.assertIn("memo[facts] = bits",code)
        self.assertNotIn("import os",code)
        self.assertNotIn("import subprocess",code)

    def test_full_independent_6561_state_equivalence(self):
        report=verify(self.artifact,self.rows)
        self.assertEqual(report["fully_enumerated_partial_states"],6561)
        self.assertTrue(report["strong_classical_exact_agreement"])
        self.assertFalse(report["external_formal_prover_used"])

    def test_inductive_membership_base_case_and_step(self):
        certificate=_independent_local_proof()
        self.assertEqual(certificate["membership_transitions"],4)
        self.assertIn("Structural induction",certificate["proof"])
        self.assertFalse(certificate["external_SMT_solver_invoked"])

    def test_full_lattice_has_many_parent_paths(self):
        full=make_graph("CompleteLattice",all_states())
        normalized=check_graph(full)
        self.assertEqual(len(normalized),6561)
        self.assertEqual(sum(len(parents) for _,parents in normalized),34992)
        self.assertEqual(max(len(parents) for _,parents in normalized),8)

    def test_generated_solver_equals_three_independent_references(self):
        graph=make_graph("AllPartialWorlds",all_states())
        prepared=check_graph(graph)
        a,_=self.solver(self.columns,len(self.rows),prepared)
        b,_=scan(self.rows,prepared)
        c,_=classical_dp(self.rows,prepared)
        d,_=StrongCachedDP(self.rows).solve(prepared)
        self.assertEqual(a,b)
        self.assertEqual(a,c)
        self.assertEqual(a,d)

    def test_actual_011_search_chooses_same_program_for_random_cases(self):
        for seed in (10,20,30,40,50,60):
            graph=cases(seed,16)
            ordered=check_graph(graph)
            expected,_=self.solver(self.columns,len(self.rows),ordered)
            for facts,_ in ordered:
                previous=self.previous.choose(self.columns,len(self.rows),facts)[0]
                self.assertEqual(expected[facts],previous)

    def test_two_different_parent_paths_give_same_candidate_set(self):
        full=check_graph(make_graph("Parents",all_states()))
        subset=next((facts,parents) for facts,parents in full if len(facts)==4)
        facts,parents=subset
        previous={}
        for item,priors in full:
            if len(item)>4:break
            previous[item]=self.solver(self.columns,len(self.rows),
                              full[:full.index((item,priors))+1])[0][item]
        self.assertEqual(previous[facts],
                         self.previous.choose(self.columns,len(self.rows),facts)[0])

    def test_wrong_intersection_or_and_inverted_evidence_refuted(self):
        full=check_graph(make_graph("Contrasts",all_states()))
        result,_=scan(self.rows,full)
        for policy in ({"join":"OR","mode":"REUSE_PARENT","pick":"FIRST","on_empty":"HOLD"},
                       {"join":"XOR","mode":"REUSE_PARENT","pick":"FIRST","on_empty":"HOLD"},
                       {"join":"AND","mode":"REUSE_PARENT","pick":"LAST","on_empty":"HOLD"},
                       {"join":"AND","mode":"REUSE_PARENT","pick":"FIRST","on_empty":"FALLBACK_ZERO"}):
            got,_=interpreter(policy,full,self.columns,len(self.rows))
            self.assertNotEqual(got,result,policy)

    def test_restart_variant_is_valid_but_must_use_more_updates(self):
        full=check_graph(make_graph("Repeat",all_states()))
        transformed=self.artifact["manifest"]["transformation_recipe"]
        restarted=dict(transformed,mode="RESTART_EACH_STATE")
        cache_result,cache_ops=interpreter(transformed,full,self.columns,len(self.rows))
        restart_result,restart_ops=interpreter(restarted,full,self.columns,len(self.rows))
        self.assertEqual(cache_result,restart_result)
        self.assertLess(cache_ops["bitset_updates"],restart_ops["bitset_updates"])

    def test_bad_state_order_is_rejected(self):
        graph=cases(7171,8)
        graph["nodes"]=list(reversed(graph["nodes"]))
        with self.assertRaises(ValueError):
            check_graph(graph)

    def test_missing_graph_parent_is_rejected(self):
        graph=cases(7172,8)
        node=next(r for r in graph["nodes"] if len(r["parents"])>1)
        node["parents"].pop()
        with self.assertRaises(ValueError):
            check_graph(graph)

    def test_forged_graph_parent_is_rejected(self):
        graph=cases(7173,8)
        node=next(r for r in graph["nodes"] if r["parents"])
        node["parents"]=[[]]
        if len(node["facts"])==1:
            node["parents"]=[[[0,False]]]
        with self.assertRaises(ValueError):
            check_graph(graph)

    def test_duplicate_or_contradictory_constraints_rejected(self):
        graph=cases(7174,8)
        target=next(r for r in graph["nodes"] if r["facts"])
        target["facts"].append(list(target["facts"][0]))
        with self.assertRaises(ValueError):
            check_graph(graph)

    def test_unknown_runtime_operation_rejected(self):
        bad={"join":"SHELL","mode":"REUSE_PARENT",
             "pick":"FIRST","on_empty":"HOLD"}
        with self.assertRaises(HOLD):
            emit_source(bad)

    def test_source_is_static_and_exact_template(self):
        report=static_source_review(self.artifact["source"])
        self.assertTrue(report["approved_template"])
        self.assertTrue(report["not_general_python_sandbox"])
        self.assertEqual(report["source_sha256"],
                         self.artifact["manifest"]["source_sha256"])

    def test_added_ast_safe_malicious_source_is_still_refused(self):
        source=self.artifact["source"]+"\ndef unrelated():\n    return 7\n"
        with self.assertRaises(HOLD):
            load_source(source)

    def test_external_python_import_and_eval_are_refused(self):
        for bad in (self.artifact["source"]+"\nimport os\n",
                    self.artifact["source"]+"\ndef hidden():return eval('2')\n"):
            with self.assertRaises(HOLD):
                load_source(bad)

    def test_mutated_manifest_checksum_refused(self):
        tampered={"source":self.artifact["source"],
                  "manifest":deepcopy(self.artifact["manifest"])}
        tampered["manifest"]["source_sha256"]="0"*64
        with self.assertRaises(HOLD):
            verify(tampered,self.rows)

    def test_rehashed_production_permission_cannot_be_promoted(self):
        tampered={"source":self.artifact["source"],
                  "manifest":deepcopy(self.artifact["manifest"])}
        tampered["manifest"]["production_patch_approved"]=True
        obj={k:v for k,v in tampered["manifest"].items() if k!="sha256"}
        tampered["manifest"]["sha256"]=digest(obj)
        with self.assertRaises(HOLD):
            verify(tampered,self.rows)

    def test_fresh_generation_reproducible(self):
        alternate=produce(self.rows)
        self.assertEqual(alternate["manifest"],self.artifact["manifest"])
        self.assertEqual(alternate["source"],self.artifact["source"])

    def test_repeatable_heldout_performance_record_with_matched_control(self):
        result,generated=execute()
        self.assertEqual(result["heldout_graphs"],80)
        self.assertTrue(result["strong_classical_and_generated_bitset_updates_identical"])
        self.assertTrue(result["tuned_classical_baseline_fully_included"])
        self.assertTrue(result["finite_and_inductive_proof"]["strong_classical_exact_agreement"])
        self.assertFalse(result["generated_code_has_live_authority"])
        self.assertEqual(result["new_source_template_recipe"],
                         self.artifact["manifest"]["transformation_recipe"])
        self.assertFalse(generated["manifest"]["source_eligible_for_automatic_merge"])
        self.assertEqual(result["graphs_by_family"]["LIGHT"]["graphs"],24)
        self.assertEqual(result["graphs_by_family"]["MEDIUM"]["graphs"],32)
        self.assertEqual(result["graphs_by_family"]["DENSE"]["graphs"],24)

    def test_research_hold_and_parent_integrity(self):
        m=self.artifact["manifest"]
        self.assertEqual(m["status"],"PROOF_REQUIRED_DRAFT")
        self.assertFalse(m["real_world_authority"])
        self.assertFalse(m["source_identity_authenticated"])
        self.assertFalse(m["independently_blinded_benchmark"])
        self.assertFalse(m["production_patch_approved"])

if __name__=="__main__":
    unittest.main()
