"""Synthetic, author-assigned falsifier portfolio for RING-003.

Compare exact hypergraph routing against myopic addition and always-all,
using identical explicitly declared goal values/costs. This cannot establish
real improvement: all cases, priors and values were constructed by us.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

import hypergraph as h


def run():
    graph=h.current_graph()
    cases=[]
    successes=Counter()
    for task in h.example_tasks():
        receipt=graph.solve(task)
        exact=receipt["selected"]
        greedy=receipt["baselines"]["greedy_single_addition"]
        all_=receipt["baselines"]["always_all_if_budgeted"]
        if all_.get("status")=="NOT_FEASIBLE_UNDER_DECLARED_BUDGET":
            all_delta=None
            successes["fixed_all_unavailable"]+=1
        else:
            all_delta=exact["declared_net_utility"]-all_["declared_net_utility"]
        if exact["declared_net_utility"]+1e-9 < greedy["declared_net_utility"]:
            raise h.HOLD("Exact solver underperformed allowed greedy control")
        cases.append({
            "case":task.name,
            "operator_declared_goals":dict(task.goals),
            "exact_selection":exact["selected"],
            "exact_uncovered":exact["missing"],
            "exact_net_declared":exact["declared_net_utility"],
            "greedy_selection":greedy["selected"],
            "greedy_net_declared":greedy["declared_net_utility"],
            "fixed_all_delta_declared":all_delta,
            "exact_minus_greedy_declared":exact["declared_net_utility"]
                                          -greedy["declared_net_utility"],
        })
        if exact["declared_net_utility"]>greedy["declared_net_utility"]:
            successes["exact_above_greedy"]+=1
        if all_delta is not None and all_delta>0:
            successes["exact_above_fixed_all"]+=1
        if exact["missing"]:
            successes["partial_or_uncovered"]+=1
    return {
        "schema":"motif.hypergraph-benchmark.v1",
        "status":"SYNTHETIC_DECLARED_UTILITY_ONLY",
        "cases":cases,
        "summary":{"cases":len(cases),**dict(successes)},
        "claim":"Conditional gains on authored values, NOT empirical method benefit",
        "unseen_real_world_generalization":"NOT_TESTED",
        "actual_source_native_task_outputs_compared":False,
        "authority":"NONE",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    report=run()
    data=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(data)
        print(json.dumps(report["summary"],sort_keys=True))
    else:
        print(data,end="")


if __name__=="__main__":
    main()
