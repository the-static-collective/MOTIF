"""Hand-built synthetic world with a question that unlocks cheaper questions.

Three unknown bits: mode, A, B. The answer is XOR(A,B). Learning mode
has zero immediate answer value, but unlocks two cheap complementary tests.
"""
import json
from dataclasses import asdict
from forest import LivingForest, Road
from multiplex import Hypothesis


def fixture():
    hypotheses = [
        Hypothesis(f"{mode}{left}{right}",
                   "YES" if left != right else "NO", 1.0)
        for mode in "01" for left in "01" for right in "01"
    ]
    names = [h.name for h in hypotheses]
    def signal(position):
        return {name: name[position] for name in names}
    roads = [
        Road("SCOUT", "ASK", 0.20, signal(0), "scout-source",
             prompt="Which mode makes the next tests available?"),
        Road("BAIT", "VERIFY", 0.60,
             {name: "YES" if name == "000" else "NO" for name in names},
             "bait-source", prompt="Are we in the rare standout state?"),
        Road("GLOBAL_A", "ASK", 1.00, signal(1), "full-a"),
        Road("GLOBAL_B", "ASK", 1.00, signal(2), "full-b"),
        Road("DUP_SCOUT", "ASK", 0.25, signal(0), "scout-source",
             prompt="Repeat the original source verbatim."),
        Road("BLOCKED", "VERIFY", 0.01,
             {name: ("YES" if name[1] != name[2] else "NO") for name in names},
             "privileged-oracle", allowed=False),
    ]
    for mode in "01":
        roads.append(Road(f"FAST_A_{mode}", "ASK", 0.35, signal(1),
                          f"fast-a-{mode}", requires=(("SCOUT", mode),),
                          prompt=f"Check the left port in mode {mode}."))
        roads.append(Road(f"FAST_B_{mode}", "ANSWER", 0.35, signal(2),
                          f"fast-b-{mode}", requires=(("SCOUT", mode),),
                          prompt=f"Compute the right port in mode {mode}."))
    return hypotheses, roads


def trace(hidden="101"):
    hypotheses, roads = fixture()
    forest = LivingForest(hypotheses, roads)
    transcripts = []
    while True:
        plan, result = forest.run_synthetic_round(lambda road: road.predicted[hidden])
        transcripts.append({
            "status_before": plan.status,
            "selected": plan.selected,
            "tentative_answer": plan.tentative_answer,
            "expected_final_accuracy": plan.expected_final_accuracy,
            "forecast_branches_not_observations": [asdict(x) for x in plan.forecasts],
            "received_separate_synthetic_evidence": asdict(result) if result else None,
        })
        if result is None:
            break
    return {
        "hidden_world_evaluator_only": hidden,
        "declared_true_answer_for_scoring": next(h.answer for h in hypotheses if h.name == hidden),
        "result": forest.plan().tentative_answer,
        "remaining_hypotheses": forest.live,
        "actual_spend": forest.spent,
        "rounds_used": forest.rounds_used,
        "counterexamples": forest.counterexamples,
        "steps": transcripts,
        "synthetic_only": True,
        "outside_world_authority": False,
    }


if __name__ == "__main__":
    print(json.dumps(trace(), indent=2, sort_keys=True))
