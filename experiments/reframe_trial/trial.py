"""Run the three-bet synthetic pilot and emit a stable evidence report."""
import argparse
from collections import defaultdict
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from world import GOAL_VALUE, PRIMITIVES, case, cohort, demo_traces, witness
from composition import Call, F, Inapplicable, Trace, checked_apply, induce_macros, signature
from planner import Work, decision, plan, primitive_calls, reading


def digest(data):
    return sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def training_libraries():
    round_a = demo_traces("tabletop", 1)
    round_b = demo_traces("handoff", 2)
    return (
        induce_macros(round_a, PRIMITIVES),
        induce_macros(round_b, PRIMITIVES),
        sum(len(trace.calls) for trace in round_a + round_b),
    )


def evaluate(task, library, policy):
    work = Work()
    question, contingencies, expected = decision(
        task.beliefs, task.asset, task.observable, library, policy, work)
    commitment = {
        "question": question,
        "contingencies": [
            {"reply": reply, "plan": asdict(route) if route else None}
            for reply, route in sorted(contingencies.items())
        ],
    }
    # The owner answers only the committed question, then verifies execution.
    observed = reading(task.truth, task.asset, question)
    route = contingencies[observed]
    expanded = tuple(primitive_calls(route.calls, PRIMITIVES | library)) if route else ()
    _, execution_cost, complete = witness(task.truth, expanded, F("delivered", task.asset))
    if route and (not complete or execution_cost != route.cost):
        raise ValueError("Owner replay disagrees with the committed route")
    return {
        "case": task.id,
        "family": task.family,
        "commitment": commitment,
        "commitment_digest": digest(commitment),
        "reply": observed,
        "expected_net_value": str(expected),
        "completed": complete,
        "outcome": "DELIVERED" if complete else "HOLD",
        "net_value": (GOAL_VALUE if complete else 0) - execution_cost - len(question),
        "query_cost": len(question),
        "execution_cost": execution_cost,
        "outer_plan_calls": len(route.calls) if route else 0,
        "primitive_calls": [asdict(call) for call in expanded],
        "planner_work": asdict(work),
    }


def discover(library):
    work = Work()
    traces = []
    routes = []
    for i in range(2):
        task = case("interactive", f"discovery-{i}", ("reusable", "interface_fits"),
                    alternative=False)
        goal = F("delivered", task.asset)
        route = plan(task.truth, goal, library, work)
        if route is None:
            raise ValueError("Discovery lesson produced no route")
        expanded = tuple(primitive_calls(route.calls, PRIMITIVES | library))
        outcome, cost, complete = witness(task.truth, expanded, goal)
        if not complete or route.cost != cost:
            raise ValueError("Discovery disagrees with owner outcome")
        traces.append(Trace(task.truth, route.calls, outcome))
        routes.append({"case": task.id, "outer_calls": len(route.calls), "primitive_cost": cost})

    # Native 006 replays each discovery trace during induction.
    compiled = induce_macros(traces, PRIMITIVES | library)
    if len(compiled) != 1:
        raise ValueError("Discovery traces did not agree on a single operator")
    operator = next(iter(compiled.values()))
    catalog = PRIMITIVES | library | compiled
    verification = {}
    for label, actual, allowed in (
        ("new-binding", ("reusable", "interface_fits"), True),
        ("wrong-interface", ("reusable",), True),
        ("denied-permission", ("reusable", "interface_fits"), False),
    ):
        task = case("tabletop", label, actual, release_allowed=allowed)
        call = Call(operator.id, (task.asset,))
        goal = F("delivered", task.asset)
        expanded = tuple(primitive_calls((call,), catalog))
        try:
            predicted = checked_apply(task.truth, call.operator, call.roles, catalog)
        except Inapplicable:
            predicted = None
        try:
            observed, _, complete = witness(task.truth, expanded, goal)
        except ValueError:
            observed, complete = None, False
        if predicted != observed or complete != (label == "new-binding"):
            raise ValueError("Discovery failed independent replay or refusal")
        verification[label] = "DELIVERED" if complete else "REJECTED"

    return {
        "operator": operator.id,
        "operator_digest": signature(operator),
        "depends_on": tuple(name for name, _ in operator.pins),
        "routes": routes,
        "search_work": asdict(work),
        "induction_primitive_rechecks": operator.depth * len(traces),
        "new_case_checks": verification,
        "new_case_primitive_guard_budget": operator.depth * len(verification),
    }


