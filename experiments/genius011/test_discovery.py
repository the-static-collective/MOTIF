"""GENIUS-011: falsifiers for previously unnamed cross-thread hypotheses."""
from __future__ import annotations

from dataclasses import replace
import json
import unittest

from discovery import (
    ALPHA, PATTERN_FAMILY_BUDGET, REGIMES, THREADS, Edge,
    Trial, analyze, canonical_pair, evaluate_case, make_world,
    mine_strand, public_trials, question_synthesis, simulate_test,
)
from benchmark import TEST_SEEDS, VALIDATION_SEEDS, run


class TestQuestionNotSupplied(unittest.TestCase):
    def test_same_graph_with_renamed_nodes_yields_same_new_expression(self):
        edges_a=(Edge("apple","brook","+","ref1"),
                 Edge("brook","cedar","-","ref2"))
        edges_b=(Edge("zx","qq","+","ref3"),
                 Edge("qq","rt","-","ref4"))
        self.assertEqual(canonical_pair(edges_a),canonical_pair(edges_b))
        self.assertNotIn("apple",canonical_pair(edges_a))
        self.assertNotIn("brook",canonical_pair(edges_a))

    def test_direction_and_edge_sign_matter_not_just_words(self):
        a=canonical_pair((Edge("a","b","+","1"),Edge("b","c","-","2")))
        b=canonical_pair((Edge("a","b","+","1"),Edge("a","c","+","2")))
        self.assertNotEqual(a,b)
        flipped=canonical_pair((Edge("a","b","-","1"),Edge("b","c","+","2")))
        self.assertNotEqual(a,flipped)

    def test_invent_hypotheses_from_local_shapes_no_hypothesis_names_given(self):
        world=make_world(11031,"TRUE_RENAMED")
        out=question_synthesis(world.strands)
        self.assertEqual(out["status"],"GENERATED_FALSIFIABLE_RELATION_QUESTIONS")
        self.assertEqual(len(out["candidates"]),2)
        for q in out["candidates"]:
            self.assertEqual(len(q.source_witnesses),3)
            self.assertNotIn("blue ribbon",q.question)
            self.assertNotIn("hinge_timing",q.question)
            self.assertEqual(len(q.digest),64)
            for _,refs in q.source_witnesses:
                self.assertEqual(len(refs),2)
                self.assertTrue(all(ref.startswith("synthetic://graph/") for ref in refs))
            self.assertIn(q.signature,q.question)

    def test_synthesis_sees_no_secret_world_parameter(self):
        world=make_world(11031,"TRUE")
        first=question_synthesis(world.strands)
        fake_world=replace(world, secret_active_signature="malicious_label",
                           secret_secondary_signature=None)
        second=question_synthesis(fake_world.strands)
        self.assertEqual(first,second)

    def test_no_shared_structure_or_duplicate_source_produces_hold(self):
        no_shared=question_synthesis(make_world(11031,"NO_SHARED").strands)
        self.assertEqual(no_shared["status"],"HOLD_NO_SHARED_TYPED_STRUCTURE")
        echoed=question_synthesis(make_world(11031,"ECHO_ROOT").strands)
        self.assertEqual(echoed["status"],"HOLD_DUPLICATE_INQUIRY_ORIGINS")
        self.assertEqual(no_shared["candidates"],[])
        self.assertEqual(echoed["candidates"],[])

    def test_public_edge_projection_excludes_withheld_private(self):
        world=make_world(11031,"TRUE")
        strand=world.strands[0]
        source=mine_strand(strand)
        withheld=Edge("vanished","unknown","+","never-publish",
                      False,"PRIVATE_NOT_FOR_NETWORK")
        modified=replace(strand,edges=strand.edges+(withheld,))
        self.assertEqual(mine_strand(modified),source)
        self.assertNotIn("PRIVATE_NOT_FOR_NETWORK",json.dumps(source))

    def test_intervention_question_is_tested_only_after_synthesis(self):
        world=make_world(11032,"TRUE")
        proposals=question_synthesis(world.strands)
        q=proposals["candidates"][0]
        raw=simulate_test(world,q)
        share=public_trials(raw)
        self.assertGreater(len(raw),len(share))
        self.assertTrue(all(x.shareable and not x.private_note for x in share))
        answer=analyze(q,share,purported_randomization_attested=True)
        self.assertIn(answer["status"],(
            "CONDITIONAL_SYNTHESIZED_BRIDGE","HOLD_BRIDGE_NOT_SUPPORTED"))
        self.assertEqual(len(answer["per_thread"]),3)
        self.assertAlmostEqual(
            answer["per_comparison_alpha"], ALPHA/(PATTERN_FAMILY_BUDGET*3))
        self.assertFalse(answer["causal_or_real_world_inference_authorized"])

    def test_forged_replayed_evidence_does_not_count_twice(self):
        w=make_world(11032,"TRUE")
        q=question_synthesis(w.strands)["candidates"][0]
        public=public_trials(simulate_test(w,q))
        replay=public+(public[0],)
        r=analyze(q,replay,purported_randomization_attested=True)
        self.assertEqual(r["status"],"HOLD_REPLAYED_EVIDENCE")
        colliding=replace(public[-1],
                          origin_root=public[0].origin_root)
        r=analyze(q,public[:-1]+(colliding,),
                  purported_randomization_attested=True)
        self.assertEqual(r["status"],"HOLD_SHARED_EXPERIMENT_ORIGIN")

    def test_randomization_declaration_not_signature_and_private_not_leaked(self):
        w=make_world(11032,"TRUE")
        q=question_synthesis(w.strands)["candidates"][0]
        public=public_trials(simulate_test(w,q))
        hold=analyze(q,public,purported_randomization_attested=False)
        self.assertEqual(hold["status"],"HOLD_UNVERIFIED_EXPERIMENT_DESIGN")
        with self.assertRaises(ValueError):
            analyze(q,simulate_test(w,q),
                    purported_randomization_attested=True)

    def test_observational_confounder_may_be_significant_without_intervention(self):
        from controls import audit_survey
        r = audit_survey(11031)
        self.assertEqual(r["status"],
                         "POSTHOC_OBSERVATIONAL_CONFOUNDING_NOT_INDEPENDENT_BLIND")
        self.assertEqual(r["generated_candidates"], 2)
        for row in r["candidate_checks"]:
            self.assertEqual(
                row["intervention_gate_status"],
                "HOLD_OBSERVATIONAL_DATA_NOT_AN_INTERVENTION")
            self.assertTrue(all(
                v["observational_difference"] > .5
                for v in row["survey_results"]))
            self.assertTrue(all(
                v["not_a_causal_or_randomized_conclusion"]
                for v in row["survey_results"]))
        self.assertNotIn("NEVER_SHARE_PRIVATE_CONTROL_NOTE",json.dumps(r))

    def test_three_strands_must_actually_support_relationship(self):
        for regime in ("PARTIAL","OPPOSED","NULL","CONFOUNDED"):
            r=evaluate_case(11031,regime)
            self.assertEqual(r["conditionally_supported"],[])
            self.assertEqual(r["two_clock"]["retrospective_callbacks"],[])

    def test_multiple_valid_bridges_does_not_force_one_interpretation(self):
        r=evaluate_case(11031,"RIVAL")
        self.assertEqual(r["bridge_status"],
                         "HOLD_MULTIPLE_COMPETING_EXPLANATIONS")
        self.assertEqual(r["conditionally_supported"],[])
        self.assertEqual(r["two_clock"]["retrospective_callbacks"],[])

    def test_valid_bridge_witness_can_reinterpret_but_not_rewrite(self):
        r=evaluate_case(11031,"TRUE",detailed=True)
        self.assertEqual(r["bridge_status"],"ONE_CONDITIONAL_SYNTHESIZED_BRIDGE")
        self.assertEqual(len(r["conditionally_supported"]),1)
        self.assertEqual(len(r["two_clock"]["retrospective_callbacks"]),3)
        self.assertTrue(r["two_clock"]["no_original_record_edited"])
        self.assertIn("/sha256/",r["two_clock"]["later_audit_source_pointer"])
        self.assertEqual(len(r["two_clock"]["source_evidence_fingerprints"]),3)
        for x in r["two_clock"]["retrospective_callbacks"]:
            self.assertEqual(x["status"],"INTERPRETATION_NOT_TESTIMONY")

    def test_effective_winner_changes_across_test_seeds_and_is_not_hardcoded(self):
        a=evaluate_case(11031,"TRUE")
        b=evaluate_case(11032,"TRUE")
        self.assertNotEqual(a["conditionally_supported"],
                            b["conditionally_supported"])
        self.assertEqual(a["conditionally_supported"],
                         [a["actual_secret_for_evaluator_only"]])
        self.assertEqual(b["conditionally_supported"],
                         [b["actual_secret_for_evaluator_only"]])


