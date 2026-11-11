"""FIRE-006 new-seed, preregistered and all-round price-of-revision study."""
from __future__ import annotations
import json
from math import sqrt
from portfolio import evaluate, POLICIES, REGIMES, N_STEPS

TEST = range(106000, 106160)
COMPARE = ("proximal3", "fixed_share3", "exp3", "fire006_no_rollback", "equal3")
FIELDS = (
    "brier", "log_loss", "revision_price", "total_loss_with_price",
    "coverage", "overconfident_errors", "effective_hypotheses",
    "revisions", "rollback_count", "rejected_proposals",
    "early_post48_brier", "late_post48_brier",
)


def mean(values):
    return sum(values) / len(values)


def paired(left, right, key="total_loss_with_price"):
    deltas = [a[key] - b[key] for a, b in zip(left, right)]
    n = len(deltas)
    average = mean(deltas)
    std = sqrt(sum((x - average) ** 2 for x in deltas) / (n - 1))
    ci = 1.96 * std / sqrt(n)
    return {"mean": round(average, 8),
            "approx_95pct_interval": [round(average - ci, 8),
                                       round(average + ci, 8)]}


def summarize(rows):
    out = {key: round(mean([r[key] for r in rows]), 8) for key in FIELDS}
    accuracies = [r["selective_accuracy"] for r in rows
                  if r["selective_accuracy"] is not None]
    out["selective_accuracy"] = (
        round(mean(accuracies), 8) if accuracies else None)
    return out


def experiment():
    results = {"experiment": "FIRE-006", "scope": "synthetic research only",
               "worlds_per_regime": len(TEST),
               "test_seeds": [TEST.start, TEST.stop - 1],
               "steps_per_world": N_STEPS, "regimes": {}}
    for regime in REGIMES:
        trials = [evaluate(seed, regime) for seed in TEST]
        by_policy = {p: [d[p] for d in trials] for p in POLICIES}
        results["regimes"][regime] = {
            "policy_means": {
                p: summarize(by_policy[p]) for p in POLICIES
            },
            "paired_fire006_minus": {
                p: paired(by_policy["fire006"], by_policy[p]) for p in COMPARE
            },
            "paired_raw_brier_fire006_minus_proximal": paired(
                by_policy["fire006"], by_policy["proximal3"], "brier"),
            "paired_early_post48_fire006_minus_proximal": paired(
                by_policy["fire006"], by_policy["proximal3"],
                "early_post48_brier"),
            "paired_late_post48_fire006_minus_proximal": paired(
                by_policy["fire006"], by_policy["proximal3"],
                "late_post48_brier"),
            "first_world_revision_receipts": by_policy["fire006"][0]["receipts"],
        }
    results["macro_primary"] = {p: round(mean([
        results["regimes"][r]["policy_means"][p]["total_loss_with_price"]
        for r in REGIMES]), 8) for p in POLICIES}
    results["macro_raw_brier"] = {p: round(mean([
        results["regimes"][r]["policy_means"][p]["brier"]
        for r in REGIMES]), 8) for p in POLICIES}
    return results


if __name__ == "__main__":
    print(json.dumps(experiment(), indent=2, sort_keys=True))
