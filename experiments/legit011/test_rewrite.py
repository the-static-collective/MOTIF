"""LEGIT-011: self-modifying search *under verified, typed source templates*.

Counterexample tests ensure the generated replacement has exact equivalence
to the existing LEGIT-010 search on 3^8 partial evidence configurations,
including unreachable and contradictory combinations. Test that its own
incremental modification is reusable in subsequent CEGIS rounds.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from itertools import product
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit010"))
from bootstrap import invent_successor_search, _compressed_candidates
from independent_oracle import TRI_TASKS,UNREACHABLE,TernaryVerifier

from rewrite import (HOLD,produce_upgrade,verify_upgrade,load_generated_source,
                     static_source_validation,emit_source,apply_recipe,recipes,
                     build_columns,synthesize_rewrite,validate_recipe)
from search_reference import (ScanOracle,StrongClassicalIndex,states,
                              independent_update_check)
from importlib.util import spec_from_file_location,module_from_spec
_spec=spec_from_file_location("legit011_local_benchmark",HERE/"benchmark.py")
_benchmark=module_from_spec(_spec)
_spec.loader.exec_module(_benchmark)
execute=_benchmark.execute
exhaustive_partial_check=_benchmark.exhaustive_partial_check
learn_three=_benchmark.learn_three


class SelfRewriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upgrade=produce_upgrade()
        cls.candidates=cls.upgrade["candidate_rows"]
        cls.generated=load_generated_source(cls.upgrade["source"])
        cls.reference=ScanOracle(cls.candidates)
        cls.strong=StrongClassicalIndex(cls.candidates)

    def test_existing_motif_generators_built_actual_candidate_catalog(self):
        self.assertEqual(len(self.candidates),152)
        self.assertEqual(len({r["truth_mask"] for r in self.candidates}),152)
        self.assertTrue(all(self.candidates[i]["cost"]<=self.candidates[i+1]["cost"]
                            for i in range(151)))

    def test_source_rewrite_was_selected_by_real_counterexamples(self):
        row=self.upgrade["manifest"]
        self.assertGreater(row["meta_counterexamples"],0)
        self.assertEqual(row["finite_verification_states"],6561)
        self.assertEqual(len(row["meta_transcript"]),row["meta_counterexamples"]+1)
        self.assertIsNone(row["meta_transcript"][-1]["counterexample"])

    def test_each_meta_counterexample_proves_previous_rewrite_wrong(self):
        index=build_columns(self.candidates)
        for phase in self.upgrade["manifest"]["meta_transcript"]:
            witness=phase["counterexample"]
            if witness is None:
                continue
            partial=tuple((i,bool(v)) for i,v in witness["partial"])
            actual=apply_recipe(phase["candidate_recipe"],index,len(self.candidates),partial)
            self.assertEqual(actual,witness["candidate_index"])
            self.assertNotEqual(actual,witness["expected_index"])
            self.assertEqual(witness["expected_index"],self.reference.query(partial)[0])

    def test_rewrite_generation_is_deterministic(self):
        first=synthesize_rewrite(self.candidates)
        second=synthesize_rewrite(self.candidates)
        self.assertEqual(first,second)
        self.assertEqual(first["program_recipe"],self.upgrade["manifest"]["generated_recipe"])

    def test_generated_recipe_is_genuine_and_not_a_strawman_scan(self):
        recipe=self.upgrade["manifest"]["generated_recipe"]
        self.assertEqual(recipe,{"combine":"AND","invert":False,
                                  "pick":"FIRST","empty":"HOLD"})
        self.assertIn("columns[row,flag]",self.upgrade["source"])
        self.assertIn("bits = bits & column",self.upgrade["source"])
        self.assertNotIn("for program in candidates:",self.upgrade["source"].split("def choose(")[1])

    def test_independent_verifier_challenges_wrong_join(self):
        base=deepcopy(self.upgrade["manifest"]["generated_recipe"])
        base["combine"]="OR"
        cols=build_columns(self.candidates)
        witness=self.reference.challenge(lambda q:apply_recipe(base,cols,len(self.candidates),q))
        self.assertIsNotNone(witness)

    def test_independent_verifier_challenges_wrong_provenance_mapping(self):
        base=deepcopy(self.upgrade["manifest"]["generated_recipe"])
        base["invert"]=True
        cols=build_columns(self.candidates)
        witness=self.reference.challenge(lambda q:apply_recipe(base,cols,len(self.candidates),q))
        self.assertIsNotNone(witness)

    def test_independent_verifier_challenges_wrong_minimum_selection(self):
        base=deepcopy(self.upgrade["manifest"]["generated_recipe"])
        base["pick"]="LAST"
        cols=build_columns(self.candidates)
        witness=self.reference.challenge(lambda q:apply_recipe(base,cols,len(self.candidates),q))
        self.assertIsNotNone(witness)

    def test_unreachable_partial_spec_is_preserved(self):
        impossible=next((q for q in states() if self.reference.query(q)[0] is None),None)
        self.assertIsNotNone(impossible)
        index=self.generated["build_index"](self.candidates)
        self.assertIsNone(self.generated["choose"](index,len(self.candidates),impossible)[0])

    def test_generated_source_is_python_not_only_a_json_description(self):
        source=self.upgrade["source"]
        self.assertIn("def choose(",source)
        self.assertIn("class IncrementalSearch:",source)
        self.assertIn("def build_index(",source)
        self.assertEqual(self.generated["SCHEMA"],"motif.generated-search-rewrite.v1")
        self.assertTrue(self.generated["RESEARCH_HOLD"])

    def test_generated_source_static_verification(self):
        result=static_source_validation(self.upgrade["source"])
        self.assertEqual(result["status"],"STATIC_SOURCE_TEMPLATE_CHECK_PASSED")
        self.assertTrue(result["not_a_general_security_sandbox"])

    def test_generated_source_rejects_external_import(self):
        with self.assertRaises(HOLD):
            static_source_validation("import socket\n"+" "*1)

    def test_generated_source_rejects_direct_eval_and_file_open(self):
        for src in ("def x(): return eval('4')\n",
                    "def x(): return open('/etc/passwd')\n",
                    "def x(): return globals()\n"):
            with self.assertRaises(HOLD):
                static_source_validation(src)

    def test_generated_source_rejects_reserved_attribute_access(self):
        with self.assertRaises(HOLD):
            static_source_validation("def x(y): return y.__class__\n")

    def test_arbitrary_string_not_accepted_as_generated_source(self):
        with self.assertRaises(HOLD):
            load_generated_source("def f(): return 1\n")

    def test_unregistered_program_recipes_are_blocked(self):
        for code in ({"combine":"PICKLE","invert":False,"pick":"FIRST","empty":"HOLD"},
                     {"combine":"AND","invert":False,"pick":"FIRST",
                      "empty":"HOLD","shell":"curl"}):
            with self.assertRaises(HOLD):
                validate_recipe(code)

    def test_previous_generated_and_is_reused_for_incremental_rewrite(self):
        update=self.upgrade["update"]
        self.assertTrue(update["previous_generation_synthesizer_used"])
        self.assertEqual(update["source_cartridge"]["truth_mask"],8)
        self.assertEqual(update["source_cartridge"]["gate_count"],2)
        self.assertTrue(update["independent_four_case_verifier"]["complete"])
        self.assertTrue(independent_update_check(lambda a,b:a and b)["complete"])

    def test_wrong_update_operator_gets_independent_counterexample(self):
        for fn in (lambda a,b:a or b,lambda a,b:a!=b):
            result=independent_update_check(fn)
            self.assertFalse(result["complete"])
            self.assertIsNotNone(result["counterexample"])

    def test_full_exact_search_equivalence_6561_states(self):
        report=verify_upgrade(self.upgrade["manifest"],
                              self.upgrade["source"],self.candidates)
        self.assertEqual(report["partial_truth_tables_checked"],6561)
        self.assertTrue(report["existing_legit010_search_behavior_preserved"])

    def test_incremental_verification_each_prefix_of_6561_states(self):
        result=exhaustive_partial_check(self.candidates,self.generated)
        self.assertEqual(result["all_partial_evidence_states_checked"],6561)
        self.assertEqual(result["errors"],0)
        self.assertTrue(result["independent_exact_classical_index_tied"])
        self.assertGreater(result["monotone_incremental_prefixes_checked"],20000)

    def test_strong_classical_index_ties_generated_source(self):
        index=self.generated["build_index"](self.candidates)
        for q in states():
            expected=self.strong.select(q)[0]
            observed=self.generated["choose"](index,len(self.candidates),q)[0]
            self.assertEqual(expected,observed)

    def test_proof_preserves_all_unseen_ternary_task_searches(self):
        for task in TRI_TASKS+(UNREACHABLE,):
            result=learn_three(TernaryVerifier(task),self.candidates,
                               self.generated,"GENERATED_INCREMENTAL")
            if task==UNREACHABLE:
                self.assertIsNone(result["program"])
                self.assertEqual(result["status"],"HOLD_UNREACHABLE")
            else:
                self.assertIsNotNone(result["program"])
                self.assertEqual(result["status"],"FULL_DOMAIN_PROVED")
                self.assertTrue(result["all_search_engines_agree"])

    def test_generated_rewrite_rejects_tampered_source_in_manifest(self):
        bad=deepcopy(self.upgrade["manifest"])
        bad["source_sha256"]="0"*64
        with self.assertRaises(HOLD):
            verify_upgrade(bad,self.upgrade["source"],self.candidates)

    def test_rehashed_manifest_cannot_forge_unsupported_scope(self):
        from rewrite import digest
        bad=deepcopy(self.upgrade["manifest"])
        bad["status"]="AUTONOMOUS_PRODUCTION_PATCH"
        raw={k:v for k,v in bad.items() if k!="sha256"}
        bad["sha256"]=digest(raw)
        with self.assertRaises(HOLD):
            verify_upgrade(bad,self.upgrade["source"],self.candidates)

    def test_full_benchmark_repeatable_and_strong_baseline_tied(self):
        a,b=execute()
        self.assertEqual((a,b),execute())
        self.assertTrue(a["prior_010_programs_reproduced"])
        self.assertTrue(a["classical_index_control_equivalent"])
        self.assertEqual(a["full_finite_search_evaluation"]["all_partial_evidence_states_checked"],6561)
        self.assertEqual(a["full_finite_search_evaluation"]["errors"],0)
        self.assertFalse(a["independently_author_blinded"])
        self.assertTrue(a["no_production_changes"])
        self.assertEqual(a["total_typed_source_rewrites"],2)
        self.assertFalse(b["bundle"]["committed_to_main"])
        self.assertEqual(len(a["new_successor_task_receipts"]),7)

    def test_committed_generated_source_exactly_matches_new_replay(self):
        source=(HERE/"generated"/"search_v2.py").read_text(encoding="utf-8")
        self.assertEqual(source,self.upgrade["source"])
        result=verify_upgrade(self.upgrade["manifest"],source,self.candidates)
        self.assertEqual(result["partial_truth_tables_checked"],6561)

    def test_committed_manifest_matches_reverified_replay(self):
        saved=json.loads((HERE/"generated"/"search_rewrite_manifest.json").read_text(
            encoding="utf-8"))
        actual,generated=execute()
        self.assertEqual(saved,generated["bundle"])
        self.assertEqual(saved["source_code_sha256"],
                         self.upgrade["source_checked"]["source_sha256"])
        self.assertFalse(saved["external_network_access_granted"])
        self.assertEqual(saved["status"],"DRAFT_SOURCE_CHANGE_REQUIRES_HUMAN_REVIEW")

    def test_non_template_code_fails_even_if_ast_safe_and_same_header(self):
        changed=self.upgrade["source"]+"def sneaky():\n    return 42\n"
        self.assertEqual(static_source_validation(changed)["status"],
                         "STATIC_SOURCE_TEMPLATE_CHECK_PASSED")
        with self.assertRaises(HOLD):
            load_generated_source(changed)

    def test_generated_file_receipts_are_only_research(self):
        manifest=self.upgrade["manifest"]
        self.assertFalse(manifest["source_changes_production"])
        self.assertFalse(manifest["unrestricted_python_self_edit"])
        self.assertFalse(manifest["real_world_authority"])
        self.assertEqual(manifest["status"],"DRAFT_SOURCE_TRANSFORMATION_ONLY")


if __name__=="__main__":
    unittest.main()
