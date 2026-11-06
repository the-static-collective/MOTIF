"""Adversarial tests: legal impossibilities without paraconsistent explosion."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from casebook import cases,by_id,lit,claim,rule,question
from engine import (HOLD,decide,export,validate,validate_case,derive,verdict,
                    remedial_questions,digest,pin,SCHEMA)
from reference import independent


class ImpossibleCourtTests(unittest.TestCase):
    def test_casebook_is_fictional_not_current_law(self):
        self.assertEqual(len(cases()),4)
        self.assertEqual(len(pin()),40)
        self.assertTrue(all(c["fictional"] for c in cases()))
        for c in cases():
            self.assertTrue(validate_case(c))
            self.assertTrue(all(rule["rule_status"]=="HYPOTHETICAL_NORM_NOT_REAL_LAW"
                                for rule in c["rules"]))

    def test_independent_classical_reference_agrees_on_all_ten_queries(self):
        count=0
        for c in cases():
            reference=independent(c)
            answer=decide(c)
            self.assertTrue(answer["all_expected_checks_match"])
            self.assertEqual(len(answer["results"]),len(reference))
            for row in answer["results"]:
                self.assertEqual(row["result"]["four_value"],
                                 reference[row["query_id"]])
                self.assertEqual(row["result"]["four_value"],
                                 row["fictional_expected_for_test"])
                count+=1
        self.assertEqual(count,10)

    def test_future_contract_distinguishes_present_acceptance_from_later_self(self):
        report=decide(by_id("FUTURE_SELF_CONTRACT"))
        self.assertEqual([x["result"]["four_value"] for x in report["results"]],
                         ["REFUTED","UNDETERMINED"])
        self.assertEqual(report["party_allegations_excluded"],2)
        present=report["results"][0]
        self.assertEqual(present["result"]["negative_proof"]["claims"],
                         ["T-NOT-SIGNED"])
        self.assertEqual(present["result"]["negative_proof"]["rules"],
                         ["T-NOT-VALID"])
        self.assertNotIn("T-LATER-SIGNATURE",
                         present["result"]["negative_proof"]["claims"])

    def test_machine_personhood_contradiction_keeps_both_proofs(self):
        c=by_id("ROBOT_INHERITANCE")
        title=decide(c)["results"][0]
        proof=title["result"]
        self.assertEqual(proof["four_value"],"BOTH")
        self.assertEqual(proof["positive_proof"]["claims"],
                         ["R-ELIGIBLE","R-GIFT"])
        self.assertEqual(proof["negative_proof"]["claims"],
                         ["R-GIFT","R-INELIGIBLE"])
        self.assertEqual(len(proof["contradiction_witness"]["claim_witness_ids"]),3)
        self.assertEqual(len(title["counterfactual_review_questions"]),2)
        self.assertEqual({x["counterfactual_if_withdrawn"]
                          for x in title["counterfactual_review_questions"]},
                         {"SUPPORTED","REFUTED"})
        self.assertTrue(all(not x["observation_performed"] for x in
                            title["counterfactual_review_questions"]))

    def test_machine_contradiction_cannot_prove_the_court_is_cheese(self):
        outcomes=decide(by_id("ROBOT_INHERITANCE"))["results"]
        self.assertEqual(outcomes[1]["result"]["four_value"],"UNDETERMINED")
        self.assertIsNone(outcomes[1]["result"]["positive_proof"])
        self.assertIsNone(outcomes[1]["result"]["negative_proof"])

    def test_divergent_courts_are_not_one_global_contradiction(self):
        result=decide(by_id("RIVAL_COURTS"))
        self.assertEqual([x["result"]["four_value"] for x in result["results"]],
                         ["SUPPORTED","REFUTED","UNDETERMINED"])
        self.assertEqual(result["party_allegations_excluded"],1)
        self.assertTrue(all(x["result"]["contradiction_witness"] is None
                            for x in result["results"]))
        self.assertTrue(result["time_forum_identity_separated"])

    def test_self_annulling_judgment_terminates_without_explosion(self):
        result=decide(by_id("SELF_NULLIFYING_ORDER"))
        self.assertEqual([x["result"]["four_value"] for x in result["results"]],
                         ["BOTH","BOTH","UNDETERMINED"])
        self.assertLess(result["proof_count"],15)
        self.assertFalse(result["results"][0]["result"]["explosion_permitted"])
        self.assertTrue(result["results"][0]["result"]["contradiction_witness"])

    def test_legal_allegation_never_automatically_becomes_a_fact(self):
        c=by_id("FUTURE_SELF_CONTRACT")
        self.assertIn("T-PARTY-RETRO", [x["id"] for x in c["claims"]])
        self.assertNotIn("T-PARTY-RETRO",{
            k for proof in derive(c).values() for k in proof["claims"]})
        self.assertEqual(decide(c)["results"][0]["result"]["four_value"],
                         "REFUTED")

    def test_no_unreviewed_source_mutation_can_be_adjudicated(self):
        c=deepcopy(by_id("FUTURE_SELF_CONTRACT"))
        c["claims"][0]["literal"]["predicate"]="COURT_MADE_OF_CHEESE"
        with self.assertRaises(HOLD):
            decide(c)

    def test_cross_forum_rules_are_refused_at_schema_boundary(self):
        c=deepcopy(by_id("RIVAL_COURTS"))
        c["rules"][0]["conclusion"]["forum"]="EXTERNAL_WORLD"
        with self.assertRaises(HOLD):
            validate_case(c,authenticate=False)

    def test_cross_time_rules_are_refused_at_schema_boundary(self):
        c=deepcopy(by_id("FUTURE_SELF_CONTRACT"))
        c["rules"][0]["premises"][0]["epoch"]="2040"
        with self.assertRaises(HOLD):
            validate_case(c,authenticate=False)

    def test_cross_identity_rules_are_refused_at_schema_boundary(self):
        c=deepcopy(by_id("FUTURE_SELF_CONTRACT"))
        c["rules"][0]["premises"][0]["subject"]="MARA_2040"
        with self.assertRaises(HOLD):
            validate_case(c,authenticate=False)

    def test_pure_missing_evidence_is_not_negation(self):
        c=by_id("RIVAL_COURTS")
        empty=lit("EXTERNAL_WORLD","2051","EVENT_K","COURT_MADE_OF_CHEESE")
        self.assertEqual(verdict(derive(c),empty)["four_value"],"UNDETERMINED")
        self.assertFalse(verdict(derive(c),empty)["explosion_permitted"])

    def test_hypothetical_retractions_never_modify_original_source(self):
        c=by_id("ROBOT_INHERITANCE")
        original=digest(c)
        self.assertEqual(verdict(derive(c,("R-INELIGIBLE",)),
                                 c["queries"][0]["literal"])["four_value"],
                         "SUPPORTED")
        self.assertEqual(verdict(derive(c,("R-ELIGIBLE",)),
                                 c["queries"][0]["literal"])["four_value"],
                         "REFUTED")
        self.assertEqual(digest(c),original)
        self.assertEqual(decide(c)["results"][0]["result"]["four_value"],"BOTH")

    def test_cannot_retract_unreviewable_or_imaginary_premise(self):
        with self.assertRaises(HOLD):
            derive(by_id("ROBOT_INHERITANCE"),("R-GIFT",))
        with self.assertRaises(HOLD):
            derive(by_id("ROBOT_INHERITANCE"),("NONEXISTENT",))
        with self.assertRaises(HOLD):
            derive(by_id("FUTURE_SELF_CONTRACT"),("T-PARTY-RETRO",))

    def test_malformed_claim_polarity_and_source_status_refused(self):
        c=deepcopy(by_id("ROBOT_INHERITANCE"))
        c["claims"][0]["literal"]["sign"]="PROBABLY"
        with self.assertRaises(HOLD):
            validate_case(c,authenticate=False)
        c=deepcopy(by_id("ROBOT_INHERITANCE"))
        c["claims"][0]["source_status"]="REAL_LAW"
        with self.assertRaises(HOLD):
            validate_case(c,authenticate=False)

    def test_replayable_dossiers_for_every_source_owned_case(self):
        for c in cases():
            raw=export(c)
            self.assertEqual(validate(raw)["case_id"],c["id"])
            doc=json.loads(raw)
            self.assertTrue(doc["fictional"])
            self.assertFalse(doc["real_world_authority"])
            self.assertFalse(doc["current_law_inferred"])
            self.assertTrue(doc["all_expected_checks_match"])

    def test_rehashed_fake_outcome_proof_scope_cannot_be_laundered(self):
        raw=json.loads(export(by_id("ROBOT_INHERITANCE")))
        for mode in ("outcome","proof","authority","scope","fake_review"):
            p=deepcopy(raw)
            if mode=="outcome":
                p["results"][0]["result"]["four_value"]="SUPPORTED"
            elif mode=="proof":
                p["results"][0]["result"]["positive_proof"]["claims"]=[]
            elif mode=="authority":
                p["real_world_authority"]=True
            elif mode=="scope":
                p["results"][0]["literal"]["forum"]="REAL_SUPREME_COURT"
            else:
                p["results"][0]["counterfactual_review_questions"][0][
                    "observation_performed"]=True
            p["checksum_sha256"]=digest({k:v for k,v in p.items()
                                         if k!="checksum_sha256"})
            with self.subTest(mode=mode),self.assertRaises(HOLD):
                validate(json.dumps(p))

    def test_no_judicial_prediction_or_external_action_claim(self):
        for c in cases():
            report=decide(c)
            self.assertFalse(report["current_law_inferred"])
            self.assertFalse(report["external_actions"])
            self.assertFalse(report["real_world_authority"])
            self.assertTrue(report["explicit_negation_not_negation_as_failure"])

    def test_boundary_no_missing_rule_established_from_dissent(self):
        c=by_id("FUTURE_SELF_CONTRACT")
        keylist=set(derive(c))
        self.assertFalse(any("RETROACTIVE_LEGAL_PERSONHOOD" in str(key)
                             for key in keylist))

if __name__=="__main__":
    unittest.main()
