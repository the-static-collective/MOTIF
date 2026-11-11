"""ORG-001: consent-bound organizational delay diagnostic (stdlib, local-only).

This is a small deterministic counterfactual planner, not an organization CRM,
a causal discovery engine, a predictor trained on organizations, or an agent.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

KINDS = {"approval", "capacity", "resource", "information", "coordination", "care", "unknown"}
STATUSES = {"todo", "active", "waiting", "done"}
AUTHORITY = {"self", "external", "unknown"}


def _days(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value < 36500:
        raise ValueError(f"{context}: require finite, nonnegative days below 36500")
    return float(value)


def _date(value: str, context: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"{context}: expected ISO date") from None


def validate(brief: dict[str, Any]) -> list[str]:
    """Return topological order; reject circular/ambiguous plans before scoring."""
    if not isinstance(brief, dict) or not brief.get("outcome"):
        raise ValueError("one explicit outcome is required")
    today = _date(brief.get("as_of"), "as_of")
    tasks = brief.get("steps")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("steps must be a nonempty list")
    by_id = {}
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str) or not task["id"]:
            raise ValueError("each step needs a nonempty id")
        key = task["id"]
        if key in by_id:
            raise ValueError(f"duplicate step id: {key}")
        by_id[key] = task
        if task.get("status") not in STATUSES:
            raise ValueError(f"{key}: unknown status")
        if task.get("blocker", "unknown") not in KINDS:
            raise ValueError(f"{key}: unknown blocker class")
        _days(task.get("remaining_days"), f"{key}.remaining_days")
        _days(task.get("touch_days", 0), f"{key}.touch_days")
        _days(task.get("observed_wait_days", 0), f"{key}.observed_wait_days")
        if task["status"] == "done" and task["remaining_days"] != 0:
            raise ValueError(f"{key}: done steps must have zero remaining days")
        if task.get("last_verified") and _date(task["last_verified"], f"{key}.last_verified") > today:
            raise ValueError(f"{key}: last_verified is in the future")
        if not isinstance(task.get("depends_on", []), list):
            raise ValueError(f"{key}: dependencies must be a list")
    order: list[str] = []
    marks: dict[str, int] = {}
    def visit(node: str) -> None:
        if node not in by_id:
            raise ValueError(f"unknown dependency: {node}")
        if marks.get(node) == 1:
            raise ValueError(f"dependency cycle involving {node}")
        if marks.get(node) == 2:
            return
        marks[node] = 1
        for prior in by_id[node].get("depends_on", []):
            if not isinstance(prior, str):
                raise ValueError("dependency id must be a string")
            visit(prior)
        marks[node] = 2
        order.append(node)
    for key in by_id:
        visit(key)
    ends = brief.get("targets")
    if not isinstance(ends, list) or not ends or any(x not in by_id for x in ends):
        raise ValueError("targets must list existing outcome step ids")
    for proposal in brief.get("interventions", []):
        if not isinstance(proposal, dict) or not proposal.get("id") or not proposal.get("hypothesis"):
            raise ValueError("each intervention needs id and explicit hypothesis")
        if proposal.get("authority") not in AUTHORITY:
            raise ValueError("intervention authority must be self/external/unknown")
        if not isinstance(proposal.get("changes"), list) or not proposal["changes"]:
            raise ValueError("intervention needs at least one modeled change")
        for c in proposal["changes"]:
            if c.get("step_id") not in by_id:
                raise ValueError("intervention references unknown step")
            _days(c.get("new_remaining_days"), "intervention new_remaining_days")
            task = by_id[c["step_id"]]
            if task["status"] == "done" and c["new_remaining_days"] != 0:
                raise ValueError("cannot rewrite completed history")
            if c["new_remaining_days"] > task["remaining_days"]:
                raise ValueError("ORG-001 proposals model reductions only")
            if task.get("non_negotiable_gate") and c["new_remaining_days"] == 0 and task["remaining_days"] > 0:
                raise ValueError("cannot model bypass of non-negotiable gate")
    return order


def _schedule(brief: dict[str, Any], order: list[str], changes: dict[str, float] | None = None) -> dict[str, Any]:
    by_id = {t["id"]: t for t in brief["steps"]}
    finish: dict[str, float] = {}
    predecessor: dict[str, str | None] = {}
    for key in order:
        deps = by_id[key].get("depends_on", [])
        pred = max(deps, key=lambda x: finish[x]) if deps else None
        predecessor[key] = pred
        own = changes.get(key, by_id[key]["remaining_days"]) if changes else by_id[key]["remaining_days"]
        finish[key] = (finish[pred] if pred else 0.0) + own
    terminal = max(brief["targets"], key=lambda x: finish[x])
    path = []
    node = terminal
    while node is not None:
        path.append(node)
        node = predecessor[node]
    path.reverse()
    return {"forecast_days": round(finish[terminal], 3), "critical_path": path, "earliest_finish_by_step": {k: round(v, 3) for k, v in finish.items()}}


def analyze(brief: dict[str, Any]) -> dict[str, Any]:
    """Diagnostic and explicitly conditional interventions; never takes action."""
    order = validate(brief)
    today = _date(brief["as_of"], "as_of")
    baseline = _schedule(brief, order)
    tasks = {t["id"]: t for t in brief["steps"]}
    unresolved = [t for t in brief["steps"] if t["status"] != "done"]
    queues = defaultdict(lambda: {"count": 0, "observed_wait_days": 0.0})
    issues = []
    for t in brief["steps"]:
        key = t["id"]
        if t["status"] == "done" and not t.get("evidence_refs"):
            issues.append(f"{key}: claimed done, no evidence reference; independent confirmation needed")
        if t["status"] != "done":
            cls = t.get("blocker", "unknown")
            queues[cls]["count"] += 1
            queues[cls]["observed_wait_days"] += float(t.get("observed_wait_days", 0))
            if not t.get("owner"):
                issues.append(f"{key}: missing responsible owner")
            if t.get("last_verified"):
                age = (today - _date(t["last_verified"], f"{key}.last_verified")).days
                if age > brief.get("stale_after_days", 7):
                    issues.append(f"{key}: {age} days since last verification; recheck before relying on forecast")
            else:
                issues.append(f"{key}: no dated verification; forecast is provisional")
    proposals = []
    for p in brief.get("interventions", []):
        changes = {c["step_id"]: float(c["new_remaining_days"]) for c in p["changes"]}
        after = _schedule(brief, order, changes)
        gain = round(max(0.0, baseline["forecast_days"] - after["forecast_days"]), 3)
        requires_review = p["authority"] != "self" or any(tasks[k].get("non_negotiable_gate") for k in changes)
        proposals.append({
            "id": p["id"], "hypothesis": p["hypothesis"], "authority": p["authority"],
            "modeled_days_saved": gain, "scenario_finish_days": after["forecast_days"],
            "new_critical_path": after["critical_path"],
            "status": "HOLD_FOR_HUMAN_AUTHORITY" if requires_review else "PROPOSAL_ONLY",
            "risk": p.get("risk", "unassessed"), "verification_test": p.get("verification_test", "not specified"),
            "action": p.get("action", "No action provided"),
            "evidence_state": "HYPOTHESIS_NOT_OBSERVED",
        })
    proposals.sort(key=lambda p: (-p["modeled_days_saved"], p["id"]))
    # Crossing cards have no receiver address, credentials, or transport. No import is performed.
    handoffs = [
        {"id": p["id"], "producer": "MOTIF.ORG-001", "receiver_candidates": ["JAR-VIS", "planZ", "reLATTE"],
         "scope": "LOCAL_REVIEW_ONLY", "disclosure": "PRIVATE_UNTIL_REVIEWED", "state": "HOLD",
         "summary": p["action"], "hypothesis": p["hypothesis"], "modeled_days_saved": p["modeled_days_saved"]}
        for p in proposals
    ]
    return {
        "kind": "MOTIF_ORG_001_DIAGNOSTIC", "world_id": brief.get("world_id", "local"),
        "as_of": brief["as_of"], "outcome": brief["outcome"],
        "observation": {"open_steps": len(unresolved), "open_work_in_progress": sum(t["status"] == "active" for t in unresolved),
                        "recorded_wait_days_total": round(sum(t.get("observed_wait_days", 0) for t in unresolved), 3),
                        "queue_by_blocker": dict(sorted(queues.items()))},
        "model": {"baseline": baseline, "assumption": "Declared future remaining_days, not a calibrated prediction or measured causal effect"},
        "verification_gaps": issues, "conditional_proposals": proposals, "local_handoff_drafts": handoffs,
        "receipts": {"evaluation": "LOCAL_DETERMINISTIC", "observations_are_not_confirmations": True,
                     "no_external_actions": True, "no_permission_inferred_from_silence": True},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path, help="local JSON brief with one outcome, steps, interventions")
    args = parser.parse_args()
    result = analyze(json.loads(args.brief.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
