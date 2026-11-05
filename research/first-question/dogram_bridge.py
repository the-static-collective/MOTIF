"""Opt-in MOTIF-Q-001 -> native Dogram finite probe-cost analysis.

No network, install step, dynamic code download, runtime autonomy, or authority
handoff. Caller supplies a trusted LOCAL Dogram checkout explicitly. MOTIF owns
question selection; Dogram only computes a declared information/cost receipt.
"""
from __future__ import annotations

from dataclasses import asdict
from itertools import combinations
from pathlib import Path
import argparse
import json
import sys

from question import dogram_probe_family


def analyze_with_dogram(dogram_root: str) -> dict[str, object]:
    root = Path(dogram_root).resolve()
    if not (root / "dogram" / "probe_cost_pareto.py").is_file():
        raise ValueError("Pass a local Dogram checkout containing probe_cost_pareto.py")
    # Explicit local source path: never fetch, install or auto-select a body.
    sys.path.insert(0, str(root))
    try:
        from dogram.probe_cost_pareto import analyze_probe_costs
        from dogram.anti_collapse_reachability import analyze_collapse
    finally:
        sys.path.pop(0)

    payload = dogram_probe_family()
    states = tuple(payload["states"])
    probes = {name: tuple(values)
              for name, values in payload["probes"].items()}
    costs = payload["costs"]
    labels = dict(zip(states, payload["target_labels"]))
    pair_receipts = []
    for left, right in combinations(states, 2):
        if labels[left] == labels[right]:
            continue  # Only ambiguity relevant to the declared target.
        receipt = analyze_probe_costs(states, probes, costs, (left, right))
        pair_receipts.append({
            "target_distinguishing_pair": [left, right],
            "dogram_calculation": asdict(receipt),
        })
    # The active MOTIF probe may leave mechanism identity unresolved even
    # when its outcomes suffice for the one declared target. Dogram accounts
    # for every lost distinction without grading its semantic importance.
    from question import select_question, target_trial, candidate_trials
    chosen = select_question(tuple(states), candidate_trials(),
                             target_trial(), budget=1)
    collapsed = tuple(probes[chosen.id]) if chosen else ()
    rich = tuple(tuple(probes[name][i] for name in sorted(probes))
                 for i in range(len(states)))
    collapse = analyze_collapse(states, rich, collapsed) if chosen else None
    target_sufficient = bool(chosen) and all(
        collapsed[i] != collapsed[j]
        or payload["target_labels"][i] == payload["target_labels"][j]
        for i in range(len(states)) for j in range(i + 1, len(states))
    )
    return {
        "schema": "motif.dogram-calculate-only/v0",
        "collapse_analysis": {
            "chosen_probe": chosen.id if chosen else None,
            "dogram_calculation": asdict(collapse) if collapse else None,
            "target_relative_sufficiency": target_sufficient,
        },
        "source": payload,
        "pair_receipts": pair_receipts,
        "boundary": (
            "Dogram evaluates declared finite partitions and costs only; "
            "MOTIF retains query choice, the fixture oracle remains separate, "
            "and no truth, evidence, causality or permission is conferred."
        ),
    }


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--dogram-root", required=True,
                     help="Trusted local checkout of the Dogram repository")
    args = cli.parse_args()
    print(json.dumps(analyze_with_dogram(args.dogram_root), indent=2))
