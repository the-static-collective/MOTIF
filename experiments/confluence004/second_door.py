"""CONFLUENCE-004 — a dead end is a *scoped* finding, not a metaphysical axiom.

Original external map path is verified. The corridor, key, tools, gate, detour,
permissions and hazards are engineer-authored overlays. This is a finite,
read-only symbolic planning experiment with strong augmented Dijkstra control.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from heapq import heappop, heappush
from pathlib import Path
from copy import deepcopy
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "experiments" / "confluence003",
             ROOT / "experiments" / "confluence001"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
from source import (Grid, Scene, astar, check_route, load_map_and_scenarios,
                    deterministic_cohort, verified_root, UPSTREAM_COMMIT)
from adapter003 import original_motif003

VARIANTS = ("KEY", "TOOL", "DETOUR", "DENIED", "UNKNOWN", "ABSENT", "HAZARD")
GATE = (3, 4)
SCHEMA = "motif.confluence004.second-door.v1"


def seal(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True, order=True)
class AgentState:
    position: int
    inventory: bool = False
    gate_open: bool = False


@dataclass(frozen=True)
class Corridor:
    source_map: str
    source_line: int
    coordinates: tuple[tuple[int, int], ...]
    published_length: float
    source_path_length: float


class Owner:
    """Synthetic gate owner, not an authenticated legal identity or API."""

    def __init__(self, corridor: Corridor, variant: str):
        if variant not in VARIANTS or len(corridor.coordinates) != 7:
            raise ValueError("NO_REVIEWED_CORRIDOR_OR_VARIANT")
        self.corridor = corridor
        self.variant = variant
        self.initial = AgentState(0)
        self.permission = ("UNKNOWN" if variant == "UNKNOWN"
                           else "DENIED" if variant == "DENIED"
                           else "GRANTED")
        self.resource_at = 1 if variant in ("KEY", "HAZARD", "DENIED", "UNKNOWN") else (
            2 if variant == "TOOL" else None)
        self.method = "REPAIR" if variant == "TOOL" else "UNLOCK"
        self.has_token = variant not in ("ABSENT", "DETOUR")
        self.hazard = variant == "HAZARD"
        self.bypass = variant == "DETOUR"
        self.source_id = "PINNED_EXTERNAL_PATH_PLUS_AUTHOR_DEFINED_CORRIDOR"
        self._read_log = []

    def observe(self, key):
        if key not in ("gate_permission", "gate_hazard", "resource_present",
                       "available_operator", "bypass_exists"):
            raise ValueError("UNAUTHORIZED_SENSOR")
        data = {
            "gate_permission": self.permission,
            "gate_hazard": self.hazard,
            "resource_present": self.has_token,
            "available_operator": self.method,
            "bypass_exists": self.bypass,
        }
        body = dict(schema=SCHEMA + ".observation",
                    kind="SOURCE_OWNED_SYNTHETIC_FIXTURE_OBSERVATION",
                    source=self.source_id,
                    upstream_git_sha=UPSTREAM_COMMIT,
                    original_map=self.corridor.source_map,
                    original_scenario_line=self.corridor.source_line,
                    property=key, value=data[key])
        record = {**body, "sha256": seal(body)}
        self._read_log.append(deepcopy(record))
        return record

    def verify(self, record):
        if not isinstance(record, dict) or record not in self._read_log:
            return False
        body = {k:v for k,v in record.items() if k != "sha256"}
        return (record.get("sha256") == seal(body)
                and record.get("source") == self.source_id
                and record.get("upstream_git_sha") == UPSTREAM_COMMIT)

    def arc(self, a, b, state: AgentState):
        if a == b or a not in range(7) or b not in range(7):
            return False
        if self.bypass and {a, b} == {2, 4}:
            return True  # Clearly authored new corridor edge.
        if abs(a-b) != 1:
            return False
        return {a, b} != set(GATE) or state.gate_open

    def symbolic_actions(self, state: AgentState):
        """Candidate-method catalogue, supplied by an engineer, not invented."""
        here = state.position
        if self.has_token and self.resource_at == here and not state.inventory:
            yield ("TAKE", AgentState(here, True, state.gate_open))
        if (here == 3 and state.inventory and not state.gate_open
                and self.permission == "GRANTED" and not self.hazard
                and not self.bypass):
            yield (self.method, AgentState(here, True, True))
        for nxt in range(7):
            if self.arc(here, nxt, state):
                yield ("MOVE:" + str(nxt), AgentState(nxt, state.inventory, state.gate_open))

    def independent_reference_steps(self, state: AgentState):
        """Separate explicit transition implementation for outcome replay."""
        result = []
        p = state.position
        if (self.has_token and p == self.resource_at and not state.inventory):
            result.append(("TAKE", AgentState(p, True, state.gate_open)))
        if (p == 3 and state.inventory and state.gate_open is False
                and self.permission == "GRANTED" and self.hazard is False
                and not self.bypass):
            result.append((self.method, AgentState(3, True, True)))
        for v in range(7):
            if v == p:
                continue
            natural = abs(v-p) == 1 and (
                not ({p,v} == {3,4}) or state.gate_open)
            alternative = self.bypass and {p,v} == {2,4}
            if natural or alternative:
                result.append(("MOVE:" + str(v),
                               AgentState(v, state.inventory, state.gate_open)))
        return tuple(result)

    def verify_path(self, steps):
        state = self.initial
        states = [state]
        for action in steps:
            candidates = dict(self.independent_reference_steps(state))
            if action not in candidates:
                return None
            state = candidates[action]
            states.append(state)
        return states if state.position == 6 else None


def nominal_reach(owner):
    """Complete BFS in *current* walk-only graph, not augmented action space."""
    start = AgentState(0)
    q, found = deque([0]), {0}
    while q:
        p = q.popleft()
        state = AgentState(p)
        for target in range(7):
            if owner.arc(p, target, state) and target not in found:
                found.add(target)
                q.append(target)
    return dict(goal_reachable=(6 in found), reached_nodes=sorted(found),
                scope="CURRENT_WALK_ONLY_GRAPH_FIXED_GATE")


def bounded_search(owner, max_expansions=256):
    """Ordinary BFS on augmented state, no automatic side-effect dispatch."""
    if type(max_expansions) is not int or max_expansions < 0:
        raise ValueError("INVALID_SEARCH_BUDGET")
    q = deque([(owner.initial, ())])
    visited = {owner.initial}
    expansions = 0
    while q:
        if expansions >= max_expansions:
            return dict(status="HOLD_BUDGET", steps=None, expansions=expansions,
                        exhausted_proof=False, discovered_states=len(visited))
        state, path = q.popleft()
        expansions += 1
        if state.position == 6:
            return dict(status="GOAL_IN_DECLARED_WORLD", steps=path,
                        expansions=expansions, exhausted_proof=False,
                        discovered_states=len(visited))
        for action, nxt in owner.symbolic_actions(state):
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, path + (action,)))
    return dict(status="NO_ROUTE_IN_DECLARED_ACTION_GRAMMAR",
                steps=None, expansions=expansions, exhausted_proof=True,
                discovered_states=len(visited))


def classical_dijkstra(owner):
    """Strong full-information classical comparator over the exact augmented space."""
    pq = [(0, 0, owner.initial)]
    seen, best, prev = set(), {owner.initial: 0}, {}
    sequence = 1
    expanded = 0
    while pq:
        score, _seq, state = heappop(pq)
        if state in seen:
            continue
        seen.add(state)
        expanded += 1
        if state.position == 6:
            route = []
            while state in prev:
                prior, op = prev[state]
                route.append(op)
                state = prior
            return dict(steps=tuple(reversed(route)), cost=score,
                        expansions=expanded)
        for action, next_state in owner.independent_reference_steps(state):
            new_cost = score + 1
            if new_cost < best.get(next_state, float("inf")):
                best[next_state] = new_cost
                prev[next_state] = state, action
                heappush(pq, (new_cost, sequence, next_state))
                sequence += 1
    return dict(steps=None, cost=None, expansions=expanded)


def motif003_aperture(owner):
    motif, source_sha = original_motif003()

    def encode(s):
        return frozenset({
            ("position", str(s.position)),
            ("inventory", str(int(s.inventory))),
            ("gate", str(int(s.gate_open))),
        })

    def decode(world):
        fields = {x[0]:x[1] for x in world}
        if len(fields) != 3:
            raise ValueError("INVALID_HYPOTHESIS")
        return AgentState(int(fields["position"]), bool(int(fields["inventory"])),
                          bool(int(fields["gate"])))

    def possibilities(world, verbs):
        for action, new in owner.symbolic_actions(decode(world)):
            yield action, (), encode(new)

    def utility(world, initial):
        state = decode(world)
        return int(state.position == 6)*10 + int(state.inventory)*2

    rows = motif.analyze_first_moves(encode(owner.initial), (), possibilities,
                                    utility, horizon=3, max_worlds=128)
    advice = motif.select_first_move(rows, "new-choices")
    first = {move.operator for move in motif.actions(encode(owner.initial),
                                                      (), possibilities)}
    if advice is not None and advice["operator"] not in first:
        raise RuntimeError("UNSOUND_MOTIF003_ADVICE")
    return dict(native="MOTIF003_REAL_EXECUTION",
                module_sha256=source_sha,
                first_legal_choices=sorted(first),
                possible_worlds_from_first_move=len(rows),
                preferred_first_step=advice["operator"] if advice else None,
                selection_is_advisory_not_truth=True)


def explain(owner, nominal, result):
    if result["status"] == "HOLD_BUDGET":
        return "HOLD_SEARCH_BUDGET_EXHAUSTED_NOT_IMPOSSIBLE"
    if result["status"] == "GOAL_IN_DECLARED_WORLD":
        if nominal["goal_reachable"]:
            return "ALTERNATE_EXISTING_ROUTE"
        if owner.method == "REPAIR":
            return "NEW_ROUTE_FROM_TOOL_AFFORDANCE"
        return "NEW_ROUTE_FROM_KEY_AFFORDANCE"
    if owner.permission == "UNKNOWN":
        return "HOLD_ASK_FOR_AUTHORIZATION"
    if owner.permission == "DENIED":
        return "HOLD_PERMISSION_DENIED"
    if owner.hazard:
        return "HOLD_HAZARD_BLOCKED"
    if not owner.has_token:
        return "CERTIFIED_NO_ROUTE_WITHIN_FINITE_AUTHORIZED_OPERATORS"
    return "HOLD_UNRESOLVED_SCOPE"


def run(owner, max_expansions=256):
    receipts = [owner.observe(name) for name in
                ("gate_permission", "gate_hazard", "resource_present",
                 "available_operator", "bypass_exists")]
    if not all(owner.verify(x) for x in receipts):
        raise RuntimeError("SOURCE_OBSERVATION_INVALID")
    initial = nominal_reach(owner)
    native = motif003_aperture(owner)
    search = bounded_search(owner, max_expansions)
    control = classical_dijkstra(owner)
    if search["status"] != "HOLD_BUDGET":
        if ((search["steps"] is None) != (control["steps"] is None)):
            raise RuntimeError("CLASSICAL_SOLVABILITY_DISAGREEMENT")
        if search["steps"] is not None and len(search["steps"]) != control["cost"]:
            raise RuntimeError("CLASSICAL_OPTIMALITY_DISAGREEMENT")
    checked = owner.verify_path(search["steps"]) if search["steps"] else None
    if (search["steps"] is not None) != (checked is not None):
        raise RuntimeError("SOURCE_OWNER_REPLAY_CONTRADICTION")
    if not owner._read_log or not all(owner.verify(x) for x in receipts):
        raise RuntimeError("SOURCE_RECEIPT_CHANGED")
    reason = explain(owner, initial, search)
    output = dict(schema=SCHEMA, status=reason,
                  simulated_fixture=owner.variant,
                  upstream_map=owner.corridor.source_map,
                  third_party_scenario_line=owner.corridor.source_line,
                  upstream_source_revision=UPSTREAM_COMMIT,
                  source_path_seven_nodes=[list(x) for x in owner.corridor.coordinates],
                  nominal_walk_only_certificate=initial,
                  methods_scope_change_required=(not initial["goal_reachable"]),
                  authorized_method=owner.method if owner.permission == "GRANTED" else None,
                  candidate_branch="PENCIL_NEW_AFFORDANCE_NOT_FACT",
                  original_motif003=native, planner="CLASSICAL_AUGMENTED_BFS",
                  search_expansions=search["expansions"],
                  search_discovered_states=search["discovered_states"],
                  bounded_search_exhausted=search["exhausted_proof"],
                  suggested_steps=list(search["steps"]) if search["steps"] else [],
                  safe_fixture_replay_verified=checked is not None,
                  classical_augmented_dijkstra_steps=(list(control["steps"])
                                                     if control["steps"] is not None else None),
                  classical_augmented_dijkstra_cost=control["cost"],
                  no_claim_of_superiority=True,
                  original_source_origin_count=1,
                  signed_source_identity=False,
                  source_receipt_sha256=[x["sha256"] for x in receipts],
                  external_actions_executed=0,
                  authority="SYNTHETIC_RESEARCH_ONLY")
    output["packet_sha256"] = seal(output)
    return output


def select_external_corridors():
    verified_root()
    selected = []
    for name in ("tiny", "dragonage"):
        grid, all_rows = load_map_and_scenarios(name)
        candidates = deterministic_cohort(name, all_rows)
        eligible = []
        for item in candidates:
            route = astar(grid, item.start, item.goal)
            if route is None:
                raise RuntimeError("MISSING_EXTERNAL_SCENARIO_ROUTE")
            path, cost, _ = route
            if abs(cost - item.oracle_length) > 1e-4 or (
                check_route(grid, path) is None):
                raise RuntimeError("EXTERNAL_SOURCE_OPTIMUM_FAILED")
            if len(path) >= 7:
                eligible.append((seal([name, item.source_line, item.start, item.goal]),
                                 item, tuple(path[:7]), cost))
        if len(eligible) < 2:
            raise RuntimeError("TOO_FEW_EXTERNAL_LONG_PATHS")
        for _, scene, positions, cost in sorted(eligible)[:2]:
            selected.append(Corridor(name, scene.source_line, positions,
                                     scene.oracle_length, cost))
    return tuple(selected)


def benchmark():
    scenarios = select_external_corridors()
    report = []
    for corridor in scenarios:
        for variant in VARIANTS:
            result = run(Owner(corridor, variant))
            route_exists = variant in ("KEY", "TOOL", "DETOUR")
            actual = result["safe_fixture_replay_verified"]
            if actual != route_exists:
                raise RuntimeError("FAILED_TO_DISTINGUISH_SCOPED_IMPOSSIBILITY")
            if variant == "UNKNOWN" and result["status"] != "HOLD_ASK_FOR_AUTHORIZATION":
                raise RuntimeError("FORGED_UNKNOWN_PERMISSION")
            if variant == "DENIED" and result["status"] != "HOLD_PERMISSION_DENIED":
                raise RuntimeError("FORGED_DENIED_PERMISSION")
            if variant == "HAZARD" and result["status"] != "HOLD_HAZARD_BLOCKED":
                raise RuntimeError("HAZARD_NOT_RESPECTED")
            if variant == "ABSENT" and result["status"] != (
                    "CERTIFIED_NO_ROUTE_WITHIN_FINITE_AUTHORIZED_OPERATORS"):
                raise RuntimeError("DECLARED_ACTION_CERTIFICATE_INVALID")
            if variant == "DETOUR" and not result["nominal_walk_only_certificate"]["goal_reachable"]:
                raise RuntimeError("MISSED_EXISTING_DETOUR")
            report.append(result)
    return dict(experiment="CONFLUENCE-004",
                upstream_source=UPSTREAM_COMMIT,
                external_corridors=len(scenarios),
                authored_gate_variants=len(VARIANTS),
                cases=len(report),
                scope_reopening_successes=sum(x["status"].startswith("NEW_ROUTE")
                                              for x in report),
                existing_alternate_routes=sum(x["status"] == "ALTERNATE_EXISTING_ROUTE"
                                               for x in report),
                authorized_simulated_goals=sum(x["safe_fixture_replay_verified"]
                                               for x in report),
                source_confirmed_holds=sum(x["status"].startswith("HOLD")
                                           for x in report),
                formally_scoped_no_route=sum(x["status"].startswith("CERTIFIED")
                                            for x in report),
                exact_classical_equal_cost_for_all_solutions=True,
                model_calls=0, external_actions=0,
                novel_algorithm=False,
                evidence="FOUR_PUBLISHED_MAP_CORRIDORS_SEVEN_AUTHOR_CREATED_VARIANTS_EACH",
                caveats=["third party map paths but authored corridor and locks",
                         "all legal operators known in advance to both planners",
                         "MOTIF003 recommendation does not control path choice",
                         "no new physics, autonomous operator invention or real permission"],
                rows=report)


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
