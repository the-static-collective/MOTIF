"""MOTIF-004: counterexamples that cause a symbolic model to abstain or revise.

All episodes are purpose-built SYNTHETIC fixtures. A recorded attempt is not
proof of execution, an observed difference is not causation, and graph permits
is not real human consent. This module NEVER acts outside its immutable graphs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '002'))
from motif002 import F, World, Fact, Verb, induce, lessons, ground, possibilities


@dataclass(frozen=True)
class Attempt:
    attempt_id: str
    before: World
    operator: str
    roles: tuple[str, ...]
    observed_after: World
    provenance: str = 'SYNTHETIC_WITNESS'
    intent_recorded: bool = True


@dataclass(frozen=True)
class Scar:
    attempt_id: str
    operator: str
    roles: tuple[str, ...]
    before: World
    predicted_after: World
    observed_after: World
    missing_predicted: World
    unexpected_observed: World
    outcome: str
    context: World
    provenance: str


@dataclass(frozen=True)
class Revision:
    operator: str
    status: str
    discriminators: World
    successes: int
    no_effect: int
    divergent: int
    reason: str


class ScarJournal:
    """Append-only local fixture ledger. No persistence or authenticated witness."""

    def __init__(self):
        self._events: list[Scar] = []
        self._ids: set[str] = set()

    @property
    def events(self) -> tuple[Scar, ...]:
        return tuple(self._events)

    def record(self, attempt: Attempt, verbs: dict[str, Verb]) -> Scar:
        if attempt.provenance != 'SYNTHETIC_WITNESS':
            raise ValueError('Only explicitly synthetic witness fixtures are supported')
        if not attempt.intent_recorded or not attempt.attempt_id.strip():
            raise ValueError('An attributable synthetic attempt is required')
        if attempt.attempt_id in self._ids:
            raise ValueError('Duplicate synthetic attempt ID')
        if attempt.operator not in verbs:
            raise ValueError('Unknown candidate transformation')
        verb = verbs[attempt.operator]
        if len(attempt.roles) != len(verb.role_types):
            raise ValueError('Incorrect role binding')
        possible = {(name, roles): world for name, roles, world in
                    possibilities(attempt.before, {attempt.operator: verb})}
        if (attempt.operator, attempt.roles) not in possible:
            raise ValueError('Candidate transition not enabled in original graph')
        predicted = possible[(attempt.operator, attempt.roles)]
        observed = attempt.observed_after
        if observed == predicted:
            outcome = 'effect_confirmed_in_fixture'
        elif observed == attempt.before:
            outcome = 'no_observed_change'
        else:
            outcome = 'divergent_observation'
        scar = Scar(attempt.attempt_id, attempt.operator, attempt.roles,
                    attempt.before, predicted, observed,
                    frozenset(predicted - observed),
                    frozenset(observed - predicted), outcome,
                    extras(attempt.before, verb, attempt.roles), attempt.provenance)
        self._events.append(scar)
        self._ids.add(attempt.attempt_id)
        return scar


def extras(world: World, verb: Verb, roles: tuple[str, ...]) -> World:
    """Context facts linked to grounded roles but NOT in the existing rule.

    Convert grounded entity IDs to role-relative placeholders. Structural
    invariance is deliberately limited to a known, small graph vocabulary.
    """
    if len(set(roles)) != len(roles):
        raise ValueError('Ambiguous overlapping roles not supported by MOTIF-004')
    entity = dict((name, '?' + str(i)) for i, name in enumerate(roles))
    required = frozenset(ground(fact, roles) for fact in verb.requires)
    return frozenset(tuple(entity.get(token, token) for token in fact)
                     for fact in world if fact not in required
                     and any(token in entity for token in fact[1:]))


def revise(operator: str, events: tuple[Scar, ...], min_each: int = 3) -> Revision:
    """Conservative correlation search, not causal identification.

    Select a feature only if it occurs in EVERY successful synthetic attempt
    and NO synthetic no-effect attempt. Multiple equally discriminating
    features => abstain (avoid arbitrary, spurious conclusions).
    """
    if min_each < 1:
        raise ValueError('minimum observations must be positive')
    relevant = [event for event in events if event.operator == operator]
    successes = [x for x in relevant if x.outcome == 'effect_confirmed_in_fixture']
    failures = [x for x in relevant if x.outcome == 'no_observed_change']
    divergences = [x for x in relevant if x.outcome == 'divergent_observation']
    if divergences:
        return Revision(operator, 'ABSTAIN', frozenset(), len(successes),
                        len(failures), len(divergences),
                        'Partial/unexpected outcomes require a richer outcome model')
    if len(successes) < min_each or len(failures) < min_each:
        return Revision(operator, 'ABSTAIN', frozenset(), len(successes),
                        len(failures), 0, 'Insufficient contrasting attempts')
    candidates = set.intersection(*(set(x.context) for x in successes))
    candidates -= set.union(*(set(x.context) for x in failures))
    if len(candidates) == 1:
        return Revision(operator, 'CONTEXT_CORRELATION', frozenset(candidates),
                        len(successes), len(failures), 0,
                        'Unique observed separator; remains a hypothesis, not a cause')
    return Revision(operator, 'ABSTAIN', frozenset(), len(successes),
                    len(failures), 0,
                    'No unique separator; incompatible observations or confounding')


def forecast(revision: Revision, world: World, verb: Verb,
             roles: tuple[str, ...]) -> str:
    """Prediction for a hypothetical attempted action, with explicit abstention."""
    possible = {(name, bound) for name, bound, _ in
                possibilities(world, {verb.id: verb})}
    if (verb.id, roles) not in possible:
        return 'NOT_ENABLED'
    if revision.operator != verb.id or revision.status != 'CONTEXT_CORRELATION':
        return 'ABSTAIN'
    return ('EFFECT_HYPOTHESIS' if revision.discriminators.issubset(
            extras(world, verb, roles)) else 'NO_EFFECT_RISK')


def examples(verb: Verb, *, positive: int = 4, negative: int = 4,
             prefix: str = 'train') -> list[Attempt]:
    """Independent synthetic fixtures: success correlated with a spare part.

    Noise features vary both within and across outcome categories. The part
    relation was NOT in the positive examples used to induce MOTIF-002's verb.
    The withheld outcome is supplied separately as an observation fixture.
    """
    data = []
    for did_work, count in ((True, positive), (False, negative)):
        for i in range(count):
            owner, helper, bicycle = (f'{prefix}_owner_{did_work}_{i}',
                                      f'{prefix}_helper_{did_work}_{i}',
                                      f'{prefix}_bike_{did_work}_{i}')
            before = {F('person', owner), F('person', helper), F('bike', bicycle),
                      F('owns', owner, bicycle), F('broken', bicycle),
                      F('skill', helper, 'repair'), F('tool', helper, 'wrench'),
                      F('permits', owner, helper, bicycle),
                      F('likes', owner, 'tea' if i % 2 == 0 else 'coffee'),
                      F('condition', bicycle, 'old' if i % 2 == 0 else 'new')}
            if did_work:
                before.add(F('part', bicycle, 'brake_kit'))
            prior = frozenset(before)
            predicted = frozenset((before - {F('broken', bicycle)}) |
                                  {F('usable', bicycle)})
            data.append(Attempt(f'{prefix}:{int(did_work)}:{i}', prior,
                                verb.id, (bicycle, owner, helper),
                                predicted if did_work else prior))
    return data


def run_demo() -> dict:
    verbs = induce(lessons())
    targets = [v for v in verbs.values() if F('usable', '?0') in v.adds]
    if len(targets) != 1:
        raise ValueError('Synthetic fixture requires exactly one repair-like verb')
    verb = targets[0]
    train = examples(verb)
    evaluation = examples(verb, positive=2, negative=2, prefix='holdout')
    journal = ScarJournal()
    for case in train:
        journal.record(case, verbs)
    revision = revise(verb.id, journal.events)
    baseline_correct = 0
    learned_correct = 0
    abstentions = 0
    predictions = []
    for case in evaluation:
        truth = 'EFFECT_HYPOTHESIS' if case.observed_after != case.before else 'NO_EFFECT_RISK'
        baseline_correct += truth == 'EFFECT_HYPOTHESIS'  # naive MOTIF-002: predicts the edit
        guess = forecast(revision, case.before, verb, case.roles)
        abstentions += guess == 'ABSTAIN'
        learned_correct += guess == truth
        predictions.append({'id': case.attempt_id, 'prediction': guess, 'observed': truth})
    return {
        'experiment': 'MOTIF-004', 'scope': 'synthetic counterfactual only',
        'induced_operator': verb.id,
        'train_attempts': len(train), 'held_out_attempts': len(evaluation),
        'scar_no_change': sum(x.outcome == 'no_observed_change' for x in journal.events),
        'revision': {'status': revision.status, 'features': sorted(revision.discriminators),
                     'supports_success': revision.successes, 'supports_no_effect': revision.no_effect},
        'naive_correct': baseline_correct, 'revised_correct': learned_correct,
        'abstentions': abstentions, 'heldout_predictions': predictions,
        'training_journal_unchanged': len(journal.events) == len(train),
    }


if __name__ == '__main__':
    print(json.dumps(run_demo(), indent=2))
