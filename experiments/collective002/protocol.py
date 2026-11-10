"""COLLECTIVE-002 research-only, finite loopback evidence exchange primitives.

Not RFC 8785/JCS or a TranchNode kernel implementation.  HMAC verifies possession
of a pre-shared toy secret, never the worldly truth of an assertion.
"""
from collections import deque
from hashlib import sha256
import hmac
import json
from pathlib import Path

MAX_CARDS = 32
MAX_BYTES = 65536


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return sha256(canonical(value)).hexdigest()


def sign(body, key):
    return {"body": body, "mac": hmac.new(key.encode(), canonical(body), sha256).hexdigest()}


def verify(envelope, key):
    if not isinstance(envelope, dict) or set(envelope) != {"body", "mac"}:
        raise ValueError("invalid envelope")
    expected = sign(envelope["body"], key)["mac"]
    if not isinstance(envelope["mac"], str) or not hmac.compare_digest(envelope["mac"], expected):
        raise ValueError("authentication failed")
    return envelope["body"]


def validate_card(card, issuer):
    if not isinstance(card, dict) or set(card) != {"kind", "source_scope", "origin", "fact_id", "from", "to", "polarity", "epistemic_state"}:
        raise ValueError("bad evidence card fields")
    if (card["kind"] != "source" or card["origin"] != issuer
        or card["epistemic_state"] != "asserted"
        or card["polarity"] not in ("edge", "not_edge")
        or any(not isinstance(card[k], str) or not card[k] or len(card[k]) > 80
               for k in ("source_scope", "origin", "fact_id", "from", "to"))):
        raise ValueError("invalid evidence card")
    return card


def import_cards(cards, recipient_scope):
    """New local-source projections, NOT cross-scope TranchNode edges."""
    output = {}
    for card in cards:
        ident = "source:" + digest({"scope": recipient_scope, "statement": card})
        if ident not in output:
            output[ident] = {
                "id": ident, "kind": "source", "scopeId": recipient_scope,
                "epistemicState": "asserted", "content": {
                    "transmitted_statement": card,
                    "does_not_inherit_origin_authority": True,
                },
            }
    return [output[k] for k in sorted(output)]


def infer_path(sources, start, goal, scope_id):
    """Derive a path from immutable, provenance-bearing source assertions.

    Every contradictory pair is held rather than resolved by voting.  Failure
    to find a path is UNKNOWN, not a negative existence claim.
    """
    if not isinstance(start, str) or not isinstance(goal, str) or not start or not goal or len(start) > 80 or len(goal) > 80:
        raise ValueError("invalid path endpoints")
    if start == goal:
        return {"status": "TRIVIAL", "path": [start], "evidence_ids": [], "tensions": [], "kind": "inference"}
    indexed = {}
    for node in sources:
        if node["scopeId"] != scope_id:
            raise ValueError("scope leakage")
        card = node["content"]["transmitted_statement"]
        pair = (card["from"], card["to"])
        indexed.setdefault(pair, {"edge": [], "not_edge": []})[card["polarity"]].append(node["id"])
    tensions = [{"from": a, "to": b, "supporting": sorted(sides["edge"]), "contesting": sorted(sides["not_edge"])}
                for (a, b), sides in sorted(indexed.items()) if sides["edge"] and sides["not_edge"]]
    # Global HOLD is conservative: a contradictory edge elsewhere in the small
    # toy graph blocks conclusion until a relevance-specific policy is tested.
    if tensions:
        return {"status": "HOLD_CONTRADICTION", "path": [], "evidence_ids": [], "tensions": tensions, "kind": "tension"}
    adjacent = {}
    for (a, b), sides in indexed.items():
        if sides["edge"]:
            adjacent.setdefault(a, []).append((b, sorted(sides["edge"])[0]))
    frontier = deque([(start, [start], [])])
    seen = {start}
    while frontier:
        current, path, evidence = frontier.popleft()
        for nxt, evidence_id in sorted(adjacent.get(current, [])):
            if nxt in seen:
                continue
            if nxt == goal:
                return {"status": "PATH_SUPPORTED_BY_ASSERTIONS", "path": path + [nxt],
                        "evidence_ids": evidence + [evidence_id], "tensions": [], "kind": "inference"}
            seen.add(nxt)
            frontier.append((nxt, path + [nxt], evidence + [evidence_id]))
    return {"status": "UNKNOWN_INSUFFICIENT_EVIDENCE", "path": [], "evidence_ids": [], "tensions": [], "kind": "tension"}


class AppendOnlyLedger:
    """Experimental per-node hash-chained ledger, not TranchNode accepted events."""
    def __init__(self, path):
        self.path = Path(path)

    def replay(self):
        events = []
        if not self.path.exists():
            return events
        for line in self.path.read_text().splitlines():
            event = json.loads(line)
            expected = {k: v for k, v in event.items() if k != "hash"}
            if (set(event) != {"seq", "previous", "kind", "body", "hash"}
                or event["seq"] != len(events) + 1
                or event["previous"] != (events[-1]["hash"] if events else None)
                or event["hash"] != digest(expected)):
                raise ValueError("ledger integrity failure")
            events.append(event)
        return events

    def append(self, kind, body):
        events = self.replay()
        event = {"seq": len(events) + 1, "previous": events[-1]["hash"] if events else None,
                 "kind": kind, "body": body}
        event["hash"] = digest(event)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(canonical(event).decode("utf-8") + "\n")
        return event
