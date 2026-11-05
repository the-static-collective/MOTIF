"""Falsification-oriented tests for WAKE SIGNAL 001."""
import json
from pathlib import Path
import tempfile
import unittest
from wake import ARMS, Hold, make_plan, read_plan, read_events, replay, record, report


def plan(count=100, verified=True, seed=9):
    return make_plan("Fellowship table", "A bounded hypothetical setup opportunity.",
        {"small": "Set one chair.", "creative": "Suggest a welcoming change.",
         "autonomous": "Offer to steward one 10-minute setup task."},
        count=count, seed=seed, verified=verified)


class WakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.planfile = Path(self.temp.name) / "plan.json"
        self.events = Path(self.temp.name) / "events.jsonl"
        self.p = plan()
        self.planfile.write_text(json.dumps(self.p), encoding="utf-8")
        self.slot = self.p["assignments"][0]["slot"]

    def add(self, event, **kwargs):
        return record(self.planfile, self.events, self.slot, event, **kwargs)

    def test_100_balanced_reproducible_and_no_automatic_send(self):
        self.assertEqual(self.p, plan())
        self.assertEqual(sorted([sum(x["arm"] == a for x in self.p["assignments"])
                                 for a in ARMS]), [33, 33, 34])
        self.assertEqual(len(set(x["slot"] for x in self.p["assignments"])), 100)
        for invitation in self.p["assignments"]:
            self.assertIn("free to decline or ignore", invitation["message"])
            self.assertNotIn("recipient_email", invitation)

    def test_different_seed_reassigns(self):
        self.assertNotEqual([x["arm"] for x in plan(seed=1)["assignments"]],
                            [x["arm"] for x in plan(seed=2)["assignments"]])

    def test_empty_report_means_unknown_not_afk(self):
        summary = report(read_plan(self.planfile), [])
        self.assertIsNone(summary["results"][ARMS[0]]["action_per_offered_descriptive"])
        self.assertFalse(summary["offerings_complete"])
        self.assertIn("Missing replies are unknown", summary["inference"])

    def test_refuses_contact_without_permission(self):
        with self.assertRaises(Hold):
            self.add("offered")
        self.assertFalse(self.events.exists())

    def test_refuses_to_offer_draft_as_real(self):
        self.planfile.write_text(json.dumps(plan(verified=False)), encoding="utf-8")
        with self.assertRaises(Hold):
            self.add("offered", consent=True)

    def test_refuses_unobserved_action(self):
        self.add("offered", consent=True)
        with self.assertRaises(Hold):
            self.add("action", attested=True, receipt="R001")

    def test_requires_attestation_and_receipt(self):
        self.add("offered", consent=True)
        self.add("replied")
        for kw in ({}, {"attested": True}, {"attested": True, "receipt": "John Smith"}):
            with self.assertRaises(Hold):
                self.add("action", **kw)
        self.add("action", attested=True, receipt="R001")
        self.add("novel_action", attested=True, receipt="R002")
        out = report(self.p, read_events(self.events))
        arm = self.p["assignments"][0]["arm"]
        self.assertEqual(out["results"][arm]["operator_attested_actions"], 1)
        self.assertEqual(out["results"][arm]["operator_attested_unplanned_actions"], 1)

    def test_optout_terminal_and_not_counted_as_failure(self):
        self.add("opted_out")
        with self.assertRaises(Hold):
            self.add("offered", consent=True)
        self.assertEqual(len(read_events(self.events)), 1)

    def test_decline_blocks_new_action(self):
        self.add("offered", consent=True)
        self.add("declined")
        with self.assertRaises(Hold):
            self.add("replied")

    def test_duplicate_event_held(self):
        self.add("offered", consent=True)
        with self.assertRaises(Hold):
            self.add("offered", consent=True)

    def test_tampered_plan_is_held(self):
        tampered = json.loads(self.planfile.read_text())
        tampered["assignments"][0]["arm"] = "autonomous" if tampered["assignments"][0]["arm"] != "autonomous" else "small"
        self.planfile.write_text(json.dumps(tampered))
        with self.assertRaises(Hold):
            read_plan(self.planfile)

    def test_corrupted_event_history_held(self):
        self.add("offered", consent=True)
        self.events.write_text(self.events.read_text() + "{incomplete\n")
        with self.assertRaises(Hold):
            report(self.p, read_events(self.events))

    def test_cross_study_event_held(self):
        self.add("offered", consent=True)
        other = plan(seed=44)
        with self.assertRaises(Hold):
            replay(other, read_events(self.events))

    def test_unverified_event_cannot_carry_receipt(self):
        self.add("offered", consent=True)
        with self.assertRaises(Hold):
            self.add("replied", attested=True, receipt="R001")

    def test_invalid_count_held(self):
        for c in (0, 1001):
            with self.assertRaises(Hold):
                plan(count=c)

    def test_no_person_level_scoring(self):
        self.add("offered", consent=True)
        r = report(self.p, read_events(self.events))
        self.assertEqual(set(r), {"study_id", "protocol", "results",
                                  "offerings_complete", "inference", "external_delivery"})
        self.assertNotIn("AFK", json.dumps(r))


if __name__ == "__main__":
    unittest.main()
