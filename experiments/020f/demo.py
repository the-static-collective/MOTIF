"""Inspect a real planZ index and a SEPARATE invented urgency experiment.

PlanZ has no verified deadlines or approvals in the public attention index.
Synthetic numbers below DO NOT describe actual organizations or emergencies.
"""
from __future__ import annotations
from dataclasses import asdict
import json

from insideout import CounterfactualOpportunity, InsideOutBox, scope_only
from planz import read_planz_snapshot


def fixture():
    # Real public plan identifiers, but these values/deadlines are invented
    # for a controlled experiment only. All source-owner gates remain on HOLD.
    return (
        CounterfactualOpportunity(
            "SHELF-001", reward_if_successful=6, last_start_tick=0,
            attention_units=1, actor_effects=(("recipient-synthetic", 6.0),)),
        CounterfactualOpportunity(
            "GARDEN-TABLE-001", reward_if_successful=8, last_start_tick=2,
            attention_units=1, actor_effects=(("recipient-synthetic", 8.0),)),
    )


def scenario():
    snapshot = read_planz_snapshot()
    timeline = InsideOutBox(snapshot, fixture(),
                            horizon=3, attention_budget=2,
                            max_parallel=1, cognition_cost_per_tick=.05).analyze()
    return {
        "origin": "planZ public INDEX_ONLY attention, checked by original validator",
        "snapshot": {
            "edition": snapshot.edition,
            "reviewed_on": snapshot.reviewed_on,
            "feed_blob": snapshot.git_blob,
            "validator_blob": snapshot.planz_validator_git_blob,
            "entries": len(snapshot.plans),
        },
        "real_world": scope_only(snapshot),
        "source_pointers": [
            {
                "id": snapshot.get(x.plan_id).id,
                "owner_source": snapshot.get(x.plan_id).source,
                "next_human_gate": snapshot.get(x.plan_id).next_gate,
                "source_blockers": snapshot.get(x.plan_id).blocked_by,
                "source_execution_allowed": snapshot.get(x.plan_id).execution_allowed,
                "source_deadline": "UNKNOWN_NOT_IN_PUBLIC_INDEX",
            } for x in fixture()
        ],
        "toy_assumptions": [asdict(x) for x in fixture()],
        "cost_of_inaction_experiment": asdict(timeline),
        "strong_classical_comparator": {
            "method": "FINITE_HORIZON_DP_ON_SAME_DECLARED_WORLD",
            "value": timeline.optimal_modeled_value,
            "ties": True,
            "planner_superiority_claimed": False,
        },
        "dispatched": False,
        "participant_or_source_owner_contacted": False,
    }


if __name__ == "__main__":
    print(json.dumps(scenario(), indent=2, sort_keys=True))
