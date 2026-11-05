"""LAW-FORGE-010: real post-identification falsification versus matched classical audits.

This experiment uses *exactly the same source-owned Stranger challenges* as
009, but gives every policy 12 identification units plus 12 audit units. The
source does not reveal oracle labels until its own question card is executed.
Reviewer/test sets remain completely disjoint from the query catalog.

The falsifier's legitimate target is detecting an out-of-grammar mechanism
*from training evidence*, before using heldout independent review as a gate.
"""
from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / "law-forge-009"))

import json
from functools import lru_cache
from entropy_cartridge import EntropyCartridge
from gap import diagnose
from falsifier import (
    LEARN_BUDGET, AUDIT_BUDGET, POLICIES, AuditLedger
)
from learner import (
    MAX_QUERIES, make_desk, Question, review, consequence_weight
)
from stranger_owner import Stranger, FAMILIES


@lru_cache(maxsize=256)
def identification(world: Stranger):
    """Same active Shannon learning for every audit policy.

    This returns even when the initial language is inadequate. A single
    remaining hypothesis is only 'identified within the frozen grammar',
    never 'true'.
    """
    learning = EntropyCartridge(world.contract, tuple(world.initial()))
    history = []
    while learning.budget_spent < LEARN_BUDGET:
        proposed = learning.propose(world.catalog(),
                                    LEARN_BUDGET - learning.budget_spent)
        if proposed is None:
            break
        request = Question.from_packet(proposed.card.packet())
        outcome = world.execute(request)
        learning = learning.ingest(proposed, outcome, world.catalog())
        history.append(proposed.card)
    return learning, tuple(history)


def inquiry(world: Stranger, policy="mutant_challenge"):
    if policy not in POLICIES:
        raise ValueError("Only registered audit policies")
    learning, learned_queries = identification(world)
    ledger = AuditLedger(learning, audit_policy=policy)
    issued = []
    questioned = []
    while ledger.audit_spent < AUDIT_BUDGET:
        proposal = ledger.propose(world.catalog())
        if proposal is None:
            break
        response = world.execute(Question.from_packet(proposal.card.packet()))
        before = len(ledger.evidence.survivor_indices)
        ledger = ledger.ingest(proposal, response, world.catalog())
        after = len(ledger.evidence.survivor_indices)
        questioned.append({
            "query": proposal.card.packet(),
            "policy": proposal.policy,
            "declared_score": round(proposal.declared_score, 6),
            "surviving_champion_before": before,
            "surviving_hypotheses_after": after,
            "actual_synthetic_label": response.y,
            "source_contract_id": response.contract_id
        })
        issued.append(proposal.card)
        if after == 0:
            break
    return ledger, learned_queries, tuple(issued), tuple(questioned)


def trial(world: Stranger, policy="mutant_challenge"):
    ledger, learned, audit, receipts = inquiry(world, policy)
    before = len(ledger.learning.survivor_indices)
    after = len(ledger.evidence.survivor_indices)
    pre_gap = diagnose(ledger.learning)
    post_gap = ledger.diagnosis()
    was_identified = before == 1
    detected_by_audit = bool(post_gap and not pre_gap)
    fitted = make_desk(world.contract,
                       ledger.evidence.observations, "classical_entropy")
    independent = review(fitted, world.contract, world.independent("review"))
    if post_gap:
        # This gate is stronger than a lack of sufficient review coverage:
        # a finite, witnessed impossibility of the grammar was demonstrated.
        decision = "HOLD_WITNESSED_GRAMMAR_GAP"
    else:
        decision = independent["status"]
    approved = decision.startswith("ELIGIBLE")
    heldout = world.independent("test")
    tested = wrong = weighted_tested = 0
    if approved:
        for row in heldout:
            prediction = fitted.predict(row.x, world.contract)
            if prediction["value"] is not None:
                tested += 1
                weighted_tested += consequence_weight(row.x)
                wrong += prediction["value"] != row.y
    assert ledger.learning.budget_spent <= LEARN_BUDGET
    assert ledger.audit_spent <= AUDIT_BUDGET
    assert ledger.learning.budget_spent + ledger.audit_spent <= MAX_QUERIES
    return {
        "family": world.family,  # evaluator-owned metrics; never learner input
        "seed": world.seed,
        "method": policy,
        "input_domain": 4096,
        "source_contract_id": world.contract.id,
        "initial_evidence_count": len(world.initial()),
        "learning_questions": len(learned),
        "learning_cost": ledger.learning.budget_spent,
        "audit_questions": len(audit),
        "audit_cost": ledger.audit_spent,
        "total_question_cost": ledger.learning.budget_spent + ledger.audit_spent,
        "hypotheses_after_learning": before,
        "hypotheses_after_audit": after,
        "single_candidate_identified": was_identified,
        "learning_grammar_gap": pre_gap is not None,
        "audit_discovered_new_gap": detected_by_audit,
        "audit_gap": post_gap.packet() if post_gap else None,
        "independent_review": independent,
        "decision": decision,
        "test_covered": tested,
        "test_wrong": wrong,
        "test_weighted_covered": weighted_tested,
        "test_total": len(heldout),
        "question_trace": list(receipts),
        "audit_cartridge": ledger.packet(),
        "no_external_action": True,
        "automatic_promotion": False
    }


