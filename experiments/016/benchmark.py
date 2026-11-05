"""Frozen eight-world comparison: living forest vs immediate greedy vs fixed policy.

All contestants have identical possible synthetic questions and budget.
The fixed diagnostic is deliberately STRONG and should tie the forest.
"""
import json
from forest import LivingForest
from demo import fixture
from multiplex import Avenue, best_answer, choose, revise


def greedy_world(hidden, hypotheses, roads):
    catalog = {r.name: r for r in roads}
    survivors = tuple(hypotheses)
    observed = {}
    spent = 0.0
    rounds = 0
    selected = []
    for _ in range(2):
        current = [
            r for r in roads if r.allowed and r.name not in observed
            and all(observed.get(source) == signal for source, signal in r.requires)
        ]
        available = [Avenue(r.name, r.kind, r.cost,
                            {h.name: r.predicted[h.name] for h in survivors}, r.origin,
                            r.prompt, r.human, r.allowed) for r in current]
        decision = choose(survivors, available, budget=1.25-spent,
                          max_parallel=2, cost_penalty=0.01)
        if not decision.selected:
            break
        outcome = {name: catalog[name].predicted[hidden] for name in decision.selected}
        status, survivors = revise(survivors, available, outcome)
        if status != "UPDATED":
            raise AssertionError("Greedy comparator unexpectedly contradicted")
        observed.update(outcome)
        spent += decision.total_cost
        rounds += 1
        selected.append(decision.selected)
    return best_answer(survivors)[0], spent, rounds, selected


def fixed_world(hidden, roads):
    # Hard-coded classical diagnostic: ask SCOUT, then ask both unlocked ports.
    catalog = {r.name: r for r in roads}
    observed_mode = catalog["SCOUT"].predicted[hidden]
    a = catalog[f"FAST_A_{observed_mode}"].predicted[hidden]
    b = catalog[f"FAST_B_{observed_mode}"].predicted[hidden]
    answer = "YES" if a != b else "NO"
    return answer, 0.20 + 0.35 + 0.35, 2


def benchmark():
    hypotheses, roads = fixture()
    totals = {
        "living_forest": {"correct": 0, "cost": 0., "rounds": 0},
        "myopic_joint_batch": {"correct": 0, "cost": 0., "rounds": 0},
        "fixed_classical_diagnostic": {"correct": 0, "cost": 0., "rounds": 0},
    }
    per_world = []
    for hidden in (h.name for h in hypotheses):
        truth = next(h.answer for h in hypotheses if h.name == hidden)
        forest = LivingForest(hypotheses, roads)
        moves = []
        for _ in range(2):
            plan, witnessed = forest.run_synthetic_round(lambda r: r.predicted[hidden])
            if witnessed is None:
                break
            moves.append(plan.selected)
        f_answer = best_answer(forest._posterior(forest.live))[0]
        g_answer, g_cost, g_rounds, g_moves = greedy_world(hidden, hypotheses, roads)
        x_answer, x_cost, x_rounds = fixed_world(hidden, roads)
        scored = [
            ("living_forest", f_answer, forest.spent, forest.rounds_used),
            ("myopic_joint_batch", g_answer, g_cost, g_rounds),
            ("fixed_classical_diagnostic", x_answer, x_cost, x_rounds),
        ]
        for label, answer, cost, rounds in scored:
            totals[label]["correct"] += int(answer == truth)
            totals[label]["cost"] += cost
            totals[label]["rounds"] += rounds
        per_world.append({
            "world": hidden, "truth": truth, "forest": f_answer,
            "forest_portfolios": moves, "greedy": g_answer,
            "greedy_portfolios": g_moves, "fixed": x_answer,
        })
    summary = {}
    for label, stats in totals.items():
        summary[label] = {
            "correct_of_8": stats["correct"],
            "accuracy": stats["correct"] / len(hypotheses),
            "mean_query_cost": round(stats["cost"] / len(hypotheses), 8),
            "mean_rounds": stats["rounds"] / len(hypotheses),
        }
    return {
        "fixture": "eight noiseless synthetic worlds, uniform prior; XOR target",
        "equal_budget": 1.25, "maximum_parallel": 2,
        "maximum_inquiry_rounds": 2,
        "results": summary, "per_world": per_world,
        "limitations": [
            "Hand-coded grammar, exact predicted observations, no out-of-grammar worlds",
            "No stochastic evidence, failures, latency, real action or human authority",
            "Fixed classical diagnostic TIES the forest; no algorithmic novelty proven",
            "Controller uses finite exact expectimax, not learned question generation",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
