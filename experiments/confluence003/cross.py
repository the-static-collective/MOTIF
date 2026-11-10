"""CONFLUENCE-003: native method adapters on external pathfinding maps.

A verified full map is available to all policies. The 3-bit proof concerns
local option-set updates, never proof that a global grid route is valid.
"""
from __future__ import annotations

from copy import deepcopy
from itertools import count
from importlib import import_module
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "experiments" / "confluence002",
          ROOT / "experiments" / "confluence001"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from native import native_modules, source_pins  # source pins enforced here
from adapter003 import original_motif003
from source import (GridOwner, Grid, Scene, DELTAS, astar, dijkstra,
                    check_route, digest, UPSTREAM_COMMIT)


def source_verified_affordance(grid, start, blocked=frozenset()):
    """Actual MOTIF-003 functions, translated through a tiny typed grid adapter."""
    motif, sha = original_motif003()
    initial = frozenset({("position", str(start[0]), str(start[1])),
                         ("seen", str(start[0]), str(start[1]))})
    def here(world):
        point = [f for f in world if f[0] == "position"]
        if len(point) != 1:
            raise ValueError("INCONSISTENT_POSITION")
        return int(point[0][1]), int(point[0][2])

    def options(world, _verbs):
        x, y = here(world)
        for destination, _weight in grid.neighbors((x, y), blocked):
            new = frozenset(f for f in world if f[0] != "position")
            future = new | {("position", str(destination[0]), str(destination[1])),
                            ("seen", str(destination[0]), str(destination[1]))}
            yield ("move_" + str(destination), (), future)

    def utility(world, _):
        return sum(f[0] == "seen" for f in world)

    rows = motif.analyze_first_moves(initial, {}, options, utility,
                                    horizon=2, max_worlds=120)
    selected = motif.select_first_move(rows, "new-choices")
    current = {x.operator for x in motif.actions(initial, {}, options)}
    if selected is not None and selected["operator"] not in current:
        raise RuntimeError("MOTIF003_PROPOSED_INAPPLICABLE_MOVE")
    return {
        "module": "ORIGINAL_MOTIF_003",
        "sha256": sha,
        "local_options": len(current),
        "affordance_preferred": selected["operator"] if selected else None,
        "reachable_states_after_selected": (
            selected["reachable_after_first_move"] if selected else 0),
        "ranking_is_not_path_optimality": True,
        "scope": "SOURCE_GRID_READ_ONLY_NO_EXTERNAL_MOVEMENT",
    }


def native_route_macro(grid, path, modules, *, blocked=frozenset()):
    """One exact two-edge route certificate, NOT a semantic game controller."""
    if len(path) < 3 or check_route(grid, path[:3], blocked) is None:
        return {"status": "HOLD_NOT_TWO_VERIFIED_EDGES"}
    m = modules["operators"]
    defs = {
        "walk_first": m.Verb(
            "walk_first", ("bike", "person"),
            frozenset({("permits", "?1", "?1", "?0"),
                       ("edge", "?0", "a", "b"),
                       ("at", "?1", "a")}),
            frozenset({("at", "?1", "b")}),
            frozenset({("at", "?1", "a")}), 2),
        "walk_second": m.Verb(
            "walk_second", ("bike", "person"),
            frozenset({("permits", "?1", "?1", "?0"),
                       ("edge", "?0", "b", "c"),
                       ("at", "?1", "b")}),
            frozenset({("at", "?1", "c")}),
            frozenset({("at", "?1", "b")}), 2),
    }

    def source_checked(name):
        if check_route(grid, path[:3], blocked) is None:
            raise ValueError("PATH_NO_LONGER_SOURCE_VALID")
        return frozenset({
            ("bike", "segment_" + str(name)),
            ("person", "walker_" + str(name)),
            ("at", "walker_" + str(name), "a"),
            ("permits", "walker_" + str(name), "walker_" + str(name),
             "segment_" + str(name)),
            ("edge", "segment_" + str(name), "a", "b"),
            ("edge", "segment_" + str(name), "b", "c"),
        })

    def calls(i):
        roles = ("segment_" + str(i), "walker_" + str(i))
        return (m.Call("walk_first", roles), m.Call("walk_second", roles))

    traces = [m.Trace(source_checked(i), calls(i),
                      m.replay(source_checked(i), calls(i), defs))
              for i in (0, 1)]
    macros = m.induce_macros(traces, defs, min_support=2)
    if len(macros) != 1:
        raise RuntimeError("NATIVE_006_NO_UNIQUE_GUARDED_MACRO")
    macro = next(iter(macros.values()))
    catalog = dict(defs)
    catalog[macro.id] = macro
    original = source_checked(2)
    out = m.checked_apply(original, macro.id,
                          ("segment_2", "walker_2"), catalog)
    if ("at", "walker_2", "c") not in out:
        raise RuntimeError("NATIVE_MACRO_WRONG_FINAL")
    try:
        no_permission = frozenset(f for f in original if f[0] != "permits")
        m.checked_apply(no_permission, macro.id, ("segment_2", "walker_2"), catalog)
    except m.Inapplicable:
        permission_held = True
    else:
        permission_held = False
    try:
        missing_arc = frozenset(
            f for f in original if f != ("edge", "segment_2", "b", "c"))
        m.checked_apply(missing_arc, macro.id, ("segment_2", "walker_2"), catalog)
    except m.Inapplicable:
        arc_held = True
    else:
        arc_held = False
    if not permission_held or not arc_held:
        raise RuntimeError("NATIVE_006_BYPASSED_GUARD")
    return {"status": "NATIVE_TWO_STEP_CERTIFIED",
            "source_path_coordinates": list(path[:3]),
            "original_graph_arc_check": True,
            "replayed_primitive_steps": macro.depth,
            "native_macro_semantics_sha": m.signature(macro),
            "permission_guard": permission_held,
            "edge_guard": arc_held,
            "two_examples_are_RENAMED_COPIES_NOT_INDEPENDENT_DATA": True,
            "bike_type_is_synthetic_adapter_not_game_semantics": True}


