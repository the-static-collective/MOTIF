"""GENIUS-007: task-renamed, goal-composition benchmark.

PUBLIC goal and instrument contracts are generated without the hidden
target-world bits. Validation and future task seeds are disjoint; every
32-world target outcome per task is exhaustively checked. This is still
one engineer-authored generator, not a blind external source.

Crucially, DIRECT_OPTIMAL is a strong exact classical comparator on direct
sensors. FOUNDRY_OPTIMAL is the stronger exact classical upper bound on
the *same synthesized instrument action space* as all foundry policies.
"""
from __future__ import annotations

from hashlib import sha256
import json
import random

from foundry import (
    Capability, Instrument, Literal, Planner, POLICIES, Task,
    run_episode,
)

FAMILIES = (
    "PAIRABLE", "TRIPLE", "MIXED_POLARITY", "MULTIGOAL",
    "NO_PAIR", "EXPENSIVE_PAIR", "DISTRACTOR",
)
VALIDATION_SEEDS = (70701, 70702)
FUTURE_SEEDS = (70731, 70732, 70733)
SELECTABLE = ("FOUNDRY_ENTROPY", "FOUNDRY_GREEDY", "FOUNDRY_LOOKAHEAD2")


def task_for(seed: int, family: str) -> Task:
    if family not in FAMILIES:
        raise ValueError("Unknown experiment family")
    rng = random.Random(seed * 991 + FAMILIES.index(family) * 109)
    # No specific names in the query synthesis algorithm. Every new task
    # uses its own unseen symbolic vocabulary.
    suffix = f"{seed:x}{FAMILIES.index(family):x}"
    variables = tuple(f"{t}_{suffix}" for t in
                      ("cedar", "river", "copper", "bridge", "ash"))
    rng.shuffle_names = None if False else None  # no effect on test data
    values = [rng.randint(0, 1) for _ in range(5)]
    def lit(i):
        return Literal(variables[i], values[i])
    reward = rng.randint(7, 12)
    caps = {
        "PAIRABLE": (Capability("safe_pair", (lit(0), lit(1)), reward),),
        "TRIPLE": (Capability("three_inputs",
                              (lit(0), lit(1), lit(2)), reward),),
        "MIXED_POLARITY": (Capability("opposed_states",
                                    (Literal(variables[0], 0),
                                     Literal(variables[1], 1)), reward),),
        "MULTIGOAL": (
            Capability("first_goal", (lit(0), lit(1)), reward),
            Capability("second_goal", (lit(2), lit(3)), reward),
        ),
        "NO_PAIR": (Capability("no_joint_assay", (lit(0), lit(1)), reward),),
        "EXPENSIVE_PAIR": (
            Capability("paired_probe_not_cost_effective",
                       (lit(0), lit(1)), reward),),
        "DISTRACTOR": (
            Capability("targeted_relevance", (lit(3), lit(4)), reward),),
    }[family]
    instrument = Instrument(
        sensor_variables=variables,
        direct_cost=2,
        pair_cost=5 if family == "EXPENSIVE_PAIR" else 3,
        can_pair=family != "NO_PAIR",
        source_ref=f"synthetic:pair-assay-contract/{family}/{seed}",
    )
    budget = {
        "PAIRABLE": 3, "TRIPLE": 5, "MIXED_POLARITY": 3,
        "MULTIGOAL": 6, "NO_PAIR": 4,
        "EXPENSIVE_PAIR": 4, "DISTRACTOR": 3,
    }[family]
    return Task(
        name=f"{family.lower()}_unseen_symbols_{seed}",
        instrument=instrument, capabilities=caps, budget=budget,
    )


def assess(task: Task) -> dict:
    p = Planner(task)
    rows = {}
    for policy in POLICIES:
        episodes = [run_episode(p, world, policy) for world in p.worlds]
        mean = sum(row["verified_reward"] for row in episodes) / len(episodes)
        rows[policy] = {
            "mean_verified_reward": round(mean, 6),
            "mean_verified_capability_count": round(
                sum(len(row["verified_capabilities"]) for row in episodes)
                / len(episodes), 6),
            "mean_measurement_cost": round(
                sum(row["total_measurement_cost"] for row in episodes)
                / len(episodes), 6),
            "synthesized_question_episodes": sum(
                row["synthesized_question_count"] > 0 for row in episodes),
            "invalid_certificates": 0,  # separate validator raises on false claim
            "evaluated_worlds": len(episodes),
        }
    expected_optimum = p.bellman(p.root, task.budget, True, -1)
    direct_expected_optimum = p.bellman(p.root, task.budget, False, -1)
    # Exhaustive empirical mean, not sample approximation: we evaluated
    # every possible world in the defined uniform finite hypothesis space.
    if abs(rows["FOUNDRY_OPTIMAL"]["mean_verified_reward"] - expected_optimum) > 1e-5:
        raise AssertionError("Bellman operator fails exhaustive independent check")
    if abs(rows["DIRECT_OPTIMAL"]["mean_verified_reward"] - direct_expected_optimum) > 1e-5:
        raise AssertionError("Direct Bellman operator fails exhaustive check")
    if rows["FOUNDRY_OPTIMAL"]["mean_verified_reward"] + 1e-5 < (
        max(r["mean_verified_reward"] for r in rows.values())):
        raise AssertionError("Classical full action-space optimum was surpassed")
    return {
        "task": task.name,
        "pair_instrument_available": task.instrument.can_pair,
        "pair_cost": task.instrument.pair_cost,
        "direct_cost": task.instrument.direct_cost,
        "budget": task.budget,
        "goal_caps": [{
            "name": c.name, "reward": c.reward,
            "prerequisites": [(x.variable, x.equals) for x in c.prerequisites],
        } for c in task.capabilities],
        "question_candidates_direct": len(p.direct),
        "question_candidates_with_composition": len(p.forge),
        "full_prior_exact_optimum": round(expected_optimum, 6),
        "full_prior_direct_only_optimum": round(direct_expected_optimum, 6),
        "memoized_classical_dp_states": p.bellman.cache_info().currsize,
        "arms": rows,
        "no_external_action": True,
    }


