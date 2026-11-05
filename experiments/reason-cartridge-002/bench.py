"""Independent synthetic evaluator and matched classical controls.

Never used by the pupil. Full-state classical BFS has the same primitive
interpreter and is expected to match the learned program, not lose to it.
"""
from collections import deque
from itertools import product
from language import Case, State, OPS, HOLD, transition, execute


def independent_cases():
    cases = []
    for a, b in product((False, True), repeat=2):
        cases.append((Case(f"unseen-positive-{int(a)}{int(b)}", a, b), "DRAFT"))
    for flavor in ("stale", "blocked", "missing_lookup", "missing_challenge",
                   "unresolved_counterexample"):
        flags = {"stale": {"fresh": False}, "blocked": {"local_ok": False},
                 "missing_lookup": {"lookup_available": False},
                 "missing_challenge": {"challenge_available": False},
                 "unresolved_counterexample": {"unresolved_counterexample": True}}[flavor]
        cases.append((Case(f"unseen-negative-{flavor}", True, True, **flags), "HOLD"))
    return tuple(cases)


def classical_bfs(case):
    """Complete bounded classical reachability with the same four primitive moves."""
    start = State()
    queue = deque([(start, tuple())])
    seen = {start}
    while queue:
        state, plan = queue.popleft()
        if state.drafted:
            return {"result": "DRAFT", "length": len(plan), "plan": plan}
        for move in OPS:
            try:
                new = transition(move, state, case)
            except HOLD:
                continue
            if new not in seen:
                seen.add(new)
                queue.append((new, plan + (move,)))
    return {"result": "HOLD", "length": None, "plan": ()}


def teacher_a(case):
    # Fixed teacher routines. No joint workflow. Mimics replay-only student.
    if case.need_challenge:
        return "HOLD"
    return execute([{"op": "VERIFY_SOURCE", "guard": "ALWAYS"},
                    {"op": "EXACT_LOOKUP", "guard": "NEED_LOOKUP"},
                    {"op": "DRAFT_HYPOTHESIS", "guard": "ALWAYS"}], case)["result"]


def teacher_b(case):
    if case.need_lookup:
        return "HOLD"
    return execute([{"op": "VERIFY_SOURCE", "guard": "ALWAYS"},
                    {"op": "TEST_COUNTEREXAMPLE", "guard": "NEED_CHALLENGE"},
                    {"op": "DRAFT_HYPOTHESIS", "guard": "ALWAYS"}], case)["result"]


def fixed_teacher_router(case):
    return teacher_a(case) if case.need_lookup else teacher_b(case)


def evaluate(program):
    cases = independent_cases()
    counts = {}
    for name, solver in (("learned", lambda c: execute(program, c)["result"]),
                         ("single_teacher_router", fixed_teacher_router),
                         ("full_classical_bfs", lambda c: classical_bfs(c)["result"])):
        counts[name] = {"correct": sum(solver(case) == expected for case, expected in cases),
                        "total": len(cases),
                        "joint_positive": solver(cases[3][0]) == "DRAFT"}
    return counts
