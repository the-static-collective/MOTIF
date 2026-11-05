"""POSTHOC audit tests: do not pretend a hindsight oracle is a policy."""
import copy
import unittest
from postmortem import ask_about_specialization_again

def example():
    rows=[]
    for i in range(50):
        rows.append({
            "id":f"T{i:02d}",
            "gold":"FOOD",
            "specialist_nodes":[{
                "role":role,"label":"FOOD" if i%2==0 else "AUDIO"
            } for role in ("SCOUT","SKEPTIC","CARTRIDGE_FINDER")],
            "methods":{"THREE_T5_2_OF_3":{"held_review_question":False}},
        })
    return {
        "cases":rows,
        "scores":{
            "SINGLE_T5_ANCHORED":{"correct_held_offers":16},
            "THREE_T5_2_OF_3":{"correct_held_offers":15},
            "SOURCE_ANCHOR_ONLY":{"correct_held_offers":31},
        },
    }
class Audit(unittest.TestCase):
    def test_no_data_means_hold(self):
        self.assertEqual(ask_about_specialization_again({})["status"],
                         "HOLD_POSTHOC_EVIDENCE_MISSING")
    def test_non_mutating_and_self_skeptical(self):
        data=example(); frozen=copy.deepcopy(data)
        x=ask_about_specialization_again(data)
        self.assertEqual(data,frozen)
        self.assertEqual(x["status"],"THREE_T5_VOTING_NOT_EARNED")
        self.assertEqual(x["quorum_gain_over_single_in_correct_held_offers"],-1)
        self.assertEqual(x["source_only_gain_over_quorum_in_correct_held_offers"],16)
        self.assertTrue(x["hindsight_oracle_is_not_an_action_policy"])
        self.assertEqual(x["model_authority"],"NONE")
        self.assertIn("NEW independently authored corpus",x["next_research_question"])
    def test_missing_specialist_not_silently_counted(self):
        x=example()
        x["cases"][0]["specialist_nodes"].pop()
        self.assertEqual(ask_about_specialization_again(x)["status"],
                         "HOLD_INCOMPLETE_SPECIALIST_RECORD")
    def test_native_bypass_not_falsely_counted_as_three_model_calls(self):
        x=example();x["cases"][0]["specialist_nodes"]=[]
        report=ask_about_specialization_again(x)
        self.assertEqual(report["all_heads_agreed_cases"],49)
if __name__=="__main__":
    unittest.main()
