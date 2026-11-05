"""The silent semantic candidate is a HELD review offer, not an authority."""
import unittest

from semantic_sentinel import synthesize_review_offer


class NeverRunModel:
    def _prepare(self):
        raise AssertionError("Native positive signal must bypass model")


class SentinelTests(unittest.TestCase):
    def test_native_question_does_not_spend_extra_model_compute(self):
        x=synthesize_review_offer(
            "Supper was advertised, but nobody checked safe handling.",
            NeverRunModel(),
        )
        self.assertEqual(x["native_finding"],"FOOD")
        self.assertFalse(x["model_used"])
        self.assertEqual(x["possible_gate"],"FOOD")
        self.assertIn("human",x["question_status"].lower())

    def test_no_model_available_is_explicit_hold(self):
        x=synthesize_review_offer(
            "The speaker cables have not been checked.",None,
        )
        self.assertFalse(x["model_used"])
        self.assertEqual(x["question_status"],"HOLD_NO_MODEL_AVAILABLE")
        self.assertIsNone(x["possible_gate"])

    def test_private_input_is_not_silently_sent_to_model(self):
        with self.assertRaises(ValueError):
            synthesize_review_offer("Send notes to hello@example.com",None)
        with self.assertRaises(ValueError):
            synthesize_review_offer("phone 507-555-1234",None)

    def test_source_boundary_stays_held_even_with_native_match(self):
        x=synthesize_review_offer("The doorway stairs need inspection.",None)
        self.assertEqual(x["native_finding"],"ACCESS")
        self.assertFalse(x["human_execution_approval"])
        self.assertFalse(x["action_dispatched"])
        self.assertFalse(x["field_fact_changed"])
        self.assertFalse(x["event_promise_published"])

    def test_model_never_needed_to_transform_input_into_unapproved_action(self):
        x=synthesize_review_offer("Nobody approved the meal service.",None)
        self.assertNotEqual(x["question_status"],"AUTHORIZED")
        self.assertFalse(x["human_execution_approval"])
        self.assertFalse(x["action_dispatched"])


if __name__=="__main__":
    unittest.main()
