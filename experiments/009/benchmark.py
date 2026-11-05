"""MOTIF-009 benchmark: can tree cartridges use a fixed label budget better?

The simulator/evaluator alone imports oracle.py. A chooser receives unlabeled
graphs, role bindings, already revealed synthetic observations and a
source-derived decision-tree cartridge committee, never oracle rule metadata.

Both strategies start with the same 16 revealed examples and spend exactly 12
additional observation requests from the same pool. A seeded RANDOM strategy
is the matched-budget control. Performance is evaluated on the same untouched
80-case test split. Results may favor neither strategy. NO physical actions.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from random import Random
from statistics import mean
import json

from oracle import FAMILIES, spec_for, split
from learner import features, observed_outcome, balanced_accuracy
from cartridge import (fit_cartridge, export_cartridge, validate_cartridge,
                       CartridgeBay, HOLD)
from experimenter import (Question, QueryBudget, public_question,
                          propose_question, train_committee,
                          independent_oracle_answer)

VERSION = "active-tree-cartridges-v1"
SEEDS = (11, 23, 37, 41, 59)
INITIAL = 16
REQUESTS = 12
POOL = 96
TEST = 80
CHECKPOINTS = (0, 6, 12)


def held_out_score(car, test):
    y = tuple(observed_outcome(x) for x in test)
    if not (any(y) and not all(y)):
        raise ValueError("Heldout synthetic test needs positive and negative examples")
    guess = tuple(car.predict(features(x.before, x.roles)) for x in test)
    return round(balanced_accuracy(y, guess), 4)


def experiment(family: str, seed: int) -> dict:
    """Fixed protocol. Neither active proposal nor random baseline sees answer."""
    spec = spec_for(family, seed)
    generated = split(spec, "train", INITIAL + POOL)
    testing = split(spec, "test", TEST)
    revealed = list(generated[:INITIAL])
    first = fit_cartridge(revealed)
    active = list(revealed)
    passive = list(revealed)
    candidates = [public_question(i, case.before, case.roles)
                  for i, case in enumerate(generated[INITIAL:])]
    secret = {q.ticket: generated[INITIAL + i] for i, q in enumerate(candidates)}
    # Test integrity: only unlabeled Question objects can enter selector.
    assert all(set(vars(q)) == {"ticket", "before", "roles"}
               for q in candidates)

    randomizer = Random(seed * 10007 + sum(ord(c) for c in family))
    random_order = randomizer.sample(tuple(q.ticket for q in candidates), REQUESTS)
    available = tuple(candidates)
    budget_active, budget_random = QueryBudget(REQUESTS), QueryBudget(REQUESTS)
    checkpoints = {}
    query_receipts = []
    initial_tree = export_cartridge(first)
    assert validate_cartridge(initial_tree) == first

    for step in range(REQUESTS + 1):
        if step in CHECKPOINTS:
            checkpoints[str(step)] = {
                "active_balanced": held_out_score(fit_cartridge(active), testing),
                "random_balanced": held_out_score(fit_cartridge(passive), testing),
                "active_seen": len(active), "random_seen": len(passive)
            }
        if step == REQUESTS:
            break
        committee = train_committee(active, seed=seed * 1000 + step,
                                    members=3)
        proposal = propose_question(available, tuple(active), committee)
        budget_active.consume(proposal.ticket)
        revealed_case = independent_oracle_answer(proposal, secret)
        active.append(revealed_case)
        available = tuple(q for q in available if q.ticket != proposal.ticket)

        random_ticket = random_order[step]
        budget_random.consume(random_ticket)
        passive.append(secret[random_ticket])

        query_receipts.append({
            "step": step + 1,
            "selected_ticket": proposal.ticket,
            "tree_cartridge_id": committee[0].id,
            "committee_votes": list(proposal.votes),
            "tree_leaf_training_count": proposal.learned_leaf_observations,
            "tree_prediction_before_observation": proposal.predicted_outcome,
            "synthetic_observed_outcome": observed_outcome(revealed_case),
            "question_exposed_outcome_before_query": proposal.answer_known,
            "random_ticket": random_ticket
        })

    end_active = fit_cartridge(active)
    end_random = fit_cartridge(passive)
    return {
        "family": family, "seed": seed, "initial": INITIAL,
        "requests_per_policy": REQUESTS,
        "test_size": TEST,
        "oracle_answers_revealed_active": len(budget_active.used),
        "oracle_answers_revealed_random": len(budget_random.used),
        "source_first_cartridge_id": first.id,
        "active_final_cartridge_id": end_active.id,
        "random_final_cartridge_id": end_random.id,
        "active_fit_balanced": end_active.fit_balanced,
        "random_fit_balanced": end_random.fit_balanced,
        "checkpoints": checkpoints,
        "active_vs_random_final": round(
            checkpoints[str(REQUESTS)]["active_balanced"] -
            checkpoints[str(REQUESTS)]["random_balanced"], 4),
        "questions": query_receipts
    }


def summarize(worlds):
    checkpoint = str(REQUESTS)
    a = [x["checkpoints"][checkpoint]["active_balanced"] for x in worlds]
    b = [x["checkpoints"][checkpoint]["random_balanced"] for x in worlds]
    if len(a) != len(b) or len(a) != len(FAMILIES) * len(SEEDS):
        raise ValueError("Incorrect complete benchmark")
    series = {}
    for stamp in CHECKPOINTS:
        rows = [x["checkpoints"][str(stamp)] for x in worlds]
        series[str(stamp)] = {
            "active": round(mean(x["active_balanced"] for x in rows), 4),
            "random": round(mean(x["random_balanced"] for x in rows), 4)
        }
    per_family = {}
    for family in FAMILIES:
        group = [x for x in worlds if x["family"] == family]
        per_family[family] = {
            "worlds": len(group),
            "active_final": round(mean(x["checkpoints"][checkpoint]["active_balanced"]
                                       for x in group), 4),
            "random_final": round(mean(x["checkpoints"][checkpoint]["random_balanced"]
                                       for x in group), 4),
            "wins": sum(x["active_vs_random_final"] > 0 for x in group),
            "ties": sum(x["active_vs_random_final"] == 0 for x in group),
            "losses": sum(x["active_vs_random_final"] < 0 for x in group),
        }
    return {
        "version": VERSION,
        "scope": "POOL_BASED_SYNTHETIC_ACTIVE_OBSERVATIONS",
        "worlds": len(worlds), "families": list(FAMILIES), "seeds": list(SEEDS),
        "initial_labeled_each": INITIAL, "additional_queries_each": REQUESTS,
        "unlabeled_pool_each": POOL, "held_out_test_each": TEST,
        "test_labels_available_to_selector": False,
        "oracle_rules_available_to_selector": False,
        "both_strategies_same_label_budget": True,
        "active_could_inspect_unlabeled_pool": True,
        "passive_used_same_unlabeled_pool": True,
        "question_type": "SELECT_PREEXISTING_OBSERVATION",
        "cartridge_predicts_real_world_actions": False,
        "mean_learning_curve": series,
        "active_final_balanced": round(mean(a), 4),
        "random_final_balanced": round(mean(b), 4),
        "active_mean_gain": round(mean(a) - mean(b), 4),
        "active_wins": sum(x > y for x, y in zip(a, b)),
        "ties": sum(x == y for x, y in zip(a, b)),
        "active_losses": sum(x < y for x, y in zip(a, b)),
        "per_family": per_family,
    }


def cartridge_review_demo():
    """Local HOLD → preview → explicitly admit read-only prediction.

    A separate fixture receiver uses data from the SAME generated vocabulary;
    a changed world namespace cannot be silently imported.
    """
    spec = spec_for("forward_join", SEEDS[0])
    training = split(spec, "train", 80)
    validation = split(spec, "validation", 32)
    learner = fit_cartridge(training)
    bundle = export_cartridge(learner)
    receiver = CartridgeBay()
    ticket = receiver.offer(bundle)
    held = ticket not in receiver.admitted
    recorded = receiver.review(ticket, "ADMIT_PREDICT_ONLY",
                               "SYNTHETIC_LOCAL_REVIEWER",
                               local_observations=validation,
                               min_balanced=0.65)
    result = receiver.predict_admitted(ticket, validation[0].before,
                                       validation[0].roles)
    receiver.revoke(ticket, "SYNTHETIC_LOCAL_REVIEWER")
    revoked = False
    try:
        receiver.predict_admitted(ticket, validation[0].before,
                                  validation[0].roles)
    except HOLD:
        revoked = True
    return {
        "initially_held": held,
        "admission": recorded["decision"],
        "review_balanced": round(recorded["local_score"], 4),
        "tree_explanation_has_path": isinstance(result["leaf_index"], int),
        "revocation_blocks_predictions": revoked,
        "real_authority": False,
        "origin_signature_verified": False
    }


def report():
    worlds = [experiment(family, seed)
              for family in FAMILIES for seed in SEEDS]
    return {
        "experiment": "MOTIF-009",
        "summary": summarize(worlds),
        "cartridge_local_review": cartridge_review_demo(),
        "worlds": worlds,
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
