"""Independent classical reference for LEGIT-001's exact finite problem.

This evaluator does not import the MOTIF router. It exhaustively enumerates
read-only decision trees over public hypotheses and synthetic query outcomes.
Equality with MOTIF is expected; it is NOT an algorithmic victory.
"""
from __future__ import annotations


def reference(task, history=(), depth=2):
    worlds = tuple(task["worlds"])
    prior = [w["prior"] for w in worlds]
    queries = {q["id"]: q for q in task["queries"]}
    spent = 0
    for observation in history:
        q = queries[observation["question"]]
        spent += q["cost"]
        prior = [v * (q["p_yes"][w["id"]] if observation["yes"] else
                      1 - q["p_yes"][w["id"]])
                 for w, v in zip(worlds, prior)]
        norm = sum(prior)
        if norm <= 0:
            raise ValueError("Impossible history")
        prior = [x / norm for x in prior]
    unavailable = {obs["question"] for obs in history}
    options = [q for q in task["queries"] if q["id"] not in unavailable]
    remaining_budget = task["max_total_cost"] - spent
    remaining_depth = min(depth, task["max_questions"] - len(history))

    def solve(weights, questions, money, steps):
        p = sum(weight for world, weight in zip(worlds, weights) if world["answer"])
        outcomes = [("ABSTAIN", task["abstain_loss"]),
                    ("PREDICT_FALSE", p), ("PREDICT_TRUE", 1 - p)]
        best_action, best_risk = min(outcomes, key=lambda item: item[1])
        best_question = None
        if steps <= 0:
            return best_action, best_question, best_risk
        for q in sorted(questions, key=lambda row: row["id"]):
            if q["cost"] > money + 1e-10:
                continue
            risk = q["cost"]
            for value in (False, True):
                likelihoods = [q["p_yes"][w["id"]] if value else
                               1 - q["p_yes"][w["id"]] for w in worlds]
                weighted = [x * y for x, y in zip(weights, likelihoods)]
                prob = sum(weighted)
                if prob > 1e-14:
                    normalized = [x / prob for x in weighted]
                    other = [x for x in questions if x["id"] != q["id"]]
                    risk += prob * solve(normalized, other, money - q["cost"],
                                         steps - 1)[2]
            if risk < best_risk - 1e-10:
                best_action, best_question, best_risk = "ASK_SYNTHETIC", q["id"], risk
        return best_action, best_question, best_risk

    return solve(prior, options, remaining_budget, remaining_depth)
