"""MOTIF PROVENANCE-PROBE-001: fallible witness families + conditional anchor inquiry.

All phenomena below are synthetic. Claimed root identifiers are NOT authenticated.
The anchor is trusted only by a declared experimental assumption, never by a
cryptographic or real-world verification. No external query is ever executed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from itertools import product
from math import exp, log, log2
from pathlib import Path
from random import Random
from typing import Iterable
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'fir001'))
sys.path.insert(0, str(ROOT / 'mathal001'))
from fir import Claim, FIRWorld, Warrant
from mathal import Program, Step, execute

# Four polarities, with fixed *known* accuracy in this deliberately finite world.
# A balanced latent truth makes CLEAN and BOTH observationally indistinguishable
# without a trusted anchor. The same applies to PRIMARY and AUDIT inversions.
HYPOTHESES = ('CLEAN', 'PRIMARY_INVERTED', 'AUDIT_INVERTED', 'BOTH_INVERTED')
FLIPS = {'CLEAN': (False, False), 'PRIMARY_INVERTED': (True, False),
         'AUDIT_INVERTED': (False, True), 'BOTH_INVERTED': (True, True)}
PRIMARY_ACCURACY = 0.85
AUDIT_ACCURACY = 0.90
READINGS = ('amber', 'blue')


def flip(value: str) -> str:
    if value not in READINGS:
        raise ValueError('unknown reading')
    return 'blue' if value == 'amber' else 'amber'


def _reading_probability(reading: str, truth: str, accuracy: float, inverted: bool) -> float:
    expected = flip(truth) if inverted else truth
    return accuracy if reading == expected else (1.0 - accuracy)


def likelihood(hypothesis: str, primary: str, audit: str, anchor: str | None = None) -> float:
    """Marginalize hidden truth when anchor absent, condition when present.

    This is a toy likelihood, not a universal probabilistic model of witnesshood.
    """
    if hypothesis not in FLIPS or primary not in READINGS or audit not in READINGS:
        raise ValueError('invalid hypothesis or observation')
    if anchor is not None and anchor not in READINGS:
        raise ValueError('invalid anchor')
    pflip, aflip = FLIPS[hypothesis]
    truths = (anchor,) if anchor is not None else READINGS
    return sum((1.0 if anchor is not None else 0.5) *
               _reading_probability(primary, t, PRIMARY_ACCURACY, pflip) *
               _reading_probability(audit, t, AUDIT_ACCURACY, aflip)
               for t in truths)


@dataclass(frozen=True)
class SourceClaim:
    """One message. source/root strings are claims, not independently verified."""
    report_id: str
    origin: str
    asserted_root: str
    reading: str

    def __post_init__(self):
        if not self.report_id or not self.origin or not self.asserted_root or self.reading not in READINGS:
            raise ValueError('ill-typed source claim')


@dataclass(frozen=True)
class Collapse:
    groups: tuple[tuple[str, str], ...]
    forwarded: int
    conflicts: tuple[str, ...]
    verified_independence: bool = False


def collapse_forwarded(reports: Iterable[SourceClaim]) -> Collapse:
    """Deduplicate by *asserted* root; never call distinct names independence.

    A root making conflicting reports is flagged, not silently majority-voted.
    """
    seen_ids: set[str] = set()
    groups: dict[str, set[str]] = {}
    count = 0
    for r in reports:
        if r.report_id in seen_ids:
            raise ValueError('duplicate report id')
        seen_ids.add(r.report_id)
        count += 1
        groups.setdefault(r.asserted_root, set()).add(r.reading)
    conflicts = tuple(sorted(k for k, values in groups.items() if len(values) > 1))
    clean_groups = tuple(sorted((k, next(iter(v))) for k, v in groups.items() if len(v) == 1))
    return Collapse(clean_groups, count - len(groups), conflicts, False)


def naive_majority(reports: Iterable[SourceClaim], *, deduplicate: bool = False) -> str | None:
    items = tuple(reports)
    if deduplicate:
        summary = collapse_forwarded(items)
        if summary.conflicts:
            return None
        readings = [r for _, r in summary.groups]
    else:
        readings = [r.reading for r in items]
    a, b = readings.count('amber'), readings.count('blue')
    return 'amber' if a > b else ('blue' if b > a else None)


@dataclass(frozen=True)
class Observation:
    event: str
    primary: str
    audit: str
    primary_root: str = 'primary-root'
    audit_root: str = 'audit-root'
    anchor: str | None = None
    # A synthetic fixture-level attestation, not a real-world authority proof.
    fixture_anchor_attested: bool = False

    def __post_init__(self):
        if not self.event or self.primary not in READINGS or self.audit not in READINGS:
            raise ValueError('missing event/readings')
        if not self.primary_root or not self.audit_root:
            raise ValueError('missing lineage assertions')
        if self.anchor is not None and self.anchor not in READINGS:
            raise ValueError('invalid anchor reading')
        if (self.anchor is not None) != self.fixture_anchor_attested:
            raise ValueError('anchor must have explicit fixture attestation')


@dataclass(frozen=True)
class Belief:
    """Immutable finite Bayes update; stores log weights and event receipts."""
    log_weights: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    seen: frozenset[str] = frozenset()
    pair_count: int = 0
    anchor_count: int = 0
    held_count: int = 0
    receipts: tuple[dict, ...] = ()

    def probabilities(self) -> dict[str, float]:
        shift = max(self.log_weights)
        weights = [exp(x - shift) for x in self.log_weights]
        total = sum(weights)
        return dict(zip(HYPOTHESES, (v / total for v in weights)))

    def ingest(self, obs: Observation) -> Belief:
        if obs.event in self.seen:
            raise ValueError('one event cannot be counted twice')
        seen = self.seen | {obs.event}
        if obs.primary_root == obs.audit_root:
            return Belief(self.log_weights, seen, self.pair_count,
                          self.anchor_count, self.held_count + 1,
                          self.receipts + ({'event': obs.event, 'status': 'HOLD_SHARED_ASSERTED_ROOT',
                                            'independence_verified': False},))
        logs = tuple(w + log(likelihood(h, obs.primary, obs.audit, obs.anchor))
                     for h, w in zip(HYPOTHESES, self.log_weights))
        return Belief(logs, seen, self.pair_count + 1,
                      self.anchor_count + int(obs.anchor is not None), self.held_count,
                      self.receipts + ({'event': obs.event,
                                        'status': 'CONDITIONAL_ANCHOR' if obs.anchor is not None else 'PAIR_ONLY',
                                        'primary_root_claim': obs.primary_root,
                                        'audit_root_claim': obs.audit_root,
                                        'fixture_anchor_assumption': obs.anchor is not None,
                                        'independence_verified': False},))

    def classification(self) -> dict:
        probs = self.probabilities()
        winner = max(probs, key=probs.get)
        # Recognize exact symmetry that *cannot* be broken by additional pairs.
        ambiguity = 'NO_ANCHOR_SYMMETRY' if self.anchor_count == 0 else 'MODEL_CONDITIONAL_ONLY'
        return {'leading_model': winner, 'probability': probs[winner],
                'status': 'I_MODEL_CONDITIONAL', 'identifiability': ambiguity,
                'pair_count': self.pair_count, 'anchor_count': self.anchor_count,
                'verified_independence': False}



def ingest_decoder_witness_pairs(pairs: Iterable) -> Belief:
    """Read-only adaptation of DECODER-INTEGRITY-001's WitnessPair surface.

    Missing audit and asserted same-root pairs are held, never converted to
    fictitious agreement. The adapter does NOT receive Episode or hidden label.
    """
    belief = Belief()
    for row in pairs:
        if row.event_key in belief.seen:
            raise ValueError('duplicate decoder event')
        if row.audit is None:
            belief = Belief(belief.log_weights, belief.seen | {row.event_key},
                            belief.pair_count, belief.anchor_count,
                            belief.held_count + 1,
                            belief.receipts + ({'event': row.event_key,
                                                'status': 'HOLD_MISSING_AUDIT'},))
            continue
        belief = belief.ingest(Observation(row.event_key, row.primary, row.audit,
                                          row.primary_origin, row.audit_origin))
    return belief


def uncertainty(p: dict[str, float]) -> float:
    return -sum(v * log2(v) for v in p.values() if v > 0)


def outcomes(query: str) -> tuple[tuple[str, ...], ...]:
    if query == 'AUDIT_PAIR':
        return tuple(product(READINGS, repeat=2))
    if query == 'VERIFY_ANCHOR':
        return tuple(product(READINGS, repeat=3))
    raise ValueError('unrecognized synthetic inquiry')


def query_information(belief: Belief, query: str) -> float:
    """Expected entropy reduction over all outcomes under the stated model.

    Observation probabilities are *not* taken from any hidden simulator state.
    """
    prior = belief.probabilities()
    prior_entropy = uncertainty(prior)
    expected_entropy = 0.0
    for result in outcomes(query):
        primary, audit = result[:2]
        anchor = result[2] if query == 'VERIFY_ANCHOR' else None
        joint = {h: prior[h] * likelihood(h, primary, audit, anchor)
                 for h in HYPOTHESES}
        prob_outcome = sum(joint.values())
        # Anchor outcomes represent P(T=t)=0.5; factor cancels in conditional
        # posterior but is essential for normalized outcome probability.
        if anchor is not None:
            prob_outcome *= 0.5
        conditional = {h: x/sum(joint.values()) for h, x in joint.items()}
        expected_entropy += prob_outcome * uncertainty(conditional)
    return max(0.0, prior_entropy - expected_entropy)


@dataclass(frozen=True)
class Inquiry:
    status: str
    query: str | None
    information_gain_bits: float
    cost: int
    expected_gain_per_cost: float
    can_execute_real_action: bool = False
    explanation: str = ''


def propose_inquiry(belief: Belief, allowed: frozenset[str], budget: int,
                    costs: dict[str, int] | None = None) -> Inquiry:
    """Budgeted, permission-checked proposal. No simulator called here."""
    if budget < 0 or any(x not in ('AUDIT_PAIR','VERIFY_ANCHOR') for x in allowed):
        raise ValueError('invalid permissions/budget')
    costs = dict(costs or {'AUDIT_PAIR': 1, 'VERIFY_ANCHOR': 3})
    if any(k not in ('AUDIT_PAIR','VERIFY_ANCHOR') or type(v) is not int or v < 1
           for k, v in costs.items()):
        raise ValueError('invalid costs')
    viable = [(kind, query_information(belief, kind), costs[kind])
              for kind in sorted(allowed) if kind in costs and costs[kind] <= budget]
    if not viable:
        return Inquiry('HOLD_NOT_ALLOWED_OR_UNAFFORDABLE', None, 0.0, 0, 0.0)
    choice = max(viable, key=lambda row: (row[1]/row[2], row[1], row[0]))
    if choice[1] < 1e-9:
        return Inquiry('HOLD_NO_EXPECTED_INFORMATION', None, 0.0, 0, 0.0)
    return Inquiry('I_SYNTHETIC_INQUIRY_PROPOSAL', choice[0], choice[1],choice[2],
                   choice[1]/choice[2], False,
                   'Information gain conditional on four fixed flip models and supplied reliabilities')


def sample_case(hypothesis: str, key: str, rng: Random,
                *, anchor: bool = False, tamper_anchor: bool = False,
                shared_origin: bool = False) -> tuple[Observation, str]:
    """Separate synthetic oracle: true regime never enters Belief or inquiry.

    Tampered anchor shows failure when a falsely attested reference is trusted.
    """
    if hypothesis not in FLIPS:
        raise ValueError('unknown fixture')
    true = READINGS[rng.randrange(2)]
    pf, af = FLIPS[hypothesis]
    expected_p = flip(true) if pf else true
    expected_a = flip(true) if af else true
    p = expected_p if rng.random() < PRIMARY_ACCURACY else flip(expected_p)
    a = expected_a if rng.random() < AUDIT_ACCURACY else flip(expected_a)
    reported_anchor = (flip(true) if tamper_anchor else true) if anchor else None
    event = Observation(key, p, a, 'shared' if shared_origin else 'primary',
                        'shared' if shared_origin else 'audit', reported_anchor, anchor)
    return event, true


def synthetic_batch(hypothesis: str, kind: str, n: int,
                    *, tamper_anchor: bool = False) -> tuple[Observation, ...]:
    if n < 0 or kind not in ('AUDIT_PAIR', 'VERIFY_ANCHOR'):
        raise ValueError('invalid synthetic experiment')
    rng = Random(int.from_bytes(sha256(f'PROBE001:{hypothesis}:{kind}:seed02'.encode()).digest()[:8], 'big'))
    return tuple(sample_case(hypothesis, f'{kind}-{i}', rng,
                             anchor=kind=='VERIFY_ANCHOR', tamper_anchor=tamper_anchor)[0]
                 for i in range(n))


def evaluate_once(hypothesis: str, anchor_samples: int = 24) -> dict:
    prior = Belief()
    pairs = synthetic_batch(hypothesis, 'AUDIT_PAIR', 160)
    for p in pairs:
        prior = prior.ingest(p)
    unanchored = prior.classification()
    after = prior
    for p in synthetic_batch(hypothesis, 'VERIFY_ANCHOR', anchor_samples):
        after = after.ingest(p)
    return {'hypothesis': hypothesis, 'pairs': len(pairs), 'anchors': anchor_samples,
            'posterior_without_anchors': prior.probabilities(),
            'posterior_after_anchors': after.probabilities(),
            'unanchored_identifiability': unanchored['identifiability'],
            'final_status': after.classification()['status']}


def fir_receipt(belief: Belief) -> dict:
    """Reasoning remains I. Finite sample count alone gets F_LOCAL."""
    scope = f'synthetic-observations:{len(belief.seen)}:{belief.pair_count}:{belief.anchor_count}'
    proposed = Claim('Leading four-model witness polarity explanation', scope)
    count_claim = Claim(f'Exactly {belief.anchor_count} fixture-attested anchors ingested', scope)
    before = FIRWorld('synthetic witness model', 'declared four-polarity observation model')
    proposal = execute(before, Program('candidate-explanation', (Step('propose', proposed),),
                                       before.carrier, before.decoder))
    exact = execute(proposal.world, Program('finite-count', (
        Step('propose', count_claim),
        Step('admit', count_claim, Warrant('finite_computation','counted immutable fixture receipts',scope))
    ), before.carrier, before.decoder))
    if not proposal.applied or not exact.applied:
        raise AssertionError('FIR contract unexpectedly refused')
    return {'proposed_role':'I', 'proposed_is_fact':proposed in exact.world.facts,
            'count_role':'F_LOCAL', 'scope':scope,
            'receipts':tuple(proposal.receipts)+tuple(exact.receipts)}


def demonstration() -> dict:
    scan = {h:evaluate_once(h) for h in HYPOTHESES}
    ambiguous = Belief()
    for p in synthetic_batch('BOTH_INVERTED','AUDIT_PAIR',160):
        ambiguous = ambiguous.ingest(p)
    nominated=propose_inquiry(ambiguous, frozenset({'AUDIT_PAIR','VERIFY_ANCHOR'}),3)
    tampered=ambiguous
    for p in synthetic_batch('BOTH_INVERTED','VERIFY_ANCHOR',24,tamper_anchor=True):
        tampered=tampered.ingest(p)
    clean=ambiguous
    for p in synthetic_batch('BOTH_INVERTED','VERIFY_ANCHOR',24):
        clean=clean.ingest(p)
    reports=(SourceClaim('a','A','A','blue'),SourceClaim('b','B','A','blue'),
             SourceClaim('c','C','A','blue'),SourceClaim('d','D','D','amber'))
    return {
        'experiment':'PROVENANCE-PROBE-001',
        'scope':'toy finite Bayes with assumed known channel error rates',
        'by_true_polarity':{h:{'pair_only':{k:round(v,6) for k,v in item['posterior_without_anchors'].items()},
                               'with_anchors':{k:round(v,6) for k,v in item['posterior_after_anchors'].items()}}
                            for h,item in scan.items()},
        'inquiry':{'status':nominated.status,'type':nominated.query,
                   'expected_information_bits':round(nominated.information_gain_bits,6),
                   'cost':nominated.cost},
        'forwards':{'raw_majority':naive_majority(reports),
                    'root_collapsed':naive_majority(reports,deduplicate=True),
                    'unverified_independence':True},
        'tampered_anchor':{'posterior_truth_model':round(tampered.probabilities()['BOTH_INVERTED'],6),
                            'posterior_correct_anchor':round(clean.probabilities()['BOTH_INVERTED'],6)},
        'fir':{'explanation_role':fir_receipt(clean)['proposed_role'],
                'count_role':fir_receipt(clean)['count_role']},
        'real_inquiries_dispatched':0,'autonomous_code_changes':0,
        'generalization':'HOLD: origin labels and anchors are not authenticated; model misspecification untested'
    }


if __name__=='__main__':
    print(json.dumps(demonstration(), indent=2, sort_keys=True))
