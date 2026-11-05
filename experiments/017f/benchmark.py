"""Reproducible MOTIF-017F synthetic self-growing question / diagnostic benchmark."""
from __future__ import annotations

from dataclasses import asdict
import json
from statistics import mean

from diagnostic import examine_room, run_policy
from grower import draft_questions, review_question
from frontier import inspect_diagnostic
from oracle import TestWorld, problem, reviewed_receipts


def benchmark():
    hypotheses, roads, offers = problem()
    proposed = draft_questions([h.name for h in hypotheses], roads, offers)
    offers_by_name = {p.offer.name: p for p in proposed}
    frontier_before = inspect_diagnostic(hypotheses, roads, proposed)
    admissions = {}
    opportunities = {}
    for proposal in proposed:
        receipt = reviewed_receipts(proposal.offer) if proposal.offer.allowed else ()
        result = review_question(proposal, receipt)
        admissions[proposal.offer.name] = result
        opportunities[proposal.offer.name] = examine_room(
            hypotheses, roads, proposal, result
        )

    frontier_after = inspect_diagnostic(hypotheses, roads, proposed, admissions)
    heldout_worlds = [TestWorld(h.name, "TEST", 1000+i)
                      for i, h in enumerate(hypotheses)]
    old = [run_policy("FROZEN_FIXED", hypotheses, roads, w)
           for w in heldout_worlds]
    comparisons = {}
    for offer_name in ("FUSED_PORTS", "DRIFT_FUSED_PORTS", "OVERPRICED_PORTS"):
        review = admissions[offer_name]
        if review.admissible_road is None:
            continue
        proposal = offers_by_name[offer_name]
        grown = [
            run_policy("GROWN_FOREST", hypotheses, roads, w,
                       review.admissible_road, proposal)
            for w in heldout_worlds
        ]
        classical = [
            run_policy("CLASSICAL_EXACT_REFIT", hypotheses, roads, w,
                       review.admissible_road, proposal)
            for w in heldout_worlds
        ]
        def metrics(group):
            return {
                "correct_of_8": sum(x.correct for x in group),
                "mean_query_cost": round(mean(x.cost for x in group), 9),
                "held_worlds": sum(x.holding for x in group),
            }
        comparisons[offer_name] = {
            "frozen_original": metrics(old),
            "grown_forest": metrics(grown),
            "classical_exact_refit": metrics(classical),
            "failures": [
                {"world": x.world, "reported_answer": x.predicted_answer,
                 "actual_answer": x.true_answer, "status": "WRONG_PREDICTION"}
                for x in grown if not x.correct
            ],
            "per_world": [{
                "world": x.world,
                "portfolios": x.selected,
                "correct": x.correct,
                "cost": x.cost,
                "holding": x.holding,
            } for x in grown],
        }
    return {
        "experiment": "MOTIF-017F — self-growing question + improvable diagnostic",
        "fixture": "Eight fixed synthetic binary worlds; separate adjudicated REVIEW vs TEST phase",
        "question_factory": {
            p.offer.name: {
                "components": p.source_component_names,
                "proposed_checksum": p.digest,
                "proposal_status": p.status,
                "offer_price": p.offer.price,
                "offer_allowed": p.offer.allowed,
                "independent_review_status": admissions[p.offer.name].status,
                "reviewed_count": admissions[p.offer.name].reviewed,
                "review_counterexamples": admissions[p.offer.name].counterexamples,
            } for p in proposed
        },
        "method_frontier": {
            "before_independent_review": asdict(frontier_before),
            "after_independent_review": asdict(frontier_after),
        },
        "diagnostic": {
            name: asdict(assessment)
            for name, assessment in opportunities.items()
        },
        "heldout": comparisons,
        "explicit_boundaries": {
            "adopted_live": False,
            "real_sources_authenticated": False,
            "external_actions": False,
            "prior_diagnostic_is_not_global_optimality_proof": True,
            "strong_refitted_classical_baseline_is_required": True,
            "novel_sensor_without_provider_offer": False,
            "post_review_drift_can_be_missed": True,
        },
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
