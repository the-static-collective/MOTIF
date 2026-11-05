import json
import unittest
from dataclasses import replace

from fixtures import DOGRAM_COMMIT, specimens, check_path
from pupil import HOLD, predict, verify_native, select_method, validate, digest, graph_input
from review import Receiver, objection_experiment
from objection import Inquiry, decide, check_certificate


def fake_local_receipt(specimen):
    """Deliberate local TEST DOUBLE, never called or claimed as native Dogram."""
    graph = specimen["inputs"]["graph"]
    edges = [tuple(e) for e in graph["edges"]]
    target = specimen["inputs"]["target"]
    removal = (target["source"], target["target"])
    before = check_path(graph["nodes"], edges)
    after = check_path(graph["nodes"], [e for e in edges if e != removal])
    return {
        "schema": "dogram.receipt/v0",
        "specimen_id": specimen["specimen_id"],
        "operator": "ablate", "operator_version": 1,
        "status": "OK", "input_digest": "sha256:" + digest(specimen),
        "consumed_inputs": ["inputs.graph","inputs.requested_targets","inputs.target"],
        "result": {"requested_targets": [{
            "source": "S", "target": "T",
            "reachable_before": before, "reachable_after": after,
        }]},
    }


def mock_rows(split):
    return [(sp, verify_native(sp, fake_local_receipt(sp)), fake_local_receipt(sp))
            for sp in specimens(split)]


