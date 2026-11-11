"""MOTIF ORG-002: institutional-shock and lawful-contingency simulation.

Author-declared durations and eligibility ONLY. Never infer motives, permission,
statutory exemptions, beneficiary equivalence, or confirmed real-world help.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "org001"))
from flow import validate, _schedule, _days  # noqa: E402 (local source-pinned dependency)

SHOCKS = {"funding_lapse", "negotiated_impasse", "capacity_loss", "statutory_pause", "unknown_delay"}
EVIDENCE = {"none", "documented_public_position", "documented_action", "attributed_claim"}
NONEQUIVALENT = "NOT_COMPARABLE_DIFFERENT_BENEFIT"
HOLD = "HOLD_FOR_SCOPE_AUTHORITY_AND_EVIDENCE"


def analyze(case: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(case, dict) or case.get("kind") != "MOTIF_ORG_002_LOCAL_CASE":
        raise ValueError("expected local-only ORG-002 case")
    baseline = case.get("baseline")
    order = validate(baseline)
    by_id = {t["id"]: t for t in baseline["steps"]}
    base = _schedule(baseline, order)
    events = case.get("events")
    if not isinstance(events, list) or not events:
        raise ValueError("at least one explicit shock is required")
    hypotheses = []
    for shock in events:
        if not isinstance(shock, dict) or shock.get("type") not in SHOCKS or not shock.get("id"):
            raise ValueError("bad shock type/id")
        if shock.get("intent_evidence") not in EVIDENCE:
            raise ValueError("unknown motive-evidence classification")
        if shock.get("intent_evidence") in {"documented_public_position", "documented_action", "attributed_claim"}:
            if not shock.get("sources") or not isinstance(shock["sources"], list):
                raise ValueError("attributed intent/position requires explicit source")
        effects = shock.get("effects")
        if not isinstance(effects, list) or not effects:
            raise ValueError("shock needs explicit affected steps")
        changes = {}
        for effect in effects:
            if not isinstance(effect, dict) or effect.get("step_id") not in by_id:
                raise ValueError("unknown affected step")
            key = effect["step_id"]
            if by_id[key]["status"] == "done" or key in changes:
                raise ValueError("cannot rewrite completed history or duplicate effects")
            extra = _days(effect.get("extra_days"), "shock.extra_days")
            changes[key] = by_id[key]["remaining_days"] + extra
        disrupted = _schedule(baseline, order, changes)
        alternatives = []
        for route in case.get("alternatives", []):
            if not isinstance(route, dict) or not route.get("id") or not route.get("proposed_benefit"):
                raise ValueError("route needs id and benefit")
            candidate = route.get("workflow")
            route_order = validate(candidate)
            alt = _schedule(candidate, route_order)
            if route.get("benefit_equivalent") is not True:
                comparison = NONEQUIVALENT
                delta = None
            elif route.get("uses_affected_funding") is not False:
                comparison = "INDEPENDENCE_UNVERIFIED"
                delta = None
            elif not route.get("authority_to_propose") or not route.get("safety_review_steps"):
                comparison = "AUTHORITY_OR_SAFETY_REQUIREMENT_UNDOCUMENTED"
                delta = None
            else:
                # User-authored scope checks, not independent legal validation.
                ids = {t["id"] for t in candidate["steps"]}
                required = route["safety_review_steps"]
                if not isinstance(required, list) or not required or any(x not in ids or not
                    next(t for t in candidate["steps"] if t["id"] == x).get("non_negotiable_gate")
                    for x in required):
                    raise ValueError("independent route must preserve explicit required safety gates")
                comparison = "CONDITIONALLY_COMPARABLE_NOT_AUTHORIZED"
                delta = round(disrupted["forecast_days"] - alt["forecast_days"], 3)
            alternatives.append({
                "id": route["id"], "proposed_benefit": route["proposed_benefit"],
                "route_forecast_days": alt["forecast_days"], "route_critical_path": alt["critical_path"],
                "comparison": comparison, "conditional_days_difference": delta,
                "authority": "HUMAN_REVIEW_REQUIRED", "disposition": HOLD,
                "warning": "Local volunteer service is not a replacement for federal benefit entitlement or a statutory duty",
            })
        hypotheses.append({
            "shock_id": shock["id"], "type": shock["type"],
            "source_classification": shock["intent_evidence"], "sources": shock.get("sources", []),
            "not_a_motive_verdict": True, "affected_steps": sorted(changes),
            "disrupted_forecast_days": disrupted["forecast_days"],
            "disrupted_critical_path": disrupted["critical_path"],
            "assumed_extra_days": {k: round(v - by_id[k]["remaining_days"], 3) for k, v in changes.items()},
            "alternative_routes": alternatives,
        })
    return {
        "kind": "MOTIF_ORG_002_RESULT",
        "as_of": baseline["as_of"], "modeled_outcome": baseline["outcome"],
        "baseline_forecast_days": base["forecast_days"],
        "baseline_critical_path": base["critical_path"],
        "shock_scenarios": hypotheses,
        "recommended_questions_not_commands": [
            "Which functions actually lack legal authority to operate, and which are excepted or separately funded?",
            "Which recorded funding condition or approval remains unresolved?",
            "What is the earliest authorized decision point, and who may decide?",
            "What truly independent, voluntarily supported option meets the same immediate human need?",
            "What safeguard, right, entitlement or consent would be lost by substitution?",
            "Which observation would distinguish strategic withholding from ordinary shortage or absent evidence?",
        ],
        "return_receipt": {
            "status": "UNVERIFIED_HYPOTHETICAL_SIMULATION",
            "human_authority_required": True, "not_measured_real_outcomes": True,
            "no_outside_action": True, "source_authentication": "NOT_PERFORMED",
            "all_alternatives_hold": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    args = parser.parse_args()
    result = analyze(json.loads(args.case.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
