"""MOTIF RING-001: need-gated multi-cartridge routing over an inspected local registry.

This is a synthetic, read-only controller. A Git branch in the inventory is
NOT an installed cartridge. No code is imported from the branch inventory.
Only the original, pinned DOOR-FOUNDRY-001 allowlisted handlers can execute.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import heapq
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
DOOR_HOME = HERE.parent / "door-foundry-001"
if str(DOOR_HOME) not in sys.path:
    sys.path.insert(0, str(DOOR_HOME))
import door_foundry as door

HOLD = door.HOLD
START_TYPES = frozenset({"world", "goal"})
BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9._/-]{1,150}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def inventory(path: Path | None = None) -> tuple[dict, ...]:
    """Read a frozen branch census as untrusted, NON-EXECUTABLE metadata."""
    file = path or HERE / "branch_inventory.json"
    raw = file.read_bytes()
    if len(raw) > 100_000:
        raise HOLD("Branch census exceeds bounded size")
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise HOLD("Invalid branch census JSON") from exc
    if (not isinstance(data, dict)
            or set(data) != {"schema", "snapshot_utc", "source", "scope", "branches"}
            or data["schema"] != "motif.branch-ring-inventory.v1"
            or data["scope"] != "DISCOVERY_ONLY_NO_IMPORTS_NO_AUTHORITY"
            or not isinstance(data["branches"], list)
            or len(data["branches"]) > 1000):
        raise HOLD("Invalid branch census contract")
    names = set()
    for row in data["branches"]:
        if (not isinstance(row, dict)
                or set(row) != {"ref", "commit", "status"}
                or not isinstance(row["ref"], str)
                or not BRANCH_PATTERN.fullmatch(row["ref"])
                or row["ref"] in ("main", "master")
                or row["ref"] in names
                or not isinstance(row["commit"], str)
                or not COMMIT_PATTERN.fullmatch(row["commit"])
                or row["status"] != "DISCOVERED_ONLY"):
            raise HOLD("Invalid, duplicate, or promoted branch census row")
        names.add(row["ref"])
    return tuple(data["branches"])


def choose(targets: tuple[str, ...], caps: tuple[door.Capability, ...],
           max_cost: int = 12, max_steps: int = 8) -> tuple[str, ...]:
    """Exact bounded minimum-declared-cost typed plan for ANY target set.

    Uses the installed DOOR-FOUNDRY allowlist; branch metadata cannot add a
    handler, grant authority, or alter a signature.
    """
    if (type(max_cost) is not int or not 0 <= max_cost <= 100
            or type(max_steps) is not int or not 0 <= max_steps <= 16):
        raise HOLD("Invalid cartridge budget")
    outputs = {x.provides for x in caps}
    if not isinstance(targets, tuple) or len(targets) > 8 or any(
        not isinstance(x, str) or x not in outputs for x in targets
    ):
        raise HOLD("Unknown or uninstalled output request")
    target_set = frozenset(targets)
    if not target_set:
        return ()
    start = START_TYPES
    queue = [(0, (), start)]
    best = {start: (0, ())}
    visits = 0
    while queue:
        cost, path, types = heapq.heappop(queue)
        if best.get(types) != (cost, path):
            continue
        visits += 1
        if visits > 4096:
            raise HOLD("Cartridge search budget exhausted")
        if target_set.issubset(types):
            return path
        if len(path) >= max_steps:
            continue
        for cap in caps:
            if (cap.state == "UNAVAILABLE" or cap.provides in types
                    or not set(cap.requires).issubset(types)
                    or cost + cap.cost > max_cost):
                continue
            after = types | {cap.provides}
            proposal = (cost + cap.cost, path + (cap.id,))
            if after not in best or proposal < best[after]:
                best[after] = proposal
                heapq.heappush(queue, (*proposal, after))
    raise HOLD("No admitted, budgeted cartridge set reaches the targets")


def waves(plan: tuple[str, ...], caps: tuple[door.Capability, ...]):
    """Independent operators share a wave; dependencies wait for results."""
    by_id = {c.id: c for c in caps}
    remaining = set(plan)
    available = set(START_TYPES)
    output = []
    while remaining:
        ready = tuple(sorted(
            (by_id[name] for name in remaining
             if set(by_id[name].requires).issubset(available)),
            key=lambda c: c.id))
        if not ready:
            raise HOLD("Cyclic or missing cartridge dependencies")
        output.append(ready)
        remaining.difference_update(c.id for c in ready)
        available.update(c.provides for c in ready)
    return tuple(output)


def _summary(kind: str, value: object) -> dict:
    """Only summarize validated, local synthetic artifacts; no raw source text."""
    if kind in ("verbs", "macro_catalog"):
        return {"operator_count": len(value)}
    if kind == "frontier":
        return dict(value)
    if kind == "macro_replay":
        return {
            "operator": value["call"].operator,
            "roles": list(value["call"].roles),
            "expanded_primitive_steps": value["expanded_steps"],
            "synthetic_trace_demonstrations": value["evidence_support"],
        }
    if kind == "door":
        return dict(value)
    raise HOLD("Unknown output type")


def run(targets: tuple[str, ...] = ("door",), *,
        world=None, goal=None, max_cost: int = 12, max_steps: int = 8,
        parallel: bool = True, census_count: int | None = None) -> dict:
    branches = inventory()  # historical ancestry; never executable branch imports
    if census_count is not None and (type(census_count) is not int or not 0 <= census_count <= 2000):
        raise HOLD("Invalid live branch census count")
    caps = door.registry()
    plan = choose(targets, caps, max_cost, max_steps)
    result = {
        "schema": "motif.cartridge-ring.v1",
        "stage": "PROPOSED" if plan else "IDLE",
        "scope": door.SCOPE,
        "real_world_authority": False,
        "external_action_executed": False,
        "observed_outcome": None,
        "discovered_uninstalled_branches": (len(branches) if census_count is None else census_count),
        "requested_outputs": list(targets),
        "selected_cartridges": [],
        "waves": [],
        "artifacts": {},
    }
    if plan:
        two, three, six = door.original_modules()  # verify every source blob before import
        world = two.scene() if world is None else world
        goal = (frozenset({
            two.F("skill", "Jo", "repair"),
            two.F("usable", "bike1"),
            two.F("usable", "bike2"),
        }) if goal is None else goal)
        if (not isinstance(world, frozenset) or not isinstance(goal, frozenset)
                or len(world | goal) > 128
                or any(not isinstance(f, tuple)
                       or not all(isinstance(s, str) for s in f)
                       for f in world | goal)):
            raise HOLD("Invalid synthetic typed world or goal")
        artifacts = {"world": world, "goal": goal}
        installed = {c.id: c for c in caps}
        # Each wave reads an immutable snapshot of earlier waves. Commit no
        # partial wave if a sibling cartridge rejects or fails.
        for wave in waves(plan, caps):
            snapshot = dict(artifacts)
            def invoke(c):
                try:
                    return door.execute_handler(c.handler, snapshot,
                                                (two, three, six))
                except HOLD:
                    raise
                except Exception as exc:
                    raise HOLD("A selected cartridge failed: " + c.id) from exc
            if parallel and len(wave) > 1:
                with ThreadPoolExecutor(max_workers=min(3, len(wave))) as pool:
                    futures = [pool.submit(invoke, c) for c in wave]
                    values = [f.result() for f in futures]
            else:
                values = [invoke(c) for c in wave]
            for c, value in zip(wave, values):
                artifacts[c.provides] = value
                result["selected_cartridges"].append({
                    "id": c.id,
                    "source": c.source,
                    "source_git_blob": door.SOURCE_LOCK[c.source] if c.source else None,
                    "provides": c.provides,
                    "declared_cost_units": c.cost,
                    "state": c.state,
                })
            result["waves"].append([c.id for c in wave])
        result["artifacts"] = {t: _summary(t, artifacts[t]) for t in targets}
    result["declared_total_cost_units"] = sum(
        r["declared_cost_units"] for r in result["selected_cartridges"])
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["receipt_sha256"] = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", nargs="*", default=["door"])
    parser.add_argument("--serial", action="store_true")
    parser.add_argument("--max-cost", type=int, default=12)
    args = parser.parse_args()
    try:
        result = run(tuple(args.outputs), parallel=not args.serial,
                     max_cost=args.max_cost)
    except HOLD as exc:
        result = {"stage": "HOLD", "reason": str(exc),
                  "real_world_authority": False, "external_action_executed": False}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
