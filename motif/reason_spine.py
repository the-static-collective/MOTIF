"""MOTIF Reasoning Spine 001 — inspectable, finite, evidence-first coordination.

This is a conservative planner over human-authored hypotheses, not an LLM,
an oracle, a verified causal engine, or an autonomous software engineer.
"""
from __future__ import annotations

import math
from collections import defaultdict

ROLES = ("explorer", "skeptic", "architect", "historian", "governor")
PHASES = ("OBSERVE", "HYPOTHESIZE", "PROBE", "REVISE", "PLAN", "VERIFY")
VALID_OUTCOMES = {"yes", "no", "unknown"}


class CaseError(ValueError):
    pass


def _entropy(counts):
    total = sum(counts)
    if not total:
        return 0.
    return -sum((n / total) * math.log2(n / total) for n in counts if n)


def information_gain(hypotheses, test_id):
    """A classical equal-prior, categorical information-gain baseline."""
    if len(hypotheses) < 2:
        return 0.
    groups = defaultdict(int)
    for h in hypotheses:
        groups[h["predictions"].get(test_id, "unknown")] += 1
    return _entropy(groups.values())


def validate_case(case):
    if not isinstance(case, dict) or not isinstance(case.get("question"), str):
        raise CaseError("Explicit question required")
    if not case["question"].strip() or not isinstance(case.get("goal"), str) or not case["goal"].strip():
        raise CaseError("Question and consequential goal required")
    hypotheses, tests, reports = case.get("hypotheses"), case.get("tests"), case.get("reports", [])
    if not isinstance(hypotheses, list) or not 1 <= len(hypotheses) <= 32:
        raise CaseError("1–32 authored hypotheses required")
    if not isinstance(tests, list) or len(tests) > 32 or not isinstance(reports, list) or len(reports) > 256:
        raise CaseError("Invalid or excessive tests/reports")
    hids, tids = set(), set()
    for h in hypotheses:
        if (not isinstance(h, dict) or not isinstance(h.get("id"), str)
                or not h["id"] or h["id"] in hids or not isinstance(h.get("predictions"), dict)):
            raise CaseError("Invalid or duplicate hypothesis")
        hids.add(h["id"])
        if any(v not in VALID_OUTCOMES for v in h["predictions"].values()):
            raise CaseError("Predictions must be yes/no/unknown")
    for t in tests:
        if not isinstance(t, dict) or not isinstance(t.get("id"), str) or not t["id"] or t["id"] in tids:
            raise CaseError("Invalid or duplicate probe")
        tids.add(t["id"])
        for name in ("cost", "risk"):
            x = t.get(name, 0)
            if not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x) or x < 0:
                raise CaseError("Probe costs/risks must be nonnegative finite numbers")
    if any(key not in tids for h in hypotheses for key in h["predictions"]):
        raise CaseError("Unrecognized probe in hypothesis predictions")
    for r in reports:
        if (not isinstance(r, dict) or not isinstance(r.get("source_root"), str)
                or not r["source_root"] or r.get("test") not in tids
                or r.get("outcome") not in VALID_OUTCOMES
                or r.get("status", "reported") not in {"reported", "reviewed"}):
            raise CaseError("Invalid report record")
        if r.get("status") == "reviewed" and not isinstance(r.get("review_receipt"), str):
            raise CaseError("Reviewed reports require an explicit review receipt")
    return hypotheses, tests, reports


def source_state(reports):
    """Immutable input preserved; latest statement by same claimed source is one vote.

    REVIEWED means a review is *declared*, not an authenticated proof of truth.
    """
    by_source = {}
    events = []
    for i, r in enumerate(reports):
        key = (r["source_root"], r["test"])
        if key in by_source and by_source[key]["outcome"] != r["outcome"]:
            events.append({"index": i, "event": "SOURCE_REVISION", "test": r["test"],
                           "source_root": r["source_root"]})
        by_source[key] = r
    grouped = defaultdict(list)
    for r in by_source.values():
        grouped[r["test"]].append(r)
    contested = [tid for tid, rows in grouped.items()
                 if len({r["outcome"] for r in rows}) > 1]
    declared_reviewed = {}
    for tid, rows in grouped.items():
        current = [r for r in rows if r.get("status") == "reviewed"]
        if current and len({r["outcome"] for r in current}) == 1 and tid not in contested:
            declared_reviewed[tid] = current[0]["outcome"]
    return {
        "latest": grouped,
        "contested": sorted(contested),
        "declared_reviewed": declared_reviewed,
        "events": events,
        "source_claims": len(by_source),
    }


def _remaining(hypotheses, reviewed):
    return [h for h in hypotheses if all(
        h["predictions"].get(test_id, "unknown") in (outcome, "unknown")
        for test_id, outcome in reviewed.items()
    )]