def summarize(rows):
    result = defaultdict(int)
    for row in rows:
        result["cases"] += 1
        for name in ("completed", "net_value", "query_cost", "execution_cost",
                     "outer_plan_calls"):
            result[name] += row[name]
        for name, amount in row["planner_work"].items():
            result[name] += amount
    return dict(result)


def load_cohort(case_file, outcome_file):
    """Join separately authored inputs and owner outcomes by case ID."""
    cases = json.loads(case_file.read_text(encoding="utf-8"))
    outcomes = json.loads(outcome_file.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not 1 <= len(cases) <= 200 or not isinstance(outcomes, dict):
        raise ValueError("Expected 1–200 case objects and an outcome mapping")
    expected = {"family", "label", "release_allowed", "alternative", "interface_unknown"}
    tasks = []
    for entry in cases:
        if not isinstance(entry, dict) or set(entry) != expected:
            raise ValueError("Case objects must contain exactly the declared public fields")
        family, label = entry["family"], entry["label"]
        if any(not isinstance(x, str) or not x.strip() or ":" in x or len(x) > 80
               for x in (family, label)):
            raise ValueError("Family and label must be nonempty and cannot contain colons")
        flags = {k: v for k, v in entry.items() if k not in {"family", "label"}}
        if any(type(value) is not bool for value in flags.values()):
            raise ValueError("Case flags must be Boolean")
        name = f"{family}:{label}"
        actual = outcomes.get(name)
        if (not isinstance(actual, list) or any(not isinstance(x, str) for x in actual)
                or len(set(actual)) != len(actual)):
            raise ValueError(f"Expected unique present-fact names for {name}")
        tasks.append(case(family, label, actual, **flags))
    ids = {task.id for task in tasks}
    if len(ids) != len(tasks) or ids != set(outcomes):
        raise ValueError("Cases and outcomes must have identical unique IDs")
    return tuple(tasks)


def run(tasks=None):
    scope = "CALLER_SUPPLIED_SHARED_GRAMMAR" if tasks is not None else "AUTHORED_SYNTHETIC_PILOT"
    tasks = cohort() if tasks is None else tasks
    first, last, training_cost = training_libraries()
    full = first | last
    configs = (
        ("fixed_probe", {}, "fixed"),
        ("entropy_probe", {}, "entropy"),
        ("exact_primitive", {}, "decision"),
        ("motif", full, "decision"),
    )
    rows = {name: [evaluate(task, library, policy) for task in tasks]
            for name, library, policy in configs}
    for classical, motif in zip(rows["exact_primitive"], rows["motif"], strict=True):
        for field in ("completed", "expected_net_value", "net_value", "execution_cost"):
            if classical[field] != motif[field]:
                raise ValueError("Macro representation altered the exact primitive objective")
    compounding = {}
    for name, library, prior_cost in (
        ("accumulated", full, training_cost),
        ("last_round_only", last, training_cost // 2),
        ("frozen_start", {}, 0),
    ):
        result = discover(library)
        result["prior_induction_primitive_rechecks"] = prior_cost
        result["charged_guard_budget"] = (
            result["search_work"]["primitive_guard_budget"]
            + result["induction_primitive_rechecks"]
            + result["new_case_primitive_guard_budget"]
            + prior_cost
        )
        compounding[name] = result

    sources = {
        path: sha256((Path(__file__).resolve().parents[1] / path).read_bytes()).hexdigest()
        for path in ("002/motif002.py", "006/composition.py", "field004/engine.py",
                     "reframe_trial/world.py", "reframe_trial/planner.py", "reframe_trial/trial.py")
    }
    report = {
        "scope": scope,
        "sources": sources,
        "summary": {name: summarize(items) for name, items in rows.items()},
        "compounding": compounding,
        "rows": rows,
    }
    report["digest"] = digest(report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path)
    parser.add_argument("--outcomes", type=Path)
    args = parser.parse_args()
    if (args.cases is None) != (args.outcomes is None):
        parser.error("--cases and --outcomes must be supplied together")
    tasks = load_cohort(args.cases, args.outcomes) if args.cases else None
    print(json.dumps(run(tasks), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
