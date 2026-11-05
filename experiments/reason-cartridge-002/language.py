"""Pure synthetic method-language contract for REASON-CARTRIDGE-002.

All "actions" are Boolean transitions in a local model. They do not look up,
contact, authenticate, approve, or act in the real world. No dynamic code exec.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
import re

SCHEMA = "motif.reason-procedure-cartridge.v1"
SOURCE_REVISION = "reason-method-sandbox-r1"
SAFE = re.compile(r"^[A-Za-z0-9_.:-]{1,96}$")
MAX_BYTES = 24000
OPS = ("VERIFY_SOURCE", "EXACT_LOOKUP", "TEST_COUNTEREXAMPLE", "DRAFT_HYPOTHESIS")
GUARDS = ("ALWAYS", "NEED_LOOKUP", "NEED_CHALLENGE", "NOT_NEED_LOOKUP",
          "NOT_NEED_CHALLENGE", "NEED_EITHER", "NEED_BOTH")


class HOLD(ValueError):
    """Synthetic refusal, not a real-world authorization decision."""


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True).encode("utf-8")).hexdigest()


def label(s):
    if not isinstance(s, str) or not SAFE.fullmatch(s):
        raise HOLD("Invalid identifier")
    return s


@dataclass(frozen=True)
class Case:
    ref: str
    need_lookup: bool
    need_challenge: bool
    fresh: bool = True
    local_ok: bool = True
    lookup_available: bool = True
    challenge_available: bool = True
    unresolved_counterexample: bool = False
    source_revision: str = SOURCE_REVISION

    def __post_init__(self):
        label(self.ref)
        label(self.source_revision)
        for field in ("need_lookup", "need_challenge", "fresh", "local_ok",
                      "lookup_available", "challenge_available", "unresolved_counterexample"):
            if type(getattr(self, field)) is not bool:
                raise HOLD("Nonboolean synthetic case field")
        if self.source_revision != SOURCE_REVISION:
            raise HOLD("Different source contract")

    def context(self):
        return {"need_lookup": self.need_lookup, "need_challenge": self.need_challenge}


@dataclass(frozen=True)
class State:
    verified: bool = False
    looked_up: bool = False
    challenged: bool = False
    drafted: bool = False

    def packet(self):
        return {"verified": self.verified, "looked_up": self.looked_up,
                "challenged": self.challenged, "drafted": self.drafted}


def matches(guard, case):
    if guard not in GUARDS:
        raise HOLD("Unknown procedural guard")
    a, b = case.need_lookup, case.need_challenge
    return {
        "ALWAYS": True, "NEED_LOOKUP": a, "NEED_CHALLENGE": b,
        "NOT_NEED_LOOKUP": not a, "NOT_NEED_CHALLENGE": not b,
        "NEED_EITHER": a or b, "NEED_BOTH": a and b,
    }[guard]


def transition(op, state, case):
    """Pure, source-owned local toy interpreter, no network or side effects."""
    if op not in OPS or not isinstance(state, State) or not isinstance(case, Case):
        raise HOLD("Unknown operation or state")
    if op == "VERIFY_SOURCE":
        if not case.fresh or not case.local_ok:
            raise HOLD("Source not fresh or toy owner gate not available")
        return replace(state, verified=True)
    if not state.verified:
        raise HOLD("Evidence must be checked first")
    if op == "EXACT_LOOKUP":
        if not case.lookup_available:
            raise HOLD("No synthetic lookup available")
        return replace(state, looked_up=True)
    if op == "TEST_COUNTEREXAMPLE":
        if not case.challenge_available or case.unresolved_counterexample:
            raise HOLD("Synthetic counterexample unavailable or unresolved")
        return replace(state, challenged=True)
    if op == "DRAFT_HYPOTHESIS":
        if ((case.need_lookup and not state.looked_up) or
                (case.need_challenge and not state.challenged)):
            raise HOLD("Required synthetic checks unfinished")
        return replace(state, drafted=True)
    raise HOLD("Unrecognized operation")


def execute(program, case):
    """Return a trace and a terminal tag; do not dispatch real work."""
    if not isinstance(program, (tuple, list)) or not isinstance(case, Case):
        raise HOLD("Malformed program")
    state = State()
    events = []
    for entry in program:
        if (not isinstance(entry, dict) or set(entry) != {"op", "guard"}
                or entry["op"] not in OPS or entry["guard"] not in GUARDS):
            raise HOLD("Malformed program step")
        if matches(entry["guard"], case):
            before = state.packet()
            try:
                state = transition(entry["op"], state, case)
            except HOLD as exc:
                return {"result": "HOLD", "reason": str(exc), "events": events,
                        "drafted": False, "authority": False}
            events.append({"op": entry["op"], "before": before, "after": state.packet()})
    return {"result": "DRAFT" if state.drafted else "INCOMPLETE",
            "events": events, "drafted": state.drafted, "authority": False}


def portable(program):
    if not isinstance(program, list) or not 1 <= len(program) <= len(OPS):
        raise HOLD("Unbounded proposed procedure")
    if (any(not isinstance(x, dict) or set(x) != {"op", "guard"}
            or x["op"] not in OPS or x["guard"] not in GUARDS for x in program)
            or len({x["op"] for x in program}) != len(program)):
        raise HOLD("Unsupported, duplicate, or privileged procedure step")
    return program
