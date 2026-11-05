import json
import unittest
from reason004 import (Inquiry, HOLD, assert_owner_source, OWNER_GIT_BLOB,
                       make, validate, Receiver, observe, digest)

def reachable():
    return Inquiry(("S","A","B","T"),
        (("S","A"),("A","T"),("S","B"),("B","T"),("S","T")),
        (("S","A","PRESENT","p1"),("A","T","PRESENT","p2"),
         ("S","B","PRESENT","p3"),("B","T","PRESENT","p4")),
        ("S","T"), True)

def unreachable():
    return Inquiry(("S","A","B","T"),
        (("S","A"),("A","T"),("S","B"),("B","T"),("S","T")),
        (("S","A","PRESENT","p1"),("A","T","ABSENT","p2"),
         ("S","B","ABSENT","p3"),("B","T","ABSENT","p4")),
        ("S","T"), True)

def unresolved():
    return Inquiry(("S","A","B","T"),
        (("S","B"),("S","A"),("A","T"),("B","T"),("S","T")),
        (("S","A","PRESENT","p1"),("B","T","ABSENT","p2")),
        ("S","T"), True)

class ObjectingTests(unittest.TestCase):
    def test_owner_source_is_pinned(self):
        self.assertEqual(assert_owner_source(), OWNER_GIT_BLOB)

    def test_true_claim_has_minimal_witness_disproof(self):
        c=validate(make(reachable()))
        self.assertEqual(c["conclusion"],"PROVED_REACHABLE")
        f=c["refutation_program"]
        self.assertEqual(f["kind"],"RETRACT_CONFIRMED_MIN_CUT")
        self.assertEqual(f["minimum_premise_retractions"],2)
        self.assertEqual(len(f["counterexample_program"]),2)
        self.assertFalse(f["proof_of_unreachability_after_retraction"])

    def test_false_claim_has_hypothetical_repair_path(self):
        c=validate(make(unreachable()))
        self.assertEqual(c["conclusion"],"PROVED_UNREACHABLE")
        f=c["refutation_program"]
        self.assertEqual(f["kind"],"REOPEN_BLOCKED_ROUTE")
        self.assertEqual(f["counterexample_program"]["minimum_unconfirmed_edges"],1)
        self.assertEqual(f["counterexample_program"]["premises_to_revise"],[["A","T"]])
        self.assertTrue(f["requires_source_owned_revision"])

    def test_unknown_asks_one_consequential_question_with_two_futures(self):
        c=validate(make(unresolved(), false_negative_cost=8,
                         false_positive_cost=3, question_cost=.1))
        self.assertEqual(c["conclusion"],"UNKNOWN")
        self.assertEqual(c["refutation_program"]["kind"],"OBSERVE_DISCRIMINATING_EDGE")
        self.assertEqual(c["refutation_program"]["edge"],["A","T"])
        self.assertEqual(c["hypothetical_futures"]["PRESENT"]["status"],"PROVED_REACHABLE")
        self.assertEqual(c["hypothetical_futures"]["ABSENT"]["status"],"PROVED_UNREACHABLE")
        self.assertFalse(c["hypothetical_futures"]["PRESENT"]["new_witness_is_real"])

    def test_open_world_does_not_equate_missing_with_false(self):
        q=unresolved()
        open_q=Inquiry(q.nodes,q.universe,q.claims,q.removed,False)
        self.assertEqual(validate(make(open_q))["conclusion"],"HOLD_OPEN_WORLD")
        self.assertEqual(validate(make(open_q))["refutation_program"]["kind"],
                         "ASK_FOR_SCOPE_CONTRACT")

    def test_conflict_preserved(self):
        q=unresolved()
        conflicting=Inquiry(q.nodes,q.universe,q.claims+
            (("A","T","PRESENT","pro"),("A","T","ABSENT","con")),
            q.removed,True)
        c=validate(make(conflicting,question_cost=.1))
        self.assertEqual(c["conclusion"],"UNKNOWN")
        self.assertEqual(c["refutation_program"]["kind"],"REQUEST_HUMAN_CONFLICT_REVIEW")
        with self.assertRaises(HOLD):
            observe(conflicting,("A","T"),"PRESENT","extra")

    def test_question_cost_can_stop(self):
        c=validate(make(unresolved(),question_cost=100))
        self.assertEqual(c["refutation_program"]["kind"],"HOLD_UNCERTAIN")
        self.assertIsNone(c["hypothetical_futures"])

    def test_new_witness_recomputes_without_automatic_external_action(self):
        result=observe(unresolved(),("A","T"),"PRESENT","independent-review-1")
        self.assertEqual(result["new_conclusion"],"PROVED_REACHABLE")
        self.assertFalse(result["external_observation_performed"])
        with self.assertRaises(HOLD):
            observe(unresolved(),("S","A"),"ABSENT","override")

    def test_altered_falsifier_or_scope_is_rejected_even_when_rehashed(self):
        for field in ("conclusion","refutation_program","inquiry"):
            c=json.loads(make(unresolved()))
            if field=="conclusion": c[field]="PROVED_REACHABLE"
            elif field=="refutation_program": c[field]["kind"]="IMPROPER"
            else: c[field]["closed_scope"]=False
            c["checksum_sha256"]=digest({k:v for k,v in c.items()
                                        if k!="checksum_sha256"})
            with self.subTest(field=field),self.assertRaises(HOLD):
                validate(json.dumps(c))

if __name__=="__main__":
    unittest.main()
