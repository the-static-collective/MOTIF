"""WITNESS-CHAIN-001 — query-relative recursive witness scrutiny (synthetic).

All identity and root claims are unverified. The only symmetry-breaking
reference is an explicitly *assumed* synthetic fixture receipt, which can be
corrupted. The engine never performs external queries or promotes truth claims.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from math import exp, log, log2
from random import Random
from typing import Iterable

CHANNELS = ('primary', 'audit', 'anchor')
READINGS = ('amber', 'blue')
ACCURACY = {'primary': .85, 'audit': .90, 'anchor': .92}
HYPOTHESES = tuple(product((0, 1), repeat=3))


def flip(x: str) -> str:
    if x not in READINGS:
        raise ValueError('invalid reading')
    return 'blue' if x == 'amber' else 'amber'


def name(bits: tuple[int, ...]) -> str:
    return ''.join(str(i) for i in bits)


def _likelihood(bits: tuple[int, ...], readings: tuple[str | None, ...],
                truth: str | None = None) -> float:
    if bits not in HYPOTHESES or len(readings) != 3 or any(
        r is not None and r not in READINGS for r in readings
    ) or truth is not None and truth not in READINGS:
        raise ValueError('invalid hypothesis or readings')
    def conditional(t: str) -> float:
        p = 1.0
        for channel, inverted, reading in zip(CHANNELS, bits, readings):
            if reading is None:
                continue
            wanted = flip(t) if inverted else t
            p *= ACCURACY[channel] if reading == wanted else (1 - ACCURACY[channel])
        return p
    if truth is not None:
        return conditional(truth)
    return (conditional('amber') + conditional('blue')) / 2


@dataclass(frozen=True)
class Witness:
    """Claimed dependency edge. A parent chain is NOT verified provenance."""
    id: str
    channel: str
    reading: str
    asserted_root: str
    parents: tuple[str, ...] = ()

    def __post_init__(self):
        if (not self.id or self.channel not in CHANNELS
            or self.reading not in READINGS or not self.asserted_root
            or len(set(self.parents)) != len(self.parents)):
            raise ValueError('invalid witness record')


@dataclass(frozen=True)
class Event:
    id: str
    witnesses: tuple[Witness, ...]

    def __post_init__(self):
        if not self.id or not self.witnesses:
            raise ValueError('event needs id and witnesses')


@dataclass(frozen=True)
class Collapsed:
    event: str
    status: str
    readings: tuple[str | None, str | None, str | None]
    root_claims: tuple[tuple[str, tuple[str, ...]], ...]
    copies_collapsed: int
    authenticated: bool = False


def collapse(event: Event) -> Collapsed:
    """Topologically trace declared parents, reject cycles and unknown parents.

    Only explicit parent edges or *identical asserted roots* establish a known
    relationship. Forged unrelated roots are deliberately undetectable here.
    """
    rows = {w.id: w for w in event.witnesses}
    if len(rows) != len(event.witnesses):
        raise ValueError('duplicate witness id')
    roots: dict[str, frozenset[str]] = {}
    visiting: set[str] = set()
    def lineage(key: str) -> frozenset[str]:
        if key not in rows:
            raise ValueError('unknown witness parent')
        if key in visiting:
            raise ValueError('provenance cycle')
        if key in roots:
            return roots[key]
        visiting.add(key)
        w = rows[key]
        result = frozenset().union(*(lineage(k) for k in w.parents)) if w.parents else frozenset((w.asserted_root,))
        visiting.remove(key)
        roots[key] = result
        return result
    for w in event.witnesses:
        lineage(w.id)
    observed = []
    summary = []
    for channel in CHANNELS:
        group = [w for w in event.witnesses if w.channel == channel]
        channel_roots = frozenset().union(*(roots[w.id] for w in group))
        summary.append((channel, tuple(sorted(channel_roots))))
        if not group:
            observed.append(None)
        elif len(channel_roots) != 1:
            return Collapsed(event.id, 'HOLD_MULTIPLE_ORIGINS_PER_CHANNEL', (None,)*3,
                             tuple(summary), 0)
        elif len({w.reading for w in group}) > 1:
            return Collapsed(event.id, 'HOLD_CONFLICTING_COPIES', (None,)*3,
                             tuple(summary), 0)
        else:
            observed.append(group[0].reading)
    nonempty = [set(v) for _, v in summary if v]
    if any(a & b for i, a in enumerate(nonempty) for b in nonempty[i+1:]):
        return Collapsed(event.id, 'HOLD_SHARED_UPSTREAM_ROOT', (None,)*3,
                         tuple(summary), 0)
    copied = len(event.witnesses) - sum(bool(v) for v in observed)
    return Collapsed(event.id, 'ACCEPTED' if all(observed) else 'ACCEPTED_PARTIAL',
                     tuple(observed), tuple(summary), copied)


@dataclass(frozen=True)
class TruthReceipt:
    event: str
    truth: str
    fixture_reference: str
    # This is a declaration. It does NOT authenticate any external witness.
    fixture_attested: bool = True

    def __post_init__(self):
        if not self.event or self.truth not in READINGS or not self.fixture_reference or not self.fixture_attested:
            raise ValueError('only explicit synthetic reference assumptions supported')


@dataclass(frozen=True)
class State:
    """Immutable Bayesian evidence state; all updating is re-evaluated exactly."""
    accepted: tuple[Collapsed, ...] = ()
    truth_receipts: tuple[TruthReceipt, ...] = ()
    seen: frozenset[str] = frozenset()
    holds: tuple[dict, ...] = ()

    def add(self, event: Event) -> State:
        if event.id in self.seen:
            raise ValueError('event replay')
        result = collapse(event)
        if not result.status.startswith('ACCEPTED'):
            return State(self.accepted, self.truth_receipts, self.seen | {event.id},
                         self.holds + ({'event': event.id, 'status': result.status},))
        # A provenance root identifies a *datum's origin*, not a sensor model.
        # Reusing that datum in a new event does not make a new independent sample.
        old_roots = {root for earlier in self.accepted for _, group in earlier.root_claims
                     for root in group}
        new_roots = {root for _, group in result.root_claims for root in group}
        if old_roots & new_roots:
            return State(self.accepted, self.truth_receipts, self.seen | {event.id},
                         self.holds + ({'event': event.id,
                                        'status': 'HOLD_REUSED_UPSTREAM_DATUM',
                                        'overlap': tuple(sorted(old_roots & new_roots))},))
        return State(self.accepted + (result,), self.truth_receipts,
                     self.seen | {event.id}, self.holds)

    def verify(self, receipt: TruthReceipt) -> State:
        if (receipt.event not in {e.event for e in self.accepted}
                or receipt.event in {r.event for r in self.truth_receipts}):
            raise ValueError('truth receipt requires previously observed, unverified event')
        return State(self.accepted, self.truth_receipts + (receipt,), self.seen, self.holds)

    def probabilities(self) -> dict[str, float]:
        known = {r.event: r.truth for r in self.truth_receipts}
        weights = []
        for hypothesis in HYPOTHESES:
            score = 0.0
            for event in self.accepted:
                score += log(_likelihood(hypothesis, event.readings, known.get(event.event)))
            weights.append(score)
        biggest = max(weights)
        exp_weights = [exp(v - biggest) for v in weights]
        z = sum(exp_weights)
        return {name(h): w/z for h, w in zip(HYPOTHESES, exp_weights)}

    def decision(self, question: str, confidence: float = .95) -> dict:
        """Query-relative stopping: relative alignment differs from absolute polarity.

        All accepted classifications remain hypotheses (I), never F.
        """
        if question not in {'absolute_polarity', 'primary_audit_alignment'} or not .5 < confidence < 1:
            raise ValueError('unknown question or confidence level')
        posterior = self.probabilities()
        if question == 'absolute_polarity':
            ranking = sorted(posterior.items(), key=lambda x: (-x[1], x[0]))
            if not self.truth_receipts:
                status = 'HOLD_GLOBAL_FLIP_SYMMETRY'
            else:
                status = 'I_CONDITIONAL_ON_FIXTURE_REFERENCE' if ranking[0][1] >= confidence else 'HOLD_INSUFFICIENT_REFERENCE_EVIDENCE'
            return {'question': question, 'status': status,
                    'candidate': ranking[0][0], 'confidence': ranking[0][1],
                    'reference_count': len(self.truth_receipts),
                    'authenticity_verified': False}
        same = sum(p for h, p in posterior.items() if h[0] == h[1])
        label, probability = ('same', same) if same >= .5 else ('opposite', 1-same)
        return {'question': question,
                'status': 'I_RELATIVE_MODEL_ONLY' if probability >= confidence else 'HOLD_RELATIVE_AMBIGUITY',
                'candidate': label, 'confidence': probability,
                'reference_count': len(self.truth_receipts),
                'authenticity_verified': False}


@dataclass(frozen=True)
class Challenge:
    """Explicit reopening of an assumed reference with immutable before/after."""
    before: State
    after: State
    receipt: dict


def challenge_reference(state: State, event: str, reason: str) -> Challenge:
    if not event or not reason or event not in {r.event for r in state.truth_receipts}:
        raise ValueError('challenge requires a present reference and a reason')
    reopened = tuple(r for r in state.truth_receipts if r.event != event)
    after = State(state.accepted, reopened, state.seen, state.holds)
    return Challenge(state, after, {
        'operation': 'reopen_synthetic_reference',
        'event': event,
        'reason': reason,
        'old_model_status': state.decision('absolute_polarity')['status'],
        'new_model_status': after.decision('absolute_polarity')['status'],
        'old_truth_count': len(state.truth_receipts),
        'new_truth_count': len(after.truth_receipts),
        'old_reference_authority': 'fixture_assumption_not_authentication',
    })


def entropy(values: Iterable[float]) -> float:
    return -sum(p*log2(p) for p in values if p > 0)


def expected_gain(state: State, action: str, event_id: str | None = None) -> float:
    """Classical expected entropy reduction. No hidden truth given to planner."""
    posterior = state.probabilities()
    prior = entropy(posterior.values())
    outcomes: list[tuple[float, tuple[float,...]]] = []
    if action == 'NEW_TRIPLET':
        for readings in product(READINGS, repeat=3):
            rows = [posterior[name(h)] * _likelihood(h, readings) for h in HYPOTHESES]
            outcomes.append((sum(rows), tuple(rows)))
    elif action == 'VERIFY_EXISTING':
        if not event_id:
            raise ValueError('verification requires event id')
        event = next((e for e in state.accepted if e.event == event_id), None)
        if event is None or event_id in {r.event for r in state.truth_receipts}:
            raise ValueError('no unverified event')
        for truth in READINGS:
            rows = []
            for h in HYPOTHESES:
                p_h = posterior[name(h)]
                marginal = _likelihood(h, event.readings)
                # Bayes P(truth | readings,h) with 50/50 truth prior.
                rows.append(p_h * .5 * _likelihood(h, event.readings, truth) / marginal)
            outcomes.append((sum(rows), tuple(rows)))
    else:
        raise ValueError('unknown inquiry type')
    ig = prior - sum(p * entropy(x / p for x in row) for p, row in outcomes if p > 0)
    return max(0.0, ig)


@dataclass(frozen=True)
class Inquiry:
    status: str
    action: str | None
    event: str | None
    information_bits: float
    cost: int
    real_authority: bool = False


def propose(state: State, allowed: frozenset[str], budget: int,
            costs: dict[str,int] | None = None) -> Inquiry:
    """Permitted inquiry nominations; never dispatch an actual check."""
    if budget < 0 or not allowed <= {'NEW_TRIPLET','VERIFY_EXISTING'}:
        raise ValueError('invalid budget or permission')
    costs = costs or {'NEW_TRIPLET': 1, 'VERIFY_EXISTING': 4}
    if any(k not in {'NEW_TRIPLET','VERIFY_EXISTING'} or type(v) is not int or v < 1
           for k, v in costs.items()):
        raise ValueError('invalid price schedule')
    candidates = []
    for action in sorted(allowed):
        if action not in costs or costs[action] > budget:
            continue
        ids = [None] if action == 'NEW_TRIPLET' else [e.event for e in state.accepted
                           if e.event not in {r.event for r in state.truth_receipts}]
        for event in ids:
            gain = expected_gain(state, action, event)
            candidates.append((gain/costs[action], gain, action, event, costs[action]))
    if not candidates:
        return Inquiry('HOLD_NOT_ALLOWED_OR_AFFORDABLE', None, None, 0.0, 0)
    score, gain, action, event, cost = max(candidates, key=lambda v: (v[0], v[1], v[2], v[3] or ''))
    if gain < 1e-9:
        return Inquiry('HOLD_NO_INFORMATION', None, None, 0.0, 0)
    return Inquiry('I_SYNTHETIC_INQUIRY_PROPOSAL', action, event, gain, cost)


def synthetic_event(hypothesis: tuple[int, int, int], key: str,
                    rng: Random) -> tuple[Event, str]:
    """Generator's hidden truth is NOT part of returned witness event."""
    if hypothesis not in HYPOTHESES:
        raise ValueError('unknown simulator mechanism')
    truth = READINGS[rng.randrange(2)]
    witnesses = []
    for channel, inversion in zip(CHANNELS, hypothesis):
        expected = flip(truth) if inversion else truth
        reading = expected if rng.random() < ACCURACY[channel] else flip(expected)
        witnesses.append(Witness(f'{key}:{channel}', channel, reading, f'{channel}:{key}'))
    return Event(key, tuple(witnesses)), truth


