"""MOTIF-020F: The Inside-Out Box — classical counterfactual scheduling.

Unlike a cost-of-computation-only question selector, this asks:
  "If we WAIT one tick, which useful futures cease to be available?"

All deadlines, values and probabilities are independently supplied synthetic
assumptions; none is inferred from planZ's INDEX_ONLY feed. WAIT is a first-
class transition. The objective never authorizes external or field actions.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from functools import lru_cache
from itertools import combinations
from math import isfinite
from typing import Mapping, Sequence

from planz import ReadonlySnapshot


@dataclass(frozen=True)
class CounterfactualOpportunity:
    plan_id: str
    reward_if_successful: float
    last_start_tick: int
    probability: float = 1.0
    value_decay_per_tick: float = 0.0
    effort_cost: float = 0.0
    attention_units: int = 1
    actor_effects: tuple[tuple[str, float], ...] = ()
    assumed_clearance: str = "HYPOTHETICAL_APPROVAL_NOT_REAL_PERMISSION"
    provenance: str = "SYNTHETIC_USER_DECLARED_HYPOTHESIS"

    def __post_init__(self):
        numbers = (self.reward_if_successful, self.probability,
                   self.value_decay_per_tick, self.effort_cost)
        if (not self.plan_id or not all(isfinite(x) for x in numbers)
                or self.reward_if_successful < 0
                or not (0 <= self.probability <= 1)
                or self.value_decay_per_tick < 0 or self.effort_cost < 0
                or not 0 <= self.last_start_tick <= 12
                or not 1 <= self.attention_units <= 10
                or self.assumed_clearance != "HYPOTHETICAL_APPROVAL_NOT_REAL_PERMISSION"
                or self.provenance != "SYNTHETIC_USER_DECLARED_HYPOTHESIS"
                or len({name for name, _ in self.actor_effects}) != len(self.actor_effects)
                or any(not name or not isfinite(amount) for name, amount in self.actor_effects)):
            raise ValueError("HOLD_INVALID_EXPLICIT_SYNTHETIC_ASSUMPTION")

    def expected_net(self, tick: int) -> float:
        if tick > self.last_start_tick:
            return float("-inf")
        return (self.probability *
                max(0., self.reward_if_successful - self.value_decay_per_tick*tick)
                - self.effort_cost)


@dataclass(frozen=True)
class ScheduledBatch:
    tick: int
    plans: tuple[str, ...]
    modeled_net_gain: float


@dataclass(frozen=True)
class OmissionReceipt:
    status: str
    edition: str
    source_git_blob: str
    assumed_world: str
    first_batch: tuple[str, ...]
    optimal_modeled_value: float
    one_tick_wait_modeled_value: float
    cost_of_waiting_one_tick: float
    cost_of_deliberation_one_tick: float
    foregone_by_permanent_omission: tuple[tuple[str, float], ...]
    plans_expiring_if_wait: tuple[str, ...]
    sequence: tuple[ScheduledBatch, ...]
    per_actor_first_batch_effect: tuple[tuple[str, float], ...]
    baseline_myopic_value: float
    model_name: str = "FINITE_HORIZON_CLASSICAL_DP"
    simulation_only: bool = True
    external_execution_allowed: bool = False
    real_deadlines_verified: bool = False
    real_costs_verified: bool = False


@dataclass(frozen=True)
class _Value:
    utility: float
    policy: tuple[ScheduledBatch, ...]


class InsideOutBox:
    """Finite DP chooses ACT/PORTFOLIO/WAIT; omission is evaluated explicitly.

    Equal-time, one-tick synthetic tasks with costed attention capacity. The
    optimal comparator is classical dynamic programming, so the method cannot
    claim to exceed an informed classical optimum on the same assumptions.
    """

    def __init__(
        self,
        snapshot: ReadonlySnapshot,
        opportunities: Sequence[CounterfactualOpportunity],
        *,
        horizon: int = 3,
        attention_budget: int = 2,
        max_parallel: int = 1,
        cognition_cost_per_tick: float = 0.05,
    ):
        if (not 1 <= horizon <= 8 or not 0 <= attention_budget <= 10
                or not 1 <= max_parallel <= 3 or len(opportunities) > 9
                or not isfinite(cognition_cost_per_tick) or cognition_cost_per_tick < 0):
            raise ValueError("HOLD_BOUND_SEARCH_OR_INVALID_COMPUTE_COST")
        if len({x.plan_id for x in opportunities}) != len(opportunities):
            raise ValueError("HOLD_DUPLICATE_PLAN_ASSUMPTION")
        for candidate in opportunities:
            source = snapshot.get(candidate.plan_id)
            if (source.execution_allowed or source.field_outcome != "NOT_VERIFIED"
                    or source.third_party_approval != "NOT_ESTABLISHED"):
                raise ValueError("HOLD_PLANZ_SOURCE_AUTHORITY_DRIFT")
        self.snapshot = snapshot
        self.opportunities = tuple(sorted(opportunities, key=lambda x: x.plan_id))
        self.horizon = horizon
        self.attention_budget = attention_budget
        self.max_parallel = max_parallel
        self.cognition_cost_per_tick = cognition_cost_per_tick

    @staticmethod
    def _actor_held(candidate: CounterfactualOpportunity) -> bool:
        # Do not aggregate away an unconsented negative actor-level effect.
        return any(v < 0 for _, v in candidate.actor_effects)

    def _value(self, start_tick: int = 0, *, excluded: frozenset[str] = frozenset(),
               max_parallel: int | None = None) -> _Value:
        opportunities = self.opportunities
        horizon = self.horizon
        width = self.max_parallel if max_parallel is None else max_parallel
        if not 1 <= width <= 3:
            raise ValueError("HOLD_UNSUPPORTED_PARALLELISM")

        @lru_cache(maxsize=None)
        def solve(tick: int, completed: tuple[str, ...], remaining: int) -> _Value:
            if tick >= horizon:
                return _Value(0.0, ())
            waited = solve(tick + 1, completed, remaining)
            # WAIT is an actual choice; "do nothing" has consequences for later
            # availability without being assigned an invented fee or permission.
            best = _Value(waited.utility, (
                ScheduledBatch(tick, (), 0.0), *waited.policy,
            ))
            already = set(completed)
            eligible = [
                x for x in opportunities
                if x.plan_id not in excluded and x.plan_id not in already
                and x.last_start_tick >= tick and x.attention_units <= remaining
                and not self._actor_held(x)
                and x.expected_net(tick) >= 0
            ]
            for size in range(1, min(len(eligible), width) + 1):
                for group in combinations(eligible, size):
                    effort = sum(x.attention_units for x in group)
                    if effort > remaining:
                        continue
                    selected = tuple(x.plan_id for x in group)
                    gain = sum(x.expected_net(tick) for x in group)
                    next_done = tuple(sorted((*completed, *selected)))
                    future = solve(tick + 1, next_done, remaining - effort)
                    total = gain + future.utility
                    # A zero-or-negligible benefit is not a reason to act.
                    if total > best.utility + 1e-10:
                        best = _Value(total, (
                            ScheduledBatch(tick, selected, round(gain, 8)),
                            *future.policy,
                        ))
            return best

        return solve(start_tick, (), self.attention_budget)

    def _greedy(self) -> float:
        # Stronger than "act once": greedy replans each tick, but disregards
        # future opportunity loss when choosing the current batch.
        budget = self.attention_budget
        completed: set[str] = set()
        value = 0.
        for tick in range(self.horizon):
            ready = [
                x for x in self.opportunities
                if x.plan_id not in completed and x.last_start_tick >= tick
                and x.attention_units <= budget and not self._actor_held(x)
                and x.expected_net(tick) >= 0
            ]
            choice = ()
            high = 0.
            for n in range(1, min(len(ready), self.max_parallel) + 1):
                for batch in combinations(ready, n):
                    if sum(x.attention_units for x in batch) > budget:
                        continue
                    gain = sum(x.expected_net(tick) for x in batch)
                    if gain > high + 1e-10:
                        high, choice = gain, batch
            for x in choice:
                budget -= x.attention_units
                completed.add(x.plan_id)
            value += high
        return value

    def analyze(self) -> OmissionReceipt:
        optimal = self._value()
        forced_wait = self._value(start_tick=1)  # same exact model, one tick late
        delay_loss = max(0.0, optimal.utility - forced_wait.utility)
        omit = tuple(
            (x.plan_id, round(max(0., optimal.utility -
                                  self._value(excluded=frozenset((x.plan_id,))).utility), 8))
            for x in self.opportunities
        )
        soon_lost = tuple(
            x.plan_id for x in self.opportunities
            if x.last_start_tick == 0 and x.expected_net(0) > 0
            and x.attention_units <= self.attention_budget
            and not self._actor_held(x)
        )
        # "Now" is tick zero. Never label a future scheduled action as the
        # immediate recommendation when the optimal policy first chooses WAIT.
        first_batch = (optimal.policy[0].plans if optimal.policy
                       and optimal.policy[0].tick == 0 else ())
        first_effects: dict[str, float] = {}
        for x in self.opportunities:
            if x.plan_id in first_batch:
                for actor, value in x.actor_effects:
                    first_effects[actor] = first_effects.get(actor, 0.) + value
        return OmissionReceipt(
            status="COUNTERFACTUAL_REVIEW_ONLY" if self.opportunities else "HOLD_NO_TEMPORAL_ASSUMPTIONS",
            edition=self.snapshot.edition,
            source_git_blob=self.snapshot.git_blob,
            assumed_world="DECLARED_SYNTHETIC_SCENARIO_NOT_PLANZ_FACTS",
            first_batch=first_batch,
            optimal_modeled_value=round(optimal.utility, 8),
            one_tick_wait_modeled_value=round(forced_wait.utility, 8),
            cost_of_waiting_one_tick=round(delay_loss, 8),
            # Deliberation consumes time AND a small direct compute cost;
            # opportunity cost often dwarfs the cost of computation.
            cost_of_deliberation_one_tick=round(delay_loss + self.cognition_cost_per_tick, 8),
            foregone_by_permanent_omission=omit,
            plans_expiring_if_wait=soon_lost,
            sequence=optimal.policy,
            per_actor_first_batch_effect=tuple(sorted(first_effects.items())),
            baseline_myopic_value=round(self._greedy(), 8),
        )


def scope_only(snapshot: ReadonlySnapshot) -> dict:
    """Real planZ pointers contain NO verified benefit, deadline or permission."""
    return {
        "status": "HOLD_NO_VERIFIED_INACTION_VALUATION",
        "edition": snapshot.edition,
        "raw_public_plan_count": len(snapshot.plans),
        "source_authority": snapshot.authority,
        "all_external_actions_blocked": all(not x.execution_allowed for x in snapshot.plans),
        "temporal_fact": snapshot.temporal_fact,
        "next_step": "Ask a source owner to declare actual deadline, consequences, costs, and permissions; no outside action.",
    }
