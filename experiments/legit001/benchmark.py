"""Reproducible, authored LEGIT-001 reason-router comparison.

Run: python experiments/legit001/benchmark.py
Scores include explicit synthetic question prices, abstention, mistakes and
covered accuracy. This is NOT an external blinded benchmark.
"""
from __future__ import annotations

import json
from collections import defaultdict

from router import digest, route
from classical_reference import reference
from stranger_gate import cases, hidden_world, observe, FROZEN_SEED, SCENARIOS


POLICIES = ("routing_2_step", "classical_exact_2_step",
            "routing_myopic", "prior_only", "always_abstain")


def one_trial(task, policy):
    truth_id = hidden_world(task)
    truth = next(w["answer"] for w in task["worlds"] if w["id"] == truth_id)
    history = []
    spent = 0.0
    if not task["grammar_covered"]:
        return {"verdict": "GRAMMAR_GAP_HELD", "loss": None, "queries": 0,
                "wrong": False, "history": []}
    while True:
        if policy == "always_abstain":
            action, question = "ABSTAIN", None
        elif policy == "classical_exact_2_step":
            action, question, _ = reference(task, history, 2)
        else:
            lookahead = {"routing_2_step": 2, "routing_myopic": 1,
                         "prior_only": 0}[policy]
            proposal = route(task, history, lookahead=lookahead)
            action, question = proposal["action"], proposal["question"]
        if action == "ASK_SYNTHETIC":
            if question is None or question in {h["question"] for h in history}:
                raise RuntimeError("Invalid duplicate inquiry")
            q = next(q for q in task["queries"] if q["id"] == question)
            spent += q["cost"]
            if spent > task["max_total_cost"] + 1e-9:
                raise RuntimeError("Budget failure")
            history.append({"question": question,
                            "yes": observe(task, truth_id, question)})
            if len(history) > task["max_questions"]:
                raise RuntimeError("Inquiry limit failure")
            continue
        if action == "ABSTAIN":
            return {"verdict": action, "loss": round(spent + task["abstain_loss"], 9),
                    "queries": len(history), "wrong": False, "history": history}
        if action in ("PREDICT_TRUE", "PREDICT_FALSE"):
            prediction = action == "PREDICT_TRUE"
            wrong = prediction != truth
            return {"verdict": action, "loss": round(spent + int(wrong), 9),
                    "queries": len(history), "wrong": wrong, "history": history}
        raise RuntimeError("Unexpected reason-router decision: " + action)


def report():
    grouped = defaultdict(lambda: defaultdict(list))
    raw_cases = list(cases())
    for family, task in raw_cases:
        for policy in POLICIES:
            grouped[family][policy].append(one_trial(task, policy))
    summary = {}
    for family, registered_count in SCENARIOS:
        summary[family] = {}
        for policy in POLICIES:
            rows = grouped[family][policy]
            if len(rows) != registered_count:
                raise RuntimeError("Missing authored scenario")
            evaluated = [r for r in rows if r["loss"] is not None]
            predicted = [r for r in evaluated if r["verdict"].startswith("PREDICT_")]
            summary[family][policy] = {
                "count": len(rows),
                "held_grammar_gaps": len(rows) - len(evaluated),
                "mean_realized_loss": (round(sum(r["loss"] for r in evaluated) /
                                              len(evaluated), 6) if evaluated else None),
                "prediction_coverage": (round(len(predicted) / len(evaluated), 6)
                                        if evaluated else None),
                "covered_error_rate": (round(sum(r["wrong"] for r in predicted) /
                                             len(predicted), 6) if predicted else None),
                "mean_questions": (round(sum(r["queries"] for r in evaluated) /
                                         len(evaluated), 6) if evaluated else None),
            }
    overall = {}
    for policy in POLICIES:
        rows = [r for family, _ in SCENARIOS for r in grouped[family][policy]]
        assessed = [r for r in rows if r["loss"] is not None]
        predicted = [r for r in assessed if r["verdict"].startswith("PREDICT_")]
        overall[policy] = {
            "assessed": len(assessed),
            "held_grammar_gaps": len(rows) - len(assessed),
            "mean_realized_loss": round(sum(r["loss"] for r in assessed) /
                                        len(assessed), 6),
            "coverage": round(len(predicted) / len(assessed), 6),
            "covered_error_rate": (round(sum(r["wrong"] for r in predicted) /
                                         len(predicted), 6) if predicted else None),
            "mean_questions": round(sum(r["queries"] for r in assessed) /
                                    len(assessed), 6),
        }
    xor = [task for family, task in raw_cases if family == "xor"]
    two_step = sum(route(task)["action"] == "ASK_SYNTHETIC" and
                   route(task, lookahead=1)["action"] == "ABSTAIN" for task in xor)
    return {
        "experiment": "MOTIF-LEGIT-001",
        "scope": "AUTHORED_SYNTHETIC_ONLY",
        "independent_unseen_test": False,
        "classical_superiority_claim": False,
        "seed": FROZEN_SEED,
        "public_fixture_sha256": digest([task for _, task in raw_cases]),
        "total_registered": len(raw_cases),
        "two_step_affordance_vs_myopia_on_xor": two_step,
        "overall": overall,
        "by_family": summary,
        "real_world_authority": False,
        "status": "RESEARCH_HOLD",
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
