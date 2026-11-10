"""GENIUS-005 proof-carrying preview adapter for MOTIF/Trench experiments.

The module does NOT modify the original GENIUS-004 controller, does NOT
publish a packet or connect to MCP, and does NOT infer anyone's motives.
It turns a fixed-window classical test into a source-aware CONDITIONAL
recommendation suitable for later human review.
"""
from __future__ import annotations

from dataclasses import dataclass
from detectors import Detectors, ALPHA, CHECK_TIMES, WIDTH, REFERENCE_N


@dataclass(frozen=True)
class Signal:
    source_node: str
    evidence_ref: str
    report_yes: bool
    shareable: bool
    local_note: str = ""


def propose_revision(
    *,
    source_node: str,
    reference: tuple[Signal, ...],
    future: tuple[Signal, ...],
    fixed_sampling_plan_attested: bool,
) -> dict:
    """Return evidence for research, never claim real-world independent IID.

    The attestation is a caller-supplied declaration. It does NOT
    certify the assumptions or authenticate the person supplying it.
    No withheld signal's value, reference or note enters the output.
    """
    if not source_node:
        raise ValueError("source_node required")
    if not fixed_sampling_plan_attested:
        return {
            "status": "HOLD_UNVERIFIED_SAMPLING_PLAN",
            "source_node": source_node, "can_auto_revise": False,
            "question": "Can the sampling and source-independence assumptions be independently checked?",
            "no_external_action": True,
        }
    if len(reference) != REFERENCE_N:
        return {
            "status": "HOLD_INSUFFICIENT_REFERENCE",
            "source_node": source_node, "reference_public_count": len(reference),
            "can_auto_revise": False, "no_external_action": True,
        }
    if any(not x.shareable or x.source_node != source_node
           or not x.evidence_ref for x in reference):
        return {
            "status": "HOLD_REFERENCE_SCOPE",
            "source_node": source_node, "can_auto_revise": False,
            "no_external_action": True,
        }
    reference_refs = [x.evidence_ref for x in reference]
    if len(set(reference_refs)) != len(reference_refs):
        return {
            "status": "HOLD_DUPLICATE_REFERENCE",
            "source_node": source_node, "can_auto_revise": False,
            "no_external_action": True,
        }
    observed = [x for x in future if x.shareable]
    if any(x.source_node != source_node or not x.evidence_ref for x in observed):
        return {
            "status": "HOLD_FOREIGN_SOURCE",
            "source_node": source_node, "can_auto_revise": False,
            "no_external_action": True,
        }
    future_refs = [x.evidence_ref for x in observed]
    if len(set(future_refs)) != len(future_refs) or (
        set(reference_refs) & set(future_refs)):
        return {
            "status": "HOLD_DUPLICATE_FUTURE_EVIDENCE",
            "source_node": source_node, "can_auto_revise": False,
            "no_external_action": True,
        }
    if any(type(x.report_yes) is not bool for x in reference + tuple(observed)):
        raise ValueError("Public observations must be binary")

    monitor = Detectors(
        tuple(x.report_yes for x in reference),
        stream_id=source_node,
    )
    for sig in observed:
        monitor.update(sig.report_yes, sig.evidence_ref)
    exact_alarm = monitor.alarms.get("EXACT")
    exact_tests = [r for r in monitor.traces if "fisher_p_value" in r]
    triggering_test = next(
        (r for r in exact_tests if r["shared_index"] == exact_alarm), None)
    if exact_alarm is not None:
        supporting_window = future_refs[exact_alarm-WIDTH:exact_alarm]
        status = "PROPOSE_REVISION_CONDITIONALLY"
        next_question = (
            "What independently verified sampling or measurement change "
            "could explain this distributional discrepancy?"
        )
    elif len(observed) < WIDTH:
        supporting_window = []
        status = "HOLD_NOT_ENOUGH_MONITORING"
        next_question = "Will enough independently sourced public observations arrive to test the hypothesis?"
    else:
        supporting_window = []
        status = "RETAIN_PROVISIONALLY_NO_REJECTED_NULL"
        next_question = "Does a different study design reveal an unobserved change?"
    return {
        "operator": "EVIDENCE_BEFORE_REVISION",
        "status": status,
        "source_node": source_node,
        "conditional_null": "iid binary source with unchanged probability and fixed non-outcome-selected sampling",
        "sampling_attestation_not_verification": True,
        "per_stream_false_alarm_bound_if_assumptions_hold": ALPHA,
        "predeclared_test_indices": list(CHECK_TIMES),
        "public_reference_count": len(reference),
        "public_future_count": len(observed),
        "withheld_count_only": len(future)-len(observed),
        "first_exact_alarm_public_index": exact_alarm,
        "exact_p_value_at_alarm": triggering_test["fisher_p_value"] if triggering_test else None,
        "per_test_threshold": ALPHA / len(CHECK_TIMES),
        "source_owned_reference_receipts": reference_refs,
        "source_owned_supporting_window_receipts": supporting_window,
        "fisher_tests_performed": [
            {"public_index": x["shared_index"], "two_sided_exact_p": x["fisher_p_value"]}
            for x in exact_tests
        ],
        "can_auto_revise": False,
        "no_external_action": True,
        "question": next_question,
    }
