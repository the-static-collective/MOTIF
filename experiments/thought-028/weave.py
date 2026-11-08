"""THOUGHT-028: proof-bearing fragment retrieval, composition and active inquiry.

This is a bounded, synthetic, oracle-assisted laboratory. No model, human-language
oracle, write-capability, or real-world data is accessed. Source-owner verified
fragments license candidate *operators*, not truth in an unfamiliar problem.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
for name in ('thought-023', 'thought-025', 'thought-027'):
    sibling = str(HERE.parent / name)
    if sibling not in sys.path:
        sys.path.insert(0, sibling)

from grammar import evaluate, validate_expression, COLORS
from specimens import Specimen, independent_target, public_brief
from abstraction import (SCHEMA as AST_SCHEMA, evaluate_reply, check_truth,
                         source_owned_program_check, validate_proposal, raw_cases)
from proof_memory import (ProofError, ProofLibrary, verify_card,
                          canonical, digest)

SCHEMA = 'motif.thought028.proof-weave.v1'
DERIVED_SCHEMA = 'motif.thought028.derived-evidence.v1'
LIBRARY_SCHEMA = 'motif.thought028.operator-owned-evidence-store.v1'


def mask(values):
    return sum(1 << i for i, color in enumerate(COLORS) if color in values)


def colorize(num):
    return frozenset(color for i, color in enumerate(COLORS) if num & (1 << i))


def expression_signature(expression):
    checked = validate_expression(expression, 'universe_constant')
    return tuple(mask(evaluate(checked, colorize(a), colorize(b),
                               'universe_constant'))
                 for a in range(8) for b in range(8))


def expr_nodes(ex):
    return 1 if 'ref' in ex else 1 + sum(expr_nodes(v) for v in ex['args'])


def uses(expression):
    if 'ref' in expression:
        return set(), {'universe'} if expression['ref'] == 'universe' else set()
    operations = {expression['op']}
    refs = set()
    for child in expression['args']:
        children, names = uses(child)
        operations.update(children)
        refs.update(names)
    return operations, refs


def as_proposal(task, expression, current_id, event_id):
    proposal = {'schema': AST_SCHEMA,
                'bindings': {'current': current_id, 'event': event_id},
                'expression': expression,
                'rationale': 'Scoped evidence candidate; new meaning remains unverified'}
    return validate_proposal(task, proposal)


def normalize_sources(cards, registry):
    """Reject tampered cards before they can license operators or be retrieved."""
    if type(cards) is not list or not 1 <= len(cards) <= 48:
        raise ProofError('bounded nonempty source-card list required')
    by_digest = {}
    for card in cards:
        if type(card) is not dict or card.get('schema') != 'motif.thought027.proof-carrying-fragment.v1':
            raise ProofError('unexpected source card')
        task = registry.get(card.get('task_key'))
        if not isinstance(task, Specimen):
            raise ProofError('unknown source task; cannot recertify')
        verify_card(task, card)
        by_digest[card['proof_digest']] = deepcopy(card)
    return by_digest


def licenses(verified):
    lic = {}
    for proof in verified.values():
        rel = proof['relation']
        if rel == 'UNION':
            lic.setdefault('union', proof['proof_digest'])
        elif rel == 'DIFFERENCE':
            lic.setdefault('difference', proof['proof_digest'])
        elif rel == 'COMPLEMENT':
            lic.setdefault('universe', proof['proof_digest'])
    return lic


def enumerate_compositions(allowed, *, max_depth=3, max_nodes=15):
    """Enumerate distinct set functions without consulting any task oracle.

    Every composite is built solely from independently rechecked operators.
    The finite Boolean signatures are derived from the defined syntax, not a
    particular new task's expected answers. Smallest expression survives.
    """
    if type(max_depth) is not int or not 1 <= max_depth <= 3 or type(max_nodes) is not int or not 3 <= max_nodes <= 19:
        raise ProofError('composition budget exceeds bounded experiment')
    permitted = {key for key in ('union', 'difference') if key in allowed}
    refs = ['state.on', 'arrival.toggles']
    if 'universe' in allowed:
        refs.append('universe')
    atom_signatures = {
        'state.on': tuple(a for a in range(8) for _ in range(8)),
        'arrival.toggles': tuple(b for _ in range(8) for b in range(8)),
        'universe': (7,) * 64,
    }
    entries = {}
    for name in refs:
        ex = {'ref': name}
        entries[atom_signatures[name]] = {'expression': ex, 'signature': atom_signatures[name],
                                          'depth': 0, 'nodes': 1}
    for depth in range(1, max_depth + 1):
        old = list(entries.values())
        fresh = {}
        for a in old:
            for b in old:
                if max(a['depth'], b['depth']) != depth - 1:
                    continue
                nodes = a['nodes'] + b['nodes'] + 1
                if nodes > max_nodes:
                    continue
                for operation in permitted:
                    sig = tuple((x | y) if operation == 'union' else (x & (~y & 7))
                                for x, y in zip(a['signature'], b['signature']))
                    ex = {'op': operation, 'args': [a['expression'], b['expression']]}
                    contender = {'expression': ex, 'signature': sig,
                                 'depth': depth, 'nodes': nodes}
                    prior = fresh.get(sig)
                    if prior is None or (nodes, canonical(ex)) < (prior['nodes'], canonical(prior['expression'])):
                        fresh[sig] = contender
        for sig, item in fresh.items():
            prior = entries.get(sig)
            if prior is None or (item['nodes'], canonical(item['expression'])) < (prior['nodes'], canonical(prior['expression'])):
                entries[sig] = item
    return sorted(entries.values(), key=lambda item: (item['nodes'], canonical(item['expression'])))


class EvidenceStore:
    """Explicitly operator-owned, in-memory JSON store. No automatic persistence."""
    def __init__(self, source_cards, source_registry):
        self.registry = dict(source_registry)
        self.sources = normalize_sources(source_cards, self.registry)
        self.derived = {}

    def add_task(self, task):
        if not isinstance(task, Specimen):
            raise ProofError('typed evaluator-owned synthetic task required')
        if task.key in self.registry and self.registry[task.key] != task:
            raise ProofError('task key mutation refused')
        self.registry[task.key] = task

    def _verify_derived(self, card):
        if type(card) is not dict or card.get('schema') != DERIVED_SCHEMA:
            raise ProofError('invalid derived card schema')
        core = {key:value for key,value in card.items() if key != 'proof_digest'}
        if set(card) != set(core)|{'proof_digest'} or digest(core) != card['proof_digest']:
            raise ProofError('tampered derived certificate')
        task = self.registry.get(card.get('task_key'))
        if not isinstance(task, Specimen) or not task.representable:
            raise ProofError('unknown or invalid downstream proof scope')
        if card['task_spec_sha256'] != digest(public_brief(task)):
            raise ProofError('source task definition changed')
        if card['status'] != 'VERIFIED_ONLY_FOR_THIS_SYNTHETIC_TASK' or card['installed'] is not False:
            raise ProofError('unverified or installed evidence refused')
        parents = card.get('parent_proof_digests')
        if type(parents) is not list or not parents or len(parents) != len(set(parents)):
            raise ProofError('missing or duplicate parent evidence')
        if card['proof_digest'] in parents:
            raise ProofError('self-referential proof chain')
        for parent in parents:
            if parent not in self.sources and parent not in self.derived:
                raise ProofError('unresolved parent certificate')
        p = validate_proposal(task, card['proposal'])
        if digest(p) != card['proposal_digest']:
            raise ProofError('proposal contents changed')
        source = check_truth(task, p)
        if source != card['independent_evaluation'] or source['correct'] != 64:
            raise ProofError('independent target disagrees')
        program = source_owned_program_check(task, p)
        if program != card['trusted_template_evaluation'] or program['correct'] != 64:
            raise ProofError('executable evidence disagrees')
        if digest(expression_signature(p['expression'])) != card['function_sha256']:
            raise ProofError('semantic fingerprint changed')
        return True

    def add_derived(self, task, successful_run):
        self.add_task(task)
        if successful_run.get('status') != 'REVIEW_SCOPED_CANDIDATE_NOT_INSTALLED' or successful_run.get('installed') is not False:
            raise ProofError('only an independently certified review candidate can be stored')
        p = validate_proposal(task, successful_run['proposal'])
        full = check_truth(task, p)
        runtime = source_owned_program_check(task, p)
        if full != successful_run['frozen'] or runtime != successful_run['trusted_runtime'] or full['correct'] != 64 or runtime['correct'] != 64:
            raise ProofError('run does not independently reproduce')
        support = sorted(set(successful_run['source_proof_digests']))
        if not support or any(s not in self.sources and s not in self.derived for s in support):
            raise ProofError('missing trusted proof support')
        card = {'schema': DERIVED_SCHEMA, 'task_key': task.key,
                'task_spec_sha256':digest(public_brief(task)),
                'proposal': p, 'proposal_digest': digest(p),
                'function_sha256':digest(expression_signature(p['expression'])),
                'parent_proof_digests':support,
                'independent_evaluation':full, 'trusted_template_evaluation':runtime,
                'status':'VERIFIED_ONLY_FOR_THIS_SYNTHETIC_TASK',
                'source_task_meaning_not_transferred_as_truth':True,
                'origin_authenticated':False, 'installed':False,
                'external_authority':'NONE'}
        card['proof_digest'] = digest(card)
        self._verify_derived(card)
        self.derived[card['proof_digest']] = deepcopy(card)
        return deepcopy(card)

    def verify_all(self):
        normalize_sources(list(self.sources.values()), self.registry)
        for card in self.derived.values():
            self._verify_derived(card)
        return True

    def export(self):
        self.verify_all()
        envelope = {'schema':LIBRARY_SCHEMA, 'source_cards':list(self.sources.values()),
                    'derived_cards':list(self.derived.values()),
                    'source_owner_created_and_controls_export':True,
                    'model_provenance_authenticated':False,
                    'contains_nonboolean_world_model':False,
                    'installed':False,'external_authority':'NONE'}
        envelope['integrity_digest'] = digest(envelope)
        return envelope

    @classmethod
    def load(cls, packet, registry):
        if type(packet) is not dict or packet.get('schema') != LIBRARY_SCHEMA:
            raise ProofError('invalid library envelope')
        core = {key:value for key,value in packet.items() if key != 'integrity_digest'}
        if set(packet) != set(core)|{'integrity_digest'} or packet['integrity_digest'] != digest(core):
            raise ProofError('library envelope altered')
        if packet.get('installed') is not False or type(packet.get('source_cards')) is not list or type(packet.get('derived_cards')) is not list or len(packet['derived_cards'])>48:
            raise ProofError('library outside review-only bounds')
        result = cls(packet['source_cards'], registry)
        for card in packet['derived_cards']:
            result._verify_derived(card)
            result.derived[card['proof_digest']] = deepcopy(card)
        result.verify_all()
        return result


def catalog(task, store, *, mode='direct', max_depth=3):
    if not isinstance(task, Specimen) or not task.representable:
        raise ProofError('cannot coerce ambiguous or nonboolean task to set logic')
    if mode not in ('direct', 'compose', 'retrieved'):
        raise ProofError('unsupported source-only reasoning strategy')
    store.verify_all()
    ids = [key for key,_ in task.fields]
    candidates = {}
    current_licenses = licenses(store.sources)

    def admit(expression, supporting_ids, origin):
        expr = validate_expression(expression, 'universe_constant')
        if not supporting_ids:
            return
        for first,second in ((ids[0],ids[1]),(ids[1],ids[0])):
            p = as_proposal(task, expr, first, second)
            sig = tuple(evaluate_reply(task, p, raw) for raw in raw_cases(task))
            key = digest(sig)
            cont = {'proposal':p, 'signature':sig,
                    'source_proof_digests':sorted(set(supporting_ids)),
                    'origin':origin, 'nodes':expr_nodes(expr)}
            old = candidates.get(key)
            if old is None or (cont['nodes'],0 if origin=='RETRIEVED_PROOF' else 1,canonical(expr)) < (old['nodes'],0 if old['origin']=='RETRIEVED_PROOF' else 1,canonical(old['proposal']['expression'])):
                candidates[key] = cont

    for c in store.sources.values():
        admit(c['typed_expression'], [c['proof_digest']], 'SOURCE_PROOF_KERNEL')
    if mode in ('compose','retrieved'):
        for proof in store.derived.values():
            admit(proof['proposal']['expression'], [proof['proof_digest']], 'RETRIEVED_PROOF')
    if mode == 'compose':
        for expression in enumerate_compositions(current_licenses,max_depth=max_depth):
            ex=expression['expression']
            operators, referents = uses(ex)
            source_ids=[current_licenses[x] for x in sorted(operators|referents) if x in current_licenses]
            # Exclude unsubstantiated direct reference-only proposals. Operators
            # must have an independently recertified precedent in the store.
            if source_ids:
                admit(ex,source_ids,'LICENSED_COMPOSITION')
    if len(candidates)>64:
        raise ProofError('bounded candidate hypothesis space exceeded')
    return candidates


def best_probe(candidates, seen):
    """Pure information-gain policy; never reads source-owner expected answer."""
    winner=None
    for a in range(8):
        for b in range(8):
            if (a,b) in seen:
                continue
            counts = Counter(c['signature'][a*8+b] for c in candidates.values())
            information = len(candidates)**2 - sum(q*q for q in counts.values())
            ranking = (information, len(counts), int(a!=0 and b!=0),
                       int((a&b)!=0), -a,-b)
            if winner is None or ranking > winner[0]:
                winner = (ranking,(a,b))
    return None if winner is None else winner[1]


def investigate(task,store,*,mode='compose',query_budget=4,min_queries=2,max_depth=3):
    if not isinstance(task,Specimen):
        raise ProofError('new task must have a source-owned explicit definition')
    if type(query_budget) is not int or not 2<=query_budget<=6 or type(min_queries) is not int or not 2<=min_queries<=query_budget:
        raise ProofError('unapproved development-query budget')
    if not task.representable:
        return {'schema':SCHEMA,'task':task.key,'mode':mode,
                'status':'HOLD_SOURCE_OWNER_NONBOOLEAN_OR_AMBIGUOUS',
                'development_queries':0,'candidate_count':0,'installed':False,
                'external_authority':'NONE'}
    choices=catalog(task,store,mode=mode,max_depth=max_depth)
    alive=dict(choices); seen=set();records=[]
    names=[n for n,_ in task.fields]
    for _ in range(query_budget):
        if len(alive)==1 and len(records)>=min_queries:
            break
        if not alive:
            break
        a,b = best_probe(alive,seen)
        if (a,b) in seen:
            raise ProofError('duplicate developer probe')
        raw={names[0]:a,names[1]:b}
        expected=independent_target(task,raw)
        before=len(alive)
        alive={k:v for k,v in alive.items() if v['signature'][a*8+b]==expected}
        records.append({'raw_inputs':raw,'source_owner_oracle_observed':expected,
                        'candidates_before':before,'candidates_remaining':len(alive)})
        seen.add((a,b))
    outcome='HOLD_NO_CONSISTENT_CANDIDATE' if not alive else ('HOLD_UNRESOLVED_DEV_AMBIGUITY' if len(alive)!=1 or len(records)<min_queries else 'DEV_CANDIDATE_FROZEN')
    frozen=program=proposal=None;parents=[];origin=None
    if outcome=='DEV_CANDIDATE_FROZEN':
        winner=next(iter(alive.values()))
        proposal=winner['proposal'];parents=winner['source_proof_digests'];origin=winner['origin']
        frozen=check_truth(task,proposal)
        if frozen['correct']==64:
            program=source_owned_program_check(task,proposal)
            outcome='REVIEW_SCOPED_CANDIDATE_NOT_INSTALLED' if program['correct']==64 else 'HOLD_TRUSTED_RUNTIME_DISAGREES'
        else:
            outcome='HOLD_FROZEN_COUNTEREXAMPLE_NO_POST_AUDIT_REPAIR'
    receipt={'schema':SCHEMA,'task':task.key,'mode':mode,'status':outcome,
            'candidate_count':len(choices),'remaining_after_development':len(alive),
            'development_queries':len(records),'development_observations':records,
            'proposal':proposal,'selected_origin':origin,
            'source_proof_digests':parents,'frozen':frozen,
            'trusted_runtime':program,
            'candidate_choice_did_not_use_target_frozen_truth':True,
            'probes_chosen_without_looking_at_expected_result':True,
            'linguistic_mapping_not_demonstrated':True,
            'full_domain_verification_only_after_candidate_selection':True,
            'automatic_install_disabled':True,'installed':False,
            'external_authority':'NONE'}
    receipt['receipt_digest']=digest(receipt)
    return receipt
