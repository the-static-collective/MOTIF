"""MOTIF-GENIUS-003: bounded hidden-profile evidence pooling.

Inspired by Stasser & Titus (1985), but this is a synthetic algebraic
exercise, NOT a real-person group deliberation or empirical replication.
Evidence weights are author-supplied, not established facts. No private
fact can be inspected or requested implicitly.
"""

from __future__ import annotations
from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    node_id: str
    signed_weight: int     # positive -> option A, negative -> option B
    shareable: bool
    evidence_ref: str      # pointer; verification external to this toy
    private_note: str = ""


@dataclass(frozen=True)
class Member:
    node_id: str
    reports: tuple[Evidence, ...]


def evidence_pool(members: tuple[Member, ...]) -> dict:
    if not members or len({m.node_id for m in members}) != len(members):
        raise ValueError("Nonempty unique member ids required")
    all_by_id = {}
    local_choices = {}
    withheld_count = 0
    for member in members:
        if not member.node_id:
            raise ValueError("Empty member id")
        local = {}
        for item in member.reports:
            if item.node_id != member.node_id:
                raise ValueError("Source must own each evidence record")
            if not item.shareable:
                withheld_count += 1
                continue
            if not item.evidence_id or not item.evidence_ref or type(item.signed_weight) is not int:
                raise ValueError("Each shared fact needs an id, reference and integer weight")
            if item.evidence_id in local and local[item.evidence_id].signed_weight != item.signed_weight:
                raise ValueError("One source cannot assign conflicting weights to the same fact")
            local[item.evidence_id] = item
            all_by_id.setdefault(item.evidence_id, []).append(item)
        weight = sum(e.signed_weight for e in local.values())
        local_choices[member.node_id] = {
            "public_weight_sum": weight,
            "reported_evidence_count": len(local),
            "local_model_preference": "A" if weight > 0 else "B" if weight < 0 else "TIE",
        }
    conflicts = []
    unique = []
    for key, items in sorted(all_by_id.items()):
        values = {x.signed_weight for x in items}
        if len(values) != 1:
            conflicts.append({
                "evidence_id": key, "status": "HOLD_CONFLICTING_DECLARED_WEIGHTS",
                "reporting_nodes": sorted({x.node_id for x in items}),
            })
            continue
        unique.append({
            "evidence_id": key, "signed_weight": next(iter(values)),
            "reporting_nodes": sorted({x.node_id for x in items}),
            "evidence_refs": sorted({x.evidence_ref for x in items}),
            "verification_status": "UNVERIFIED_SOURCE_POINTER",
        })
    majority_a = sum(x["local_model_preference"] == "A" for x in local_choices.values())
    majority_b = sum(x["local_model_preference"] == "B" for x in local_choices.values())
    majority = "A" if majority_a > majority_b else "B" if majority_b > majority_a else "TIE"
    if conflicts:
        outcome = "HOLD_INCONSISTENT_EVIDENCE"
        candidate = None
    else:
        outcome = "MODEL_CHOICE_CONDITIONAL_ON_DECLARED_WEIGHTS"
        total = sum(x["signed_weight"] for x in unique)
        candidate = "A" if total > 0 else "B" if total < 0 else None

    return {
        "status": outcome, "conditional_candidate": candidate,
        "evidence_aggregation": "DEDUPLICATE_BY_SHARED_EVIDENCE_ID_THEN_SUM",
        "unique_public_evidence": unique,
        "conflicts": conflicts, "reported_local_choices": local_choices,
        "simple_majority_local_preference": majority,
        "pooled_weight_sum": sum(x["signed_weight"] for x in unique) if not conflicts else None,
        "withheld_records_count": withheld_count,
        "questions_for_next_voluntary_return": [
            "Does anyone wish to share an additional independently checkable fact?",
            "Can evidence owners verify their cited references and signed weights?",
            "Does this mathematical toy represent the real decision constraints?",
        ],
        "no_real_world_ground_truth_established": True,
        "no_external_action_taken": True,
    }


def demo() -> dict:
    common = lambda owner: Evidence("common", owner, 3, True, "synthetic://same")
    return evidence_pool((
        Member("A", (common("A"),
                     Evidence("hidden_a", "A", 1000, False, "private:do-not-leak",
                              "PRIVATE_SENSITIVE_001"))),
        Member("B", (common("B"),
                     Evidence("unique_b", "B", -2, True, "synthetic://unique-b"))),
        Member("C", (common("C"),
                     Evidence("unique_c", "C", -5, True, "synthetic://unique-c"))),
    ))


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True))
