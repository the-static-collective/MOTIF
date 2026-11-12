"""REASON-CARTRIDGE-001: infer a bounded *choice of reasoning method* from corrections.

This learns a priority relation among five predeclared, read-only strategy moves.
It does NOT extract a teacher's private chain-of-thought, learn arbitrary algorithms,
or grant access to tools. Python 3.10+, stdlib only.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
import re

SCHEMA = "motif.reason-cartridge.v1"
SOURCE_REVISION = "synthetic-reason-routing-v1"
SIGNALS = (
    "MISSING_AUTHORITY",
    "CONTRADICTION",
    "STALE_SOURCE",
    "LOOKUP_AVAILABLE",
    "PLAN_POSSIBLE",
)
MOVES = {
    "MISSING_AUTHORITY": "HOLD_FOR_AUTHORITY",
    "CONTRADICTION": "TEST_COUNTEREXAMPLE",
    "STALE_SOURCE": "REVALIDATE_SOURCE",
    "LOOKUP_AVAILABLE": "EXACT_CLASSICAL_LOOKUP",
    "PLAN_POSSIBLE": "DRAFT_HYPOTHETICAL_PLAN",
}
LIMIT_BYTES = 12000
SAFE_LABEL = re.compile(r"^[A-Za-z0-9_.:-]{1,100}$")


class HOLD(ValueError):
    """Abstain instead of assuming unknown teacher priorities or permissions."""


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True).encode()).hexdigest()


def _label(value):
    if not isinstance(value, str) or not SAFE_LABEL.fullmatch(value):
        raise HOLD("Invalid provenance label")
    return value


def _signals(value):
    if (not isinstance(value, (tuple, list)) or not 1 <= len(value) <= 5
            or any(not isinstance(s, str) or s not in SIGNALS for s in value)
            or len(set(value)) != len(value)):
        raise HOLD("Unknown, duplicate or empty signal set")
    return tuple(value)


@dataclass(frozen=True)
class Correction:
    """An observable correction, NEVER a claimed internal reasoning transcript."""
    task_ref: str
    active: tuple[str, str]
    pupil_guess: str
    teacher_choice: str
    evidence_ref: str
    source_revision: str = SOURCE_REVISION

    def __post_init__(self):
        for field in (self.task_ref, self.evidence_ref, self.source_revision):
            _label(field)
        active = _signals(self.active)
        if len(active) != 2 or tuple(sorted(active)) != active:
            raise HOLD("Training examples must isolate one distinct pair")
        if self.pupil_guess not in active or self.teacher_choice not in active:
            raise HOLD("Teacher/pupil choice not present in case")
        if self.pupil_guess == self.teacher_choice:
            raise HOLD("A correction must change the pupil's choice")
        if self.source_revision != SOURCE_REVISION:
            raise HOLD("Stale teacher task contract")

    @property
    def receipt(self):
        # The original scenario text is not exported. A hash is NOT a signature.
        return digest({"task": self.task_ref, "active": self.active,
                       "pupil": self.pupil_guess, "teacher": self.teacher_choice,
                       "evidence": self.evidence_ref, "revision": self.source_revision})


class Pupil:
    def __init__(self):
        self.corrections: list[Correction] = []

    def _reach(self):
        graph = {s: set() for s in SIGNALS}
        for c in self.corrections:
            loser = next(s for s in c.active if s != c.teacher_choice)
            graph[c.teacher_choice].add(loser)
        # Transitive closure: if A precedes B and B precedes C, A precedes C.
        for middle in SIGNALS:
            for left in SIGNALS:
                if middle in graph[left]:
                    graph[left].update(graph[middle])
        if any(s in graph[s] for s in SIGNALS):
            raise HOLD("Conflicting teacher corrections form a cycle")
        return graph

    def add(self, correction: Correction):
        if not isinstance(correction, Correction):
            raise HOLD("Unrecognized teacher response")
        if any(c.task_ref == correction.task_ref for c in self.corrections):
            raise HOLD("Duplicate task receipt")
        pair = correction.active
        if any(c.active == pair for c in self.corrections):
            raise HOLD("Repeated or conflicting comparison")
        self.corrections.append(correction)
        try:
            self._reach()
        except HOLD:
            self.corrections.pop()
            raise

    def next_probe(self):
        """Ask the teacher a discriminating two-signal case, never for its hidden thoughts."""
        reach = self._reach()
        for a, b in combinations(SIGNALS, 2):
            if b not in reach[a] and a not in reach[b]:
                return tuple(sorted((a, b)))
        return None

    def learned_order(self):
        reach = self._reach()
        if self.next_probe() is not None:
            raise HOLD("Teacher ordering still ambiguous; ask another contrasting case")
        return tuple(sorted(SIGNALS, key=lambda s: (-len(reach[s]), s)))

    def export(self, origin_claim="SYNTHETIC_TEACHER_UNVERIFIED"):
        _label(origin_claim)
        order = self.learned_order()
        body = {
            "schema": SCHEMA,
            "source_contract": SOURCE_REVISION,
            "origin_claim": origin_claim,
            "priority_program": [{"when": s, "then": MOVES[s]} for s in order],
            "correction_receipts": sorted(c.receipt for c in self.corrections),
            "evidence_count": len(self.corrections),
            "status": "PROPOSAL_ONLY",
            "scope": "LOCAL_SYNTHETIC_READ_ONLY",
            "real_world_authority": False,
        }
        packet = dict(body, checksum_sha256=digest(body))
        raw = json.dumps(packet, sort_keys=True, indent=2) + "\n"
        validate(raw)
        return raw


def validate(raw):
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > LIMIT_BYTES:
        raise HOLD("Oversize or invalid reasoning cartridge")
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise HOLD("Malformed JSON") from exc
    fields = {"schema", "source_contract", "origin_claim", "priority_program",
              "correction_receipts", "evidence_count", "status", "scope",
              "real_world_authority", "checksum_sha256"}
    if not isinstance(obj, dict) or set(obj) != fields:
        raise HOLD("Unrecognized cartridge schema fields")
    if (obj["schema"] != SCHEMA or obj["source_contract"] != SOURCE_REVISION
            or obj["status"] != "PROPOSAL_ONLY"
            or obj["scope"] != "LOCAL_SYNTHETIC_READ_ONLY"
            or obj["real_world_authority"] is not False):
        raise HOLD("Unrecognized contract or elevated authority claim")
    _label(obj["origin_claim"])
    program = obj["priority_program"]
    if (not isinstance(program, list) or len(program) != len(SIGNALS)
            or any(not isinstance(p, dict) or set(p) != {"when", "then"}
                   for p in program)):
        raise HOLD("Invalid bounded reasoning program")
    order = [p["when"] for p in program]
    if set(order) != set(SIGNALS) or len(set(order)) != len(SIGNALS):
        raise HOLD("Invalid program signal coverage")
    if any(p["then"] != MOVES[p["when"]] for p in program):
        raise HOLD("Attempt to extend executable method vocabulary")
    receipts = obj["correction_receipts"]
    if (not isinstance(receipts, list) or not 1 <= len(receipts) <= 10
            or receipts != sorted(set(receipts))
            or any(not isinstance(x, str) or not re.fullmatch(r"[0-9a-f]{64}", x)
                   for x in receipts)
            or type(obj["evidence_count"]) is not int
            or obj["evidence_count"] != len(receipts)):
        raise HOLD("Invalid correction provenance")
    claimed = obj["checksum_sha256"]
    if not isinstance(claimed, str) or claimed != digest({k: v for k, v in obj.items()
                                                        if k != "checksum_sha256"}):
        raise HOLD("Changed or corrupted cartridge")
    return obj


def choose(program, active):
    active = _signals(active)
    priority = [p["when"] for p in program]
    selected = next(s for s in priority if s in active)
    return {"signal": selected, "method": MOVES[selected],
            "stage": "SUGGEST_ONLY", "executed": False,
            "real_world_authority": False}


class LocalReceiver:
    """Separate receiver-owned review gate; hashes never confer admission."""
    def __init__(self, raw, current_source_revision=SOURCE_REVISION):
        self.packet = validate(raw)
        if self.packet["source_contract"] != current_source_revision:
            raise HOLD("Destination source revision mismatch")
        self.admitted = False
        self._preview_digest = None
        self._preview_passed = False

    def preview(self, independent_cases):
        """Cases are (active signals, expected teacher choice), held by destination."""
        if not isinstance(independent_cases, tuple) or not independent_cases:
            raise HOLD("Independent receiver review required")
        decisions = []
        for active, expected in independent_cases:
            normalized = _signals(active)
            if expected not in normalized:
                raise HOLD("Invalid independent review label")
            got = choose(self.packet["priority_program"], normalized)["signal"]
            decisions.append([list(normalized), got, expected])
        errors = sum(got != expected for _, got, expected in decisions)
        self._preview_passed = errors == 0
        self._preview_digest = digest({"cartridge": self.packet["checksum_sha256"],
                                       "decisions": decisions, "errors": errors})
        return {"stage": "HOLD_REVIEW", "cases": len(decisions),
                "correct": len(decisions) - errors, "errors": errors,
                "review_digest": self._preview_digest, "authority": False}

    def admit(self, decision, review_digest):
        if decision != "ADMIT_READ_ONLY" or not self._preview_passed:
            raise HOLD("Explicit local review with passing independent cases required")
        if not isinstance(review_digest, str) or review_digest != self._preview_digest:
            raise HOLD("Review decision is not tied to the current preview")
        self.admitted = True

    def suggest(self, active):
        if not self.admitted:
            raise HOLD("Unreviewed reasoning cartridge")
        return choose(self.packet["priority_program"], active)