class TestFutureFreeze(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=run()

    def test_heldout_and_validation_are_disjoint_and_source_bound(self):
        r=self.r
        self.assertEqual(r["status"],"RESEARCH_HOLD_ENGINEER_AUTHORED_SYNTHESIS")
        self.assertEqual(len(r["study_protocol_sha256_before_test_generation"]),64)
        self.assertFalse(set(TEST_SEEDS)&set(VALIDATION_SEEDS))
        self.assertEqual(set(r["future"]),set(REGIMES))
        self.assertTrue(r["strong_classical_exact_graph_miner_and_fisher_same_outcomes"])
        self.assertTrue(r["no_novel_mathematical_algorithm"])
        self.assertTrue(r["no_external_action"])

    def test_true_multiple_holds_and_null_have_expected_categorization(self):
        x=self.r["future"]
        for regime in ("TRUE","TRUE_RENAMED"):
            self.assertEqual(x[regime]["single_supported_bridge_count"],
                             len(TEST_SEEDS))
            self.assertEqual(x[regime]["spurious_supported_bridge_count"],0)
        for regime in ("NULL","CONFOUNDED","PARTIAL","OPPOSED",
                       "ECHO_ROOT","RIVAL","NO_SHARED"):
            self.assertEqual(x[regime]["single_supported_bridge_count"],0)

    def test_sensitive_or_hidden_information_not_part_of_receipts(self):
        text=json.dumps(self.r)
        self.assertNotIn("NEVER_EXPORT_PRIVATE_SYNTHETIC_CONTENT",text)
        for case in self.r["proof_carrying_source_cases"].values():
            if case["two_clock"] is not None:
                self.assertTrue(case["two_clock"]["no_original_record_edited"])
            if case["tests_performed"]:
                self.assertEqual(len(case["candidate_signatures"]),
                                 case["tests_performed"])


if __name__=="__main__":
    unittest.main()
