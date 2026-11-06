"""LEGIT-002: typed public-evidence admissibility gate for a consciousness question.

Not a patient diagnostic, language understanding, or autonomous literature reader.
A deterministic adapter supplied by its author, NOT a learned MOTIF method.
Its purpose is to prevent a specific invalid probability inversion.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

PACKET_PATH = Path(__file__).with_name("consciousness_packet.json")

class Hold(ValueError):
    pass

def load_packet(path=PACKET_PATH):
    with open(path, encoding="utf-8") as source:
        obj = json.load(source)
    return validate(obj)

def validate(packet):
    if not isinstance(packet, dict) or packet.get("schema") != "motif.stranger-evidence.v0":
        raise Hold("Unknown provenance or source schema")
    if packet.get("scope") != "GENERAL_RESEARCH_NOT_PATIENT_DIAGNOSIS":
        raise Hold("Real patient decisions are not authorized")
    if packet.get("target") != "SUBJECTIVE_EXPERIENCE_UNOBSERVED":
        raise Hold("Unknown latent target")
    if packet.get("proxy") != "TASK_BASED_NEURAL_COMMAND_FOLLOWING":
        raise Hold("Cannot equate this observation with other consciousness tests")
    if not isinstance(packet.get("methodological_gaps"), list):
        raise Hold("Missing observation limits")
    if packet.get("status") != "PUBLIC_RESEARCH_PACKET_HAND_COMPILED":
        raise Hold("Evidence must identify manual compilation")
    sources = packet.get("source_cards")
    if not isinstance(sources, list) or not 1 <= len(sources) <= 8:
        raise Hold("Invalid source bundle")
    ids = set()
    cohorts = {}
    for src in sources:
        if not isinstance(src, dict) or not isinstance(src.get("id"), str) or src["id"] in ids:
            raise Hold("Duplicate or missing source identity")
        ids.add(src["id"])
        url = src.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            raise Hold("No auditable public source address")
        if "counts" in src:
            if not isinstance(src["counts"], list):
                raise Hold("Invalid source cohort")
            for row in src["counts"]:
                if not isinstance(row, dict) or set(row) != {
                        "group", "total", "positive_neural_task", "negative_neural_task"}:
                    raise Hold("Unknown fields or missing denominator")
                total, pos, neg = (row["total"], row["positive_neural_task"],
                                   row["negative_neural_task"])
                if (any(type(v) is not int for v in (total,pos,neg))
                        or total <= 0 or not (0 <= pos <= total and 0 <= neg <= total)
                        or pos + neg != total):
                    raise Hold("Numerators fail denominator reconciliation")
                group = row["group"]
                if group in cohorts or not isinstance(group, str):
                    raise Hold("Repeated group (could double-count subjects)")
                cohorts[group] = (total,pos,neg,src["id"])
    if set(cohorts) != {"NO_OBSERVABLE_COMMAND_RESPONSE",
                        "OBSERVABLE_COMMAND_RESPONSE"}:
        raise Hold("Cannot compare without both documented groups")
    if not isinstance(packet.get("permitted_outputs"), list) or not isinstance(
            packet.get("prohibited_outputs"), list):
        raise Hold("Missing review scope")
    if "POSTERIOR_FROM_PREVALENCE_ALONE" not in packet["prohibited_outputs"]:
        raise Hold("Unsafe inference not explicitly refused")
    return packet

def run(packet=None):
    """Report *observed sample frequencies* and hold a latent state claim.

    A positive command-following EEG/fMRI is an operational marker, not proof
    of every form of subjective consciousness. No calibrated likelihood model
    linking the latent target to test results is provided.
    """
    obj = validate(packet if packet is not None else load_packet())
    cohort = {}
    anchors = {}
    for src in obj["source_cards"]:
        for row in src.get("counts", []):
            cohort[row["group"]] = row
            anchors[row["group"]] = src["id"]
    unresponsive = cohort["NO_OBSERVABLE_COMMAND_RESPONSE"]
    responsive = cohort["OBSERVABLE_COMMAND_RESPONSE"]
    false_negative_proxy = responsive["negative_neural_task"]
    if false_negative_proxy <= 0:
        raise Hold("No demonstrated task-response miss in the comparator")
    normalized = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return {
        "challenge": obj["challenge"],
        "registered_target": obj["target"],
        "observation": obj["proxy"],
        "method_selected": "CHECK_CONDITIONAL_COUNTS_THEN_HOLD_LATENT_INFERENCE",
        "behaviorally_unresponsive_neural_positive_rate": {
            "numerator": unresponsive["positive_neural_task"],
            "denominator": unresponsive["total"],
            "sample_rate": round(unresponsive["positive_neural_task"]/unresponsive["total"], 6),
            "source_id": anchors["NO_OBSERVABLE_COMMAND_RESPONSE"]},
        "behaviorally_responsive_neural_negative_rate": {
            "numerator": responsive["negative_neural_task"],
            "denominator": responsive["total"],
            "sample_rate": round(false_negative_proxy/responsive["total"], 6),
            "source_id": anchors["OBSERVABLE_COMMAND_RESPONSE"]},
        "negative_neural_test_proves_no_awareness": False,
        "inference": "NO_NEGATIVE_TEST_EXCLUSION_OF_EXPERIENCE",
        "individual_probability_of_awareness": None,
        "reason_code": "ABSENT_REFERENCE_STANDARD_FOR_SUBJECTIVE_EXPERIENCE",
        "next_scientific_question":
            "How well do repeated, controlled, multimodal active tasks detect known volitional responses; what are the confounds and externally validated false-negative rates?",
        "requires_separate_human_clinical_governance": True,
        "real_world_authority": False,
        "native_MOTIF_reasoning": False,
        "honest_boundary": "Hand-authored evidence schema and deterministic check, not autonomous paper-reading, discovered consciousness law, or individualized diagnosis.",
        "source_packet_sha256": hashlib.sha256(normalized.encode()).hexdigest(),
        "status": "HOLD_PATIENT_LEVEL_LATENT_CLAIM",
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
