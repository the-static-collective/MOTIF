"""Unfamiliar-world trial against source-pinned independently published maps.

The underlying planner IS classical A*. Other methods provide separate
source verification, action preview, guarded macro and scoped proof. Test
ablation as evidence-layer loss, not falsely improved shortest-path accuracy.
"""
from __future__ import annotations

from functools import lru_cache
import json

from source import (GridOwner, load_map_and_scenarios, deterministic_cohort,
                    astar, dijkstra, check_route, digest, verified_root)
from cross import (native_modules, source_verified_affordance, native_route_macro,
                   ProofService, fixed_three_option_cells, options_mask,
                   field_shift_lineage)


FLAGS = frozenset(("affordance003", "macro006", "lineage008", "proof001"))
MODES = {
    "FULL": FLAGS,
    "NO_003": FLAGS - {"affordance003"},
    "NO_006": FLAGS - {"macro006"},
    "NO_FIELD": FLAGS - {"lineage008"},
    "NO_PROOF": FLAGS - {"proof001"},
}


def ensure_optimal(actual, baseline, published, *, original):
    if actual is None or baseline is None:
        raise RuntimeError("SOURCE_PATH_NOT_REACHABLE")
    a_path, a_cost, _ = actual
    b_path, b_cost, _ = baseline
    if abs(a_cost - b_cost) > 1e-7:
        raise RuntimeError("COMPETITIVE_CLASSICAL_COST_DISAGREEMENT")
    if original and abs(a_cost - published) > 1e-4:
        raise RuntimeError("INDEPENDENT_PUBLISHED_OPTIMUM_DISAGREES")
    if not a_path or not b_path:
        raise RuntimeError("EMPTY_ROUTE")


def run_trial(grid, scene, modules, proofs, mode="FULL"):
    if mode not in MODES:
        raise ValueError("UNREVIEWED_COMPOSITION_MODE")
    enabled = MODES[mode]
    owner = GridOwner(grid)

    # Planner takes *only* coordinates + source map. No oracle distance.
    ordinary = astar(grid, scene.start, scene.goal)
    conventional = dijkstra(grid, scene.start, scene.goal)
    ensure_optimal(ordinary, conventional, scene.oracle_length, original=True)
    path, cost, expanded = ordinary
    if abs(check_route(grid, path) - cost) > 1e-7:
        raise RuntimeError("INDEPENDENT_ROUTE_REPLAY_FAILED")

    # Local source receipts are separate from the public scenario's hindsight
    # optimal-distance field, which the planner never receives.
    start_receipt = owner.observe(scene.start)
    if not owner.verify(start_receipt):
        raise RuntimeError("THIRD_PARTY_SOURCE_RECHECK_FAILED")
    motif003 = (source_verified_affordance(grid, scene.start)
                if "affordance003" in enabled else None)
    macro = (native_route_macro(grid, path, modules)
             if "macro006" in enabled else None)

    first_step = path[1] if len(path) > 1 else None
    option_cells = fixed_three_option_cells(grid, scene.start, first_step)
    old_options = options_mask(grid, scene.start, option_cells, owner.blocked)

    # A change is possible only if a path step exists and there is at least
    # one alternative immediately accessible edge. Otherwise do not fake one.
    alternatives = set(dict(grid.neighbors(scene.start))) - (
        {first_step} if first_step is not None else set())
    inject = first_step is not None and first_step != scene.goal and bool(alternatives)
    native_field = None
    if inject:
        if "lineage008" in enabled:
            native_field = field_shift_lineage(owner, first_step, modules)
        else:
            owner.shift_block(first_step)
            update = owner.observe(first_step)
            if not owner.verify(update):
                raise RuntimeError("CONTROLLED_UPDATE_NOT_VERIFIED")
        if owner.route_reality(path) is not None:
            raise RuntimeError("SOURCE_SHIFT_FAILED_TO_INVALIDATE_OLD_ROUTE")

    revised = astar(grid, scene.start, scene.goal, owner.blocked)
    revised_classical = dijkstra(grid, scene.start, scene.goal, owner.blocked)
    if (revised is None) != (revised_classical is None):
        raise RuntimeError("SHIFTED_CLASSICAL_DISAGREEMENT")
    if revised is not None:
        ensure_optimal(revised, revised_classical, 0, original=False)
        if abs(check_route(grid, revised[0], owner.blocked) - revised[1]) > 1e-7:
            raise RuntimeError("SHIFTED_ROUTE_REPLAY_FAILURE")

    new_options = options_mask(grid, scene.start, option_cells, owner.blocked)
    toggled = old_options ^ new_options
    native_proof = (proofs.verify_update(old_options, toggled, new_options)
                    if "proof001" in enabled else None)

    if not owner.check():
        raise RuntimeError("PREVIOUS_SOURCE_RECEIPTS_INVALID_AFTER_SHIFT")
    source_hashes = [r["sha256"] for r in owner.issued]
    result = dict(
        status="REPLANNED_AFTER_CONTROLLED_CHANGE" if inject else "NO_CHANGE_REQUIRED",
        case=f"{grid.label}:{scene.source_line}",
        source=grid.label, scenario_line=scene.source_line, bucket=scene.bucket,
        original_published_optimum=scene.oracle_length,
        pre_change_astar_cost=round(cost, 6),
        pre_change_dijkstra_cost=round(conventional[1], 6),
        original_full_info_astar_expansions=expanded,
        original_dijkstra_expansions=conventional[2],
        original_path_edges=len(path)-1,
        controlled_fault_injection=inject,
        overlay_revision=owner.epoch,
        post_change_route_exists=revised is not None,
        post_change_astar_cost=(round(revised[1],6) if revised else None),
        post_change_classical_cost=(round(revised_classical[1],6)
                                    if revised_classical else None),
        native_003=motif003 is not None,
        native_006=(macro is not None and
                    macro["status"] == "NATIVE_TWO_STEP_CERTIFIED"),
        native_006_hold=(macro is not None and
                         macro["status"] == "HOLD_NOT_TWO_VERIFIED_EDGES"),
        native_008=native_field is not None,
        native_proof001=native_proof is not None,
        updated_mask_source_truth=[old_options, new_options],
        native_proof001_scope=(native_proof["scope"] if native_proof else None),
        original_receipt_sha256=start_receipt["sha256"],
        source_receipt_digests=source_hashes,
        proof_identity_not_authenticated=True,
        source_origin_count=1,
        reentry_new_development_questions=(
            native_proof["reentry_new_development_questions"] if native_proof else None),
        authority="NO_EXTERNAL_ACTIONS_OR_REAL_WORLD_SAFETY_CLAIM",
        policy=mode,
    )
    result["packet_sha256"] = digest(result)
    return result


