"""Real MOTIF-003 import adapter, applied to new synthetic fencing transitions.

The planner is classical BFS. MOTIF-003 supplies its ORIGINAL action/affordance
analysis; its opportunity ranking is a diagnostic, not a safety oracle.
"""
from __future__ import annotations

from collections import deque
from functools import lru_cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


@lru_cache(maxsize=1)
def original_motif003():
    path = Path(__file__).resolve().parents[1] / "003" / "affordance.py"
    if not path.is_file():
        raise RuntimeError("canonical MOTIF-003 source missing")
    spec = spec_from_file_location("confluence_canonical_motif003", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load reviewed MOTIF-003")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, sha256(path.read_bytes()).hexdigest()


def assess(plan, worlds):
    if not worlds:
        raise ValueError("no evidence-bound worlds")
    if plan == "PANEL_AND_CHAIR" and any(w.panel_span != 2 for w in worlds):
        raise ValueError("panel plan has an unverified prerequisite")
    if plan == "MESH_AND_CHAIR" and any(not w.mesh_safe for w in worlds):
        raise ValueError("mesh plan has an unverified safety prerequisite")
    if plan not in ("PANEL_AND_CHAIR", "MESH_AND_CHAIR"):
        raise ValueError("unknown plan")

    motif, source_sha = original_motif003()
    initial = frozenset({("material", "chair"),
                         ("material", "panel" if plan == "PANEL_AND_CHAIR" else "mesh")})
    goals = frozenset({("covered", "0"), ("covered", "1"), ("covered", "2")})

    def options(world, _):
        out = []
        if plan == "PANEL_AND_CHAIR":
            if ("skill", "braced") not in world:
                out.append(("brace_panel", (), world | {("skill", "braced")}))
            if ("skill", "braced") in world and ("covered", "0") not in world:
                out.append(("place_panel", (), world | {("covered", "0"), ("covered", "1")}))
        else:
            if ("skill", "mesh_prepared") not in world:
                out.append(("prepare_mesh", (), world | {("skill", "mesh_prepared")}))
            if ("skill", "mesh_prepared") in world and ("covered", "0") not in world:
                out.append(("place_mesh", (), world | {("covered", "0"), ("covered", "1")}))
        if ("covered", "2") not in world:
            out.append(("place_chair", (), world | {("covered", "2")}))
        return out

    def utility(world, _initial):
        return len(goals & world)

    rows = motif.analyze_first_moves(initial, (), options, utility,
                                    horizon=3, max_worlds=40)
    favorite = motif.select_first_move(rows, priority="new-choices")
    # An exact goal-search controller must not blindly follow a high-affordance
    # suggestion. It checks *all* steps against the actual rewrite interface.
    queue = deque([(initial, ())])
    visited = {initial}
    trace = None
    while queue:
        world, taken = queue.popleft()
        if goals <= world:
            trace = taken
            break
        if len(taken) >= 4:
            continue
        for move in motif.actions(world, (), options):
            if move.future not in visited:
                visited.add(move.future)
                queue.append((move.future, taken + (move.operator,)))
    if trace is None:
        raise RuntimeError("no witnessed synthetic route to goal")
    if set(trace) != set(
            ("brace_panel", "place_panel", "place_chair")
            if plan == "PANEL_AND_CHAIR"
            else ("prepare_mesh", "place_mesh", "place_chair")):
        raise RuntimeError("route did not pass through expected guards")
    return dict(source="ORIGINAL_MOTIF_003_RUNTIME_IMPORT",
                original_file="experiments/003/affordance.py",
                original_source_sha256=source_sha,
                first_suggested=favorite["operator"] if favorite else None,
                first_move_candidates=len(rows),
                hypothetical_new_choices=len(favorite["new_affordances"]) if favorite else 0,
                exact_classical_route=list(trace),
                goal_reached=True,
                distinct_simulated_states=len(visited),
                scope="FICTIONAL_REWRITE_ONLY_NO_ACTION_AUTHORITY")
