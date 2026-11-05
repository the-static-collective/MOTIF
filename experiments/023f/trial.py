"""MOTIF-023F: REAL tiny-model critic nomination benchmark.

No scripted MODEL scores. The two other Chorus roles are openly scripted to
save CPU during this critic-specific benchmark. The critic is real T5,
with (A) unrestricted text2text and (B) token-constrained registered-ID
decoding. Both modes enter the *same* 022F gate and real 016 Forest.

Synthetic calibration and hidden RUN responses remain evaluator-owned.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for folder in ("021f", "022f", "016"):
    sys.path.append(str(ROOT / folder))

from chorus import LocalFlanT5Small, SidecarNote, SidecarRun, parallel_critique
from feedback import QuestionAwareBackend, QuestionLedger, submit_critic_question
from forest import LivingForest
from model_backend import NO_TEST, RealT5Critic
from cases import CASES, inputs
from sealed_oracle import SealedSyntheticOracle


def reference_challenge(case, name, native, projection,
                        hypotheses, roads, catalog, reviews):
    """Give a deterministic classical reference exactly the candidate selected."""
    note = SidecarNote(
        role="CRITIC", status="UNVERIFIED_TEXT_AVAILABLE",
        text="TEST_ID="+name,
        backend="REFERENCE_CATALOG_ENUMERATOR_NOT_A_MODEL",
        snapshot_sha256=projection.digest(),
    )
    observation = SidecarRun(
        native=native, notes=(note,),
        sidecar_completed=True, native_completed=True,
        native_wall_ms=0., end_to_end_wall_ms=0., sidecar_budget_ms=0.,
    )
    return submit_critic_question(
        observation, projection, hypotheses, roads, catalog, reviews,
        QuestionLedger(), budget=.65,
        cost_of_wait_if_delayed=case.delay_loss,
    )


def run_case(case, model, method: str):
    hypotheses, roads, catalog, reviews = inputs(case)
    projection = case.projection()
    native = LivingForest(hypotheses, roads, budget=.65,
                          rounds=1, max_parallel=2).plan()
    options = tuple(t.road.name for t in catalog)
    candidates = {
        test_id: reference_challenge(case, test_id, native, projection,
                                     hypotheses, roads, catalog, reviews)
        for test_id in options
    }
    viable = tuple(name for name, x in candidates.items()
                   if x.status == "ELIGIBLE_SYNTHETIC_REPLAN_ONLY")
    max_gain = max((
        x.challenged_expected_accuracy - native.expected_final_accuracy
        for x in candidates.values()
        if x.status == "ELIGIBLE_SYNTHETIC_REPLAN_ONLY"
    ), default=0.)
    worker = RealT5Critic(model, projection,
        tuple((x.road.name, x.label) for x in catalog),
        method=method,
    )
    chorus = parallel_critique(
        lambda: native,
        projection,
        QuestionAwareBackend(worker, catalog),
        sidecar_grace_seconds=3.,
    )
    critic = next(n for n in chorus.notes if n.role == "CRITIC")
    chosen = submit_critic_question(
        chorus, projection, hypotheses, roads, catalog, reviews,
        QuestionLedger(), budget=.65,
        cost_of_wait_if_delayed=case.delay_loss,
    )
    gain = (
        chosen.challenged_expected_accuracy - native.expected_final_accuracy
        if chosen.status == "ELIGIBLE_SYNTHETIC_REPLAN_ONLY" else 0.
    )
    model_answer = worker.reports[-1] if worker.reports else None
    actual = None
    if chosen.status == "ELIGIBLE_SYNTHETIC_REPLAN_ONLY":
        test = next(t for t in catalog if t.road.name == chosen.proposed_test)
        new_forest = LivingForest(
            hypotheses, (*roads, replace(test.road, allowed=True)),
            budget=.65, rounds=1, max_parallel=2,
        )
        oracle = SealedSyntheticOracle(case.hidden)
        plan, receipt = new_forest.run_synthetic_round(oracle.execute)
        truth = next(h.answer for h in hypotheses if h.name == case.hidden)
        after = new_forest.plan()
        actual = {
            "test_world_not_shared_with_model": case.hidden,
            "actual_evaluator_observations": oracle.executed,
            "result": after.tentative_answer,
            "ground_truth_class": truth,
            "correct": after.tentative_answer == truth,
            "model_held": new_forest.state == "HOLD_MODEL_FALSIFIED",
            "provenance_sources": receipt.evidence if receipt else (),
        }
    return {
        "id": case.id,
        "method": method,
        "choices_offered": options,
        "prior_worlds": case.worlds,
        "hidden_world_in_evaluator_only": case.hidden,
        "reference_eligible_ids": viable,
        "reference_max_accuracy_gain": round(max_gain,6),
        "baseline_accuracy": native.expected_final_accuracy,
        "critic_raw_text": critic.text,
        "critic_sidecar_status": critic.status,
        "generation_report": asdict(model_answer) if model_answer else None,
        "question_status": chosen.status,
        "proposed_id": chosen.proposed_test,
        "accuracy_gain_from_admitted_question": round(gain,6),
        "selected_from_real_model": worker.critic_calls > 0,
        "well_formed": critic.text.startswith("TEST_ID=") and
                       bool(chosen.proposed_test is not None),
        "correct_eligibility_choice": (
            (chosen.proposed_test in viable) if viable
            else chosen.status != "ELIGIBLE_SYNTHETIC_REPLAN_ONLY"
        ),
        "strictly_safe_no_new_question": chosen.status != "ELIGIBLE_SYNTHETIC_REPLAN_ONLY",
        "synthetic_execution": actual,
        "external_authority": False,
        "observer_and_hypeman_are_scripted": True,
    }


def summarize(rows):
    if not rows:
        return {}
    gold_cases = sum(bool(x["reference_eligible_ids"]) for x in rows)
    useful = sum(x["question_status"] == "ELIGIBLE_SYNTHETIC_REPLAN_ONLY" for x in rows)
    selected = sum(x["selected_from_real_model"] for x in rows)
    valid = sum(x["well_formed"] for x in rows)
    correct = sum(x["correct_eligibility_choice"] for x in rows)
    learned = sum(x["accuracy_gain_from_admitted_question"] for x in rows)
    theoretical = sum(x["reference_max_accuracy_gain"] for x in rows)
    failures = [(x["id"], x["question_status"], x["critic_raw_text"])
                for x in rows if not x["correct_eligibility_choice"]]
    return {
        "case_count": len(rows),
        "cases_with_reference_improving_test": gold_cases,
        "actually_model_generated_critic_cases": selected,
        "strict_test_id_packet_count": valid,
        "eligible_synthetic_test_nominations": useful,
        "correct_useful_or_safe_hold_rate": round(correct/len(rows),4),
        "total_synthetic_accuracy_gain": round(learned,4),
        "reference_max_total_gain_same_catalog": round(theoretical,4),
        "independent_RUN_correct_on_accepted_cases": sum(
            x["synthetic_execution"]["correct"] for x in rows
            if x["synthetic_execution"] is not None
        ),
        "independent_RUN_wrong_on_accepted_cases": sum(
            not x["synthetic_execution"]["correct"] for x in rows
            if x["synthetic_execution"] is not None
        ),
        "model_missed_or_incorrect_cases": failures,
        "real_world_action_count": 0,
    }


def controls():
    """Same independent classical ground truth; no model or invented advantage."""
    rng = random.Random(20261105)
    reports = {"ALWAYS_FOOD_TEST":[], "SEEDED_RANDOM_REGISTERED_OR_ABSTAIN":[]}
    for case in CASES:
        hypotheses, roads, catalog, reviews = inputs(case)
        projection = case.projection()
        native = LivingForest(hypotheses, roads,
                              budget=.65, rounds=1, max_parallel=2).plan()
        options = tuple(t.road.name for t in catalog)
        for baseline in reports:
            if baseline == "ALWAYS_FOOD_TEST":
                proposed = "FOOD_SERVICE_GATE"
            else:
                proposed = rng.choice(options + ("NO_TEST",))
            c = reference_challenge(case, proposed, native, projection,
                                    hypotheses, roads, catalog, reviews)
            reports[baseline].append({
                "case_id":case.id,
                "selected":proposed,
                "status":c.status,
                "expected_accuracy_gain":round(
                    (c.challenged_expected_accuracy - native.expected_final_accuracy)
                    if c.status == "ELIGIBLE_SYNTHETIC_REPLAN_ONLY" else 0., 6
                ),
            })
    return {
        k:{
            "admitted_improvement_cases":sum(
                x["status"]=="ELIGIBLE_SYNTHETIC_REPLAN_ONLY" for x in v
            ),
            "total_accuracy_gain":round(sum(x["expected_accuracy_gain"] for x in v),4),
            "selection_trace":v,
        }
        for k,v in reports.items()
    }


def benchmark(modes=("RAW_GENERATION","CONSTRAINED_IDS")):
    import torch
    torch.set_num_threads(2)
    started = time.monotonic()
    model = LocalFlanT5Small()
    load_start = time.monotonic()
    model._prepare()
    load_sec = time.monotonic() - load_start
    outputs = {}
    for method in modes:
        rows = [run_case(case, model, method) for case in CASES]
        outputs[method] = {
            "summary":summarize(rows),
            "cases":rows,
        }
    return {
        "schema":"motif023f.real-flan-t5-question-nomination/v0",
        "model_id":"google/flan-t5-small",
        "real_model_weights_loaded":True,
        "real_model_generation_or_token_logit_choice":True,
        "model_role_evaluated":"CRITIC_ONLY",
        "observer_hypeman_in_this_benchmark":"SCRIPTED_NOT_SCORED",
        "model_load_seconds":round(load_sec,3),
        "end_to_end_seconds":round(time.monotonic()-started,3),
        "torch_version":torch.__version__,
        "outputs":outputs,
        "fixed_baselines":controls(),
        "limits":{
            "all_cases_synthetic":True,
            "data_set_small_and_hand_constructed":True,
            "model_not_trained_or_fine_tuned":True,
            "no_real_welfare_valuation":True,
            "source_truth_guaranteed_after_calibration":False,
            "all_case_scores_are_conditional_to_declared_world_grammar":True,
            "matched_classical_optimum_with_same_catalog_expected_to_tie":True,
            "outside_execution_or_person_contact":False,
        },
    }


if __name__=="__main__":
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
