"""Inspect a synergistic two-avenue discovery and a greedy failure."""
import json
from dataclasses import asdict
from multiplex import Avenue, Hypothesis, best_answer, choose, execute_synthetic, revise


def fixture():
    hypotheses = [
        Hypothesis(name=bits, answer=("YES" if bits.count("1") == 1 else "NO"))
        for bits in ("00", "01", "10", "11")
    ]
    avenues = [
        Avenue("LEFT", "ASK", 1.0, {h.name: h.name[0] for h in hypotheses}, "port-left", "What is the first port?"),
        Avenue("RIGHT", "ANSWER", 1.0, {h.name: h.name[1] for h in hypotheses}, "independent-model", "Compute the second port."),
        Avenue("BAIT", "VERIFY", 1.0, {h.name: str(h.name == "00") for h in hypotheses}, "diagnostic", "Check the standout state."),
        Avenue("DUPLICATE_LEFT", "ASK", 1.0, {h.name: h.name[0] for h in hypotheses}, "port-left", "Repeat first port."),
    ]
    return hypotheses, avenues


if __name__ == "__main__":
    hypotheses, avenues = fixture()
    one = choose(hypotheses, avenues, max_parallel=1)
    multi = choose(hypotheses, avenues, max_parallel=2)
    hidden = "01"  # evaluator-only truth; not passed to choose
    observations = execute_synthetic(multi, avenues, lambda a: a.predicted[hidden])
    status, survivors = revise(hypotheses, avenues, observations)
    print(json.dumps({
        "single_step": asdict(one),
        "joint_portfolio": asdict(multi),
        "synthetic_observations": observations,
        "revision_status": status,
        "resulting_answer": best_answer(survivors),
        "synthetic_only": True,
    }, indent=2, sort_keys=True))

