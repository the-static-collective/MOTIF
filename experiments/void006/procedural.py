"""VOID-006: source-witnessed procedural habits, guarded reflex chunks and local surprise.

This is an analogy to automatic action selection, not a claim about biological
subconscious processes. Every primitive action is still executed and witnessed.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "void005"))
sys.path.insert(0, str(HERE.parent / "void004"))
from adversary import (DynamicOwner, EpistemicLedger, pick, projected_score,
                       relay_choice, REGIMES)
from waves import (GATES, WAVES, HUB, MAX_ATTEMPTS, TARGET_ATTEMPTS,
                   RELAY_COVERAGE, public_route, seal, verified)

DEV_SEEDS = (61001, 61007, 61019, 61031)
TEST_SEEDS = tuple(96001 + 37*i for i in range(20))
POLICIES = ("muscle_compiled", "classical_sparse", "classical_voi", "classical_stale")
SONAR_THRESHOLD = .90
MIN_HABIT_REPETITIONS = 2
MIN_CHUNK = 3


class NewWorldOwner(DynamicOwner):
    """Same unmodified VOID-005 mechanics with strictly new seed namespace."""
    def __init__(self, seed, regime):
        if seed not in DEV_SEEDS + TEST_SEEDS or regime not in REGIMES:
            raise ValueError("UNREGISTERED_NEW_WORLD")
        # DynamicOwner is limited to VOID-005's obsolete test seeds. Exactly
        # its private constructor is generalized; inherited transitions,
        # drift, fallible relays and defense feedback are not modified.
        self._lanes = {w: GATES[pick(seed, f"initial-{w}", 4)]
                       for w in range(1, WAVES + 1)}
        self.seed, self.regime = seed, regime
        self.attempt, self.sequence, self.source_epoch = 0, 0, 0
        self.phase, self.position, self.turn = "not_started", HUB, 0
        self.current_wave, self.sonar_left, self.relay_used = 1, 0, False
        self.successful_defenses = 0
        self.triggered = set()
        self.changed_waves = []  # evaluator only
        self.false_relay_claims = 0


@dataclass
class LocalEvidence:
    """Shared, non-muscle source witness: don't let fresh hearsay erase facts."""
    verified_gates: dict = field(default_factory=dict)
    verified_conflicts: int = 0

    def learn(self, receipt):
        if not verified(receipt):
            raise ValueError("UNVERIFIED_SOURCE")
        kind = receipt["kind"]
        if kind not in ("SONAR", "DEFEND"):
            return
        w = receipt["wave"]
        gate = receipt["gate"] if kind == "SONAR" else receipt["actual_gate"]
        previous = self.verified_gates.get(w)
        if previous is not None and previous[0] != gate:
            self.verified_conflicts += 1
        self.verified_gates[w] = (gate, receipt["source_epoch"])

    def confidence(self, ledger, w):
        owner = self.verified_gates.get(w)
        if owner:
            epochs_old = ledger.epoch - owner[1]
            return max(.91, 1.0 - .045 * max(0, epochs_old))
        row = ledger.latest.get(w)
        if row is None:
            return .25
        # Fallible relays are never trusted enough to bypass independent sonar.
        if row["tier"] == "fallible_relay":
            return .70 if ledger.source_downgrade else .86
        return ledger.confidence(w)

    def predict(self, ledger, w):
        owner = self.verified_gates.get(w)
        if owner:
            return owner[0]
        return ledger.predict(w)


@dataclass
class Reflex:
    gate: str
    success_count: int
    last_epoch: int


