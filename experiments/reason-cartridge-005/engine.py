"""REASON-005: objections that can be challenged, budgeted and retained.

A finite synthetic experiment. The critic does not turn a hypothetical
counterexample into evidence. The "owner" is an explicit local test fixture,
not a human, a third-party service or authentication of worldly facts.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1, sha256
from pathlib import Path
import json
import math
import re
import sys

OWNER_PATH = Path(__file__).resolve().parents[1] / "reason-cartridge-004" / "reason004.py"
OWNER_GIT_BLOB = "334fe8feb389cfa2aa7a418e31c433ae3f6ae9e3"
SCHEMA = "motif.reason.meta-objection-cartridge.v1"
SOURCE_REVISION = "reason-005-synthetic-source-v1"
MAX_BYTES = 32000
ID = re.compile(r"^[A-Za-z0-9_.:-]{1,96}$")


class HOLD(ValueError):
    pass


def pinned_owner():
    data = OWNER_PATH.read_bytes()
    current = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if current != OWNER_GIT_BLOB:
        raise HOLD("Owner REASON-004 changed; cannot silently inherit")
    return current


pinned_owner()
sys.path.append(str(OWNER_PATH.parent))
import reason004 as owner4  # noqa: E402


def hashed(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def _clean_id(s):
    if not isinstance(s, str) or not ID.fullmatch(s):
        raise HOLD("Invalid synthetic source identifier")
    return s


def _known(q):
    return owner4.evidence(q)


@dataclass(frozen=True)
class Objection:
    reference: str
    kind: str
    edges: tuple[tuple[str, str], ...]

    def __post_init__(self):
        _clean_id(self.reference)
        if (self.kind not in ("RETRACT_PRESENT", "REVIEW_ABSENCE")
                or not isinstance(self.edges, tuple)
                or not 1 <= len(self.edges) <= 3
                or len(set(self.edges)) != len(self.edges)
                or any(not isinstance(e, tuple) or len(e) != 2
                       or not all(isinstance(n, str) for n in e)
                       for e in self.edges)):
            raise HOLD("Unknown/overbroad objection")


def enc_objection(o):
    return {"reference": o.reference, "kind": o.kind,
            "edges": [list(e) for e in o.edges]}


def dec_objection(v):
    if not isinstance(v, dict) or set(v) != {"reference", "kind", "edges"}:
        raise HOLD("Unrecognized objection packet")
    if not isinstance(v["edges"], list) or any(not isinstance(e, list) for e in v["edges"]):
        raise HOLD("Malformed objecting edges")
    return Objection(v["reference"], v["kind"],
                     tuple(tuple(e) for e in v["edges"]))


def _stressed(q, challenge):
    """Delete a claim to model doubt; DO NOT allege it was really disproved."""
    definite, possible, conflicted, _ = _known(q)
    affected = set(challenge.edges)
    if any(e not in q.universe or e == q.removed for e in affected):
        raise HOLD("Out-of-scope objection")
    if challenge.kind == "RETRACT_PRESENT":
        if any(e not in definite for e in affected):
            raise HOLD("Cannot retract something not unambiguously confirmed")
        claims = tuple(c for c in q.claims if c[:2] not in affected)
    else:
        impossible = set(q.universe) - possible
        if any(e not in impossible for e in affected):
            raise HOLD("Cannot review an edge without unambiguous ABSENT evidence")
        claims = tuple(c for c in q.claims if c[:2] not in affected)
        claims += tuple((a, b, "PRESENT", "HYPOTHETICAL_ONLY")
                        for a, b in sorted(affected))
    return owner4.Inquiry(q.nodes, q.universe, claims, q.removed,
                          q.closed_scope, q.source, q.target)


def stress(q, objection):
    """Objection-to-objection: can the original proof survive the challenge?"""
    pinned_owner()
    base = owner4.decide(q)
    if base["status"] not in ("PROVED_REACHABLE", "PROVED_UNREACHABLE"):
        return {"classification": "HOLD_UNPROVED_OR_OPEN_WORLD",
                "base": base["status"], "no_external_review": True}
    hypoth = _stressed(q, objection)
    counter = owner4.decide(hypoth)
    if counter["status"] == base["status"]:
        proof = counter.get("certificate")
        if not proof or not owner4.check_certificate(hypoth, counter):
            raise HOLD("No valid alternate proof for objection defense")
        return {"classification": "DEFENSE",
                "base": base["status"], "counterfactual": counter["status"],
                "alternate_proof": proof,
                "scope": "ONLY_IF_THIS_HYPOTHETICAL_CHALLENGE_WERE_TRUE",
                "objection_was_checked_externally": False}
    return {"classification": "MATERIAL_OBJECTION",
            "base": base["status"], "counterfactual": counter["status"],
            "requires_owner_observation": True,
            "counterfactual_is_not_evidence": True}


@dataclass(frozen=True)
class Model:
    chance_of_correction: float = 0.5
    benefit_if_corrected: float = 6.0
    verification_cost: float = 1.0
    reasoning_cost: float = 0.25

    def __post_init__(self):
        for value in (self.chance_of_correction, self.benefit_if_corrected,
                      self.verification_cost, self.reasoning_cost):
            if type(value) not in (float, int) or not math.isfinite(value):
                raise HOLD("Invalid hypothetical inquiry model")
        if (not 0 <= self.chance_of_correction <= 1
                or self.benefit_if_corrected < 0 or self.verification_cost < 0
                or self.reasoning_cost < 0):
            raise HOLD("Out-of-range hypothetical costs")

    def value(self):
        avoidable_omission = self.chance_of_correction * self.benefit_if_corrected
        net = avoidable_omission - self.verification_cost - self.reasoning_cost
        return {"declared_expected_cost_of_ignoring": round(avoidable_omission, 6),
                "verification_cost": self.verification_cost,
                "reasoning_cost": self.reasoning_cost,
                "net_value_of_further_reasoning": round(net, 6),
                "hypothetical_not_calibrated": True}


class ToyOwner:
    """Independent source-owned synthetic truth; no credential or real observer."""
    def __init__(self, source_id, truth):
        self.source_id = _clean_id(source_id)
        if (not isinstance(truth, dict) or not truth
                or any(not isinstance(e, tuple) or len(e) != 2 or type(v) is not bool
                       for e, v in truth.items())):
            raise HOLD("Invalid synthetic owner truth table")
        self._truth = dict(truth)
        self.calls = 0

    def review(self, q, obj):
        # May run ONLY following a local fixture decision to query.
        _stressed(q, obj)
        if not all(e in self._truth for e in obj.edges):
            raise HOLD("Toy owner cannot observe requested edges")
        before = owner4.encode(q)
        self.calls += 1
        old = [list(c) for c in q.claims if c[:2] in obj.edges]
        kept = [c for c in q.claims if c[:2] not in obj.edges]
        new_claims = tuple(kept + [
            (a, b, "PRESENT" if self._truth[(a,b)] else "ABSENT",
             f"{self.source_id}-fixture-{self.calls}")
            for a,b in sorted(obj.edges)
        ])
        updated = owner4.Inquiry(q.nodes, q.universe, new_claims, q.removed,
                                 q.closed_scope, q.source, q.target)
        body = {"schema": "motif.reason.synthetic-owner-revision.v1",
                "source_id": self.source_id,
                "fixture_turn": self.calls,
                "source_before_sha256": owner4.digest(before),
                "source_after_sha256": owner4.digest(owner4.encode(updated)),
                "challenge": enc_objection(obj),
                "superseded_claims": old,
                "reviewed_truth": [{"edge": list(e), "present": self._truth[e]}
                                   for e in sorted(obj.edges)],
                "status": "FIXTURE_ONLY_NOT_WORLD_AUTHENTICATION",
                "external_action": False}
        return updated, dict(body, checksum_sha256=hashed(body))


def build_record(q, objection, classification, *,
                 after=None, owner_receipt=None):
    """Portable records cannot inherit teacher privileges or actual authority."""
    if not isinstance(q, owner4.Inquiry):
        raise HOLD("Not an original source-owned inquiry")
    initial = stress(q, objection)
    if classification == "DEFENSE":
        if initial["classification"] != "DEFENSE" or after is not None or owner_receipt:
            raise HOLD("Unsubstantiated defense")
        outcome = {"status": "DEFENSE_ONLY_WITHIN_DECLARED_SCOPE",
                   "rebuttal": initial["alternate_proof"],
                   "original_conclusion_survives_hypothetical_objection": True,
                   "source_witness_changed": False}
    elif classification in ("CORRECTION", "OWNER_DEFENSE"):
        if (initial["classification"] != "MATERIAL_OBJECTION"
                or not isinstance(after, owner4.Inquiry)
                or not isinstance(owner_receipt, dict)
                or owner_receipt.get("status") != "FIXTURE_ONLY_NOT_WORLD_AUTHENTICATION"
                or owner_receipt.get("challenge") != enc_objection(objection)
                or owner_receipt.get("source_before_sha256") != owner4.digest(owner4.encode(q))
                or owner_receipt.get("source_after_sha256") != owner4.digest(owner4.encode(after))):
            raise HOLD("Correction lacks attributable source-owned fixture revision")
        result = owner4.decide(after)
        changed = result["status"] != initial["base"]
        if (classification == "CORRECTION") != changed:
            raise HOLD("Correction/defense classification disagrees with source")
        # Structural replay: receipt and witnesses must show precisely which
        # premise changed. Does not establish true external identity.
        if owner_receipt.get("checksum_sha256") != hashed({
            k: v for k, v in owner_receipt.items() if k != "checksum_sha256"
        }):
            raise HOLD("Changed synthetic receipt")
        old = [list(c) for c in q.claims if c[:2] in objection.edges]
        if owner_receipt.get("superseded_claims") != old:
            raise HOLD("Source supersession history lost")
        truth = owner_receipt.get("reviewed_truth")
        if (not isinstance(truth, list)
                or truth != [{"edge": list(e), "present": any(
                    c[:2] == e and c[2] == "PRESENT" for c in after.claims)}
                              for e in sorted(objection.edges)]):
            raise HOLD("Synthetic owner result does not match revised evidence")
        kept = [c for c in q.claims if c[:2] not in objection.edges]
        appended = [c for c in after.claims if c[:2] in objection.edges]
        turn = owner_receipt.get("fixture_turn")
        source_id = owner_receipt.get("source_id")
        if (type(turn) is not int or not 1 <= turn <= 8
                or not isinstance(source_id, str) or not ID.fullmatch(source_id)
                or [c for c in after.claims if c[:2] not in objection.edges] != kept
                or len(appended) != len(objection.edges)
                or any(c[3] != f"{source_id}-fixture-{turn}" for c in appended)):
            raise HOLD("Unreviewed other changes piggybacked on revision")
        if (not result.get("certificate")
                or not owner4.check_certificate(after, result)):
            raise HOLD("Corrected source has no independent proof")
        outcome = {"status": ("CORRECTION_WITHIN_SYNTHETIC_REVIEW" if changed
                               else "OWNER_REBUTTAL_WITHIN_SYNTHETIC_REVIEW"),
                   "new_conclusion": result["status"],
                   "new_certificate": result["certificate"],
                   "source_witness_changed": True,
                   "actual_world_authenticated": False}
    else:
        raise HOLD("Unsupported cartridge")
    body = {"schema": SCHEMA, "source_revision": SOURCE_REVISION,
            "owner_reason004_blob": pinned_owner(),
            "original_inquiry": owner4.encode(q),
            "objection": enc_objection(objection),
            "classification": classification,
            "outcome": outcome,
            "revised_inquiry": owner4.encode(after) if after else None,
            "synthetic_owner_receipt": owner_receipt,
            "stage": "PROPOSED_FOR_REVIEW",
            "external_execution": False, "real_world_authority": False}
    result = dict(body, checksum_sha256=hashed(body))
    raw = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if len(raw.encode()) > MAX_BYTES:
        raise HOLD("Too much transferred reasoning")
    return raw


def validate(raw):
    if not isinstance(raw, str) or len(raw.encode()) > MAX_BYTES:
        raise HOLD("Invalid method-cartridge size")
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise HOLD("Malformed data-only cartridge") from exc
    keys = {"schema", "source_revision", "owner_reason004_blob",
            "original_inquiry", "objection", "classification", "outcome",
            "revised_inquiry", "synthetic_owner_receipt", "stage",
            "external_execution", "real_world_authority", "checksum_sha256"}
    if not isinstance(obj, dict) or set(obj) != keys:
        raise HOLD("Unrecognized cartridge fields")
    if (obj["schema"] != SCHEMA or obj["source_revision"] != SOURCE_REVISION
            or obj["owner_reason004_blob"] != pinned_owner()
            or obj["stage"] != "PROPOSED_FOR_REVIEW"
            or obj["external_execution"] is not False
            or obj["real_world_authority"] is not False):
        raise HOLD("Altered source authority boundary")
    original = owner4.decode(obj["original_inquiry"])
    challenge = dec_objection(obj["objection"])
    after = (owner4.decode(obj["revised_inquiry"])
             if obj["revised_inquiry"] is not None else None)
    regenerated = json.loads(build_record(original, challenge, obj["classification"],
                                           after=after,
                                           owner_receipt=obj["synthetic_owner_receipt"]))
    if obj != regenerated:
        raise HOLD("Forged or unreplayable proof/defense/correction")
    return obj
