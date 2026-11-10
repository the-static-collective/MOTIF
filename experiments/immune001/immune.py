"""MOTIF-IMMUNE-001: bounded epistemic graph defense, not a network security sandbox.

External records are *data*. Their instructions, claimed credentials, declared
source identities, and asserted certainty never authorize execution or promotion.
The only promotion authority in this research cartridge is a locally executed
finite mathematical check, requested separately by the operator.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

DOMAIN = tuple(range(-5, 6))
MAX_RECORDS = 500
UNSAFE = frozenset({"FALSIFIED", "WITHDRAWN", "DEPENDENCY_REVIEW"})


class HOLD(ValueError):
    """Malformed or unadjudicable evidence is never silently promoted."""


@dataclass(frozen=True)
class Claim:
    label: str
    lhs: tuple[int, ...] | None = None
    rhs: tuple[int, ...] | None = None


@dataclass(frozen=True)
class Record:
    id: str
    claim: Claim
    source: str
    parents: tuple[str, ...] = ()
    asserted_mode: str = "HYPOTHESIS"
    payload: str = ""


@dataclass(frozen=True)
class BoundedCheck:
    claim_digest: str
    verified_on_domain: bool
    domain: tuple[int, ...]
    counterexample: int | None
    method: str = "EXACT_FINITE_INTEGER_EVALUATION_NOT_GENERAL_PROOF"


@dataclass
class Inspection:
    status: dict[str, str]
    lineage_roots: dict[str, tuple[str, ...]]
    next_action: dict[str, str]
    checks: dict[str, BoundedCheck]
    ancestry: dict[str, tuple[str, ...]]

    def source_count(self, key: str, records: tuple[Record, ...]) -> int:
        """Count declared origin chains; never claim authenticated independence."""
        claim = next(r.claim for r in records if r.id == key)
        return len(set().union(*(set(self.lineage_roots[r.id])
                 for r in records if r.claim == claim)))


def _polynomial(coefficients: tuple[int, ...], x: int) -> int:
    value = 0
    for coefficient in reversed(coefficients):
        value = value * x + coefficient
    return value


def _validate_claim(c: Claim) -> None:
    if not isinstance(c, Claim) or not isinstance(c.label, str) or not c.label:
        raise HOLD("A nonempty typed claim label is required")
    if (c.lhs is None) != (c.rhs is None):
        raise HOLD("Both sides of finite claim are required")
    for side in (c.lhs, c.rhs):
        if side is not None and (not isinstance(side, tuple)
                or not 1 <= len(side) <= 6
                or any(type(v) is not int or abs(v) > 1000 for v in side)):
            raise HOLD("Only bounded exact integer polynomials admitted")


def _digest_claim(c: Claim) -> str:
    return sha256(json.dumps([c.label, c.lhs, c.rhs],
                              separators=(",", ":")).encode()).hexdigest()


def bounded_check(c: Claim) -> BoundedCheck:
    """Only checks equality on 11 declared integers; never proves a theorem."""
    _validate_claim(c)
    if c.lhs is None:
        raise HOLD("This claim has no executable local mathematical witness")
    wrong = next((x for x in DOMAIN if
                 _polynomial(c.lhs, x) != _polynomial(c.rhs, x)), None)
    return BoundedCheck(_digest_claim(c), wrong is None, DOMAIN, wrong)


def _topology(records: tuple[Record, ...]) -> tuple[Record, ...]:
    if not isinstance(records, tuple) or len(records) > MAX_RECORDS:
        raise HOLD("Finite, immutable evidence tuple within budget required")
    by_id = {}
    for r in records:
        if not isinstance(r, Record) or not isinstance(r.id, str) or not r.id:
            raise HOLD("Malformed evidence record")
        if r.id in by_id:
            raise HOLD("Duplicate node id")
        _validate_claim(r.claim)
        if (not isinstance(r.source, str) or not r.source
                or not isinstance(r.parents, tuple)
                or any(not isinstance(p, str) for p in r.parents)
                or len(set(r.parents)) != len(r.parents)
                or not isinstance(r.asserted_mode, str)
                or not isinstance(r.payload, str)):
            raise HOLD("Malformed evidence fields")
        by_id[r.id] = r
    ordered = []
    active = set()
    done = set()

    def visit(key: str) -> None:
        if key not in by_id:
            raise HOLD("Missing parent; no invented provenance")
        if key in active:
            raise HOLD("Dependency cycle")
        if key in done:
            return
        active.add(key)
        for parent in by_id[key].parents:
            visit(parent)
        active.remove(key)
        done.add(key)
        ordered.append(by_id[key])

    for r in records:
        visit(r.id)
    return tuple(ordered)


def inspect(records: tuple[Record, ...],
            review_ids: tuple[str, ...] = (),
            withdrawn_ids: tuple[str, ...] = ()) -> Inspection:
    """Inspect inert DAG with explicit local verifications and selective repair.

    review_ids are an operator request to run the checker *now*, not evidence
    supplied by an external record. Unchecked claims retain HYPOTHESIS status.
    """
    ordered = _topology(records)
    known = {r.id for r in ordered}
    for requested in (review_ids, withdrawn_ids):
        if (not isinstance(requested, tuple)
                or any(not isinstance(x, str) or x not in known for x in requested)):
            raise HOLD("Invalid review or withdrawal request")
    if len(set(review_ids)) != len(review_ids):
        raise HOLD("Duplicate verification request")
    if set(review_ids) & set(withdrawn_ids):
        raise HOLD("Cannot verify and withdraw the same node")

    status, roots, actions, checks, ancestry = {}, {}, {}, {}, {}
    for r in ordered:
        roots[r.id] = (tuple(sorted(set().union(
            *(set(roots[p]) for p in r.parents))))
            if r.parents else (r.id,))
        ancestry[r.id] = tuple(sorted(set(r.parents).union(
            *(set(ancestry[p]) for p in r.parents))))
        if r.id in withdrawn_ids:
            status[r.id] = "WITHDRAWN"
            actions[r.id] = "TRACE_DEPENDENTS_AND_REQUEST_NEW_EVIDENCE"
            continue

        if r.id in review_ids:
            try:
                check = bounded_check(r.claim)
            except HOLD:
                status[r.id] = "HOLD"
                actions[r.id] = "REQUEST_INDEPENDENT_VERIFIABLE_EVIDENCE"
            else:
                checks[r.id] = check
                status[r.id] = ("VERIFIED_FINITE" if check.verified_on_domain
                                else "FALSIFIED")
                actions[r.id] = ("RETAIN_BOUNDED_SCOPE" if check.verified_on_domain
                                 else "TRACE_DEPENDENTS_AND_REVISE")
            continue

        if any(status[p] in UNSAFE for p in r.parents):
            status[r.id] = "DEPENDENCY_REVIEW"
            actions[r.id] = "RECHECK_UNSAFE_ANCESTOR_AND_THIS_CLAIM"
        else:
            status[r.id] = "HYPOTHESIS"
            actions[r.id] = ("RUN_EXACT_BOUNDED_CHECK" if r.claim.lhs is not None
                             else "SEEK_INDEPENDENT_EVIDENCE")
    return Inspection(status, roots, actions, checks, ancestry)


def naive_counting_baseline(records: tuple[Record, ...], target_id: str) -> str:
    """Deliberately weak comparator: apparent consensus/certainty promotion."""
    ordered = _topology(records)
    selected = next((r for r in ordered if r.id == target_id), None)
    if selected is None:
        raise HOLD("Unknown target")
    same = [r for r in ordered if r.claim == selected.claim]
    return ("PROMOTE" if len(same) >= 3 or any(
        r.asserted_mode in ("PROVEN", "SYSTEM_VERIFIED") for r in same)
        else "HOLD")


def classical_verifier_baseline(records: tuple[Record, ...],
                                target_id: str, review: bool) -> str:
    """Strong conventional control for the finite mathematical portion."""
    ordered = _topology(records)
    selected = next((r for r in ordered if r.id == target_id), None)
    if selected is None:
        raise HOLD("Unknown target")
    if not review:
        return "HOLD"
    try:
        result = bounded_check(selected.claim)
    except HOLD:
        return "HOLD"
    return "PROMOTE" if result.verified_on_domain else "REJECT"
