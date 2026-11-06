"""LEGIT-002 evidence-routing falsifiers; no patients or external actions."""
import copy
import json
import unittest

from evidence_router import Hold, load_packet, run, validate

class CovertConsciousnessTests(unittest.TestCase):
    def setUp(self):
        self.packet = load_packet()

    def test_exact_published_numbers(self):
        result = run(self.packet)
        self.assertEqual(result["behaviorally_unresponsive_neural_positive_rate"]["numerator"],60)
        self.assertEqual(result["behaviorally_unresponsive_neural_positive_rate"]["denominator"],241)
        self.assertEqual(result["behaviorally_responsive_neural_negative_rate"]["numerator"],69)
        self.assertEqual(result["behaviorally_responsive_neural_negative_rate"]["denominator"],112)
        self.assertAlmostEqual(result["behaviorally_unresponsive_neural_positive_rate"]["sample_rate"],60/241,places=6)
        self.assertAlmostEqual(result["behaviorally_responsive_neural_negative_rate"]["sample_rate"],69/112,places=6)

    def test_latent_consciousness_not_equated_with_positive_test(self):
        result = run()
        self.assertIsNone(result["individual_probability_of_awareness"])
        self.assertEqual(result["status"],"HOLD_PATIENT_LEVEL_LATENT_CLAIM")
        self.assertFalse(result["negative_neural_test_proves_no_awareness"])
        self.assertEqual(result["reason_code"],"ABSENT_REFERENCE_STANDARD_FOR_SUBJECTIVE_EXPERIENCE")

    def test_reports_manual_provenance_not_autonomous_comprehension(self):
        result = run()
        self.assertFalse(result["native_MOTIF_reasoning"])
        self.assertFalse(result["real_world_authority"])
        self.assertTrue(result["requires_separate_human_clinical_governance"])
        self.assertTrue(len(result["source_packet_sha256"])==64)

    def test_repeat_reproducibility(self):
        self.assertEqual(run(),run())

    def test_missing_denominator_refused(self):
        x=copy.deepcopy(self.packet)
        x["source_cards"][0]["counts"][0].pop("total")
        with self.assertRaises(Hold):run(x)

    def test_positive_negative_nonreconciliation_refused(self):
        x=copy.deepcopy(self.packet)
        x["source_cards"][0]["counts"][0]["positive_neural_task"]=61
        with self.assertRaises(Hold):run(x)

    def test_duplicate_cohort_refused(self):
        x=copy.deepcopy(self.packet)
        x["source_cards"][0]["counts"].append(copy.deepcopy(x["source_cards"][0]["counts"][0]))
        with self.assertRaises(Hold):run(x)

    def test_duplicate_source_refused(self):
        x=copy.deepcopy(self.packet)
        x["source_cards"].append(copy.deepcopy(x["source_cards"][0]))
        with self.assertRaises(Hold):run(x)

    def test_tampered_target_refused(self):
        x=copy.deepcopy(self.packet)
        x["target"]="ALL_EXPERIENCE_CERTAIN"
        with self.assertRaises(Hold):run(x)

    def test_patient_scope_refused(self):
        x=copy.deepcopy(self.packet)
        x["scope"]="LIVE_PATIENT_DIAGNOSIS"
        with self.assertRaises(Hold):run(x)

    def test_unsupported_passive_paradigm_refused(self):
        x=copy.deepcopy(self.packet)
        x["proxy"]="PASSIVE_AUDITORY_RESPONSES"
        with self.assertRaises(Hold):run(x)

    def test_missing_denominator_group_refused(self):
        x=copy.deepcopy(self.packet)
        x["source_cards"][0]["counts"]=x["source_cards"][0]["counts"][:1]
        with self.assertRaises(Hold):run(x)

    def test_missing_inference_prohibition_refused(self):
        x=copy.deepcopy(self.packet)
        x["prohibited_outputs"].remove("POSTERIOR_FROM_PREVALENCE_ALONE")
        with self.assertRaises(Hold):run(x)

    def test_noninteger_count_refused(self):
        x=copy.deepcopy(self.packet)
        x["source_cards"][0]["counts"][0]["positive_neural_task"]=60.0
        with self.assertRaises(Hold):run(x)

    def test_different_observation_model_refused(self):
        x=copy.deepcopy(self.packet)
        x["source_cards"][0]["counts"][1]["negative_neural_task"]=0
        x["source_cards"][0]["counts"][1]["positive_neural_task"]=112
        with self.assertRaises(Hold):run(x)

    def test_source_url_required(self):
        x=copy.deepcopy(self.packet)
        x["source_cards"][0]["url"]="unverified"
        with self.assertRaises(Hold):run(x)

    def test_unknown_instrument_scope_refused(self):
        x=copy.deepcopy(self.packet)
        x["status"]="AUTOMATICALLY_VERIFIED"
        with self.assertRaises(Hold):run(x)

if __name__ == "__main__":
    unittest.main()
