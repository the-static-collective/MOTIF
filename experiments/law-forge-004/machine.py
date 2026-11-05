"""LAW-FORGE-004 — The Grammar Breaker.

A source-separated *finite-state operator* learner, not an open-ended compiler.
The old language is an accumulator folding a single binary output through a
fixed binary truth table. If that cannot fit actual observations, propose an
evidence-gathering protocol and synthesize a bounded state-transition program.

The hidden simulator is never imported here. Every proposed sample must be
executed by a separate evaluator; reviewing a model never grants authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from typing import Optional
import json


MAX_TRAIN_LENGTH = 7
MAX_STATES = 4
SUFFIX_HORIZON = 3
PREFIX_HORIZON = 3
AUTHORITY = "SYNTHETIC_MEMBERSHIP_QUERY_ONLY"


def digest(value):
    return sha256(json.dumps(value, sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


def valid_word(word, max_length=12):
    if (not isinstance(word, (tuple, list)) or len(word) > max_length
            or any(type(x) is not int or x not in (0, 1) for x in word)):
        raise ValueError("Expected bounded binary word")
    return tuple(word)


def words(max_length, minimum=0):
    return tuple(w for n in range(minimum, max_length + 1)
                 for w in product((0, 1), repeat=n))


@dataclass(frozen=True)
class Observation:
    word: tuple[int, ...]
    result: int
    provenance: str = "SYNTHETIC_MEMBERSHIP_OBSERVATION"

    def __post_init__(self):
        valid_word(self.word)
        if (type(self.result) is not int or self.result not in (0, 1)
                or self.provenance != "SYNTHETIC_MEMBERSHIP_OBSERVATION"):
            raise ValueError("Invalid synthetic evidence")


def evidence_table(observations):
    table = {}
    for row in observations:
        if not isinstance(row, Observation):
            raise ValueError("All witnesses must be typed synthetic observations")
        if row.word in table and table[row.word] != row.result:
            raise ValueError("Conflicting witnesses for identical membership query")
        table[row.word] = row.result
    return table


def evidence_id(observations):
    table = evidence_table(observations)
    return digest([[list(w), y] for w, y in sorted(
        table.items(), key=lambda item: (len(item[0]), item[0]))])


@dataclass(frozen=True)
class FoldModel:
    table: tuple[int, int, int, int]
    source_digest: str

    def predict(self, word):
        word = valid_word(word)
        if not word:
            return None
        state = word[0]
        for x in word[1:]:
            state = self.table[2 * state + x]
        return state


def fold_candidates(observations):
    seen = evidence_table(observations)
    source = evidence_id(observations)
    return tuple(
        model for outputs in product((0, 1), repeat=4)
        for model in (FoldModel(tuple(outputs), source),)
        if all(model.predict(w) == y for w, y in seen.items() if w)
    )


@dataclass(frozen=True)
class MembershipBatch:
    words: tuple[tuple[int, ...], ...]
    authority: str = AUTHORITY

    def __post_init__(self):
        if self.authority != AUTHORITY or len(self.words) > 255:
            raise ValueError("No privileged or unbounded probe batches")
        if len(set(self.words)) != len(self.words):
            raise ValueError("Duplicate probe query")
        for word in self.words:
            valid_word(word, MAX_TRAIN_LENGTH)

    @property
    def cost(self):
        return len(self.words)

    def packet(self):
        # A digest permits concise receipts; the concrete request words
        # remain inspectable in the actual typed batch.
        return {"schema": "motif.law-forge.membership-batch.v1",
                "count": len(self.words),
                "word_set_digest": digest([list(w) for w in self.words]),
                "authority": self.authority, "real_world_authority": False}

    @classmethod
    def from_word_batch(cls, word_batch, packet):
        if not isinstance(packet, dict) or set(packet) != {
            "schema", "count", "word_set_digest", "authority",
            "real_world_authority"
        } or packet["schema"] != "motif.law-forge.membership-batch.v1" or (
            packet["authority"] != AUTHORITY or
            packet["real_world_authority"] is not False
        ):
            raise ValueError("Invalid synthetic-only membership proposal")
        batch = cls(tuple(valid_word(w, MAX_TRAIN_LENGTH)
                          for w in word_batch))
        if (type(packet["count"]) is not int or packet["count"] != batch.cost
                or packet["word_set_digest"] != batch.packet()["word_set_digest"]):
            raise ValueError("Tampered membership batch")
        return batch


def missing_queries(observations):
    seen = evidence_table(observations)
    return MembershipBatch(tuple(w for w in words(MAX_TRAIN_LENGTH)
                                 if w not in seen))


@dataclass(frozen=True)
class StateProgram:
    """Executable Moore machine: a persisted state changes per input event."""
    outputs: tuple[int, ...]
    transitions: tuple[tuple[int, int], ...]
    source_digest: str
    evidence_horizon: int = MAX_TRAIN_LENGTH

    def __post_init__(self):
        n = len(self.outputs)
        if not (1 <= n <= MAX_STATES and len(self.transitions) == n):
            raise ValueError("Machine has more than four states or inconsistent rows")
        if any(type(x) is not int or x not in (0, 1) for x in self.outputs):
            raise ValueError("State outputs must be Boolean")
        for pair in self.transitions:
            if (not isinstance(pair, tuple) or len(pair) != 2 or
                    any(type(x) is not int or not 0 <= x < n for x in pair)):
                raise ValueError("Missing or invalid state transitions")
        if (not isinstance(self.source_digest, str) or
                len(self.source_digest) != 64 or any(
                    c not in "0123456789abcdef" for c in self.source_digest
                ) or type(self.evidence_horizon) is not int or (
                    self.evidence_horizon != MAX_TRAIN_LENGTH
                )):
            raise ValueError("Unverifiable source digest or training horizon")

    @property
    def state_count(self):
        return len(self.outputs)

    def trace(self, word):
        word = valid_word(word)
        state = 0
        visited = [state]
        for symbol in word:
            state = self.transitions[state][symbol]
            visited.append(state)
        return tuple(visited)

    def predict(self, word):
        return self.outputs[self.trace(word)[-1]]

    @property
    def id(self):
        return "fsm-" + digest({
            "outputs": self.outputs,
            "transitions": self.transitions,
            "horizon": self.evidence_horizon,
            "evidence": self.source_digest
        })[:24]

    def packet(self):
        return {"schema": "motif.law-forge.state-program.v1",
                "id": self.id,
                "state_count": self.state_count,
                "start_state": 0,
                "outputs": list(self.outputs),
                "transitions": [list(row) for row in self.transitions],
                "source_digest": self.source_digest,
                "evidence_horizon": self.evidence_horizon,
                "status": "PROPOSAL_ONLY",
                "authority": "SYNTHETIC_PREDICTION_ONLY",
                "real_world_authority": False}

    @classmethod
    def from_packet(cls, packet):
        if not isinstance(packet, dict) or set(packet) != {
            "schema", "id", "state_count", "start_state", "outputs",
            "transitions", "source_digest", "evidence_horizon",
            "status", "authority", "real_world_authority"
        } or packet["schema"] != "motif.law-forge.state-program.v1" or (
            packet["status"] != "PROPOSAL_ONLY"
        ) or packet["authority"] != "SYNTHETIC_PREDICTION_ONLY" or (
            packet["real_world_authority"] is not False
        ) or type(packet["start_state"]) is not int or (
            packet["start_state"] != 0
        ):
            raise ValueError("Malformed or privileged finite-state machine")
        if (not isinstance(packet["outputs"], list) or
                not isinstance(packet["transitions"], list) or
                type(packet["state_count"]) is not int or
                len(packet["outputs"]) != packet["state_count"]):
            raise ValueError("Mismatched machine fields")
        transitions = tuple(tuple(row) if isinstance(row, list) else ()
                            for row in packet["transitions"])
        model = cls(tuple(packet["outputs"]), transitions,
                    packet["source_digest"], packet["evidence_horizon"])
        if model.id != packet["id"]:
            raise ValueError("Tampered state-machine content")
        return model


@dataclass(frozen=True)
class Discovery:
    status: str
    machine: Optional[StateProgram]
    distinctions: tuple[tuple[tuple[int, ...], tuple[int, ...],
                              tuple[int, ...]], ...] = ()
    candidate_states: int = 0


def infer(observations):
    """Finite observation-table DFA inference (classical, not novel maths).

    Histories (prefixes) are empirically distinct when an observed future
    continuation causes different outputs. Build states from those residual
    signatures, then infer transitions. Refuse if table is not closed,
    inconsistent, larger than MAX_STATES, or disagrees with any observation.

    Prefix representatives reach depth 3. Suffix witnesses reach depth 3.
    Every concatenation reaches depth <=7, not an oracle hidden variable.
    """
    observed = evidence_table(observations)
    expected = words(MAX_TRAIN_LENGTH)
    if any(w not in observed for w in expected):
        return Discovery("HOLD_INSUFFICIENT_MEMBERSHIP_EVIDENCE", None)
    prefixes = words(PREFIX_HORIZON)
    expanded = words(PREFIX_HORIZON + 1)
    suffixes = words(SUFFIX_HORIZON)
    def signature(prefix):
        return tuple(observed[prefix + suffix] for suffix in suffixes)
    reps = {}
    for prefix in prefixes:
        reps.setdefault(signature(prefix), prefix)
    if len(reps) > MAX_STATES:
        return Discovery("HOLD_STATE_CAPACITY_EXCEEDED", None,
                         candidate_states=len(reps))
    for prefix in expanded:
        if signature(prefix) not in reps:
            return Discovery("HOLD_UNCLOSED_STATE_TABLE", None,
                             candidate_states=len(reps))
    state_ids = {sig: i for i, sig in enumerate(reps)}
    for sig, rep in reps.items():
        for prefix in prefixes:
            if signature(prefix) != sig:
                continue
            if any(signature(rep + (bit,)) != signature(prefix + (bit,))
                   for bit in (0, 1)):
                return Discovery("HOLD_INCONSISTENT_STATE_TABLE", None,
                                 candidate_states=len(reps))
    transitions = tuple(tuple(state_ids[signature(rep + (bit,))]
                              for bit in (0, 1))
                        for rep in reps.values())
    outputs = tuple(observed[rep] for rep in reps.values())
    machine = StateProgram(outputs, transitions, evidence_id(observations))
    if any(machine.predict(word) != value for word, value in observed.items()):
        return Discovery("HOLD_TRAINING_CONTRADICTION", None,
                         candidate_states=len(reps))
    # A distinction certificate is always a *measured suffix*, not a claim
    # about hidden causal variables.
    pairs = []
    ordered = list(reps.items())
    for i, (sig_a, rep_a) in enumerate(ordered):
        for sig_b, rep_b in ordered[i+1:]:
            distinction = next((suffix for j, suffix in enumerate(suffixes)
                                if sig_a[j] != sig_b[j]), None)
            if distinction is None:
                raise AssertionError("Non-distinct row in state basis")
            pairs.append((rep_a, rep_b, distinction))
    return Discovery("PROPOSE_STATEFUL_OPERATOR", machine,
                     tuple(pairs), candidate_states=len(reps))


def independent_review(model, examples):
    if model is None:
        return {"status": "HOLD_UNIDENTIFIED", "failures": None}
    rows = tuple(examples)
    if len(rows) < 64:
        return {"status": "HOLD_INSUFFICIENT_REVIEW", "failures": None}
    if any(not isinstance(row, Observation) for row in rows):
        raise ValueError("Independent review requires typed synthetic evidence")
    distinct = {row.word for row in rows}
    by_length = {n: sum(len(w) == n for w in distinct) for n in (8, 9, 10, 11)}
    if len(distinct) < 64 or any(count < 12 for count in by_length.values()):
        return {"status": "HOLD_REVIEW_COVERAGE", "failures": None}
    failures = sum(model.predict(row.word) != row.result for row in rows)
    return {"status": ("ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW"
                       if failures == 0 else "HOLD_INDEPENDENT_FALSIFIER"),
            "failures": failures}
