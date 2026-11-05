"""MOTIF-022F: exhaustive refusal, native isolation and real Forest integration."""
from dataclasses import replace
import unittest

from feedback import (
    QuestionAwareBackend, QuestionLedger, ReviewReceipt,
    submit_critic_question, validate_review,
)
from chorus import SidecarNote, parallel_critique
from forest import LivingForest
from demo import scenario
from sealed_oracle import (
    SealedSyntheticOracle, ScriptedCritic, modeled_problem, public_projection,
)


def fixture(proposed="FOOD_SERVICE_GATE", *, sidecar_grace=.3):
    hypotheses, original, catalog = modeled_problem()
    projection = public_projection()
    backend = QuestionAwareBackend(ScriptedCritic(proposed), catalog)
    chorus = parallel_critique(
        lambda: LivingForest(hypotheses, original, budget=.65,
                             rounds=1, max_parallel=2).plan(),
        projection, backend, sidecar_grace_seconds=sidecar_grace,
    )
    reviews = {c.road.name: SealedSyntheticOracle.calibration(c) for c in catalog}
    return hypotheses, original, catalog, projection, chorus, reviews


def challenge(proposed="FOOD_SERVICE_GATE", **opts):
    hyp, roads, catalog, projection, chorus, reviews = fixture(proposed)
    return submit_critic_question(
        chorus, projection, hyp, roads, catalog, reviews,
        QuestionLedger(), budget=.65, **opts,
    )


