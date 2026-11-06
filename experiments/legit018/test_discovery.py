"""LEGIT-018 adversarial discovery tests.

Three tests of epistemic integrity:
- "reachable AND subset-sum" is false for constrained paths;
- a source derived from a previous certified program can be adapted to
  a new constraint, but finite-check and reference validation remain
  mandatory;
- providing a larger grammar is NOT evidence of general or independent
  ability to discover algorithms.

Performance success is a measured observation, not an assertion.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from statistics import median
from copy import deepcopy
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from challenge import (Challenge,generate,suite,check,reference,
                       classical_index,classical_answer,finite_cases)
from synth import (ancestry,typed,emit,compile_spec,explore_specs,
                   check_tool,HOLD)
from trial import (trial,run,exhaustive,compare_sources,STATUS)

class CapabilityDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ancestor=ancestry()
        cls.witness,cls.sources=run()

    def test_prior_017_really_loaded_and_sha_verified(self):
        old=self.ancestor
        self.assertEqual(set(old["tools"]),{"GRAPH","SUBSET"})
        self.assertTrue(old["verified_upstream_017"])
        for family,tool in old["tools"].items():
            self.assertEqual(tool["source_sha256"],
                             old["source_sha256"][family])
            self.assertTrue(callable(tool["build"]))
            self.assertTrue(callable(tool["answer"]))

    def test_task_families_are_distinct_and_train_test_separate(self):
        for family in ("EXACT","FORBIDDEN"):
            a=suite("TRAIN",family);b=suite("HELDOUT",family)
            self.assertEqual(check(a),8)
            self.assertEqual(check(b),12)
            self.assertFalse({t.name for t in a}&{t.name for t in b})
            self.assertEqual(sum(len(t.queries) for t in b),576)

    def test_new_constraints_change_a_real_answer(self):
        t=Challenge("FORBIDDEN","EXPLICIT",(
            (0,1,2),(1,2,3)),((0,2,5,-1),(0,2,5,1)),3)
        self.assertTrue(reference(t,t.queries[0]))
        self.assertFalse(reference(t,t.queries[1]))
        idx=classical_index(t)
        for q in t.queries:
            self.assertEqual(classical_answer(idx,q),reference(t,q))

    def test_naive_ancestral_composition_is_mathematically_false(self):
        # Graph closure says reachable; global subset sum says 2+3=5.
        # But edge ordering forbids making an exact 5 path 0->2.
        t=Challenge("EXACT","COUNTEREXAMPLE",(
            (0,1,2),(0,2,3)),((0,2,5,-1),),3)
        bad=typed("EXACT","BAD_JOIN",("REACH","SUM"))
        tool=compile_spec(bad,self.ancestor)
        self.assertTrue(tool["answer"](tool["build"](t),t.queries[0]))
        self.assertFalse(reference(t,t.queries[0]))
        record=check_tool(tool,(t,))
        self.assertFalse(record["correct"])
        self.assertIsNotNone(record["first_counterexample"])

    def test_wrong_composition_receives_real_counterexample_during_trial(self):
        for stage in ("A","B_WITH_ANCESTRY"):
            row=self.witness["training_proposals"][stage]
            self.assertGreater(row["counterexample_rejected"],0)
            wrong=[x for x in row["records"]
                   if x["status"]=="REJECTED_BY_COUNTEREXAMPLE"]
            self.assertTrue(wrong)
            self.assertTrue(all(x["finite_truth_check"]["first_counterexample"]
                                for x in wrong))
            self.assertTrue(any(x["spec"]["kernel"]=="BAD_JOIN" for x in wrong))

    def test_complete_small_dag_domain_independent_reference(self):
        cases=tuple(finite_cases())
        self.assertEqual(len(cases),27)
        for t in cases:
            idx=classical_index(t)
            for q in t.queries:
                self.assertEqual(reference(t,q),classical_answer(idx,q))
        self.assertEqual(sum(len(t.queries) for t in cases),4536)

    def test_bounded_bitset_source_passes_small_complete_domain(self):
        base=typed("EXACT","BITSET_PATH",("REACH","SUM"))
        compiled=compile_spec(base,self.ancestor)
        proof=exhaustive("EXACT",compiled)
        self.assertTrue(proof["full_small_domain_verified"])
        self.assertEqual(proof["exhaustive_cases_checked_before_first_failure"],
                         27*6*7)

    def test_episode_B_adaptation_has_actual_checked_previous_source(self):
        selected=self.witness["adaptation"]
        self.assertTrue(selected["episode_B_sees_verified_A_bitset"])
        self.assertEqual(selected["episode_A_verified_bitset_source_sha256"],
                         sha256(self.sources["programs"][
                             "A_VERIFIED_BITSET_LIBRARY"].encode()).hexdigest())
        with self.assertRaises(HOLD):
            typed("FORBIDDEN","BITSET_PATH",("REACH","SUM"))

    def test_revised_node_exclusion_correct_for_full_finite_domain(self):
        old=self.sources["programs"]["A_VERIFIED_BITSET_LIBRARY"]
        spec=typed("FORBIDDEN","BITSET_PATH",("REACH","SUM"),old)
        compiled=compile_spec(spec,self.ancestor,old)
        proof=exhaustive("FORBIDDEN",compiled)
        self.assertTrue(proof["full_small_domain_verified"])
        self.assertEqual(proof["exhaustive_cases_checked_before_first_failure"],
                         4536)

    def test_without_ancestors_correct_path_fallback_remains_possible(self):
        plans=explore_specs("FORBIDDEN")
        self.assertEqual(len(plans),1)
        self.assertEqual(plans[0]["kernel"],"DFS_EXACT")
        tool=compile_spec(plans[0])
        self.assertTrue(exhaustive("FORBIDDEN",tool)["full_small_domain_verified"])

    def test_research_grammar_disallows_unknown_source_and_unsanctioned_ban(self):
        with self.assertRaises(HOLD):
            typed("FORBIDDEN","BITSET_PATH",(),None)
        with self.assertRaises(HOLD):
            typed("MONEY","DFS_EXACT")
        with self.assertRaises(HOLD):
            typed("EXACT","UNKNOWN")
        a=typed("EXACT","DFS_EXACT")
        with self.assertRaises(HOLD):
            compile_spec(a,provided=emit(a)+"\nimport os\n")
        with self.assertRaises(HOLD):
            compile_spec(a,provided=emit(a)+"\ndef f():pass\n")

    def test_two_phase_real_program_reuse_but_no_source_adoption(self):
        bundle=self.sources
        report=self.witness
        self.assertEqual(bundle["schema"],
                         "motif.legit018.generated-compositional-sources.v1")
        self.assertFalse(bundle["production_authority"])
        self.assertFalse(report["automatically_merged_or_deployed"])
        self.assertTrue(report["actual_working_source_composed_and_reused"])
        self.assertTrue(report["adaptation"]["source_inheritance_available_only_with_A"])

    def test_all_heldout_answers_reference_matched(self):
        for stage in ("A","B_WITH_ANCESTRY","B_NO_ANCESTRY"):
            result=self.witness["heldout"][stage]
            self.assertEqual(result["cases"],12)
            self.assertEqual(result["queries"],576)
            self.assertTrue(result["zero_wrong_answers"])
            self.assertEqual(set(result["timings"]),
                             {"DIRECT","STRONG_CLASSICAL","GENERATED"})

    def test_raw_timings_and_independently_optimized_comparator(self):
        for stage in self.witness["heldout"].values():
            for arm in stage["timings"].values():
                self.assertEqual(len(arm["wall_ms"]),11)
                self.assertEqual(len(arm["cpu_ms"]),11)
                self.assertAlmostEqual(median(arm["wall_ms"]),
                                       arm["median_wall_ms"],places=5)
                self.assertGreater(arm["median_wall_ms"],0)

    def test_two_phase_selection_had_no_holdout_access(self):
        for stage in self.witness["training_proposals"].values():
            self.assertEqual(sum(x["status"]=="FROZEN_TRAINING_SELECTION"
                                 for x in stage["records"]),1)
            self.assertGreater(stage["proposed"],0)
            self.assertTrue(all(x["selected_on_training_only"]
                                for x in stage["records"]))
        self.assertFalse(self.witness["adaptation"]
                         ["model_selection_used_test_work"])

    def test_researcher_grammar_difference_is_explicit_not_causal_proof(self):
        self.assertTrue(self.witness["adaptation"]
                        ["different_search_grammars_by_design"])
        self.assertTrue(self.witness["adaptation"]
                        ["causal_effect_on_unrestricted_discovery_unproven"])
        self.assertFalse(self.witness["independent_external_challenge_author"])
        self.assertFalse(self.witness["causal_compounding_of_open_ended_research_proved"])
        self.assertFalse(self.witness["unrestricted_algorithm_invention"])
        self.assertFalse(self.witness["full_human_development_cost_measured"])

    def test_actual_source_archive_json_matches_signed_canonical_templates(self):
        report=self.witness
        bundle=self.sources
        for label,src in bundle["programs"].items():
            spec=bundle["manifests"][label]
            spec["prechecks"]=tuple(spec["prechecks"])
            # B routines were allowed to use the frozen checked A source.
            parent=(bundle["programs"]["A_VERIFIED_BITSET_LIBRARY"]
                    if spec["family"]=="FORBIDDEN" and
                    spec["ancestor_A_sha256"] is not None else None)
            self.assertEqual(emit(spec,parent),src)
        self.assertEqual(report["status"],STATUS)

    def test_competing_classical_engine_remains_a_hard_reference(self):
        self.assertTrue(self.witness["strong_classical_compared"])
        self.assertTrue(self.witness["small_finite_falsifiers_only"])
        self.assertFalse(self.witness["new_open_world_capability_claimed"])
        self.assertFalse(self.witness["real_world_authority"])

if __name__=="__main__":
    unittest.main()
