"""LEGIT-019 adversarial test suite for TWO failed-or-surviving claims.

No tool is allowed to proclaim newly invented historically original math
merely because external Z3 proves a bitvector equality. Likewise no
system may infer compounding from a with/without-lemma comparison unless
the same bounded search algorithm gains independent, end-to-end returns.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from statistics import median
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from corpus import (
    FIXTURE,PATTERN,PUBLIC_REPO,REVISION,IDENTIFIERS,load,
    git_blob_sha1,train_only,external_test_for,provenance,HOLD
)
from algebra import (
    norm,val,prove_equal,conjecture_mine,verified_rewrites,canonical,
    X,ZERO,ONE,ALL,_tuplify
)
from search import search,frozen_public_evaluation,as_tuple,MAX_EXPANSIONS
from trial import run,STATUS,REPEATS

class TwoFrontierFalsifiers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus=load()
        cls.result=run()

    def test_external_authorship_and_fixed_2017_commit(self):
        prov=self.result["external_benchmark_provenance"]
        self.assertEqual(prov["origin"],"SyGuS-Org/benchmarks")
        self.assertEqual(prov["original_public_repository_commit"],REVISION)
        self.assertTrue(prov["task_authors_independent_of_MOTIF"])
        self.assertFalse(prov["no_independent_experiment_operator"] is False)
        self.assertTrue(prov["benchmark_labels_public_not_private_blind"])
        self.assertEqual(len(cls_corpus:=self.corpus),4)

    def test_original_git_objects_recomputed_not_just_self_reported_rows(self):
        fixture=json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(fixture["benchmark_ids"],list(IDENTIFIERS))
        for task in fixture["cases"]:
            for label,num in (("train_10",10),("external_test_100",100)):
                doc=task["sources"][label]
                src=doc["source"].encode()
                self.assertEqual(git_blob_sha1(src),doc["git_blob_sha1"])
                self.assertEqual(len(PATTERN.findall(doc["source"])),num)

    def test_source_input_size_not_confused_with_sample_count(self):
        self.assertEqual(len(self.corpus),4)
        for task in self.corpus:
            self.assertEqual(len(task.train),10)
            self.assertEqual(len(task.test),100)
            self.assertTrue(all(0<=x<2**64 and 0<=y<2**64
                                for x,y in task.train+task.test))

    def test_mathematical_conjectures_are_proposed_by_executable_engine(self):
        discovered=self.result["math_discovery"]
        self.assertTrue(discovered[
            "all_generated_hypotheses_from_code_not_handwritten_equations"])
        self.assertGreaterEqual(discovered["proved_64bit_equations"],1)
        self.assertGreaterEqual(discovered["genuine_wrong_conjectures_refuted"],1)
        self.assertGreaterEqual(discovered["verified_rewrite_count"],1)
        self.assertGreater(discovered[
            "hypothesis_generation_Z3_proof_and_reproof_cpu_ms"],0)

    def test_64bit_Z3_proofs_reproducible_and_8bit_scope_explicit(self):
        proof=self.result["math_discovery"]["conjecture_search"]
        for record in proof["z3_formal_proved"]:
            a,b=as_tuple(record["lhs"]),as_tuple(record["rhs"])
            self.assertTrue(prove_equal(a,b,64)["identity_valid"])
            self.assertEqual(record["secondary_exhaustive_8bit_check"],256)
            self.assertTrue(all(val(a,i,8)==val(b,i,8) for i in range(256)))
            self.assertEqual(record["formal"]["z3_result"],"UNSAT")

    def test_Z3_counterexamples_not_relabelled_as_theorems(self):
        proof=self.result["math_discovery"]["conjecture_search"]
        for record in proof["z3_formal_refuted"]:
            a,b=as_tuple(record["lhs"]),as_tuple(record["rhs"])
            cex=record["formal"]["counterexample"]
            x=int(cex["x"],16)
            self.assertNotEqual(val(a,x),val(b,x))
            self.assertEqual(record["formal"]["z3_result"],"SAT")
            self.assertFalse(prove_equal(a,b)["identity_valid"])
            self.assertIn(cex["x"],proof["probe_values"])

    def test_discovered_nonconstant_cross_operator_theorem_is_actually_proved(self):
        receipt=self.result["math_discovery"]["conjecture_search"]
        complex_proofs=[row for row in receipt["z3_formal_proved"]
                        if row["search_round"]=="CROSS_OPERATOR_DISCOVERY"]
        self.assertGreaterEqual(len(complex_proofs),1)
        self.assertEqual(receipt["proved_cross_operator_nonconstant_equations"],
                         len(complex_proofs))
        for row in complex_proofs:
            a,b=as_tuple(row["lhs"]),as_tuple(row["rhs"])
            self.assertNotEqual(a[0],b[0])
            self.assertNotEqual(len({val(a,x) for x in (0,1,2,3,123456)}),1)
            self.assertTrue(prove_equal(a,b)["identity_valid"])
            self.assertTrue(all(val(a,x,8)==val(b,x,8) for x in range(256)))
        self.assertFalse(receipt["mathematical_laws_historically_new"])

    def test_forged_proof_can_never_become_rewrite(self):
        report=deepcopy(self.result["math_discovery"]["conjecture_search"])
        report["rewrites"].append([["x"],["k",1]])
        with self.assertRaises(Exception):
            verified_rewrites(report)

    def test_proved_rewrites_rechecked_before_matching_programs(self):
        report=self.result["math_discovery"]["conjecture_search"]
        found=verified_rewrites(report)
        self.assertGreater(len(found),0)
        for left,right in found:
            self.assertTrue(prove_equal(left,right)["identity_valid"])
            self.assertGreaterEqual(len(repr(left)),len(repr(right)))

    def test_unknown_arbitrary_math_operator_never_compiles(self):
        with self.assertRaises(Exception):
            norm(("execute_system_command",X))
        with self.assertRaises(Exception):
            val(("import",X),4)
        with self.assertRaises(Exception):
            norm(("k",2**65))

    def test_matched_synthesis_has_same_budget_and_train_examples(self):
        rr=self.result["equal_budget_research_trial"]
        self.assertEqual(rr["train_examples_per_task"],10)
        self.assertEqual(rr["published_public_test_examples_per_task"],100)
        self.assertEqual(rr["repeat_searches_per_arm"],REPEATS)
        self.assertTrue(rr["same_observational_semantic_deduplication_for_both_arms"])
        self.assertTrue(rr["previously_discovered_proven_rewrites_available_only_to_treatment"])
        self.assertEqual(set(rr["training_search"]),set(map(str,IDENTIFIERS)))
        for task in rr["training_search"].values():
            self.assertEqual(set(task),
                {"UNASSISTED","WITH_SELF_PROVED_LEMMAS"})
            for arm in task.values():
                self.assertEqual(arm["max_expansions"],MAX_EXPANSIONS)
                self.assertFalse(arm["heldout_data_accessed"])
                self.assertEqual(len(arm["raw_search_runs"]),REPEATS)

    def test_frozen_source_hash_reconstructs_without_any_test_labels(self):
        rr=self.result["equal_budget_research_trial"]
        raw={str(i):{
            arm:{"program":r["program"],
                 "candidates_evaluated":r["candidates_evaluated"]}
            for arm,r in arms.items()
        }for i,arms in ((int(k),v)for k,v in rr["training_search"].items())}
        sha=sha256(json.dumps(raw,sort_keys=True).encode()).hexdigest()
        self.assertEqual(sha,rr["frozen_train_decisions_sha256"])

    def test_external_100_examples_actually_exercised(self):
        rr=self.result["equal_budget_research_trial"]
        for case,arms in rr["published_external_100_example_results"].items():
            for method,assessment in arms.items():
                self.assertEqual(assessment["examples"],100)
                self.assertEqual(
                    assessment["solved"],assessment["passed"]==100)
                self.assertTrue(assessment["no_new_program_selected_after_test"])
                self.assertTrue(0<=assessment["passed"]<=100)

    def test_some_competition_program_can_generalize_but_not_all(self):
        rr=self.result["equal_budget_research_trial"]
        # The fixed bounded DSL is deliberately incomplete.
        self.assertTrue(rr["published_external_100_example_results"]["112"]
                        ["UNASSISTED"]["solved"])
        self.assertTrue(rr["published_external_100_example_results"]["112"]
                        ["WITH_SELF_PROVED_LEMMAS"]["solved"])
        self.assertFalse(rr["published_external_100_example_results"]["100"]
                         ["UNASSISTED"]["solved"])

    def test_external_examples_not_reused_to_change_earlier_choice(self):
        rr=self.result["equal_budget_research_trial"]
        for problem in self.corpus:
            for method,archived in rr["training_search"][str(problem.identifier)].items():
                evaluated=frozen_public_evaluation(
                    archived,problem.test)
                self.assertEqual(evaluated,
                    rr["published_external_100_example_results"]
                    [str(problem.identifier)][method])

    def test_observed_compound_return_calculates_real_proof_overhead(self):
        rr=self.result["equal_budget_research_trial"]
        cost=self.result["math_discovery"][
            "hypothesis_generation_Z3_proof_and_reproof_cpu_ms"]
        self.assertAlmostEqual(
            rr["total_treated_search_plus_mining_cpu_ms"],
            round(rr["assisted_total_median_search_cpu_ms_excluding_proof"]+cost,6),
            places=5)
        self.assertEqual(
            rr["treated_search_plus_mining_paid_back_by_four_tasks"],
            rr["total_treated_search_plus_mining_cpu_ms"]<
            rr["unassisted_total_median_search_cpu_ms"])

    def test_mathematical_proof_does_not_authenticate_historical_originality(self):
        self.assertFalse(self.result["claimed_novel_mathematics"])
        self.assertFalse(self.result["math_discovery"]["conjecture_search"]
                         ["new_math_novelty_authenticated"])
        self.assertFalse(self.result["gate"][
            "historically_novel_mathematical_theorem_independently_certified"])
        self.assertFalse(self.result["gate"][
            "competition_benchmark_adjudication_blinded_by_external_organizer"])

    def test_saved_CI_report_is_cryptographically_source_grounded_and_reproves(self):
        saved=json.loads((HERE/"generated"/"two_frontier_external_challenge_receipt.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual(saved["experiment"],"MOTIF-LEGIT-019")
        self.assertFalse(saved["claimed_novel_mathematics"])
        self.assertFalse(saved["claimed_independently_verified_compounding"])
        self.assertEqual(saved["math_discovery"]["conjecture_search"]
                         ["proved_cross_operator_nonconstant_equations"],3)
        self.assertEqual(saved["math_discovery"]["genuine_wrong_conjectures_refuted"],1)
        self.assertEqual(saved["external_benchmark_provenance"]
                         ["original_public_repository_commit"],REVISION)
        for case in self.corpus:
            shas=saved["external_benchmark_provenance"]["source_blob_git_sha1"][
                str(case.identifier)]
            self.assertEqual(shas["10"],case.sha_train)
            self.assertEqual(shas["100"],case.sha_test)
            both=saved["equal_budget_research_trial"]["training_search"][
                str(case.identifier)]
            for method,r in both.items():
                self.assertEqual(len(r["raw_search_runs"]),3)
                self.assertAlmostEqual(median(
                    [v["cpu_ms"] for v in r["raw_search_runs"]]),
                    r["median_cpu_ms"],places=5)
                evaluated=frozen_public_evaluation(r,case.test)
                self.assertEqual(evaluated,
                    saved["equal_budget_research_trial"][
                        "published_external_100_example_results"][
                            str(case.identifier)][method])
        for item in saved["math_discovery"]["conjecture_search"]["z3_formal_proved"]:
            self.assertTrue(prove_equal(as_tuple(item["lhs"]),
                                        as_tuple(item["rhs"]))["identity_valid"])
        self.assertFalse(saved["gate"][
            "historically_novel_mathematical_theorem_independently_certified"])
        # Never require fresh CPU durations equal saved GitHub Actions values;
        # the invariant is the program/proof/outcome, not wall time noise.

    def test_compounding_is_not_claimed_without_causal_successive_inventions(self):
        self.assertEqual(self.result["status"],STATUS)
        self.assertFalse(self.result["claimed_independently_verified_compounding"])
        self.assertFalse(self.result["gate"][
            "actually_adopted_research_upgrade_causally_enables_later_new_invention"])
        self.assertFalse(self.result["gate"]["software_auto_deploy_permitted"])
        self.assertEqual(self.result["external_write_actions"],0)

    def test_source_corpus_lacks_magic_truth_for_unregistered_task(self):
        with self.assertRaises(HOLD):
            search(tuple([(0,0)]*10))
        with self.assertRaises(HOLD):
            search(((1,2),),max_expansions=12000)
        with self.assertRaises(HOLD):
            search(self.corpus[0].train,max_expansions=9999999)

if __name__=="__main__":
    unittest.main()
