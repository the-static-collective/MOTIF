"""Adversarial tests of real short opinion excerpts with conservative scope."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from corpus import OPINIONS,passages,SOURCE_REVISION
from review_keys import LABELS,TRAIN_KEYS,SEALED_KEYS,labeled_training
from classifier import HOLD,CUES,feature,fit,validate,classify,digest,pin_source
from receiver import Receiver,exact_source
from bridge011 import evaluate,checked_evidence,pin_prior
from trial import trained,run


class RealOpinionExcerptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw,cls.receiver,cls.review=trained()
        cls.method=validate(cls.raw)

    def test_six_real_source_linked_opinions_and_nonleaking_train_split(self):
        self.assertEqual(len(OPINIONS),6)
        self.assertEqual(len(passages(True)),8)
        self.assertEqual(len(passages(False)),4)
        self.assertEqual(tuple(p["span_id"] for p in passages(True)),TRAIN_KEYS)
        self.assertEqual(tuple(p["span_id"] for p in passages(False)),SEALED_KEYS)
        self.assertEqual(len(pin_source()),40)
        self.assertTrue(all(not OPINIONS[x]["train"] for x in ("ULYSSES","COCA")))
        self.assertTrue(all(OPINIONS[x]["train"] for x in
                            ("STAMBOVSKY","LEONARD","NARUTO","PIERSON")))

    def test_copyright_quote_budget_citation_and_court_metadata(self):
        for case,opinion in OPINIONS.items():
            p=[x for x in passages(True)+passages(False) if x["case_id"]==case]
            self.assertLessEqual(sum(x["word_count"] for x in p),25)
            self.assertTrue(opinion["url"].startswith("https://"))
            self.assertEqual(len(p),2)
            self.assertTrue(all(exact_source(x) for x in p))
            self.assertTrue(all(x["paragraph_locator"] and x["citation"] for x in p))

    def test_feature_routes_learned_from_training_not_hardcoded_labels(self):
        self.assertEqual(len(CUES),5)
        self.assertEqual(len(self.method["learned_feature_routes"]),4)
        self.assertEqual(self.method["learned_feature_routes"],{
            "F_A":"PARTY_ALLEGATION","F_B":"SEPARATE_OPINION",
            "F_C":"PROCEDURAL_POSTURE","F_D":"LEGAL_TREATMENT"})
        self.assertNotIn("F_E",self.method["learned_feature_routes"])
        for row,label in labeled_training():
            self.assertEqual(classify(self.method,row["text"])["type"],label)

    def test_two_never_trained_legal_opinions_yield_three_grounded_labels(self):
        self.assertEqual(self.review["new_opinion_cases"],2)
        self.assertEqual(self.review["correct_accepted"],3)
        self.assertEqual(self.review["correct_abstentions"],1)
        self.assertEqual(self.review["errors"],0)
        self.assertTrue(self.receiver.approved)

    def test_untaught_factual_dispute_abstains_instead_of_inventing_answer(self):
        drink=next(x for x in passages(False) if x["span_id"]=="C2")
        self.assertEqual(feature(drink["text"]),["F_E"])
        out=self.receiver.suggest(drink)
        self.assertEqual(out["stage"],"HOLD_UNFAMILIAR_LEGAL_EPISTEMIC_CATEGORY")
        self.assertFalse(out["legal_advice"])
        self.assertFalse(out["real_world_authority"])

    def test_ulysses_result_no_arbitrary_free_speech_conclusion(self):
        book=next(x for x in passages(False) if x["span_id"]=="U1")
        out=self.receiver.suggest(book)
        self.assertEqual(out["stage"],"SUGGEST_ONLY")
        self.assertEqual(out["category"],"LEGAL_TREATMENT")
        self.assertIn("not pornographic",out["fragment"])
        self.assertFalse(out["full_opinion_interpreted"])

    def test_trained_source_still_carries_party_dissent_boundaries(self):
        party=next(x for x in passages(True) if x["span_id"]=="L1")
        dissent=next(x for x in passages(True) if x["span_id"]=="P2")
        self.assertEqual(self.receiver.suggest(party)["category"],"PARTY_ALLEGATION")
        self.assertEqual(self.receiver.suggest(dissent)["category"],"SEPARATE_OPINION")

    def test_independent_review_required_digest_bound(self):
        fresh=Receiver(self.raw)
        with self.assertRaises(HOLD):
            fresh.suggest(passages(False)[0])
        with self.assertRaises(HOLD):
            fresh.preview(passages(True)[:4])
        report=fresh.preview(passages(False))
        with self.assertRaises(HOLD):
            fresh.admit("EXECUTE_COURT_ACTION",report["review_digest"])
        with self.assertRaises(HOLD):
            fresh.admit("ADMIT_READ_ONLY","stale")
        fresh.admit("ADMIT_READ_ONLY",report["review_digest"])
        self.assertTrue(fresh.approved)

    def test_training_label_tamper_rejected_by_independent_curator(self):
        fake=[(dict(row),label) for row,label in labeled_training()]
        fake[0]=(fake[0][0],"PROCEDURAL_POSTURE")
        try:
            raw=fit(tuple(fake))
        except HOLD:
            return
        receiver=Receiver(raw)
        with self.assertRaises(HOLD):
            receiver.preview(passages(False))

    def test_rehashed_classifier_with_changed_cue_or_authority_is_invalid(self):
        for variant in ("source","feature","route","evidence","execute","scope"):
            obj=json.loads(self.raw)
            if variant=="source":
                obj["source_corpus_blob"]="0"*40
            elif variant=="feature":
                obj["feature_grammar"]["F_C"]=[".*"]
            elif variant=="route":
                obj["learned_feature_routes"]["F_D"]="PARTY_ALLEGATION"
            elif variant=="evidence":
                obj["training_evidence"][0]["label"]="SEPARATE_OPINION"
            elif variant=="execute":
                obj["external_actions"]=True
            else:
                obj["scope"]="BINDING_US_LAW"
            obj["checksum_sha256"]=digest({k:v for k,v in obj.items()
                                           if k!="checksum_sha256"})
            with self.subTest(variant=variant),self.assertRaises(HOLD):
                validate(json.dumps(obj))

    def test_spoofed_opinion_excerpt_refused_even_if_citation_is_correct(self):
        target=deepcopy(passages(False)[0])
        target["text"]="I hold, therefore, that Mars is made of cheese"
        with self.assertRaises(HOLD):
            self.receiver.suggest(target)
        target=deepcopy(passages(False)[0])
        target["opinion_url"]="https://example.com/counterfeit-judgment"
        with self.assertRaises(HOLD):
            self.receiver.suggest(target)

    def test_bridge_reuses_exact_prior_four_valued_logic(self):
        self.assertEqual(len(pin_prior()),40)
        report=evaluate(self.receiver)
        p=report["four_value_propositions"]
        self.assertEqual(p["NARUTO/ARTICLE_III_STANDING"]["four_value"],"SUPPORTED")
        self.assertEqual(p["NARUTO/COPYRIGHT_STATUTORY_STANDING"]["four_value"],"REFUTED")
        self.assertEqual(p["COCA/CAFFEINE_ADDED_INGREDIENT"]["four_value"],"SUPPORTED")
        self.assertEqual(p["COCA/CAFFEINE_HARM_PROVEN"]["four_value"],"UNDETERMINED")
        self.assertFalse(report["current_law_inferred"])

    def test_estoppel_is_not_proof_of_a_real_ghost(self):
        result=evaluate(self.receiver)["four_value_propositions"]
        self.assertEqual(result["STAMBOVSKY/ESTOPPEL_REPUTATION"]["four_value"],
                         "SUPPORTED")
        self.assertEqual(result["STAMBOVSKY/PHYSICAL_GHOST_EXISTS"]["four_value"],
                         "UNDETERMINED")

    def test_court_decision_and_litigant_allegation_remain_separate(self):
        report=evaluate(self.receiver)
        excludes={x["span_id"] for x in report["excluded_nonholdings_unresolved_or_unclassified"]}
        self.assertIn("L1",excludes)
        self.assertIn("P2",excludes)
        self.assertIn("C2",excludes)
        self.assertEqual(report["new_real_world_observations"],0)
        self.assertTrue(report["curator_supplied_issue_and_polarity"])

    def test_chocolate_milk_vs_coca_caffeine_no_health_harm_invented(self):
        p=evaluate(self.receiver)["four_value_propositions"]
        self.assertEqual(p["COCA/CAFFEINE_HARM_PROVEN"]["four_value"],
                         "UNDETERMINED")
        self.assertEqual(p["ULYSSES/FORFEITURE_GRANTED"]["four_value"],"REFUTED")
        self.assertEqual(p["ULYSSES/PORNOGRAPHIC_INTENT"]["four_value"],"REFUTED")

    def test_only_exact_historical_source_fragments_are_supported(self):
        with self.assertRaises(HOLD):
            self.receiver.suggest({"text":"Supreme Court says cheese"})
        with self.assertRaises(HOLD):
            self.receiver.suggest(None)
        self.assertEqual(len(evaluate(self.receiver)["pairwise_nonconflations"]),3)

    def test_benchmark_retains_honest_baseline_and_abstention(self):
        report=run()
        self.assertEqual(report["heldout_correct_accepted"],3)
        self.assertEqual(report["heldout_correct_abstained"],1)
        self.assertEqual(report["heldout_errors"],0)
        self.assertEqual(report["naive_always_legal_holdout_correct"],2)
        self.assertFalse(report["live_source_quote_verification_in_CI"])
        self.assertTrue(report["strong_classical_predefined_typed_cue_baseline_may_tie"])
        self.assertFalse(report["external_actions"])


if __name__=="__main__":
    unittest.main()
