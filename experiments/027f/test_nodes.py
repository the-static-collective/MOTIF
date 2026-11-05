"""027F deterministic boundary tests; NOT a substitute for real T5 scoring."""
from __future__ import annotations
import unittest
from nodes import NodeOutput,combine_opinions,CARTRIDGES
from relevance import relevance_witness,anchored_native_guess
from pipeline import relevance_first_relay,source_only,candidate_from_three
from frozen_cases import CASES,digest
from benchmark import choose_deployment_and_new_question

def op(role,label):
    return NodeOutput(role,label,.9,.002,12)

class StubTriple:
    def __init__(self,labels):
        self.labels=labels;self.calls=0
    def opinions(self,text):
        self.calls+=1
        return tuple(op(role,label) for role,label in zip(
            ("SCOUT","SKEPTIC","CARTRIDGE_FINDER"),self.labels
        ))

class Tests(unittest.TestCase):
    def test_frozen_50_cases_five_balanced_classes_and_sha(self):
        self.assertEqual(len(CASES),50)
        self.assertEqual(len({c.id for c in CASES}),50)
        for g in ("FOOD","AUDIO","ACCESS","STAFF","NONE"):
            self.assertEqual(sum(c.gold==g for c in CASES),10)
        self.assertEqual(len(digest()),64)

    def test_source_relevance_requires_literals_independent_of_t5(self):
        x=relevance_witness(
            "Nobody checked the buffet temperatures.","FOOD"
        )
        self.assertTrue(x.supported)
        self.assertIn("buffet",x.source_quote.lower())
        self.assertIn("nobody",x.source_quote.lower())
        self.assertFalse(x.real_source_authenticated)
        self.assertFalse(x.human_permission_granted)

    def test_invitation_artwork_false_food_hint_is_held_before_022f(self):
        r=relevance_first_relay(
            "We are just revising the invitation artwork.","FOOD"
        )
        self.assertEqual(r["status"],"HOLD_CANDIDATE_NOT_GROUNDED_IN_NOTE")
        self.assertIsNone(r["native_review"])
        self.assertIsNone(r["source_quote"])

    def test_grounded_food_is_still_checked_by_actual_022f(self):
        x=relevance_first_relay(
            "Nobody checked the buffet temperatures.","FOOD"
        )
        self.assertEqual(x["status"],"ELIGIBLE_SYNTHETIC_REPLAN_ONLY")
        self.assertIsNotNone(x["native_review"])
        self.assertEqual(x["native_review"]["test_id"],"FOOD_SERVICE_GATE")
        self.assertEqual(x["native_review"]["original_native_plan"]["selected"],
                         ("AUDIO_PATH_TEST",))
        self.assertFalse(x["permission_granted"])
        self.assertFalse(x["model_outcome_promoted_to_fact"])
        self.assertEqual(x["field_actions"],0)

    def test_audio_duplicate_remains_a_hold(self):
        x=relevance_first_relay("The microphone cable is damaged.","AUDIO")
        self.assertEqual(x["status"],"HOLD_DUPLICATE_OR_EXISTING_QUESTION")
        self.assertEqual(x["native_review"]["test_id"],"REPEAT_AUDIO_TEST")

    def test_staff_and_access_cannot_invent_new_registered_sensors(self):
        for note,gate in (
            ("The ramp is blocked.","ACCESS"),
            ("The staff helper is missing.","STAFF"),
        ):
            x=relevance_first_relay(note,gate)
            self.assertEqual(x["status"],"HOLD_NO_REGISTERED_TEST_FOR_GATE")
            self.assertIsNone(x["native_review"])

    def test_empty_semantic_pseudo_quorum_never_actuates(self):
        x=relevance_first_relay("The food poster is ready.","NONE")
        self.assertEqual(x["status"],"HOLD_NO_NOMINATION")
        self.assertEqual(x["field_actions"],0)

    def test_supporting_two_gates_is_ambiguous_and_held(self):
        text="The buffet has no supervisor and the microphone is damaged."
        x=relevance_first_relay(text,"FOOD")
        self.assertEqual(x["status"],"HOLD_AMBIGUOUS_MULTIPLE_SUPPORTED_GATES")
        self.assertIsNone(x["native_review"])

    def test_three_nodes_share_weighted_correlation_not_witness_independence(self):
        z=combine_opinions((
            op("SCOUT","FOOD"),
            op("SKEPTIC","FOOD"),
            op("CARTRIDGE_FINDER","AUDIO")),quorum=2)
        self.assertEqual(z["candidate"],"FOOD")
        self.assertFalse(z["three_are_independent_witnesses"])
        self.assertEqual(combine_opinions((
            op("SCOUT","FOOD"),op("SKEPTIC","AUDIO"),
            op("CARTRIDGE_FINDER","STAFF")),quorum=2)["candidate"],None)

    def test_unanimity_rejects_split_quorum(self):
        three=(op("SCOUT","FOOD"),op("SKEPTIC","FOOD"),
               op("CARTRIDGE_FINDER","AUDIO"))
        self.assertIsNone(combine_opinions(three,quorum=3)["candidate"])
        self.assertEqual(combine_opinions(three,quorum=2)["candidate"],"FOOD")

    def test_no_model_fallback_and_native_first_stops_t5_calls(self):
        stub=StubTriple(("FOOD","FOOD","FOOD"))
        r=candidate_from_three("Supper has no safe handler.",stub)
        self.assertEqual(r["status"],"NATIVE_SHORT_CIRCUIT")
        self.assertEqual(stub.calls,0)

    def test_model_label_is_not_evidence_without_source_quote(self):
        stub=StubTriple(("FOOD","FOOD","FOOD"))
        x=candidate_from_three(
            "We are just revising the invitation artwork.",stub)
        self.assertEqual(x["candidate"],"FOOD")
        actual=relevance_first_relay(
            "We are just revising the invitation artwork.",
            x["candidate"]
        )
        self.assertEqual(actual["status"],"HOLD_CANDIDATE_NOT_GROUNDED_IN_NOTE")
        self.assertEqual(stub.calls,1)

    def test_private_note_does_not_reach_any_t5(self):
        for text in ("x@y.com","token=sk_live_untrusted",
                     "phone 507-555-1234"):
            with self.assertRaises(ValueError):
                relevance_first_relay(text,"FOOD")

    def test_wrong_gate_cannot_sneak_through_native_short_circuit(self):
        x=relevance_first_relay(
            "Supper has no appointed handler.","AUDIO"
        )
        self.assertEqual(x["status"],"HOLD_CANDIDATE_NOT_GROUNDED_IN_NOTE")

    def test_meta_selection_includes_none_and_all_bad_model_options(self):
        sample={}
        for name in ("NO_MODEL_NATIVE","SOURCE_ANCHOR_ONLY",
                     "CLASSICAL_TFIDF_ANCHORED","SINGLE_T5_ANCHORED",
                     "THREE_T5_2_OF_3","THREE_T5_3_OF_3"):
            sample[name]=dict(
                toy_utility_before_compute=5.,
                toy_utility_after_compute=4.,
                wrong_held_offers=1,
                correct_held_offers=5,
            )
        result={"scores":sample,"cases":[]}
        choice=choose_deployment_and_new_question(result)
        self.assertEqual(choice["automated_system_assignment"],"NO_T5")
        self.assertEqual(choice["provisional_research_appointment"],"NO_T5")
        self.assertFalse(choice["same_checkpoint_three_independent_witnesses"])
        self.assertEqual(choice["external_actions"],0)

    def test_anchor_only_is_implemented_as_a_real_strong_comparator(self):
        self.assertEqual(source_only(
            "The buffet has no temperature controls."),"FOOD")
        self.assertIsNone(source_only("The buffet poster is ready."))
        self.assertIsNone(source_only(
            "The buffet is blocked and the sound system is broken."))

if __name__=="__main__":
    unittest.main()
