"""GENIUS-006: frozen finite research-task evaluation, not autonomous invention.

The deliberately classical posterior planners all share a public hypothesis
space; the secret truth is revealed only by calling a selected question.
Validation samples are generated from distinct seeds before any future
sample world is drawn. Every claimed downstream capability is separately
checked against the target world after inquiry.
"""
from __future__ import annotations

from hashlib import sha256
import json
import random

from discovery import POLICIES, Planner, episode, scenario

FAMILIES = ("CHAIN", "DEEP_CHAIN", "PARALLEL", "NOISE_USEFUL", "SPARSE", "MIXED")
VALIDATION_SEEDS = (60601, 60602)
FUTURE_SEEDS = (60631, 60632, 60633)
TRAIN_SAMPLES_PER_SEED = 20
FUTURE_SAMPLES_PER_SEED = 32
CANDIDATES = ("ENTROPY", "DIVERSITY", "MYOPIC_GAIN", "AFFORDANCE_2")
# Complexity penalty is engineer-authored and cannot make comparisons
# to exact classical DP fairer than the full finite problem itself.
COMPLEXITY_PENALTY = {
    "ENTROPY": 0.0,
    "DIVERSITY": 0.0,
    "MYOPIC_GAIN": 0.01,
    "AFFORDANCE_2": 0.05,
}


def public_sample_indices(seed: int, family: str, count: int, universe: int) -> list[int]:
    if count <= 0 or count > universe:
        raise ValueError("Finite sample size is invalid")
    rng = random.Random(seed * 1013 + 17 * FAMILIES.index(family))
    return rng.sample(range(universe), count)


def run_policy(planner: Planner, indices: list[int], policy: str) -> dict:
    outcomes = [episode(planner, planner.worlds[i], policy) for i in indices]
    return {
        "policy": policy,
        "evaluated": len(outcomes),
        "mean_verified_value": round(
            sum(o["verified_capability_value"] for o in outcomes) / len(outcomes), 6),
        "mean_verified_capability_count": round(
            sum(o["verified_capability_count"] for o in outcomes) / len(outcomes), 6),
        "mean_questions": round(
            sum(o["question_count"] for o in outcomes) / len(outcomes), 6),
        "false_certificates": 0,  # Independent verifier raises before reaching here.
        "no_external_action": all(o["no_real_world_action"] for o in outcomes),
    }


def trial() -> dict:
    planners = {family: Planner(scenario(family)) for family in FAMILIES}
    frozen = {}
    baseline_value = {}
    for family in FAMILIES:
        planner = planners[family]
        validation = [
            i for seed in VALIDATION_SEEDS
            for i in public_sample_indices(seed, family, TRAIN_SAMPLES_PER_SEED,
                                           len(planner.worlds))
        ]
        scores = {arm: run_policy(planner, validation, arm) for arm in CANDIDATES}
        selected = min(
            CANDIDATES,
            key=lambda arm: (
                -scores[arm]["mean_verified_value"] + COMPLEXITY_PENALTY[arm],
                CANDIDATES.index(arm),
            ),
        )
        # POST-HOC CAUTION: this guard was introduced AFTER reviewing the
        # first heldout DEEP_CHAIN counterexample. It is a conservative
        # engineering response, not a prespecified generalization result.
        exact_validation = run_policy(planner, validation, "EXACT_BELLMAN")
        margin = 0.05
        acceptable = (
            scores[selected]["mean_verified_value"] >=
            exact_validation["mean_verified_value"] - margin
        )
        frozen[family] = {
            "selected_method": selected,
            "training_only_scores": scores,
            "strong_exact_validation_score": exact_validation,
            "candidate_within_005_of_exact_validation": acceptable,
            "research_adoption_status": (
                "RESEARCH_ONLY_NEEDS_EXTERNAL_REVIEW" if acceptable
                else "HOLD_NO_PROMOTION_FALLBACK_CLASSICAL"
            ),
            "recommended_nonexecuting_method": (
                selected if acceptable else "EXACT_BELLMAN"
            ),
            "posthoc_guard_provenance": (
                "INTRODUCED_AFTER_FIRST_TEST_INSPECTION_NO_BLIND_CLAIM"
            ),
            "selection_objective": "maximize mean verified downstream value - fixed complexity penalty",
        }
        baseline_value[family] = round(planner.exact_value(planner.root, (),
                                                         planner.task.budget), 6)

    # SHA binds the selected policies and comparator contract before future
    # sampling. It is NOT a cryptographic independent preregistration.
    freeze_packet = {
        "families": FAMILIES,
        "budgets": {family: planners[family].task.budget for family in FAMILIES},
        "validation_seeds": VALIDATION_SEEDS,
        "future_seeds": FUTURE_SEEDS,
        "future_samples_per_seed": FUTURE_SAMPLES_PER_SEED,
        "candidate_policy_choices": CANDIDATES,
        "penalties": COMPLEXITY_PENALTY,
        "frozen_selectors": frozen,
        "strong_exact_bellman_expected_values": baseline_value,
    }
    digest = sha256(json.dumps(freeze_packet, sort_keys=True).encode()).hexdigest()
    futures = {}
    demonstrations = []
    for family in FAMILIES:
        planner = planners[family]
        indices = [
            i for seed in FUTURE_SEEDS
            for i in public_sample_indices(seed, family, FUTURE_SAMPLES_PER_SEED,
                                           len(planner.worlds))
        ]
        selected = frozen[family]["selected_method"]
        rows = {arm: run_policy(planner, indices, arm) for arm in POLICIES}
        selected_result = rows[selected]
        rows["TRAINING_SELECTED"] = dict(selected_result, policy=selected,
                                         selected_before_future=True)
        conservative = frozen[family]["recommended_nonexecuting_method"]
        rows["POSTHOC_GUARDED_RESEARCH_RECOMMENDATION"] = dict(
            rows[conservative], policy=conservative,
            posthoc_guard_not_fresh_blind_test=True,
            no_method_promoted_or_deployed=True,
        )
        futures[family] = {
            "evaluation": rows,
            "exact_uniform_prior_expected_value": baseline_value[family],
            "measured_sample_regret_vs_exact": round(
                rows["EXACT_BELLMAN"]["mean_verified_value"] -
                selected_result["mean_verified_value"], 6),
            "exact_dp_memo_states": planner.exact_value.cache_info().currsize,
        }
        # One explicitly synthetic, source-attributed demonstration per
        # task type (no real people's data and no live actions).
        example = episode(planner, planner.worlds[indices[0]], selected)
        demonstrations.append({
            "family": family,
            "method_selected_on_validation": selected,
            "trace": example["trace"],
            "certificates": example["certificates"],
            "verified_value": example["verified_capability_value"],
        })
    return {
        "status": "RESEARCH_HOLD_ENGINEER_AUTHORED",
        "experiment": "MOTIF-GENIUS-006",
        "objective": "verified weighted downstream capabilities per bounded research questions",
        "frozen_sha256_before_test_sampling": digest,
        "selection": frozen,
        "future": futures,
        "synthetic_examples": demonstrations,
        "classical_optimality_scope": "EXACT_BELLMAN is optimal only for the published finite uniform prior, fixed budget and engineered reward",
        "nonclaims": [
            "No novel mathematics or autonomous invention of a general research algorithm",
            "No externally authored/blind challenge or independent real-world capability",
            "No real action, human modeling, Trench app, or MCP integration",
            "No generalized adaptive-submodularity or approximation guarantee",
        ],
        "no_external_action": True,
    }


if __name__ == "__main__":
    print(json.dumps(trial(), indent=2, sort_keys=True))
