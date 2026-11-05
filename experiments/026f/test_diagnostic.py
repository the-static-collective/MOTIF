"""026F: retrospective meta-question is a review ticket, not self-training."""
import copy
import unittest
from diagnostic import inspect_semantic_link

def receipt():
    cases=[]
    for n in range(25):
        gold="NONE" if n==0 else "FOOD"
        label="FOOD" if n==0 else gold
        cases.append({
            "case":f"Q{n:02d}",
            "synthetic_gold":gold,
            "comparison":{"REAL_T5":{
                "gate":label,
                "native_review":"ELIGIBLE_SYNTHETIC_REPLAN_ONLY",
            }},
        })
    return {"sample_size":25,"cases":cases,
            "methods":{"REAL_T5":{"correct_gate":24},
                       "CLASSICAL_TFIDF":{"correct_gate":20}}}

class MetaTests(unittest.TestCase):
    def test_detect_incorrect_irrelevant_question_and_find_next_falsifier(self):
        data=receipt()
        before=copy.deepcopy(data)
        r=inspect_semantic_link(data)
        self.assertEqual(data,before)
        self.assertEqual(r["status"],"OPEN_IMPROVEMENT_TICKET")
        self.assertEqual(r["synthetic_irrelevant_reviewed_test_cases"],["Q00"])
        self.assertIn("relevance",r["question_for_next_planning_round"])
        self.assertFalse(r["new_field_capability_installed"])

    def test_no_witness_no_claim_to_new_capability(self):
        self.assertEqual(inspect_semantic_link({})["status"],
                         "HOLD_INCOMPLETE_EVIDENCE")
        data=receipt()
        data["cases"][0]["comparison"]["REAL_T5"]["native_review"]="HOLD"
        self.assertEqual(inspect_semantic_link(data)["status"],
                         "HOLD_NO_OBSERVED_IRRELEVANT_ADMISSIONS")

    def test_meta_question_never_rewrites_original_scores(self):
        data=receipt()
        a=inspect_semantic_link(data)
        self.assertTrue(a["original_results_immutable"])
        self.assertTrue(a["not_a_trained_or_autonomous_model"])
        self.assertEqual(a["recommended_current_operator_action"],
                         "KEEP_T5_AS_HELD_REVIEW_ONLY")

if __name__=="__main__":
    unittest.main()
