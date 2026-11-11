"""VOID-004: bounded, authored survival-wave maze with repeated attempts.

The user asked for a challenge that can take more/less than ten tries.
This is an engineered deterministic 2D fortress, not an independent game benchmark.
Cognitive policies observe only source-owned receipts; their future "intel slots"
are counterfactual affordances, NOT knowledge of the attack directions.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAP = (
    "###########",
    "#.........#",
    "#..A...B..#",
    "#.........#",
    "#....H....#",
    "#.........#",
    "#..C...D..#",
    "#.........#",
    "###########",
)
HUB = (5, 4)
WAVES = 24
MAX_ATTEMPTS = 14
TARGET_ATTEMPTS = 10
PREP_STEPS = 4
GATES = ("N", "E", "S", "W")
RELAY_COVERAGE = {
    "A": (1, 5, 9), "B": (2, 6, 10),
    "C": (3, 7, 11), "D": (4, 8, 12),
}
POLICIES = ("motif_iterative", "classical_iterative", "classical_immediate", "classical_no_memory")
DEV_SEEDS = (40101, 40103, 40107, 40111)
TEST_SEEDS = tuple(81001 + 17 * i for i in range(24))
STEPS = (("west", (-1, 0)), ("east", (1, 0)), ("north", (0, -1)), ("south", (0, 1)))
POSITIONS = {c: (x, y) for y, row in enumerate(MAP) for x, c in enumerate(row) if c in RELAY_COVERAGE}


def seal(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verified(row):
    return row.get("seal") == seal({k: v for k, v in row.items() if k != "seal"})


def layout(xy):
    x, y = xy
    return MAP[y][x] if 0 <= y < len(MAP) and 0 <= x < len(MAP[0]) else "#"


def public_route(target):
    """Shared classical BFS on the explicitly public map; no hidden attack data."""
    goal = POSITIONS[target]
    paths = {HUB: ()}
    q = deque((HUB,))
    while q:
        here = q.popleft()
        if here == goal:
            return paths[here]
        for action, (dx, dy) in STEPS:
            p = (here[0] + dx, here[1] + dy)
            if p not in paths and layout(p) != "#":
                paths[p] = paths[here] + (action,)
                q.append(p)
    raise RuntimeError("DECLARED_RELAY_UNREACHABLE")


def native003():
    p = HERE.parent / "003" / "affordance.py"
    spec = importlib.util.spec_from_file_location("void004_native_003", p)
    if spec is None or spec.loader is None:
        raise RuntimeError("ORIGINAL_MOTIF_003_NOT_PRESENT")
    import sys
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FortOwner:
    """Actual truth is private; source reports are emitted only on allowed actions."""
    def __init__(self, seed):
        if seed not in DEV_SEEDS + TEST_SEEDS:
            raise ValueError("UNREGISTERED_CHALLENGE_SEED")
        self._lanes = {w: GATES[int(sha256(f"wave:v1:{seed}:{w}".encode()).hexdigest(), 16) % 4]
                       for w in range(1, WAVES + 1)}
        self.seed = seed
        self.attempt = 0
        self.phase = "not_started"
        self.position = HUB
        self.turn = 0
        self.current_wave = 1
        self.sonar_left = 0
        self.relay_used = False
        self.sequence = 0

    def public_view(self):
        return {"map": MAP, "hub": HUB, "relay_coverage": RELAY_COVERAGE,
                "waves": WAVES, "max_attempts": MAX_ATTEMPTS,
                "attempt": self.attempt, "source_epoch": 0}

    def _receipt(self, kind, **kwargs):
        self.sequence += 1
        row = {"source": "AUTHOR_BUILT_FORTRESS_ENGINE", "kind": kind,
               "attempt": self.attempt, "sequence": self.sequence,
               "source_epoch": 0, **kwargs}
        row["seal"] = seal(row)
        return row

    def begin(self):
        if not self.phase in ("not_started", "failed", "cleared"):
            raise RuntimeError("ATTEMPT_ALREADY_RUNNING")
        self.attempt += 1
        if self.attempt > MAX_ATTEMPTS:
            raise RuntimeError("ATTEMPT_BUDGET_EXCEEDED")
        self.phase = "preparation"
        self.position = HUB
        self.turn = 0
        self.current_wave = 1
        self.sonar_left = 1
        self.relay_used = False
        return self._receipt("RESET", position=self.position, sonar=1, wave=1)

    def walk(self, name):
        if self.phase != "preparation" or self.turn >= PREP_STEPS:
            raise RuntimeError("PREPARATION_EXHAUSTED")
        delta = dict(STEPS).get(name)
        if delta is None:
            raise ValueError("INVALID_MOVE")
        target = (self.position[0] + delta[0], self.position[1] + delta[1])
        if layout(target) == "#":
            raise RuntimeError("ATTEMPT_TO_CROSS_WALL")
        self.turn += 1
        self.position = target
        return self._receipt("MOVE", step=self.turn, position=self.position)

    def read_relay(self):
        if self.phase != "preparation" or self.relay_used:
            raise RuntimeError("RELAY_ALREADY_USED_OR_WRONG_PHASE")
        c = layout(self.position)
        if c not in RELAY_COVERAGE:
            raise RuntimeError("NO_ACTUALLY_VISITED_RELAY")
        self.relay_used = True
        self.sonar_left = 0  # One shared information battery: relay OR live sonar.
        return self._receipt("RELAY", relay=c,
                             facts=[[wave, self._lanes[wave]] for wave in RELAY_COVERAGE[c]],
                             position=self.position)

    def start_waves(self):
        if self.phase != "preparation":
            raise RuntimeError("BAD_PHASE")
        self.phase = "waves"
        return self._receipt("WAVES_START", wave=1)

    def sonar(self):
        if self.phase != "waves" or self.sonar_left != 1:
            raise RuntimeError("NO_SONAR_AVAILABLE")
        self.sonar_left = 0
        return self._receipt("SONAR", wave=self.current_wave,
                             gate=self._lanes[self.current_wave])

    def defend(self, gate):
        if self.phase != "waves" or gate not in GATES:
            raise RuntimeError("INVALID_DEFENSE")
        w = self.current_wave
        actual = self._lanes[w]
        held = actual == gate
        if held:
            self.current_wave += 1
            if self.current_wave > WAVES:
                self.phase = "cleared"
        else:
            self.phase = "failed"
        return self._receipt("DEFEND", wave=w, guessed_gate=gate, actual_gate=actual,
                             held=held, completed=self.phase == "cleared",
                             lives_after=1 if held else 0)


@dataclass
class Knowledge:
    """Only owner-attested past observations; never inferred imagined gates."""
    gates: dict[int, str] = field(default_factory=dict)
    visited_relays: set[str] = field(default_factory=set)
    ledger: list[dict] = field(default_factory=list)

    def learn(self, receipt):
        if not verified(receipt) or receipt.get("source") != "AUTHOR_BUILT_FORTRESS_ENGINE":
            raise ValueError("UNVERIFIED_SOURCE_RECEIPT")
        kind = receipt["kind"]
        if kind == "RELAY":
            rid = receipt["relay"]
            if rid not in RELAY_COVERAGE or tuple(w for w, _ in receipt["facts"]) != RELAY_COVERAGE[rid]:
                raise ValueError("WRONG_RELAY_SCOPE")
            observations = receipt["facts"]
            self.visited_relays.add(rid)
        elif kind == "SONAR":
            observations = ((receipt["wave"], receipt["gate"]),)
        elif kind == "DEFEND":
            observations = ((receipt["wave"], receipt["actual_gate"]),)
        else:
            observations = ()
        for w, direction in observations:
            if not 1 <= w <= WAVES or direction not in GATES:
                raise ValueError("INVALID_SOURCE_FACT")
            if w in self.gates and self.gates[w] != direction:
                raise ValueError("INCOMPATIBLE_HISTORY_SOURCE_EPOCH")
            self.gates[w] = direction
        self.ledger.append(receipt)


def expected_progress(known, sonar_available=True):
    """Exact expected consecutive defended waves with one sonar and uniform guesses.

    Critically, this uses *knowledge of which waves* would be revealed, not
    their hidden directions. A conventional Bayesian one-trial comparator.
    """
    live_prob = 1.0
    sonar = sonar_available
    expected = 0.0
    for wave in range(1, WAVES + 1):
        if wave not in known and sonar:
            sonar = False
        elif wave not in known:
            live_prob *= .25
        expected += live_prob
    return expected


def accessible_relays(knowledge):
    return tuple(r for r in sorted(RELAY_COVERAGE)
                 if r not in knowledge.visited_relays
                 and len(public_route(r)) <= PREP_STEPS)


def choose_classical(knowledge, iteration=True, remaining_attempts=MAX_ATTEMPTS):
    """Classical expected survival plus explicitly future information payoff.

    Includes a no-scout option that preserves the sole current-wave sonar.
    All values depend on PUBLIC relay coverage and past receipts, not secret gates.
    It is a competent conventional VOI heuristic, not an optimal POMDP.
    """
    options = (None,) + accessible_relays(knowledge)
    known = set(knowledge.gates)
    if not iteration:
        # Diagnostic one-wave objective: why spend a shared information charge
        # on reconnaissance that doesn't immediately secure the next wave?
        # Can still learn by losing, but no advance investment.
        return None

    def score(r):
        revealed = set(RELAY_COVERAGE[r]) - known if r else set()
        current = expected_progress(known | revealed, sonar_available=(r is None))
        # Two-period conventional approximation: future usefulness of today's
        # observation, discounted and multiplied by remaining replay chances.
        next_run = expected_progress(known | revealed, sonar_available=True)
        value = current + min(remaining_attempts - 1, 3) * .75 * next_run
        return (round(value, 12), len(revealed),
                -(len(public_route(r)) if r else 0),
                -(ord(r) if r else 0))
    return max(options, key=score)


def choose_motif(knowledge, remaining_attempts):
    """Original MOTIF-003 ranks hypothetical *future* read capabilities.

    Shared charge means scouting sacrifices a live sonar THIS attempt, but may
    create reusable evidence in later attempts. All imagined gates remain blank.
    """
    options = accessible_relays(knowledge)
    native = native003()
    if not options:
        return None
    initial = frozenset({("witnessed", str(w)) for w in knowledge.gates} |
                        {("visited", r) for r in knowledge.visited_relays} |
                        {("remaining", str(min(3, remaining_attempts)))})
    def possibilities(state, _verbs):
        rem = int(next(t[1] for t in state if t[0] == "remaining"))
        if rem <= 0:
            return
        already = {t[1] for t in state if t[0] == "visited"}
        for rid in options:
            if rid in already:
                continue
            base = frozenset(t for t in state if t[0] != "remaining")
            future = base | {("visited", rid), ("remaining", str(rem - 1))}
            for w in RELAY_COVERAGE[rid]:
                future |= {("potential_intel", str(w)), ("skill", f"read_wave_{w}")}
            yield (f"inspect:{rid}", (), frozenset(future))
        for tag, name in state:
            if tag == "potential_intel":
                yield (f"hypothetical_option:{name}", (), state)
    def utility(state, _initial):
        potential = {int(t[1]) for t in state if t[0] == "potential_intel"}
        witnessed = {int(t[1]) for t in state if t[0] == "witnessed"}
        return sum((WAVES + 1 - wave) / WAVES for wave in potential - witnessed)
    rows = native.analyze_first_moves(
        initial, tuple(options), possibilities, utility,
        horizon=min(3, remaining_attempts), max_worlds=128)
    rows = [r for r in rows if r["operator"].startswith("inspect:")]
    if not rows:
        return None
    def rank(row):
        rid = row["operator"].split(":", 1)[1]
        return (len(row["new_affordances"]), len(row["new_skill_facts"]),
                round(row["immediate_delta"], 10),
                row["reachable_after_first_move"],
                -len(public_route(rid)), -ord(rid[0]))
    chosen_row = max(rows, key=rank)
    rid = chosen_row["operator"].split(":", 1)[1]
    coverage = len(set(RELAY_COVERAGE[rid]) - set(knowledge.gates))
    # Native capability evidence is valued only if a future replay can use it.
    # Otherwise retain the one-use current sonar. This is an authored rule,
    # *not* a learned optimal policy.
    immediate_without = expected_progress(set(knowledge.gates), True)
    immediate_with = expected_progress(set(knowledge.gates) | set(RELAY_COVERAGE[rid]), False)
    future_dividend = max(0, remaining_attempts - 1) * .85 * coverage
    return rid if immediate_with + future_dividend > immediate_without else None


def pick_relay(knowledge, policy, attempt):
    if policy == "motif_iterative":
        return choose_motif(knowledge, MAX_ATTEMPTS - attempt + 1)
    if policy in ("classical_iterative", "classical_no_memory"):
        return choose_classical(knowledge, iteration=True, remaining_attempts=MAX_ATTEMPTS - attempt + 1)
    if policy == "classical_immediate":
        return choose_classical(knowledge, iteration=False, remaining_attempts=MAX_ATTEMPTS - attempt + 1)
    raise ValueError("UNREGISTERED_POLICY")


def run_case(seed, policy):
    if policy not in POLICIES or seed not in DEV_SEEDS + TEST_SEEDS:
        raise ValueError("UNREGISTERED_CASE")
    owner = FortOwner(seed)
    memory = Knowledge()
    attempts = []
    for n in range(1, MAX_ATTEMPTS + 1):
        if policy == "classical_no_memory":
            memory = Knowledge()  # deliberate memory ablation
        attempt_receipts = []
        def note(receipt):
            memory.learn(receipt)
            attempt_receipts.append(receipt)
            return receipt
        note(owner.begin())
        chosen = pick_relay(memory, policy, n)
        steps = 0
        if chosen is not None:
            for move in public_route(chosen):
                note(owner.walk(move)); steps += 1
            note(owner.read_relay())
        note(owner.start_waves())
        defended = 0
        failure = None
        for w in range(1, WAVES + 1):
            if w not in memory.gates and owner.sonar_left:
                note(owner.sonar())
            # If unknown after the limited sonar, guess fixed N. The environment
            # reveals the true answer only after the attempted defense.
            gate = memory.gates.get(w, "N")
            witnessed = note(owner.defend(gate))
            if witnessed["held"]:
                defended += 1
            else:
                failure = w
                break
        completed = defended == WAVES
        attempts.append({"attempt": n, "relay": chosen,
                         "prep_steps": steps, "waves_survived": defended,
                         "first_breach_wave": failure,
                         "completed": completed,
                         "distinct_wave_facts": len(memory.gates),
                         "visited_relays": sorted(memory.visited_relays),
                         "sonar_used": sum(x["kind"] == "SONAR" for x in attempt_receipts),
                         "receipts": attempt_receipts})
        if completed:
            break
    finished_at = next((a["attempt"] for a in attempts if a["completed"]), None)
    return {"seed": seed, "policy": policy, "completed_at": finished_at,
            "completed_by_10": finished_at is not None and finished_at <= TARGET_ATTEMPTS,
            "completed_by_14": finished_at is not None,
            "attempts_used": len(attempts),
            "restricted_attempts": finished_at if finished_at is not None else MAX_ATTEMPTS + 1,
            "total_prep_moves": sum(a["prep_steps"] for a in attempts),
            "total_sonar": sum(a["sonar_used"] for a in attempts),
            "total_defense_steps": sum(a["waves_survived"] + (a["first_breach_wave"] is not None)
                                       for a in attempts),
            "wave_facts_at_finish": len(memory.gates),
            "distinct_relays_at_finish": len(memory.visited_relays),
            "attempts": attempts, "model_calls": 0, "real_world_actions": 0,
            "source_scope": "AUTHOR_BUILT_DETERMINISTIC_FORTRESS_REPLAY"}


def aggregate(rows):
    subset = {p: [x for x in rows if x["policy"] == p] for p in POLICIES}
    def stats(ss):
        successes = sorted(r["completed_at"] for r in ss if r["completed_at"] is not None)
        return {"cases": len(ss), "cleared_by_10": sum(r["completed_by_10"] for r in ss),
                "cleared_by_14": len(successes),
                "first_success_attempts": successes,
                "mean_attempts_success_only": round(sum(successes)/len(successes), 5) if successes else None,
                "mean_restricted_attempts_all": round(sum(r["restricted_attempts"] for r in ss)/len(ss), 5),
                "mean_total_prep_moves": round(sum(r["total_prep_moves"] for r in ss)/len(ss), 3),
                "mean_wave_facts_at_finish": round(sum(r["wave_facts_at_finish"] for r in ss)/len(ss), 3)}
    return {p: stats(ss) for p, ss in subset.items()}


def benchmark(split="development", full_receipts=False):
    if split not in ("development", "heldout"):
        raise ValueError("UNREGISTERED_SPLIT")
    seeds = DEV_SEEDS if split == "development" else TEST_SEEDS
    runs = [run_case(seed, policy) for seed in seeds for policy in POLICIES]
    summary = aggregate(runs)
    pairs = []
    for seed in seeds:
        items = {r["policy"]: r for r in runs if r["seed"] == seed}
        pairs.append({"seed": seed,
                      "motif_minus_classical_restricted_attempts": (
                          items["motif_iterative"]["restricted_attempts"] -
                          items["classical_iterative"]["restricted_attempts"]),
                      "motif_minus_immediate_restricted_attempts": (
                          items["motif_iterative"]["restricted_attempts"] -
                          items["classical_immediate"]["restricted_attempts"])})
    result = {"experiment": "VOID-004", "classification": "AUTHOR_AUTHORED_WAVE_SIMULATOR",
              "split": split, "map": MAP, "wave_count": WAVES,
              "max_attempts": MAX_ATTEMPTS, "target_attempts": TARGET_ATTEMPTS,
              "scout_steps_per_attempt": PREP_STEPS, "sonar_per_attempt": 1,
              "policy_summaries": summary, "paired": pairs,
              "actual_native_motif003": True, "llm_calls": 0,
              "source_is_independently_authored": False,
              "real_world_actions": 0,
              "limits": "Known deterministic resets, engineered map and deterministic hidden waves; no independently administered game benchmark, no learning of mechanics, no claim beyond this controlled simulation.",
              "cases": runs if full_receipts else [{k: v for k, v in r.items() if k != "attempts"} for r in runs]}
    result["seal"] = seal(result)
    return result


if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--split", choices=("development", "heldout"), default="development")
    parser.add_argument("--full-receipts", action="store_true")
    args=parser.parse_args()
    print(json.dumps(benchmark(args.split, args.full_receipts), indent=2, sort_keys=True))