@dataclass
class HabitBook:
    """Store practiced wave->gate reactions separately from deliberative beliefs.

    Habits form only from actual held DEFEND receipts; not synthetic relays,
    hypothetical MOTIF successors, or source epoch advertisements. Consecutive
    trained reactions become options-like chunks, but execute step-by-step.
    """
    candidates: dict = field(default_factory=dict)
    reflexes: dict = field(default_factory=dict)
    chunk_index: dict = field(default_factory=dict)
    chunks: tuple = ()
    invalidations: int = 0
    updates: int = 0

    def invalidate(self, wave):
        if wave in self.reflexes:
            self.invalidations += 1
            del self.reflexes[wave]
            self._compile()

    def learn(self, receipt):
        if not verified(receipt):
            raise ValueError("UNVERIFIED_HABIT_RECEIPT")
        kind = receipt["kind"]
        if kind == "SONAR":
            w, g = receipt["wave"], receipt["gate"]
            if w in self.reflexes and self.reflexes[w].gate != g:
                self.invalidate(w)
            if self.candidates.get(w, (None,))[0] != g:
                self.candidates[w] = (g, 0)
            return
        if kind != "DEFEND":
            return
        w, actual = receipt["wave"], receipt["actual_gate"]
        old = self.candidates.get(w)
        if old and old[0] != actual:
            self.invalidate(w)
            self.candidates[w] = (actual, 0)
        if not receipt["held"]:
            # A failed primitive action is an interruption signal, not practice.
            self.invalidate(w)
            self.candidates[w] = (actual, 0)
            return
        old = self.candidates.get(w)
        repetitions = old[1] + 1 if old and old[0] == actual else 1
        self.candidates[w] = (actual, repetitions)
        if repetitions >= MIN_HABIT_REPETITIONS:
            previous = self.reflexes.get(w)
            self.reflexes[w] = Reflex(actual, repetitions, receipt["source_epoch"])
            if previous is None:
                self._compile()
        self.updates += 1

    def _compile(self):
        groups = []
        start = None
        for w in range(1, WAVES + 2):
            active = w <= WAVES and w in self.reflexes
            if active and start is None:
                start = w
            if not active and start is not None:
                if w - start >= MIN_CHUNK:
                    groups.append(tuple(range(start, w)))
                start = None
        self.chunks = tuple(groups)
        self.chunk_index = {w: tuple(group)
                            for group in self.chunks for w in group}

    def reflex(self, wave):
        r = self.reflexes.get(wave)
        if r is None:
            return None
        return {"gate": r.gate,
                "chunked": wave in self.chunk_index,
                "chunk_length": len(self.chunk_index.get(wave, ())),
                "prior_confirmed_successes": r.success_count}


class SparseView:
    """Reuses the same classical VOI formula with wave-local source confidence."""
    def __init__(self, ledger, local):
        self.ledger, self.local = ledger, local
        self.source_downgrade = ledger.source_downgrade

    def confidence(self, wave, stale=False):
        return self.local.confidence(self.ledger, wave)


def sparse_relay_choice(ledger, local, remaining):
    available = (None,) + tuple(r for r in sorted(RELAY_COVERAGE)
                                 if r not in ledger.visited_relays)
    view = SparseView(ledger, local)
    return max(available, key=lambda r:
               (projected_score(view, r, remaining),
                0 if r is None else 1))


def run_case(seed, regime, policy, full=False):
    if seed not in DEV_SEEDS + TEST_SEEDS or regime not in REGIMES or policy not in POLICIES:
        raise ValueError("UNREGISTERED_TRIAL")
    owner = NewWorldOwner(seed, regime)
    ledger, local, habits = EpistemicLedger(), LocalEvidence(), HabitBook()
    episodes = []
    totals = Counter()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        trace = []
        def note(receipt):
            if not verified(receipt):
                raise AssertionError("OWNER_RECEIPT_INVALID")
            ledger.learn(receipt)
            local.learn(receipt)
            if policy == "muscle_compiled":
                habits.learn(receipt)
            if full:
                trace.append(receipt)
            return receipt
        note(owner.begin())
        if policy in ("muscle_compiled", "classical_sparse"):
            relay = sparse_relay_choice(ledger, local, MAX_ATTEMPTS + 1 - attempt)
        else:
            relay = relay_choice(ledger, policy, MAX_ATTEMPTS + 1 - attempt)
        if relay:
            for move in public_route(relay):
                note(owner.walk(move))
            note(owner.read_relay())
        note(owner.start_waves())
        success = 0
        breached = None
        step_log = []
        for w in range(1, WAVES + 1):
            if policy in ("muscle_compiled", "classical_sparse"):
                conf = local.confidence(ledger, w)
            else:
                conf = ledger.confidence(w, stale_ablated=(policy == "classical_stale"))
            if conf < SONAR_THRESHOLD and owner.sonar_left:
                r = note(owner.sonar())
                totals["sonars"] += 1
                # Any unexpected authoritative observation can interrupt habits.
                if policy in ("muscle_compiled", "classical_sparse"):
                    conf = local.confidence(ledger, w)
            reflex = habits.reflex(w) if policy == "muscle_compiled" else None
            if reflex is not None:
                gate = reflex["gate"]
                totals["automatic_defenses"] += 1
                if reflex["chunked"]:
                    totals["chunk_primitive_defenses"] += 1
                    totals["chunk_length_sum"] += reflex["chunk_length"]
            else:
                gate = (local.predict(ledger, w)
                        if policy in ("muscle_compiled", "classical_sparse")
                        else ledger.predict(w)) or "N"
                totals["deliberative_gate_lookups"] += 1
            old_invalidations = habits.invalidations
            result = note(owner.defend(gate))
            totals["defenses"] += 1
            if policy == "muscle_compiled":
                totals["surprise_interruptions"] += habits.invalidations - old_invalidations
            if full:
                step_log.append({"wave": w, "gate": gate, "confidence_pre_action": conf,
                                 "automatic": reflex is not None,
                                 "chunked": bool(reflex and reflex["chunked"]),
                                 "held": result["held"], "epoch": ledger.epoch})
            if result["held"]:
                success += 1
            else:
                breached = w
                break
        cleared = breached is None and success == WAVES
        episodes.append({"attempt": attempt, "relay": relay, "held": success,
                         "breached_wave": breached, "cleared": cleared,
                         "known_ledger_waves": len(ledger.latest),
                         "source_epoch": ledger.epoch, "step_log": step_log,
                         "receipts": trace})
        if cleared:
            break
    completion = next((a["attempt"] for a in episodes if a["cleared"]), None)
    out = {
        "seed": seed, "regime": regime, "policy": policy,
        "first_clear_attempt": completion,
        "restricted_attempts": completion or MAX_ATTEMPTS + 1,
        "cleared_by_10": completion is not None and completion <= TARGET_ATTEMPTS,
        "cleared_by_14": completion is not None,
        "total_attempts": len(episodes),
        "defenses": totals["defenses"],
        "deliberative_gate_lookups": totals["deliberative_gate_lookups"],
        "automatic_defenses": totals["automatic_defenses"],
        "chunk_primitive_defenses": totals["chunk_primitive_defenses"],
        "mean_active_chunk_length": round(
            totals["chunk_length_sum"] / totals["chunk_primitive_defenses"], 4)
            if totals["chunk_primitive_defenses"] else 0.0,
        "sonars": totals["sonars"],
        "reflexes_at_end": len(habits.reflexes),
        "chunks_at_end": len(habits.chunks),
        "reflex_invalidations": habits.invalidations,
        "verified_source_conflicts": local.verified_conflicts,
        "surprise_interruptions": totals["surprise_interruptions"],
        "owner_report_falsehoods_evaluator_only": owner.false_relay_claims,
        "owner_changes_evaluator_only": owner.changed_waves,
        "research_only": True, "actual_native_owner": True,
        "model_calls": 0, "external_actions": 0,
        "attempts": episodes,
    }
    out["seal"] = seal(out)
    return out


