"""023F: deterministic tests are NOT FLAN-T5 quality results."""
from dataclasses import replace
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
for folder in ("021f", "022f", "016"):
    sys.path.append(str(ROOT / folder))

from chorus import LocalFlanT5Small, SidecarNote, SidecarRun
from forest import LivingForest
from feedback import QuestionLedger, submit_critic_question
from cases import CASES, inputs
from model_backend import NO_TEST, allowed_next, permitted_sequences
from sealed_oracle import SealedSyntheticOracle
from trial import controls, reference_challenge, summarize


class TinyFakeTokenizer:
    eos_token_id = 3
    def encode(self, text, add_special_tokens=False):
        return [ord(c)+10 for c in text]


class FeedbackTrialTests(unittest.TestCase):
    def test_freeze_synthetic_case_ids(self):
        self.assertEqual(len(CASES),16)
        self.assertEqual(len({c.id for c in CASES}),len(CASES))
        self.assertTrue(all(c.hidden in c.worlds for c in CASES))
        self.assertTrue(all(not any("@" in str(v) for v in c.facts) for c in CASES))

    def test_token_trie_exactly_limits_outputs_to_registered_contract(self):
        tokens = permitted_sequences(TinyFakeTokenizer(),("FOOD_SERVICE_GATE","BAD_FOOD_TEST"))
        self.assertEqual(len(tokens),3)
        self.assertIn("TEST_ID=NO_TEST",tokens.values())
        self.assertNotIn("TEST_ID=AUTHORIZE_MEAL",tokens.values())
        common = "TEST_ID="
        prefix = tuple(TinyFakeTokenizer().encode(common))
        allowed = allowed_next(prefix,tokens,3)
        self.assertEqual(set(allowed),set(ord(c)+10 for c in "FBN"))
        self.assertNotIn(ord("X")+10,allowed)

    def test_token_trie_rejects_duplicate_or_unsafe_ids(self):
        t = TinyFakeTokenizer()
        with self.assertRaises(ValueError):
            permitted_sequences(t,("FOOD_SERVICE_GATE","FOOD_SERVICE_GATE"))
        with self.assertRaises(ValueError):
            permitted_sequences(t,("FOOD;SHARE_PRIVATE_DATA",))
        with self.assertRaises(ValueError):
            permitted_sequences(t,tuple("TEST_"+str(i) for i in range(9)))

    def test_safe_abstain_is_not_a_hallucinated_privilege(self):
        case = CASES[0]
        h, r, catalog, reviews = inputs(case)
        native = LivingForest(h,r,budget=.65,rounds=1,max_parallel=2).plan()
        x = reference_challenge(case,NO_TEST,native,case.projection(),
                                h,r,catalog,reviews)
        self.assertEqual(x.status,"HOLD_MODEL_ABSTAINED")
        self.assertFalse(x.field_execution_authorized)
        self.assertIsNone(x.challenged_plan)

    def test_reference_knows_food_is_useful_but_not_needed_once_resolved(self):
        open_case = CASES[0]
        h,r,catalog,reviews=inputs(open_case)
        native=LivingForest(h,r,budget=.65,rounds=1,max_parallel=2).plan()
        x=reference_challenge(open_case,"FOOD_SERVICE_GATE",native,
                              open_case.projection(),h,r,catalog,reviews)
        self.assertEqual(x.status,"ELIGIBLE_SYNTHETIC_REPLAN_ONLY")
        self.assertAlmostEqual(native.expected_final_accuracy,.5)
        self.assertAlmostEqual(x.challenged_expected_accuracy,1.)
        known_case=CASES[3]
        h,r,catalog,reviews=inputs(known_case)
        native=LivingForest(h,r,budget=.65,rounds=1,max_parallel=2).plan()
        y=reference_challenge(known_case,"FOOD_SERVICE_GATE",native,
                              known_case.projection(),h,r,catalog,reviews)
        self.assertNotEqual(y.status,"ELIGIBLE_SYNTHETIC_REPLAN_ONLY")
        self.assertAlmostEqual(native.expected_final_accuracy,1.)

    def test_fake_better_price_stays_refused(self):
        case=CASES[7]
        h,r,catalog,reviews=inputs(case)
        native=LivingForest(h,r,budget=.65,rounds=1,max_parallel=2).plan()
        x=reference_challenge(case,"BAD_FOOD_TEST",native,
                              case.projection(),h,r,catalog,reviews)
        self.assertEqual(x.status,"REFUSE_CALIBRATION_FALSIFIED")

    def test_human_only_and_delayed_queries_stay_blocked(self):
        for case,expected in ((CASES[8],"HOLD_HUMAN_AUTHORITY_REQUIRED"),
                               (CASES[11],"HOLD_DELAY_INFORMATION_TRADEOFF_UNCALIBRATED")):
            h,r,catalog,reviews=inputs(case)
            native=LivingForest(h,r,budget=.65,rounds=1,max_parallel=2).plan()
            x=reference_challenge(case,catalog[0].road.name,native,
                                  case.projection(),h,r,catalog,reviews)
            self.assertEqual(x.status,expected)

    def test_drifting_source_is_falsified_by_independent_held_run(self):
        case=CASES[13]
        h,r,catalog,reviews=inputs(case)
        native=LivingForest(h,r,budget=.65,rounds=1,max_parallel=2).plan()
        x=reference_challenge(case,catalog[0].road.name,native,
                              case.projection(),h,r,catalog,reviews)
        self.assertEqual(x.status,"ELIGIBLE_SYNTHETIC_REPLAN_ONLY")
        tree=LivingForest(h,(*r,replace(catalog[0].road,allowed=True)),
                          budget=.65,rounds=1,max_parallel=2)
        oracle=SealedSyntheticOracle(case.hidden)
        plan,step=tree.run_synthetic_round(oracle.execute)
        self.assertIn("DRIFT_FOOD_TEST",plan.selected)
        self.assertEqual(tree.plan().tentative_answer,"A1_M0")
        self.assertEqual(case.hidden,"11")
        self.assertEqual(tree.state,"ANSWER") # false confidence is a real failure

    def test_reference_controls_never_promote_unauthorized_operations(self):
        r=controls()
        self.assertEqual(set(r),{"ALWAYS_FOOD_TEST","SEEDED_RANDOM_REGISTERED_OR_ABSTAIN"})
        self.assertTrue(all(
            x["status"]!="ELIGIBLE_SYNTHETIC_REPLAN_ONLY"
            for x in r["SEEDED_RANDOM_REGISTERED_OR_ABSTAIN"]["selection_trace"]
            if x["selected"]=="HUMAN_FOOD_CONFIRMATION"
        ))

    def test_model_must_be_explicitly_loaded_for_real_trial(self):
        model=LocalFlanT5Small()
        self.assertIsNone(model._model)
        self.assertEqual(model.model_id,"google/flan-t5-small")


if __name__=="__main__":
    unittest.main()
