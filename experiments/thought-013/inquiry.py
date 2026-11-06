"""THOUGHT-013: finite, source-anchored, adaptive active inquiry.

A question is an operation over *declared hypothetical worlds*, never a true
fact or an evidence-source. Geometry is optional display, not evidence.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from json import dumps
from math import log2
from pathlib import Path
import sys

SIBLING = str(Path(__file__).resolve().parent.parent / 'thought-008')
if SIBLING not in sys.path:
    sys.path.append(SIBLING)
from multiview import ThoughtViews, ViewError

SCHEMA = 'motif.thought-adaptive-inquiry.v1'
LENS = {'associated': 'association', 'requires': 'dependency',
        'contradicts': 'tension', 'enables': 'affordance'}
ORDER = ('dependency', 'tension', 'affordance', 'association')


def _json(data):
    return dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('utf8')


def sha(data):
    return sha256(_json(data)).hexdigest()


def entropy(labels):
    if not labels:
        return 0.0
    counts = defaultdict(int)
    for x in labels:
        counts[x] += 1
    n = len(labels)
    return -sum((c / n) * log2(c / n) for c in counts.values())


def information_gain(worlds, atom, goal):
    """Exact finite uniform information gain; never uses oracle answer."""
    if len(worlds) < 2:
        return 0.0
    if goal == 'decision':
        labels = [w['decision'] for w in worlds]
    else:
        labels = [w['id'] for w in worlds]
    prior = entropy(labels)
    weighted = 0.0
    for outcome in (False, True):
        subset = [w for w in worlds if w['atoms'][atom] == outcome]
        if subset:
            subset_labels = [w['decision'] if goal == 'decision' else w['id'] for w in subset]
            weighted += len(subset)/len(worlds)*entropy(subset_labels)
    return round(max(0., prior-weighted), 12)


class InquiryError(ValueError):
    pass


class InquiryCycle:
    """Re-select each QUESTION_ONLY inquiry after each external toy observation.

    Input hypothetical worlds encode the caller's modeled possibilities. This
    engine does not discover or authenticate them. Truth oracle is supplied by
    separate fixture only; it is never inferred from layout or text.
    """

    def __init__(self, engine: ThoughtViews, worlds, *, seed_pair,
                 strategy='decision', allowed_lenses=ORDER, geometry=False):
        if not isinstance(engine, ThoughtViews):
            raise InquiryError('expected source-owned THOUGHT-008 engine')
        if (not isinstance(seed_pair, (tuple, list)) or len(seed_pair) != 2 or
            any(type(x) is not str or x not in engine.manifests for x in seed_pair) or
            seed_pair[0] == seed_pair[1]):
            raise InquiryError('two distinct existing manifestation IDs required')
        if strategy not in ('decision', 'world'):
            raise InquiryError('unknown explicit inquiry strategy')
        if (not isinstance(allowed_lenses,(tuple,list)) or not allowed_lenses or
            len(allowed_lenses) != len(set(allowed_lenses)) or
            any(x not in ORDER for x in allowed_lenses)):
            raise InquiryError('invalid lens set')
        if type(geometry) is not bool:
            raise InquiryError('geometry flag must be boolean')
        self.engine = engine
        self.seed_pair = tuple(seed_pair)
        self.strategy = strategy
        self.allowed = tuple(allowed_lenses)
        self.geometry = geometry
        self.catalog = self._build_catalog()
        if not self.catalog:
            raise InquiryError('no declared typed inquiry edges in local cut')
        if (not isinstance(worlds, list) or not 2 <= len(worlds) <= 64 or
            any(not isinstance(w, dict) or set(w) != {'id','decision','atoms'} for w in worlds)):
            raise InquiryError('2..64 explicit hypothetical world records required')
        if len({w['id'] for w in worlds}) != len(worlds):
            raise InquiryError('duplicate hypothetical world IDs')
        required = {c['atom'] for c in self.catalog}
        for w in worlds:
            if (type(w['id']) is not str or not w['id'] or len(w['id']) > 90 or
                w['decision'] not in ('YES','NO') or
                type(w['atoms']) is not dict or set(w['atoms']) != required or
                any(type(value) is not bool for value in w['atoms'].values())):
                raise InquiryError('hypothetical worlds must cover all typed questions with boolean states')
        self.original = sorted([{'id':w['id'], 'decision':w['decision'],
                                 'atoms': dict(w['atoms'])} for w in worlds], key=lambda x:x['id'])
        self.remaining = list(self.original)
        self.attempted = set()
        self.steps = []
        self.stop_reason = None
        self.source_digest = engine.input_digest
        self.identity_digest = engine.source_snapshot_digest
        self.world_model_digest = sha(self.original)

    def _build_catalog(self):
        # The local inquiry cut is graph-based; it is independent of positions.
        near = set(self.seed_pair)
        for rel in self.engine.relations:
            if rel['status'] == 'AUTHORED' and rel['source'] in near:
                near.add(rel['target'])
        questions = []
        for rel in self.engine.relations:
            if rel['status'] != 'AUTHORED' or rel['predicate'] not in LENS:
                continue
            if not (rel['source'] in near or rel['target'] in near):
                continue
            questions.append({'id':'ask:'+rel['id'], 'atom':rel['id'],
                'lens':LENS[rel['predicate']], 'relation_id':rel['id'],
                'source':rel['source'], 'target':rel['target'],
                'predicate':rel['predicate'], 'claimed_origin':rel['origin'],
                'status':'QUESTION_ONLY', 'meaning':'Check a caller-authored relation, not established truth'})
        return sorted(questions, key=lambda x:x['id'])

    @property
    def candidates(self):
        return [q for q in self.catalog if q['id'] not in self.attempted and q['lens'] in self.allowed]

    def next_question(self):
        if self.stop_reason:
            return None
        decisions = {w['decision'] for w in self.remaining}
        if len(decisions) == 1:
            self.stop_reason = 'MODEL_CONSENSUS_NOT_TRUTH'
            return None
        rated = []
        for q in self.candidates:
            info = information_gain(self.remaining, q['atom'], self.strategy)
            rated.append((info, self.allowed.index(q['lens']), q['id'], q))
        if not rated:
            self.stop_reason='HOLD_NO_MORE_TESTABLE_QUESTIONS'
            return None
        rated.sort(key=lambda x:(-x[0], x[1], x[2]))
        gain, _, _, q = rated[0]
        if gain == 0:
            self.stop_reason='HOLD_NO_DISCRIMINATING_QUESTION'
            return None
        return {**q, 'expected_information_gain_bits':gain,
                'strategy':'decision_relevant_information' if self.strategy=='decision' else 'world_entropy',
                'remaining_hypothetical_worlds':len(self.remaining),
                'geometry_used_for_evidence':False}

    def observe(self, question, answer):
        canonical_q = next((q for q in self.candidates
                            if isinstance(question,dict) and q['id']==question.get('id')),None)
        if (canonical_q is None or any(question.get(key)!=value
                for key,value in canonical_q.items()) or
                (self.engine.input_digest != self.source_digest or
                 self.engine.source_snapshot_digest != self.identity_digest)):
            raise InquiryError('question/source must match current frozen inquiry catalog')
        if not (type(answer) is bool or answer == 'UNKNOWN' and type(answer) is str):
            raise InquiryError('oracle answer must be YES, NO, or UNKNOWN')
        # Explicit source-only projection can help display, never alter posterior.
        projected = None
        if self.geometry:
            view = self.engine.project(canonical_q['lens'],anchor=self.seed_pair[1])
            if (view['source_evidence_digest'] != self.source_digest or
                view['relations'] != self.engine.relations or view['external_authority'] != 'NONE'):
                raise InquiryError('representation changed source evidence')
            projected = len(view['placements'])
        old = list(self.remaining)
        new = [w for w in old if w['atoms'][canonical_q['atom']] == answer] if answer != 'UNKNOWN' else old
        mismatch = answer != 'UNKNOWN' and len(new) == 0
        self.attempted.add(canonical_q['id'])
        if mismatch:
            self.stop_reason = 'HOLD_MODEL_MISMATCH'
        elif answer != 'UNKNOWN':
            self.remaining = new
        step = {'index':len(self.steps)+1, 'question_id':canonical_q['id'],
                'lens':canonical_q['lens'],'atom':canonical_q['atom'],
                'relation_id':canonical_q['relation_id'], 'claimed_origin':canonical_q['claimed_origin'],
                'answer':'UNKNOWN' if answer=='UNKNOWN' else ('YES' if answer else 'NO'),
                'response_is_fixture_oracle_not_world_witness':True,
                'expected_information_gain_bits':information_gain(old,canonical_q['atom'],self.strategy),
                'prior_model_world_count':len(old),'posterior_model_world_count':len(self.remaining),
                'model_mismatch':mismatch,'source_digest':self.source_digest,
                'previous_receipt':self.steps[-1]['receipt'] if self.steps else '0'*64,
                'projection_placement_count':projected, 'coordinates_used_for_evidence':False,
                'external_authority':'NONE', 'pen_status':'UNCHANGED'}
        step['receipt'] = sha(step)
        self.steps.append(step)
        return step

    def run(self, oracle, *, budget=3):
        if not callable(oracle):
            raise InquiryError('oracle must be a deliberately supplied test function')
        if type(budget) is not int or not 0 <= budget <= 12:
            raise InquiryError('question budget must be 0..12')
        while len(self.steps) < budget:
            q = self.next_question()
            if q is None: break
            a = oracle(q['atom'])
            self.observe(q,a)
        if len(self.steps) >= budget and not self.stop_reason:
            self.stop_reason='HOLD_BUDGET_EXHAUSTED' if len({w['decision'] for w in self.remaining})>1 else 'MODEL_CONSENSUS_NOT_TRUTH'
        return self.report()

    def report(self):
        if self.engine.input_digest != self.source_digest:
            raise InquiryError('source changed during inquiry')
        votes={x:sum(w['decision']==x for w in self.remaining) for x in ('YES','NO')}
        agreement=next((x for x,c in votes.items() if c==len(self.remaining)),None)
        payload = {'schema':SCHEMA,'source_digest':self.source_digest,
                   'identity_digest':self.identity_digest, 'world_model_digest':self.world_model_digest,
                   'strategy':self.strategy, 'allowed_lenses':list(self.allowed),
                   'starting_manifestations':list(self.seed_pair),
                   'candidate_question_count':len(self.catalog),
                   'model_worlds_remaining':len(self.remaining),
                   'decision_distribution_under_assumptions':votes,
                   'proposed_decision':agreement, 'conclusion_status':self.stop_reason or 'OPEN_PENCIL',
                   'question_steps':list(self.steps),'view_count':sum(s['projection_placement_count'] is not None for s in self.steps),
                   'geometry_used_for_evidence':False, 'pen_status':'UNCHANGED',
                   'effective_external_authority':'NONE',
                   'warning':'Finite hypothetical models and caller-provided test answers; consensus is NOT verified world truth.'}
        return {**payload,'receipt_digest':sha(payload)}
