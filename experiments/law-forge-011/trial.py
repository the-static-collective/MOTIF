"""LAW-FORGE-011 frozen, source-separated signed-critic comparison.

A new 12-family synthetic owner fixture replaces the original Stranger source
for the new experiment. 12 learning + 12 auditing budget; every method sees
the same initial four observations and identical owner-approved catalog.
Hidden review/test labels are never used to select questions.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import json
import sys

sys.path.extend((str(Path(__file__).resolve().parents[1] / "law-forge-009"),
                 str(Path(__file__).resolve().parents[1] / "law-forge-008")))
from entropy_cartridge import EntropyCartridge
from learner import Question, make_desk, review, consequence_weight
from signed_critic import (
    LEARN_BUDGET, AUDIT_BUDGET, POLICIES, SignedAudit,
    surviving_critics
)
from source_owner import FAMILIES, UnknownOwner


@lru_cache(maxsize=256)
def learn(owner):
    """Original 009 Shannon skill, frozen equally for every competitor."""
    model = EntropyCartridge(owner.contract, owner.initial())
    offered = []
    while model.budget_spent < LEARN_BUDGET:
        candidate = model.propose(owner.catalog(),
                                  LEARN_BUDGET - model.budget_spent)
        if candidate is None:
            break
        query = Question.from_packet(candidate.card.packet())
        witness = owner.execute(query)
        model = model.ingest(candidate, witness, owner.catalog())
        offered.append(query)
    return model, tuple(offered)


def inquire(owner, method):
    if method not in POLICIES:
        raise ValueError("Predeclared policy required")
    learned, previous = learn(owner)
    audit = SignedAudit(learned, method)
    queries = []
    while audit.audit_spent < AUDIT_BUDGET:
        question = audit.propose(owner.catalog())
        if question is None:
            break
        source_card = Question.from_packet(question.card.packet())
        witness = owner.execute(source_card)
        audit = audit.ingest(question, witness, owner.catalog())
        queries.append(source_card)
        if not audit.evidence.survivor_indices:
            break
    return audit, previous, tuple(queries)


def trial(owner, method="signed_counterfactual"):
    audit, learned_questions, audit_questions = inquire(owner, method)
    gap = audit.grammar_gap()
    learned_one = len(audit.learning.survivor_indices) == 1
    diagnosed = gap is not None and learned_one
    desk = make_desk(owner.contract, audit.evidence.observations,
                     "classical_entropy")
    reviewed = review(desk, owner.contract, owner.independent("review"))
    decision = ("HOLD_WITNESSED_GRAMMAR_GAP"
                if gap else reviewed["status"])
    accepted = decision.startswith("ELIGIBLE")
    test_rows = owner.independent("test")
    covered = incorrect = weighted = 0
    if accepted:
        for witness in test_rows:
            response = desk.predict(witness.x, owner.contract)
            if response["value"] is None:
                continue
            covered += 1
            incorrect += response["value"] != witness.y
            weighted += consequence_weight(witness.x)
    stale = desk.predict(owner.initial()[0].x, owner.changed_epoch().contract)
    return {
        "family": owner.family,  # evaluator metadata only
        "seed": owner.seed,
        "method": method,
        "source_contract_id": owner.contract.id,
        "learning_cost": audit.learning.budget_spent,
        "audit_cost": audit.audit_spent,
        "total_cost": audit.learning.budget_spent + audit.audit_spent,
        "learning_queries": len(learned_questions),
        "audit_queries": len(audit_questions),
        "identified_exactly_one": learned_one,
        "counterfactuals_after_learning": (
            len(surviving_critics(audit.learning)) if learned_one else None
        ),
        "discovered_gap_after_audit": diagnosed,
        "gap_evidence": gap.packet() if gap else None,
        "surviving_rules_after_audit": len(audit.evidence.survivor_indices),
        "independent_review": reviewed,
        "decision": decision,
        "heldout_cases": len(test_rows),
        "heldout_covered": covered,
        "heldout_wrong": incorrect,
        "heldout_weighted_covered": weighted,
        "stale_source_status": stale["status"],
        "audit_cartridge": audit.packet(),
        "real_world_authority": False,
        "external_actions": 0
    }


def summarize(records):
    accepted = [x for x in records if x["decision"].startswith("ELIGIBLE")]
    return {
        "worlds": len(records),
        "identified_one": sum(x["identified_exactly_one"] for x in records),
        "source_audit_cost": sum(x["audit_cost"] for x in records),
        "total_cost": sum(x["total_cost"] for x in records),
        "grammar_gaps_detected": sum(
            x["discovered_gap_after_audit"] for x in records),
        "review_eligible": len(accepted),
        "held": len(records) - len(accepted),
        "test_covered": sum(x["heldout_covered"] for x in records),
        "test_wrong": sum(x["heldout_wrong"] for x in records),
        "source_queries_used": sum(
            x["learning_queries"] + x["audit_queries"] for x in records),
        "mean_candidate_critics_after_learning": round(
            sum((x["counterfactuals_after_learning"] or 0)
                for x in records) / len(records), 2)
    }


def benchmark():
    development = [UnknownOwner(f, seed) for f in FAMILIES
                   for seed in (0,1)]
    # New seeds not used in LAW-FORGE-010 evaluations and a new owner
    # partition function; STILL researcher-authored not external worlds.
    evaluation = [UnknownOwner(f, seed) for f in FAMILIES
                  for seed in (7,8,9,10)]
    dev = {m: summarize([trial(w,m) for w in development])
           for m in POLICIES}
    baseline = max(
        (dev[p] for p in ("classical_diversity", "classical_boundary",
                          "classical_fixed", "classical_seeded_random")),
        key=lambda r: (r["grammar_gaps_detected"], -r["total_cost"])
    )
    ours=dev["signed_counterfactual"]
    qualify=(ours["grammar_gaps_detected"]>=
             baseline["grammar_gaps_detected"] + 2 and
             ours["total_cost"]<=baseline["total_cost"] and
             ours["test_wrong"]<=baseline["test_wrong"])
    return {
        "schema":"motif.law-forge.signed-counterfactual-benchmark.v1",
        "preregistered_promotion_rule":
            "at-least-two-more-grammar-gaps-than-best-classical-control-on-development-at-no-higher-total-source-cost-and-no-more-errors",
        "learning_budget":LEARN_BUDGET,
        "audit_budget":AUDIT_BUDGET,
        "unseen_domain_size":4096,
        "source_is_researcher_authored":True,
        "development":dev,
        "frozen_decision":("PROPOSE_FOR_HUMAN_REVIEW_ONLY" if qualify
                           else "NO_METHOD_PROMOTION"),
        "evaluation":{m:summarize([trial(w,m) for w in evaluation])
                      for m in POLICIES},
        "examples":{
            f:trial(UnknownOwner(f,8))
            for f in ("bit", "signed_exception",
                      "two_signed_exceptions","four_bit_parity",
                      "training_review_shift","hidden_context_shift")
        },
        "nonclaims":[
            "real-world independent source authentication or sensor permission",
            "novel Boolean mathematics",
            "calibrated confidence",
            "general physical causal knowledge",
            "automatic GRAFT/ALEX/Question Machine integration",
            "source-derived critics from real independent inquiry",
            "out-of-family extrapolation guarantee"
        ],
        "automatic_promotion":False,"real_world_authority":False
    }


if __name__=="__main__":
    print(json.dumps(benchmark(),sort_keys=True,indent=2))
