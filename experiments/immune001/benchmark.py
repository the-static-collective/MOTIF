"""IMMUNE-001 reproducible, source-owned finite benchmark.

All data are synthetic and engineer-designed. Seed split prevents literal
fixture reuse, but families/grammar are shared; not blind external adjudication.
"""
from __future__ import annotations

from collections import Counter
import json
from immune import (inspect, naive_counting_baseline,
                    classical_verifier_baseline)
from oracle import corpus, FAMILIES

DEVELOPMENT_SEEDS = range(0, 10)
HELDOUT_SEEDS = range(200, 240)


def evaluate(items):
    counts = Counter()
    by_family = {}
    errors = []
    for s in items:
        result = inspect(s.records, s.review_ids, s.withdrawn_ids)
        got = result.status[s.target]
        target_promotable = s.expected == "VERIFIED_FINITE"
        guard_promotes = got == "VERIFIED_FINITE"
        naive = naive_counting_baseline(s.records, s.target) == "PROMOTE"
        classical = (classical_verifier_baseline(
            s.records, s.target, s.target in s.review_ids) == "PROMOTE")
        counts["cases"] += 1
        counts["attacks"] += int(s.is_attack)
        counts["exact_status_matches"] += int(got == s.expected)
        counts["guard_false_promotions"] += int(guard_promotes and not target_promotable)
        counts["naive_false_promotions"] += int(naive and not target_promotable)
        counts["classical_false_promotions"] += int(classical and not target_promotable)
        counts["guard_benign_verified_retained"] += int(guard_promotes and target_promotable)
        counts["naive_benign_verified_retained"] += int(naive and target_promotable)
        counts["classical_benign_verified_retained"] += int(classical and target_promotable)
        counts["benign_verifiable"] += int(target_promotable)
        counts["guard_binary_correct"] += int(guard_promotes == target_promotable)
        counts["naive_binary_correct"] += int(naive == target_promotable)
        counts["classical_binary_correct"] += int(classical == target_promotable)
        counts["local_bounded_checks"] += len(result.checks)
        counts["selective_dependency_reviews"] += int(got == "DEPENDENCY_REVIEW")
        if got != s.expected:
            errors.append({"family": s.family, "target": s.target,
                           "expected": s.expected, "got": got})
        family = by_family.setdefault(s.family, Counter())
        family["cases"] += 1
        family["guard_correct"] += int(got == s.expected)
        family["naive_promotions"] += int(naive)
        family["strong_promotions"] += int(classical)
    return {"metrics": dict(sorted(counts.items())),
            "by_family": {k: dict(sorted(v.items()))
                          for k, v in sorted(by_family.items())},
            "errors": errors[:30]}


def benchmark():
    train = evaluate(corpus(DEVELOPMENT_SEEDS))
    test = evaluate(corpus(HELDOUT_SEEDS))
    return {
        "experiment": "MOTIF-IMMUNE-001",
        "claim": "finite source-owned graph integrity and local check",
        "challenge_design": "engineer-authored synthetic twelve-family fixture",
        "seed_policy": {"development": [0, 9],
                        "heldout": [200, 239],
                        "same_attack_families": True},
        "family_count": len(FAMILIES),
        "development": train,
        "heldout": test,
        "security_boundary": "no executions or privileged actions from record payload",
        "caveats": [
            "lineage IDs are synthetic declarations, not authenticated identities",
            "11-point integer equality is not a general mathematical proof",
            "the strong classical finite-check baseline is expected to tie binary promotion",
            "no natural-world adversarial data, LLMs, online learning or autonomous immunity",
            "no evidence of historical novelty, recursive improvement, or external validity",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
