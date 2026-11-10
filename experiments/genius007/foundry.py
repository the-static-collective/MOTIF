"""MOTIF-GENIUS-007: THE QUESTION FOUNDRY.

Goal-directed synthesis of *typed candidate experiments* from capability
requirements and a declared finite laboratory instrument grammar.

All possible query outcomes are hypothetical until a supported measurement
is performed. The true world is read only AFTER choosing an experiment.
This is classical combinatorial experimental design, not the autonomous
invention of new science, hardware, mathematics, or social intelligence.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product
from math import log2
from typing import Optional

POLICIES = (
    "DIRECT_ENTROPY", "DIRECT_OPTIMAL", "FOUNDRY_ENTROPY",
    "FOUNDRY_GREEDY", "FOUNDRY_LOOKAHEAD2", "FOUNDRY_OPTIMAL",
)


@dataclass(frozen=True, order=True)
class Literal:
    variable: str
    equals: int


@dataclass(frozen=True)
class Capability:
    name: str
    prerequisites: tuple[Literal, ...]
    reward: int


@dataclass(frozen=True)
class Instrument:
    sensor_variables: tuple[str, ...]
    direct_cost: int = 2
    pair_cost: int = 3
    can_pair: bool = True
    source_ref: str = "synthetic:declared-instrument"

    def validate(self) -> None:
        if (not self.sensor_variables
                or len(self.sensor_variables) != len(set(self.sensor_variables))
                or any(not v for v in self.sensor_variables)
                or self.direct_cost < 1 or self.pair_cost < 1
                or not self.source_ref):
            raise ValueError("Invalid public instrument contract")


@dataclass(frozen=True)
class Task:
    name: str
    instrument: Instrument
    capabilities: tuple[Capability, ...]
    budget: int


@dataclass(frozen=True)
class Query:
    """New expression composed from public capability literals and operator."""

    kind: str                     # DIRECT or PAIR_MATCH
    tests: tuple[Literal, ...]
    cost: int
    derived_from: tuple[str, ...]
    operator_source: str

    @property
    def key(self) -> str:
        if self.kind == "DIRECT":
            return "d:" + self.tests[0].variable
        return "p:" + "&".join(f"{l.variable}={l.equals}" for l in self.tests)


@dataclass(frozen=True)
class World:
    """Simulator-owned truth. The planner never receives this object."""
    variables: tuple[str, ...]
    bits: tuple[int, ...]

    def value(self, var: str) -> int:
        return self.bits[self.variables.index(var)]


def validate(task: Task) -> None:
    task.instrument.validate()
    if task.budget < 0 or task.budget > 10 or not task.name:
        raise ValueError("Bounded nonnegative inquiry budget required")
    if not task.capabilities:
        raise ValueError("One explicit objective required")
    if len(set(c.name for c in task.capabilities)) != len(task.capabilities):
        raise ValueError("Duplicate capability id")
    allowed = set(task.instrument.sensor_variables)
    for c in task.capabilities:
        if not c.name or c.reward < 0 or not 1 <= len(c.prerequisites) <= 6:
            raise ValueError("Invalid capability")
        observed = {}
        for lit in c.prerequisites:
            if lit.variable not in allowed or type(lit.equals) is not int or lit.equals not in (0, 1):
                raise ValueError("Invalid/unsupported requirement")
            if lit.variable in observed:
                raise ValueError("Repeated/contradictory requirement")
            observed[lit.variable] = lit.equals


def _pair_candidates(task: Task) -> tuple[Query, ...]:
    """COMPOSE new candidate formulas, never copy from a question menu.

    A pair is physically admissible only because the explicitly declared
    instrumentation supports this exact two-channel match assay.
    Derivation records which public capability clauses suggested the pair.
    """
    if not task.instrument.can_pair:
        return ()
    source_map: dict[tuple[Literal, Literal], set[str]] = {}
    for cap in task.capabilities:
        for a, b in combinations(sorted(cap.prerequisites), 2):
            source_map.setdefault((a, b), set()).add(cap.name)
    return tuple(
        Query("PAIR_MATCH", lits, task.instrument.pair_cost,
              tuple(sorted(origins)), task.instrument.source_ref)
        for lits, origins in sorted(source_map.items())
    )


def candidates(task: Task, include_synthesis: bool) -> tuple[Query, ...]:
    validate(task)
    # Direct probes are part of public instrumentation, including *irrelevant*
    # variables: an entropy-only baseline must be free to choose them.
    direct = tuple(
        Query("DIRECT", (Literal(var, 1),), task.instrument.direct_cost,
              (), task.instrument.source_ref)
        for var in sorted(task.instrument.sensor_variables)
    )
    generated = _pair_candidates(task) if include_synthesis else ()
    return tuple(sorted(direct + generated, key=lambda q: q.key))


def verify_instrument(task: Task, query: Query) -> bool:
    """Explicit physical-feasibility and cost check before simulated reading."""
    if query.operator_source != task.instrument.source_ref:
        return False
    if query.kind == "DIRECT":
        return (
            len(query.tests) == 1
            and query.tests[0].variable in task.instrument.sensor_variables
            and query.tests[0].equals == 1
            and query.cost == task.instrument.direct_cost
        )
    if query.kind == "PAIR_MATCH":
        return query in _pair_candidates(task) and query.cost == task.instrument.pair_cost
    return False


def observation(task: Task, query: Query, world: World) -> dict:
    """Independent synthetic sensor oracle. Not available inside planning."""
    if not verify_instrument(task, query):
        return {
            "status": "HOLD_UNSUPPORTED_INSTRUMENT_OR_COST",
            "no_measurement_taken": True,
            "source": task.instrument.source_ref,
        }
    if world.variables != task.instrument.sensor_variables or (
        len(world.bits) != len(world.variables)
        or any(type(v) is not int or v not in (0, 1) for v in world.bits)
    ):
        return {"status": "HOLD_OUTSIDE_DECLARED_MODEL",
                "no_measurement_taken": True}
    if query.kind == "DIRECT":
        response = world.value(query.tests[0].variable)
    else:
        response = int(all(world.value(l.variable) == l.equals for l in query.tests))
    return {
        "status": "SYNTHETIC_MEASUREMENT_RECEIPT",
        "response": response,
        "source": task.instrument.source_ref,
        "query": query.key,
        "declared_cost": query.cost,
        "derivation_from_objectives": list(query.derived_from),
        "no_external_action": True,
    }


def independent_capability_check(world: World, caps: tuple[Capability, ...]) -> dict:
    """Truth oracle separately checks each requirement, after the inquiry."""
    for cap in caps:
        if any(world.value(l.variable) != l.equals for l in cap.prerequisites):
            raise AssertionError("False capability certificate " + cap.name)
    return {
        "verified": [c.name for c in caps],
        "verified_reward": sum(c.reward for c in caps),
        "method": "DIRECT_SIMULATOR_FACT_CHECK_NOT_EXTERNAL_VERIFICATION",
    }


class Planner:
    def __init__(self, task: Task):
        validate(task)
        self.task = task
        variables = task.instrument.sensor_variables
        if len(variables) > 7:
            raise ValueError("Finite model bound: 7 binary variables max")
        self.worlds = tuple(World(variables, bits)
                            for bits in product((0, 1), repeat=len(variables)))
        self.root = tuple(range(len(self.worlds)))
        self.direct = candidates(task, False)
        self.forge = candidates(task, True)

    def _answer(self, world_id: int, query: Query) -> int:
        w = self.worlds[world_id]
        if query.kind == "DIRECT":
            return w.value(query.tests[0].variable)
        return int(all(w.value(l.variable) == l.equals for l in query.tests))

    @lru_cache(maxsize=None)
    def branches(self, belief: tuple[int, ...], query: Query
                 ) -> tuple[tuple[int, tuple[int, ...]], ...]:
        partition: dict[int, list[int]] = {}
        for idx in belief:
            partition.setdefault(self._answer(idx, query), []).append(idx)
        return tuple((ans, tuple(indices)) for ans, indices in sorted(partition.items()))

    def certified(self, belief: tuple[int, ...]) -> tuple[Capability, ...]:
        return tuple(
            cap for cap in self.task.capabilities
            if belief and all(
                all(self.worlds[i].value(l.variable) == l.equals
                    for l in cap.prerequisites)
                for i in belief
            )
        )

    def value(self, belief: tuple[int, ...]) -> int:
        return sum(cap.reward for cap in self.certified(belief))

    def available(self, belief: tuple[int, ...], remaining: int,
                  *, synthesize: bool) -> tuple[Query, ...]:
        source = self.forge if synthesize else self.direct
        return tuple(q for q in source
                     if q.cost <= remaining
                     and len(self.branches(belief, q)) > 1)

    @lru_cache(maxsize=None)
    def bellman(self, belief: tuple[int, ...],
                remaining: int, synthesize: bool,
                max_depth: int) -> float:
        """Classical exhaustive expected-value dynamic programming.

        max_depth=-1 = full horizon; positive max_depth bounds how many
        additional questions the planner anticipates.
        """
        incumbent = float(self.value(belief))
        if remaining <= 0 or max_depth == 0:
            return incumbent
        for q in self.available(belief, remaining, synthesize=synthesize):
            future = sum(
                len(part)/len(belief) *
                self.bellman(part, remaining-q.cost, synthesize,
                             max_depth if max_depth == -1 else max_depth-1)
                for _, part in self.branches(belief, q)
            )
            incumbent = max(incumbent, future)
        return incumbent

    def choose(self, belief: tuple[int, ...], remaining: int,
               policy: str) -> dict:
        if policy not in POLICIES:
            raise ValueError("Unknown question-selection policy")
        synthesize = not policy.startswith("DIRECT_")
        options = self.available(belief, remaining, synthesize=synthesize)
        ranked = []
        for q in options:
            branches = self.branches(belief, q)
            entropy = -sum((len(group)/len(belief)) *
                           log2(len(group)/len(belief)) for _, group in branches)
            depth = (
                -1 if policy.endswith("OPTIMAL")
                else 2 if policy == "FOUNDRY_LOOKAHEAD2"
                else 1
            )
            expected = sum(
                len(group)/len(belief) * self.bellman(
                    group, remaining-q.cost, synthesize,
                    depth if depth == -1 else depth-1)
                for _, group in branches
            )
            score = (
                entropy/q.cost if policy.endswith("ENTROPY")
                else expected
            )
            ranked.append((score, q, expected, entropy))
        if not ranked:
            return {"status": "HOLD_NO_VALID_INFORMATIVE_QUERY",
                    "query": None, "proposals": []}
        ranked.sort(key=lambda row: (-row[0], row[1].key))
        top = ranked[0]
        proposals = [
            {
                "query": q.key, "operator": q.kind, "cost": q.cost,
                "derivation_from_capabilities": list(q.derived_from),
                "instrument_source": q.operator_source,
                "expected_lookahead_value": round(expected, 6),
                "entropy_bits": round(entropy, 6),
                "score": round(score, 6),
                "sensor_verified": verify_instrument(self.task, q),
            }
            for score, q, expected, entropy in ranked
        ]
        return {
            "status": "SYNTHESIZED_QUESTION_PROPOSAL" if top[1].kind == "PAIR_MATCH"
                      else "DIRECT_QUESTION_PROPOSAL",
            "query": top[1],
            "public_hypotheses_remaining": len(belief),
            "policy": policy,
            "proposals": proposals,
            "no_target_world_consulted": True,
        }


def run_episode(planner: Planner, target: World, policy: str) -> dict:
    if target not in planner.worlds:
        return {"status": "HOLD_OUTSIDE_DECLARED_MODEL",
                "verified_capabilities": [], "verified_reward": 0,
                "no_external_action": True}
    remaining = planner.task.budget
    belief = planner.root
    receipts = []
    spent = 0
    while remaining > 0:
        proposal = planner.choose(belief, remaining, policy)
        q = proposal["query"]
        if q is None:
            break
        # The target is consulted only AFTER a provenance-verified selection.
        measurement = observation(planner.task, q, target)
        if measurement["status"] != "SYNTHETIC_MEASUREMENT_RECEIPT":
            return {"status": measurement["status"], "verified_reward": 0,
                    "no_external_action": True}
        partitions = dict(planner.branches(belief, q))
        answer = measurement["response"]
        before = len(belief)
        belief = partitions[answer]
        remaining -= q.cost
        spent += q.cost
        checked = independent_capability_check(target, planner.certified(belief))
        receipts.append({
            "query": q.key,
            "operator": q.kind,
            "question_invented_from_goal": q.kind == "PAIR_MATCH",
            "derived_from": list(q.derived_from),
            "instrument_provenance": measurement["source"],
            "cost": q.cost, "result": answer,
            "belief_count_before": before,
            "belief_count_after": len(belief),
            "verified_capabilities_so_far": checked["verified"],
            "verified_reward_so_far": checked["verified_reward"],
            "hypothetical_branches_were_not_taken_as_observations": True,
        })
    final = independent_capability_check(target, planner.certified(belief))
    return {
        "status": "EXACT_FINITE_SIMULATOR_RECEIPT",
        "policy": policy,
        "task": planner.task.name,
        "verified_capabilities": final["verified"],
        "verified_reward": final["verified_reward"],
        "total_measurement_cost": spent,
        "budget_remaining": remaining,
        "remaining_hypotheses": len(belief),
        "synthesized_question_count": sum(
            e["question_invented_from_goal"] for e in receipts),
        "trace": receipts,
        "no_external_action": True,
    }
