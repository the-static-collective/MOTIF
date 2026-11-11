"""Frozen FIRE-005 prequential 960-world study, 92,160 labeled decisions.

The full 96-step Brier includes every prediction, including HOLDs and bad
alarms. No model can access hidden truth or source reliability before its
forecast. Separate synthetic verification follows all current predictions.
"""
from __future__ import annotations
import json
from math import sqrt

from discernment import N_STEPS, REGIMES, MODEL_NAMES, evaluate

TEST = range(81000, 81160)
COMPARE = ("hedge2", "bocpd", "hedge", "fire004", "regret_only")
NUMERIC = (
    "brier", "log_loss", "coverage", "high_confidence_wrong",
    "early_post_48_brier", "late_post_48_brier",
)


def average(values):
    return sum(values) / len(values)


def paired(x, y):
    ds = [left - right for left, right in zip(x, y)]
    n = len(ds)
    mean = average(ds)
    var = sum((d - mean) ** 2 for d in ds) / (n - 1)
    err = 1.96 * sqrt(var / n)
    return {
        "delta": round(mean, 8),
        "approx_95pct_interval": [
            round(mean - err, 8), round(mean + err, 8)
        ]
    }


def stats(rows):
    result = {name: round(average([r[name] for r in rows]), 8)
              for name in NUMERIC}
    accuracies = [r["selective_accuracy"] for r in rows
                  if r["selective_accuracy"] is not None]
    result["mean_selective_accuracy"] = round(average(accuracies), 8) if accuracies else None
    return result


def experiment():
    summary = {
        "experiment": "FIRE-005",
        "scope": "engineer-authored synthetic streams only",
        "prequential_steps": N_STEPS,
        "test_seed_range": [TEST.start, TEST.stop - 1],
        "worlds_per_regime": len(TEST),
        "regimes": {}
    }
    for regime in REGIMES:
        trials = [evaluate(seed, regime) for seed in TEST]
        sets = {policy: [world[policy] for world in trials]
                for policy in MODEL_NAMES}
        switches = [len(r["switch_steps"]) for r in sets["fire005"]]
        rollbacks = [len(r["rollback_steps"]) for r in sets["fire005"]]
        initial_change = [min((step - 48 for step in row["switch_steps"]
                              if 48 <= step <= 64), default=None)
                          for row in sets["fire005"]]
        early = [d for d in initial_change if d is not None]
        summary["regimes"][regime] = {
            "policies": {policy: stats(sets[policy]) for policy in MODEL_NAMES},
            "paired_fire005_minus": {
                policy: paired(
                    [r["brier"] for r in sets["fire005"]],
                    [r["brier"] for r in sets[policy]]
                ) for policy in COMPARE
            },
            "paired_early_post_fire005_minus_hedge2": paired(
                [r["early_post_48_brier"] for r in sets["fire005"]],
                [r["early_post_48_brier"] for r in sets["hedge2"]]
            ),
            "paired_late_post_fire005_minus_hedge2": paired(
                [r["late_post_48_brier"] for r in sets["fire005"]],
                [r["late_post_48_brier"] for r in sets["hedge2"]]
            ),
            "method_revisions": {
                "switches_per_world": round(average(switches), 8),
                "rollbacks_per_world": round(average(rollbacks), 8),
                "fraction_switching_in_48_to_64": round(
                    len(early) / len(TEST), 8),
                "mean_switch_delay_conditional_on_switch": (
                    round(average(early), 8) if early else None),
            }
        }
    summary["macro_brier"] = {
        p: round(average(
            [summary["regimes"][regime]["policies"][p]["brier"]
             for regime in REGIMES]), 8)
        for p in MODEL_NAMES
    }
    return summary


if __name__ == "__main__":
    print(json.dumps(experiment(), indent=2, sort_keys=True))
