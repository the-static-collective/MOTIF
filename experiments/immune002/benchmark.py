"""IMMUNE-002 research portfolio: stronger classical controls and full task utility.

The measured outputs are results on engineer-authored inert fixtures, not
evidence of deployed prompt-injection immunity or model behavior.
"""
from __future__ import annotations

from collections import Counter
import json

from giants import build_field, compare_revision, authorized
from reference import brute_support, reference_gate
from oracle import (REASON_FAMILIES, ACTION_FAMILIES, reason_case, action_case)

DEV_SEEDS = range(0, 8)
TEST_SEEDS = range(300, 340)


def score(seeds) -> dict:
    reason_counts = Counter()
    action_counts = Counter()
    reason_families = {}
    action_families = {}
    errors = []
    for seed in seeds:
        for family in REASON_FAMILIES:
            s = reason_case(family, seed)
            before = build_field(s.sources, s.rules, s.before)
            after = build_field(s.sources, s.rules, s.after)
            revised = compare_revision(before, after)
            reference = brute_support(s.sources, s.rules, s.after)
            correct_status = after.status[s.target] == s.expected
            equal_reference = after.environments == reference
            # Deliberately weak document-majority / claimed-authority control.
            target_statement = next(
                (r.statement for r in s.sources if r.id == s.target), None)
            alleged = (any(r.claimed_authority in ("PROVEN", "SYSTEM_VERIFIED")
                           for r in s.sources)
                       or (target_statement is not None and sum(
                           r.statement == target_statement
                           for r in s.sources) >= 3))
            status_admitted = bool(after.environments[s.target])
            reason_counts["cases"] += 1
            reason_counts["adversarial"] += int(s.is_attack)
            reason_counts["expected_status"] += int(correct_status)
            reason_counts["strong_reference_environments_agree"] += int(equal_reference)
            reason_counts["verified_or_rule_supported"] += int(status_admitted)
            reason_counts["weak_unverified_promotions"] += int(alleged and not status_admitted)
            reason_counts["alternative_retained"] += int(
                s.target in revised["alternative_retained"])
            reason_counts["support_lost"] += int(s.target in revised["lost"])
            reason_counts["correctly_preserved_supported_novelty"] += int(
                (not s.is_attack) and status_admitted)
            if not correct_status or not equal_reference:
                errors.append({"seed": seed, "family": family,
                               "got": after.status[s.target],
                               "expected": s.expected,
                               "reference_equal": equal_reference})
            item = reason_families.setdefault(family, Counter())
            item["cases"] += 1
            item["statuses_match"] += int(correct_status)
            item["reference_agrees"] += int(equal_reference)
        for family in ACTION_FAMILIES:
            a = action_case(family, seed)
            got = authorized(a.proposal, a.grants, a.used)
            ref = reference_gate(a.proposal, a.grants, a.used)
            action_counts["cases"] += 1
            action_counts["adversarial"] += int(a.is_attack)
            action_counts["correct_policy_decisions"] += int(got == a.expected)
            action_counts["classical_acl_agreements"] += int(got == ref)
            action_counts["unauthorized_actions_approved"] += int(
                a.is_attack and got.startswith("ALLOW"))
            action_counts["benign_actions_allowed"] += int(
                not a.is_attack and got.startswith("ALLOW"))
            action_counts["benign_actions_total"] += int(not a.is_attack)
            if got != a.expected or got != ref:
                errors.append({"seed": seed, "family": family,
                               "got": got, "expected": a.expected,
                               "reference": ref})
            item = action_families.setdefault(family, Counter())
            item["cases"] += 1
            item["correct"] += int(got == a.expected)
            item["classical_control_agrees"] += int(got == ref)
    return {
        "reason": {"summary": dict(sorted(reason_counts.items())),
                   "per_family": {k: dict(sorted(v.items()))
                                  for k, v in sorted(reason_families.items())}},
        "actions": {"summary": dict(sorted(action_counts.items())),
                    "per_family": {k: dict(sorted(v.items()))
                                   for k, v in sorted(action_families.items())}},
        "errors": errors[:20],
    }


def benchmark() -> dict:
    return {
        "experiment": "IMMUNE-002_SHOULDERS_OF_GIANTS",
        "design": "Source-owned, bounded, deterministic, synthetic and inert",
        "independent_sources": "No — cases are engineer-authored",
        "method_portfolio": [
            "Doyle 1979 justification-based truth maintenance",
            "de Kleer 1986 bounded assumption-environment reasoning",
            "classical least fixed point inference / Datalog semantics",
            "exact symbolic equality for bounded integer polynomials",
            "source-to-sink information-flow discipline / reference monitor",
            "independent exhaustive subset truth-maintenance control",
            "independent exact-argument classical ACL control",
        ],
        "evaluation_seed_ranges": {
            "development": [min(DEV_SEEDS), max(DEV_SEEDS)],
            "evaluation": [min(TEST_SEEDS), max(TEST_SEEDS)],
            "families_shared": True,
        },
        "development": score(DEV_SEEDS),
        "heldout": score(TEST_SEEDS),
        "limitations": [
            "no LLM read tool; all injection-looking strings remain inert",
            "truth is defined by operator-authored rule semantics and exact grammar",
            "no source authentication or cryptographic authorization",
            "grants only simulate a trusted runtime policy boundary",
            "rule antecedents are not a substitute for independently proved implication",
            "strong classical baselines are expected to tie",
            "no externally authored novel attack family or adaptive generalization",
            "no direct actions, payments, file writes, network or private-data access",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
