"""LEGIT-017 falsifiers for source generated tools and research workflow."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from statistics import median
from itertools import product
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from tasks import (FAMILIES,suite,check_suite,direct,strong_build,strong_ask,Task)
from toolsmith import (HOLD,STRATEGIES,emit,compile_tool,review,verify,
                       bounded_falsification)
from metatool import (compile_verifier,check_variants,VERIFIER_SOURCE)
from benchmark import (training,run,work,_select,ASSUMED_FUTURE_BATCHES,
                       TOOL_BUDGET)

class ProductivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train=suite("TRAIN")
        cls.holdout=suite("HELDOUT")
        cls.tools={family:[
            compile_tool(family,variant) for variant in STRATEGIES[family]]
            for family in FAMILIES}
        cls.meta=compile_verifier()
        cls.report,cls.bundle=run()

    def test_three_distinct_problem_domains(self):
        self.assertEqual(FAMILIES,("GRAPH","SUBSET","TEXT"))
        self.assertEqual(len(self.train),18)
        self.assertEqual(len(self.holdout),36)
        self.assertEqual(check_suite(self.train),18)
        self.assertEqual(check_suite(self.holdout),36)

    def test_training_and_heldout_are_distinct_fixed_seeds(self):
        self.assertFalse(set(t.identifier for t in self.train)&
                         set(t.identifier for t in self.holdout))
        self.assertNotEqual(self.train[0].instance,self.holdout[0].instance)
        self.assertTrue(all(t.identifier.startswith("HELDOUT") for t in self.holdout))

    def test_six_actual_algorithm_sources_compile(self):
        self.assertEqual(sum(len(x) for x in self.tools.values()),6)
        for family,group in self.tools.items():
            for tool in group:
                self.assertTrue(callable(tool["build"]))
                self.assertTrue(callable(tool["answer"]))
                self.assertEqual(tool["source"],emit(family,tool["strategy"]))
                self.assertEqual(tool["source_sha256"],
                                 sha256(tool["source"].encode()).hexdigest())

    def test_generated_sources_are_only_known_classical_templates(self):
        for family,group in self.tools.items():
            for t in group:
                review(family,t["strategy"],t["source"])
        with self.assertRaises(HOLD):
            compile_tool("GRAPH","SUBSET_BITSET")
        with self.assertRaises(HOLD):
            compile_tool("UNRECOGNIZED","GRAPH_STACK")

    def test_ast_safe_appended_python_is_still_refused(self):
        tool=self.tools["GRAPH"][0]
        altered=tool["source"]+"\ndef extra():\n    return 7\n"
        with self.assertRaises(HOLD):
            compile_tool("GRAPH",tool["strategy"],altered)

    def test_python_import_and_extra_io_cannot_be_added(self):
        tool=self.tools["TEXT"][0]
        with self.assertRaises(HOLD):
            compile_tool("TEXT",tool["strategy"],tool["source"]+"\nimport os\n")
        with self.assertRaises(HOLD):
            compile_tool("TEXT",tool["strategy"],tool["source"]+"\nopen('x','w')\n")

    def test_all_six_generated_solvers_correct_on_training(self):
        for family,tools in self.tools.items():
            for tool in tools:
                receipt=verify(tool,self.train)
                self.assertEqual(receipt["tests"],240)
                self.assertTrue(receipt["independent_exact_answers_match"])

    def test_all_six_solvers_correct_on_separate_holdout(self):
        for family,tools in self.tools.items():
            for tool in tools:
                receipt=verify(tool,self.holdout)
                self.assertEqual(receipt["tests"],864)

    def test_small_complete_finite_problem_domains(self):
        counts={"GRAPH":576,"SUBSET":832,"TEXT":384}
        for family,tools in self.tools.items():
            for tool in tools:
                res=bounded_falsification(tool)
                self.assertEqual(res["exact_cases_checked"],counts[family])

    def test_strong_conventional_solvers_agree_with_independent_oracle(self):
        for task in self.holdout:
            ctx=strong_build(task)
            for query in task.queries:
                self.assertEqual(strong_ask(task,ctx,query),direct(task,query))

    def test_meta_instrument_is_a_real_shared_executable_source(self):
        self.assertTrue(callable(self.meta["build"]))
        self.assertTrue(callable(self.meta["answer"]))
        self.assertEqual(self.meta["source"],VERIFIER_SOURCE)
        self.assertEqual(self.meta["source_sha256"],
                         sha256(VERIFIER_SOURCE.encode()).hexdigest())
        self.assertFalse(self.meta["not_general_python_sandbox"] is False)

    def test_meta_instrument_checks_every_candidate_in_all_domains(self):
        direct_receipt=check_variants(self.train,self.tools,"RECHECK")
        cache_receipt=check_variants(self.train,self.tools,"CACHE",self.meta)
        strong_receipt=check_variants(self.train,self.tools,"STRONG")
        self.assertEqual(direct_receipt["checked_tool_query_pairs"],1440)
        self.assertEqual(cache_receipt["checked_tool_query_pairs"],1440)
        self.assertEqual(strong_receipt["checked_tool_query_pairs"],1440)
        self.assertEqual(direct_receipt["reference_calls"],1440)
        self.assertEqual(cache_receipt["reference_calls"],720)
        self.assertEqual(strong_receipt["reference_calls"],720)

    def test_meta_tool_can_reuse_optimized_independently_checked_reference(self):
        older=check_variants(self.train,self.tools,"CACHE",self.meta)
        better=check_variants(self.train,self.tools,"IMPROVED_CACHE",self.meta)
        classical=check_variants(self.train,self.tools,"STRONG")
        self.assertEqual(older["checked_tool_query_pairs"],1440)
        self.assertEqual(better["checked_tool_query_pairs"],1440)
        self.assertEqual(classical["checked_tool_query_pairs"],1440)
        self.assertEqual(better["reference_calls"],720)
        self.assertEqual(classical["reference_calls"],720)
        self.assertEqual(better["source"],
                         "CONVENTIONAL_CLASSICAL_PRECOMPUTED_REFERENCE")

    def test_research_about_research_selects_meta_witness_from_training_only(self):
        report=self.report
        meta=report["second_order_generated_verifier"]
        self.assertEqual(meta["training_selected_verifier_mode"],
                         report["frozen_plan"]["research_verifier_mode"])
        self.assertEqual(self.bundle["selected_research_verifier_mode"],
                         report["frozen_plan"]["research_verifier_mode"])
        self.assertTrue(meta["heldout_timing_was_not_used_for_verifier_selection"])
        self.assertIn(meta["training_selected_verifier_mode"],
                      ("CACHE","IMPROVED_CACHE"))
        self.assertIn("IMPROVED_CACHE",meta["test_ms"])
        self.assertEqual(len(meta["test_ms"]),4)
        self.assertFalse(meta["proves_future_research_discovery_time_reduced"])

    def test_meta_source_detects_duplicate_or_missing_witnesses(self):
        with self.assertRaises(ValueError):
            self.meta["build"]([(("T",0),True),(("T",0),False)])
        saved=self.meta["build"]([(("X",1),False)])
        with self.assertRaises(KeyError):
            self.meta["answer"](saved,("Y",1))

    def test_selection_budget_exact_classical_optimizer(self):
        toy={
            "GRAPH":{"projected_net_ms":12},
            "SUBSET":{"projected_net_ms":9},
            "TEXT":{"projected_net_ms":-10},
        }
        self.assertEqual(_select(toy),("GRAPH","SUBSET"))
        self.assertEqual(_select({k:{"projected_net_ms":-1}
                                  for k in FAMILIES}),())

    def test_frozen_selection_uses_training_only(self):
        r=self.report
        self.assertFalse(r["training_source_selection_never_used_heldout"] is False)
        self.assertEqual(r["training_tasks"],18)
        self.assertEqual(r["heldout_tasks"],36)
        self.assertLessEqual(len(r["frozen_plan"]["selected"]),TOOL_BUDGET)
        self.assertEqual(r["frozen_plan"]["hypothetical_horizon"],
                         ASSUMED_FUTURE_BATCHES)
        self.assertFalse(r["gates"]["independent_blinded_task_author"])

    def test_all_heldout_queries_checked_and_benchmark_competitors_present(self):
        r=self.report
        self.assertEqual(r["heldout_verified_query_answers"],36*72)
        self.assertEqual(set(r["heldout_portfolio_ms"]),
                         {"DIRECT","STRONG","FROZEN_PORTFOLIO"})
        self.assertEqual(set(r["heldout_family_ms"]),set(FAMILIES))
        self.assertTrue(all(v["repeat_count"]==11 for v
                            in r["heldout_portfolio_ms"].values()))
        self.assertTrue(all(v["median_wall_ms"]>0
                            for v in r["heldout_portfolio_ms"].values()))

    def test_verifier_ablation_includes_full_priming_cost_and_control(self):
        r=self.report["second_order_generated_verifier"]
        self.assertEqual(r["no_cache_reference_calls"],5184)
        self.assertEqual(r["with_tool_reference_calls"],2592)
        self.assertEqual(r["strong_classical_reference_calls"],2592)
        self.assertTrue(r["proves_future_research_discovery_time_reduced"] is False)
        self.assertTrue(r["does_not_establish_superiority_to_classical_memoization"])
        self.assertIn("STRONG",r["test_ms"])
        self.assertIn("CACHE",r["test_ms"])
        self.assertIn("RECHECK",r["test_ms"])

    def test_metadata_disallows_automatic_deployment_or_compounding_claims(self):
        r=self.report
        self.assertEqual(r["status"],
            "HOLD_RESEARCH_ONLY_INDEPENDENT_COMPOUNDING_NOT_DEMONSTRATED")
        self.assertFalse(r["second_order_research_discovery_compounding_confirmed"])
        self.assertFalse(r["automatically_installed_tools"])
        self.assertFalse(r["general_superiority_over_classical"])
        self.assertEqual(r["production_actions"],0)
        self.assertFalse(r["gates"]["causal_successive_discoveries_demonstrated"])

    def test_actual_generated_source_bundle_matches_frozen_manifest(self):
        source=self.bundle
        self.assertEqual(source["frozen_plan_sha256"],
                         self.report["frozen_plan_sha256"])
        self.assertFalse(source["production_write_approved"])
        for family,text in source["selected_tools"].items():
            strategy=self.report["selected_source_manifest"][family]["strategy"]
            self.assertEqual(text,emit(family,strategy))
            self.assertEqual(sha256(text.encode()).hexdigest(),
                             source["selected_sources_verified"][family])
        self.assertEqual(source["research_meta_tool"],VERIFIER_SOURCE)

    def test_new_research_cannot_claim_general_proof_or_independent_author(self):
        r=self.report
        self.assertFalse(r["external_mathematical_prover_invoked_for_general_tools"])
        self.assertTrue(r["all_task_families_author_created"])
        self.assertFalse(r["gates"]["source_custody_external_verified"])
        self.assertFalse(r["gates"]["full_test_development_cost_measured"])
        self.assertFalse(r["second_order_research_discovery_compounding_confirmed"])

if __name__=="__main__":
    unittest.main()
