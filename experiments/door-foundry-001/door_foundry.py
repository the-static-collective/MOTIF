"""DOOR-FOUNDRY-001: typed, source-pinned composition of actual MOTIF organs.

LOCAL SYNTHETIC DEMONSTRATION ONLY. A composed hypothetical edit is not an
observed event, external capability, real permission, or approved action.
Python 3.10+, standard library. No dynamic imports from registry values.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import heapq
import importlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

# These are exact *Git blob* hashes of original main-branch source files.
# Updating a source means consciously reviewing and changing this lock.
SOURCE_LOCK = {
    "experiments/002/motif002.py": "b9f1e7b7879a94f7ef3869bc305608c4d7fa8695",
    "experiments/003/affordance.py": "db25da0d50a9c8e2cd87aa576a22f969405737cf",
    "experiments/006/composition.py": "953e1cf4072be5a3ff1f29dcef1edbfc39ba8be0",
}
ALLOWED_HANDLERS = {
    "induce_original_002": ((), "verbs"),
    "compile_original_006": (("verbs",), "macro_catalog"),
    "frontier_original_003": (("world", "verbs"), "frontier"),
    "replay_original_006": (("world", "goal", "macro_catalog"), "macro_replay"),
    "assemble_local_door": (("world", "goal", "frontier", "macro_replay"), "door"),
}
SCOPE = "SYNTHETIC_PROPOSAL_ONLY"
VALID_STATES = {"EXPERIMENTAL_VERIFIED", "MAIN_VERIFIED", "UNAVAILABLE"}


class HOLD(ValueError):
    """Refuse, preserve uncertainty, and make no external effects."""


@dataclass(frozen=True)
class Capability:
    id: str
    handler: str
    requires: tuple[str, ...]
    provides: str
    cost: int
    state: str
    source: str | None
    scope: str


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def verify_sources() -> None:
    """An altered or absent owner module cannot enter the runtime."""
    for path, expected in SOURCE_LOCK.items():
        full = ROOT / path
        if not full.is_file() or git_blob(full) != expected:
            raise HOLD("Pinned source missing or changed: " + path)


def registry(path: Path | None = None) -> tuple[Capability, ...]:
    """Data-only registry; it cannot name arbitrary Python code to run."""
    raw = (path or HERE / "registry.json").read_bytes()
    if len(raw) > 32000:
        raise HOLD("Oversized registry")
    try:
        obj = json.loads(raw)
    except ValueError as exc:
        raise HOLD("Malformed capability registry") from exc
    if not isinstance(obj, list) or not 1 <= len(obj) <= 32:
        raise HOLD("Invalid capability registry")
    caps = []
    for row in obj:
        fields = {"id", "handler", "requires", "provides", "cost",
                  "state", "source", "scope"}
        if not isinstance(row, dict) or set(row) != fields:
            raise HOLD("Unexpected capability contract")
        handler = row["handler"]
        if handler not in ALLOWED_HANDLERS:
            raise HOLD("Unknown capability handler")
        req, produced = ALLOWED_HANDLERS[handler]
        if (row["requires"] != list(req) or row["provides"] != produced or
                row["scope"] != SCOPE or row["state"] not in VALID_STATES or
                type(row["cost"]) is not int or not 0 < row["cost"] <= 100 or
                not isinstance(row["id"], str) or not row["id"].isascii() or
                not 1 <= len(row["id"]) <= 70):
            raise HOLD("Capability signature, scope, or cost mismatch")
        expected_source = {
            "induce_original_002": "experiments/002/motif002.py",
            "compile_original_006": "experiments/006/composition.py",
            "frontier_original_003": "experiments/003/affordance.py",
            "replay_original_006": "experiments/006/composition.py",
            "assemble_local_door": None,
        }[handler]
        if row["source"] != expected_source:
            raise HOLD("Source binding mismatch")
        caps.append(Capability(row["id"], handler, req, produced,
                               row["cost"], row["state"], row["source"],
                               row["scope"]))
    if len({x.id for x in caps}) != len(caps):
        raise HOLD("Duplicate capability id")
    if len({x.handler for x in caps}) != len(caps):
        raise HOLD("Duplicate capability handler")
    return tuple(sorted(caps, key=lambda x: x.id))


def compose(caps: tuple[Capability, ...], available: set[str],
            target: str = "door", max_steps: int = 8):
    """Bounded exact typed-state Dijkstra; no chosen order is hardcoded.

    Costs are operator declarations, NOT measured energy, economics, or value.
    Only locally source-verified eligible handlers can be used.
    """
    if max_steps < 0 or max_steps > 16:
        raise HOLD("Planning depth out of bounds")
    start = frozenset(available)
    queue = [(0, (), start)]
    best = {start: (0, ())}
    checked = 0
    while queue:
        cost, path, types = heapq.heappop(queue)
        if best.get(types) != (cost, path):
            continue
        checked += 1
        if checked > 4096:
            raise HOLD("Search budget exceeded")
        if target in types:
            return path
        if len(path) == max_steps:
            continue
        for cap in caps:
            if (cap.state == "UNAVAILABLE" or cap.provides in types or
                    not set(cap.requires).issubset(types)):
                continue
            new_types = types | {cap.provides}
            proposal = (cost + cap.cost, path + (cap.id,))
            if new_types not in best or proposal < best[new_types]:
                best[new_types] = proposal
                heapq.heappush(queue, (*proposal, new_types))
    raise HOLD("No eligible typed composition reaches the target")


def original_modules():
    """Known owners, verified before loading; not registry-controlled paths."""
    verify_sources()
    for folder in ("002", "003", "006"):
        path = str(ROOT / "experiments" / folder)
        if path not in sys.path:
            sys.path.insert(0, path)
    return (importlib.import_module("motif002"),
            importlib.import_module("affordance"),
            importlib.import_module("composition"))


def execute_handler(handler: str, artifacts: dict, modules) -> object:
    two, three, six = modules
    if handler == "induce_original_002":
        return two.induce(two.lessons())
    if handler == "compile_original_006":
        verbs = artifacts["verbs"]
        traces, inner, outer = six.two_level_training(verbs)
        if len(traces) < 2 or inner.depth >= outer.depth:
            raise HOLD("Macro has insufficient source evidence")
        return dict(verbs, **{inner.id: inner, outer.id: outer})
    if handler == "frontier_original_003":
        rows = three.analyze_first_moves(
            artifacts["world"], artifacts["verbs"],
            two.possibilities, two.utility, horizon=3, max_worlds=500)
        if not rows or any(row["truncated"] for row in rows):
            raise HOLD("Unavailable or truncated synthetic affordance frontier")
        chosen = three.select_first_move(rows, "new-choices")
        return {"candidate_count": len(rows),
                "first_operator": chosen["operator"],
                "first_roles": list(chosen["roles"]),
                "new_choice_count": len(chosen["new_affordances"]),
                "reachable_after_first_move": chosen["reachable_after_first_move"]}
    if handler == "replay_original_006":
        world, catalog, goal = (artifacts["world"],
                                artifacts["macro_catalog"], artifacts["goal"])
        eligible = [name for name, op in catalog.items()
                    if isinstance(op, six.Macro) and op.depth >= 2]
        try:
            outcomes = list(six.available_macros(
                world, catalog, tuple(eligible), max_groundings=500))
        except (ValueError, six.Inapplicable) as exc:
            raise HOLD("Synthetic macro grounding unavailable") from exc
        matches = sorted(
            ((call, after) for call, after in outcomes
             if goal.issubset(after) and after != world),
            key=lambda v: (catalog[v[0].operator].depth,
                           v[0].operator, v[0].roles))
        if not matches:
            raise HOLD("No independently rechecked macro reaches declared goal")
        call, predicted = matches[0]
        # Recheck the whole candidate one more time against pinned components.
        if six.checked_apply(world, call.operator, call.roles, catalog) != predicted:
            raise HOLD("Macro replay disagreement")
        return {"call": call, "predicted": predicted,
                "expanded_steps": catalog[call.operator].depth,
                "evidence_support": catalog[call.operator].demonstrations}
    if handler == "assemble_local_door":
        world, goal = artifacts["world"], artifacts["goal"]
        frontier = artifacts["frontier"]
        replay = artifacts["macro_replay"]
        predicted = replay["predicted"]
        if not goal or goal.issubset(world) or not goal.issubset(predicted):
            raise HOLD("Goal is already true, empty, or not reached")
        return {
            "schema": "motif.door.v0",
            "stage": "PROPOSED",
            "scope": SCOPE,
            "real_world_authority": False,
            "external_action_executed": False,
            "observed_outcome": None,
            "goal_facts": [list(x) for x in sorted(goal)],
            "predicted_new_facts": [list(x) for x in sorted(predicted - world)],
            "affordance_first_move": frontier,
            "replayed_macro": {
                "operator": replay["call"].operator,
                "roles": list(replay["call"].roles),
                "expanded_primitive_steps": replay["expanded_steps"],
                "synthetic_trace_demonstrations": replay["evidence_support"],
            },
            "limitations": [
                "The first affordance move is not claimed to equal the macro's first step.",
                "Hypothetical replay is not an observed outcome.",
                "Synthetic permissions do not establish anyone's real consent.",
                "A macro does not reduce underlying physical actions.",
            ],
        }
    raise HOLD("No authorized handler")


def run(world=None, goal=None, caps=None) -> dict:
    two, three, six = original_modules()
    world = world if world is not None else two.scene()
    goal = goal if goal is not None else frozenset({
        two.F("skill", "Jo", "repair"),
        two.F("usable", "bike1"),
        two.F("usable", "bike2"),
    })
    if not isinstance(world, frozenset) or not isinstance(goal, frozenset):
        raise HOLD("World and goal must be immutable typed synthetic facts")
    if (any(not isinstance(f, tuple) or not all(isinstance(x, str)
            for x in f) for f in world | goal) or len(world | goal) > 128):
        raise HOLD("Malformed or oversized synthetic field")
    caps = caps if caps is not None else registry()
    plan = compose(caps, {"world", "goal"})
    by_id = {c.id: c for c in caps}
    artifacts = {"world": world, "goal": goal}
    receipts = []
    for cap_id in plan:
        cap = by_id[cap_id]
        if cap.state == "UNAVAILABLE":
            raise HOLD("Unavailable candidate was selected")
        result = execute_handler(cap.handler, artifacts, (two, three, six))
        artifacts[cap.provides] = result
        receipts.append({"id": cap.id, "provides": cap.provides,
                         "source": cap.source,
                         "source_git_blob": (SOURCE_LOCK[cap.source]
                                             if cap.source else None),
                         "state": cap.state,
                         "declared_cost_units": cap.cost})
    door = artifacts["door"]
    # A conventional, independent original MOTIF-002 planner is the baseline.
    baseline = two.explore(world, artifacts["verbs"], steps=3)
    baseline_hit = goal.issubset(baseline["final"])
    door["fixed_classical_baseline"] = {
        "original_002_goal_reached": baseline_hit,
        "original_002_primitive_steps": len(baseline["path"]),
        "note": "No claimed advantage over the existing fixed classical planner."
    }
    door["composition"] = receipts
    door["declared_total_cost_units"] = sum(x["declared_cost_units"]
                                             for x in receipts)
    body = json.dumps(door, sort_keys=True, separators=(",", ":"))
    door["content_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    return door


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deny-synthetic-permission", action="store_true",
                        help="Demonstrate a required HOLD, not an external denial")
    args = parser.parse_args()
    try:
        if args.deny_synthetic_permission:
            two, _, _ = original_modules()
            result = run(world=two.scene(permissions=False))
        else:
            result = run()
    except HOLD as exc:
        result = {"stage": "HOLD", "reason": str(exc),
                  "real_world_authority": False, "external_action_executed": False}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
