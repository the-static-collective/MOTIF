"""RING-013: evidence safeguards for action utility under ordinary ambiguity."""
from __future__ import annotations
from copy import deepcopy
import unittest

import scenario,value,freeze,trial,evidence_graph


class EvidenceOfActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen=freeze.search()
        cls.report=trial.run_frozen(cls.frozen)

    def test_record_contains_measured_benefit_and_measured_costs(self):
        graph=evidence_graph.build(self.frozen,self.report)
        self.assertEqual(graph["schema"],evidence_graph.SCHEMA)
        self.assertEqual(len(graph["hyperedges"]),2)
        gains=graph["hyperedges"][1]
        self.assertEqual(gains["total_cases"],60)
        self.assertEqual(gains["frontier_policy"]["cases"],60)
        self.assertIn("negative_value_cases_not_suppressed",gains)
        self.assertEqual(len(gains["heads"]),5)
        self.assertTrue(graph["positive_action_value_can_proceed_without_ambiguity_resolution"])
        self.assertFalse(graph["real_world_autonomous_execution_demonstrated"])
        self.assertEqual(graph["new_external_tool_permissions"],0)
        self.assertEqual(graph["authority"],"NONE")

    def test_changed_negative_case_tally_cannot_rehash_into_truth(self):
        mutated=deepcopy(self.report)
        mutated["test_packets"][1]["metrics"]["FRONTIER"][
            "negative_utility_cases"]+=1
        mutated["combined"]["FRONTIER"]["negative_utility_cases"]+=1
        mutated["receipt_sha256"]=value.digest({
            k:v for k,v in mutated.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"aggregate"):
            evidence_graph.build(self.frozen,mutated)

    def test_forged_nonlocal_action_denied_even_if_outcome_claim_favorable(self):
        mutated=deepcopy(self.report)
        step=next(row["value_trace"]["steps"][0] for pack in
                  mutated["test_packets"] for row in pack["case_witnesses"]
                  if row["value_trace"]["steps"])
        step["action"]="EXTERNAL_COMMIT"
        mutated["receipt_sha256"]=value.digest({
            k:v for k,v in mutated.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Unapproved"):
            evidence_graph.build(self.frozen,mutated)

    def test_simulated_human_question_is_never_real_user_interruption(self):
        graph=evidence_graph.build(self.frozen,self.report)
        self.assertEqual(graph["hyperedges"][1]["frontier_policy"][
            "real_user_interruptions"],0)
        self.assertEqual(graph["hyperedges"][1]["ask_before_act_control"][
            "real_user_interruptions"],0)

    def test_rehashed_policy_that_promotes_external_authority_is_refused(self):
        modified=deepcopy(self.frozen)
        modified["new_real_world_agent_authority"]="UNRESTRICTED"
        modified["receipt_sha256"]=value.digest({
            k:v for k,v in modified.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(trial.HOLD,"policy"):
            trial.verify_frozen(modified)


if __name__=="__main__":
    unittest.main()
