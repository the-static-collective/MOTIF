"""024F deterministic preflight — real T5 inference is separately accounted."""
import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
for folder in ("021f","022f","023f","016"):
    sys.path.append(str(ROOT/folder))

from heldout import CASES
from native import TwinCase, native_shortlist, make_inputs, independent_run
from rerank import lexical_rule, prompt, risk_score, rerank_with_real_model
from feedback import validate_review
from model_backend import permitted_sequences


class NativeShortlistTests(unittest.TestCase):
    def test_20_balanced_frozen_independent_future_regimes(self):
        self.assertEqual(len(CASES),20)
        self.assertEqual(len({c.id for c in CASES}),20)
        self.assertEqual(sum(c.drifted_source=="PROBE_ALPHA" for c in CASES),8)
        self.assertEqual(sum(c.drifted_source=="PROBE_BETA" for c in CASES),8)
        self.assertEqual(sum(c.drifted_source is None for c in CASES),4)
        self.assertEqual(sum(c.regime=="ADVERSARIAL_CUE" for c in CASES),4)

    def test_actual_native_016_and_022f_admit_both_only_after_reviews(self):
        case=CASES[0]
        r=native_shortlist(case)
        self.assertEqual(r.eligible_ids,("PROBE_ALPHA","PROBE_BETA"))
        self.assertEqual(r.native_choice,"PROBE_ALPHA")
        self.assertAlmostEqual(r.original_expected_accuracy,.5)
        self.assertAlmostEqual(r.modeled_accuracy_after,1.)
        self.assertTrue(all(x[1]=="ELIGIBLE_SYNTHETIC_REPLAN_ONLY" for x in r.audit))
        self.assertEqual(r.source_label,"INDEPENDENT_SYNTHETIC_CALIBRATION_ONLY")

    def test_source_reviews_are_separate_from_future_drift(self):
        case=CASES[0]
        h,roads,catalog,reviews=make_inputs(case)
        self.assertEqual(len(reviews),2)
        self.assertEqual(
            validate_review(catalog[0], reviews["PROBE_ALPHA"],[x.name for x in h])[0],
            "ELIGIBLE_SYNTHETIC_TEST_ONLY",
        )
        self.assertEqual(
            validate_review(catalog[1], reviews["PROBE_BETA"],[x.name for x in h])[0],
            "ELIGIBLE_SYNTHETIC_TEST_ONLY",
        )
        bad=independent_run(case,"PROBE_ALPHA")
        good=independent_run(case,"PROBE_BETA")
        self.assertFalse(bad["correct"])
        self.assertTrue(good["correct"])
        self.assertEqual(bad["ground_truth_class"],good["ground_truth_class"])
        self.assertTrue(bad["field_actions"]==0==good["field_actions"])
        self.assertFalse(bad["model_holds"]) # in-grammar drift remains an error

    def test_adversarial_risk_notes_are_not_ground_truth(self):
        case=CASES[12]
        self.assertEqual(case.regime,"ADVERSARIAL_CUE")
        self.assertEqual(case.drifted_source,"PROBE_ALPHA")
        a=independent_run(case,"PROBE_ALPHA")
        b=independent_run(case,"PROBE_BETA")
        self.assertFalse(a["correct"])
        self.assertTrue(b["correct"])

    def test_no_drift_both_sources_reach_same_correct_world(self):
        for case in CASES[-4:]:
            self.assertIsNone(case.drifted_source)
            for choice in ("PROBE_ALPHA","PROBE_BETA"):
                self.assertTrue(independent_run(case,choice)["correct"])

    def test_language_prompt_only_uses_registered_candidates_and_notes(self):
        case=CASES[0]
        shortlist=native_shortlist(case)
        p=prompt(case,shortlist)
        q=prompt(case,shortlist,reverse=True)
        self.assertIn(case.alpha_note,p)
        self.assertIn(case.beta_note,p)
        self.assertIn("TEST_ID=PROBE_ALPHA",p)
        self.assertIn("TEST_ID=PROBE_BETA",p)
        self.assertNotEqual(p,q)
        self.assertNotIn(case.id,p)
        self.assertNotIn(case.hidden_world,p)
        self.assertNotIn("drifted_source",p)

    def test_native_only_and_classical_lexical_get_same_inputs(self):
        for case in CASES:
            native=native_shortlist(case)
            lexical=lexical_rule(case)
            self.assertIn(lexical,native.eligible_ids)
        self.assertGreater(risk_score(CASES[0].alpha_note),
                           risk_score(CASES[0].beta_note))

    def test_reranker_bypasses_when_no_actual_tie_without_loading_model(self):
        case=CASES[0]
        shortlist=native_shortlist(case)
        from dataclasses import replace
        narrowed=replace(shortlist,eligible_ids=("PROBE_ALPHA",))
        class BackendThatMustNotRun:
            def _prepare(self):
                raise AssertionError("model should not run")
        r=rerank_with_real_model(BackendThatMustNotRun(),case,narrowed)
        self.assertFalse(r["actual_model_called"])
        self.assertEqual(r["selected"],"PROBE_ALPHA")

    def test_unknown_or_unreviewed_synthetic_choice_refused(self):
        with self.assertRaises(ValueError):
            independent_run(CASES[0],"FABRICATED_SOURCE")

    def test_real_world_consequences_not_inferred(self):
        for case in CASES:
            self.assertEqual(case.regime in ("DECLARED_SYNTHETIC",
                                            "ADVERSARIAL_CUE","NO_DRIFT"),True)
            self.assertAlmostEqual(case.delay_loss,0.0)


if __name__=="__main__":
    unittest.main()