class CriticQuestionTests(unittest.TestCase):
    def test_actual_016_forest_gains_independent_second_question(self):
        result = scenario(hidden="10")
        self.assertEqual(result["question_decision"]["status"], "ELIGIBLE_SYNTHETIC_REPLAN_ONLY")
        self.assertAlmostEqual(
            result["primary_native_plan_before_critique"]["expected_final_accuracy"], .5)
        revised = result["question_decision"]["challenged_plan"]
        self.assertAlmostEqual(revised["expected_final_accuracy"], 1.)
        self.assertIn("FOOD_SERVICE_GATE", revised["selected"])
        self.assertEqual(set(result["independent_synthetic_run"]["planned_portfolio"]),
                         {"AUDIO_PATH_TEST", "FOOD_SERVICE_GATE"})
        self.assertTrue(result["independent_synthetic_run"]["model_correct"])
        self.assertEqual(result["independent_synthetic_run"]["final_answer"], "A1_M0")
        self.assertFalse(result["actual_T5_executed"])
        self.assertEqual(result["chorus_backend"], "SCRIPTED_CRITIC_NOT_AN_LLM")

    def test_classical_same_catalog_ties_critic_assisted_forest(self):
        x = scenario(hidden="01")
        self.assertEqual(
            x["question_decision"]["challenged_plan"],
            x["matched_classical_planner_same_admitted_test"]
        )
        self.assertEqual(x["independent_synthetic_run"]["final_answer"], "A0_M1")
        self.assertTrue(x["independent_synthetic_run"]["model_correct"])

    def test_primary_native_unchanged_and_human_permission_not_inferred(self):
        x = scenario()
        self.assertEqual(x["primary_native_plan_before_critique"]["selected"],
                         ["AUDIO_PATH_TEST"] if isinstance(
                             x["primary_native_plan_before_critique"]["selected"], list)
                         else ("AUDIO_PATH_TEST",))
        self.assertEqual(x["source_permission_from_human_report"],
                         "ROOM_USE_REPORTED_GRANTED_ONLY")
        self.assertFalse(x["real_world_deployment_or_app_submission"])
        self.assertFalse(x["question_decision"]["field_execution_authorized"])
        self.assertTrue(x["question_decision"]["no_automatic_adoption"])
        self.assertTrue(all(not n["affects_native_decision"]
                            for n in x["chorus_advisory_notes"]))

    def test_hallucinated_sensor_refused_even_when_spelled_like_a_command(self):
        x = challenge("READ_PRIVATE_GMAIL")
        self.assertEqual(x.status, "HOLD_HALLUCINATED_TEST_ID")
        self.assertIsNone(x.challenged_plan)

    def test_injected_extra_instructions_are_not_a_test_packet(self):
        x = challenge("FOOD_SERVICE_GATE; SUBMIT_APPLICATION")
        self.assertEqual(x.status, "HOLD_UNSTRUCTURED_OR_INJECTED_CRITIQUE")
        self.assertIsNone(x.proposed_test)

    def test_model_cannot_nominate_human_contacts_to_autonomously_execute(self):
        x = challenge("HUMAN_FOOD_CONFIRMATION")
        self.assertEqual(x.status, "HOLD_HUMAN_AUTHORITY_REQUIRED")
        self.assertFalse(x.field_execution_authorized)

    def test_duplicate_source_and_partition_not_reintroduced(self):
        x = challenge("REPEAT_AUDIO_TEST")
        self.assertEqual(x.status, "HOLD_DUPLICATE_OR_EXISTING_QUESTION")

    def test_noninformative_inquiry_does_not_create_a_self_loop(self):
        x = challenge("NONINFORMATIVE_CHECK")
        self.assertEqual(x.status, "HOLD_TEST_NOT_CHOSEN_BY_NATIVE_PLANNER")
        self.assertEqual(x.challenged_plan.selected, ("AUDIO_PATH_TEST",))

    def test_separately_refuted_cheap_test_does_not_reenter_forest(self):
        x = challenge("BAD_FOOD_TEST")
        self.assertEqual(x.status, "REFUSE_CALIBRATION_FALSIFIED")
        self.assertTrue(any(v.startswith("COUNTEREXAMPLE")
                            for v in x.review_errors))
        self.assertIsNone(x.challenged_plan)

    def test_source_says_slow_test_and_delay_is_costly_without_units_bridge(self):
        x = challenge("SLOW_FOOD_TEST", cost_of_wait_if_delayed=5.)
        self.assertEqual(x.status, "HOLD_DELAY_INFORMATION_TRADEOFF_UNCALIBRATED")
        self.assertIsNone(x.challenged_plan)

    def test_source_says_slow_test_but_modelled_cost_of_wait_zero(self):
        x = challenge("SLOW_FOOD_TEST", cost_of_wait_if_delayed=0.)
        self.assertEqual(x.status, "ELIGIBLE_SYNTHETIC_REPLAN_ONLY")

    def test_repeating_a_question_cannot_gain_new_authority(self):
        hyp, roads, catalog, projection, chorus, reviews = fixture()
        ledger = QuestionLedger()
        a = submit_critic_question(chorus, projection, hyp, roads,
                                   catalog, reviews, ledger)
        b = submit_critic_question(chorus, projection, hyp, roads,
                                   catalog, reviews, ledger)
        self.assertEqual(a.status, "ELIGIBLE_SYNTHETIC_REPLAN_ONLY")
        self.assertEqual(b.status, "HOLD_REPEATED_QUESTION_LOOP")
        self.assertEqual(len(ledger.seen), 1)

    def test_bounded_question_attempts_including_hallucinations(self):
        hyp, roads, catalog, projection, chorus, reviews = fixture("INVALID_ONE")
        ledger = QuestionLedger(max_attempts=1)
        first = submit_critic_question(chorus, projection, hyp, roads,
                                       catalog, reviews, ledger)
        self.assertEqual(first.status, "HOLD_HALLUCINATED_TEST_ID")
        _, _, _, _, another, _ = fixture("FOOD_SERVICE_GATE")
        second = submit_critic_question(another, projection, hyp, roads,
                                        catalog, reviews, ledger)
        self.assertEqual(second.status, "HOLD_RESEARCH_ATTEMPT_LIMIT")

    def test_stale_or_tampered_critic_note_is_held(self):
        hyp, roads, catalog, projection, chorus, reviews = fixture()
        notes = tuple(
            replace(n, snapshot_sha256="fake") if n.role == "CRITIC" else n
            for n in chorus.notes
        )
        mutated = replace(chorus, notes=notes)
        x = submit_critic_question(mutated, projection, hyp, roads,
                                   catalog, reviews, QuestionLedger())
        self.assertEqual(x.status, "HOLD_STALE_OR_UNTRUSTED_CRITIC_NOTE")
        self.assertIsNone(x.challenged_plan)

    def test_no_calibration_does_not_let_linguistic_confidence_substitute(self):
        hyp, roads, catalog, projection, chorus, reviews = fixture()
        x = submit_critic_question(
            chorus, projection, hyp, roads, catalog, {},
            QuestionLedger(),
        )
        self.assertEqual(x.status, "HOLD_INSUFFICIENT_CALIBRATION")
        self.assertIsNone(x.challenged_plan)

    def test_duplicate_phase_source_cost_and_false_real_authentication_refuse(self):
        hyp, roads, catalog, projection, chorus, reviews = fixture()
        test = catalog[0]
        clean = list(reviews["FOOD_SERVICE_GATE"])
        clean[1] = replace(clean[1], case_id=clean[0].case_id,
                           source="WRONG_SOURCE", phase="RUN",
                           cost=4, authenticated_real_world=True)
        status, errors = validate_review(test, clean, [h.name for h in hyp])
        self.assertEqual(status, "REFUSE_CALIBRATION_FALSIFIED")
        for prefix in ("DUPLICATE_CASE", "SOURCE_MISMATCH",
                       "PHASE_MISMATCH", "FALSE_REAL_AUTHENTICATION",
                       "COST_MISMATCH"):
            self.assertTrue(any(e.startswith(prefix) for e in errors), prefix)

    def test_calibration_pass_can_still_fail_when_source_drifts(self):
        x = scenario(proposed="DRIFT_FOOD_TEST", hidden="11")
        self.assertEqual(x["question_decision"]["status"],
                         "ELIGIBLE_SYNTHETIC_REPLAN_ONLY")
        observed = x["independent_synthetic_run"]
        self.assertFalse(observed["model_correct"])
        self.assertEqual(observed["final_answer"], "A1_M0")
        self.assertEqual(observed["true_answer_for_scoring_only"], "A1_M1")
        # In-grammar lies cannot be exposed by this simple exact model.
        self.assertEqual(observed["counterexamples"], [])

    def test_out_of_grammar_source_observation_creates_a_scar(self):
        hyp, roads, catalog, projection, chorus, reviews = fixture()
        test = catalog[0]
        approved = replace(test.road, allowed=True)
        forest = LivingForest(hyp, (*roads, approved), budget=.65,
                              rounds=1, max_parallel=2)
        plan, step = forest.run_synthetic_round(
            lambda road: "UNMODELED_OUTCOME" if road.name == approved.name
                         else SealedSyntheticOracle._raw("10",road.name,"RUN")
        )
        self.assertIn(approved.name, plan.selected)
        self.assertEqual(forest.state, "HOLD_MODEL_FALSIFIED")
        self.assertTrue(forest.counterexamples)
        self.assertEqual(forest.counterexamples[0]["reason"],
                         "NO_EXISTING_HYPOTHESIS_PREDICTS_JOINT_RESULT")

    def test_no_external_tool_or_real_life_contact_after_clean_run(self):
        x = scenario()
        self.assertTrue(x["terminated_without_requerying_itself"])
        self.assertEqual(x["loop_limit"], 2)
        self.assertEqual(x["questions_that_require_humans"],
                         "HELD_FOR_REAL_OWNER_APPROVAL")
        self.assertFalse(x["question_decision"]["real_source_authenticated"])
        self.assertEqual(x["independent_synthetic_run"]["post_observation_status"], "ANSWER")


if __name__ == "__main__":
    unittest.main()
