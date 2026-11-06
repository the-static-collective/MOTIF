"""LEGIT-006: finite evidence ledger and semantic adversary (synthetic only).

Separates four propositions:
  lack of positive evidence, possession of negative evidence,
  lack of negative evidence, possession of positive evidence.
Neither evidence ledger proposition is the unobserved world's state.

All source trust and search-coverage declarations are *synthetic premises*.
A negative sensor report entails absence ONLY if declared-valid, exhaustive,
and perfectly detecting within the closed finite sample. Independent witness
roots are declared identifiers, not cryptographic authentication.
No real-world or clinical inference, authority, network, or I/O.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re

SCHEMA = "motif.synthetic-epistemic-ledger.v1"
KINDS = frozenset(("POSITIVE_WITNESS", "NEGATIVE_SENSOR"))
ASSURANCES = frozenset(("DECLARED_VALID", "UNVERIFIED"))
COVERAGES = frozenset(("EXHAUSTIVE", "PARTIAL", "UNSPECIFIED"))
DETECTIONS = frozenset(("GUARANTEED", "UNKNOWN", "UNSPECIFIED"))
CLAIMS = frozenset(("NO_POSITIVE_EVIDENCE", "HAS_NEGATIVE_EVIDENCE",
                     "NO_NEGATIVE_EVIDENCE", "HAS_POSITIVE_EVIDENCE",
                     "MUST_ABSENT", "CAN_PRESENT",
                     "MUST_PRESENT", "CAN_ABSENT"))
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,79}$")


class HOLD(ValueError):
    pass


def fingerprint(record):
    return sha256(json.dumps(record, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def _fields(value, fields, label):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise HOLD("Unknown or absent " + label + " fields")


def validate(record):
    _fields(record, ("schema", "id", "scope", "target", "indicator", "reports"),
            "ledger")
    if record["schema"] != SCHEMA or record["scope"] != "SYNTHETIC_ONLY":
        raise HOLD("No real-world inference authorized")
    if (not isinstance(record["id"], str) or not ID.fullmatch(record["id"])
            or not isinstance(record["target"], str)
            or not 1 <= len(record["target"]) <= 80
            or not isinstance(record["indicator"], str)
            or not 1 <= len(record["indicator"]) <= 80):
        raise HOLD("Bad task or target")
    reports = record["reports"]
    if not isinstance(reports, list) or len(reports) > 32:
        raise HOLD("Too many source reports")
    if len(json.dumps(record, allow_nan=False)) > 15000:
        raise HOLD("Oversize evidence packet")
    ids = set()
    root_signature = {}
    for report in reports:
        _fields(report, ("id", "root", "kind", "assurance",
                         "coverage", "detection"), "report")
        if (not isinstance(report["id"], str) or not ID.fullmatch(report["id"])
                or report["id"] in ids
                or not isinstance(report["root"], str) or not ID.fullmatch(report["root"])):
            raise HOLD("Repeated report ID or unknown source root")
        ids.add(report["id"])
        kind, assurance = report["kind"], report["assurance"]
        coverage, detection = report["coverage"], report["detection"]
        if (kind not in KINDS or assurance not in ASSURANCES or
                coverage not in COVERAGES or detection not in DETECTIONS):
            raise HOLD("Unknown measurement or review state")
        if kind == "POSITIVE_WITNESS" and (
                coverage != "UNSPECIFIED" or detection != "UNSPECIFIED"):
            raise HOLD("Positive witness cannot claim negative-survey calibration")
        if kind == "NEGATIVE_SENSOR" and (
                coverage == "UNSPECIFIED" or detection == "UNSPECIFIED"):
            raise HOLD("Missing declared negative-assay conditions")
        # An adversary cannot convert one source into two independent roots.
        signature = (kind, assurance, coverage, detection)
        if report["root"] in root_signature and root_signature[report["root"]] != signature:
            raise HOLD("Echo reports disagree on a shared source root")
        root_signature[report["root"]] = signature
    return record


def inspect(record):
    validate(record)
    roots = {}
    for report in record["reports"]:
        roots.setdefault(report["root"], report)
    unique = sorted(roots.values(), key=lambda r: r["root"])
    positive = [r for r in unique if r["kind"] == "POSITIVE_WITNESS"
                and r["assurance"] == "DECLARED_VALID"]
    negative = [r for r in unique if r["kind"] == "NEGATIVE_SENSOR"
                and r["assurance"] == "DECLARED_VALID"]
    exhaustive = [r for r in negative if
                  r["coverage"] == "EXHAUSTIVE" and
                  r["detection"] == "GUARANTEED"]
    # Exactly two possible finite states; discard states forbidden by admitted
    # premises. There is no source-strength arithmetic, hidden prior or
    # Bayesian posterior.
    worlds = [False, True]
    if positive:
        worlds = [w for w in worlds if w is True]
    if exhaustive:
        worlds = [w for w in worlds if w is False]
    if not worlds:
        state = "HOLD_CONFLICTING_DECLARED_PREMISES"
    elif worlds == [True]:
        state = "PRESENT_WITHIN_DECLARED_MODEL"
    elif worlds == [False]:
        state = "ABSENT_WITHIN_DECLARED_MODEL"
    else:
        state = "UNIDENTIFIED"
    return {
        "schema": "motif.epistemic-inspection.v1",
        "ledger_digest": fingerprint(record),
        "distinct_root_count": len(unique),
        "echo_count": len(record["reports"]) - len(unique),
        "declared_valid_positive_roots": len(positive),
        "declared_valid_negative_roots": len(negative),
        "declared_exhaustive_guaranteed_negative_roots": len(exhaustive),
        "unverified_roots": sum(r["assurance"] == "UNVERIFIED" for r in unique),
        "worlds": worlds,
        "state": state,
        "source_authentication": False,
        "individual_probability": None,
        "scope": "SYNTHETIC_ONLY",
        "real_world_authority": False,
    }


def evaluate(record, claim):
    if claim not in CLAIMS:
        raise HOLD("Unknown semantic proposition")
    summary = inspect(record)
    if summary["state"] == "HOLD_CONFLICTING_DECLARED_PREMISES":
        verdict = "HOLD_INCONSISTENT_PREMISES"
        truth = None
    else:
        has_pos = summary["declared_valid_positive_roots"] > 0
        has_neg = summary["declared_valid_negative_roots"] > 0
        possibilities = summary["worlds"]
        truth = {
            "NO_POSITIVE_EVIDENCE": not has_pos,
            "HAS_NEGATIVE_EVIDENCE": has_neg,
            "NO_NEGATIVE_EVIDENCE": not has_neg,
            "HAS_POSITIVE_EVIDENCE": has_pos,
            "MUST_ABSENT": possibilities == [False],
            "CAN_PRESENT": True in possibilities,
            "MUST_PRESENT": possibilities == [True],
            "CAN_ABSENT": False in possibilities,
        }[claim]
        verdict = "TRUE_IN_DECLARED_LEDGER" if truth else "FALSE_IN_DECLARED_LEDGER"
    return {
        "claim": claim, "value": truth, "verdict": verdict,
        "worlds": summary["worlds"],
        "supporting_counts": {
            "positive_roots": summary["declared_valid_positive_roots"],
            "negative_roots": summary["declared_valid_negative_roots"],
            "complete_guaranteed_negative_roots":
                summary["declared_exhaustive_guaranteed_negative_roots"],
            "echoes_ignored": summary["echo_count"],
        },
        "ledger_digest": summary["ledger_digest"],
        "status": "RESEARCH_HOLD",
        "real_world_authority": False,
        "interpretation": ("Entailment only within finite, synthetic, declared "
                           "premises; no inference about actual absence or consciousness."),
    }