def benchmark():
    verified_root()
    modules = native_modules()
    proofs = ProofService(modules)
    result = []
    for name in ("tiny", "dragonage"):
        grid, all_scenes = load_map_and_scenarios(name)
        cohort = deterministic_cohort(name, all_scenes)
        for scene in cohort:
            full = run_trial(grid, scene, modules, proofs, "FULL")
            variants = {mode: run_trial(grid, scene, modules, proofs, mode)
                        for mode in MODES if mode != "FULL"}
            core = ("pre_change_astar_cost", "post_change_astar_cost",
                    "post_change_route_exists", "controlled_fault_injection")
            for mode, other in variants.items():
                if tuple(full[k] for k in core) != tuple(other[k] for k in core):
                    raise RuntimeError("ABLATION_CHANGED_SHARED_CLASSICAL_ROUTE")
            if not full["native_003"] or not full["native_proof001"]:
                raise RuntimeError("CORE_NATIVE_METHOD_NOT_EXECUTED")
            if full["original_path_edges"] >= 2 and not full["native_006"]:
                raise RuntimeError("NATIVE_006_MISSED_AVAILABLE_ROUTE")
            if full["controlled_fault_injection"] and not full["native_008"]:
                raise RuntimeError("NATIVE_LINEAGE_MISSED_SHIFT")
            if variants["NO_003"]["native_003"] or variants["NO_006"]["native_006"]:
                raise RuntimeError("DISABLED_NATIVE_COMPONENT_EXECUTED")
            if variants["NO_FIELD"]["native_008"] or variants["NO_PROOF"]["native_proof001"]:
                raise RuntimeError("DISABLED_PROOF_COMPONENT_EXECUTED")
            result.append(full)
    total = len(result)
    if total != 16:
        raise RuntimeError("EXPECTED_FIXED_SIXTEEN_EXTERNAL_SCENARIOS")
    summary = {
        "experiment": "CONFLUENCE-003",
        "source_repository": "ovunctuzel/GridWorldPathfinding",
        "source_git_revision": verified_root(),
        "cohort_size": total,
        "each_domain": {name: sum(r["source"] == name for r in result)
                        for name in ("tiny", "dragonage")},
        "independently_published_lengths_matched": total,
        "competitive_classical_astar_and_dijkstra_same_cost": total,
        "native_003_executed": sum(r["native_003"] for r in result),
        "native_006_executed": sum(r["native_006"] for r in result),
        "native_008_controlled_shift_evidence": sum(r["native_008"] for r in result),
        "native_collective_exact_scoped_proof_reentered": sum(
            r["native_proof001"] for r in result),
        "controlled_injected_changes": sum(r["controlled_fault_injection"] for r in result),
        "shifted_routes_reached": sum(
            r["post_change_route_exists"] and r["controlled_fault_injection"]
            for r in result),
        "full_vs_classical_route_cost_delta": 0,
        "full_vs_each_native_ablation_route_cost_delta": {
            name: 0 for name in MODES if name != "FULL"},
        "original_astar_total_node_expansions": sum(
            r["original_full_info_astar_expansions"] for r in result),
        "original_dijkstra_total_node_expansions": sum(
            r["original_dijkstra_expansions"] for r in result),
        "independent_source_origins": 1,
        "external_actions": 0,
        "model_calls": 0,
        "reentry_original_development_questions": proofs.development_queries,
        "reentry_new_development_questions": 0,
        "status": "NATIVE_INTEROP_ON_THIRD_PARTY_MAPS_NO_ALGORITHMIC_PATHFINDING_GAIN",
        "limits": [
            "external original maps and labels but adapter/selection authored here",
            "not a third-party-blind hidden mechanism trial",
            "full source map available to all methods, not uncertain navigation",
            "classical A* remains the path planner and equally strong comparator",
            "original source optimal lengths do not cover controlled mutations",
            "native 006 checks a two-edge symbolic fixture, not physical motion",
            "FIELD-008 retraction concerns authored future hypotheses",
            "COLLECTIVE-001 only verifies explicit 3-bit local option-set XOR",
            "no external action or deployment",
        ],
        "cases": result,
    }
    summary["sha256"] = digest(summary)
    return summary


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
