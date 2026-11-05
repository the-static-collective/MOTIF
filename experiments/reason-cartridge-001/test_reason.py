import json
import unittest
from reason import (Pupil, Correction, LocalReceiver, HOLD, SIGNALS,
                    digest, choose, validate)
from teacher_fixture import teach_pair, withheld_review, rote_case_baseline
from demo import run


def learned():
    pupil = Pupil()
    for index in range(10):
        probe = pupil.next_probe()
        if probe is None:
            break
        pupil.add(teach_pair(probe, index))
    return pupil


class ReasonCartridgesTest(unittest.TestCase):
    def test_active_questions_learn_priority_instead_of_teacher_source_code(self):
        p = learned()
        self.assertIsNone(p.next_probe())
        self.assertEqual(p.learned_order(), (
            "MISSING_AUTHORITY", "CONTRADICTION", "STALE_SOURCE",
            "LOOKUP_AVAILABLE", "PLAN_POSSIBLE"))
        self.assertLessEqual(len(p.corrections), 10)

    def test_unseen_multisignal_cases_generalize(self):
        r = LocalReceiver(learned().export())
        cases = withheld_review()
        self.assertTrue(all(len(active) >= 3 for active, _ in cases))
        result = r.preview(cases)
        self.assertEqual((result["correct"], result["errors"]), (len(cases), 0))
        self.assertLess(sum(rote_case_baseline(active) == expected
                            for active, expected in cases), len(cases))
        r.admit("ADMIT_READ_ONLY", result["review_digest"])
        self.assertEqual(r.suggest(SIGNALS)["method"], "HOLD_FOR_AUTHORITY")
        self.assertFalse(r.suggest(SIGNALS)["executed"])

    def test_not_learned_yet_holds_instead_of_guessing(self):
        p = Pupil()
        p.add(teach_pair(tuple(sorted(SIGNALS[:2])), 0))
        with self.assertRaises(HOLD):
            p.export()
        self.assertIsNotNone(p.next_probe())

    def test_unreviewed_receiver_stays_held(self):
        r = LocalReceiver(learned().export())
        with self.assertRaises(HOLD):
            r.suggest(SIGNALS)
        with self.assertRaises(HOLD):
            r.admit("ADMIT_READ_ONLY", "fabricated")
        result = r.preview(withheld_review())
        with self.assertRaises(HOLD):
            r.admit("DENY", result["review_digest"])
        with self.assertRaises(HOLD):
            r.admit("ADMIT_READ_ONLY", "stale")
        self.assertFalse(r.admitted)

    def test_source_contract_shift_holds(self):
        with self.assertRaises(HOLD):
            LocalReceiver(learned().export(), current_source_revision="v2")
        with self.assertRaises(HOLD):
            Correction("task", tuple(sorted(SIGNALS[:2])), SIGNALS[0],
                       SIGNALS[1], "evidence", source_revision="v2")

    def test_conflicting_teacher_cycle_holds(self):
        p = Pupil()
        a, b, c = SIGNALS[:3]
        p.add(Correction("ab", tuple(sorted((a, b))), b, a, "proof-ab"))
        p.add(Correction("bc", tuple(sorted((b, c))), c, b, "proof-bc"))
        with self.assertRaises(HOLD):
            p.add(Correction("ca", tuple(sorted((a, c))), a, c, "proof-ca"))
        self.assertEqual(len(p.corrections), 2)

    def test_injected_execution_and_unknown_signal_holds(self):
        obj = json.loads(learned().export())
        obj["execute_python"] = "untrusted_code"
        obj["checksum_sha256"] = digest({k: v for k, v in obj.items()
                                         if k != "checksum_sha256"})
        with self.assertRaises(HOLD):
            validate(json.dumps(obj))
        with self.assertRaises(HOLD):
            choose(json.loads(learned().export())["priority_program"], ["BUY_STUFF"])

    def test_rehashing_does_not_earn_trust_or_fake_a_test(self):
        obj = json.loads(learned().export())
        obj["priority_program"].reverse()
        obj["checksum_sha256"] = digest({k: v for k, v in obj.items()
                                         if k != "checksum_sha256"})
        r = LocalReceiver(json.dumps(obj))  # a checksum is NOT author authentication
        result = r.preview(withheld_review())
        self.assertGreater(result["errors"], 0)
        with self.assertRaises(HOLD):
            r.admit("ADMIT_READ_ONLY", result["review_digest"])

    def test_tamper_without_rehash_and_privilege_escalation_holds(self):
        obj = json.loads(learned().export())
        obj["priority_program"][0]["then"] = "SEND_PRIVATE_DATA"
        with self.assertRaises(HOLD):
            validate(json.dumps(obj))
        obj = json.loads(learned().export())
        obj["real_world_authority"] = True
        obj["checksum_sha256"] = digest({k: v for k, v in obj.items()
                                         if k != "checksum_sha256"})
        with self.assertRaises(HOLD):
            validate(json.dumps(obj))

    def test_duplicate_or_bogus_correction_holds(self):
        p = Pupil()
        a, b = tuple(sorted(SIGNALS[:2]))
        c = Correction("a1", (a, b), b, a, "proof")
        p.add(c)
        with self.assertRaises(HOLD):
            p.add(c)
        with self.assertRaises(HOLD):
            p.add(Correction("a2", (a, b), a, b, "proof2"))
        with self.assertRaises(HOLD):
            Correction("x", (a, a), a, b, "proof")

    def test_demo_receipt_truthful(self):
        receipt = run()
        self.assertTrue(receipt["receiver_admitted_read_only"])
        self.assertEqual(receipt["learned_correct"], receipt["heldout_cases"])
        self.assertEqual(receipt["full_knowledge_teacher_correct"], receipt["heldout_cases"])
        self.assertFalse(receipt["real_world_authority"])


if __name__ == "__main__":
    unittest.main()
