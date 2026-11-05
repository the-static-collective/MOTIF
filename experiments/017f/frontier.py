"""MOTIF-017F: diagnostic self-audit and explicitly uncertain research tickets.

Even 100% accuracy on a known tiny world is NOT a proof that this method is
optimal under costs, drift, new questions or unseen hypotheses. This module
ranks *hypothetical* improvements without executing or admitting them.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Sequence

from grower import QuestionProposal, Review
from forest import LivingForest, Road
from multiplex import Hypothesis


@dataclass(frozen=True)
class ImprovementTicket:
    candidate_name: str
    question: str
    status: str
    current_best_cost: float
    possible_cost: float | None
    potential_saving_if_true: float | None
    epistemic_status: str = "UNVERIFIED_PREDICTION_NOT_A_MEASURED_GAIN"


@dataclass(frozen=True)
class DiagnosticFrontier:
    status: str
    known_model_accuracy_ceiling: float
    global_optimality_established: bool
    known_worlds_exhaustive_of_reality: bool
    future_source_reliability_proven: bool
    improvement_axes: tuple[str, ...]
    tickets: tuple[ImprovementTicket, ...]
    review_priority: tuple[str, ...]
    deferred_to_external_review: bool = True


def inspect_diagnostic(
    hypotheses: Sequence[Hypothesis],
    roads: Sequence[Road],
    proposals: Sequence[QuestionProposal],
    reviews: Mapping[str, Review] | None = None,
) -> DiagnosticFrontier:
    """Choose which question innovation deserves *review* before implementation.

    A falsely cheap hypothesis can win the triage rank; that is why admission
    always follows separate observations. 'Ceiling' means ONLY 100% accuracy
    within the *declared* grammar; no extrapolation to the outside world.
    """
    reviews = reviews or {}
    incumbent = LivingForest(hypotheses, roads)
    current = incumbent.plan()
    current_cost = current.expected_total_cost
    tickets = []
    for proposal in proposals:
        review = reviews.get(proposal.offer.name)
        name = proposal.offer.name
        if not proposal.offer.allowed:
            tickets.append(ImprovementTicket(name, proposal.candidate.prompt,
                                             "HOLD_PERMISSION", current_cost, None, None))
            continue
        if review is not None and review.proposal_digest != proposal.digest:
            tickets.append(ImprovementTicket(name, proposal.candidate.prompt,
                                             "HOLD_MISMATCHED_REVIEW", current_cost, None, None))
            continue
        if review is not None and review.status != "ELIGIBLE_SYNTHETIC_ONLY":
            tickets.append(ImprovementTicket(name, proposal.candidate.prompt,
                                             review.status, current_cost, None, None))
            continue
        # Counterfactual only: set allowed=True within a throwaway exact planner,
        # never within actual executable state. No independent observation here.
        shadow = Road(proposal.candidate.name, proposal.candidate.kind,
                      proposal.candidate.cost, proposal.candidate.predicted,
                      proposal.candidate.origin, allowed=True)
        hypothetical = LivingForest(hypotheses, tuple(roads)+(shadow,)).plan()
        gain = round(current_cost - hypothetical.expected_total_cost, 9)
        if gain > 1e-10:
            status = ("REVIEWED_POSSIBLE_REVISION" if review is not None
                      else "RESEARCH_NEXT_NOT_ADMITTED")
        else:
            status = "HOLD_NO_SHADOW_GAIN"
        tickets.append(ImprovementTicket(
            name, proposal.candidate.prompt, status, round(current_cost, 9),
            round(hypothetical.expected_total_cost, 9), gain,
        ))
    tickets.sort(key=lambda t: (
        t.status not in {"RESEARCH_NEXT_NOT_ADMITTED", "REVIEWED_POSSIBLE_REVISION"},
        -(t.potential_saving_if_true if t.potential_saving_if_true is not None else -1),
        t.candidate_name
    ))
    return DiagnosticFrontier(
        status="OPEN_METHOD_FRONTIER_NOT_A_PROVEN_CEILING",
        known_model_accuracy_ceiling=1.0,
        global_optimality_established=False,
        known_worlds_exhaustive_of_reality=False,
        future_source_reliability_proven=False,
        improvement_axes=(
            "lower_question_cost", "new_licensed_questions", "fewer_human_interruptions",
            "better_uncertainty_calibration", "detect_unseen_causes",
            "negative_transfer_resistance", "new_future_affordances",
        ),
        tickets=tuple(tickets),
        review_priority=tuple(t.candidate_name for t in tickets
                              if t.status == "RESEARCH_NEXT_NOT_ADMITTED"),
    )
