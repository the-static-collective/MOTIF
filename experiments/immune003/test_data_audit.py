"""IMMUNE-003Q independent benchmark answer-key audit tests."""
import unittest
import data_audit


class DataAuditTests(unittest.TestCase):
    def test_gold_visible_but_relation_undecided(self):
        a = data_audit.audit_label("$200.00", "We received $200.00 from Stripe.")
        self.assertEqual(a.status, "LITERAL_GOLD_AMOUNT_PRESENT_RELATION_UNVERIFIED")
        self.assertFalse(a.semantic_label_adjudicated)

    def test_unknown_is_not_automatically_true(self):
        a = data_audit.audit_label("unknown", "We received $200.00 from Stripe.")
        self.assertEqual(a.status, "UNKNOWN_ABSENCE_NOT_VERIFIED")

    def test_suspicious_source_incoherence_is_flagged_without_forging_truth(self):
        rows = ({
            "context": "SUBJECT: Payment|CONTENT: We have received your 205.12. Thank you!",
            "question": "What amount was paid to Sara?",
            "ideal": "$2,500",
        },)
        r = data_audit.report(rows)
        self.assertEqual(r["status_counts"]["GOLD_AMOUNT_NOT_LITERAL_IN_SOURCE"], 1)
        self.assertEqual(r["potential_annotation_or_context_mismatch"][0]["row_index"], 0)
        self.assertTrue(r["source_disagreement_is_not_proof_gold_wrong"])

    def test_complete_row_shape_and_duplicate_grain(self):
        rows = (
            {"context": "A paid $12.00 to B.", "question": "Amount paid to B?", "ideal": "$12.00"},
            {"context": "A paid $12.00 to B.", "question": "Amount paid to B?", "ideal": "$12.00"},
            {"context": "", "question": "x", "ideal": "$12.00"},
        )
        p = data_audit.report(rows)
        self.assertEqual(p["duplicate_exact_rows"], 1)
        self.assertEqual(p["complete_rows"], 2)
        self.assertEqual(p["missing_rows"], 1)

    def test_multiple_amount_label_requires_all_visible(self):
        a = data_audit.audit_label("$12.00, $15.00", "She paid $12.00.")
        self.assertEqual(a.status, "GOLD_AMOUNT_NOT_LITERAL_IN_SOURCE")


if __name__ == "__main__":
    unittest.main()
