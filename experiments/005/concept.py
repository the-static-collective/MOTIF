"""MOTIF-005: induce a new *composite relational predicate* from scarred events.

This is conservative symbolic concept induction, not discovery of an entirely
unknown physical relation, not neural learning, and not causal identification.
No outside operations, permission inference, or modifications to observation
graphs are possible. Python 3.10+, standard library.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "002"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "004"))
from motif002 import F, Verb, World, Fact, induce, lessons, possibilities
from scar import Attempt, Scar, ScarJournal

Motif = tuple[Fact, ...]


def canonical(facts: tuple[Fact, ...], roles: tuple[str, ...]) -> Motif:
    """Replace concrete identities with role variables and joined witnesses.

    A non-role symbol is treated as an existential witness, NEVER assumed to
    be a known constant. This is an explicit simplifying design choice.
    """
    if len(roles) != len(set(roles)):
        raise ValueError("Overlapping grounded roles are ambiguous")
    mapping = {value: f"?{i}" for i, value in enumerate(roles)}
    next_witness = 0
    result = []
    for fact in sorted(facts):
        row = [fact[0]]
        for token in fact[1:]:
            if token not in mapping:
                mapping[token] = f"?e{next_witness}"
                next_witness += 1
            row.append(mapping[token])
        result.append(tuple(row))
    return tuple(sorted(result))


def candidate_motifs(world: World, roles: tuple[str, ...]) -> frozenset[Motif]:
    """Enumerate 1-edge predicates and connected 2-edge existential joins.

    Every edge must touch at least one operator role. A two-edge motif must
    connect *two different roles* via an identical non-role witness.
    Neither a relation name nor the eventual learned pattern is supplied.
    """
    role_ids = set(roles)
    connected = sorted(fact for fact in world
                       if any(token in role_ids for token in fact[1:]))
    discovered = set()
    for fact in connected:
        discovered.add(canonical((fact,), roles))
    for a, b in combinations(connected, 2):
        ar = set(a[1:]) & role_ids
        br = set(b[1:]) & role_ids
        shared = (set(a[1:]) & set(b[1:])) - role_ids
        if ar and br and len(ar | br) >= 2 and shared:
            discovered.add(canonical((a, b), roles))
    return frozenset(discovered)


def holds(motif: Motif, world: World, roles: tuple[str, ...]) -> bool:
    """Exact graph substructure matching with shared existential witnesses."""
    if not motif or len(roles) != len(set(roles)):
        return False
    bound = {f"?{i}": value for i, value in enumerate(roles)}
    facts = sorted(world)

    def match_one(pattern: Fact, actual: Fact, bindings: dict[str, str]):
        if len(pattern) != len(actual) or pattern[0] != actual[0]:
            return None
        updated = dict(bindings)
        for symbol, item in zip(pattern[1:], actual[1:]):
            if symbol.startswith("?"):
                if symbol in updated and updated[symbol] != item:
                    return None
                updated[symbol] = item
            elif symbol != item:
                return None
        return updated

    def search(index: int, bindings: dict[str, str]) -> bool:
        if index == len(motif):
            return True
        for fact in facts:
            next_bindings = match_one(motif[index], fact, bindings)
            if next_bindings is not None and search(index + 1, next_bindings):
                return True
        return False

    return search(0, bound)


@dataclass(frozen=True)
class Concept:
    id: str
    status: str
    definition: Motif
    support_success: int
    support_failure: int
    alternatives: int
    best_single_accuracy: float
    explanation: str

    def data(self):
        return dict(id=self.id, status=self.status,
                    definition=[list(f) for f in self.definition],
                    support_success=self.support_success,
                    support_failure=self.support_failure,
                    alternatives=self.alternatives,
                    best_single_accuracy=self.best_single_accuracy,
                    explanation=self.explanation)


def discover(events: tuple[Scar, ...], operator: str,
             minimum_each: int = 3) -> Concept:
    """Propose only one unambiguous, two-edge joint concept.

    The derived concept isn't admitted into any real ontology. A perfect
    discriminator in deliberately structured observations can still be
    confounded: this is evidence of predictive structure, NOT a cause.
    """
    if minimum_each < 1:
        raise ValueError("minimum_each must be >= 1")
    relevant = [x for x in events if x.operator == operator]
    good = [x for x in relevant if x.outcome == "effect_confirmed_in_fixture"]
    bad = [x for x in relevant if x.outcome == "no_observed_change"]
    other = [x for x in relevant if x.outcome == "divergent_observation"]
    def held():
        return Concept("", "ABSTAIN", (), len(good), len(bad), 0, 0.0,
                       "insufficient, inconsistent or divergent examples")
    if len(good) < minimum_each or len(bad) < minimum_each or other:
        return held()
    possible = set()
    for event in good:
        possible.update(candidate_motifs(event.before, event.roles))

    def hits(pattern, rows):
        return sum(holds(pattern, x.before, x.roles) for x in rows)

    scores = []
    for pattern in sorted(possible):
        tp, fp = hits(pattern, good), hits(pattern, bad)
        # Equal-class importance is intentional, regardless of class imbalance.
        balanced = 0.5 * (tp / len(good) + (len(bad) - fp) / len(bad))
        scores.append((pattern, tp, fp, balanced))
    single = [x for x in scores if len(x[0]) == 1]
    best_single = max((x[3] for x in single), default=0.5)
    perfect = [x for x in scores if x[1] == len(good) and x[2] == 0]
    if len(perfect) > 1:
        return Concept("", "ABSTAIN_AMBIGUOUS", (), len(good), len(bad),
                       len(perfect), best_single,
                       "several perfect hypotheses fit the same synthetic evidence")
    if not perfect:
        return Concept("", "ABSTAIN_NO_SEPARATION", (), len(good), len(bad),
                       0, best_single,
                       "no exact one-or-two-edge separator in the selected grammar")
    pattern = perfect[0][0]
    if len(pattern) != 2:
        return Concept("", "NO_NEW_COMPOSITE_CONCEPT", (), len(good), len(bad),
                       1, best_single,
                       "existing single-edge representation already separates outcomes")
    identifier = "concept-" + sha256(json.dumps(pattern).encode()).hexdigest()[:12]
    return Concept(identifier, "PROPOSED", pattern, len(good), len(bad),
                   1, best_single,
                   "an anonymous two-edge existential join; provisional, not causal")


def concept_projection(model: Concept, world: World,
                       roles: tuple[str, ...]) -> frozenset[Fact]:
    """Ephemeral, inferential overlay; NEVER writes to observed \`world\`."""
    if model.status != "PROPOSED":
        return frozenset()
    if holds(model.definition, world, roles):
        return frozenset({F(model.id, *roles)})
    return frozenset()


def guarded_moves(world: World, verb: Verb, model: Concept):
    """Filter already-permitted *synthetic* actions by a discovered concept.

    The graph's \`permits\` token is a toy precondition, NOT authentication.
    No new actions are executed or authorized, only hypothetical successors.
    """
    if model.status != "PROPOSED":
        return ()
    rows = []
    for operator, roles, after in possibilities(world, {verb.id: verb}):
        if concept_projection(model, world, roles):
            rows.append((operator, roles, after))
    return tuple(rows)


def repair_operator(verbs: dict[str, Verb]) -> Verb:
    """Fixture selector, not part of the discovery algorithm."""
    matched = [verb for verb in verbs.values() if F("usable", "?0") in verb.adds]
    if len(matched) != 1:
        raise ValueError("Expected exactly one synthetic repair operator")
    return matched[0]


def examples(verb: Verb, positive=6, negative=12, namespace="train",
             confound=False) -> list[Attempt]:
    """Build a controlled relational join experiment with hard negatives.

    All synthetic examples contain 'carries' and 'fits' somewhere. Only
    positive examples connect the *same* intermediate part to repairer/bike.
    Naming, irrelevant graph attributes, and ID assignments vary. Some
    hard negatives contain both useful-looking edges, but no valid join.
    """
    cases = []
    for success, count in ((True, positive), (False, negative)):
        for i in range(count):
            mark = f"{namespace}_{int(success)}_{i}"
            bicycle, owner, worker = f"b_{mark}", f"o_{mark}", f"w_{mark}"
            part_a, part_b = f"part_A_{mark}", f"part_B_{mark}"
            before = {
                F("bike", bicycle), F("person", owner), F("person", worker),
                F("broken", bicycle), F("owns", owner, bicycle),
                F("skill", worker, "repair"), F("tool", worker, "wrench"),
                F("permits", owner, worker, bicycle),
                F("likes", owner, "tea" if i % 2 else "coffee"),
                F("color", bicycle, "blue" if i % 3 == 0 else "green"),
                # Unconnected decoys guarantee both relation names occur,
                # but NEVER with the same witnessed part.
                F("carries", worker, f"decoy_c_{mark}"),
                F("fits", f"decoy_f_{mark}", bicycle),
            }
            if success:
                before |= {F("carries", worker, part_a),
                           F("fits", part_a, bicycle)}
                if confound:
                    before.add(F("badge", worker, "gold"))
            else:
                kind = i % 4
                if kind in (0, 1):
                    before.add(F("carries", worker, part_a))
                if kind in (0, 2):
                    before.add(F("fits", part_b, bicycle))
            prior = frozenset(before)
            outcome = (frozenset((before - {F("broken", bicycle)}) |
                                 {F("usable", bicycle)}) if success else prior)
            cases.append(Attempt(f"{namespace}:{int(success)}:{i}", prior,
                                 verb.id, (bicycle, owner, worker), outcome))
    return cases


def labeled(events: list[Attempt], verbs: dict[str, Verb]) -> tuple[Scar, ...]:
    journal = ScarJournal()
    for episode in events:
        journal.record(episode, verbs)
    return journal.events


def run_demo():
    verbs = induce(lessons())
    verb = repair_operator(verbs)
    train = labeled(examples(verb), verbs)
    concept = discover(train, verb.id)
    test = labeled(examples(verb, positive=4, negative=8,
                            namespace="heldout"), verbs)
    correct = 0
    absent = 0
    for scar in test:
        guess = bool(concept_projection(concept, scar.before, scar.roles))
        actual = scar.outcome == "effect_confirmed_in_fixture"
        correct += guess == actual
        absent += not guess
    # Unique invented relation is an *inference* only, never an observation.
    mismatched = next(s for s in test if s.outcome == "no_observed_change")
    matched = next(s for s in test if s.outcome == "effect_confirmed_in_fixture")
    return {
        "experiment": "MOTIF-005", "scope": "synthetic only",
        "train_episodes": len(train), "heldout_episodes": len(test),
        "concept": concept.data(),
        "correct_heldout": correct,
        "single_edge_baseline_balanced_accuracy": concept.best_single_accuracy,
        "join_mismatch_rejected": not bool(concept_projection(
            concept, mismatched.before, mismatched.roles)),
        "joined_case_admitted_to_simulation": bool(guarded_moves(
            matched.before, verb, concept)),
        "unjoined_case_held_from_simulation": not bool(guarded_moves(
            mismatched.before, verb, concept)),
        "observed_world_unchanged": all(
            F(concept.id, *s.roles) not in s.before for s in test)
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