class ForeignTeacherTest(unittest.TestCase):
    def test_balanced_disjoint_worlds(self):
        train, hold = specimens("train"), specimens("withheld")
        self.assertEqual((len(train), len(hold)), (12, 18))
        self.assertEqual({len(s["inputs"]["graph"]["nodes"]) for s in train}, {5})
        self.assertEqual({len(s["inputs"]["graph"]["nodes"]) for s in hold}, {6})
        self.assertTrue(set(x["specimen_id"] for x in train).isdisjoint(
            {x["specimen_id"] for x in hold}))
        for split in (train, hold):
            labels = [fake_local_receipt(s)["result"]["requested_targets"][0] for s in split]
            self.assertEqual(sum(not r["reachable_before"] for r in labels), len(split) // 3)
            self.assertEqual(sum(r["reachable_before"] and not r["reachable_after"]
                                 for r in labels), len(split) // 3)
            self.assertEqual(sum(r["reachable_after"] for r in labels), len(split) // 3)

    def test_instrument_selection_from_observations_not_teacher_import(self):
        raw = select_method(mock_rows("train"))
        c = validate(raw)
        self.assertEqual(c["learned_method"], "RECHECK_GRAPH_REACHABILITY")
        self.assertFalse(c["external_execution"])
        self.assertEqual(c["source_revision"], DOGRAM_COMMIT)

    def test_heldout_and_classical_control(self):
        rec = Receiver(select_method(mock_rows("train")), DOGRAM_COMMIT)
        with self.assertRaises(HOLD):
            rec.suggest(specimens("withheld")[0])
        review = rec.preview(mock_rows("withheld"))
        self.assertEqual(review["learner_correct"], 18)
        self.assertEqual(review["full_classical_correct"], 18)
        self.assertEqual(review["always_breaks_correct"], 12)
        self.assertEqual(review["status_quo_correct"], 12)
        with self.assertRaises(HOLD):
            rec.admit("WRONG_PERMISSION", review["review_digest"])
        with self.assertRaises(HOLD):
            rec.admit("ADMIT_READ_ONLY", "stale")
        rec.admit("ADMIT_READ_ONLY", review["review_digest"])
        self.assertFalse(rec.suggest(specimens("withheld")[0])["externally_executed"])

    def test_receipt_tamper_and_rehash_mislabel(self):
        sp = specimens("train")[0]
        actual = fake_local_receipt(sp)
        modified = json.loads(json.dumps(actual))
        modified["result"]["requested_targets"][0]["reachable_after"] ^= True
        # Changed teacher label still passes a content digest check if the
        # adversary controls both data and digest. Source checkout/CI is required
        # for provenance; unit tests don't establish origin authentication.
        self.assertNotEqual(actual["result"], modified["result"])
        with self.assertRaises(HOLD):
            verify_native(dict(sp, specimen_id="attacker"), actual)
        with self.assertRaises(HOLD):
            verify_native(sp, dict(actual, input_digest="sha256:bad"))
        with self.assertRaises(HOLD):
            verify_native(sp, dict(actual, status="REFUSE"))
        with self.assertRaises(HOLD):
            verify_native(sp, dict(actual, operator="reach"))

    def test_unrecognized_graph_or_execution_method_refused(self):
        sp = specimens("train")[0]
        with self.assertRaises(HOLD):
            predict("RUN_SHELL", sp)
        changed = json.loads(json.dumps(sp))
        changed["inputs"]["graph"]["edges"].append(changed["inputs"]["graph"]["edges"][0])
        with self.assertRaises(HOLD):
            graph_input(changed)
        with self.assertRaises(HOLD):
            select_method(mock_rows("train")[:-1])

    def test_rehash_no_expanded_authority(self):
        obj = validate(select_method(mock_rows("train")))
        obj["real_world_authority"] = True
        obj["checksum_sha256"] = digest({k:v for k,v in obj.items()
                                         if k != "checksum_sha256"})
        with self.assertRaises(HOLD):
            validate(json.dumps(obj))
        obj = validate(select_method(mock_rows("train")))
        obj["learned_method"] = "SEND_EMAIL"
        obj["checksum_sha256"] = digest({k:v for k,v in obj.items()
                                         if k != "checksum_sha256"})
        with self.assertRaises(HOLD):
            validate(json.dumps(obj))

    def test_source_mismatch_and_repeated_review_hold(self):
        with self.assertRaises(HOLD):
            Receiver(select_method(mock_rows("train")), "different")
        rec = Receiver(select_method(mock_rows("train")), DOGRAM_COMMIT)
        bad = mock_rows("withheld")
        bad[0] = bad[1]
        with self.assertRaises(HOLD):
            rec.preview(bad)


class ObjectionTest(unittest.TestCase):
    def test_closed_world_positive_path_certificate(self):
        q = Inquiry(("S","A","T"), (("S","A"),("A","T"),("S","T")),
                    (("S","A","PRESENT","s1"),("A","T","PRESENT","s2")),
                    ("S","T"), True)
        result = decide(q)
        self.assertEqual(result["status"], "PROVED_REACHABLE")
        self.assertTrue(check_certificate(q, result))
        result["certificate"]["nodes"] = ["S","T"]
        self.assertFalse(check_certificate(q, result))

    def test_closed_world_negative_cut_certificate(self):
        q = Inquiry(("S","A","T"), (("S","A"),("A","T"),("S","T")),
                    (("S","A","PRESENT","s1"),("A","T","ABSENT","s2")),
                    ("S","T"), True)
        result = decide(q)
        self.assertEqual(result["status"], "PROVED_UNREACHABLE")
        self.assertTrue(check_certificate(q, result))
        result["certificate"]["reachable_partition"].append("T")
        self.assertFalse(check_certificate(q, result))

    def test_open_world_never_converts_absence_into_false(self):
        q = Inquiry(("S","A","T"), (("S","A"),("A","T"),("S","T")),
                    (("S","A","PRESENT","s1"),("A","T","ABSENT","s2")),
                    ("S","T"), False)
        self.assertEqual(decide(q)["status"], "HOLD_OPEN_WORLD")

    def test_conflicting_claims_do_not_entail_everything(self):
        q = Inquiry(("S","A","T"), (("S","A"),("A","T"),("S","T")),
                    (("S","A","PRESENT","w1"), ("A","T","PRESENT","w2"),
                     ("A","T","ABSENT","w3")),
                    ("S","T"), True)
        result = decide(q, false_negative_cost=8, false_positive_cost=3, question_cost=.1)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["conflicts_preserved"], [["A","T"]])
        self.assertEqual(result["omission_analysis"]["recommended_question"]["edge"],
                         ["A","T"])
        self.assertGreater(result["omission_analysis"]["cost_of_omission"], 0)
        self.assertEqual(result["omission_analysis"]["status"], "QUESTION_PROPOSAL")

    def test_witness_loss_after_deletion_and_cost_of_not_asking(self):
        obj = objection_experiment()
        self.assertEqual(obj["query"]["status"], "UNKNOWN")
        self.assertEqual(obj["query"]["omission_analysis"]["recommended_question"]["edge"],
                         ["A","T"])
        self.assertFalse(obj["human_action_taken"])

    def test_question_cost_can_make_nonaction_rational(self):
        q = Inquiry(("S","A","T"), (("S","A"),("A","T"),("S","T")),
                    (("S","A","PRESENT","s1"),), ("S","T"), True)
        self.assertEqual(decide(q, question_cost=100)["omission_analysis"]["status"],
                         "HOLD_NO_POSITIVE_QUERY")

    def test_bad_claims_and_nonfinite_cost_hold(self):
        with self.assertRaises(HOLD):
            Inquiry(("S","T"), (("S","T"),), (("X","T","PRESENT","s1"),), ("S","T"))
        q = Inquiry(("S","T"), (("S","T"),), (), ("S","T"), True)
        with self.assertRaises(HOLD):
            decide(q, question_cost=float("nan"))


if __name__ == "__main__":
    unittest.main()
