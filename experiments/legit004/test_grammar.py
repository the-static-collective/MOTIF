"""LEGIT-004 research falsifiers: no hidden gold, unsupported grammar holds,
semantic direction preserved, classical baseline not disadvantaged.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from grammar import HOLD, learn, parse
from bridge import trained_grammar, examine, historical_neuroscience, assemble
from benchmark import registered, raw_case, classical, report


class InducedQuestionGrammarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grammar=trained_grammar()

    def test_teacher_learns_four_rules_without_domain_specific_words(self):
        self.assertEqual(self.grammar["teacher_count"],8)
        self.assertEqual(len(self.grammar["rules"]),4)
        templates=str(self.grammar["rules"])
        for token in ("neural command","sonar echo","bacterial growth",
                      "alien civilization","radio emission"):
            self.assertNotIn(token,templates)

    def test_known_forms_generalize_to_unseen_terms(self):
        for row in registered():
            if row["group"]!="learned_syntax_unseen_domains":continue
            ans=parse(row["question"],self.grammar)
            self.assertEqual(ans["status"],"PARSE_PROPOSAL_ONLY",row["id"])
            self.assertEqual((ans["kind"],ans["proxy"],ans["target"]),
                             (row["gold"]["kind"],row["gold"]["proxy"],
                              row["gold"]["target"]),row["id"])

    def test_true_novel_phrasings_are_not_falsely_promoted(self):
        for row in registered():
            if row["group"]!="unseen_paraphrase":continue
            self.assertEqual(parse(row["question"],self.grammar)["status"],
                             "HOLD_UNKNOWN_GRAMMAR",row["id"])

    def test_hostile_reversals_and_negations_hold(self):
        for row in registered():
            if row["group"]!="hostile_or_unsupported":continue
            self.assertNotEqual(parse(row["question"],self.grammar)["status"],
                                "PARSE_PROPOSAL_ONLY",row["id"])

    def test_mismatch_between_source_indicator_and_parsed_proxy_holds(self):
        for row in registered():
            if row["group"]!="source_indicator_mismatch":continue
            raw=raw_case(row,3)
            out=examine(raw,self.grammar)
            self.assertEqual(out["status"],"HOLD_SOURCE_INDICATOR_MISMATCH")

    def test_public_neuroscience_question_without_supplied_latent_schema(self):
        packet=historical_neuroscience()
        self.assertNotIn("latent_target",packet)
        self.assertNotIn("observed_proxy",packet)
        result=examine(packet,self.grammar)
        self.assertEqual(result["status"],"RESEARCH_HOLD")
        self.assertEqual(result["parser"]["proxy"],"task based neural command following")
        self.assertEqual(result["parser"]["target"],"subjective experience")
        self.assertEqual(result["reasoned_claim"]["compatible_latent_true_bounds"],[0,250])
        self.assertEqual(result["reasoned_claim"]["verdict"],
                         "NOT_IDENTIFIABLE_FROM_ADMITTED_EVIDENCE")
        self.assertIsNone(result["reasoned_claim"]["individual_probability"])
        self.assertFalse(result["real_world_authority"])

    def test_source_labels_not_hidden_in_raw_task(self):
        row=registered()[0]
        raw=raw_case(row,0)
        self.assertNotIn("target",raw)
        self.assertNotIn("gold",raw)
        typed,meaning=assemble(raw,self.grammar)
        self.assertEqual(typed["latent_target"],"FISSILE_MATERIAL")
        self.assertEqual(typed["observed_proxy"],"NEUTRON_FLUX_GAUGE")
        self.assertEqual(typed["anchors"],[])
        self.assertEqual(meaning["kind"],"PROXY_NEGATIVE_IMPLIES_TARGET_ABSENT")

    def test_positive_claim_direction_supported_without_known_target_labels(self):
        row=next(x for x in registered() if x["id"]=="I09")
        result=examine(raw_case(row,8),self.grammar)
        self.assertEqual(result["reasoned_claim"]["kind"],
                         "PROXY_POSITIVE_IMPLIES_TARGET_PRESENT")
        self.assertEqual(result["reasoned_claim"]["antecedent_proxy"],"positive")
        self.assertEqual(result["reasoned_claim"]["verdict"],
                         "NOT_IDENTIFIABLE_FROM_ADMITTED_EVIDENCE")
        self.assertIsNone(result["reasoned_claim"]["individual_probability"])

    def test_fewer_than_two_teacher_instances_refused(self):
        import json
        from bridge import GRAMMAR_FILE
        with open(GRAMMAR_FILE,encoding="utf-8") as fp:
            teacher=json.load(fp)["examples"]
        with self.assertRaises(HOLD):learn(teacher[:-1])

    def test_repeated_teacher_identifiers_refused(self):
        import json
        from bridge import GRAMMAR_FILE
        with open(GRAMMAR_FILE,encoding="utf-8") as fp:
            teacher=json.load(fp)["examples"]
        teacher[0]["id"]=teacher[1]["id"]
        with self.assertRaises(HOLD):learn(teacher)

    def test_invalid_teacher_contradictory_kind_refused(self):
        import json
        from bridge import GRAMMAR_FILE
        with open(GRAMMAR_FILE,encoding="utf-8") as fp:
            teacher=json.load(fp)["examples"]
        teacher[1]["kind"]="PROXY_POSITIVE_IMPLIES_TARGET_PRESENT"
        with self.assertRaises(HOLD):learn(teacher)

    def test_unknown_teacher_intent_refused(self):
        import json
        from bridge import GRAMMAR_FILE
        with open(GRAMMAR_FILE,encoding="utf-8") as fp:
            teacher=json.load(fp)["examples"]
        teacher[0]["kind"]="PROVE_PATIENT_UNCONSCIOUS"
        with self.assertRaises(HOLD):learn(teacher)

    def test_reused_proxy_target_does_not_count_as_distinct_teacher(self):
        import json
        from bridge import GRAMMAR_FILE
        with open(GRAMMAR_FILE,encoding="utf-8") as fp:
            teacher=json.load(fp)["examples"]
        teacher[1]["proxy"]=teacher[0]["proxy"]
        teacher[1]["target"]=teacher[0]["target"]
        teacher[1]["question"]=teacher[0]["question"]
        with self.assertRaises(HOLD):learn(teacher)

    def test_unsupported_punctuation_and_braced_injection_hold(self):
        with self.assertRaises(HOLD):
            parse("If {proxy} is negative, must awareness be absent?",self.grammar)

    def test_source_count_tampering_refused(self):
        row=registered()[0]
        raw=raw_case(row,0)
        raw["observations"][0]["positive"]=-2
        result=examine(raw,self.grammar)
        self.assertEqual(result["status"],"HOLD_INVALID_SOURCE_EVIDENCE")

    def test_invalid_source_url_refused(self):
        row=registered()[0]
        raw=raw_case(row,0)
        raw["sources"][0]["url"]="https://faked-synthetic-source"
        result=examine(raw,self.grammar)
        self.assertEqual(result["status"],"HOLD_INVALID_SOURCE_EVIDENCE")

    def test_real_world_patient_claim_not_authorized(self):
        raw=historical_neuroscience()
        raw["scope"]="LIVE_PATIENT_DIAGNOSIS"
        with self.assertRaises(HOLD):examine(raw,self.grammar)

    def test_unknown_hidden_answer_field_rejected(self):
        raw=historical_neuroscience()
        raw["secret_truth"]=True
        with self.assertRaises(HOLD):examine(raw,self.grammar)

    def test_whitespace_and_case_invariance(self):
        first=registered()[0]
        query="  "+first["question"].upper().replace(" ","  ")+"  "
        guess=parse(query,self.grammar)
        self.assertEqual(guess["kind"],first["gold"]["kind"])
        self.assertEqual(guess["proxy"],first["gold"]["proxy"])

    def test_classical_reference_handles_more_novel_paraphrases(self):
        novel=[x for x in registered() if x["group"]=="unseen_paraphrase"]
        baseline=sum(classical(raw_case(x,i)) is not None for i,x in enumerate(novel))
        self.assertEqual(baseline,2)

    def test_benchmark_reproducibility_and_honest_classical_lead(self):
        observed=report()
        self.assertEqual(observed,report())
        self.assertEqual(observed["evaluation_cases"],30)
        self.assertFalse(observed["full_text_to_evidence_comprehension"])
        induct=observed["methods"]["induced"]
        classic=observed["methods"]["strong_classical_regex"]
        self.assertEqual(induct["correct_accepted"],16)
        self.assertEqual(classic["correct_accepted"],18)
        self.assertEqual(induct["false_accept"],0)
        self.assertEqual(classic["false_accept"],0)
        self.assertGreater(induct["toy_loss"],classic["toy_loss"])
        self.assertEqual(observed["clinical_packet_implication"],
                         "NOT_IDENTIFIABLE_FROM_ADMITTED_EVIDENCE")


if __name__=="__main__":
    unittest.main()
