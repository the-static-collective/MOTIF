"""MOTIF-019F: live *synthetic* action receipts, model edits and replanning.

This is a local simulation. Nothing here invokes an actuator, connected app,
human, or permission. The hidden intervention model is evaluator-only.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
from math import inf
from typing import FrozenSet, Mapping

from classical import (
    MethodCartridge, Operator, Task, develop_methods, find_plan, verify_plan
)
from engine import GuardProposal, fixture_cases, propose_guard, sample_clue


@dataclass(frozen=True)
class ActionReceipt:
    serial: int
    name: str
    attempted_cost: float
    before: tuple[str, ...]
    after: tuple[str, ...]
    success: bool
    observed_status: str
    provenance: str = "INDEPENDENT_SYNTHETIC_ACTUATOR"


@dataclass(frozen=True)
class ModelStep:
    revision: int
    chosen_method: str
    generated_method: dict
    candidate_plan: tuple[str, ...]
    predicted_model_cost: float
    action_receipt: ActionReceipt
    generated_guard: str | None
    question_gate_status: str | None
    unexpected: bool


class SyntheticWorld:
    """Hidden source of applied action effects; not passed to planner methods."""

    def __init__(self, state: FrozenSet[str],
                 additional_guards: Mapping[str, FrozenSet[str]]):
        self.state = state
        self.additional_guards = dict(additional_guards)
        self.serial = 0

    def attempt(self, action: Operator) -> ActionReceipt:
        before = self.state
        self.serial += 1
        applicable = (action.pre | self.additional_guards.get(action.name, frozenset())) <= before
        if applicable:
            self.state = action.apply(before)
        return ActionReceipt(
            serial=self.serial, name=action.name,
            attempted_cost=action.cost,
            before=tuple(sorted(before)),
            after=tuple(sorted(self.state)),
            success=applicable,
            observed_status="APPLIED" if applicable else "REPORTED_NOT_APPLIED",
        )


def base_problem():
    ops = (
        Operator("open_gate", frozenset({"outside", "parcel"}),
                 frozenset({"inside"}), frozenset({"outside"}), 1.),
        Operator("collect_token", frozenset({"outside"}),
                 frozenset({"token"}), cost=1.),
        Operator("detour", frozenset({"outside", "parcel"}),
                 frozenset({"inside"}), frozenset({"outside"}), 5.),
        Operator("deliver", frozenset({"inside", "parcel"}),
                 frozenset({"delivered"}), cost=1.),
    )
    return Task(frozenset({"outside", "parcel"}), frozenset({"delivered"}), ops)


def weighted_problem():
    return Task(
        frozenset({"start"}), frozenset({"done"}), (
            Operator("a_direct", frozenset({"start"}), frozenset({"done"}), cost=7.),
            Operator("b_collect", frozenset({"start"}), frozenset({"material"}), cost=1.),
            Operator("c_finish", frozenset({"material"}), frozenset({"done"}), cost=1.),
        )
    )


def run_online(world_kind="TOKEN", method="FOUNDRY", *,
               source_complete=True, max_steps=9) -> dict:
    """Dynamically generate classical methods & guards from actual receipts.

    Fixed validation cases are available to the hypothesis learner, not the
    oracle's hidden action precondition. In the shifted world they mislead it.
    """
    if world_kind not in {"TOKEN", "SHIFT_BADGE"} or method not in {"FOUNDRY", "UCS_ONLY"}:
        raise ValueError("Invalid synthetic world or classical method")
    task = base_problem()
    hard_guard = frozenset({"token"}) if world_kind == "TOKEN" else frozenset({"badge"})
    oracle = SyntheticWorld(task.facts, {"open_gate": hard_guard})
    training, discovery, review = fixture_cases()
    record = []
    history: list[ModelStep] = []
    spent = 0.0
    extra_inquiry_cost = 0.0
    guard_attempted = False
    rejections = []
    issue: GuardProposal | None = None
    method_versions = set()
    for _ in range(max_steps):
        if task.goal <= oracle.state:
            break
        task = replace(task, facts=oracle.state)
        foundry = develop_methods(task, budget_expansions=2000)
        if method == "FOUNDRY" and foundry.chosen is not None:
            algorithm = foundry.chosen.algorithm
            selected_method = foundry.chosen
        else:
            algorithm = "UCS"
            selected_method = next((x for x in foundry.candidates if x.algorithm == "UCS"), None)
        plan = find_plan(task, algorithm, max_expanded=2000)
        if plan.status != "PLAN" or not plan.actions:
            rejections.append("HOLD_NO_VERIFIED_PLAN")
            break
        valid, cost = verify_plan(task, plan.actions)
        if not valid or abs(cost - plan.cost) > 1e-9:
            rejections.append("HOLD_UNSOUND_CLASSICAL_PLAN")
            break
        action = next(o for o in task.operators if o.name == plan.actions[0])
        receipt = oracle.attempt(action)
        spent += receipt.attempted_cost
        fresh_guard = None
        gate_status = None
        if not receipt.success:
            if action.name == "open_gate" and not guard_attempted:
                guard_attempted = True
                issue = propose_guard(
                    action.name, training, discovery, review,
                    sample_clue(include_source=source_complete)
                )
                gate_status = issue.status
                if issue.status == "ELIGIBLE_MODEL_GUARD_ONLY" and issue.feature is not None:
                    guard = issue.feature.guard_fact
                    # The graph relation is not sufficient to conjure a new
                    # physical ability. Require an already modeled producer.
                    if any(guard in op.add for op in task.operators):
                        task = task.replace_guard(action.name, guard)
                        fresh_guard = guard
                        extra_inquiry_cost += issue.feature.probe_cost
                    else:
                        rejections.append("HOLD_NO_MODELED_PRODUCER_OF_NEW_GUARD")
                else:
                    rejections.append(gate_status)
            if fresh_guard is None:
                # Failed method remains falsified for this world. Never retry
                # an unsupported action indefinitely; take the known detour.
                task = replace(
                    task, version=task.version + 1,
                    operators=tuple(o for o in task.operators if o.name != action.name),
                )
                if action.name == "open_gate" and guard_attempted:
                    rejections.append("HOLD_UNEXPLAINED_OR_CHANGED_CAUSE")
        if selected_method is not None:
            model_receipt = asdict(selected_method)
            method_versions.add((selected_method.algorithm, selected_method.model_version))
        else:
            model_receipt = {"status": "NO_REVIEWABLE_METHOD"}
        history.append(ModelStep(
            revision=task.version, chosen_method=algorithm,
            generated_method=model_receipt,
            candidate_plan=plan.actions,
            predicted_model_cost=plan.cost,
            action_receipt=receipt,
            generated_guard=fresh_guard,
            question_gate_status=gate_status,
            unexpected=not receipt.success,
        ))
    return {
        "status": "DELIVERED" if task.goal <= oracle.state else "HOLD_UNFINISHED",
        "world_family": world_kind,
        "requested_method": method,
        "true_world_rule_known_to_evaluator_only": str(sorted(hard_guard)),
        "total_attempted_action_cost": round(spent, 6),
        "inquiry_cost": round(extra_inquiry_cost, 6),
        "total_cost": round(spent + extra_inquiry_cost, 6),
        "method_versions_generated": len(method_versions),
        "final_model_version": task.version,
        "learned_guard": issue.feature.guard_fact if issue and issue.feature else None,
        "learned_guard_status": issue.status if issue else None,
        "native_question_source_blob": issue.native_question_blob if issue else None,
        "native_dogram_source_blob": issue.native_dogram_blob if issue else None,
        "refuted_rivals": issue.rejected_rivals if issue else (),
        "failures_retained": tuple(rejections),
        "receipts": [asdict(step) for step in history],
        "outside_world_authority": False,
        "automatically_deployed_new_code": False,
    }


def static_fallback(world_kind="TOKEN") -> dict:
    """Existing strong *fixed-route* baseline, no question-learning.

    First tries its cheapest modeled gate, then takes its known detour after
    failure. Not the exact classical adaptive diagnostic with same evidence.
    """
    task = base_problem()
    hard = frozenset({"token"}) if world_kind == "TOKEN" else frozenset({"badge"})
    world = SyntheticWorld(task.facts, {"open_gate": hard})
    sequence = ("open_gate", "detour", "deliver")
    receipts = []
    for step in sequence:
        operator = next(op for op in task.operators if op.name == step)
        receipts.append(world.attempt(operator))
    return {
        "delivered": task.goal <= world.state,
        "total_cost": sum(x.attempted_cost for x in receipts),
        "receipt_status": [x.observed_status for x in receipts],
    }
