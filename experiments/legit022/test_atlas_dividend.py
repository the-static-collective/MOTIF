"""LEGIT-022 adversarial independent-origin and research compounding controls.

Source graphs are externally originated from the 1998 Atlas, but the
pairing protocol and experimental author are NOT external. Match the
actual preceding-source acquisition against a conventional data-trained
priority and an explicit no-previous-tool control. A single non-blinded
study is insufficient to certify recursive self-improvement or novelty.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from statistics import mean,median
from unittest.mock import patch
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from atlas import (
    Task,TRAIN_SIZE,TEST_SIZE,VERSION,SEED,
    cohort,verify_prepared,HOLD
)
from theorems import (
    all_unlabeled_sources_up_to_four,components,
    propose_composition_rule,certify_factorization,
    challenge_degree_conjecture,correct_product
)
from trial import (
    prior_apertures,training_priority,counterfactual,
    query_matrix,study,STATUS,run
)
from graph_inventor import (
    grammar,characterize,count,reference_count,cycles
)

class IndependentChallengeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train,cls.heldout,cls.origin=cohort()
        cls.priors,cls.source=prior_apertures()
        cls.result=run()

    def test_true_external_carrier_origins_and_data_version(self):
        src=self.origin
        self.assertEqual(src["networkx_version"],VERSION)
        self.assertEqual(src["seven_node_graphs"],1044)
        self.assertEqual(src["atlas_graphs"],1253)
        self.assertEqual(len(src["atlas_data_sha256"]),64)
        self.assertTrue(src["original_carrier_authorship_independent_of_MOTIF"])
        self.assertTrue(src["challenge_pairing_and_split_authored_by_MOTIF"])
        self.assertTrue(src["benchmark_is_public_and_not_externally_blind"])

    def test_challenge_pairs_are_split_without_candidate_probe_answers(self):
        self.assertEqual(len(self.train),TRAIN_SIZE)
        self.assertEqual(len(self.heldout),TEST_SIZE)
        self.assertTrue(verify_prepared(self.train,self.heldout,self.origin))
        self.assertFalse(set(x.atlas_ids for x in self.train)&
                         set(x.atlas_ids for x in self.heldout))
        self.assertTrue(self.origin[
            "challenge_pairs_selected_without_probing_homomorphism_outcomes"])

    def test_all_pairs_share_degree_multisets_and_are_distinct_atlas_entries(self):
        for item in self.train+self.heldout:
            self.assertNotEqual(item.atlas_ids[0],item.atlas_ids[1])
            self.assertEqual(item.graphs[0][0],7)
            self.assertEqual(item.graphs[1][0],7)
            self.assertEqual(sum(item.degree_signature),
                             2*len(item.graphs[0][1]))
            self.assertEqual(len(item.graphs[0][1]),
                             len(item.graphs[1][1]))

    def test_independent_classical_iso_confirms_external_graph_pairs_differ(self):
        import networkx as nx
        for item in (self.train+self.heldout)[:16]:
            g=[]
            for n,edges in item.graphs:
                graph=nx.Graph()
                graph.add_nodes_from(range(n))
                graph.add_edges_from(edges)
                g.append(graph)
            self.assertFalse(nx.is_isomorphic(*g))

    def test_real_prior_generated_sources_have_original_mathematical_witness(self):
        self.assertEqual(len(self.priors),3)
        self.assertTrue(characterize(self.priors[0])["triangle"])
        self.assertTrue(characterize(self.priors[1])["three_leaf_star"])
        self.assertTrue(characterize(self.priors[2])["four_cycle"])
        self.assertTrue(self.source["prior_mathematical_witnesses_replayed"])
        self.assertEqual(self.source["prior_experiment"],"MOTIF-LEGIT-021")

    def test_source_plans_no_unverified_legacy_replay(self):
        import trial
        old=trial.PREVIOUS
        try:
            trial.PREVIOUS=HERE/"fake-nonexistent-previous.json"
            with self.assertRaises(FileNotFoundError):
                prior_apertures()
        finally:
            trial.PREVIOUS=old

    def test_complete_unlabeled_four_vertex_grammar_contains_disconnected(self):
        sources=all_unlabeled_sources_up_to_four()
        self.assertEqual(len(sources),18)
        connected=[p for p in sources if len(components(p))==1]
        disconnected=[p for p in sources if len(components(p))>1]
        self.assertEqual(len(connected),len(grammar()))
        self.assertEqual(len(disconnected),8)
        self.assertEqual(set(connected),set(grammar()))

    def test_computational_miner_proposes_factorization_not_hardcoded_result(self):
        miner=self.result["math_novelty_attempt"][
            "source_decomposition_rule_hypothesis"]
        self.assertEqual(miner["selected"],"PRODUCT")
        self.assertEqual(set(miner["candidate_operation_language"]),
                         {"PRODUCT","SUM","MAX","MIN"})
        self.assertEqual(miner["failed_hypotheses"],["SUM","MAX","MIN"])
        for name in miner["failed_hypotheses"]:
            self.assertTrue(miner["genuinely_computed_training_spectra"]
                            [name]["first_counterexample"])
        self.assertFalse(miner["historically_novel_mathematics"])

    def test_factorization_exact_source_map_enumeration_not_only_samples(self):
        certificate=self.result["math_novelty_attempt"][
            "independent_finite_and_combinatorial_certificate"]
        self.assertEqual(certificate["connected_sources_kept"],10)
        self.assertEqual(certificate["disconnected_sources_mathematically_redundant_for_separation"],8)
        self.assertEqual(certificate["unlabeled_sources_total"],18)
        self.assertTrue(certificate["universal_proof_argument_written_by_researcher"])
        self.assertGreater(certificate["independent_exhaustive_assignment_comparisons"],0)

    def test_math_factorization_transfers_without_new_formula_search(self):
        for source in all_unlabeled_sources_up_to_four():
            if len(components(source))>1:
                for item in self.heldout[:3]:
                    for target in item.graphs:
                        self.assertEqual(correct_product(source,target),
                                         reference_count(source,target))

    def test_invalid_degree_conjecture_never_promoted_as_math_fact(self):
        attempt=self.result["math_novelty_attempt"][
            "overgeneralized_degree_to_tree_conjecture"]
        self.assertFalse(attempt["no_general_all_tree_equivalence_theorem_claimed"] is False)
        self.assertFalse(self.result["math_novelty_attempt"][
            "historically_novel_theorem_credible"])

    def test_identical_worlds_remain_unresolved_by_all_observation_grammars(self):
        carrier=cycles(6)
        for order in (grammar(),all_unlabeled_sources_up_to_four()):
            r=study(Task((777,777),(carrier,carrier),tuple()),order)
            self.assertFalse(r["resolved"])
            self.assertTrue(r["all_unsolved_probes_form_explicit_hold"])
            self.assertEqual(r["number_of_questions"],len(order))

    def test_matched_policies_return_same_solved_flags_on_all_heldout(self):
        packet=self.result["two_research_episodes"]["prior_aperture_reuse"]
        rows=packet["query_receipts"]
        expected=[x["resolved"] for x in rows["CANONICAL_CONNECTED_ONLY"]]
        for arm,receipts in rows.items():
            self.assertEqual(len(receipts),TEST_SIZE)
            self.assertEqual([x["resolved"] for x in receipts],expected)
            self.assertTrue(all(x["number_of_questions"]>0
                                and x["two_world_source_hom_calls"]==
                                    2*x["number_of_questions"]
                                for x in receipts))

    def test_mathematical_source_counters_each_recover_exact_observation(self):
        records=self.result["two_research_episodes"]["prior_aperture_reuse"]
        order=records["actual_frozen_probe_orders"]
        for arm in order:
            self.assertGreater(len(order[arm]),0)
        for t,receipt in zip(self.heldout,
            records["query_receipts"]["LEGIT021_ACQUIRED_APERTURES_FIRST"]):
            for row in receipt["all_actual_probe_answers"]:
                p=row["probe"]
                probe=next(q for q in grammar() if characterize(q)==p)
                self.assertEqual(row["counts"],
                    [reference_count(probe,g) for g in t.graphs])

    def test_strong_classical_cost_sensitive_training_sees_same_grammar(self):
        b=training_priority(self.train,grammar())
        self.assertEqual(len(b),10)
        self.assertEqual(set(b),set(grammar()))
        self.assertEqual(
            self.result["two_research_episodes"]["prior_aperture_reuse"][
            "actual_frozen_probe_orders"]["STRONG_CLASSICAL_TRAINED_COST_SENSITIVE"],
            [[p[0],[list(e) for e in p[1]]] for p in b])

    def test_previous_probe_library_cannot_change_query_grammar(self):
        orders=self.result["two_research_episodes"][
            "prior_aperture_reuse"]["actual_frozen_probe_orders"]
        self.assertEqual(len(orders["LEGIT021_ACQUIRED_APERTURES_FIRST"]),10)
        self.assertEqual(len(orders["CANONICAL_CONNECTED_ONLY"]),10)
        self.assertEqual(len(orders["ALL_UNFILTERED_SOURCE_GRAPHS"]),18)

    def test_all_four_policies_identical_external_tasks_and_matched_budget(self):
        packet=self.result["two_research_episodes"]["prior_aperture_reuse"]
        self.assertTrue(packet["shared_heldout_pairs_across_all_arms"])
        self.assertTrue(packet["candidate_probes_not_retrained_after_heldout"])
        self.assertTrue(packet["strong_classical_source_ordering_same_grammar_as_prior"])
        self.assertTrue(packet["unfiltered_baseline_known_weaker_by_design"])
        self.assertFalse(self.result["evidence_and_scope"][
            "external_challenge_pairing_independently_authored"])

    def test_assignments_are_positive_and_measured_for_all_failed_probes(self):
        packet=self.result["two_research_episodes"][
            "prior_aperture_reuse"]
        for arm,rows in packet["query_receipts"].items():
            for row in rows:
                self.assertEqual(
                    row["enumerative_assignment_trial_budget"],
                    sum(v["pair_graph_assignment_trials"]
                        for v in row["all_actual_probe_answers"]))
                self.assertEqual(
                    row["number_of_questions"],len(row["all_actual_probe_answers"]))
                self.assertTrue(all(v["pair_graph_assignment_trials"]==
                    2*(7**v["source_vertices"])
                    for v in row["all_actual_probe_answers"]))

    def test_frozen_policy_hash_is_from_only_declared_source_orders(self):
        packet=self.result["two_research_episodes"]["prior_aperture_reuse"]
        text=json.dumps(packet["actual_frozen_probe_orders"],sort_keys=True,
                        separators=(",",":")).encode()
        self.assertEqual(sha256(text).hexdigest(),packet["source_plans_frozen_sha256"])

    def test_pinned_atlas_sha256_not_just_package_semver(self):
        from atlas import EXPECTED_ATLAS_SHA256
        self.assertEqual(len(EXPECTED_ATLAS_SHA256),64)
        self.assertEqual(self.origin["atlas_data_sha256"],EXPECTED_ATLAS_SHA256)

    def test_real_uncached_cpu_samples_account_for_every_probe(self):
        packet=self.result["two_research_episodes"]["prior_aperture_reuse"]
        expected=packet["heldout_matched_observations"]
        costs=packet["actual_uncached_cpu_and_wall_microbenchmarks"]
        self.assertEqual(set(costs),set(expected))
        for arm,row in costs.items():
            self.assertEqual(row["repeat_count"],3)
            self.assertEqual(len(row["wall_ms"]),3)
            self.assertEqual(len(row["cpu_ms"]),3)
            self.assertEqual(len(set(row["questions"])),1)
            self.assertGreater(row["median_wall_ms"],0)
            self.assertGreater(row["median_cpu_ms"],0)
            self.assertEqual(row["questions"][0],expected[arm]["total_queries"])
            self.assertEqual(row["full_uncached_source_homomorphism_evaluations"],
                             expected[arm]["total_homomorphism_calls"])
            self.assertAlmostEqual(median(row["cpu_ms"]),
                                   row["median_cpu_ms"],places=5)

    def test_mined_math_proof_has_real_setup_cost_but_not_forged_prior_costs(self):
        costs=self.result["math_novelty_attempt"][
            "actual_theorem_hypothesis_and_finite_verification_cost_ms"]
        self.assertGreater(costs["wall_ms"],0)
        self.assertGreater(costs["cpu_ms"],0)
        self.assertIsNone(costs["full_original_human_and_prior_021_engineering_cost"])

    def test_scientific_holds_are_not_bypassed_by_marginal_performance(self):
        r=self.result
        self.assertEqual(r["status"],STATUS)
        self.assertFalse(r["evidence_and_scope"][
            "new_historical_mathematics_demonstrated"])
        self.assertFalse(r["evidence_and_scope"][
            "independent_adjudicator_of_recursive_improvement"])
        self.assertFalse(r["evidence_and_scope"][
            "repeated_adopted_successive_optimizations_causally_proved"])
        self.assertFalse(r["evidence_and_scope"][
            "economic_compounding_rate_identifiable"])
        self.assertFalse(r["evidence_and_scope"][
            "no_new_software_auto_promotion"] is False)

if __name__=="__main__":
    unittest.main()
