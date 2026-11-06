"""Native-vs-adapter boundary falsifiers."""
import unittest

from bridge import demonstrate

class ActualNativeBoundaryTests(unittest.TestCase):
    def test_native_refuses_unfamiliar_empirical_packet(self):
        result=demonstrate()
        self.assertEqual(result["native_MOTIF_legit001"]["decision"],
                         "HOLD_UNSUPPORTED_SCIENTIFIC_EVIDENCE_SCHEMA")
        self.assertIsNone(result["native_MOTIF_legit001"]["native_answer_to_consciousness_question"])
        self.assertEqual(result["native_MOTIF_legit001"]["status"], "HOLD")

    def test_adapted_computation_is_not_promoted_as_native(self):
        result=demonstrate()
        self.assertFalse(result["separately_authored_typed_adapter"]["native_MOTIF_reasoning"])
        self.assertIsNone(result["winner"])
        self.assertFalse(result["independent_blind_comparison"])
        self.assertFalse(result["real_world_authority"])

if __name__ == "__main__":
    unittest.main()
