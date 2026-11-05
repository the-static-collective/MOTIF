"""FIELD-001 hostile tests: matches are held reports, never verified history."""
import copy
from datetime import datetime
import unittest

from field_protocol import (
    FieldError, SCHEMA, candidate_pairs, example, summarize, validate,
)

AS_OF = "2026-11-04T18:00:00Z"


def event(kind, subject="pair:demo-offer:demo-need", id_="event-1"):
    return {
        "id":id_, "subject":subject, "kind":kind, "reporter":"Operator A",
        "source":"operator_heard_owner",
        "occurred_at":"2026-11-04T16:00:00Z",
        "recorded_at":"2026-11-04T17:00:00Z", "note":"",
    }


class FieldProtocolTests(unittest.TestCase):
    def setUp(self):
        self.log = example()

    def test_explicit_demo_is_a_synthetic_fixture_not_an_observation(self):
        summary = summarize(self.log, AS_OF)
        self.assertEqual(summary["eligible_pairs"], 1)
        self.assertEqual(summary["pairs"][0]["disposition"],
                         "HOLD_CONFIRM_DIRECTLY")
        self.assertFalse(summary["causal_effect_identified"])
        self.assertFalse(summary["authorship_verified"])
        self.assertEqual(len(summary["log_sha256_unsigned"]), 64)

    def test_prospectively_recorded_candidate_precedes_reports(self):
        first = event("candidate_proposed")
        first["source"] = "operator_generated"
        second = event("benefit_reported", id_="event-2")
        second["recorded_at"] = "2026-11-04T17:30:00Z"
        self.log["events"] = [first,second]
        report=summarize(self.log,AS_OF)
        self.assertEqual(report["prospective_proposals_recorded"],1)
        self.assertEqual(report["unresolved_proposals"],0)
        self.assertEqual(report["reported_outcomes"]["benefit_reports"],1)
        self.assertFalse(report["causal_effect_identified"])

    def test_prospective_proposal_without_followup_is_not_failure(self):
        proposed = event("candidate_proposed")
        proposed["source"] = "operator_generated"
        self.log["events"] = [proposed]
        report = summarize(self.log,AS_OF)
        self.assertEqual(report["prospective_proposals_recorded"],1)
        self.assertEqual(report["unresolved_proposals"],1)
        self.assertEqual(report["reported_outcomes"]["no_benefit_reports"],0)

    def test_no_postdicted_or_double_proposal(self):
        proposed = event("candidate_proposed")
        proposed["source"] = "operator_generated"
        self.log["events"] = [event("benefit_reported",id_="early"),proposed]
        with self.assertRaises(FieldError):
            validate(self.log)
        self.log["events"] = [proposed,event("candidate_proposed",id_="second")]
        self.log["events"][1]["source"]="operator_generated"
        with self.assertRaises(FieldError):
            validate(self.log)

    def test_proposal_provenance_is_operator_generated_only(self):
        proposed=event("candidate_proposed")
        self.log["events"]=[proposed]
        with self.assertRaises(FieldError):
            validate(self.log)
        proposed["source"]="operator_generated"
        validate(self.log)

    def test_no_permission_or_third_party_sharing(self):
        self.log["cards"][0]["share_ok"] = False
        self.assertEqual(candidate_pairs(self.log, AS_OF), [])
        self.log["cards"][0]["share_ok"] = True
        self.log["cards"][0]["origin"] = "third_party_unverified"
        with self.assertRaises(FieldError):
            validate(self.log)

    def test_expiry_and_future_created_are_not_active(self):
        self.assertEqual(candidate_pairs(self.log, "2026-11-05T15:00:00Z"), [])
        self.assertEqual(candidate_pairs(self.log, "2026-11-03T15:00:00Z"), [])

    def test_area_topic_and_alias_must_agree(self):
        for field, value in [("topic","tool"), ("area","another-town"),
                             ("alias","Demo A")]:
            fresh = copy.deepcopy(self.log)
            fresh["cards"][1][field] = value
            self.assertEqual(candidate_pairs(fresh, AS_OF), [])

    def test_no_names_locations_or_contact_required(self):
        for card in self.log["cards"]:
            self.assertNotIn("phone", card)
            self.assertNotIn("address", card)
            self.assertNotIn("email", card)
        self.assertEqual(len(validate(self.log)["cards"]), 2)

    def test_dual_yes_still_not_cryptographic_consent(self):
        self.log["events"] = [
            event("provider_yes_reported", id_="e1"),
            event("requester_yes_reported", id_="e2"),
        ]
        result = candidate_pairs(self.log, AS_OF)[0]
        self.assertEqual(result["disposition"], "DUAL_YES_REPORTED_NOT_VERIFIED")

    def test_outcome_is_reported_not_causal(self):
        self.log["events"] = [event("benefit_reported")]
        summary = summarize(self.log, AS_OF)
        self.assertEqual(summary["pairs"][0]["disposition"],
                         "BENEFIT_REPORTED_NOT_CAUSAL")
        self.assertEqual(summary["reported_outcomes"]["benefit_reports"], 1)
        self.assertFalse(summary["causal_effect_identified"])

    def test_contradictory_outcome_reports_remain_conflicting(self):
        self.log["events"] = [
            event("benefit_reported", id_="a"),
            event("no_benefit_reported", id_="b"),
        ]
        self.assertEqual(candidate_pairs(self.log, AS_OF)[0]["disposition"],
                         "CONFLICTING_OUTCOME_REPORTS")

    def test_no_answer_must_not_count_as_no_effect(self):
        self.log["events"] = [event("unknown_reported")]
        summary = summarize(self.log, AS_OF)
        self.assertEqual(summary["reported_outcomes"]["unknown_reports"], 1)
        self.assertEqual(summary["reported_outcomes"]["no_benefit_reports"], 0)

    def test_decline_closes_candidate_without_deleting_history(self):
        self.log["events"] = [event("requester_no_reported")]
        rows = candidate_pairs(self.log, AS_OF)
        self.assertEqual(rows[0]["disposition"], "CLOSED_DECLINED_REPORTED")
        self.assertEqual(len(self.log["events"]), 1)

    def test_append_only_withdrawal_blocks_future_matches(self):
        self.log["events"] = [
            event("card_withdrawn", "demo-offer", "withdrawal-1")
        ]
        self.assertEqual(candidate_pairs(self.log, AS_OF), [])
        self.assertEqual(len(self.log["cards"]), 2)

    def test_future_withdrawal_does_not_backdate(self):
        withdrawn = event("card_withdrawn", "demo-offer")
        withdrawn["occurred_at"] = "2026-11-05T13:00:00Z"
        withdrawn["recorded_at"] = "2026-11-05T14:00:00Z"
        self.log["events"] = [withdrawn]
        self.assertEqual(len(candidate_pairs(self.log, AS_OF)), 1)
        self.assertEqual(candidate_pairs(self.log, "2026-11-05T14:30:00Z"), [])

    def test_unknown_pair_and_card_rejected(self):
        self.log["events"] = [event("benefit_reported", "pair:other:fake")]
        with self.assertRaises(FieldError):
            validate(self.log)
        self.log["events"] = [event("card_withdrawn", "missing-card")]
        with self.assertRaises(FieldError):
            validate(self.log)

    def test_duplicate_ids_rejected(self):
        self.log["cards"].append(copy.deepcopy(self.log["cards"][0]))
        with self.assertRaises(FieldError):
            validate(self.log)
        self.log = example()
        self.log["events"] = [event("benefit_reported"),
                              event("no_benefit_reported")]
        with self.assertRaises(FieldError):
            validate(self.log)

    def test_no_fabricated_past_occurrence(self):
        e = event("unknown_reported")
        e["occurred_at"] = "2026-11-06T00:00:00Z"
        self.log["events"] = [e]
        with self.assertRaises(FieldError):
            validate(self.log)

    def test_unknown_fields_or_overlarge_notes_rejected(self):
        self.log["cards"][0]["unverified_contact"] = "+1"
        with self.assertRaises(FieldError):
            validate(self.log)
        self.log = example()
        self.log["cards"][0]["note"] = "x" * 361
        with self.assertRaises(FieldError):
            validate(self.log)

    def test_snapshot_hash_reproduces_and_mutations_change_it(self):
        s1 = summarize(self.log, AS_OF)
        s2 = summarize(copy.deepcopy(self.log), AS_OF)
        self.assertEqual(s1["log_sha256_unsigned"],s2["log_sha256_unsigned"])
        self.log["cards"][0]["note"] = "updated draft"
        self.assertNotEqual(s1["log_sha256_unsigned"],
                            summarize(self.log, AS_OF)["log_sha256_unsigned"])

    def test_input_log_is_not_modified(self):
        before = copy.deepcopy(self.log)
        summarize(self.log, AS_OF)
        self.assertEqual(self.log, before)

    def test_expiration_does_not_erase_past_report(self):
        self.log["events"] = [event("benefit_reported")]
        summary = summarize(self.log, "2026-11-06T18:00:00Z")
        self.assertEqual(summary["eligible_pairs"], 0)
        self.assertEqual(summary["reported_outcomes"]["benefit_reports"], 1)


if __name__ == "__main__":
    unittest.main()
