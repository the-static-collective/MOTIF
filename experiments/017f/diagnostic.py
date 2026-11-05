"""MOTIF-017F: make the diagnostic an inspectable, challengable policy.

A perfect-accuracy incumbent is not necessarily cost-optimal. Compare a
question-graft challenger to BOTH that incumbent and a classical refitted
optimal planner. Keep independent review separate from hidden TEST scoring.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Sequence

from grower import QuestionProposal, Review  # installs the relative 016 import path
from forest import LivingForest, Road
from multiplex import Hypothesis, best_answer
from oracle import TestWorld, measure


@dataclass(frozen=True)
class DiagnosticOutcome:
    policy: str
    world: str
    phase: str
    predicted_answer: str
    true_answer: str  # disclosed only in evaluator result
    correct: bool
    cost: float
    selected: tuple[tuple[str, ...], ...]
    holding: bool
    counterexamples: tuple[str, ...]


@dataclass(frozen=True)
class ImprovementReview:
    incumbent: str
    challenger_digest: str
    status: str
    n_cases: int
    incumbent_accuracy: float
    challenger_accuracy: float
    incumbent_mean_cost: float
    challenger_mean_cost: float
    measured_cost_gap: float
    scope: str = "FINITE_SYNTHETIC_REVIEW_ONLY"
    authority: str = "NO_AUTOMATIC_POLICY_INSTALL"


def _truth(world: str) -> str:
    return "YES" if world[1] != world[2] else "NO"


def run_policy(
    policy: str,
    hypotheses: Sequence[Hypothesis],
    roads: Sequence[Road],
    world: TestWorld,
    candidate: Road | None = None,
    proposal: QuestionProposal | None = None,
) -> DiagnosticOutcome:
    """A test driver, not part of question invention or permission granting."""
    if policy not in {"FROZEN_FIXED", "GROWN_FOREST", "CLASSICAL_EXACT_REFIT"}:
        raise ValueError("Unknown diagnostic")
    known = {road.name: road for road in roads}
    if policy == "FROZEN_FIXED":
        # Existing strong MOTIF-016 classical policy: diagnostic mode scout and
        # *both* matching ports; it remains correct on every known world.
        m = known["SCOUT"].predicted[world.name]
        selected = (("SCOUT",), (f"FAST_A_{m}", f"FAST_B_{m}"))
        a = known[f"FAST_A_{m}"].predicted[world.name]
        b = known[f"FAST_B_{m}"].predicted[world.name]
        answer = "YES" if a != b else "NO"
        cost = sum(known[name].cost for group in selected for name in group)
        return DiagnosticOutcome(policy, world.name, world.phase,
                                 answer, _truth(world.name), answer == _truth(world.name),
                                 cost, selected, False, ())
    if candidate is None or proposal is None or not candidate.allowed:
        raise ValueError("Cannot evaluate a nonadmitted synthetic question")
    # The refit baseline sees exactly the same new sensor, cost and hypotheses
    # as the grown forest. It is deliberately an identical exact optimal
    # finite-model planner under a different role. Ties are expected.
    forest = LivingForest(hypotheses, tuple(roads) + (candidate,))
    selected = []
    for _ in range(2):
        plan, step = forest.run_synthetic_round(
            lambda road: (
                measure(proposal.offer, world)
                if road.name == candidate.name else road.predicted[world.name]
            )
        )
        if step is None:
            break
        selected.append(plan.selected)
        if step.status == "HOLD_MODEL_FALSIFIED":
            break
    answer = best_answer(forest._posterior(forest.live))[0]
    holding = forest.state == "HOLD_MODEL_FALSIFIED"
    return DiagnosticOutcome(policy, world.name, world.phase,
                             answer, _truth(world.name), answer == _truth(world.name),
                             round(forest.spent, 9), tuple(selected), holding,
                             tuple(c["reason"] for c in forest.counterexamples))


def examine_room(
    hypotheses: Sequence[Hypothesis],
    roads: Sequence[Road],
    proposal: QuestionProposal,
    review: Review,
    *,
    minimum_gain: float = 0.02,
) -> ImprovementReview:
    """Independently test whether the incumbent method can be beaten.

    The output merely *invites* later independent human review. The incumbent
    is never edited, nor is the challenger deployed.
    """
    if minimum_gain < 0:
        raise ValueError("Negative gain threshold")
    if review.proposal_digest != proposal.digest or review.admissible_road is None:
        return ImprovementReview("FROZEN_FIXED", proposal.digest, "HOLD_UNVERIFIED", 0,
                                 0, 0, 0, 0, 0)
    worlds = [TestWorld(h.name, "REVIEW") for h in hypotheses]
    incumbent = [
        run_policy("FROZEN_FIXED", hypotheses, roads, w)
        for w in worlds
    ]
    challenger = [
        run_policy("GROWN_FOREST", hypotheses, roads, w,
                   review.admissible_road, proposal)
        for w in worlds
    ]
    incumbent_accuracy = mean(x.correct for x in incumbent)
    challenger_accuracy = mean(x.correct for x in challenger)
    old_cost, new_cost = mean(x.cost for x in incumbent), mean(x.cost for x in challenger)
    gap = round(old_cost - new_cost, 9)
    if (challenger_accuracy < incumbent_accuracy or any(x.holding for x in challenger)):
        status = "REFUSE_REGRESSION"
    elif gap > minimum_gain and challenger_accuracy >= incumbent_accuracy:
        status = "ELIGIBLE_FOR_EXPLICIT_LOCAL_POLICY_REVIEW"
    else:
        status = "HOLD_NO_VALIDATED_IMPROVEMENT"
    return ImprovementReview(
        "FROZEN_FIXED", proposal.digest, status, len(worlds),
        incumbent_accuracy, challenger_accuracy, round(old_cost, 9),
        round(new_cost, 9), gap,
    )