def analyze(case, lenses=None, policy="spine"):
    """Build a branch-aware reasoning plan using only user-entered structured data.

    A branch lens influences the *question strategy* but never imports or runs
    source code and never changes a report into verified truth.
    """
    hypotheses, tests, reports = validate_case(case)
    if policy not in {"fixed", "classical_ig", "spine"}:
        raise CaseError("Policy must be a measured, implemented planner")
    lenses = lenses or []
    for lens in lenses:
        if not isinstance(lens, dict) or lens.get("admission") != "NONE" or lens.get("execution") != "NONE":
            raise CaseError("Only non-executing held lenses permitted")
    state = source_state(reports)
    remaining = _remaining(hypotheses, state["declared_reviewed"])
    available = [t for t in tests if t["id"] not in state["declared_reviewed"]]
    candidates = []
    for test in available:
        ig = information_gain(remaining, test["id"])
        cost, risk = test.get("cost", 0), test.get("risk", 0)
        score = (ig if policy != "fixed" else 0) - (cost + risk if policy == "spine" else 0)
        candidates.append({
            "id": test["id"], "classical_information_gain_bits": round(ig, 6),
            "cost": cost, "risk": risk, "selection_score": round(score, 6),
        })
    if policy == "fixed":
        candidates.sort(key=lambda c: next(i for i, t in enumerate(tests) if t["id"] == c["id"]))
    else:
        candidates.sort(key=lambda c: (-c["selection_score"], c["id"]))
    next_probe = candidates[0] if candidates else None
    if policy == "spine" and next_probe and next_probe["selection_score"] <= 0:
        next_probe = None
    if policy == "classical_ig" and next_probe and next_probe["classical_information_gain_bits"] <= 0:
        next_probe = None

    identities = sorted({c for l in lenses for c in l.get("capabilities", [])})
    if not remaining:
        status = "HOLD_MODEL_FALSIFIED"
    elif state["contested"]:
        status = "HOLD_CONTESTED_REPORTS"
    elif len(remaining) == 1 and state["declared_reviewed"]:
        status = "VERIFY_HYPOTHESIS_NOT_TRUTH"
    elif next_probe:
        status = "PROPOSE_PROBE"
    else:
        status = "HOLD_INFORMATION_NOT_WORTH_COST"
    next_question = None
    if "two-doors" in identities and status.startswith(("HOLD_", "PROPOSE_")):
        next_question = {
            "mode": "LET_MOTIF_ASK",
            "question": ("Which independent observation would distinguish these explanations?"
                         if not next_probe else "Would you voluntarily inspect " + next_probe["id"] + "?"),
            "why": "Explicitly improve a consequential choice; reports are not automatic truth",
            "requires_opt_in": True,
        }

    return {
        "schema": "motif.reason-spine/v1",
        "question": case["question"], "goal": case["goal"], "policy": policy,
        "phases": list(PHASES),
        "roles": {
            "explorer": {"authored_hypotheses": [h["id"] for h in hypotheses]},
            "skeptic": {"contested_tests": state["contested"],
                        "counterexample": "NO_MODEL_FITS" if not remaining else None},
            "architect": {"method_admission": "NONE",
                          "candidate_foundry": "method-foundry" in identities},
            "historian": {"source_revisions": state["events"],
                          "no_source_vote_multiplication": True},
            "governor": {"policy": policy, "probe_budget": len(tests),
                         "stop_reason": status},
        },
        "reported_source_claims": state["source_claims"],
        "declared_reviewed_observations_not_authenticated_truth": state["declared_reviewed"],
        "remaining_hypotheses": [h["id"] for h in remaining],
        "ranked_probes": candidates,
        "next_probe": next_probe,
        "next_voluntary_question": next_question,
        "branch_lenses": [{"source": l.get("source"), "capabilities": l.get("capabilities"),
                            "admission": "NONE"} for l in lenses],
        "result": status,
        "external_action": "NONE",
        "truth_status": "NO_REAL_WORLD_CAUSAL_VERIFICATION",
        "human_review_required": True,
    }


def comparison(case, lenses=None):
    """No imaginary LLM or human-performance results; only executed local policies."""
    return {
        "schema": "motif.reason-spine-comparison/v1",
        "fixed_classical": analyze(case, policy="fixed"),
        "strong_classical_ig": analyze(case, policy="classical_ig"),
        "motif_spine": analyze(case, lenses=lenses, policy="spine"),
        "real_pretrained_llm": {"status": "NOT_RUN_REQUIRES_REAL_MODEL_AND_MATCHED_INPUTS"},
        "real_llm_plus_motif": {"status": "NOT_RUN_REQUIRES_REAL_MODEL_AND_MATCHED_INPUTS"},
        "conclusion": "POLICY_OPTIONS_ONLY_NO_CLAIM_OF_OUTPERFORMANCE",
    }