def mean_policy(task_results: list[dict], method: str) -> float:
    return round(sum(row["arms"][method]["mean_verified_reward"]
                     for row in task_results) / len(task_results), 6)


def trial() -> dict:
    # All methods' high-level policies are fixed before any test tasks are
    # generated. Nothing learns hidden target bits or invents physical assays.
    validation = {
        family: [assess(task_for(seed, family)) for seed in VALIDATION_SEEDS]
        for family in FAMILIES
    }
    selected = {
        family: min(
            SELECTABLE,
            key=lambda method: (
                -mean_policy(rows, method),
                SELECTABLE.index(method),
            ),
        )
        for family, rows in validation.items()
    }
    validation_scores = {
        family: {arm: mean_policy(rows, arm)
                 for arm in POLICIES}
        for family, rows in validation.items()
    }
    freeze_packet = {
        "selected": selected,
        "validation_scores": validation_scores,
        "validation_seeds": VALIDATION_SEEDS,
        "future_seeds": FUTURE_SEEDS,
        "families": FAMILIES,
        "policy_grammar": POLICIES,
        "assay_costs": "direct=2, pair=3 except expensive_pair=5",
        "reward": "sum independently certified positive goal capabilities",
        "prior": "uniform every 5-bit world",
    }
    digest = sha256(json.dumps(freeze_packet, sort_keys=True).encode()).hexdigest()

    # The next task contracts use different vocabulary suffixes and random
    # prerequisite polarities/goal rewards. Same authored task *families*:
    # do not call this an externally authored cross-domain generalization.
    futures = {}
    proof_examples = []
    for family in FAMILIES:
        tasks = [assess(task_for(seed, family)) for seed in FUTURE_SEEDS]
        mean_results = {
            arm: mean_policy(tasks, arm) for arm in POLICIES
        }
        chosen = selected[family]
        futures[family] = {
            "validation_selected": chosen,
            "measured_mean_verified_reward_by_arm": mean_results,
            "strong_direct_baseline": mean_results["DIRECT_OPTIMAL"],
            "strong_generated_action_space_baseline": mean_results["FOUNDRY_OPTIMAL"],
            "potential_composition_dividend_vs_direct_exact": round(
                mean_results["FOUNDRY_OPTIMAL"]-mean_results["DIRECT_OPTIMAL"], 6),
            "validation_selected_gap_to_strong_generated": round(
                mean_results["FOUNDRY_OPTIMAL"]-mean_results[chosen], 6),
            "task_receipts": tasks,
            "nonclaim": "No algorithm here beats exact classical DP over the same query operators",
        }
        p = Planner(task_for(FUTURE_SEEDS[0], family))
        target = p.worlds[-1]
        proof_examples.append({
            "family": family,
            "policy": chosen,
            "example": run_episode(p, target, chosen),
        })
    return {
        "experiment": "MOTIF-GENIUS-007",
        "status": "RESEARCH_HOLD_ENGINEER_AUTHORED_TYPED_QUERY_COMPOSITION",
        "selection_frozen_sha256_before_future_task_generation": digest,
        "validation_selected": selected,
        "validation": validation_scores,
        "test": futures,
        "example_proof_packets": proof_examples,
        "model_authorship": "ALL_GOALS_SENSOR_OPERATORS_WORLD_PROBABILITIES_AND_VERIFIERS_ENGINEER_AUTHORED",
        "nonclaims": [
            "No external or newly invented physical measurement capability",
            "No historically novel mathematics or general language-understanding method",
            "No independent third-party blind test or real-world problem solved",
            "No Trench app or MCP deployment; no real-world actions",
            "No advantage over classical exact planning given the same generated questions",
        ],
        "no_external_action": True,
    }


if __name__ == "__main__":
    print(json.dumps(trial(), indent=2, sort_keys=True))
