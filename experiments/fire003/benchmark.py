"""FIRE-003 matched-world fixed-exposure calibration and bounded task results."""
from __future__ import annotations
import json
from math import sqrt
from smoke import REGIMES, POLICIES, BUDGET, run, fixed_forecast_audit

TEST = range(53000, 53300)


def mean(xs):
    return sum(xs) / len(xs)


def interval(xs):
    m = mean(xs)
    sd = sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))
    e = 1.96 * sd / sqrt(len(xs))
    return {"mean": round(m, 6), "approx_95pct_interval":
            [round(m - e, 6), round(m + e, 6)]}


def measure():
    output = {"experiment": "FIRE-003", "test_seeds": [TEST.start, TEST.stop - 1],
              "worlds_per_regime": len(TEST), "budget": BUDGET,
              "scope": "engineer-authored synthetic source registry and truth",
              "regimes": {}}
    for regime in REGIMES:
        exposures = [fixed_forecast_audit(s, regime) for s in TEST]
        trials = {p: [run(s, regime, p) for s in TEST] for p in POLICIES}
        fixed = {
            kind: {metric: round(mean([r[kind][metric] for r in exposures]), 6)
                   for metric in ("brier", "overconfident_errors", "held",
                                  "dependence_detected")}
            for kind in ("naive", "guarded", "oracle_roots")
        }
        values = {
            policy: {metric: round(mean([r[metric] for r in trials[policy]]), 6)
                     for metric in ("certified_value", "certified_count",
                                    "failed_verifications", "holds",
                                    "dependence_alerts", "unverifiable_alerts",
                                    "confident_failures", "verified_learning_events",
                                    "operations_spent", "audit_steps", "net_value")}
            for policy in POLICIES
        }
        output["regimes"][regime] = {
            "fixed_exposure": fixed,
            "paired_guarded_minus_naive_brier": interval(
                [r["guarded"]["brier"] - r["naive"]["brier"]
                 for r in exposures]),
            "task_outcomes": values,
            "paired_online_minus_frozen_net_value": interval(
                [a["net_value"] - b["net_value"] for a, b in
                 zip(trials["guarded_online"], trials["guarded_frozen"])]),
            "paired_guarded_online_minus_naive_online_net_value": interval(
                [a["net_value"] - b["net_value"] for a, b in
                 zip(trials["guarded_online"], trials["naive_online"])]),
        }
    return output


if __name__ == "__main__":
    print(json.dumps(measure(), indent=2, sort_keys=True))
