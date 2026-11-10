"""FIELD-002: one witness -> hypotheses -> composed probe -> new witnesses.

Finite research sandbox. Self-repair is explicitly limited to an authored
UNARY -> <=2-term DNF grammar ladder. The evaluator controls observations;
programs/relations are never promoted to facts without a new measurement.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
import hashlib
import json
from collections import deque

VERSION = "field002/v1"


def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class World:
    name: str
    axes: tuple[str, ...]
    revision: str

    @property
    def n(self):
        return len(self.axes)

    def outcome(self, mask):
        """Owner-only deterministic evaluator. Not passed to the investigator.

        The first two tasks are graph reachability through closed/open
        switches; the third is a resource recipe; the fourth is an adversarial
        out-of-grammar parity rule. These are authored simulations, not actual
        electrical, hydraulic or survival evidence.
        """
        if not 0 <= mask < (1 << self.n):
            raise ValueError("invalid switch/resources state")
        b = [(mask >> i) & 1 for i in range(self.n)]
        if self.name == "two_way_lamp":
            # A/B are two changeover contacts selecting rail 0 or 1.
            # Traverse actual conditional conductor edges (not a truth table).
            edges = [("power", "r0" if not b[0] else "r1"),
                     ("r1" if not b[1] else "r0", "lamp")]
            return connected(edges, "power", "lamp")
        if self.name == "parallel_pipe":
            edges = []
            if b[0]: edges.append(("in", "split"))
            if b[1]: edges.append(("split", "out"))
            if b[2]: edges.append(("split", "out"))
            return connected(edges, "in", "out")
        if self.name == "shelter_recipe":
            held = {key for i, key in enumerate(self.axes) if b[i]}
            return any(recipe <= held for recipe in (
                {"frame", "rope"}, {"frame", "screws"}))
        if self.name == "parity_3":
            return sum(b) % 2 == 1
        raise ValueError("unknown world")


def connected(edges, start, dest):
    adjacency = {}
    for a, b in edges:
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)
    seen = {start}
    todo = deque([start])
    while todo:
        for nextnode in adjacency.get(todo.popleft(), ()):
            if nextnode == dest: return True
            if nextnode not in seen:
                seen.add(nextnode)
                todo.append(nextnode)
    return False


WORLDS = (
    World("two_way_lamp", ("left_switch", "right_switch"), "lamp-wiring-001"),
    World("parallel_pipe", ("main_valve", "route_b", "route_c"), "pipe-model-001"),
    World("shelter_recipe", ("frame", "rope", "screws"), "recipe-model-001"),
    World("parity_3", ("lever_a", "lever_b", "lever_c"), "hostile-grammar-001"),
)


class Witness:
    def __init__(self, world):
        self.world = world
        self.queries = 0
    def observe(self, mask):
        result = bool(self.world.outcome(mask))
        self.queries += 1
        payload = {"schema": VERSION, "source": self.world.name,
                   "source_revision": self.world.revision,
                   "axes": list(self.world.axes), "state_mask": mask,
                   "observed": result, "kind": "SIMULATOR_OBSERVATION"}
        return {**payload, "sha256": digest(payload)}
    def verify(self, receipt):
        """A checksum alone is never accepted as truth or source identity."""
        if not isinstance(receipt, dict): return False
        payload = {k: v for k, v in receipt.items() if k != "sha256"}
        try:
            return (receipt["sha256"] == digest(payload)
                    and self.observe(receipt["state_mask"]) == receipt)
        except (TypeError, KeyError, ValueError):
            return False


def term_value(cube, state):
    return all(v < 0 or ((state >> i) & 1) == v for i, v in enumerate(cube))


def program_value(program, state):
    return any(term_value(term, state) for term in program)


def programs(n, grammar):
    """Explicitly authored synthesis space; finite exhaustive enumeration.

    A program is disjunction of zero, one or two conjunctive cubes.
    A cube is a 0/1/* condition on every variable. Semantic duplicates
    are normalized by their full truth signatures.
    """
    if grammar == "UNARY":
        allwild = (-1,) * n
        items = [(), (allwild,)]
        for i in range(n):
            for val in (0, 1):
                cube = [-1] * n
                cube[i] = val
                items.append((tuple(cube),))
    elif grammar == "DNF2":
        cubes = list(product((-1, 0, 1), repeat=n))
        items = [()] + [(c,) for c in cubes] + list(combinations(cubes, 2))
    else:
        raise ValueError("unknown grammar")
    unique = {}
    for prog in items:
        sig = tuple(int(program_value(prog, s)) for s in range(1 << n))
        # Reuse programs from unary grammar when possible (first canonical ID).
        if sig not in unique or (len(prog), repr(prog)) < (len(unique[sig]), repr(unique[sig])):
            unique[sig] = prog
    return unique


def consistent(space, receipts):
    return {sig: pg for sig, pg in space.items()
            if all(bool(sig[mask]) == bool(row["observed"]) for mask, row in receipts.items())}


def best_query(version_space, seen, current, n):
    """Balanced hypothesis disagreement; deterministic cost-aware tie-break.

    Falls back to a novel state even when model predictions all agree, so an
    unexpectedly falsifying observation is still possible. One observation is
    obtained only after the plan has been selected and executed.
    """
    options = [s for s in range(1 << n) if s not in seen]
    if not options: return None
    if not version_space: return None
    def score(s):
        yes = sum(sig[s] for sig in version_space)
        no = len(version_space) - yes
        return (min(yes, no), -(s ^ current).bit_count(), -s)
    return max(options, key=score)


def plan(from_state, to_state, n):
    toggled = [i for i in range(n) if ((from_state ^ to_state) >> i) & 1]
    states = []
    state = from_state
    for i in toggled:
        state ^= 1 << i
        states.append({"toggle_axis": i, "result_mask": state})
    assert state == to_state
    return states


def investigate(world, allow_synthesis=True, max_queries=None, initial_grammar="UNARY"):
    """Single-seed, fully witnessed finite protocol; no hidden oracle peeking.

    Inferences remain proposed until the evaluator is explicitly queried.
    The program grammar is allowed to grow once only upon a proof of
    contradiction in the initial grammar. No externally consequential action.
    """
    n = world.n
    bound = 1 << n
    limit = bound if max_queries is None else min(max_queries, bound)
    oracle = Witness(world)
    spaces = {"UNARY": programs(n, "UNARY"), "DNF2": programs(n, "DNF2")}
    observations = {}
    expansions, steps = [], []
    if initial_grammar not in spaces: raise ValueError("invalid initial grammar")
    grammar, current = initial_grammar, 0
    # One starting fact, and nothing else is observed yet.
    receipt = oracle.observe(current)
    observations[current] = receipt
    while len(observations) < limit:
        available = consistent(spaces[grammar], observations)
        if not available:
            if grammar == "UNARY" and allow_synthesis:
                expansions.append({"trigger": "UNSAT_UNARY", "after_observations": len(observations),
                                   "prior_grammar_size": len(spaces[grammar]),
                                   "composed_grammar": "DNF2", "new_candidate_functions":
                                   len(spaces["DNF2"]) - len(spaces["UNARY"]),
                                   "witnesses": sorted(observations),
                                   "status": "GRAMMAR_PROPOSAL_NOT_FACT"})
                grammar = "DNF2"
                available = consistent(spaces[grammar], observations)
            if not available: break
        chosen = best_query(available, observations, current, n)
        if chosen is None: break
        # This is a *new* composite question when >=2 primitives are combined.
        hypothesis = {"operation": "OBSERVE_AFTER_TOGGLES", "from": current,
                      "target": chosen, "plan": plan(current, chosen, n),
                      "predicted_true": sum(s[chosen] for s in available),
                      "candidate_count": len(available), "grammar": grammar,
                      "query_status": "PROPOSED"}
        before = oracle.queries
        observed = oracle.observe(chosen)
        assert oracle.queries == before + 1
        observations[chosen] = observed
        steps.append({**hypothesis, "query_status": "EXECUTED_IN_SIMULATOR",
                      "receipt_sha256": observed["sha256"],
                      "actual": observed["observed"]})
        current = chosen
    survivors = consistent(spaces[grammar], observations)
    covered = len(observations) == bound
    final_status = ("HOLD_GRAMMAR_INSUFFICIENT" if not survivors else
                    "FINITE_DOMAIN_VERIFIED" if covered else "HOLD_UNOBSERVED_STATES")
    assert oracle.queries == len(observations)
    result = {"schema": VERSION, "world": world.name,
              "source_revision": world.revision,
              "axes": world.axes, "initial_grammar": initial_grammar,
              "starting_fact": observations[0],
              "source_queries": oracle.queries,
              "composite_multitoggle_probes": sum(len(s["plan"]) > 1 for s in steps),
              "grammar": grammar, "grammar_expansions": expansions,
              "candidate_functions_initial": len(spaces["UNARY"]),
              "candidate_functions_composed": len(spaces["DNF2"]),
              "surviving_functions": len(survivors), "status": final_status,
              "program": None if not survivors or not covered else
                 [list(cube) for cube in next(iter(survivors.values()))],
              "observations": [observations[k] for k in sorted(observations)],
              "steps": steps, "limitations": ["authored finite typed grammar and simulator",
                     "no actual live physical observations", "no universal law inferred",
                     "checksum is not source authentication", "heldout source is developer-authored"]}
    result["packet_sha256"] = digest(result)
    return result


def check_packet(packet, world):
    """Refuse a rehashed, semantically forged, omitted or reordered packet."""
    try:
        if packet["packet_sha256"] != digest({k:v for k,v in packet.items() if k != "packet_sha256"}):
            return False
        rerun = investigate(world, allow_synthesis=packet["grammar_expansions"] != [],
                            max_queries=packet["source_queries"],
                            initial_grammar=packet["initial_grammar"])
        return packet == rerun
    except (KeyError, ValueError, TypeError):
        return False


def experiment():
    cases = []
    for world in WORLDS:
        experiment_case = investigate(world)
        unary_only = investigate(world, allow_synthesis=False)
        preexpanded = investigate(world, initial_grammar="DNF2")
        # Strong classical comparator: ask every possible state, and take its
        # exact table. This is the true information-equivalent comparator for
        # claims of *perfect* coverage; no speed advantage is possible here.
        full_table = tuple(int(world.outcome(s)) for s in range(1 << world.n))
        reconstructed = [None] * (1 << world.n)
        for r in experiment_case["observations"]:
            reconstructed[r["state_mask"]] = int(r["observed"])
        comparison = {
            "unary_only_queries": unary_only["source_queries"],
            "unary_only_status": unary_only["status"],
            "preexpanded_DNF2_queries": preexpanded["source_queries"],
            "preexpanded_DNF2_status": preexpanded["status"],
            "strong_classical_exhaustive_queries": 1 << world.n,
            "strong_classical_exact": True,
            "discovery_reconstructed_exact": tuple(reconstructed) == full_table,
            "exact_binary_table": full_table,
            "queries_not_run_due_to_HOLD":
            (1 << world.n) - experiment_case["source_queries"] if
            experiment_case["status"].startswith("HOLD") else 0}
        # Never add benchmark fields to the signed reproducible evidence packet.
        cases.append({"proof": experiment_case, "comparison": comparison})
    return {"experiment": "FIELD-002", "protocol": VERSION,
            "source_scope": "engineer-authored simulators; 2 graph-continuity cases, 1 recipe transfer, 1 parity negative control",
            "cases": cases,
            "summary": {"worlds": len(cases),
                 "finite_exact": sum(c["proof"]["status"] == "FINITE_DOMAIN_VERIFIED" for c in cases),
                 "honest_holds": sum(c["proof"]["status"].startswith("HOLD") for c in cases),
                 "grammar_expansion_worlds": sum(bool(c["proof"]["grammar_expansions"]) for c in cases),
                 "total_simulator_observations": sum(c["proof"]["source_queries"] for c in cases),
                 "composite_multitoggle_probes": sum(c["proof"]["composite_multitoggle_probes"] for c in cases),
                 "exact_cases_query_savings_vs_exhaustive":
                    sum(c["comparison"]["strong_classical_exhaustive_queries"] - c["proof"]["source_queries"]
                        for c in cases if c["proof"]["status"] == "FINITE_DOMAIN_VERIFIED")},
            "epistemic_verdict": "CLASSICAL_BOUNDED_COMPOSITION_NOT_AUTONOMOUS_METHOD_INVENTION"}


if __name__ == "__main__":
    print(json.dumps(experiment(), indent=2, sort_keys=True))