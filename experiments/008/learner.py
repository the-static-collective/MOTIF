"""MOTIF-008 local, domain-agnostic relational hypothesis learner.

IMPORTANT: this module never imports oracle.py, nor sees a family name, hidden
success flag, or held-out evaluation split. It receives only synthetic
before/after observations and explicitly supplied actor/target role bindings.

Induces 1-edge, 2-edge shared-witness, and conjunction-of-two candidate
conditions; validation-selects a predictor and abstains if its observed
performance is inadequate. Compare with a simple edge-only baseline and a
classical depth-2 decision-tree baseline trained on the SAME observations.

This is symbolic relational feature induction, not a neural native model,
causal proof, privacy guarantee, or authority to act.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable
import math

Fact = tuple[str, ...]
Motif = tuple[Fact, ...]
FeatureSet = frozenset[Motif]

MIN_CLASS = 3
MIN_SUPPORT = 3
MAX_FEATURES = 80
MAX_PAIRS = 4000
ABSTAIN_BELOW = 0.90


def features(world: frozenset[Fact], roles: tuple[str, str],
             use_joins=True) -> FeatureSet:
    """Role-invariant graph motifs. No knowledge of predicate vocabulary.

    The candidate grammar is nevertheless hand-designed and limited to:
    (i) unary and direct-binary facts touching both role IDs;
    (ii) two directed edges joining actor and target through ONE identical
    non-role witness, in either direction.
    """
    if len(roles) != 2 or roles[0] == roles[1]:
        raise ValueError("Experiment needs two distinct explicit roles")
    actor, target = roles
    names = {actor: "?0", target: "?1"}
    tokens = set()
    edges = []
    for fact in world:
        if not isinstance(fact, tuple) or not (2 <= len(fact) <= 4):
            raise ValueError("Invalid finite relational fact")
        if len(fact) == 2 and fact[1] in names:
            tokens.add((tuple([fact[0], names[fact[1]]]),))
        elif len(fact) == 3:
            if all(x in names for x in fact[1:]):
                tokens.add(((fact[0], names[fact[1]], names[fact[2]]),))
            edges.append(fact)
    if not use_joins:
        return frozenset(tokens)
    for start, finish in ((actor, target), (target, actor)):
        for first in edges:
            if first[1] != start or first[2] in names:
                continue
            intermediate = first[2]
            for second in edges:
                if second[1] != intermediate or second[2] != finish:
                    continue
                pattern = ((first[0], names[start], "?x"),
                           (second[0], "?x", names[finish]))
                tokens.add(tuple(sorted(pattern)))
    return frozenset(tokens)


def observed_outcome(episode) -> bool:
    """Only use independent before/after graphs, not an oracle label."""
    if getattr(episode, "provenance", None) != "SYNTHETIC_ORACLE":
        raise ValueError("MOTIF-008 accepts only declared synthetic observations")
    if not (hasattr(episode, "before") and hasattr(episode, "observed_after")
            and hasattr(episode, "roles")):
        raise ValueError("Missing before/after evidence")
    before, after = episode.before, episode.observed_after
    # The intentionally constrained oracle never has a partial success.
    # Any change is the derived target in this benchmark, not a real 'good' outcome.
    return before != after


def encoded(episodes, use_joins=True) -> tuple[tuple[FeatureSet, bool], ...]:
    return tuple((features(e.before, e.roles, use_joins),
                  observed_outcome(e)) for e in episodes)


def balanced_accuracy(truth: Iterable[bool], prediction: Iterable[bool]) -> float:
    actual, predicted = tuple(truth), tuple(prediction)
    if not actual or len(actual) != len(predicted):
        raise ValueError("Mismatched labeled benchmark examples")
    pos = sum(actual)
    neg = len(actual) - pos
    if not pos or not neg:
        raise ValueError("Both classes needed for balanced accuracy")
    tp = sum(y and guess for y, guess in zip(actual, predicted))
    tn = sum((not y) and (not guess) for y, guess in zip(actual, predicted))
    return .5 * (tp / pos + tn / neg)


def candidate_features(training, max_features=MAX_FEATURES):
    counts = Counter(f for x, _ in training for f in x)
    allowed = [f for f, count in counts.items()
               if MIN_SUPPORT <= count <= len(training) - MIN_SUPPORT]
    # Deterministic cap, not a supervision-driven ranking. Report truncation.
    allowed.sort(key=lambda f: (len(f), f))
    return tuple(allowed[:max_features]), len(allowed) > max_features


def positive_if(row: FeatureSet, condition: tuple[Motif, ...]) -> bool:
    return all(item in row for item in condition)


@dataclass(frozen=True)
class Conjunction:
    condition: tuple[Motif, ...]
    validation_balanced: float
    training_balanced: float
    status: str
    considered: int
    truncated: bool

    def predict(self, row: FeatureSet) -> bool | None:
        if self.status != "PROPOSED":
            return None
        return positive_if(row, self.condition)


def fit_relational(training_episodes, validation_episodes, *, joins=True,
                   max_clauses=2, abstain_below=ABSTAIN_BELOW) -> Conjunction:
    """Fit only on training and validation. Test worlds are not accepted."""
    if max_clauses not in (1, 2):
        raise ValueError("Only bounded conjunctions are supported")
    train = encoded(training_episodes, joins)
    valid = encoded(validation_episodes, joins)
    if not train or not valid:
        raise ValueError("Need independent train and validation observations")
    if min(sum(y for _, y in train), sum(not y for _, y in train),
           sum(y for _, y in valid), sum(not y for _, y in valid)) < MIN_CLASS:
        return Conjunction((), 0.0, 0.0, "ABSTAIN_CLASS_SPARSE", 0, False)
    atoms, cut = candidate_features(train)
    options = ((atom,) for atom in atoms)
    if max_clauses == 2:
        options = list(options) + list(combinations(atoms, 2))
    best_score = None
    selected = ()
    selected_scores = (0.0, 0.0)
    considered = 0
    for combination in options:
        if considered >= MAX_PAIRS:
            cut = True
            break
        considered += 1
        train_score = balanced_accuracy(
            (y for _, y in train),
            (positive_if(x, combination) for x, _ in train))
        valid_score = balanced_accuracy(
            (y for _, y in valid),
            (positive_if(x, combination) for x, _ in valid))
        # Prefer independent validation, then train, then fewer clauses/edges.
        # A lexicographically stable order resolves remaining equalities.
        complexity = sum(len(x) for x in combination)
        score = (round(valid_score, 8), round(train_score, 8),
                 -complexity, -len(combination))
        if best_score is None or score > best_score:
            best_score, selected, selected_scores = score, combination, (
                train_score, valid_score)
    train_score, valid_score = selected_scores
    status = ("PROPOSED" if selected and valid_score >= abstain_below
              else "ABSTAIN_VALIDATION")
    return Conjunction(tuple(selected), valid_score, train_score,
                       status, considered, cut)


def majority(training_episodes) -> bool:
    labels = [observed_outcome(x) for x in training_episodes]
    if not labels:
        raise ValueError("Need labeled synthetic attempts")
    return sum(labels) > len(labels) / 2


@dataclass(frozen=True)
class Tree:
    first: Motif
    second: Motif
    leaves: tuple[bool, bool, bool, bool]
    validation_balanced: float
    considered: int

    def predict(self, row: FeatureSet) -> bool:
        idx = 2 * (self.first in row) + (self.second in row)
        return self.leaves[idx]


def fit_tree(training_episodes, validation_episodes) -> Tree:
    """Classical two-bit decision-tree baseline with the SAME evidence.

    This benchmark builds learned leaf labels and searches up to two tests
    from the same feature grammar (including joins). It is intentionally a
    stronger baseline than a constant or one-edge model. No test split access.
    """
    train = encoded(training_episodes)
    valid = encoded(validation_episodes)
    if not train or not valid:
        raise ValueError("Need train and validation")
    if min(sum(y for _, y in train), sum(not y for _, y in train),
           sum(y for _, y in valid), sum(not y for _, y in valid)) < MIN_CLASS:
        raise ValueError("Sparse classes for benchmark tree")
    atoms, _ = candidate_features(train)
    if not atoms:
        raise ValueError("No discoverable relational atoms")
    fallback = sum(y for _, y in train) > len(train) / 2
    best = None
    selected = None
    count = 0
    for i, first in enumerate(atoms):
        for second in atoms[i:]:
            count += 1
            groups = [[] for _ in range(4)]
            for fs, y in train:
                groups[2 * (first in fs) + (second in fs)].append(y)
            leaves = tuple((sum(group) > len(group) / 2) if group
                           else fallback for group in groups)
            score = balanced_accuracy(
                (y for _, y in valid),
                (leaves[2 * (first in fs) + (second in fs)] for fs, _ in valid))
            # Simpler trees win ties, never choose based on test outcomes.
            key = (round(score, 8), -len(first) - len(second),
                   -int(first != second))
            if best is None or key > best:
                best = key
                selected = (first, second, leaves, score)
    first, second, leaves, score = selected
    return Tree(first, second, leaves, score, count)