def synthetic_cases(hypothesis: tuple[int,int,int], seed: int, size: int) -> tuple[tuple[Event,str], ...]:
    if size < 1:
        raise ValueError('size must be positive')
    rng = Random(int.from_bytes(sha256(f'witnesschain001:{seed}:{name(hypothesis)}'.encode()).digest()[:8], 'big'))
    return tuple(synthetic_event(hypothesis, f's{seed}:e{i}', rng) for i in range(size))


def from_probe_observation(probe) -> Event:
    """A previous fixture-attested anchor becomes a FALLIBLE witness here.

    The previous document's attestation is not treated as certified ground truth.
    """
    witnesses = [Witness(probe.event+':p', 'primary', probe.primary, probe.primary_root),
                 Witness(probe.event+':a', 'audit', probe.audit, probe.audit_root)]
    if probe.anchor is not None:
        witnesses.append(Witness(probe.event+':r','anchor',probe.anchor,
                                 'prior-fixture-anchor-claim'))
    return Event(probe.event, tuple(witnesses))


def fir_receipt(state: State) -> dict:
    """A finite evidence tally is F_LOCAL; causal/model inference remains I."""
    from pathlib import Path
    import sys
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'fir001'))
    sys.path.insert(0, str(root / 'mathal001'))
    from fir import Claim, FIRWorld, Warrant
    from mathal import Program, Step, execute
    snapshot = repr((state.accepted, state.truth_receipts, state.holds))
    scope = 'synthetic-ledger:' + sha256(snapshot.encode()).hexdigest()[:20]
    hypothesis = Claim('Most probable absolute witness-polarity mechanism', scope)
    count = Claim(f'Finite ledger has {len(state.accepted)} accepted events and '
                  f'{len(state.truth_receipts)} declared synthetic truth receipts', scope)
    fir = FIRWorld('synthetic finite witness ledger', 'fallible source ancestry')
    program = Program('do-not-promote-interpretation',(
        Step('propose',hypothesis),
        Step('propose',count),
        Step('admit',count,Warrant('finite_computation',
                     'recounted exact finite ledger rows; no authenticity checking',scope))
    ),fir.carrier,fir.decoder)
    run = execute(fir,program)
    if not run.applied or hypothesis in run.world.facts or count not in run.world.facts:
        raise AssertionError('mathematical admission boundary violated')
    return {'hypothesis_role':'I','ledger_count_role':'F_LOCAL','scope':scope,
            'admitted_model':False,'receipts':run.receipts}


