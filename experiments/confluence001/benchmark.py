"""Finite, fully disclosed synthetic comparison; no real-world superiority claims."""
from __future__ import annotations

from confluence import Confluence, SyntheticOwner, WORLDS, PLANS, digest, plan_for
import json


def exact_classical_cost(first):
    """Independent two-question contingent strategy over all four fixture worlds."""
    if first not in ("measure_panel", "inspect_mesh"):
        raise ValueError("unreviewed baseline")
    second = "inspect_mesh" if first == "measure_panel" else "measure_panel"
    first_cost = 1 if first == "measure_panel" else 2
    second_cost = 1 if second == "measure_panel" else 2
    total = 0
    for w in WORLDS:
        known = [x for x in WORLDS if (
            x.panel_span == w.panel_span if first == "measure_panel"
            else x.mesh_safe == w.mesh_safe
        )]
        total += first_cost
        if plan_for(known) is None:
            total += second_cost
    return total


def benchmark():
    rows = []
    for world in WORLDS:
        owner = SyntheticOwner(world.panel_span, world.mesh_safe, True)
        controller = Confluence(owner)
        report = controller.run(budget=2)
        measured = [r["sensor"] for r in owner._issued if r["sensor"] != "permission"]
        cost = sum(1 if q == "measure_panel" else 2 for q in measured)
        should_work = world.panel_span == 2 or world.mesh_safe
        if (report["status"] == "PLAN_SIMULATED") != should_work:
            raise AssertionError("source-backed synthetic goal mismatch")
        if not controller.ledger.valid(owner):
            raise AssertionError("corrupt proof chain")
        rows.append(dict(world=world.identifier(), status=report["status"],
                         selected_plan=report["plan"], query_sequence=measured,
                         weighted_probe_cost=cost,
                         source_receipts=report["ink_count"],
                         conditional_worlds_remaining=len(report["remaining_conditional_worlds"]),
                         evidence_tip=report["proof_chain_tip"]))
    realized_cost = sum(r["weighted_probe_cost"] for r in rows)
    strong_optimal_cost = min(exact_classical_cost(first)
                              for first in ("measure_panel", "inspect_mesh"))
    if realized_cost != strong_optimal_cost:
        raise AssertionError("heuristic did not tie exact classical in fixture")
    output = dict(experiment="CONFLUENCE-001",
                  scenario="FOUR_AUTHOR_DESIGNED_SYNTHETIC_FENCE_WORLDS",
                  cases=len(rows), source_origins=1, external_actions=0,
                  actual_questions=sum(len(x["query_sequence"]) for x in rows),
                  weighted_question_cost=realized_cost,
                  exact_classical_best_weighted_cost=strong_optimal_cost,
                  full_measurement_baseline_cost=len(rows) * 3,
                  synthetically_actionable_cases=sum(x["status"] == "PLAN_SIMULATED"
                                                      for x in rows),
                  original_motif003_runtime_used=True,
                  rows=rows,
                  verdict="TIES_EXACT_CLASSICAL_ON_ENGINEER_AUTHORED_FINITE_FIXTURE",
                  limits=["not a blinded benchmark", "not an independent source",
                          "MOTIF-003 is used for affordance analysis, not to select probes",
                          "no demonstrated generalization or physical safety"])
    output["sha256"] = digest(output)
    return output


if __name__ == "__main__":
    print(json.dumps(benchmark(), sort_keys=True, indent=2))
