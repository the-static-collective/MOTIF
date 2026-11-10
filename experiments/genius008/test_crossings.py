"""GENIUS-008 falsifiers: do not force historical, artistic or ethical unity."""
import json
import unittest

from crossings import (
    Beat, Plan, Witness, counterpoint, demo, participation_draft,
    source_ladder, story_braid,
)


class TestStrangeGeniusCrossings(unittest.TestCase):
    def test_enoch_later_identification_not_primary_genesis_witness(self):
        r=demo()["enoch_bacon_aquinas"]
        self.assertEqual(r["status"], "HOLD_NO_EARLY_EXPLICIT_WITNESS")
        self.assertEqual(r["witnesses"][0]["source_id"],
                         "3Enoch:MetatronNarrative")
        self.assertTrue(r["sources_not_copied_back_in_time"])
        self.assertTrue(r["no_external_fact_or_theology_decided"])

    def test_enoch_primary_claim_can_be_witnessed_at_its_own_layer(self):
        e=(Witness("Genesis5", 0, "Enoch walked with God", "EXPLICIT_TEXT"),)
        r=source_ladder(e, "Enoch walked with God", 0)
        self.assertEqual(r["status"], "ATTESTED_AT_REQUESTED_LAYER")

    def test_a_modern_interpretation_does_not_become_ancient_explicit_text(self):
        r=source_ladder((Witness("modern", 3, "X", "LATER_INTERPRETATION"),), "X", 3)
        self.assertEqual(r["status"], "HOLD_NO_EARLY_EXPLICIT_WITNESS")

    def test_nonlinear_triple_story_and_reinterpreting_callback(self):
        r=demo()["povenmire_acaster_nolan_shakespeare"]
        self.assertEqual(r["status"], "CONSISTENT_SYNTHETIC_BRAID")
        self.assertEqual(r["distinct_strands"], ["A", "B", "C"])
        self.assertEqual(r["audience_reveal"][:2], ["clock", "door_open"])
        self.assertEqual(r["chronology"][:2], ["door_open", "clock"])
        self.assertEqual(len(r["callbacks"]), 2)
        self.assertEqual(r["convergence_ids"], ["convergence"])
        self.assertTrue(r["not_a_measurement_of_comedic_quality"])

    def test_unchanged_callback_text_does_not_count_as_reinterpretation(self):
        r=story_braid((
            Beat("A", "A", 1, 1, "motif", "same"),
            Beat("B", "B", 2, 2, "different", "other"),
            Beat("C", "C", 3, 3, "third", "other"),
            Beat("payoff", "ALL", 4, 4, "motif", "same", "A", True),
        ))
        self.assertEqual(r["status"], "HOLD_MISSING_OR_INVALID_BRAID")
        self.assertEqual(r["invalid_callbacks"], ["payoff"])

    def test_broken_reference_or_reveal_order_is_rejected(self):
        r=story_braid((
            Beat("A", "A", 1, 1, "m", "old"),
            Beat("B", "B", 2, 2, "n", "n"),
            Beat("C", "C", 3, 3, "o", "o"),
            Beat("last", "ALL", 4, 4, "m", "new", "missing", True),
        ))
        self.assertEqual(r["status"], "HOLD_MISSING_OR_INVALID_BRAID")

    def test_cornell_jackson_tesla_4_vs_5_realigns_at_20(self):
        r=counterpoint(4, 5, 4)
        self.assertEqual(r["full_realignment_beats"], 20)
        self.assertEqual(r["voice_accents"], [0, 4, 8, 12, 16, 20])
        self.assertEqual(r["guitar_accents"], [0, 5, 10, 15, 20])
        self.assertEqual(r["quarter_cycle_resultant_vectors"][0], (1.0, 0.0))
        self.assertEqual(r["quarter_cycle_resultant_vectors"][1], (0.0, 1.0))
        self.assertTrue(r["constant_magnitude_verified"])
        self.assertTrue(r["not_a_recording_transcription_or_free_energy_claim"])

    def test_invalid_meter_refused(self):
        with self.assertRaises(ValueError):
            counterpoint(0, 5, 4)
        with self.assertRaises(ValueError):
            counterpoint(True, 5, 4)
        with self.assertRaises(ValueError):
            counterpoint(4, 5, 4, rotor_phase_quarters=2)

    def test_jesus_simmons_oppenheimer_draft_refuses_throughput_over_consent(self):
        r=demo()["jesus_simmons_oppenheimer"]
        self.assertEqual(r["candidate"], "small_accessible_table")
        self.assertEqual(r["evaluated"][0]["status"], "HOLD")
        self.assertIn("EXPLICIT_REFUSAL", r["evaluated"][0]["reasons"])
        self.assertIn("ACCESSIBILITY_NOT_ESTABLISHED", r["evaluated"][0]["reasons"])
        self.assertTrue(r["never_sent_or_executed"])

    def test_missing_access_or_missing_risk_review_is_hold(self):
        for accessible, risks in ((False, True), (True, False)):
            p=Plan("bad", (("A", "YES_TO_DRAFT"),), accessible, risks, 1, 0)
            r=participation_draft((p,), ("A",))
            self.assertEqual(r["status"], "HOLD_NO_ACCEPTABLE_DRAFT")

    def test_withheld_consent_not_inferred(self):
        r=participation_draft((
            Plan("incomplete", (("A", "YES_TO_DRAFT"),), True, True, 4, 1),
        ), ("A", "B"))
        self.assertIsNone(r["candidate"])
        self.assertEqual(r["evaluated"][0]["reasons"],
                         ["NO_DISCLOSED_UNANIMOUS_DRAFT_PERMISSION"])

    def test_no_fake_repeated_votes(self):
        with self.assertRaises(ValueError):
            participation_draft((
                Plan("x", (("A", "YES_TO_DRAFT"), ("A", "NO")), True, True, 5, 0),
            ), ("A",))

    def test_four_distinct_proof_boundaries_and_no_act(self):
        r=demo()
        self.assertTrue(r["no_external_action"])
        self.assertEqual(r["status"], "SYNTHETIC_CROSSING_RECEIPTS_NOT_GENIUS_PROOF")
        self.assertEqual(len(set(r) - {"status", "no_external_action"}), 4)
        self.assertNotIn("approval_to_execute", json.dumps(r))


if __name__ == "__main__":
    unittest.main()