def summarize(rows):
    eligible = tuple(r for r in rows if r["decision"].startswith("ELIGIBLE"))
    return {
        "worlds": len(rows),
        "identified_one": sum(r["single_candidate_identified"] for r in rows),
        "training_gap_before_audit": sum(r["learning_grammar_gap"] for r in rows),
        "new_grammar_gaps_from_audit": sum(
            r["audit_discovered_new_gap"] for r in rows),
        "source_review_eligible": len(eligible),
        "held": len(rows) - len(eligible),
        "learning_cost": sum(r["learning_cost"] for r in rows),
        "audit_cost": sum(r["audit_cost"] for r in rows),
        "total_cost": sum(r["total_question_cost"] for r in rows),
        "test_covered": sum(r["test_covered"] for r in rows),
        "test_wrong": sum(r["test_wrong"] for r in rows),
        "test_weighted_covered": sum(r["test_weighted_covered"] for r in rows),
    }


def benchmark():
    development = [Stranger(f, s) for f in FAMILIES for s in (0, 1)]
    evaluation = [Stranger(f, s) for f in FAMILIES
                  for s in (2, 3, 4, 5, 6)]
    dev = {m: summarize([trial(w, m) for w in development])
           for m in POLICIES}
    # Freeze the comparison against the STRONGEST classical audit control,
    # not merely 'no audit'. Added detection must also avoid wrongly flagging
    # a known in-grammar source under the original source training contract.
    classic = max(
        (dev[p] for p in ("classical_diversity",
                          "classical_fixed", "classical_random")),
        key=lambda r: (r["new_grammar_gaps_from_audit"],
                       -r["total_cost"])
    )
    ours = dev["mutant_challenge"]
    promote = (
        ours["new_grammar_gaps_from_audit"] >=
        classic["new_grammar_gaps_from_audit"] + 2 and
        ours["total_cost"] <= classic["total_cost"] and
        ours["test_wrong"] <= classic["test_wrong"]
    )
    result = {
        "schema": "motif.law-forge.blind-falsifier-benchmark.v1",
        "research_goal": "independent training-time challenge of a sole surviving model before review labels",
        "learning_budget": LEARN_BUDGET,
        "post_identification_audit_budget": AUDIT_BUDGET,
        "total_budget": MAX_QUERIES,
        "source_question_catalog_size": 128,
        "source_review_test_disjoint": True,
        "development": dev,
        "frozen_method_decision": (
            "PROPOSE_FOR_HUMAN_REVIEW_ONLY"
            if promote else "NO_METHOD_PROMOTION"
        ),
        "evaluation": {m: summarize([trial(w, m) for w in evaluation])
                       for m in POLICIES},
        "examples": {name: trial(Stranger(name, 3)) for name in (
            "single_bit", "two_bit_xor", "conditional_mux",
            "four_bit_parity", "four_bit_threshold",
            "drifting_pair_xor", "hidden_exception"
        )},
        "limitations": [
            "all question policies are classical; critic mutations are predeclared",
            "the owner uses synthetic researcher-authored mechanism families",
            "identification uses the same limited 650-rule hypothesis grammar",
            "unseen rival grammar truth cannot be guaranteed from finite evidence",
            "source SHA hashes provide no authentication of real witnesses",
            "post-identification audit is not an independent real-world source",
            "native external ALEX, GRAFT and Question Machine remain unwired",
            "abstention is not a proof of physics or calibrated confidence"
        ],
        "real_world_authority": False,
        "automatic_admission": False
    }
    return result


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
