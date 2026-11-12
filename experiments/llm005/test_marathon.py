"""Synthetic 879+ serial action marathon falsifiers."""
import copy,json,unittest
from unittest.mock import patch
from marathon import Marathon,GROUPS,MIN_ACTIONS,MIN_GATES,SEGMENTS,INTERLINKS,ACTION_CAP,experiment
from odyssey import digest,POLICIES

class MarathonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=Marathon(GROUPS[0],"hypermap_voi")
        cls.summary=cls.m.execute()
    def test_01_219_actions_per_stage_exact_minimum(self):
        self.assertEqual(MIN_ACTIONS,219*4+3)
        self.assertEqual(MIN_ACTIONS,879)
    def test_02_384_distinct_decision_gates(self):
        self.assertEqual(MIN_GATES,384)
    def test_03_completed_marathon_is_genuinely_long(self):
        s=self.summary
        self.assertTrue(s["completed"])
        self.assertGreaterEqual(s["actual_serial_actions"],MIN_ACTIONS)
        self.assertEqual(s["completed_decision_gates"],384)
    def test_04_no_segment_skips_or_false_completion(self):
        s=self.summary
        self.assertEqual(s["completed_subchains"],4)
        self.assertEqual(s["total_required_subchains"],4)
        self.assertEqual(len(self.m.children),4)
        self.assertTrue(all(c["summary"]["completed"] for c in self.m.children))
    def test_05_exactly_three_mandatory_chain_handoffs(self):
        s=self.summary
        self.assertEqual(s["mandatory_handoffs_completed"],3)
        self.assertEqual(len([e for e in self.m.events if e["kind"]=="mandatory_handoff"]),3)
    def test_06_48_independent_authored_owner_coordinates(self):
        self.assertEqual(self.summary["distinct_source_owner_seeds"],48)
        self.assertEqual(len(set(x for c in self.m.children for x in c["distinct_source_owners"])),48)
    def test_07_all_96_audits_and_12_relays_passed(self):
        self.assertEqual(self.summary["audits"],96)
        self.assertEqual(self.summary["relays"],12)
    def test_08_first_global_record_is_child_action_not_handoff(self):
        self.assertEqual(self.m.events[0]["kind"],"odyssey_action")
        self.assertEqual(self.m.events[0]["segment"],0)
        self.assertEqual(self.m.events[0]["payload"]["child_action"],1)
    def test_09_every_following_handoff_starts_after_terminal(self):
        for e in [x for x in self.m.events if x["kind"]=="mandatory_handoff"]:
            p=e["payload"]
            c=self.m.children[e["segment"]]
            self.assertEqual(p["verified_previous_segment_terminal_digest"],c["last_action_digest"])
            self.assertEqual(p["previous_stage_global_hash"],c["segment_terminal_global_hash"])
            self.assertEqual(p["next_registered_seed"],self.m.seeds[e["segment"]+1])
    def test_10_hash_chains_every_900ish_element(self):
        prev="0"*64
        for i,e in enumerate(self.m.events,1):
            self.assertEqual(e["index"],i)
            self.assertEqual(e["prior_hash"],prev)
            self.assertEqual(e["hash"],digest({k:v for k,v in e.items() if k!="hash"}))
            prev=e["hash"]
        self.assertEqual(prev,self.summary["global_final_digest"])
    def test_11_each_child_contains_source_checked_correct_commitment(self):
        self.assertEqual(self.summary["verified_commitments"],384)
        for c in self.m.children:
            self.assertEqual(c["summary"]["metrics"]["correct_commits"],96)
            self.assertEqual(c["summary"]["metrics"]["surveys"],96)
    def test_12_replaying_exact_scenario_and_policy_is_deterministic(self):
        again=Marathon(GROUPS[0],"hypermap_voi")
        other=again.execute()
        self.assertEqual(other["global_final_digest"],self.summary["global_final_digest"])
        self.assertEqual(other["actual_serial_actions"],self.summary["actual_serial_actions"])
    def test_13_different_registered_scenarios_change_trace_identity(self):
        b=Marathon(GROUPS[1],"hypermap_voi")
        x=b.execute()
        self.assertNotEqual(x["global_final_digest"],self.summary["global_final_digest"])
    def test_14_invalid_group_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"BAD_REGISTERED_GROUP"):
            Marathon((8001,8001,8001,8001))
    def test_15_invalid_policy_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"BAD_POLICY"):
            Marathon(GROUPS[0],"make_up_truth")
    def test_16_global_budget_cannot_silently_grant_completion(self):
        with patch("marathon.ACTION_CAP",80):
            m=Marathon(GROUPS[0],"hypermap_voi")
            x=m.execute()
        self.assertEqual(x["state"],"GLOBAL_BUDGET_EXHAUSTED")
        self.assertFalse(x["completed"])
        self.assertEqual(x["mandatory_handoffs_completed"],0)
        self.assertEqual(x["actual_serial_actions"],80)
    def test_17_no_hidden_owner_program_exported(self):
        p=self.m.public_record()
        self.assertTrue(p["hidden_owner_truth_excluded"])
        self.assertFalse(p["external_actions"])
        self.assertNotIn('"_truth":',json.dumps(p))
        self.assertNotIn('"owner_program_index":',json.dumps(p))
    def test_18_copy_mutation_does_not_alter_owned_trace(self):
        obj=self.m.public_record()
        obj["global_events"][0]["payload"]["child_meta"]["x"]=[9,9,9]
        self.assertNotEqual(obj["global_events"][0],self.m.events[0])
    def test_19_same_child_different_segments_remain_serialized(self):
        ids=[(e["segment"],e["payload"]["child_action"]) for e in self.m.events
            if e["kind"]=="odyssey_action"]
        self.assertEqual(ids[0],(0,1))
        self.assertEqual(ids[-1][0],3)
        self.assertTrue(all(i[0]<=j[0] for i,j in zip(ids,ids[1:])))
    def test_20_two_group_four_policy_survey_has_correct_shape(self):
        study=experiment(groups=GROUPS[:2])
        self.assertEqual(len(study["arms"]),len(POLICIES))
        self.assertEqual(study["sequential_minimum"],879)
        self.assertEqual(study["required_decision_gates"],384)
        self.assertTrue(all(a["marathons"]==2 for a in study["arms"]))

if __name__=="__main__":unittest.main()
