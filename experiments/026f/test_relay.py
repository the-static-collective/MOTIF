"""026F: deterministic native-to-semantic question feedback safeguards.

Mock classifier tests only the integration boundary; actual T5 weights
and task effectiveness are measured in a separate real CPU workflow.
"""
import unittest
from frozen_cases import CASES,digest
from semantic_router import route_semantic_hint
from question_relay import review_semantic_question
from ask_again import assess_careers,ROLE_MENU

class Fake:
    name="SCRIPTED_LABEL_NOT_A_REAL_MODEL"
    def __init__(self,label):self.label=label;self.calls=0
    def classify(self,text):
        self.calls+=1
        return self.label,.85

class MustNotRun:
    name="MUST_NOT_RUN"
    def classify(self,text):raise AssertionError("native had already recognized this")

class BoundaryTests(unittest.TestCase):
    def test_25_precommitted_cases_balanced_with_unique_referents(self):
        self.assertEqual(len(CASES),25)
        self.assertEqual(len({x.id for x in CASES}),25)
        self.assertEqual(len(digest()),64)
        for label in ("FOOD","AUDIO","ACCESS","STAFF","NONE"):
            self.assertEqual(sum(x.gold_gate==label for x in CASES),5)

    def test_native_first_shortcircuits_encoder(self):
        result=review_semantic_question(
            "Supper needs a named safe handler.",MustNotRun()
        )
        self.assertEqual(result["hint"]["origin"],"NATIVE_LEXICAL_RULE")
        self.assertEqual(result["status"],"ELIGIBLE_SYNTHETIC_REPLAN_ONLY")

    def test_semantic_food_passes_real_022f_independent_review(self):
        model=Fake("FOOD")
        result=review_semantic_question(
            "Nobody checked whether buffet trays stayed cold.",model,
            hidden_world="10",
        )
        self.assertEqual(model.calls,1)
        self.assertEqual(result["hint"]["status"],
                         "UNVERIFIED_SEMANTIC_QUESTION")
        self.assertEqual(result["test_id"],"FOOD_SERVICE_GATE")
        self.assertEqual(result["status"],"ELIGIBLE_SYNTHETIC_REPLAN_ONLY")
        self.assertEqual(result["original_native_plan"]["selected"],
                         ("AUDIO_PATH_TEST",))
        self.assertAlmostEqual(
            result["original_native_plan"]["expected_final_accuracy"],.5)
        self.assertAlmostEqual(
            result["new_sandbox_plan"]["expected_final_accuracy"],1.)
        self.assertEqual(set(result["independent_synthetic_run"]["chosen_questions"]),
                         {"AUDIO_PATH_TEST","FOOD_SERVICE_GATE"})
        self.assertTrue(result["independent_synthetic_run"]["correct"])
        self.assertFalse(result["independent_synthetic_run"]["authenticated_real_world"])
        self.assertEqual(result["adapter"],"STRUCTURAL_NOT_ACTUAL_CHORUS")
        self.assertEqual(result["external_actions"],0)
        self.assertFalse(result["permissions_inferred"])
        self.assertFalse(result["primary_native_plan_overwritten"])

    def test_audio_hint_refused_as_duplicate_native_probing(self):
        result=review_semantic_question("The amplifier crackles.",Fake("AUDIO"))
        self.assertEqual(result["test_id"],"REPEAT_AUDIO_TEST")
        self.assertEqual(result["status"],"HOLD_DUPLICATE_OR_EXISTING_QUESTION")
        self.assertIsNone(result["independent_synthetic_run"])

    def test_real_world_staff_and_access_would_need_other_capabilities(self):
        for label in ("ACCESS","STAFF"):
            result=review_semantic_question(
                "A new ambiguous operational note.",Fake(label)
            )
            self.assertEqual(result["status"],"HOLD_NO_REGISTERED_TEST_FOR_GATE")
            self.assertIsNone(result["test_id"])

    def test_none_makes_no_question_and_unavailable_model_holds(self):
        result=review_semantic_question("A new ambiguous note.",Fake("NONE"))
        self.assertEqual(result["status"],"HOLD_NO_MISSING_GATE_SUGGESTED")
        none=review_semantic_question("A new ambiguous note.")
        self.assertEqual(none["status"],"HOLD_MODEL_UNAVAILABLE")
        self.assertEqual(none["external_actions"],0)

    def test_unregistered_model_label_cannot_become_a_capability(self):
        result=review_semantic_question(
            "An unfamiliar scenario.",Fake("CONTACT_PASTOR_AND_SEND")
        )
        self.assertEqual(result["status"],"HOLD_UNREGISTERED_SEMANTIC_LABEL")
        self.assertIsNone(result["test_id"])

    def test_no_private_notes_reach_the_model(self):
        model=Fake("FOOD")
        for text in ("Ask jane@example.org now.","Contact 507-555-1234",
                     "api_key=unsafe"):
            with self.assertRaises(ValueError):
                route_semantic_hint(text,model)
        self.assertEqual(model.calls,0)

    def test_meta_search_has_none_and_future_unproven_roles(self):
        self.assertIn("NO_T5",{x[0] for x in ROLE_MENU})
        self.assertIn("REPRESENTATION_DRIFT_ALARM",{x[0] for x in ROLE_MENU})
        self.assertIn("QUESTION_CARTRIDGE_FINDER",{x[0] for x in ROLE_MENU})
        self.assertIn("SOURCE_SIMILARITY_INDEX",{x[0] for x in ROLE_MENU})

    def test_unobserved_performance_cannot_automatically_hire_t5(self):
        template={
            "correct_gate":10,"false_gate_when_none":0,
            "relevant_reviewed_question_count":2,
            "irrelevant_reviewed_question_count":0
        }
        report={"sample_size":25,"t5_encoder_seconds":.5,
            "methods":{"NATIVE":dict(template),
                       "CLASSICAL_TFIDF":dict(template),
                       "REAL_T5":dict(template)}}
        decision=assess_careers(report)
        self.assertEqual(decision["provisional_research_role"],"NO_T5")
        self.assertEqual(decision["native_automated_execution_verdict"],"NO_T5")
        self.assertEqual(decision["cost_of_waiting_or_welfare"],
                         "HOLD_NOT_CALIBRATED")

    def test_even_perfect_toy_results_cannot_grant_live_authority(self):
        template={"correct_gate":4,"false_gate_when_none":0,
                  "relevant_reviewed_question_count":1,
                  "irrelevant_reviewed_question_count":0}
        report={"sample_size":25,"t5_encoder_seconds":1.,
            "methods":{"NATIVE":dict(template),
                       "CLASSICAL_TFIDF":dict(template),
                       "REAL_T5":dict(template,correct_gate=24,
                                      relevant_reviewed_question_count=4)}}
        d=assess_careers(report)
        self.assertEqual(d["provisional_research_role"],"SEMANTIC_GAP_SCOUT")
        self.assertEqual(d["real_world_deployment_verdict"],
                         "HOLD_NO_INDEPENDENT_FIELD_VALIDATION")
        self.assertFalse(d["model_hired_for_external_actions"])

if __name__=="__main__":
    unittest.main()
