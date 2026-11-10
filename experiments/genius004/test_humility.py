"""MOTIF GENIUS-004 tests: falsifiable self-correction, not learned morality."""
import json
import unittest

from humility import (
    ABSTAIN_COST, ARMS, POLICIES, Learner, Observation, Policy, TOPICS,
    build_world, decide, evaluate, public_projection, run,
)


def item(k, yes, *, node="A", topic="safety", shared=True, opt_in=False,
         note=""):
    return Observation(
        event_id=f"test-{node}-{topic}-{k}",
        node=node, topic=topic, yes=yes,
        shareable=shared, opt_in=opt_in,
        evidence_ref=f"synthetic:{node}/{topic}/{k}", private_note=note,
    )


def prior(node="A", topic="safety", answers=None):
    if answers is None:
        answers = [True] * 20
    return tuple(item(i, ans, node=node, topic=topic) for i, ans in enumerate(answers))


class TestHumilityAperture(unittest.TestCase):
    def test_public_projection_excludes_withheld_and_strips_private_note(self):
        raw = (item(1, True, note="PRIVATE_NOTE"),
               item(2, False, shared=False, note="HIDDEN_LABEL"))
        p = public_projection(raw)
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0].private_note, "")
        self.assertNotIn("PRIVATE_NOTE", json.dumps(p[0].__dict__))
        model = Learner().seed(raw)
        self.assertEqual(model.global_history, [True])
        with self.assertRaises(ValueError):
            model.ingest(raw[0])  # Never ingest local state unprojected
        with self.assertRaises(ValueError):
            model.ingest(p[0])    # Replayed source id

    def test_invariants_when_evidence_missing(self):
        model = Learner().seed(prior())
        h = decide(model, item("new", True, node="visitor"), Policy(.2, .4, .06))
        self.assertEqual(h["action"], "HOLD")
        self.assertIsNone(h["probability"])
        asked = decide(model, item("new", True, node="visitor", opt_in=True),
                       Policy(.2, .4, .06))
        self.assertEqual(asked["action"], "ASK")
        self.assertIsNone(asked["probability"])
        self.assertTrue(asked["question"])
        self.assertFalse("question" in h and h["question"])
        self.assertEqual(model.predict("visitor", "safety")["GLOBAL"], None)

    def test_event_current_answer_not_read_before_decision(self):
        model = Learner().seed(prior(answers=[True] * 16))
        a = decide(model, item("future", False), Policy(.2, .45, .05))
        b = decide(model, item("future", True), Policy(.2, .45, .05))
        self.assertEqual(a, b)  # event label is not touched by selection
        self.assertEqual(a["action"], "RETAIN")

    def test_revise_from_recent_but_do_not_invent_proof(self):
        model = Learner().seed(prior(answers=[True] * 12 + [False] * 2))
        r = decide(model, item("new", False), Policy(.1, .99, 0.0))
        self.assertEqual(r["action"], "REVISE")
        self.assertGreater(r["gap"], .1)
        self.assertEqual(r["probability"], model.predict("A", "safety")["WINDOW4"])
        self.assertTrue(r["no_external_action"])

    def test_cross_topic_reframe_requires_multiple_discrepancies(self):
        data = prior(topic="safety", answers=[True]*16 + [False]*4) + \
               prior(topic="speed", answers=[True]*16 + [False]*4)
        model = Learner().seed(data)
        r = decide(model, item("now", False), Policy(.2, .99, 0))
        self.assertEqual(r["action"], "REFRAME")
        self.assertGreaterEqual(r["divergent_topics"], 2)
        self.assertEqual(r["probability"], model.predict("A", "safety")["EWMA"])

    def test_release_abstains_when_recent_past_violates_old_rule(self):
        model = Learner().seed(prior(answers=[True]*16+[False]*4))
        r = decide(model, item("later", True), Policy(.12, .4, 0))
        self.assertEqual(r["action"], "RELEASE")
        self.assertIsNone(r["probability"])
        self.assertIn("withhold forecast", r["reasons"][0])

    def test_ask_when_equivocal_only_if_opted_in(self):
        model = Learner().seed(prior(answers=[True, False] * 10))
        not_opted = decide(model, item("later", True), Policy(.2, .5, .07))
        opted = decide(model, item("later", True, opt_in=True), Policy(.2, .5, .07))
        self.assertEqual(not_opted["action"], "RETAIN")
        self.assertEqual(opted["action"], "ASK")
        self.assertIsNone(opted["probability"])

    def test_abstention_has_nonzero_cost_and_reported_coverage(self):
        train = prior()
        future = (item("new", True, node="visitor", opt_in=True),)
        e = evaluate(train, future, Policy(.2, .4, .06), "STABLE")
        m = e["method"]["HUMILITY"]
        self.assertEqual(m["coverage"], 0)
        self.assertEqual(m["accepted_events"], 0)
        self.assertEqual(m["mean_costed_brier"], ABSTAIN_COST)
        self.assertEqual(e["unseen_pair_first_response_abstentions"], 1)
        self.assertEqual(m["action_counts"]["ASK"], 1)

    def test_withheld_outcomes_cannot_change_next_forecast(self):
        training = prior()
        later = item(99, False, shared=False)
        m = Learner().seed(training)
        p1 = m.predict("A", "safety")
        self.assertFalse(m.ingest(later))
        self.assertEqual(m.predict("A", "safety"), p1)
        self.assertEqual(len(m.global_history), 20)

    def test_duplicate_source_event_rejected_and_bad_input_rejected(self):
        model = Learner().seed(prior(answers=[True]*4))
        with self.assertRaises(ValueError):
            model.ingest(item(0, True))
        with self.assertRaises(ValueError):
            model.ingest(item("corrupt", 1))
        with self.assertRaises(ValueError):
            build_world(44444, "FABRICATED_MODE")

    def test_separately_seeded_future_is_not_training_label(self):
        train, fut = build_world(40421, "ABRUPT")
        self.assertTrue(train and fut)
        self.assertFalse(set(x.event_id for x in train) & set(x.event_id for x in fut))
        self.assertTrue(all(x.private_note for x in fut))
        e = evaluate(train, fut, POLICIES[0], "ABRUPT", record_receipts=True)
        self.assertTrue(all(r["new_evidence_used_only_after_forecast"] for r in e["receipts"]))
        self.assertEqual(e["method"]["HUMILITY"]["graded_events"], len(e["receipts"]))
        self.assertNotIn("NEVER_EXPOSE_PRIVATE_SIMULATOR_NOTES", json.dumps(e))
        self.assertEqual(e["method"]["GLOBAL"]["graded_events"],
                         e["method"]["HUMILITY"]["graded_events"])


class TestFrozenValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run()

    def test_freeze_receipt_and_controls_are_present(self):
        r = self.report
        self.assertEqual(r["validation_world_count"], 10)
        self.assertEqual(len(r["pre_future_policy_sha256"]), 64)
        self.assertEqual(r["status"], "RESEARCH_HOLD_NOT_EXTERNAL_PROOF")
        self.assertTrue(r["no_human_contact_no_external_action"])
        self.assertEqual(set(r["costed_brier_by_regime"]),
                         {"STABLE", "ABRUPT", "LOCAL", "GRADUAL", "STABLE_NOISY"})
        for regime, results in r["costed_brier_by_regime"].items():
            self.assertEqual(set(results), set(ARMS) | {"HUMILITY"})
            self.assertTrue(all(0 <= loss <= 1 for loss in results.values()))

    def test_self_critique_gate_keeps_classical_method_when_unproven(self):
        gate = self.report["promotion_gate"]
        self.assertIn(gate["selected_classical_fallback"], ARMS)
        self.assertEqual(gate["authority"], "NO_RUNTIME_PROMOTION_OR_EXTERNAL_ACTION")
        self.assertEqual(
            gate["provenance_caveat"],
            "POSTHOC_GATE_INTRODUCED_AFTER_FIRST_HELDOUT_INSPECTION",
        )
        means = gate["validation_macro_mean_costed_brier"]
        best = gate["selected_classical_fallback"]
        self.assertEqual(means[best], min(means[a] for a in ARMS))
        if not gate["candidate_beats_classical_on_validation"]:
            self.assertEqual(gate["status"], "RESEARCH_ONLY_NO_PROMOTION")
        else:
            self.assertLess(means["HUMILITY"] + gate["minimum_required_macro_margin"],
                            means[best])

    def test_heldout_receipts_and_frozen_policy_are_bounded(self):
        r = self.report
        self.assertIn(r["selected_policy"], [p.as_dict() for p in POLICIES])
        for by_regime in r["holdouts"].values():
            for result in by_regime.values():
                self.assertEqual(result["policy"], r["selected_policy"])
                self.assertGreater(result["withheld_excluded"], 0)
                self.assertNotIn("NEVER_EXPOSE_PRIVATE_SIMULATOR_NOTES", json.dumps(result))
                self.assertEqual(result["method"]["CUMULATIVE"]["graded_events"],
                                 result["method"]["HUMILITY"]["graded_events"])


if __name__ == "__main__":
    unittest.main()
