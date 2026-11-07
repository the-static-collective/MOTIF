"""MOTIF SELF-MIRROR-001: bounded, auditable policy self-revision (synthetic).

This experiment does not alter an operating agent. It inspects the choice policy
used to rank MOTIF-003-shaped hypothetical action rows, proposes weight edits
from training failures, and tests them against untouched simulated cases.
No causal identification, cross-world proof, autonomous deployment, or human
permission is inferred from synthetic accuracy or an FIR warrant.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from random import Random
from typing import Iterable
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mathal001"))
from mathal import Program, Step, execute, mark
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fir001"))
from fir import Claim, FIRWorld, Warrant

CARRIER = "MOTIF-003 synthetic policy selection"
DECODER = "read-only choices plus independently supplied simulated outcomes"


@dataclass(frozen=True)
class Move:
    name: str
    immediate: int
    affordances: int
    reach: int
    truncated: bool = False

    def __post_init__(self):
        if not self.name or self.affordances < 0 or self.reach < 0:
            raise ValueError("invalid bounded candidate")


@dataclass(frozen=True)
class Case:
    key: str
    moves: tuple[Move, ...]
    rewards: tuple[int, ...]  # simulation's outcomes, NOT input to the policy
    regime: str

    def __post_init__(self):
        if not self.key or not self.moves or len(self.moves) != len(self.rewards):
            raise ValueError("case requires one independent outcome per candidate")
        if len({m.name for m in self.moves}) != len(self.moves):
            raise ValueError("candidate identities must be unique")


@dataclass(frozen=True)
class Policy:
    frontier_weight: int = 0
    reach_weight: int = 0

    def __post_init__(self):
        if not (0 <= self.frontier_weight <= 6 and 0 <= self.reach_weight <= 2):
            raise ValueError("policy outside frozen hypothesis grammar")

    def score(self, move: Move) -> int:
        return (move.immediate + self.frontier_weight * move.affordances
                + self.reach_weight * move.reach)

    def choose(self, moves: tuple[Move, ...]) -> int:
        if not moves or any(m.truncated for m in moves):
            raise ValueError("incomplete affordance exploration requires HOLD")
        # Stable tie break means observations cannot choose a candidate by row order.
        return min(range(len(moves)), key=lambda i: (-self.score(moves[i]), moves[i].name))

    def signature(self) -> str:
        return f"immediate + {self.frontier_weight}*new_choices + {self.reach_weight}*reach"


@dataclass(frozen=True)
class Measurement:
    cases: int
    mean_reward: float
    mean_regret: float
    optimal_choices: int


def measure(policy: Policy, cases: tuple[Case, ...]) -> Measurement:
    if not cases:
        raise ValueError("empty measurement is not evidence")
    reward = 0
    regret = 0
    optimal = 0
    for case in cases:
        selected = policy.choose(case.moves)
        best = max(case.rewards)
        reward += case.rewards[selected]
        regret += best - case.rewards[selected]
        optimal += case.rewards[selected] == best
    return Measurement(len(cases), reward / len(cases), regret / len(cases), optimal)


def generate_cases(split: str, size: int, regime: str = "iid") -> tuple[Case, ...]:
    """Independent deterministic fixture. Seeds are split-specific, never tuned."""
    if split not in {"train", "validation", "test", "ood"}:
        raise ValueError("undeclared dataset split")
    if size < 1 or regime not in {"iid", "shift"} or (regime == "shift" and split != "ood"):
        raise ValueError("invalid experiment split")
    seed = int.from_bytes(sha256(f"selfmirror001|{split}|{regime}|v1".encode()).digest()[:8], "big")
    rng = Random(seed)
    out = []
    for idx in range(size):
        moves = []
        outcomes = []
        for action in ("A", "B", "C", "D"):
            immediate = rng.randint(0, 15)
            afford = rng.randint(0, 5)
            reach = rng.randint(1, 8)
            noise = rng.randint(-2, 2)
            # In IID tasks an enabled option is valuable. In OOD tasks it is
            # a trap: this tests extrapolation, not a universal moral objective.
            weight = 3 if regime == "iid" else -4
            value = immediate + weight * afford + reach + noise
            moves.append(Move(action, immediate, afford, reach))
            outcomes.append(value)
        out.append(Case(f"{split}-{idx:03d}", tuple(moves), tuple(outcomes), regime))
    return tuple(out)


def dataset_digest(cases: tuple[Case, ...]) -> str:
    data = [(c.key, c.regime,
             [(m.name, m.immediate, m.affordances, m.reach, m.truncated)
              for m in c.moves], c.rewards) for c in cases]
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return sha256(raw).hexdigest()[:16]


def failures(incumbent: Policy, training: tuple[Case, ...]) -> tuple[dict, ...]:
    """Error receipts: contrasts are observed in training, not predicted causes."""
    observations = []
    for case in training:
        selected = incumbent.choose(case.moves)
        best = min(range(len(case.moves)),
                   key=lambda i: (-case.rewards[i], case.moves[i].name))
        if case.rewards[best] > case.rewards[selected]:
            actual, chosen = case.moves[best], case.moves[selected]
            observations.append({
                "case": case.key, "regret": case.rewards[best] - case.rewards[selected],
                "chosen": chosen.name, "better": actual.name,
                "delta_new_choices": actual.affordances - chosen.affordances,
                "delta_reach": actual.reach - chosen.reach,
                "reason": "counterexample to choice optimality under observed synthetic rewards",
            })
    return tuple(observations)


@dataclass(frozen=True)
class Revision:
    before: Policy
    after: Policy
    reason: str
    source_signature: str
    target_signature: str
    source_receipt: tuple[dict, ...]
    fir_status: str


def propose_revisions(incumbent: Policy, training: tuple[Case, ...],
                      budget: int = 12) -> tuple[Revision, ...]:
    """Diagnose wrong training choices; propose bounded edits from contrast signs.

    The grammar is frozen in code. No language model invents a new operator.
    Validation and holdouts are *not accepted inputs* to this function.
    """
    if budget < 1:
        raise ValueError("candidate budget must be positive")
    misses = failures(incumbent, training)
    frontier_signal = sum(x["regret"] * x["delta_new_choices"] for x in misses)
    reach_signal = sum(x["regret"] * x["delta_reach"] for x in misses)
    if not misses or frontier_signal <= 0 and reach_signal <= 0:
        return ()
    new_frontiers = [v for v in (1, 2, 3, 4, 5, 6)
                     if v != incumbent.frontier_weight] if frontier_signal > 0 else []
    new_reaches = [v for v in (1, 2)
                   if v != incumbent.reach_weight] if reach_signal > 0 else []
    targets = []
    # Mechanism: differential diagnosis -> single-feature edits -> interactions.
    targets += [Policy(v, incumbent.reach_weight) for v in new_frontiers]
    targets += [Policy(incumbent.frontier_weight, v) for v in new_reaches]
    targets += [Policy(f, r) for f in new_frontiers for r in new_reaches]
    # Preserve distinct proposal receipts even where end weights coincide.
    revisions = []
    for target in dict.fromkeys(targets):
        if len(revisions) >= budget:
            break
        claim = Claim(f"Explore policy {target.signature()}",
                      scope="synthetic training-derived hypothesis")
        run = execute(FIRWorld(CARRIER, DECODER), Program(
            name="propose-policy-revision", carrier=CARRIER, decoder=DECODER,
            steps=(Step("propose", claim),)))
        if not run.applied or claim not in run.world.ideas or claim in run.world.facts:
            raise AssertionError("candidate bypassed FIR proposal gate")
        revisions.append(Revision(incumbent, target,
            f"training failures={len(misses)}; frontier_contrast={frontier_signal}; reach_contrast={reach_signal}",
            incumbent.signature(), target.signature(),
            tuple(run.receipts) + ({"op": "diagnose", "training_digest": dataset_digest(training),
                                     "examples": tuple(misses[:3])},),
            "I"))
    return tuple(revisions)


@dataclass(frozen=True)
class Selection:
    policy: Policy
    status: str
    validation_before: Measurement
    validation_after: Measurement
    inspected_proposals: int


def choose_on_validation(incumbent: Policy, proposals: tuple[Revision, ...],
                         validation: tuple[Case, ...]) -> Selection:
    """Selection uses validation outcomes, not held-out outcomes."""
    original = measure(incumbent, validation)
    best, best_result = incumbent, original
    for proposed in proposals:
        if proposed.before != incumbent or proposed.fir_status != "I":
            raise ValueError("foreign or pre-admitted proposal")
        result = measure(proposed.after, validation)
        if result.mean_regret < best_result.mean_regret - 1e-12:
            best, best_result = proposed.after, result
    return Selection(best, "PROPOSED_VALIDATION_WIN" if best != incumbent else "HOLD_NO_VALIDATION_GAIN",
                     original, best_result, len(proposals))


def grid_control(incumbent: Policy, validation: tuple[Case, ...],
                 budget: int | None = None) -> Selection:
    """Strong classical exhaustive benchmark, optionally budget-matched.

    This is the *same frozen 2D linear grammar*. It may beat the revision agent.
    """
    grid = [Policy(f, r) for f in range(7) for r in range(3)]
    grid.remove(incumbent)
    if budget is not None:
        grid = grid[:budget]
    # These proposals are classical enumeration, not manufactured FIR claims.
    original = measure(incumbent, validation)
    best = incumbent
    best_result = original
    for policy in grid:
        result = measure(policy, validation)
        if result.mean_regret < best_result.mean_regret - 1e-12:
            best, best_result = policy, result
    return Selection(best, "CLASSICAL_GRID_COMPARISON", original, best_result, len(grid))


def preview_motif003(rows: list[dict], policy: Policy) -> dict:
    """Use real MOTIF-003 action-row shape, WITHOUT claiming any observed payoff."""
    def name(row):
        return str(row["operator"]) + ":" + repr(tuple(row["roles"]))
    moves = tuple(Move(name(row), int(row["immediate_delta"]),
                       len(row["new_affordances"]), int(row["reachable_after_first_move"]),
                       bool(row.get("truncated", False))) for row in rows)
    if any(m.truncated for m in moves):
        return {"status": "HOLD_INCOMPLETE_FRONTIER", "admitted_fact": False,
                "selection": None, "evidence": "simulation-only"}
    index = policy.choose(moves) if moves else None
    return {"status": "I", "admitted_fact": False,
            "selection": None if index is None else moves[index].name,
            "evidence": "MOTIF-003 counterfactual preview only"}


@dataclass(frozen=True)
class Audit:
    selection: Selection
    narrow_test_claim: str
    narrow_test_role: str
    test_before: Measurement
    test_after: Measurement
    ood_before: Measurement
    ood_after: Measurement
    generalization_status: str
    receipts: tuple[dict, ...]


def audit_frozen(incumbent: Policy, selection: Selection, iid_test: tuple[Case,...],
                 ood: tuple[Case,...]) -> Audit:
    """Read the two held-out sets once; never use them to select or retune weights."""
    base_test = measure(incumbent, iid_test)
    choice_test = measure(selection.policy, iid_test)
    base_ood = measure(incumbent, ood)
    choice_ood = measure(selection.policy, ood)
    scope = "test:" + dataset_digest(iid_test)
    claim = Claim("Policy candidate improves mean regret over incumbent on exactly this finite test fixture",scope)
    world = FIRWorld(CARRIER, DECODER)
    proposed = execute(world, Program("held-out claim", (Step("propose", claim),),
                                     CARRIER, DECODER))
    if not proposed.applied:
        raise AssertionError("failed to propose local claim")
    receipts = list(proposed.receipts)
    role = "I"
    if (selection.status == "PROPOSED_VALIDATION_WIN" and
        choice_test.mean_regret < base_test.mean_regret - 1e-12):
        receipt = ("recomputed exact finite synthetic rewards "+scope+
                   "; baseline="+str(base_test.mean_regret)+
                   "; candidate="+str(choice_test.mean_regret))
        narrowed = execute(proposed.world, Program("finite only",(
            Step("admit", claim, Warrant("finite_computation",receipt,scope)),),
            CARRIER, DECODER))
        if not narrowed.applied or claim not in narrowed.world.facts:
            raise AssertionError("failed to record narrow test-only admission")
        receipts.extend(narrowed.receipts)
        role = "F_LOCAL"
    # An OOD failure refuses UNIVERSAL promotion even when finite test beats incumbent.
    if choice_ood.mean_regret > base_ood.mean_regret + 1e-12:
        status = "HOLD_OOD_REGRESSION"
        receipts.append({"operation":"refuse", "claim":"universal policy improvement",
                         "reason":"synthetic OOD regret increases", "scope":"shift:"+dataset_digest(ood)})
    else:
        status = "HOLD_UNPROVEN_GENERALIZATION"
        receipts.append({"operation":"refuse", "claim":"universal policy improvement",
                         "reason":"finite synthetic controls cannot establish generality"})
    return Audit(selection,claim.text,role,base_test,choice_test,base_ood,choice_ood,
                 status,tuple(receipts))


def demonstration() -> dict:
    train=generate_cases("train", 60)
    validation=generate_cases("validation", 40)
    iid_test=generate_cases("test", 80)
    ood=generate_cases("ood", 80, "shift")
    baseline = Policy()
    error_log = failures(baseline,train)
    proposals = propose_revisions(baseline,train)
    selection = choose_on_validation(baseline,proposals,validation)
    audit = audit_frozen(baseline,selection,iid_test,ood)
    grid = grid_control(baseline,validation)
    matched = grid_control(baseline,validation, budget=len(proposals))
    return {
        "experiment":"MOTIF SELF-MIRROR-001", "scope":"synthetic policy revision only",
        "split_digests":{k:dataset_digest(v) for k,v in
            (("train",train),("validation",validation),("test",iid_test),("ood",ood))},
        "training_failures":len(error_log), "proposed_policy_mathals":len(proposals),
        "incumbent":baseline.signature(),"candidate":selection.policy.signature(),
        "validation_regret":{"before":selection.validation_before.mean_regret,
                             "after":selection.validation_after.mean_regret},
        "iid_holdout_regret":{"before":audit.test_before.mean_regret,
                              "after":audit.test_after.mean_regret},
        "ood_shift_regret":{"before":audit.ood_before.mean_regret,
                            "after":audit.ood_after.mean_regret},
        "finite_test_claim":audit.narrow_test_role,
        "generalization_status":audit.generalization_status,
        "classical_grid_validation_regret":grid.validation_after.mean_regret,
        "classical_grid_matched_validation_regret":matched.validation_after.mean_regret,
        "classical_grid_search_budget":grid.inspected_proposals,
        "revision_search_budget":len(proposals),
        "external_actions":0, "runtime_policy_changed":False,
        "claims":"No general autonomous improvement or mechanism discovery demonstrated",
    }


if __name__ == "__main__":
    print(json.dumps(demonstration(),indent=2,sort_keys=True))
