"""LEGIT-005 falsifiers for semantic composition and logical complement.

All tests are synthetic or use previously hand-curated published aggregates;
they establish no clinical fact about any specific patient.
"""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from meaning import HOLD, learn, parse, complement_certificate, counterexample_truth
from runner import trained, examine, neuro_packet
from benchmark import cases, raw_case, benchmark
from classical_reference import parse_classical
from exact_reference import reference_oracle


class MeaningFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grammar=trained()

    def test_four_meanings_and_unseen_combinatorial_rules(self):
        self.assertEqual(self.grammar["teacher_count"],16)
        self.assertEqual(len(self.grammar["rules"]),16)
        self.assertEqual(self.grammar["novel_combinations"],8)
        self.assertFalse(self.grammar["source_authenticated"])
        self.assertFalse(self.grammar["real_world_authority"])

    def test_learned_rules_do_not_memorize_domain_words(self):
        rules=str(self.grammar["rules"])
        for word in ("neural command response","sonar echo","subjective experience",
                     "underwater habitat","wildfire activity","infrared glow"):
            self.assertNotIn(word,rules)

    def test_parses_unseen_recombined_phrases_in_new_domains(self):
        subset=[x for x in cases() if x["group"]=="unseen_recomposition"]
        self.assertEqual(len(subset),16)
        for row in subset:
            parsed=parse(row["question"],self.grammar)
            self.assertEqual(parsed["status"],"PARSED_PROPOSAL_ONLY",row["id"])
            self.assertFalse(parsed["seen_pair_in_teacher"],row["id"])
            self.assertEqual({x:parsed[x] for x in ("kind","proxy","target")},
                             row["gold"],row["id"])

    def test_held_aside_known_pairs_transfer_to_other_topics(self):
        subset=[x for x in cases() if x["group"]=="seen_phrase_pair_new_domain"]
        self.assertEqual(len(subset),16)
        for row in subset:
            parsed=parse(row["question"],self.grammar)
            self.assertEqual(parsed["status"],"PARSED_PROPOSAL_ONLY",row["id"])
            self.assertTrue(parsed["seen_pair_in_teacher"],row["id"])

    def test_unseen_lexical_paraphrase_refused_not_invented(self):
        subset=[x for x in cases() if x["group"]=="new_lexical_paraphrase"]
        self.assertEqual(len(subset),4)
        for row in subset:
            self.assertEqual(parse(row["question"],self.grammar)["status"],
                             "HOLD_UNSUPPORTED_MEANING",row["id"])

    def test_negation_scope_and_false_friend_traps_hold(self):
        subset=[x for x in cases() if x["group"]=="hostile_or_unsupported"]
        self.assertEqual(len(subset),8)
        for row in subset:
            raw=raw_case(row,17)
            result=examine(raw,self.grammar)
            self.assertNotEqual(result["status"],"RESEARCH_HOLD",row["id"])

    def test_source_instrument_mismatch_holds(self):
        subset=[x for x in cases() if x["group"]=="source_indicator_mismatch"]
        self.assertEqual(len(subset),4)
        for row in subset:
            result=examine(raw_case(row,3),self.grammar)
            self.assertEqual(result["status"],
                             "HOLD_INDICATOR_SOURCE_MISMATCH",row["id"])

    def test_four_atoms_of_counterexample_truth_tables(self):
        cert=complement_certificate()
        self.assertEqual(len(cert["negative"]),4)
        self.assertEqual(len(cert["positive"]),4)
        for sign,a,b in (("negative","U_NEG","CAN_NEG"),
                         ("positive","U_POS","CAN_POS")):
            for row in cert[sign]:
                self.assertEqual(row["counterexample"],row["possibility_witness"])
                self.assertEqual(row["counterexample"],counterexample_truth(
                    a,row["proxy_positive"],row["target_present"]))
                self.assertEqual(row["possibility_witness"],counterexample_truth(
                    b,row["proxy_positive"],row["target_present"]))

    def test_neuroscience_dual_preserves_unknown_actual_state(self):
        raw=neuro_packet()
        a=examine(raw,self.grammar)
        b=examine(dict(raw,question="Does missing neural command response rule out subjective experience?"),self.grammar)
        self.assertEqual(a["claim"]["possible_counterexample_count_bounds"],[0,250])
        self.assertEqual(b["claim"]["possible_counterexample_count_bounds"],[0,250])
        self.assertTrue(a["claim"]["logical_answer_in_admitted_model"])
        self.assertFalse(b["claim"]["logical_answer_in_admitted_model"])
        self.assertIsNone(a["claim"]["actual_hidden_target_state"])
        self.assertIsNone(b["claim"]["individual_probability"])
        self.assertEqual(a["interpretation"],b["interpretation"])
        self.assertFalse(a["real_world_authority"])

    def test_positive_and_negative_duality_against_independent_exact_reference(self):
        row=cases()[0]
        raw=raw_case(row,0)
        pairings=(
            ("Does missing microwave reflection rule out buried satellite?",
             "Can buried satellite exist without microwave reflection?",
             "U_NEG","CAN_NEG"),
            ("Does detecting microwave reflection guarantee buried satellite?",
             "Can microwave reflection appear without buried satellite?",
             "U_POS","CAN_POS")
        )
        for universal,existential,u,e in pairings:
            x=examine(dict(raw,question=universal),self.grammar)
            y=examine(dict(raw,question=existential),self.grammar)
            self.assertEqual(x["status"],"RESEARCH_HOLD")
            self.assertEqual(y["status"],"RESEARCH_HOLD")
            self.assertEqual(x["claim"]["logical_answer_in_admitted_model"],
                             reference_oracle(raw,u))
            self.assertEqual(y["claim"]["logical_answer_in_admitted_model"],
                             reference_oracle(raw,e))
            self.assertNotEqual(x["claim"]["logical_answer_in_admitted_model"],
                                y["claim"]["logical_answer_in_admitted_model"])

    def test_negative_certified_absence_reverses_answer(self):
        row=cases()[0]
        raw=raw_case(row,1) # all negative proxy synthetic targets proven absent
        x=examine(raw,self.grammar)
        y=examine(dict(raw,question="Can buried satellite exist without microwave reflection?"),
                  self.grammar)
        self.assertTrue(x["claim"]["logical_answer_in_admitted_model"])
        self.assertFalse(y["claim"]["logical_answer_in_admitted_model"])
        self.assertEqual(x["claim"]["possible_counterexample_count_bounds"],[0,0])

    def test_positive_certified_presence_reverses_answer(self):
        row=cases()[0]
        raw=raw_case(row,2) # all positive proxy targets proven present
        x=examine(dict(raw,question="Does detecting microwave reflection guarantee buried satellite?"),self.grammar)
        y=examine(dict(raw,question="Can microwave reflection appear without buried satellite?"),self.grammar)
        self.assertTrue(x["claim"]["logical_answer_in_admitted_model"])
        self.assertFalse(y["claim"]["logical_answer_in_admitted_model"])
        self.assertEqual(x["claim"]["possible_counterexample_count_bounds"],[0,0])

    def test_falsified_implications_are_logical_not_diagnostic(self):
        row=cases()[0]
        raw=raw_case(row,3) # synthetic certifies counterexamples
        x=examine(raw,self.grammar)
        y=examine(dict(raw,question="Does detecting microwave reflection guarantee buried satellite?"),self.grammar)
        self.assertFalse(x["claim"]["logical_answer_in_admitted_model"])
        self.assertFalse(y["claim"]["logical_answer_in_admitted_model"])
        self.assertGreater(x["claim"]["possible_counterexample_count_bounds"][0],0)
        self.assertGreater(y["claim"]["possible_counterexample_count_bounds"][0],0)

    def test_no_relevant_measurements_holds_not_global_absence(self):
        row=cases()[0]
        raw=raw_case(row,0)
        for obs in raw["observations"]:
            obs["negative"]=0
        out=examine(raw,self.grammar)
        self.assertIsNone(out["claim"]["logical_answer_in_admitted_model"])
        self.assertEqual(out["claim"]["verdict"],"HOLD_NO_RELEVANT_SAMPLE_CASES")

    def test_real_research_cannot_use_synthetic_latent_labels(self):
        raw=neuro_packet()
        raw["anchors"]=[{"group":raw["observations"][0]["group"],
                         "proxy":"negative","known_latent_true":1,
                         "known_latent_false":0,"origin":"SIMULATOR_TRUTH"}]
        out=examine(raw,self.grammar)
        self.assertEqual(out["status"],"HOLD_INVALID_SOURCE_EVIDENCE")
        self.assertIsNone(out["answer"])

    def test_reject_hidden_truth_injected_into_raw_input(self):
        raw=neuro_packet()
        raw["actual_experience"]=True
        with self.assertRaises(HOLD):
            examine(raw,self.grammar)

    def test_bad_count_refuses_inference(self):
        raw=neuro_packet()
        raw["observations"][0]["negative"]=-1
        self.assertEqual(examine(raw,self.grammar)["status"],
                         "HOLD_INVALID_SOURCE_EVIDENCE")

    def test_unknown_teacher_contradictory_semantics_refused(self):
        with open(__import__("pathlib").Path(__file__).with_name("teacher.json"),encoding="utf-8") as handle:
            items=json.load(handle)["examples"]
        items[0]["meaning"]="CAN_POS"
        with self.assertRaises(HOLD):learn(items)

    def test_teacher_roles_missing_refused(self):
        with open(__import__("pathlib").Path(__file__).with_name("teacher.json"),encoding="utf-8") as handle:
            items=json.load(handle)["examples"]
        items[0]["left"]="something else"
        with self.assertRaises(HOLD):learn(items)

    def test_teacher_duplicate_id_refused(self):
        with open(__import__("pathlib").Path(__file__).with_name("teacher.json"),encoding="utf-8") as handle:
            items=json.load(handle)["examples"]
        items[0]["id"]=items[1]["id"]
        with self.assertRaises(HOLD):learn(items)

    def test_malformed_grammar_does_not_execute(self):
        bad=deepcopy(self.grammar)
        bad["status"]="ADMIT_AUTONOMOUS_CONTROL"
        with self.assertRaises(HOLD):parse("Can buried satellite exist without microwave reflection?",bad)

    def test_budget_of_training_examples_required(self):
        with open(__import__("pathlib").Path(__file__).with_name("teacher.json"),encoding="utf-8") as handle:
            items=json.load(handle)["examples"]
        with self.assertRaises(HOLD):learn(items[:7])

    def test_source_name_vs_text_ambiguity_never_silently_matches(self):
        raw=neuro_packet()
        raw["indicator"]="brain electrical signal"
        self.assertEqual(examine(raw,self.grammar)["status"],
                         "HOLD_INDICATOR_SOURCE_MISMATCH")

    def test_strong_classical_reference_recognizes_some_new_forms(self):
        novel=[r for r in cases() if r["group"]=="new_lexical_paraphrase"]
        self.assertEqual(sum(parse_classical(r["question"],r["indicator"]) is not None
                             for r in novel),2)

    def test_full_registered_benchmark_and_negative_result(self):
        r=benchmark()
        self.assertEqual(r,benchmark())
        self.assertEqual(r["registered_cases"],48)
        self.assertEqual(r["valid_questions"],36)
        self.assertFalse(r["author_independent_blind_test"])
        metrics=r["metrics"]
        self.assertEqual(metrics["induced"]["ALL"]["correct_semantics"],32)
        self.assertEqual(metrics["rote"]["ALL"]["correct_semantics"],16)
        self.assertEqual(metrics["classical"]["ALL"]["correct_semantics"],34)
        self.assertEqual(metrics["always_hold"]["ALL"]["correct_semantics"],0)
        for name in metrics:
            self.assertEqual(metrics[name]["ALL"]["incorrect_semantics"],0,name)
            self.assertEqual(metrics[name]["ALL"]["incorrect_logical_verdict"],0,name)
            self.assertEqual(metrics[name]["ALL"]["unjustified_accepts"],0,name)
        self.assertEqual(metrics["induced"]["ALL"]["toy_selective_loss"],1.0)
        self.assertEqual(metrics["classical"]["ALL"]["toy_selective_loss"],.5)
        self.assertEqual(metrics["rote"]["ALL"]["toy_selective_loss"],5.0)

    def test_no_implicit_external_action(self):
        raw=neuro_packet()
        result=examine(raw,self.grammar)
        self.assertTrue(result["no_external_actions"])
        self.assertFalse(result["real_world_authority"])
        self.assertTrue(result["logical_operators_predeclared"])
        self.assertFalse(result["native_unrestricted_language_understanding"])

if __name__=="__main__":
    unittest.main()