def benchmark(split="development", full=False):
    if split not in ("development", "heldout"):
        raise ValueError("UNREGISTERED_SPLIT")
    seeds = DEV_SEEDS if split == "development" else TEST_SEEDS
    rows = [run_case(seed, regime, policy, full)
            for seed in seeds for regime in REGIMES for policy in POLICIES]
    groups = {}
    paired = []
    for regime in REGIMES:
        groups[regime] = {}
        for policy in POLICIES:
            rs = [x for x in rows if x["regime"] == regime and x["policy"] == policy]
            groups[regime][policy] = {
                "n": len(rs),
                "cleared_by_10": sum(x["cleared_by_10"] for x in rs),
                "cleared_by_14": sum(x["cleared_by_14"] for x in rs),
                "mean_restricted_attempts": round(sum(x["restricted_attempts"] for x in rs) / len(rs), 5),
                "mean_deliberative_gate_lookups": round(sum(x["deliberative_gate_lookups"] for x in rs) / len(rs), 4),
                "mean_automatic_defenses": round(sum(x["automatic_defenses"] for x in rs) / len(rs), 4),
                "mean_chunk_primitive_defenses": round(sum(x["chunk_primitive_defenses"] for x in rs) / len(rs), 4),
                "mean_sonar_uses": round(sum(x["sonars"] for x in rs) / len(rs), 4),
                "surprise_interruptions": sum(x["surprise_interruptions"] for x in rs),
            }
        for seed in seeds:
            group = {x["policy"]: x for x in rows if x["seed"] == seed and x["regime"] == regime}
            paired.append({
                "seed": seed, "regime": regime,
                "muscle_minus_sparse": group["muscle_compiled"]["restricted_attempts"]
                                        - group["classical_sparse"]["restricted_attempts"],
                "muscle_minus_voi": group["muscle_compiled"]["restricted_attempts"]
                                     - group["classical_voi"]["restricted_attempts"],
            })
    summary = {
        "experiment": "VOID-006", "split": split,
        "source": "INHERITED_PROGRAMMER_AUTHORED_VOID005_FORTRESS",
        "status": "RESEARCH_HOLD_PROCEDURAL_MEMORY_NOT_BIOLOGICAL_SUBCONSCIOUS",
        "seeds": seeds, "regimes": REGIMES, "policies": POLICIES,
        "cases": len(rows), "summary": groups, "paired": paired,
        "primary": "RESTRICTED_FIRST_24_WAVE_CLEAR_ATTEMPT",
        "all_primitive_defenses_witnessed": True,
        "outcome_truth_is_owner_programmed": True,
        "new_heldout_scores_not_USED_TO_TUNE_METHOD": True,
        "model_calls": 0, "external_actions": 0,
        "rows": rows,
    }
    summary["seal"] = seal(summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("development", "heldout"), default="development")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    print(json.dumps(benchmark(args.split, args.full), sort_keys=True, indent=2))
