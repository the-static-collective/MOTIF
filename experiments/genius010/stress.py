"""GENIUS-010 after-first-inspection stress sweep.

This additional seed range was chosen *after* the first six-seed results
were inspected. It is an OPEN EXPLORATORY ROBUSTNESS CHECK, not a second
blind preregistered validation or evidence of external generalization.
"""
from __future__ import annotations
import json
from collections import Counter
from convergence import REGIMES, evaluate_world

POSTHOC_SEEDS = tuple(range(101131, 101171))  # 40 independent PRNG starts


def run() -> dict:
    rows = {}
    for regime in REGIMES:
        verdicts = [
            evaluate_world(seed, regime) for seed in POSTHOC_SEEDS
        ]
        counts = Counter(k for r in verdicts
                         for k in r["verdict"]["conditional_candidates"])
        holds = Counter(c["status"] for r in verdicts
                        for c in r["verdict"]["candidates"]
                        if c["status"].startswith("HOLD_")
                        and c["status"] != "HOLD_CONVERGENCE_NOT_ESTABLISHED")
        rows[regime] = {
            "cases": len(verdicts),
            "conditional_bridge_frequency": dict(sorted(counts.items())),
            "any_bridge_cases": sum(
                bool(r["verdict"]["conditional_candidates"]) for r in verdicts),
            "source_hold_codes": dict(sorted(holds.items())),
            "withheld_excluded": sum(
                r["withheld_not_scored_or_ingested"] for r in verdicts),
        }
    return {
        "status": "POSTHOC_EXPLORATORY_NOT_INDEPENDENT_BLIND",
        "seed_range": [POSTHOC_SEEDS[0], POSTHOC_SEEDS[-1]],
        "experimental_worlds": len(POSTHOC_SEEDS)*len(REGIMES),
        "regimes": rows,
        "disposition": "Never choose new thresholds from these cases and rebrand them as a prespecified holdout.",
        "no_external_action": True,
    }


if __name__=="__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
