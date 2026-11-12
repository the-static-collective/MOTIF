"""Versioned, strictly synthetic JSON stdin bridge for private MEMENTO experiments.

No imports from MEMENTO, no credential access, and no private source data.
Accepts structural episodes only. Never executes user-supplied code.
"""
import json
import sys

from unknown_unknown import Episode, assess, classical_exhaustive_selector, discover, fit

MAX_BYTES = 250_000
MAX_ROWS = 128
MAX_EDGES = 12
MAX_TOKEN = 90


def fail(reason):
    print(json.dumps({"schema": "motif018.memento-bridge-result/v0",
                      "status": "REFUSE_INVALID_PACKET", "error": reason,
                      "authority": "NONE", "external_actions": 0},
                     sort_keys=True))
    return 2


def token(value):
    return (isinstance(value, str) and 0 < len(value) <= MAX_TOKEN
            and all(c.isascii() and (c.isalnum() or c in "_-.") for c in value))


def to_episodes(rows, split):
    if not isinstance(rows, list) or len(rows) < 1 or len(rows) > MAX_ROWS:
        raise ValueError("BAD_" + split.upper() + "_ROWS")
    seen = set()
    parsed = []
    for raw in rows:
        if not isinstance(raw, dict) or set(raw) != {"identity", "x", "edges", "outcome", "authorized"}:
            raise ValueError("BAD_ROW_SCHEMA")
        ident = raw["identity"]
        if not token(ident) or ident in seen:
            raise ValueError("BAD_OR_DUPLICATE_ID")
        seen.add(ident)
        if type(raw["x"]) is not int or raw["x"] not in (0, 1):
            raise ValueError("NON_BINARY_X")
        if type(raw["outcome"]) is not int or raw["outcome"] not in (0, 1):
            raise ValueError("NON_BINARY_OUTCOME")
        if type(raw["authorized"]) is not bool:
            raise ValueError("NOT_BOOLEAN_PERMISSION")
        edges = raw["edges"]
        if not isinstance(edges, list) or len(edges) > MAX_EDGES:
            raise ValueError("BAD_EDGE_LIST")
        cleaned = []
        for item in edges:
            if not isinstance(item, list) or len(item) != 3 or not all(map(token, item)):
                raise ValueError("BAD_EDGE_TRIPLE")
            cleaned.append(tuple(item))
        parsed.append(Episode(ident, raw["x"], tuple(cleaned),
                              raw["outcome"], raw["authorized"]))
    return tuple(parsed)


def process(packet):
    if not isinstance(packet, dict) or set(packet) != {"schema", "train", "validation", "holdout"}:
        raise ValueError("BAD_PACKET_SCHEMA")
    if packet["schema"] != "motif018.memento-evidence/v0":
        raise ValueError("BAD_PACKET_VERSION")
    train, validation, holdout = [to_episodes(packet[k], k) for k in
                                  ("train", "validation", "holdout")]
    if len({e.identity for e in train + validation + holdout}) != sum(
            len(part) for part in (train, validation, holdout)):
        raise ValueError("CROSS_SPLIT_ID_COLLISION")
    selected = discover(train, validation)
    baseline = fit(train)
    classical = classical_exhaustive_selector(train, validation)
    model = selected["model"]
    # Positive outcome labels in holdout are *only* used after selecting model.
    return {
        "schema": "motif018.memento-bridge-result/v0",
        "status": selected["status"],
        "diagnostics": selected["diagnostics"],
        "candidate_concepts": selected["candidates"],
        "cartridge": selected.get("cartridge"),
        "surface_holdout": assess(baseline, holdout),
        "selected_holdout": assess(model, holdout) if model else None,
        "classical_holdout": assess(classical, holdout) if classical else None,
        "counts": {"train": len(train), "validation": len(validation),
                   "holdout": len(holdout)},
        "source": "MEMENTO caller supplied synthetic structural episodes",
        "observation_authenticated": False,
        "selection_used_holdout": False,
        "authority": "NONE",
        "external_actions": 0,
    }


def main():
    raw = sys.stdin.buffer.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        return fail("PACKET_TOO_LARGE")
    try:
        packet = json.loads(raw)
        print(json.dumps(process(packet), indent=2, sort_keys=True))
        return 0
    except (ValueError, TypeError, KeyError, RecursionError) as error:
        return fail(str(error))


if __name__ == "__main__":
    sys.exit(main())
