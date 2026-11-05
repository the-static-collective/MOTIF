"""OBJECTION ENGINE 001: proof-carrying, omission-aware classical inference.

Not a replacement for Boolean logic. A small epistemic envelope that refuses
to convert absent observations or contradictory claims into certain truth.
Optional value-of-information calculations use EXPLICIT uniform synthetic
world weights; they are not empirical priors or estimates of real costs.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import deque
from itertools import product
import math


class HOLD(ValueError):
    pass


@dataclass(frozen=True)
class Inquiry:
    nodes: tuple[str, ...]
    universe: tuple[tuple[str, str], ...]
    claims: tuple[tuple[str, str, str, str], ...]
    removed: tuple[str, str]
    closed_scope: bool = False
    source: str = "S"
    target: str = "T"

    def __post_init__(self):
        if (not isinstance(self.nodes, tuple) or not 2 <= len(self.nodes) <= 8
                or len(set(self.nodes)) != len(self.nodes)
                or any(not isinstance(n, str) or not n or len(n) > 32
                       for n in self.nodes)
                or not isinstance(self.universe, tuple) or len(self.universe) > 28
                or len(set(self.universe)) != len(self.universe)
                or any(not isinstance(e, tuple) or len(e) != 2 or
                       e[0] not in self.nodes or e[1] not in self.nodes
                       for e in self.universe)
                or self.removed not in self.universe
                or self.source not in self.nodes or self.target not in self.nodes
                or type(self.closed_scope) is not bool):
            raise HOLD("Invalid bounded inquiry or completeness assertion")
        for claim in self.claims:
            if (not isinstance(claim, tuple) or len(claim) != 4
                    or claim[:2] not in self.universe
                    or claim[2] not in ("PRESENT", "ABSENT")
                    or not isinstance(claim[3], str) or not claim[3]
                    or len(claim[3]) > 96):
                raise HOLD("Malformed attributed observation")
        if len(self.claims) != len(set(self.claims)):
            raise HOLD("Duplicated source witness")


def path(nodes, edges, start, target):
    adjacency = {n: [] for n in nodes}
    for a, b in edges:
        adjacency[a].append(b)
    queue = deque([(start, (start,))])
    visited = {start}
    while queue:
        here, walk = queue.popleft()
        if here == target:
            return walk
        for nxt in sorted(adjacency[here]):
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, walk + (nxt,)))
    return None


def visited_from(nodes, edges, source):
    outgoing = {n: [] for n in nodes}
    for a, b in edges:
        outgoing[a].append(b)
    visited = {source}
    queue = deque([source])
    while queue:
        for nxt in sorted(outgoing[queue.popleft()]):
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    return tuple(sorted(visited))


def evidence(inquiry):
    present, absent = {}, {}
    for a, b, stance, witness in inquiry.claims:
        group = present if stance == "PRESENT" else absent
        group.setdefault((a,b), []).append(witness)
    definite = set(present) - set(absent)
    impossible = set(absent) - set(present)
    conflicted = set(present) & set(absent)
    # A contradicted edge is neither proved present nor proved absent.
    possible = set(inquiry.universe) - impossible
    definite.discard(inquiry.removed)
    possible.discard(inquiry.removed)
    unknown = tuple(sorted(possible - definite))
    return definite, possible, conflicted, unknown


def question_value(inquiry, definite, uncertain, fn_cost, fp_cost, query_cost):
    if len(uncertain) > 8:
        return {"status": "HOLD_BUDGET", "reason": "More than 8 unresolved edges"}
    assignments = []
    for bits in product((False, True), repeat=len(uncertain)):
        active = definite | {e for e, bit in zip(uncertain, bits) if bit}
        truth = path(inquiry.nodes, active, inquiry.source, inquiry.target) is not None
        assignments.append((bits, truth))
    total = len(assignments)
    positives = sum(t for _, t in assignments)

    def error_loss(rows):
        yes = sum(int(truth) for _, truth in rows)
        no = len(rows) - yes
        return min(yes * fn_cost, no * fp_cost)

    before = error_loss(assignments) / total
    proposals = []
    for i, edge in enumerate(uncertain):
        left = [entry for entry in assignments if not entry[0][i]]
        right = [entry for entry in assignments if entry[0][i]]
        after = (error_loss(left) + error_loss(right)) / total
        net = before - after - query_cost
        proposals.append({"edge": list(edge), "information_value": round(before-after, 6),
                          "net_avoided_loss": round(net, 6)})
    proposals.sort(key=lambda p: (-p["net_avoided_loss"], p["edge"]))
    top = proposals[0] if proposals and proposals[0]["net_avoided_loss"] > 0 else None
    return {"status": "QUESTION_PROPOSAL" if top else "HOLD_NO_POSITIVE_QUERY",
            "uncalibrated_uniform_world_prior": True,
            "hypothetical_reachability_fraction": round(positives / total, 6),
            "cost_of_omission": round(before, 6),
            "recommended_question": top,
            "ranked_questions": proposals}


def decide(inquiry, *, false_negative_cost=5.0, false_positive_cost=4.0,
           question_cost=0.2):
    if not isinstance(inquiry, Inquiry):
        raise HOLD("Unrecognized inquiry")
    costs = (false_negative_cost, false_positive_cost, question_cost)
    if any(type(v) not in (float, int) or not math.isfinite(v) or v < 0
           for v in costs) or costs[0] == 0 or costs[1] == 0:
        raise HOLD("Invalid declared hypothetical cost model")
    definite, possible, conflicted, uncertain = evidence(inquiry)
    real_path = path(inquiry.nodes, definite, inquiry.source, inquiry.target)
    if real_path is not None:
        return {
            "status": "PROVED_REACHABLE",
            "certificate": {"kind": "WITNESSED_PATH", "nodes": list(real_path)},
            "conflicts_preserved": [list(e) for e in sorted(conflicted)],
            "world_authority": False,
        }
    potential_path = path(inquiry.nodes, possible, inquiry.source, inquiry.target)
    if potential_path is None and inquiry.closed_scope:
        reached = visited_from(inquiry.nodes, possible, inquiry.source)
        return {
            "status": "PROVED_UNREACHABLE",
            "certificate": {"kind": "FINITE_CUT", "reachable_partition": list(reached),
                            "assumes_declared_universe_complete": True},
            "conflicts_preserved": [list(e) for e in sorted(conflicted)],
            "world_authority": False,
        }
    if not inquiry.closed_scope:
        return {"status": "HOLD_OPEN_WORLD", "reason": "Unlisted edges might exist",
                "positive_certificate": False, "negative_certificate": False,
                "conflicts_preserved": [list(e) for e in sorted(conflicted)],
                "world_authority": False}
    analysis = question_value(inquiry, definite, uncertain,
                              false_negative_cost, false_positive_cost, question_cost)
    return {"status": "UNKNOWN", "possible_path": list(potential_path) if potential_path else None,
            "conflicts_preserved": [list(e) for e in sorted(conflicted)],
            "omission_analysis": analysis,
            "world_authority": False}


def check_certificate(inquiry, response):
    """Independently check proof terms against the *same declared assumptions*."""
    definite, possible, _, _ = evidence(inquiry)
    c = response.get("certificate")
    if not isinstance(c, dict):
        return False
    if c.get("kind") == "WITNESSED_PATH":
        nodes = c.get("nodes")
        return (isinstance(nodes, list) and len(nodes) > 0
                and nodes[0] == inquiry.source and nodes[-1] == inquiry.target
                and all((a,b) in definite for a,b in zip(nodes, nodes[1:])))
    if c.get("kind") == "FINITE_CUT":
        return (inquiry.closed_scope and
                c.get("assumes_declared_universe_complete") is True and
                c.get("reachable_partition") ==
                    list(visited_from(inquiry.nodes, possible, inquiry.source)) and
                inquiry.target not in c["reachable_partition"])
    return False
