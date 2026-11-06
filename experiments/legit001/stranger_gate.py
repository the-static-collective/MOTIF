"""LEGIT-001 authored synthetic challenges and independent hidden-outcome simulator.

The router never imports this module. These are PREDECLARED, developer-authored
toy families, not independent unseen repositories or physical-world tests.
Hidden simulator outcomes enter only after a query proposal is emitted.
"""
from __future__ import annotations

from hashlib import sha256
from random import Random

SCENARIOS = (
    ("xor", 40), ("or", 40), ("biased", 24),
    ("uninformative", 24), ("limited", 24),
    ("costly", 24), ("grammar_gap", 8),
)
FROZEN_SEED = "motif-legit001-authored-suite-2026-11-06-v1"


def _seed(*values):
    return int(sha256("|".join(map(str, (FROZEN_SEED,) + values)).encode()
                      ).hexdigest()[:16], 16)


def public_problem(family, index):
    """Task contains no selected true world or future realized sensor reading."""
    if family not in {name for name, _ in SCENARIOS}:
        raise ValueError("Unknown registered family")
    if type(index) is not int or index < 0:
        raise ValueError("Invalid trial index")
    bits = ((False, False), (False, True), (True, False), (True, True))
    priors = ([0.05, 0.05, 0.10, 0.80] if family == "biased"
              else [0.25] * 4)
    worlds = [{"id": "w" + str(i),
               "answer": (a != b if family != "or" else a or b),
               "prior": priors[i]}
              for i, (a, b) in enumerate(bits)]
    queries = []
    for col, label in ((0, "measure_a"), (1, "measure_b")):
        probabilities = {("w" + str(i)):
                         (0.5 if family == "uninformative"
                          else 0.9 if pair[col] else 0.1)
                         for i, pair in enumerate(bits)}
        queries.append({"id": label,
                        "cost": 0.2 if family == "costly" else 0.02,
                        "p_yes": probabilities})
    return {"schema": "motif.reason-routing-task.v0",
            "id": f"{family}-{index:03d}",
            "scope": "SYNTHETIC_ONLY",
            "grammar_covered": family != "grammar_gap",
            "worlds": worlds, "queries": queries,
            "abstain_loss": 0.28,
            "max_questions": 1 if family == "limited" else 2,
            "max_total_cost": 0.03 if family == "limited" else 0.4}


def hidden_world(task):
    """Sample hidden synthetic world from declared prior. Not imported by router."""
    number = Random(_seed(task["id"], "world")).random()
    cumulative = 0.0
    for row in task["worlds"]:
        cumulative += row["prior"]
        if number < cumulative:
            return row["id"]
    return task["worlds"][-1]["id"]


def observe(task, world_id, question_id):
    """Generate a reproducible noisy synthetic measurement after a ticket."""
    questions = {q["id"]: q for q in task["queries"]}
    if question_id not in questions or world_id not in {
            w["id"] for w in task["worlds"]}:
        raise ValueError("Unknown original sensor/world")
    probability = questions[question_id]["p_yes"][world_id]
    return Random(_seed(task["id"], question_id, "observation")).random() < probability


def cases():
    for family, count in SCENARIOS:
        for index in range(count):
            yield family, public_problem(family, index)
