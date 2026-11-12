"""No real telemetry: deterministic synthetic bridge fixture tests."""
import unittest
from observer import UnsafeObservation
from webz_bridge import packet_from_aggregate
from observer import evaluate

def source():
    return {
        "schema": "posthog.one-thing.consented-funnel/v1",
        "query_ref": "fixture:future-optin-funnel",
        "window_start": "2026-11-05T00:00:00Z",
        "window_end": "2026-11-05T22:00:00Z",
        "exported_at": "2026-11-06T08:00:00Z",
        "entry_count": 100,
        "completed_count": 30,
        "source_reviewed": True,
        "consent_confirmed": True
    }

class BridgeTests(unittest.TestCase):
    def test_synthetic_aggregate_makes_review_only_receipt(self):
        packet=packet_from_aggregate(source(),expected_rate=0.7,minimum_n=10)
        self.assertEqual(packet["prediction"]["metric"],"self_report_preparation_rate")
        verdict=evaluate(packet,now="2026-11-06T09:00:00Z")
        self.assertEqual(verdict["status"],"REVIEW_DEPARTURE")
        self.assertFalse(verdict["boundary"]["field_outcome_verified"])
        self.assertFalse(verdict["boundary"]["permission_to_act"])
        self.assertEqual(verdict["sample_size"],100)

    def test_unreviewed_query_holds(self):
        s=source();s["source_reviewed"]=False
        p=packet_from_aggregate(s,expected_rate=0.7,minimum_n=10)
        self.assertEqual(evaluate(p,now="2026-11-06T09:00:00Z")["status"],"HOLD")

    def test_deny_explicit_consent_missing(self):
        s=source();s["consent_confirmed"]=False
        with self.assertRaises(UnsafeObservation):
            packet_from_aggregate(s,expected_rate=0.7,minimum_n=10)

    def test_deny_person_level_data_and_extra_fields(self):
        for extra in ("user_ids","person","note","raw_events","session_url"):
            s=source();s[extra]=["private"]
            with self.subTest(extra=extra),self.assertRaises(UnsafeObservation):
                packet_from_aggregate(s,expected_rate=0.7,minimum_n=10)

    def test_deny_incoherent_counts(self):
        s=source();s["completed_count"]=999
        p=packet_from_aggregate(s,expected_rate=0.7,minimum_n=10)
        with self.assertRaises(UnsafeObservation):
            evaluate(p,now="2026-11-06T09:00:00Z")

if __name__=="__main__":unittest.main()