def investigate(state: State, question: str, allowed: frozenset[str],
                budget: int, confidence: float = .95) -> dict:
    """Query-relative stopping, then budget-aware hypothetical probe nomination."""
    decision = state.decision(question, confidence)
    if decision['status'].startswith('I_'):
        return {'status':'STOP_QUERY_SUFFICIENT_UNDER_MODEL',
                'decision':decision,'inquiry':None,'real_actions':0}
    next_step = propose(state, allowed, budget)
    return {'status':next_step.status,'decision':decision,
            'inquiry':next_step,'real_actions':0}


def demonstration() -> dict:
    truth_h = (1,1,1)
    pairs = synthetic_cases(truth_h, 7, 100)
    state = State()
    for event, _ in pairs:
        state = state.add(event)
    before = state.decision('absolute_polarity')
    alignment = state.decision('primary_audit_alignment')
    nominated = propose(state, frozenset({'NEW_TRIPLET', 'VERIFY_EXISTING'}), 4)
    for event, truth in pairs[:3]:
        state = state.verify(TruthReceipt(event.id, truth, 'synthetic-oracle-only'))
    corrected = state.decision('absolute_polarity')
    corrupted = State()
    for event, _ in pairs:
        corrupted = corrupted.add(event)
    for event, truth in pairs[:3]:
        corrupted = corrupted.verify(TruthReceipt(event.id, flip(truth), 'tampered-fixture'))
    damaged = corrupted.decision('absolute_polarity')
    reconsidered = state
    for e,_ in pairs[:3]:
        reconsidered = challenge_reference(reconsidered, e.id,
                         'reopen the synthetic reference premise').after
    return {
        'experiment':'WITNESS-CHAIN-001',
        'observations':len(pairs),
        'unreferenced_absolute':before,
        'unreferenced_relative':alignment,
        'nominated_inquiry':{'status':nominated.status,'type':nominated.action,
                             'information_bits':round(nominated.information_bits,5),
                             'cost':nominated.cost},
        'truth_assumption_result':corrected,
        'tampered_truth_assumption':damaged,
        'after_reopening_reference':reconsidered.decision('absolute_polarity'),
        'synthetic_truth':name(truth_h),
        'fir':{k:v for k,v in fir_receipt(state).items() if k != 'receipts'},
        'real_queries':0,'automated_code_changes':0,
        'general_status':'HOLD_REAL_WORLD_SOURCE_AUTHENTICITY_UNPROVEN',
    }


if __name__ == '__main__':
    import json
    print(json.dumps(demonstration(), indent=2, sort_keys=True))
