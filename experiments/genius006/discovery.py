"""MOTIF GENIUS-006 — The Discovery Dividend.

A *finite model-based* active research toy with proof-carrying hypothetical
capabilities, gated successor questions and strong classical comparators.

Questions disclose only the chosen observation in the secret world; planners
may inspect a PUBLIC finite hypothesis grammar, not the hidden answer.
All algorithms are conventional finite enumeration / Bellman planning.
No historically new mathematics, autonomous question-language invention,
real-world action, Trench/MCP integration or general AI advancement claimed.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import log2
from typing import Any

FIELDS = ("a", "b", "c", "d", "noise_x", "noise_y")
POLICIES = ("ENTROPY", "DIVERSITY", "MYOPIC_GAIN", "AFFORDANCE_2", "EXACT_BELLMAN")


@dataclass(frozen=True)
class World:
    fields: tuple[int, int, int, int, int, int]

    def get(self, key: str) -> int:
        return self.fields[FIELDS.index(key)]


@dataclass(frozen=True)
class Question:
    name: str
    reveals: str
    requires: tuple[tuple[str, int], ...] = ()
    cost: int = 1


@dataclass(frozen=True)
class Capability:
    name: str
    requires: tuple[tuple[str, int], ...]
    value: int


@dataclass(frozen=True)
class Task:
    name: str
    questions: tuple[Question, ...]
    capabilities: tuple[Capability, ...]
    budget: int = 3


def sample_space() -> tuple[World, ...]:
    # 16 Boolean contexts x 4 x 4 irrelevant/relevant 2-bit fields.
    # The finite hypothesis model is public, but the target world is not.
    return tuple(World(tuple(x)) for x in product(
        (0, 1), (0, 1), (0, 1), (0, 1), range(4), range(4)))


def scenario(name: str) -> Task:
    questions = (
        Question("inspect_a", "a"),
        Question("confirm_b", "b"),
        Question("inspect_c", "c", (("b", 1),)),
        Question("verify_d", "d", (("b", 1), ("c", 1))),
        Question("survey_noise_x", "noise_x"),
        Question("survey_noise_y", "noise_y"),
    )
    if name == "CHAIN":
        caps = (
            Capability("foundational_a", (("a", 1),), 1),
            Capability("access", (("b", 1), ("c", 1)), 4),
            Capability("new_service", (("b", 1), ("c", 1), ("d", 1)), 7),
            Capability("support_a_b", (("a", 1), ("b", 1)), 2),
        )
    elif name == "PARALLEL":
        caps = (
            Capability("support_a", (("a", 1),), 3),
            Capability("support_b", (("b", 1),), 3),
            Capability("joint_a_b", (("a", 1), ("b", 1)), 5),
            Capability("joint_a_c", (("a", 1), ("b", 1), ("c", 1)), 5),
        )
    elif name == "NOISE_USEFUL":
        caps = (
            Capability("calibration_x", (("noise_x", 3),), 7),
            Capability("calibration_y", (("noise_y", 2),), 7),
            Capability("simple_a", (("a", 1),), 1),
            Capability("simple_b", (("b", 1),), 1),
        )
    elif name == "SPARSE":
        caps = (
            Capability("rare_service", (("b", 1), ("c", 1), ("d", 1)), 9),
            Capability("recovery_a", (("a", 1),), 1),
        )
    elif name == "MIXED":
        caps = (
            Capability("access", (("b", 1), ("c", 1)), 4),
            Capability("calibration_x", (("noise_x", 3),), 3),
            Capability("repair_a", (("a", 1),), 2),
            Capability("rare_a_d", (("a", 1), ("b", 1), ("c", 1), ("d", 1)), 5),
        )
    else:
        raise ValueError("Unknown task family")
    return Task(name=name, questions=questions, capabilities=caps)


def validate(task: Task) -> None:
    if task.budget < 0 or task.budget > 5:
        raise ValueError("Budget outside finite contract")
    qnames = [q.name for q in task.questions]
    cnames = [c.name for c in task.capabilities]
    if len(set(qnames)) != len(qnames) or len(set(cnames)) != len(cnames):
        raise ValueError("No duplicate question or capability ids")
    for q in task.questions:
        if q.reveals not in FIELDS or q.cost != 1 or not q.name:
            raise ValueError("Typed, unit-cost finite questions only")
        if any(k not in FIELDS for k, _ in q.requires):
            raise ValueError("Unknown gating fact")
    for cap in task.capabilities:
        if cap.value < 0 or any(k not in FIELDS for k, _ in cap.requires):
            raise ValueError("Invalid capability contract")
        if not cap.requires:
            raise ValueError("No free capabilities in this test")


class Planner:
    def __init__(self, task: Task):
        validate(task)
        self.task = task
        self.worlds = sample_space()
        self.root = tuple(range(len(self.worlds)))
        self.questions = {q.name: q for q in task.questions}
        self._query_count = 0

    def certifies(self, belief: tuple[int, ...],
                  required: tuple[tuple[str, int], ...]) -> bool:
        return bool(belief) and all(
            all(self.worlds[i].get(k) == val for k, val in required)
            for i in belief
        )

    def certified(self, belief: tuple[int, ...]) -> tuple[Capability, ...]:
        return tuple(cap for cap in self.task.capabilities
                     if self.certifies(belief, cap.requires))

    def value(self, belief: tuple[int, ...]) -> int:
        return sum(c.value for c in self.certified(belief))

    def available(self, belief: tuple[int, ...],
                  asked: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(q.name for q in self.task.questions
                     if q.name not in asked and
                     self.certifies(belief, q.requires))

    @lru_cache(maxsize=None)
    def partitions(self, belief: tuple[int, ...], qname: str
                   ) -> tuple[tuple[int, tuple[int, ...]], ...]:
        q = self.questions[qname]
        out: dict[int, list[int]] = {}
        for i in belief:
            out.setdefault(self.worlds[i].get(q.reveals), []).append(i)
        return tuple((answer, tuple(indices)) for answer, indices in sorted(out.items()))

    @lru_cache(maxsize=None)
    def exact_value(self, belief: tuple[int, ...],
                    asked: tuple[str, ...], remaining: int) -> float:
        """Bellman optimal expected *terminal* capability reward.

        Strong exact classical comparator, finite known hypothesis space.
        It cannot access the secret world; it averages over ALL possible
        observations of available questions.
        """
        base = self.value(belief)
        if remaining <= 0:
            return float(base)
        best = float(base)
        for q in self.available(belief, asked):
            branches = self.partitions(belief, q)
            if len(branches) <= 1:
                continue
            extended = tuple(sorted(asked + (q,)))
            v = sum(len(part) / len(belief) *
                    self.exact_value(part, extended, remaining-1)
                    for _, part in branches)
            best = max(best, v)
        return best

    @lru_cache(maxsize=None)
    def expected_at_depth(self, belief: tuple[int, ...],
                          asked: tuple[str, ...], depth: int) -> float:
        """Classical finite lookahead surrogate, only 1 or 2 steps."""
        if depth <= 0:
            return float(self.value(belief))
        return max(
            [float(self.value(belief))] + [
                sum(len(part) / len(belief) *
                    self.expected_at_depth(part, tuple(sorted(asked + (q,))), depth-1)
                    for _, part in branches)
                for q in self.available(belief, asked)
                if len(branches := self.partitions(belief, q)) > 1
            ]
        )

    def choose(self, belief: tuple[int, ...],
               asked: tuple[str, ...], remaining: int,
               policy: str) -> dict:
        """Return only the NEXT question, with all candidate score receipts.

        No prospective branch is treated as an actual observation. Planning
        is a finite expectation over public hypotheses, not hindsight.
        """
        if policy not in POLICIES:
            raise ValueError("Unknown policy")
        if remaining <= 0:
            return {"question": None, "status": "BUDGET_EXHAUSTED", "candidates": []}
        candidates = []
        for qname in self.available(belief, asked):
            branches = self.partitions(belief, qname)
            if len(branches) <= 1:
                continue
            total = len(belief)
            entropy = -sum((len(part)/total) * log2(len(part)/total)
                           for _, part in branches)
            next_asked = tuple(sorted(asked + (qname,)))
            immediate = sum(
                len(part)/total * self.value(part) for _, part in branches)
            lookahead_2 = sum(
                len(part)/total *
                self.expected_at_depth(part, next_asked,
                                       min(1, remaining-1))
                for _, part in branches)
            expected_exact = (
                sum(len(part)/total *
                    self.exact_value(part, next_asked, remaining-1)
                    for _, part in branches)
                if policy == "EXACT_BELLMAN" else None
            )
            scores = {
                "ENTROPY": entropy,
                "DIVERSITY": len(branches),
                "MYOPIC_GAIN": immediate,
                "AFFORDANCE_2": lookahead_2,
                "EXACT_BELLMAN": expected_exact,
            }
            candidates.append({
                "question": qname,
                "public_possible_answers": [answer for answer, _ in branches],
                "possible_outcome_counts": {str(answer): len(part) for answer, part in branches},
                "entropy_bits": round(entropy, 6),
                "expected_immediate_verified_value": round(immediate, 6),
                "expected_two_step_value": round(lookahead_2, 6),
                "selection_score": scores[policy],
            })
        if not candidates:
            return {"question": None, "status": "HOLD_NO_INFORMATIVE_QUESTION",
                    "candidates": []}
        # Canonical stable tie-breaker; never consult the target world's answer.
        order = sorted(candidates, key=lambda c: (-c["selection_score"], c["question"]))
        chosen = order[0]
        return {
            "question": chosen["question"], "status": "NEXT_QUESTION_PROPOSED",
            "objective": policy, "candidates": order,
            "hypotheses_considered": len(belief),
            "already_certified_value": self.value(belief),
        }


def independent_verify(world: World, caps: tuple[Capability, ...]) -> dict:
    """Separate direct-feature validator: refuses unsupported certificates."""
    for cap in caps:
        for k, val in cap.requires:
            if world.get(k) != val:
                raise AssertionError(f"Invalid certificate: {cap.name} requires {k}={val}")
    return {
        "status": "EXACT_FINITE_WITNESS_CHECKED",
        "verified_names": [cap.name for cap in caps],
        "verified_value": sum(cap.value for cap in caps),
        "method": "DIRECT_HIDDEN_WORLD_REQUIREMENT_CHECK",
    }


def episode(planner: Planner, world: World, policy: str) -> dict:
    """Reveal only explicitly asked answers, verify certificates separately."""
    if world not in planner.worlds:
        raise ValueError("Target is outside the declared model; HOLD instead of guessing")
    belief = planner.root
    asked: tuple[str, ...] = ()
    trace = []
    for _ in range(planner.task.budget):
        decision = planner.choose(belief, asked, planner.task.budget-len(asked), policy)
        qname = decision["question"]
        if qname is None:
            break
        query = planner.questions[qname]
        before = len(belief)
        # The only access to the hidden world happens AFTER choosing question.
        answer = world.get(query.reveals)
        branch = dict(planner.partitions(belief, qname))
        belief = branch[answer]
        asked = tuple(sorted(asked + (qname,)))
        proof = independent_verify(world, planner.certified(belief))
        trace.append({
            "question": qname, "answer": answer,
            "source": f"synthetic://{planner.task.name}/{world.fields}/{qname}",
            "candidates_before": before,
            "candidates_after": len(belief),
            "newly_certified": proof["verified_names"],
            "independent_verified_value_after": proof["verified_value"],
            "no_action_executed": True,
        })
    caps = planner.certified(belief)
    verification = independent_verify(world, caps)
    return {
        "task": planner.task.name, "policy": policy,
        "status": "RESEARCH_HOLD_ENGINEER_AUTHORED",
        "question_count": len(trace),
        "verified_capability_count": len(caps),
        "verified_capability_value": verification["verified_value"],
        "certificates": [{
            "capability": c.name, "value": c.value,
            "requirements": list(c.requires),
            "proof": "TRUE_IN_ALL_REMAINING_PUBLIC_HYPOTHESES",
            "separate_world_check": "PASS",
        } for c in caps],
        "remaining_possible_worlds": len(belief),
        "trace": trace,
        "no_real_world_action": True,
    }
