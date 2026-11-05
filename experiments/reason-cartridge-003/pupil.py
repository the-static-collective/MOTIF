"""Pupil and portable method contract. Never imports native Dogram.

Student selects a verified synthetic graph-query method from a finite menu.
This is *behavioral* distillation from genuine Dogram outputs, not extraction
of Dogram's actual algorithm or its internal reasoning trace.
"""
from __future__ import annotations
from collections import deque
from hashlib import sha256
from pathlib import Path
import json
import re

SCHEMA = "motif.reason.foreign-method.v1"
DOGRAM_COMMIT = "551b5f9df18f17ec69b452ddcdff01718e0ff771"
SOURCE = "the-static-collective/Dogram"
MENU = ("ALWAYS_BREAKS", "STATUS_QUO", "OUTDEGREE_PROXY", "DIRECT_SHORTCUT",
        "RECHECK_GRAPH_REACHABILITY")
MAX_BYTES = 16000


class HOLD(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def graph_input(specimen):
    if (not isinstance(specimen, dict) or specimen.get("schema") != "dogram.specimen/v0"
            or specimen.get("operator") != "ablate" or
            specimen.get("operator_version") != 1):
        raise HOLD("Unrecognized foreign teacher contract")
    meta = specimen.get("metadata")
    if (not isinstance(meta, dict) or meta.get("teacher_commit") != DOGRAM_COMMIT
            or meta.get("teacher_repo") != SOURCE):
        raise HOLD("Wrong pinned teacher")
    inp = specimen.get("inputs")
    if not isinstance(inp, dict):
        raise HOLD("Malformed foreign graph")
    graph = inp.get("graph")
    if not isinstance(graph, dict) or set(graph) != {"nodes", "edges"}:
        raise HOLD("Malformed graph schema")
    nodes, raw = graph["nodes"], graph["edges"]
    if (not isinstance(nodes, list) or not 2 <= len(nodes) <= 8 or
            any(not isinstance(n, str) or not re.fullmatch(r"[A-Za-z0-9_]{1,20}", n) for n in nodes)
            or len(set(nodes)) != len(nodes) or
            not {"S", "T"}.issubset(set(nodes)) or
            not isinstance(raw, list) or len(raw) > 28):
        raise HOLD("Invalid graph node or edge bounds")
    if (any(not isinstance(e, list) or len(e) != 2 or
            any(not isinstance(n, str) or n not in nodes for n in e) for e in raw)
            or len({tuple(e) for e in raw}) != len(raw)):
        raise HOLD("Malformed graph edges")
    removal = inp.get("target")
    if (not isinstance(removal, dict) or set(removal) != {"kind", "source", "target"}
            or removal["kind"] != "edge"
            or (removal["source"], removal["target"]) not in {tuple(x) for x in raw}
            or inp.get("requested_targets") != [["S", "T"]]):
        raise HOLD("Only valid source-owned edge ablation is supported")
    return tuple(nodes), tuple(tuple(e) for e in raw), (
        removal["source"], removal["target"])


def reach(nodes, edges, start="S", end="T"):
    # A developer-provided complete classical algorithm. Not invented by MOTIF.
    queue = deque([start])
    seen = {start}
    while queue:
        here = queue.popleft()
        if here == end:
            return True
        for a, b in edges:
            if a == here and b not in seen:
                seen.add(b)
                queue.append(b)
    return False


def predict(hypothesis, specimen):
    if hypothesis not in MENU:
        raise HOLD("Unknown method menu entry")
    nodes, edges, removed = graph_input(specimen)
    after = tuple(e for e in edges if e != removed)
    if hypothesis == "ALWAYS_BREAKS":
        return False
    if hypothesis == "STATUS_QUO":
        return reach(nodes, edges)
    if hypothesis == "OUTDEGREE_PROXY":
        return reach(nodes, edges) and sum(a == "S" for a, _ in edges) >= 2
    if hypothesis == "DIRECT_SHORTCUT":
        return ("S", "T") in after
    return reach(nodes, after)


def verify_native(specimen, receipt):
    """Native, source-attested-by-CI-run transcript; SHA is not authorship proof."""
    graph_input(specimen)
    if (not isinstance(receipt, dict)
            or receipt.get("schema") != "dogram.receipt/v0"
            or receipt.get("specimen_id") != specimen["specimen_id"]
            or receipt.get("operator") != "ablate"
            or receipt.get("operator_version") != 1
            or receipt.get("status") != "OK"
            or receipt.get("input_digest") != "sha256:" + digest(specimen)
            or receipt.get("consumed_inputs") !=
            ["inputs.graph", "inputs.requested_targets", "inputs.target"]):
        raise HOLD("Foreign result is missing, refused or unbound")
    result = receipt.get("result")
    if not isinstance(result, dict):
        raise HOLD("Foreign result was not calculable")
    targets = result.get("requested_targets")
    if (not isinstance(targets, list) or len(targets) != 1
            or not isinstance(targets[0], dict) or set(targets[0]) != {
                "source", "target", "reachable_before", "reachable_after"
            } or targets[0]["source"] != "S" or targets[0]["target"] != "T"
            or type(targets[0]["reachable_before"]) is not bool
            or type(targets[0]["reachable_after"]) is not bool):
        raise HOLD("Malformed native teaching label")
    # Do not compare to our own BFS during teaching; that's the competing
    # classical reference and would leak the target into teacher verification.
    return targets[0]["reachable_after"]


def rows(directory, split):
    root = Path(directory) / split
    result = []
    for path in sorted(root.glob("*.json")):
        if path.name.endswith(".receipt.json"):
            continue
        specimen = json.loads(path.read_text(encoding="utf-8"))
        receipt_path = path.with_suffix(".receipt.json")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        target = verify_native(specimen, receipt)
        result.append((specimen, target, receipt))
    expected = {"train": 12, "withheld": 18}
    if len(result) != expected.get(split):
        raise HOLD(f"Incorrect independent {split} witness count")
    return result


def select_method(training_rows):
    if not isinstance(training_rows, list) or len(training_rows) != 12:
        raise HOLD("Missing real native teacher observations")
    survivor = []
    distinct = set()
    for specimen, label, receipt in training_rows:
        if not isinstance(label, bool):
            raise HOLD("Nonboolean teacher correction")
        if specimen["specimen_id"] in distinct:
            raise HOLD("Repeated teacher episode")
        distinct.add(specimen["specimen_id"])
        if verify_native(specimen, receipt) != label:
            raise HOLD("Pupil cannot trust claimed training target")
    for method in MENU:
        mistakes = sum(predict(method, sp) != label for sp, label, _ in training_rows)
        if mistakes == 0:
            survivor.append(method)
    if len(survivor) != 1:
        raise HOLD("Insufficient differentiating teacher evidence")
    body = {
        "schema": SCHEMA,
        "source_repo": SOURCE,
        "source_revision": DOGRAM_COMMIT,
        "learned_method": survivor[0],
        "candidate_count": len(MENU),
        "training_count": len(training_rows),
        "training_receipts": sorted(digest(receipt) for _, _, receipt in training_rows),
        "status": "PROPOSE_ONLY",
        "scope": "BOUNDED_SYNTHETIC_GRAPH_READ_ONLY",
        "external_execution": False,
        "real_world_authority": False,
    }
    packet = dict(body, checksum_sha256=digest(body))
    raw = json.dumps(packet, sort_keys=True, indent=2) + "\n"
    validate(raw)
    return raw


def validate(raw):
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_BYTES:
        raise HOLD("Invalid or oversized transfer")
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise HOLD("Malformed method JSON") from exc
    keys = {"schema", "source_repo", "source_revision", "learned_method",
            "candidate_count", "training_count", "training_receipts", "status",
            "scope", "external_execution", "real_world_authority",
            "checksum_sha256"}
    if not isinstance(obj, dict) or set(obj) != keys:
        raise HOLD("Unknown foreign method artifact")
    if (obj["schema"] != SCHEMA or obj["source_repo"] != SOURCE
            or obj["source_revision"] != DOGRAM_COMMIT
            or obj["learned_method"] not in MENU
            or type(obj["candidate_count"]) is not int
            or obj["candidate_count"] != len(MENU)
            or type(obj["training_count"]) is not int or obj["training_count"] != 12
            or obj["status"] != "PROPOSE_ONLY"
            or obj["scope"] != "BOUNDED_SYNTHETIC_GRAPH_READ_ONLY"
            or obj["external_execution"] is not False
            or obj["real_world_authority"] is not False):
        raise HOLD("Schema, method or authority boundary changed")
    digests = obj["training_receipts"]
    if (not isinstance(digests, list) or len(digests) != 12
            or digests != sorted(set(digests))
            or any(not isinstance(x, str) or not re.fullmatch(r"[0-9a-f]{64}", x)
                   for x in digests)
            or obj["checksum_sha256"] != digest({k: v for k, v in obj.items()
                                                 if k != "checksum_sha256"})):
        raise HOLD("Corrupt or incomplete source teaching record")
    return obj