class ProofService:
    """True COLLECTIVE-001 proof memory built once, rechecked per fresh case."""
    def __init__(self, modules):
        self.m = modules
        self.task = modules["specimens"].BY_KEY["cancel_or_add"]
        self.store = modules["memory"].seeds()
        inquiry = modules["weave"].investigate(self.task, self.store, mode="compose")
        if inquiry["status"] != "REVIEW_SCOPED_CANDIDATE_NOT_INSTALLED":
            raise RuntimeError("COLLECTIVE_DID_NOT_CERTIFY_SYNTHETIC_SET_RULE")
        self.input_fields = tuple(key for key, _ in self.task.fields)
        self.development_queries = inquiry["development_queries"]
        self.node = modules["answer"].first_answer(
            self.task, self.store, inquiry,
            dict(zip(self.input_fields, (0, 0))))

    def verify_update(self, initial, changed, expected):
        if any(type(x) is not int or x not in range(8)
               for x in (initial, changed, expected)):
            raise ValueError("MASK_MUST_BE_THREE_BITS")
        data = dict(zip(self.input_fields, (initial, changed)))
        updated = self.m["answer"].reenter(
            json.loads(json.dumps(self.node)), self.store.registry, inputs=data)
        node = updated["answer_node"]
        if (node["answer"]["output_mask"] != expected
                or node["answer"]["owner_oracle_output_mask"] != expected):
            raise RuntimeError("INDEPENDENT_GRID_STATE_NOT_CERTIFIED_BY_MASK_PROOF")
        return dict(status="NATIVE_SCOPED_SET_PROOF",
                    scope="ONLY_THREE_LOCAL_DIRECTION_OPTIONS",
                    source_proof_digest=node["answer"]["proof_digest"],
                    source_memory_digest=node["proof_memory"]["integrity_digest"],
                    independently_verified_64_input_cases=(
                        node["answer"]["finite_oracle_cases_verified"]),
                    reentry_new_development_questions=updated["new_development_queries"],
                    reentry_full_verification=updated["full_owner_proof_recheck_still_required"],
                    declared_option_mask_initial=initial,
                    declared_toggle_mask=changed,
                    observed_option_mask_after=expected,
                    NO_GLOBAL_ROUTE_OR_PHYSICAL_SAFETY_PROOF=True)


def fixed_three_option_cells(grid, start, first_step):
    x, y = start
    if first_step is None:
        potential = [(x + dx, y + dy) for dx, dy in DELTAS]
        potential = [p for p in potential if grid.in_bounds(p)]
    else:
        potential = [first_step] + [(x + dx, y + dy) for dx, dy in DELTAS
                                    if (x + dx, y + dy) != first_step
                                    and grid.in_bounds((x + dx, y + dy))]
    if len(potential) < 3:
        raise ValueError("NO_THREE_OPTION_APERTURE")
    return tuple(potential[:3])


def options_mask(grid, start, options, blocked):
    available = set(dict(grid.neighbors(start, blocked)))
    return sum(1 << i for i, candidate in enumerate(options)
               if candidate in available)


def field_shift_lineage(owner, first_step, modules):
    """Real FIELD008 BlanchLedger, clearly models an ARTIFICIAL changing world."""
    from native import FieldOwnerView
    native = modules["blanch"].BlanchLedger()
    view = FieldOwnerView(owner)
    initial = owner.observe(first_step)
    if initial["answer"] is not True:
        raise RuntimeError("FIRST_SOURCE_EDGE_NOT_OPEN")
    native.ink("original_map", view.normalize(initial), view)
    native.blanch("pencil_future_open", [["original_map"]])
    native.blanch("pencil_future_blocked", [["original_map"]])
    native.claim("prediction_open", [["pencil_future_open"]],
                 claim_kind="LOCAL_PREDICTION")
    native.claim("prediction_blocked", [["pencil_future_blocked"]],
                 claim_kind="LOCAL_PREDICTION")
    # The following is an engineer-authored fault injection, NOT part of the
    # external benchmark and NOT evidence of spontaneous real-world change.
    owner.shift_block(first_step)
    shifted = owner.observe(first_step)
    if shifted["answer"] is not False or not owner.verify(initial):
        raise RuntimeError("SHIFT_NOT_VERIFIED")
    native.ink("controlled_shift", view.normalize(shifted), view)
    native.resolve("prediction_open", "REFUTED_LOCAL_PREDICTION")
    native.resolve("prediction_blocked", "OBSERVED_MATCH")
    negative = native.blanch("after_open", [["prediction_open"]])
    positive = native.blanch("after_blocked", [["prediction_blocked"]])
    if (negative["state"] != "HOLD_CONTRADICTED"
            or positive["state"] != "PENCIL_CONDITIONAL"):
        raise RuntimeError("LINEAGE_SELECTIVE_RETRACTION_FAILED")
    if positive["independent_origin_count"] != 1:
        raise RuntimeError("DUPLICATE_WITNESSES_COUNTED_AS_INDEPENDENT")
    return dict(status="FIELD008_NATIVE_SELECTIVE_RETRACTION",
                source_map_origin_count=1,
                historical_observation_still_valid=owner.verify(initial),
                current_observation_verified=owner.verify(shifted),
                old_open_prediction=negative,
                new_blocked_prediction=positive,
                controlled_change_only=True,
                original_source_commit=UPSTREAM_COMMIT,
                source_receipts=[initial, shifted])
