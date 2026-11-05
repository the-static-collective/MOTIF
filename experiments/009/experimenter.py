"""MOTIF-009: The Experimenter — tree cartridges propose which graph to inspect.

No oracle imports here. The explorer sees only *unlabeled* candidate graphs,
role bindings and already revealed synthetic observations. An independent
evaluator resolves selected tickets and supplies outcomes. It cannot act on
real people, query networks, or authenticate synthetic evidence.

Unlike intervention design, this is POOL-BASED ACTIVE OBSERVATION: it selects
which already-existing synthetic example to reveal, not which change to
perform on the world.
"""
from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "008"))

from collections import Counter
from dataclasses import dataclass
from random import Random
from hashlib import sha256
from typing import Iterable

from cartridge import Cartridge, fit_cartridge
from learner import features


@dataclass(frozen=True)
class Question:
    ticket: str
    before: frozenset[tuple[str, ...]]
    roles: tuple[str, str]


@dataclass(frozen=True)
class ProposedQuestion:
    ticket: str
    basis: str
    votes: tuple[bool, ...]
    leaf_index: int
    learned_leaf_observations: int
    score: tuple[float, ...]
    predicted_outcome: bool
    answer_known: bool = False


class QueryBudget:
    """Experimental observation budget, separate from world-actuation rights."""

    def __init__(self, maximum: int):
        if type(maximum) is not int or maximum < 1:
            raise ValueError("Question budget must be positive")
        self.maximum = maximum
        self.used: set[str] = set()

    def consume(self, ticket: str):
        if len(self.used) >= self.maximum:
            raise ValueError("No remaining observation budget")
        if ticket in self.used:
            raise ValueError("Observation ticket already consumed")
        self.used.add(ticket)


def train_committee(observed, seed=0, members=3):
    """Build role-relative, immutable tree cartridges from revealed evidence only."""
    records = tuple(observed)
    if not records:
        raise ValueError("No observed synthetic episodes")
    if members < 1 or members > 5:
        raise ValueError("Committee budget must be within 1..5")
    result = [fit_cartridge(records)]
    for idx in range(1, members):
        rng = Random((seed + 7919) * 997 + idx)
        sample = tuple(records[rng.randrange(len(records))]
                       for _ in range(len(records)))
        result.append(fit_cartridge(sample))
    return tuple(result)


def propose_question(pool: Iterable[Question], observed, 
                     committee: tuple[Cartridge, ...]) -> ProposedQuestion:
    """Prefer tree disagreement, sparse leaves, and unseen structural motifs.

    This heuristic is not a calibrated information-gain estimate. A stable
    lexical tie-break avoids consulting hidden outcome labels.
    """
    candidates = tuple(pool)
    if not candidates or not committee:
        raise ValueError("Need unlabeled candidates and a learned cartridge")
    if len({q.ticket for q in candidates}) != len(candidates):
        raise ValueError("Duplicate unlabeled query tickets")
    all_seen = Counter(f for case in observed
                       for f in features(case.before, case.roles))
    base = committee[0]
    best = None
    best_key = None
    for query in sorted(candidates, key=lambda x: x.ticket):
        row = features(query.before, query.roles)
        votes = tuple(model.predict(row) for model in committee)
        dissent = min(sum(votes), len(votes) - sum(votes))
        leaf_index = base.leaf(row)
        count = sum(base.counts[leaf_index])
        p = base.probability(row)
        uncertainty = 1 - abs(2 * p - 1)
        # Query whole-population novelty is allowed: these graphs are visible
        # *unlabeled*, unlike their outcomes.
        novelty = sum(1 / (all_seen[f] + 1) for f in row) / max(len(row), 1)
        # Tree disagreement is prioritized. Other signals break ties.
        score = (float(dissent), round(1 / (count + 1), 8),
                 round(uncertainty, 8), round(novelty, 8))
        key = (score, query.ticket)
        if best is None or key > best_key:
            best_key = key
            best = ProposedQuestion(
                query.ticket, "TREE_DISAGREEMENT_THEN_SPARSE_LEAF",
                votes, leaf_index, count, score, base.predict(row)
            )
    return best


def public_question(index: int, before, roles) -> Question:
    """Create an opaque ticket without putting the outcome in the interface."""
    if type(index) is not int or index < 0:
        raise ValueError("Ticket index invalid")
    if not isinstance(roles, tuple) or len(roles) != 2:
        raise ValueError("Explicit two-role query required")
    return Question(f"Q{index:05d}", before, roles)


def independent_oracle_answer(question: ProposedQuestion,
                              secret_index: dict[str, object]):
    """Only the EVALUATOR imports/calls this function.

    The selector has no reference to secret_index or to answer fields.
    Returns one independently generated synthetic episode when a ticket is
    consumed. QueryBudget enforcement belongs to the caller.
    """
    if question.ticket not in secret_index:
        raise ValueError("Unknown query ticket")
    return secret_index[question.ticket]
