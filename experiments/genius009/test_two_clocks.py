"""MOTIF GENIUS-009: tests distinguish later reinterpretation from earlier testimony.

All corpora are engineered illustrative cases, not independent historical
validation or proof that any textual, artistic, or physical interpretation
is true. The strongest comparator is a plain append-only typed ledger,
which is equally correct on source fidelity.
"""
import itertools
import json
import unittest

from two_clocks import (
    Assertion, Corpus, Reading, Witness, check_attribution,
    compose_readings, fixtures, naive_flatten, plain_append_only,
    run, validate,
)


class TestTwoClocks(unittest.TestCase):
    def test_later_enochic_association_does_not_modify_genesis(self):
        corpus = fixtures()[0]
        e = check_attribution(corpus, "Enoch-Metatron identification", "Genesis5", 0)
        self.assertEqual(e["status"], "HOLD_UNSUPPORTED_RETROJECTION")
        self.assertIsNone(e["source_polairty"])
        self.assertEqual(e["later_witnesses_with_explicit_affirmation"][0]["source"],
                         "3Enoch")
        late = check_attribution(corpus, "Enoch-Metatron identification",
                                 "3Enoch", 3)
        self.assertEqual(late["status"], "EXPLICIT_SOURCE_ATTESTATION")
        self.assertEqual(late["source_polairty"], "AFFIRM")
        self.assertTrue(late["no_theological_or_historical_certification"])

    def test_what_source_says_never_depends_on_reveal_order(self):
        corpus = fixtures()[0]
        seen = set()
        for order in itertools.permutations(w.witness_id for w in corpus.witnesses):
            result = compose_readings(corpus, order)
            seen.add(json.dumps(result["final_source_attributions"], sort_keys=True))
            genesis = [r for r in result["final_source_attributions"]
                       if r["owner"] == "Genesis5"]
            self.assertEqual(len(genesis), 1)
            self.assertEqual(genesis[0]["proposition"], "Enoch walks with God")
            self.assertTrue(all(r["source_histories_never_edited"]
                                for r in result["snapshots"]))
        self.assertEqual(len(seen), 1)

    def test_revelation_order_changes_when_reader_recognizes_callback(self):
        corpus = fixtures()[0]
        forward = compose_readings(corpus, ("Genesis5", "1Enoch", "3Enoch"))
        reverse = compose_readings(corpus, ("3Enoch", "1Enoch", "Genesis5"))
        self.assertEqual(forward["snapshots"][-1]["new_reader_reinterpretations"][0]
                         ["reading_id"], "later_enochic_association")
        self.assertEqual(reverse["snapshots"][-1]["new_reader_reinterpretations"][0]
                         ["reading_id"], "later_enochic_association")
        # A distinct mixed order activates a callback in the *middle*,
        # even though final source ledger never changes.
        mixed = compose_readings(corpus, ("Genesis5", "3Enoch", "1Enoch"))
        self.assertEqual(len(mixed["snapshots"][1]["new_reader_reinterpretations"]), 1)
        self.assertEqual(len(mixed["snapshots"][2]["new_reader_reinterpretations"]), 0)
        self.assertEqual(forward["final_reinterpretations"],
                         mixed["final_reinterpretations"])

    def test_retrojection_control_is_wrong_but_classical_ledger_is_right(self):
        for corpus in fixtures():
            weak = naive_flatten(corpus)
            strong = plain_append_only(corpus)
            self.assertEqual(weak["false_attribution_count"], 1)
            self.assertEqual(strong["false_attribution_count"], 0)
            self.assertEqual(len(strong["source_claims"]), 3)

    def test_empirical_calibration_updates_interpretation_not_old_sensor(self):
        corpus = fixtures()[2]
        result = compose_readings(
            corpus, ("sensor_t0", "lab_t1", "calibration_t2"))
        first = [r for r in result["final_source_attributions"]
                 if r["owner"] == "sensor_t0"]
        self.assertEqual(first[0]["proposition"], "Instrument reading was 12")
        self.assertIn("subtracting an offset", result["final_reinterpretations"][0]
                      ["interpretation"])
        self.assertNotIn("Calibration offset was 3", first[0]["proposition"])

    def test_narrative_callback_annotation_is_not_event_rewrite(self):
        corpus = fixtures()[1]
        result = compose_readings(
            corpus, ("scene_final", "scene_second", "scene_first"))
        self.assertEqual(result["source_order"],
                         ["scene_first", "scene_second", "scene_final"])
        self.assertEqual(result["disclosure_order"],
                         ["scene_final", "scene_second", "scene_first"])
        self.assertEqual(result["snapshots"][-1]["new_reader_reinterpretations"][0]
                         ["about_earlier"], "scene_first")

    def test_missing_claim_does_not_get_invented(self):
        corpus = fixtures()[1]
        r = check_attribution(corpus, "Never recorded", "scene_first", 0)
        self.assertEqual(r["status"], "HOLD_UNSUPPORTED_RETROJECTION")
        self.assertEqual(r["later_witnesses_with_explicit_affirmation"], [])
        self.assertEqual(check_attribution(corpus, "unknown", "NO_SUCH_SOURCE")
                         ["status"], "HOLD_UNKNOWN_SOURCE")

    def test_era_constraint_holds_even_when_later_source_explicit(self):
        corpus = fixtures()[0]
        r = check_attribution(corpus, "Enoch-Metatron identification",
                              "3Enoch", 0)
        self.assertEqual(r["status"], "HOLD_SOURCE_OUTSIDE_REQUESTED_LAYER")

    def test_invalid_cross_lane_interpretation_rejected(self):
        a = Witness("A", 0, "TEXT_TRADITION", (Assertion("one"),), "ref:A")
        b = Witness("B", 1, "EMPIRICAL_INSTRUMENT", (Assertion("two"),), "ref:B")
        corpus = Corpus("bad_lane", (a, b),
                        (Reading("r", "B", "A", "fake transfer", "two"),))
        with self.assertRaises(ValueError):
            validate(corpus)

    def test_reading_cannot_claim_nonexistent_later_explicit_text(self):
        a = Witness("A", 0, "TEXT_TRADITION", (Assertion("one"),), "ref:A")
        b = Witness("B", 1, "TEXT_TRADITION", (Assertion("two"),), "ref:B")
        corpus = Corpus("bad_provenance", (a, b),
                        (Reading("r", "B", "A", "fake", "not actually attested"),))
        with self.assertRaises(ValueError):
            validate(corpus)

    def test_future_reinterpretation_cannot_be_retroactively_earlier(self):
        a = Witness("A", 1, "TEXT_TRADITION", (Assertion("one"),), "ref:A")
        b = Witness("B", 0, "TEXT_TRADITION", (Assertion("two"),), "ref:B")
        corpus = Corpus("bad_era", (a, b),
                        (Reading("r", "B", "A", "fake", "two"),))
        with self.assertRaises(ValueError):
            validate(corpus)

    def test_disclosure_replay_or_omission_is_rejected(self):
        corpus = fixtures()[0]
        for order in (("Genesis5", "Genesis5", "3Enoch"),
                      ("Genesis5", "1Enoch"), ("Genesis5", "1Enoch", "alien")):
            with self.assertRaises(ValueError):
                compose_readings(corpus, order)

    def test_duplicate_witness_proposition_and_reading_rejected(self):
        a = Witness("A", 0, "TEXT_TRADITION",
                    (Assertion("one"), Assertion("one")), "ref:A")
        with self.assertRaises(ValueError):
            validate(Corpus("x", (a,), ()))
        c = Witness("C", 2, "TEXT_TRADITION", (Assertion("three"),), "ref:C")
        d = Witness("D", 0, "TEXT_TRADITION", (Assertion("other"),), "ref:D")
        r = Reading("r", "C", "D", "association", "three")
        with self.assertRaises(ValueError):
            validate(Corpus("x", (c, d), (r, r)))

    def test_three_domains_six_disclosure_orders_each(self):
        r = run()
        self.assertTrue(r["no_external_action"])
        self.assertEqual(r["status"],
                         "RESEARCH_HOLD_SYNTHETIC_INTERPRETATION_EXPERIMENT")
        self.assertEqual(len(r["worlds"]), 3)
        for key, row in r["worlds"].items():
            self.assertEqual(row["presentations_evaluated"], 6)
            self.assertTrue(row["source_record_invariant_under_reordering"])
            self.assertTrue(row["final_reader_reinterpretations_invariant"])
            self.assertEqual(row["weak_flatten_false_attributions"], 1)
            self.assertEqual(row["strong_classical_append_only_false_attributions"], 0)
            self.assertEqual(row["two_clock_false_attributions"], 0)
        self.assertTrue(r["classical_ledger_baseline_is_equally_source_correct"])


if __name__ == "__main__":
    unittest.main()
