"""MOTIF-IMMUNE-002: classical reasoning giants as small, inspectable algorithms.

Research primitives: Doyle-style reason maintenance; de Kleer-style minimal
assumption environments (a bounded analogue); source/sink reference monitor;
exact polynomial identity checking; separate explicit operator authority.

This is a *simulation*, not a secure process boundary, signed provenance,
an LLM-based defense, a cryptographic capability system or a general prover.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from itertools import product
import json

MAX_ROOTS = 24
MAX_RULES = 72
MAX_ENVIRONMENTS = 256
MAX_COEFFICIENTS = 6
OPERATIONS = frozenset(("READ_PUBLIC", "PUBLISH", "WRITE", "SEND", "DELETE"))


class HOLD(ValueError):
    pass


@dataclass(frozen=True)
class Source:
    id: str
    statement: str
    text: str = ""
    upstream: str | None = None
    claimed_authority: str = "UNVERIFIED"
    lhs: tuple[int, ...] | None = None
    rhs: tuple[int, ...] | None = None


@dataclass(frozen=True)
class Rule:
    """A local, operator-provided implication, never parsed from source text."""
    conclusion: str
    premises: tuple[str, ...]


@dataclass(frozen=True)
class Scope:
    """Direct controller input only. Do not construct this from retrieved text."""
    check_ids: tuple[str, ...] = ()
    assumed_ids: tuple[str, ...] = ()
    revoked_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExactResult:
    equal_as_polynomials: bool
    counterexample: tuple[int, int, int] | None
    method: str = "CANONICAL_INTEGER_POLYNOMIAL_COEFFICIENTS"


@dataclass
class Field:
    environments: dict[str, tuple[frozenset[str], ...]]
    status: dict[str, str]
    checked: dict[str, ExactResult]
    declared_roots: dict[str, tuple[str, ...]]
    admitted: tuple[str, ...]
    excluded: tuple[str, ...]

    def roots_of(self, claim: str) -> tuple[tuple[str, ...], ...]:
        return tuple(tuple(sorted(env)) for env in self.environments[claim])


def _positive_name(x: str) -> bool:
    return type(x) is str and bool(x) and len(x) <= 100


def _check_tuple_names(xs: tuple[str, ...], known: set[str]) -> None:
    if (type(xs) is not tuple or len(set(xs)) != len(xs)
            or any(not _positive_name(x) or x not in known for x in xs)):
        raise HOLD("Invalid controller id list")


def _check_poly(poly: tuple[int, ...] | None) -> None:
    if (type(poly) is not tuple or not 1 <= len(poly) <= MAX_COEFFICIENTS
            or any(type(c) is not int or abs(c) > 10_000 for c in poly)):
        raise HOLD("Invalid exact bounded integer polynomial grammar")


def _normalized(poly: tuple[int, ...]) -> tuple[int, ...]:
    out = list(poly)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out)


def _eval(poly: tuple[int, ...], x: int) -> int:
    value = 0
    for c in reversed(poly):
        value = value * x + c
    return value


def exact_identity(root: Source) -> ExactResult:
    """Complete equality decision in this finite-degree coefficient grammar."""
    _check_poly(root.lhs)
    _check_poly(root.rhs)
    if _normalized(root.lhs) == _normalized(root.rhs):
        return ExactResult(True, None)
    for x in range(-5, 6):
        lhs, rhs = _eval(root.lhs, x), _eval(root.rhs, x)
        if lhs != rhs:
            return ExactResult(False, (x, lhs, rhs))
    # A nonzero polynomial of degree <= 5 has <= 5 distinct roots.
    raise AssertionError("Nonzero degree <=5 polynomial has >5 roots")


def source_digest(s: Source) -> str:
    return sha256(json.dumps([s.id, s.statement, s.text, s.upstream,
                              s.claimed_authority, s.lhs, s.rhs],
                             separators=(",", ":"), ensure_ascii=False)
                  .encode("utf-8")).hexdigest()


def _validate(sources: tuple[Source, ...], rules: tuple[Rule, ...],
              scope: Scope) -> tuple[dict[str, Source], set[str]]:
    if (type(sources) is not tuple or len(sources) > MAX_ROOTS
            or type(rules) is not tuple or len(rules) > MAX_RULES):
        raise HOLD("Invalid bounded typed graph")
    seen = {}
    for s in sources:
        if (not isinstance(s, Source) or not _positive_name(s.id)
                or not _positive_name(s.statement)
                or type(s.text) is not str or len(s.text) > 4000
                or type(s.claimed_authority) is not str
                or len(s.claimed_authority) > 100
                or (s.upstream is not None and not _positive_name(s.upstream))):
            raise HOLD("Invalid source entry")
        if s.id in seen:
            raise HOLD("Duplicate source id")
        if (s.lhs is None) != (s.rhs is None):
            raise HOLD("Partial exact proof")
        if s.lhs is not None:
            _check_poly(s.lhs)
            _check_poly(s.rhs)
        seen[s.id] = s

    for k in seen:
        prior = set()
        node = k
        while seen[node].upstream is not None:
            if node in prior:
                raise HOLD("Cyclic upstream provenance")
            prior.add(node)
            node = seen[node].upstream
            if node not in seen:
                raise HOLD("Missing declared upstream source")

    nodes = set(seen)
    for r in rules:
        if (not isinstance(r, Rule) or not _positive_name(r.conclusion)
                or type(r.premises) is not tuple or not r.premises
                or len(r.premises) > MAX_ROOTS
                or any(not _positive_name(p) for p in r.premises)
                or len(set(r.premises)) != len(r.premises)):
            raise HOLD("Invalid local operator rule")
        nodes.add(r.conclusion)
    for r in rules:
        if any(p not in nodes for p in r.premises):
            raise HOLD("Unknown rule antecedent")
    if not isinstance(scope, Scope):
        raise HOLD("Requires operator-provided Scope")
    for xs in (scope.check_ids, scope.assumed_ids, scope.revoked_ids):
        _check_tuple_names(xs, set(seen))
    if set(scope.check_ids) & set(scope.assumed_ids):
        raise HOLD("Do not mix proof and subjective assumption for same source")
    return seen, nodes


def _minimal(environments) -> tuple[frozenset[str], ...]:
    ordered = sorted(set(environments), key=lambda env: (len(env), tuple(sorted(env))))
    keep = []
    for env in ordered:
        if not any(other <= env for other in keep):
            keep.append(env)
        if len(keep) > MAX_ENVIRONMENTS:
            raise HOLD("Excessive alternative proof environments")
    return tuple(keep)


def _declared_origin(sid: str, roots: dict[str, Source]) -> str:
    while roots[sid].upstream is not None:
        sid = roots[sid].upstream
    return sid


def build_field(sources: tuple[Source, ...], rules: tuple[Rule, ...],
                scope: Scope) -> Field:
    roots, nodes = _validate(sources, rules, scope)
    withdrawn = set(scope.revoked_ids)
    checked = {}
    accepted_roots = set()
    for sid in scope.check_ids:
        checked[sid] = exact_identity(roots[sid]) if sid not in withdrawn else None
        if checked[sid] is not None and checked[sid].equal_as_polynomials:
            accepted_roots.add(sid)
    accepted_roots |= set(scope.assumed_ids) - withdrawn
    accepted_roots -= {sid for sid, check in checked.items()
                       if check is not None and not check.equal_as_polynomials}
    supports = {node: () for node in nodes}
    for sid in accepted_roots:
        supports[sid] = (frozenset((sid,)),)

    # Monotone least fixed point: no self-supporting cycles. Acyclic and
    # recursive rules are allowed, with an explicit environment budget.
    limit = 1 + MAX_ROOTS * MAX_RULES
    for _ in range(limit):
        updated = {node: list(supports[node]) for node in nodes}
        for rule in rules:
            if not all(supports[p] for p in rule.premises):
                continue
            for combined in product(*(supports[p] for p in rule.premises)):
                env = frozenset().union(*combined)
                updated[rule.conclusion].append(env)
                if len(updated[rule.conclusion]) > MAX_ENVIRONMENTS * 8:
                    updated[rule.conclusion] = list(
                        _minimal(updated[rule.conclusion]))
        next_supports = {node: _minimal(updated[node]) for node in nodes}
        if next_supports == supports:
            break
        supports = next_supports
    else:
        raise HOLD("Proof-fixpoint iteration budget exceeded")
    status = {}
    checked_true = {sid for sid, value in checked.items()
                    if value is not None and value.equal_as_polynomials}
    for node in nodes:
        if node in withdrawn:
            status[node] = "WITHDRAWN"
        elif (node in checked and checked[node] is not None
              and not checked[node].equal_as_polynomials):
            status[node] = "FALSIFIED_EXACT"
        elif node in checked_true:
            status[node] = "VERIFIED_EXACT"
        elif supports[node]:
            status[node] = ("RULE_SUPPORTED_EXACT"
                            if any(env <= checked_true for env in supports[node])
                            else "RULE_SUPPORTED_ASSUMPTION")
        else:
            status[node] = "HYPOTHESIS" if node in roots else "UNSUPPORTED"
    declared = {sid: (_declared_origin(sid, roots),) for sid in roots}
    return Field(supports, status, {k: v for k, v in checked.items()
                                   if v is not None}, declared,
                 tuple(sorted(accepted_roots)),
                 tuple(sorted(set(roots) - accepted_roots)))


def compare_revision(before: Field, after: Field) -> dict[str, tuple[str, ...]]:
    """Separate lost support from an alternate successful justification."""
    if set(before.environments) != set(after.environments):
        raise HOLD("Cannot compare different graph propositions")
    lost = []
    alternate = []
    unaffected = []
    for node in sorted(before.environments):
        a, b = before.environments[node], after.environments[node]
        if a and not b:
            lost.append(node)
        elif a and b and a != b:
            alternate.append(node)
        elif a == b:
            unaffected.append(node)
    return {"lost": tuple(lost), "alternative_retained": tuple(alternate),
            "unchanged": tuple(unaffected)}


@dataclass(frozen=True)
class Action:
    operation: str
    arguments: tuple[tuple[str, str], ...] = ()
    source: str = "MODEL_PROPOSAL"


@dataclass(frozen=True)
class Grant:
    """Must be supplied by a trusted controller, never a retrieved document."""
    operation: str
    arguments_sha256: str
    nonce: str


def _valid_action(action: Action) -> None:
    if (not isinstance(action, Action) or action.operation not in OPERATIONS
            or type(action.arguments) is not tuple
            or len(action.arguments) > 24
            or any(type(p) is not tuple or len(p) != 2
                   or not all(type(v) is str and len(v) <= 512 for v in p)
                   for p in action.arguments)
            or len(set(k for k, _ in action.arguments)) != len(action.arguments)):
        raise HOLD("Malformed action or ambiguous arguments")


def action_digest(action: Action) -> str:
    _valid_action(action)
    return sha256(json.dumps([action.operation, sorted(action.arguments)],
                             separators=(",", ":"), ensure_ascii=False)
                  .encode("utf-8")).hexdigest()


def authorized(action: Action, grants: tuple[Grant, ...] = (),
               used_nonces: frozenset[str] = frozenset()) -> str:
    """Side-effect-free policy preview; caller must enforce the decision.

    A runtime-approved, exact action+arguments grant is needed for mutating
    operations. The model cannot elevate Source.text or its own Action.source
    into a Grant. The caller MUST keep grants outside the model/data channel.
    """
    _valid_action(action)
    if type(grants) is not tuple or type(used_nonces) is not frozenset:
        raise HOLD("Invalid trusted controller grant collection")
    if action.operation == "READ_PUBLIC":
        return "ALLOW_PUBLIC_READ"
    for grant in grants:
        if (isinstance(grant, Grant) and grant.operation == action.operation
                and grant.arguments_sha256 == action_digest(action)
                and _positive_name(grant.nonce)
                and grant.nonce not in used_nonces):
            return "ALLOW_EXACT_GRANT"
    return "DENY_NO_EXACT_GRANT"
