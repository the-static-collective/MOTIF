"""Exhaustive four-world source-preserving comparison, not independent science."""
from __future__ import annotations
from confluence import WORLDS, SyntheticOwner, digest
from benchmark import exact_classical_cost
from native import coherent_trial
import json


def run():
    rows = []
    for world in WORLDS:
        owner = SyntheticOwner(world.panel_span, world.mesh_safe)
        result = coherent_trial(owner)
        reads = [e["sensor"] for e in owner._issued if e["sensor"] != "permission"]
        weighted = sum(1 if r == "measure_panel" else 2 for r in reads)
        is_feasible = world.panel_span == 2 or world.mesh_safe
        if (result["status"] == "REVIEW_ONLY_SYNTHETIC_PROOF") != is_feasible:
            raise AssertionError("INTEGRATED_GOAL_MISMATCH")
        if result["status"] == "REVIEW_ONLY_SYNTHETIC_PROOF":
            if not (result["macro"]["primitive_replay_agrees"]
                    and result["proof"]["verified_coverage_mask"] == 7
                    and result["proof"]["reentry_new_development_queries"] == 0
                    and result["base"]["proof_chain"][-1]["payload"]["motif003"]["goal_reached"]):
                raise AssertionError("CROSS_MODULE_INVALID")
        if result["field"]["independent_source_origins"] != 1:
            raise AssertionError("FALSE_INDEPENDENT_SOURCE")
        rows.append(dict(world=world.identifier(), status=result["status"],
                         plan=result["base"]["plan"], weighted_question_cost=weighted,
                         fresh_source_reads=reads,
                         conditional_predictions=result["field"]["proposed_branch_predictions"],
                         local_predictions_refuted=result["field"]["refuted_predictions"],
                         four_native_methods_called=(result["proof"] is not None),
                         external_actions=0,
                         proof_or_hold_tip=result["packet_sha256"] if
                             "packet_sha256" in result else result["base"]["proof_chain_tip"]))
    total = sum(x["weighted_question_cost"] for x in rows)
    best_classical = min(exact_classical_cost(x)
                         for x in ("measure_panel", "inspect_mesh"))
    if total != best_classical:
        raise AssertionError("MOTIF_WIN_LOSS_UNEXPECTED")
    output = dict(experiment="CONFLUENCE-002", cases=4,
                  integrated_method_count=4, real_source_003_006_field008_collective001=True,
                  cross_module_successes=sum(x["four_native_methods_called"] for x in rows),
                  synthetic_goals=3,
                  total_weighted_source_questions=total,
                  exact_classical_optimum_cost=best_classical,
                  full_read_baseline_cost=12,
                  source_origins=1, new_model_calls=0, external_actions=0,
                  benchmark_caveat="authored same-source tiny synthetic construction domain",
                  verdict="FOUR_REAL_METHODS_INTEROPERATE_BUT_NO_GAIN_OVER_EXACT_CLASSICAL",
                  rows=rows)
    output["sha256"] = digest(output)
    return output


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
