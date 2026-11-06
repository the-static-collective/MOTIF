"""LEGIT-001: finite, inspectable reason routing in a synthetic world.

The router has NO oracle import, filesystem/network I/O, external tool access,
real-world authority, source authentication, or learned general intelligence.
Its two-step lookahead is classical decision theory, not a novel algorithm.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
import re

SCHEMA = "motif.reason-routing-task.v0"
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
MAX_WORLDS = 8
MAX_QUESTIONS = 5
MAX_STEPS = 3


class Hold(ValueError):
    """Reject unreviewed, malformed, or logically impossible synthetic input."""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def _number(value, lower=0.0, upper=1.0):
    return (type(value) in (int, float) and math.isfinite(value)
            and lower <= value <= upper)


def validate_task(task):
    if not isinstance(task, dict) or set(task) != {
            "schema", "id", "scope", "grammar_covered", "worlds", "queries",
            "abstain_loss", "max_questions", "max_total_cost"}:
        raise Hold("Unexpected or missing task fields")
    if task["schema"] != SCHEMA or task["scope"] != "SYNTHETIC_ONLY":
        raise Hold("Unsupported schema or authority scope")
    if not isinstance(task["id"], str) or not SAFE_ID.fullmatch(task["id"]):
        raise Hold("Invalid task identifier")
    if type(task["grammar_covered"]) is not bool:
        raise Hold("Grammar coverage requires a Boolean declaration")
    if (not _number(task["abstain_loss"]) or
            not _number(task["max_total_cost"], 0.0, 10.0) or
            type(task["max_questions"]) is not int or
            not 0 <= task["max_questions"] <= MAX_STEPS):
        raise Hold("Invalid loss or bounded investigation budget")
    worlds = task["worlds"]
    if not isinstance(worlds, list) or not 2 <= len(worlds) <= MAX_WORLDS:
        raise Hold("Unsupported hypothesis count")
    ids = []
    total = 0.0
    for row in worlds:
        if (not isinstance(row, dict) or set(row) != {"id", "answer", "prior"}
                or not isinstance(row["id"], str)
                or not SAFE_ID.fullmatch(row["id"])
                or type(row["answer"]) is not bool
                or not _number(row["prior"])):
            raise Hold("Invalid hypothesis")
        ids.append(row["id"])
        total += row["prior"]
    if len(set(ids)) != len(ids) or abs(total - 1.0) > 1e-9:
        raise Hold("Non-normalized or duplicate hypotheses")
    queries = task["queries"]
    if not isinstance(queries, list) or len(queries) > MAX_QUESTIONS:
        raise Hold("Too many proposed questions")
    qids = []
    for q in queries:
        if (not isinstance(q, dict) or set(q) != {"id", "cost", "p_yes"}
                or not isinstance(q["id"], str) or not SAFE_ID.fullmatch(q["id"])
                or not _number(q["cost"], 0.0, 10.0)
                or not isinstance(q["p_yes"], dict)
                or set(q["p_yes"]) != set(ids)
                or not all(_number(v) for v in q["p_yes"].values())):
            raise Hold("Invalid or out-of-support question")
        qids.append(q["id"])
    if len(set(qids)) != len(qids):
        raise Hold("Duplicate question identifier")
    if len(canonical(task).encode("utf-8")) > 30000:
        raise Hold("Task too large")
    return task


def posterior_after(task, history):
    """Update only from declared synthetic observation tickets, never hidden truth."""
    validate_task(task)
    if not isinstance(history, (tuple, list)) or len(history) > task["max_questions"]:
        raise Hold("Observation budget exceeded")
    questions = {q["id"]: q for q in task["queries"]}
    belief = {w["id"]: float(w["prior"]) for w in task["worlds"]}
    used = set()
    spent = 0.0
    for record in history:
        if (not isinstance(record, dict) or set(record) != {"question", "yes"}
                or type(record["yes"]) is not bool
                or record["question"] not in questions
                or record["question"] in used):
            raise Hold("Forged, repeated, or malformed observation")
        q = questions[record["question"]]
        used.add(q["id"])
        spent += q["cost"]
        if spent > task["max_total_cost"] + 1e-10:
            raise Hold("Question exceeded budget")
        for wid in belief:
            likelihood = q["p_yes"][wid]
            belief[wid] *= likelihood if record["yes"] else 1.0 - likelihood
        norm = sum(belief.values())
        if norm <= 1e-14:
            raise Hold("Impossible or zero-likelihood observation")
        belief = {wid: prob / norm for wid, prob in belief.items()}
    return belief, used, round(task["max_total_cost"] - spent, 10)


def terminal(task, belief):
    p = sum(belief[w["id"]] for w in task["worlds"] if w["answer"])
    # Deliberately prefer abstention on exact ties.
    candidates = (("ABSTAIN", task["abstain_loss"]),
                  ("PREDICT_FALSE", p), ("PREDICT_TRUE", 1.0 - p))
    name, risk = min(candidates, key=lambda row: row[1])
    return {"action": name, "risk": risk, "confidence_true": p}


def _updated(belief, q, yes):
    weighted = {wid: p * (q["p_yes"][wid] if yes else
                          1 - q["p_yes"][wid]) for wid, p in belief.items()}
    total = sum(weighted.values())
    return ({wid: p / total for wid, p in weighted.items()} if total > 1e-14
            else None), total


def _plan(task, belief, available, budget, depth):
    current = terminal(task, belief)
    best = {"action": current["action"], "question": None,
            "risk": current["risk"]}
    if depth <= 0:
        return best
    for q in sorted(available, key=lambda row: row["id"]):
        if q["cost"] > budget + 1e-10:
            continue
        future = [row for row in available if row["id"] != q["id"]]
        risk = q["cost"]
        for yes in (False, True):
            next_belief, probability = _updated(belief, q, yes)
            if probability > 1e-14:
                risk += probability * _plan(
                    task, next_belief, future, budget - q["cost"], depth - 1
                )["risk"]
        # Strict improvement: a query with no value must not be sent.
        if risk < best["risk"] - 1e-10:
            best = {"action": "ASK_SYNTHETIC", "question": q["id"], "risk": risk}
    return best


def route(task, history=(), *, lookahead=2):
    """Choose a METHOD, not an external action. No observations are issued here.

    lookahead=1 is the registered myopic ablation. lookahead=2 is the
    bounded affordance-aware selector. The hypothesis family is supplied,
    not discovered. A grammar gap is only held for independent inspection.
    """
    belief, used, budget = posterior_after(task, history)
    if type(lookahead) is not int or not 0 <= lookahead <= MAX_STEPS:
        raise Hold("Lookahead outside declared research bound")
    fingerprint = digest({"task": task, "history": list(history)})
    if not task["grammar_covered"]:
        return {"action": "PROPOSE_GRAMMAR_REVIEW_HELD", "question": None,
                "prediction": None, "expected_remaining_loss": None,
                "confidence_true": None, "content_digest": fingerprint,
                "status": "HOLD", "real_world_authority": False,
                "basis": "Declared grammar gap is NOT an impossibility proof"}
    candidates = [q for q in task["queries"] if q["id"] not in used]
    depth = min(lookahead, task["max_questions"] - len(used), len(candidates))
    plan = _plan(task, belief, candidates, budget, depth)
    current = terminal(task, belief)
    action = plan["action"]
    return {"action": action, "question": plan["question"],
            "prediction": (True if action == "PREDICT_TRUE"
                           else False if action == "PREDICT_FALSE" else None),
            "expected_remaining_loss": round(plan["risk"], 9),
            "confidence_true": round(current["confidence_true"], 9),
            "content_digest": fingerprint,
            "status": "PROPOSAL_ONLY", "real_world_authority": False,
            "basis": "Classical finite Bayesian lookahead; no external action"}
