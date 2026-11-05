"""Native Dogram tests on intentionally synthetic report histories only."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from field_protocol import example
from field_dogram import calculate


def pair_log():
    log=example()
    extra=deepcopy(log["cards"])
    extra[0].update(id="other-offer",alias="Demo C",topic="repair")
    extra[1].update(id="other-need",alias="Demo D",topic="repair")
    log["cards"].extend(extra)
    first={
        "id":"p1","subject":"pair:demo-offer:demo-need",
        "kind":"candidate_proposed","reporter":"demo-operator",
        "source":"operator_generated",
        "occurred_at":"2026-11-04T16:00:00Z",
        "recorded_at":"2026-11-04T16:00:00Z","note":"",
    }
    second={
        "id":"p2","subject":"pair:demo-offer:demo-need",
        "kind":"benefit_reported","reporter":"demo-operator",
        "source":"operator_heard_owner",
        "occurred_at":"2026-11-04T16:20:00Z",
        "recorded_at":"2026-11-04T16:30:00Z","note":"",
    }
    third={
        "id":"p3","subject":"pair:other-offer:other-need",
        "kind":"benefit_reported","reporter":"demo-operator",
        "source":"third_party_unverified",
        "occurred_at":"2026-11-04T16:45:00Z",
        "recorded_at":"2026-11-04T17:00:00Z","note":"",
    }
    log["events"]=[first,second,third]
    return log


class DogramFieldTests(unittest.TestCase):
    def test_rejects_implicit_dogram_lookup(self):
        with self.assertRaises(ValueError):
            calculate(pair_log(), "/no/dogram/available/here")

    @unittest.skipUnless(os.getenv("DOGRAM_ROOT"),"Native Dogram root not supplied")
    def test_preserves_provenance_distinction_lost_by_yes_label(self):
        source=pair_log()
        before=deepcopy(source)
        r=calculate(source,os.environ["DOGRAM_ROOT"])
        self.assertEqual(r["schema"],"motif.field-dogram/v0")
        self.assertEqual(r["pair_count"],2)
        self.assertEqual(r["status"],"DECLARED_CALCULATION_ONLY")
        self.assertTrue(r["calculation"]["lawful_quotient"])
        self.assertEqual(len(r["calculation"]["lost_distinctions"]),1)
        self.assertFalse(r["verification_claimed"])
        self.assertFalse(r["causal_effect_identified"])
        self.assertEqual(source,before)

    @unittest.skipUnless(os.getenv("DOGRAM_ROOT"),"Native Dogram root not supplied")
    def test_single_pair_refuses_loss_inference(self):
        r=calculate(example(),os.environ["DOGRAM_ROOT"])
        self.assertEqual(r["status"],"INSUFFICIENT_COMPARABLE_PAIRS")
        self.assertIsNone(r["calculation"])


if __name__=="__main__":
    unittest.main()
