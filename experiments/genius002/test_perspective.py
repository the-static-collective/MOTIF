"""GENIUS-002 falsifiers: disagreement, autonomy, abstention, source integrity.

All cases are invented; tests establish implementation behavior, not a
psychometric or real-world causal claim.
"""
import json
import unittest

from perspective import (
    Claim, Crosswalk, NodeState, PerspectiveGuess, Proposal, Vote,
    deliberate, demo, project_packet,
)


class TestPerspectiveWithoutErasure(unittest.TestCase):
    def test_majority_can_override_one_person_but_protocol_does_not(self):
        r = demo()
        self.assertEqual(r["unsafe_first_majority_control"], "a_rush")
        self.assertEqual(r["selected_option_id"], "b_shared")
        self.assertEqual(r["status"], "CANDIDATE_FOR_HUMAN_REVIEW")
        self.assertTrue(r["no_external_action_taken"])
        self.assertEqual(r["options"][0]["status"], "REFUSED_BY_STAKEHOLDER")
        self.assertEqual(r["options"][1]["status"], "ELIGIBLE_DRAFT_NOT_EXECUTED")
        self.assertEqual(r["options"][0]["public_responses"]["courier"]["response"], "NO")

    def test_perspective_model_checks_public_report_not_imagined_motives(self):
        r = demo()
        by_source = {x["from"]: x for x in r["perspective_checks"]}
        self.assertEqual(by_source["grower"]["status"], "CORRECTED_BY_TARGET")
        self.assertEqual(by_source["grower"]["target_self_report"], "NO")
        self.assertEqual(by_source["courier"]["status"], "MATCHED_SELF_REPORT")
        # A claim from one node is not silently reassigned to a second node.
        self.assertEqual(sorted(c["owner_id"] for c in r["source_bound_claim_ledger"]),
                         ["courier", "grower"])

    def test_matched_topic_preserves_explicit_disagreement(self):
        r = demo()
        c = r["contested_claims"]
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0]["status"], "CONTESTED_NOT_ADJUDICATED")
        self.assertEqual(c[0]["affirming_nodes"], ["grower"])
        self.assertEqual(c[0]["denying_nodes"], ["courier"])
        self.assertTrue(any("verify disputed" in q for q in r["questions_for_human_return"]))

    def test_private_claim_and_private_vote_never_enter_shared_packet(self):
        secret = "KEY_123_DO_NOT_LEAK"
        local = NodeState(
            "A",
            claims=(Claim("s", "A", "private", secret, "AFFIRM", "secret:ref", False),),
            votes=(Vote("x", "YES_TO_DRAFT", 3, reason=secret, shareable=False),),
            perspective_guesses=(PerspectiveGuess("B", "x", "NO", False),),
        )
        other = NodeState("B", votes=(Vote("x", "YES_TO_DRAFT", 2, shareable=True),))
        public = deliberate((local, other), (Proposal("x", "draft", ("A", "B")),))
        self.assertEqual(public["status"], "HOLD_NO_SHARED_JOINT_PLAN")
        self.assertEqual(public["options"][0]["status"], "HOLD_INCOMPLETE_CONSENT")
        self.assertEqual(public["options"][0]["public_responses"]["A"]["response"],
                         "NOT_SHARED")
        self.assertNotIn(secret, json.dumps(public))
        self.assertNotIn("secret:ref", json.dumps(public))
        self.assertEqual(project_packet(local)["claims"], [])

    def test_unreviewed_translation_must_not_collapse_distinct_terms(self):
        same = "This arrangement is free"
        a = NodeState("A", claims=(Claim("a", "A", "free", same, "AFFIRM",
                                        "synthetic:a", True),))
        b = NodeState("B", claims=(Claim("b", "B", "free", same, "DENY",
                                        "synthetic:b", True),))
        not_yet = (Crosswalk("A", "free", "no_cost", True),
                   Crosswalk("B", "free", "no_cost", False))
        r = deliberate((a, b), (), not_yet)
        self.assertEqual(r["contested_claims"], [])
        self.assertEqual(len(r["source_bound_claim_ledger"]), 2)
        self.assertEqual(r["source_bound_claim_ledger"][1]["translation_status"],
                         "UNMAPPED")
        self.assertTrue(any("B:free" in q for q in r["questions_for_human_return"]))

    def test_explicit_shared_no_cannot_be_outvoted(self):
        nodes = (
            NodeState("A", votes=(Vote("x", "YES_TO_DRAFT", 3, shareable=True),)),
            NodeState("B", votes=(Vote("x", "YES_TO_DRAFT", 3, shareable=True),)),
            NodeState("C", votes=(Vote("x", "NO", reason="I cannot", shareable=True),)),
        )
        r = deliberate(nodes, (Proposal("x", "No-go", ("A", "B", "C")),))
        self.assertIsNone(r["selected_option_id"])
        self.assertEqual(r["status"], "HOLD_NO_SHARED_JOINT_PLAN")
        self.assertEqual(r["unsafe_first_majority_control"], "x")

    def test_withheld_target_response_not_read_by_prediction(self):
        a = NodeState("A", perspective_guesses=(PerspectiveGuess("B", "x", "YES_TO_DRAFT", True),))
        b = NodeState("B", votes=(Vote("x", "NO", reason="SECRET_REASON", shareable=False),))
        r = deliberate((a, b), (Proposal("x", "experiment", ("A", "B")),))
        self.assertEqual(r["perspective_checks"][0]["status"],
                         "HOLD_NO_SHARED_TARGET_RESPONSE")
        self.assertNotIn("target_self_report", r["perspective_checks"][0])
        self.assertNotIn("SECRET_REASON", json.dumps(r))

    def test_claim_owner_and_multiple_votes_fail_fast(self):
        with self.assertRaises(ValueError):
            deliberate((NodeState("A", claims=(
                Claim("s", "B", "thing", "it is", "AFFIRM", "ref", True),)),), ())
        with self.assertRaises(ValueError):
            deliberate((NodeState("A", votes=(
                Vote("x", "YES_TO_DRAFT", 2, shareable=True),
                Vote("x", "NO", shareable=True))),),
                (Proposal("x", "test", ("A",)),))
        with self.assertRaises(ValueError):
            deliberate((NodeState("A", votes=(
                Vote("x", "YES_TO_DRAFT", utility=True, shareable=True),)),),
                (Proposal("x", "test", ("A",)),))

    def test_consented_draft_is_not_permission_to_execute(self):
        a = NodeState("A", votes=(Vote("x", "YES_TO_DRAFT", 1, shareable=True),))
        r = deliberate((a,), (Proposal("x", "draft only", ("A",)),))
        self.assertTrue(r["no_external_action_taken"])
        self.assertIn("draft only", r["consent_scope"])
        self.assertEqual(r["selected_option_id"], "x")

    def test_same_author_does_not_get_more_votes_with_repeated_claims(self):
        a = NodeState("A", claims=tuple(
            Claim(f"a{i}", "A", "issue", "Issue exists", "AFFIRM",
                  f"synthetic:a{i}", True) for i in range(5)))
        b = NodeState("B", claims=(Claim("b", "B", "issue", "Issue exists",
                                        "DENY", "synthetic:b", True),))
        r = deliberate((a, b), (), (
            Crosswalk("A", "issue", "issue", True),
            Crosswalk("B", "issue", "issue", True)))
        self.assertEqual(r["contested_claims"][0]["affirming_nodes"], ["A"])
        self.assertEqual(r["contested_claims"][0]["denying_nodes"], ["B"])


if __name__ == "__main__":
    unittest.main()
