"""Independent small-world classical reference for IMMUNE-002.

Brute-force assumption environments and an exact-match access-control monitor
rather than reusing the tested fixed-point truth-maintenance algorithm.
"""
from __future__ import annotations

from itertools import combinations
from giants import (HOLD, Source, Rule, Scope, Action, Grant,
                    exact_identity, action_digest)


def brute_support(sources: tuple[Source, ...], rules: tuple[Rule, ...],
                  scope: Scope) -> dict[str, tuple[frozenset[str], ...]]:
    nodes = {s.id for s in sources}
    nodes.update(r.conclusion for r in rules)
    accepted = set(scope.assumed_ids) - set(scope.revoked_ids)
    lookup = {s.id: s for s in sources}
    for sid in scope.check_ids:
        if sid not in set(scope.revoked_ids) and exact_identity(lookup[sid]).equal_as_polynomials:
            accepted.add(sid)
    if len(accepted) > 10:
        raise HOLD("Reference exhaustive limit")
    found = {n: set() for n in nodes}
    order = sorted(accepted)
    for count in range(len(order) + 1):
        for choice in combinations(order, count):
            chosen = frozenset(choice)
            closure = set(chosen)
            while True:
                additions = {r.conclusion for r in rules
                             if set(r.premises) <= closure}
                if additions <= closure:
                    break
                closure |= additions
            for node in closure:
                found[node].add(chosen)

    def minimal(groups):
        keep = []
        for env in sorted(groups, key=lambda e: (len(e), tuple(sorted(e)))):
            if not any(prior <= env for prior in keep):
                keep.append(env)
        return tuple(keep)

    return {k: minimal(v) for k, v in found.items()}


def reference_gate(action: Action, grants: tuple[Grant, ...] = (),
                   used_nonces: frozenset[str] = frozenset()) -> str:
    """Independent policy expression for action admission on an exact scope."""
    if action.operation == "READ_PUBLIC":
        return "ALLOW_PUBLIC_READ"
    canonical = action_digest(action)
    permitted = any(g.operation == action.operation
                    and g.arguments_sha256 == canonical
                    and g.nonce not in used_nonces
                    and bool(g.nonce)
                    for g in grants)
    return "ALLOW_EXACT_GRANT" if permitted else "DENY_NO_EXACT_GRANT"
