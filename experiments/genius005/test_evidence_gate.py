"""GENIUS-005: evidence-projection contract and research-only revision gate."""
import json
import unittest

from evidence_gate import Signal, propose_revision


def obs(prefix: str, count: int, value: bool, *, shared=True, owner="nodeA"):
    return tuple(Signal(owner, f"receipt:{prefix}:{i}", value, shared,
                        "DO_NOT_PUBLISH_THIS_NOTE") for i in range(count))


class TestEvidenceGate(unittest.TestCase):
    def test_exact_public_window_gives_conditional_proposal_not_action(self):
        r = propose_revision(
            source_node="nodeA", reference=obs("baseline", 40, False),
            future=obs("future", 36, True),
            fixed_sampling_plan_attested=True,
        )
        self.assertEqual(r["status"], "PROPOSE_REVISION_CONDITIONALLY")
        self.assertEqual(r["first_exact_alarm_public_index"], 24)
        self.assertLess(r["exact_p_value_at_alarm"], r["per_test_threshold"])
        self.assertEqual(len(r["source_owned_supporting_window_receipts"]), 24)
        self.assertEqual(len(r["source_owned_reference_receipts"]), 40)
        self.assertFalse(r["can_auto_revise"])
        self.assertTrue(r["no_external_action"])
        self.assertNotIn("DO_NOT_PUBLISH_THIS_NOTE", json.dumps(r))

    def test_no_alarm_is_not_a_proof_of_unchanging_preferences(self):
        reference = obs("baseline", 40, False)
        future = obs("future", 40, False)
        r = propose_revision(
            source_node="nodeA", reference=reference, future=future,
            fixed_sampling_plan_attested=True)
        self.assertEqual(r["status"], "RETAIN_PROVISIONALLY_NO_REJECTED_NULL")
        self.assertIsNone(r["exact_p_value_at_alarm"])
        self.assertFalse(r["can_auto_revise"])

    def test_withheld_data_stays_invisible_even_with_opposite_values(self):
        reference = obs("baseline", 40, False)
        public = obs("public", 18, False)
        withheld = obs("private", 28, True, shared=False)
        r = propose_revision(
            source_node="nodeA", reference=reference,
            future=public + withheld, fixed_sampling_plan_attested=True)
        self.assertEqual(r["status"], "HOLD_NOT_ENOUGH_MONITORING")
        self.assertEqual(r["public_future_count"], 18)
        self.assertEqual(r["withheld_count_only"], 28)
        self.assertNotIn("receipt:private:", json.dumps(r))
        self.assertNotIn("DO_NOT_PUBLISH_THIS_NOTE", json.dumps(r))

    def test_unverified_sampling_holds_even_if_distribution_changes(self):
        r = propose_revision(
            source_node="nodeA", reference=obs("baseline", 40, False),
            future=obs("future", 40, True), fixed_sampling_plan_attested=False)
        self.assertEqual(r["status"], "HOLD_UNVERIFIED_SAMPLING_PLAN")
        self.assertNotIn("source_owned_reference_receipts", r)

    def test_echo_replay_and_foreign_source_are_not_independent_evidence(self):
        reference = obs("baseline", 40, False)
        duplicate = obs("future", 30, True)
        repeated = duplicate + duplicate
        r = propose_revision(
            source_node="nodeA", reference=reference, future=repeated,
            fixed_sampling_plan_attested=True)
        self.assertEqual(r["status"], "HOLD_DUPLICATE_FUTURE_EVIDENCE")
        foreign = obs("future", 30, True, owner="foreign")
        f = propose_revision(
            source_node="nodeA", reference=reference, future=foreign,
            fixed_sampling_plan_attested=True)
        self.assertEqual(f["status"], "HOLD_FOREIGN_SOURCE")

    def test_invalid_reference_scope_holds(self):
        r = propose_revision(
            source_node="nodeA", reference=obs("baseline", 39, False),
            future=obs("future", 40, True), fixed_sampling_plan_attested=True)
        self.assertEqual(r["status"], "HOLD_INSUFFICIENT_REFERENCE")
        r = propose_revision(
            source_node="nodeA", reference=obs("baseline", 40, False, shared=False),
            future=obs("future", 40, True), fixed_sampling_plan_attested=True)
        self.assertEqual(r["status"], "HOLD_REFERENCE_SCOPE")


if __name__ == "__main__":
    unittest.main()
