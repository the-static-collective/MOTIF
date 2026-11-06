"""Adversarial primary-source tests with sealed review annotations."""
from __future__ import annotations

import json
import unittest
from copy import deepcopy

from opinions import DOCUMENTS,documents,SOURCE_REVISION
from reader import (HOLD,source_document,source_pin,voiced_paragraphs,read,
                    export,validate,investigate,digest,normalize,speaker_header)
from bridge011 import evaluate,source_pin as prior_pin
from gold import NEW_EVALUATION,TRAINING_CONTROLS


class AdversarialOpinionTests(unittest.TestCase):
    def test_disjoint_court_split_and_source_integrity(self):
        self.assertEqual(set(documents(True)),{"MCBOYLE","VINEGAR"})
        self.assertEqual(set(documents(False)),{"NIX","YATES"})
        self.assertFalse(set(documents(True))&set(documents(False)))
        self.assertEqual(len(source_pin()),40)
        self.assertEqual(len(prior_pin()),40)
        self.assertTrue(all(x["url"].startswith("https://")
                            for x in DOCUMENTS.values()))
        self.assertTrue(all(len(x["paragraphs"])>=8 for x in DOCUMENTS.values()))
        self.assertEqual(len(DOCUMENTS["YATES"]["paragraphs"]),21)

    def test_train_context_opinion_headers_and_disposition_are_not_source_labels(self):
        for case,expect in TRAINING_CONTROLS.items():
            r=read(case)
            self.assertEqual(list(r["parsed_voices"]),expect["judges"])
            self.assertEqual(r["parsed_voices"][expect["judges"][0]]["role"],
                             "OPINION_OF_COURT")
            self.assertIn(expect["disposition"],
                          r["parsed_voices"][expect["judges"][0]]["disposition_signals"])
            self.assertFalse(r["authoritative_holding_automatically_inferred"])

    def test_first_unseen_tomato_opinion_keeps_science_and_tariff_ordinary_usage_apart(self):
        r=read("NIX")
        gold=NEW_EVALUATION["NIX"]
        self.assertEqual(set(r["parsed_voices"]),set(gold["speakers"]))
        for judge,expected in gold["speakers"].items():
            for k,v in expected.items():
                self.assertEqual(r["parsed_voices"][judge][k],v)
        signals={node["feature"] for node in r["evidence_nodes"]}
        self.assertIn("BOTANICAL_FRUIT",signals)
        self.assertIn("ORDINARY_VEGETABLE",signals)
        self.assertEqual(evaluate("NIX")["per_voice_interpretations"]["GRAY"][
                          "reported_legal_interpretation_status"],"UNDETERMINED")
        self.assertFalse(r["current_law_inferred"])

    def test_second_new_fish_opinion_recovers_three_distinct_judicial_voices(self):
        r=read("YATES")
        gold=NEW_EVALUATION["YATES"]
        self.assertEqual(set(r["parsed_voices"]),set(gold["speakers"]))
        for judge,expect in gold["speakers"].items():
            actual=r["parsed_voices"][judge]
            for key,value in expect.items():
                self.assertEqual(actual[key],value,msg=f"{judge}.{key}")
        self.assertTrue(any(x["relation"]==
            "COMPETING_VOICES_NOT_SINGLE_SOURCE_CONTRADICTION"
            for x in r["argument_links"]))

    def test_original_reason011_four_value_engine_preserves_vote_split(self):
        report=evaluate("YATES")
        self.assertEqual(report["named_judgment_alignment"],(5,4))
        views=report["per_voice_interpretations"]
        self.assertEqual(views["GINSBURG"]["reported_legal_interpretation_status"],
                         "SUPPORTED")
        self.assertEqual(views["ALITO"]["reported_legal_interpretation_status"],
                         "SUPPORTED")
        self.assertEqual(views["KAGAN"]["reported_legal_interpretation_status"],
                         "REFUTED")
        self.assertFalse(any(v["reported_legal_interpretation_status"]=="BOTH"
                             for v in views.values()))
        self.assertTrue(report["majority_judgment_is_not_single_majority_rationale"])

    def test_textual_distinction_no_single_majority_rationale_is_claimed(self):
        r=read("YATES")
        self.assertEqual(r["parsed_voices"]["GINSBURG"]["explicit_votes"],4)
        self.assertEqual(r["parsed_voices"]["ALITO"]["explicit_votes"],1)
        self.assertEqual(r["parsed_voices"]["KAGAN"]["explicit_votes"],4)
        self.assertEqual(r["parsed_voices"]["ALITO"]["role"],
                         "CONCURRENCE_IN_JUDGMENT")
        self.assertEqual(r["parsed_voices"]["KAGAN"]["role"],"DISSENT")

    def test_dissent_affirmance_is_not_mistaken_for_actual_disposition(self):
        y=read("YATES")["parsed_voices"]
        self.assertEqual(y["GINSBURG"]["disposition_signals"],["REVERSAL"])
        self.assertEqual(y["KAGAN"]["disposition_signals"],["AFFIRMANCE"])
        self.assertNotIn("AFFIRMANCE",y["GINSBURG"]["disposition_signals"])

    def test_party_arguments_and_lower_court_stances_not_promoted(self):
        r=read("YATES")
        all_nodes=r["evidence_nodes"]
        self.assertFalse(any(n["paragraph"]=="P05" for n in all_nodes))
        v=read("VINEGAR")
        self.assertFalse(any(n["paragraph"]=="P04" for n in v["evidence_nodes"]))
        self.assertTrue(all(n["judge"] in r["parsed_voices"] for n in all_nodes))

    def test_every_proof_span_replays_against_source_paragraph_digest(self):
        for case in DOCUMENTS:
            doc=source_document(case)
            report=read(case)
            for node in report["evidence_nodes"]:
                p=int(node["paragraph"][1:])-1
                text=doc["paragraphs"][p]
                from hashlib import sha256
                self.assertEqual(sha256(text.encode()).hexdigest(),
                                 node["source_sha256"])
                self.assertEqual(node["paragraph_text"],text)
                self.assertEqual(node["source_url"],doc["url"])

    def test_unsupported_cheese_lawsuit_correctly_holds(self):
        r=investigate("YATES","Is the courthouse made of cheese?")
        self.assertEqual(r["stage"],"HOLD_NO_RELEVANT_ANCHORED_EVIDENCE")
        self.assertEqual(r["sources"],[])
        self.assertFalse(r["legal_advice"])

    def test_relevant_question_returns_anchored_prose_not_fabricated_verdict(self):
        r=investigate("YATES","What did tangible object mean for record information fish?")
        self.assertEqual(r["stage"],"SOURCE_SPANS_NEED_INTERPRETATION")
        self.assertTrue(r["not_a_judicial_yes_no_answer"])
        self.assertGreaterEqual(len(r["sources"]),1)
        self.assertTrue(all(p["source_sha256"] for p in r["sources"]))

    def test_mismatching_source_data_and_unbounded_requests_hold(self):
        with self.assertRaises(HOLD):source_document("NOT_A_REAL_OPINION")
        with self.assertRaises(HOLD):investigate("YATES","")
        with self.assertRaises(HOLD):investigate("NIX","a"*400)
        self.assertIsNone(speaker_header("Justice"))

    def test_rehashed_dissent_promotion_or_laundered_evidence_cannot_pass(self):
        baseline=json.loads(export("YATES"))
        for mode in ("role","votes","quote","year","authority","argument"):
            doc=deepcopy(baseline)
            if mode=="role":
                doc["parsed_voices"]["KAGAN"]["role"]="OPINION_OF_COURT"
            elif mode=="votes":
                doc["parsed_voices"]["GINSBURG"]["explicit_votes"]=9
            elif mode=="quote":
                doc["evidence_nodes"][0]["paragraph_text"]="The fish is made of cheese"
            elif mode=="year":
                doc["year"]="2026"
            elif mode=="authority":
                doc["real_world_authority"]=True
            else:
                doc["argument_links"]=[]
            doc["checksum_sha256"]=digest({
                k:v for k,v in doc.items() if k!="checksum_sha256"})
            with self.subTest(mode=mode),self.assertRaises(HOLD):
                validate(json.dumps(doc))

    def test_export_validates_exact_source_owned_record(self):
        for case in DOCUMENTS:
            validated=validate(export(case))
            self.assertEqual(validated["case_id"],case)
            self.assertFalse(validated["external_execution"])
            self.assertFalse(validated["real_world_authority"])

    def test_cross_court_and_cross_year_cannot_become_judicial_rule(self):
        x=evaluate("YATES")
        self.assertTrue(x["no_current_precedential_authority_inferred"])
        n=read("NIX")
        self.assertNotEqual(n["year"],read("YATES")["year"])
        self.assertTrue(n["text_inference_only_from_declared_cues"])

    def test_injection_paragraph_if_source_code_changed_requires_new_owner_pin(self):
        from hashlib import sha1
        text=DOCUMENTS["YATES"]["paragraphs"][0]+" Chief Justice of Cheese"
        wrong=sha1(b"blob "+str(len(text.encode())).encode()+b"\0"+text.encode()).hexdigest()
        self.assertNotEqual(source_pin(),wrong)

    def test_no_full_raw_opinion_or_general_law_inference_claim(self):
        for case in DOCUMENTS:
            report=read(case)
            self.assertFalse(report["full_opinion_read"])
            self.assertFalse(report["current_law_inferred"])
            self.assertTrue(report["text_inference_only_from_declared_cues"])

if __name__=="__main__":
    unittest.main()
