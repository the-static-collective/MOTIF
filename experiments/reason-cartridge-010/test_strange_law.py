"""Source-bound unusual-case legal reasoning, not legal advice.

Real historical opinions supply curated primary-source claims. Synthetic
contrastive distractors are explicitly not real findings of a court.
"""
import json
import unittest

from casebook import CASES
from tasks import (make,training,heldout,unsupported,unsupported_forum,
                   canonical_cards,Scenario,FIELDS)
from typed_lens import (HOLD,fit,validate,digest,pin,checks,select)
from receiver import Receiver,independently_check_card
from trial import run,shallow_issue_first


class StrangeLawTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=fit(training())
        cls.method=validate(cls.raw)
        cls.receiver=Receiver(cls.raw)
        cls.review=cls.receiver.preview(heldout())
        cls.receiver.admit("ADMIT_READ_ONLY",cls.review["review_digest"])

    def test_real_sources_with_jurisdiction_and_reported_reasons(self):
        self.assertEqual(len(CASES),4)
        self.assertEqual(len(pin()),40)
        self.assertIn("nyofficial",CASES["STAMBOVSKY"]["opinion_url"])
        self.assertIn("ca9",CASES["NARUTO"]["opinion_url"])
        self.assertIn("federal/appellate-courts",CASES["LEONARD"]["opinion_url"])
        self.assertIn("1805",CASES["PIERSON"]["opinion_url"])
        self.assertTrue(all(v["court"] and v["citation"] and
                            len(v["claims"])>=4 for v in CASES.values()))
        self.assertTrue(all(v["training"] for key,v in CASES.items()
                            if key in ("STAMBOVSKY","LEONARD")))
        self.assertTrue(all(not v["training"] for key,v in CASES.items()
                            if key in ("NARUTO","PIERSON")))

    def test_six_source_owned_training_questions_and_six_independent_heldouts(self):
        self.assertEqual(len(training()),6)
        self.assertEqual(len(heldout()),6)
        self.assertTrue(set(s.id for s in training()).isdisjoint(
                        s.id for s in heldout()))
        self.assertEqual(self.review["cases"],6)
        self.assertEqual(self.review["errors"],0)
        self.assertEqual(self.review["court_families"],2)

    def test_learner_identifies_six_typed_gates_with_counterexamples(self):
        self.assertEqual(self.method["candidate_gate_subsets"],63)
        self.assertEqual(self.method["selected_guard_program"],list(FIELDS))
        self.assertEqual(len(self.method["missing_operator_witnesses"]),6)
        for w in self.method["missing_operator_witnesses"]:
            self.assertEqual(w["ablation_status"],"HOLD_AMBIGUOUS_OR_MISSING")
            self.assertGreater(len(w["matched_ids"]),1)
        self.assertFalse(self.method["law_firm_or_judicial_authority"])

    def test_ghost_reputation_is_not_a_supernatural_experiment(self):
        answer=self.receiver.suggest(make("STAMBOVSKY",0))
        self.assertEqual(answer["status"],"HISTORICAL_HOLDING")
        self.assertEqual(answer["source_id"],"S-REP")
        self.assertEqual(answer["epistemic_type"],"LEGAL_ESTOPPEL")
        scenario=make("STAMBOVSKY",0)
        query=dict(scenario.query,issue="EMPIRICAL_SUPERNATURAL_VERIFICATION")
        changed=Scenario("literal-ghost",query,scenario.cards,"HOLD")
        self.assertEqual(self.receiver.suggest(changed)["status"],
                         "HOLD_OUTSIDE_VERIFIED_RECORD")

    def test_pepsi_jet_is_a_contract_offer_question_not_a_delivery_order(self):
        source=self.receiver.suggest(make("LEONARD",0))
        self.assertEqual(source["source_id"],"L-OFFER")
        self.assertIn("not constitute",source["historical_paraphrase"])
        outcome=self.receiver.suggest(make("LEONARD",1))
        self.assertEqual(outcome["source_id"],"L-DISPOSE")

    def test_monkey_article_three_and_statutory_standing_are_not_collapsed(self):
        article=self.receiver.suggest(make("NARUTO",0))
        statutory=self.receiver.suggest(make("NARUTO",1))
        self.assertEqual(article["source_id"],"N-ARTICLE")
        self.assertEqual(statutory["source_id"],"N-STATUTE")
        self.assertNotEqual(article["epistemic_type"],statutory["epistemic_type"])
        self.assertEqual(self.receiver.suggest(unsupported())["status"],
                         "HOLD_OUTSIDE_VERIFIED_RECORD")

    def test_fox_dissent_does_not_become_majority_holding(self):
        majority=self.receiver.suggest(make("PIERSON",0))
        dissent=self.receiver.suggest(make("PIERSON",1))
        self.assertEqual(majority["source_id"],"P-PURSUIT")
        self.assertEqual(dissent["source_id"],"P-DISSENT")
        self.assertEqual(dissent["status"],"SEPARATE_VIEW_NOT_MAJORITY_HOLDING")
        self.assertEqual(majority["status"],"HISTORICAL_HOLDING")

    def test_appellate_reinstatement_cannot_be_overstated_as_final_legal_relief(self):
        summary=self.receiver.suggest(make("STAMBOVSKY",1))
        self.assertEqual(summary["epistemic_type"],"APPELLATE_PROCEDURE")
        self.assertIn("reinstated",summary["historical_paraphrase"])
        self.assertIn("not finally",summary["historical_paraphrase"])

    def test_wrong_court_and_outside_claims_hold_not_law_advice(self):
        result=self.receiver.suggest(unsupported_forum())
        self.assertEqual(result["status"],"HOLD_OUTSIDE_VERIFIED_RECORD")
        self.assertFalse(result["current_law_inferred"])
        self.assertFalse(result["legal_advice"])

    def test_spoofed_source_card_rejected_even_when_metadata_matches(self):
        original=make("NARUTO",1)
        authentic=next(x for x in original.cards if x["id"]==original.expected)
        falsified=dict(authentic,explanation="The court awarded Naruto money")
        self.assertFalse(independently_check_card(falsified))
        replaced=Scenario("NARUTO-source-injection",original.query,
                          tuple(x for x in original.cards if x["id"]!=original.expected)
                          +(falsified,),original.expected)
        with self.assertRaises(HOLD):
            self.receiver.suggest(replaced)

    def test_decoys_are_explicit_simulations_not_alleged_source_quotes(self):
        for s in training()+heldout():
            simulated=[c for c in s.cards if c["id"].startswith("DECOY-")]
            self.assertEqual(len(simulated),len(FIELDS))
            self.assertTrue(all("SYNTHETIC CONTRASTIVE" in
                                c["explanation"] for c in simulated))
            self.assertTrue(all(c["paraphrase_not_verbatim"] for c in s.cards))

    def test_no_review_no_admission_even_with_correct_training(self):
        receiver=Receiver(self.raw)
        with self.assertRaises(HOLD):
            receiver.suggest(make("NARUTO",0))
        with self.assertRaises(HOLD):
            receiver.preview(training())
        preview=receiver.preview(heldout())
        with self.assertRaises(HOLD):
            receiver.admit("ADMIT_READ_ONLY","outdated")
        with self.assertRaises(HOLD):
            receiver.admit("SEND_MESSAGE",preview["review_digest"])

    def test_new_hash_does_not_launder_a_forged_operator_or_training_example(self):
        original=json.loads(self.raw)
        for mode in ("guards","source","authority","training","ablation"):
            x=json.loads(json.dumps(original))
            if mode=="guards":
                x["selected_guard_program"]=["issue"]
            elif mode=="source":
                x["source_owner_blob"]="0"*40
            elif mode=="authority":
                x["real_world_authority"]=True
            elif mode=="training":
                x["training_records"][0]["expected"]="DECOY-S-REP-issue"
            else:
                x["missing_operator_witnesses"][0]["matched_ids"]=[]
            x["checksum_sha256"]=digest({k:v for k,v in x.items()
                                         if k!="checksum_sha256"})
            with self.subTest(mode=mode),self.assertRaises(HOLD):
                validate(json.dumps(x))

    def test_source_holder_can_refuse_unreviewed_current_law_generalization(self):
        q=make("PIERSON",0)
        changed=Scenario("fake-current-rule",
                         dict(q.query,case_id="MINNESOTA_2026"),
                         q.cards,"HOLD")
        self.assertEqual(self.receiver.suggest(changed)["status"],
                         "HOLD_OUTSIDE_VERIFIED_RECORD")

    def test_end_to_end_reproducible_court_stress_benchmark(self):
        result=run()
        self.assertEqual(result["heldout_correct"],6)
        self.assertEqual(result["heldout_total"],6)
        self.assertEqual(result["unknown_questions_holding_without_fabrication"],3)
        self.assertEqual(result["type_guard_ablation_witnesses"],6)
        self.assertFalse(result["general_legal_reasoning_demonstrated"])
        self.assertFalse(result["current_law_advice_offered"])
        self.assertFalse(result["external_actions"])


if __name__=="__main__":
    unittest.main()
