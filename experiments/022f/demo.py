"""MOTIF-022F: a bounded Chorus -> Question Machine -> Living Forest loop.

The default uses a scripted critic (NOT model inference) and separate
synthetic calibration + held-out RUN observations. Actual local FLAN-T5-small
may be opted into, but is never downloaded or silently promoted to authority.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import argparse
import json

from feedback import QuestionAwareBackend, QuestionLedger, submit_critic_question
from chorus import LocalFlanT5Small, parallel_critique
from forest import LivingForest
from sealed_oracle import (
    SealedSyntheticOracle, ScriptedCritic, modeled_problem, public_projection,
)


def scenario(*, proposed="FOOD_SERVICE_GATE", hidden="10",
             actual_t5=False, sidecar_grace=.5,
             hypothetical_delay_loss=0.0) -> dict:
    hypotheses, original_roads, catalog = modeled_problem()
    projection = public_projection()
    backend = LocalFlanT5Small() if actual_t5 else ScriptedCritic(proposed)
    chorus = parallel_critique(
        lambda: LivingForest(hypotheses, original_roads,
                             budget=.65, rounds=1, max_parallel=2).plan(),
        projection, QuestionAwareBackend(backend, catalog),
        sidecar_grace_seconds=sidecar_grace,
    )

    # Independent evaluator owns all calibration, not the text model.
    # The model only nominates one catalog ID, and cannot write or edit
    # the synthetic observation receipts.
    calibration = {
        item.road.name: SealedSyntheticOracle.calibration(item)
        for item in catalog
    }
    ledger = QuestionLedger()
    decision = submit_critic_question(
        chorus, projection, hypotheses, original_roads,
        catalog, calibration, ledger,
        budget=.65, cost_of_wait_if_delayed=hypothetical_delay_loss,
    )

    witnessed = None
    matched_optimal = None
    actual = None
    if decision.status == "ELIGIBLE_SYNTHETIC_REPLAN_ONLY":
        test = next(item for item in catalog if item.road.name == decision.proposed_test)
        admitted = replace(test.road, allowed=True)
        # The classic exact comparator gets precisely the same model and
        # registered reviewed probe; it is expected to tie (not lose).
        exact = LivingForest(hypotheses, (*original_roads, admitted),
                             budget=.65, rounds=1, max_parallel=2)
        matched_optimal = asdict(exact.plan())
        evaluator = SealedSyntheticOracle(hidden)
        before, after = exact.run_synthetic_round(evaluator.execute)
        witnessed = {
            "planned_portfolio": before.selected,
            "independently_reported_synthetic_probes": evaluator.executed,
            "actual_model_evidence": asdict(after) if after else None,
            "posterior": exact.live,
            "post_observation_status": exact.state,
            "final_answer": exact.plan().tentative_answer,
            "true_answer_for_scoring_only": next(
                h.answer for h in hypotheses if h.name == hidden
            ),
            "model_correct": exact.plan().tentative_answer ==
                             next(h.answer for h in hypotheses if h.name == hidden),
            "counterexamples": exact.counterexamples,
        }
        actual = exact.state

    return {
        "schema": "motif022f.critic-question-feedback/v0",
        "primary_native_plan_before_critique": asdict(chorus.native),
        "chorus_backend": backend.name,
        "actual_T5_executed": actual_t5 and
            any(n.role == "CRITIC" and n.status == "UNVERIFIED_TEXT_AVAILABLE"
                for n in chorus.notes),
        "chorus_advisory_notes": [asdict(n) for n in chorus.notes],
        "question_decision": asdict(decision),
        "matched_classical_planner_same_admitted_test": matched_optimal,
        "independent_synthetic_run": witnessed,
        "source_permission_from_human_report": "ROOM_USE_REPORTED_GRANTED_ONLY",
        "questions_that_require_humans": "HELD_FOR_REAL_OWNER_APPROVAL",
        "real_world_deployment_or_app_submission": False,
        "loop_limit": 2,
        "terminated_without_requerying_itself": True,
        "caveat": (
            "The default critic is scripted, not FLAN-T5 inference. "
            "A typed question may enter a sandbox Forest only after independent "
            "synthetic checks; all actual field owner permissions are still "
            "separate. No calibrated improvement in real-world outcomes."
        ),
    }


if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("--test-id", default="FOOD_SERVICE_GATE",
                      help="Only used by the deterministic simulated critic")
    argp.add_argument("--hidden-world", default="10",
                      help="Synthetic evaluator fixture, never sent to critic")
    argp.add_argument("--local-t5", action="store_true",
                      help="Optional existing local-only FLAN-T5-small cache")
    argp.add_argument("--grace", type=float, default=.5)
    args = argp.parse_args()
    print(json.dumps(scenario(
        proposed=args.test_id, hidden=args.hidden_world,
        actual_t5=args.local_t5, sidecar_grace=args.grace,
    ), indent=2, sort_keys=True))
