"""GEOM-009 — bounded-per-search induction of new rewrite rules.

Claims: hypotheses inferred from examples (PENCIL only), never observations,
permission, semantic truth, a live grammar mutation, or novel mathematics.
Every proposal is evaluated against a frozen heldout set after selection.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import hashlib

from living_graph import LivingGraph, RewriteGrammar, RewriteRule, canonical, stable_id, nonempty


@dataclass(frozen=True)
class Example:
    identity: str
    before: tuple[str, ...]
    after: tuple[str, ...]
    expected: bool
    source_root: str

    def __post_init__(self) -> None:
        nonempty(self.identity, 'example id')
        nonempty(self.source_root, 'claimed source root')
        if type(self.expected) is not bool:
            raise ValueError('expected must be bool')
        if self.before == self.after:
            raise ValueError('identity example cannot establish a rewrite')
        if any(not isinstance(t, str) or not t.strip() for t in self.before + self.after):
            raise ValueError('tokens must be nonempty strings')

    def data(self) -> dict:
        return {'id': self.identity, 'before': list(self.before), 'after': list(self.after),
                'expected': self.expected, 'claimed_root': self.source_root}


def predicts(rule: RewriteRule, example: Example) -> bool:
    """Exact membership of a proposed single-step rewrite outcome."""
    return any(out == example.after for _, out in rule.outcomes(example.before))


def candidate_patterns(before: Sequence[str], after: Sequence[str]):
    """Enumerate all one-contiguous-span replacements explaining one transition.

    No fixed token/arity/pattern-length cap. Memory/time bounded by caller's
    candidate budget, and this is only a single-step symbolic rewrite grammar.
    """
    b, a = tuple(before), tuple(after)
    prefix = 0
    while prefix < min(len(b), len(a)) and b[prefix] == a[prefix]:
        prefix += 1
    suffix = 0
    while suffix < min(len(b), len(a)) and b[len(b)-1-suffix] == a[len(a)-1-suffix]:
        suffix += 1
    seen = set()
    # Prefer general reusable rules (short spans) without knowing heldout.
    all_patterns = []
    for p in range(prefix+1):
        for s in range(min(suffix, len(b)-p, len(a)-p)+1):
            find = b[p:len(b)-s if s else len(b)]
            replace = a[p:len(a)-s if s else len(a)]
            if find != replace and (find, replace) not in seen:
                seen.add((find, replace))
                all_patterns.append((find, replace))
    all_patterns.sort(key=lambda x: (len(x[0])+len(x[1]),len(x[0]),x))
    yield from all_patterns


def score(rule: RewriteRule, cases: Sequence[Example]) -> dict:
    observed = [{'id': e.identity, 'expected': e.expected,
                 'predicted': predicts(rule, e)} for e in cases]
    correct = sum(x['expected'] == x['predicted'] for x in observed)
    tp = sum(x['expected'] and x['predicted'] for x in observed)
    fp = sum(not x['expected'] and x['predicted'] for x in observed)
    return {'correct': correct, 'total': len(cases), 'true_positives': tp,
            'false_positives': fp, 'predictions': observed}


def propose_revision(parent: RewriteGrammar, training: Sequence[Example],
                     heldout: Sequence[Example], *, candidate_budget: int,
                     cursor: dict | None = None, require_distinct_declared_roots: int = 2) -> dict:
    """Find a missing rewrite rule suggested by training examples.

    Cursor is a deterministic position in patterns of FIRST positive example.
    No performance assertion is made when the budget cuts the search; candidate
    selection is on training ONLY. Heldout scores are post-selection. A prior
    untested candidate is not promoted just because a later run has no result.
    """
    train, test = tuple(training), tuple(heldout)
    if type(candidate_budget) is not int or candidate_budget <= 0:
        raise ValueError('positive candidate_budget required')
    if type(require_distinct_declared_roots) is not int or require_distinct_declared_roots < 1:
        raise ValueError('invalid root count')
    if not train or not test:
        raise ValueError('nonempty training and frozen heldout required')
    if len({e.identity for e in train+test}) != len(train+test):
        raise ValueError('example identity overlaps between train and heldout')
    positive = [e for e in train if e.expected]
    if not positive:
        return {'status':'HOLD', 'reason':'no positive demonstrations', 'authority':'NONE'}
    # An existing composition does not count as a representational deficiency.
    parent_unexplained = [e.identity for e in positive
                          if not any(predicts(r,e) for r in parent.rules)]
    if not parent_unexplained:
        return {'status':'HOLD','reason':'existing grammar already explains all positives',
                'authority':'NONE'}
    roots = {e.source_root for e in positive}
    if len(roots) < require_distinct_declared_roots:
        return {'status':'HOLD', 'reason':'insufficient separately declared positive source roots',
                'root_count':len(roots),'authority':'NONE'}
    # Only a deterministic candidate list from the first positive; no heldout leakage.
    patterns = list(candidate_patterns(positive[0].before,positive[0].after))
    domain=stable_id('grammar-search:', {'parent':parent.fingerprint,
        'train':[e.data() for e in train], 'heldout_ids':[e.identity for e in test],
        'root_threshold':require_distinct_declared_roots})
    if cursor is None:
        offset,best_pair=0,None
    else:
        if not isinstance(cursor,dict) or set(cursor)!={'domain','offset','best_pair'} or cursor['domain']!=domain \
           or type(cursor['offset']) is not int or cursor['offset']<0:
            raise ValueError('invalid or mismatched continuation cursor')
        offset=cursor['offset']
        pair=cursor['best_pair']
        if pair is not None and (not isinstance(pair,list) or len(pair)!=2
                                 or not all(isinstance(x,list) for x in pair)):
            raise ValueError('invalid cursor candidate')
        best_pair=(tuple(pair[0]),tuple(pair[1])) if pair is not None else None
    if offset>len(patterns) or (best_pair is not None and best_pair not in patterns[:offset]):
        raise ValueError('cursor beyond domain or forged candidate')
    known = {(r.find, r.replace) for r in parent.rules}
    best = None
    if best_pair is not None:
        restored=RewriteRule('inferred-'+hashlib.sha256(canonical(best_pair).encode()).hexdigest()[:12],*best_pair)
        restored_score=score(restored,train)
        if best_pair in known or restored_score['correct']!=len(train) or restored_score['false_positives']:
            raise ValueError('invalid restored candidate')
        best=((len(restored.find)+len(restored.replace),len(restored.find),restored.find,restored.replace),restored,restored_score)
    considered = 0
    last_cursor = offset
    for index in range(offset, min(len(patterns),offset+candidate_budget)):
        last_cursor = index+1
        pair = patterns[index]
        considered += 1
        if pair in known:
            continue
        rule = RewriteRule('inferred-'+hashlib.sha256(canonical(pair).encode()).hexdigest()[:12], *pair)
        train_score = score(rule,train)
        if train_score['correct'] != len(train) or train_score['false_positives']:
            continue
        if not all(predicts(rule,e) for e in positive):
            continue
        # Select the simplest candidate using TRAIN alone. No semantic truth.
        key = (len(rule.find)+len(rule.replace), len(rule.find),rule.find,rule.replace)
        if best is None or key < best[0]:
            best = (key,rule,train_score)
    # Never assert a globally best candidate on an incomplete search slice.
    complete = last_cursor >= len(patterns)
    if not complete:
        return {'status':'CONTINUE_SEARCH', 'evaluated_this_slice':considered,
                'next_cursor':{'domain':domain,'offset':last_cursor,
                    'best_pair':[list(best[1].find),list(best[1].replace)] if best else None},
                'provisional_candidate':_rule_data(best[1]) if best else None,
                'completeness':'INCOMPLETE', 'authority':'NONE','instrument':'PENCIL'}
    if best is None:
        return {'status':'HOLD', 'reason':'no new one-span rule passes training in this completed slice',
                'evaluated_this_slice':considered, 'authority':'NONE'}
    _,rule,train_score = best
    heldout_score = score(rule,test)
    return {'status':'PENCIL_GRAMMAR_REVISION_PROPOSED', 'rule':_rule_data(rule),
            'parent_fingerprint':parent.fingerprint,
            'proposed_fingerprint':RewriteGrammar(parent.scope,parent.rules+(rule,)).fingerprint,
            'training':train_score, 'heldout':heldout_score,
            'existing_grammar_gap': {'unexplained_positive_cases':parent_unexplained,
                                     'diagnosis':'single-step observed transition unavailable from present vocabulary'},
            'claimed_positive_roots':len(roots),
            'evaluated_this_slice':considered,
            'candidate_space_size':len(patterns), 'scope':parent.scope,
            'completeness':'COMPLETE_FOR_ONE_SPAN_GRAMMAR',
            'authority':'NONE', 'instrument':'PENCIL',
            'limitations':'single-span induction from labeled synthetic examples; no new semantic ontology'}


def _rule_data(rule: RewriteRule) -> dict:
    return {'name':rule.name,'find':list(rule.find),'replace':list(rule.replace)}


def rule_from_proposal(proposal: dict) -> RewriteRule:
    if not isinstance(proposal,dict) or set(proposal) != {'name','find','replace'}:
        raise ValueError('invalid proposed rule fields')
    if not isinstance(proposal['find'],list) or not isinstance(proposal['replace'],list):
        raise ValueError('rule sequences must be arrays')
    return RewriteRule(proposal['name'],tuple(proposal['find']),tuple(proposal['replace']))


def compare_fork(parent: RewriteGrammar, revision: dict, seeds: Sequence[Sequence[str]],
                 targets: Sequence[Sequence[str]], *, work_budget: int) -> dict:
    """Separate scratch graph per grammar. NEVER mutates its parent or an observed atlas.

    Finite work budget, so target misses are UNKNOWN when a frontier remains.
    Outputs counts and coverage only for the explored subgraphs.
    """
    if type(work_budget) is not int or work_budget <= 0:
        raise ValueError('positive work_budget required')
    if not seeds or not targets:
        raise ValueError('seeds and targets required')
    rule = rule_from_proposal(revision)
    if any((rule.find,rule.replace) == (r.find,r.replace) for r in parent.rules):
        raise ValueError('revision duplicates parent')
    new = RewriteGrammar(parent.scope,parent.rules+(rule,))
    output = {}
    for label,gram in [('parent',parent),('revised',new)]:
        with LivingGraph(scope=gram.scope) as graph:
            for seed in seeds:
                graph.seed(seed,source_root='fixture:declared-seed')
            result = graph.grow(gram,work_budget=work_budget)
            hits = []
            for target in targets:
                row = graph.db.execute('SELECT 1 FROM nodes WHERE id=?',
                    (LivingGraph.expression_id(target),)).fetchone()
                hits.append(bool(row))
            output[label]={'counts':graph.counts(),'growth_status':result['status'],
                           'target_hits':sum(hits),'target_results':hits,
                           'unobserved_targets_are_negative': result['status']=='SATURATED_FOR_CURRENT_GRAMMAR',
                           'integrity':graph.verify()}
    return {'status':'PENCIL_COUNTERFACTUAL_FORK', 'scope':parent.scope,
            'parent_fingerprint':parent.fingerprint,'revised_fingerprint':new.fingerprint,
            'comparison':output,'authority':'NONE',
            'note':'non-mutating synthetic fork; finite incomplete frontier means misses are not negative evidence'}


def preserve_proposal(graph: LivingGraph, parent: RewriteGrammar, proposal: dict,
                      training: Sequence[Example], heldout: Sequence[Example]) -> dict:
    """Archive a deterministic recomputed candidate with synthetic lineage as PENCIL only."""
    if graph.scope != parent.scope:
        raise ValueError('scope mismatch')
    # Explicit exact recomputation disallows forged scores and altered source cases.
    budget = proposal.get('candidate_space_size') if isinstance(proposal,dict) else None
    if type(budget) is not int or budget <= 0:
        raise ValueError('missing bounded candidate-space receipt')
    repeated = propose_revision(parent,training,heldout,candidate_budget=budget)
    if repeated['status']!='PENCIL_GRAMMAR_REVISION_PROPOSED':
        raise ValueError('cannot preserve unproven or partial proposal')
    protected=('rule','parent_fingerprint','proposed_fingerprint','training','heldout','existing_grammar_gap')
    if any(proposal.get(k)!=repeated[k] for k in protected):
        raise ValueError('proposal evidence mismatch')
    identity=stable_id('grammar-revision:',{
        'rule':proposal['rule'],'parent':parent.fingerprint,
        'train_ids':[e.identity for e in training], 'test_ids':[e.identity for e in heldout]})
    graph.add_node(identity,kind='reason_grammar_candidate',label=proposal['rule']['name'],
                   payload={'proposal':proposal,'authority':'NONE'},source_root='local:synthetic-induction')
    witnesses=[('proposal',identity)]
    for role,cases in [('training_case',training),('heldout_case',heldout)]:
        for case in cases:
            eid=stable_id('case:',case.data())
            graph.add_node(eid,kind='synthetic_grammar_case',label=case.identity,
                           payload=case.data(),source_root=case.source_root)
            witnesses.append((role,eid))
    graph.add_relation('grammar_revision_proposal_witnesses',witnesses,
                       source_root='local:synthetic-induction',
                       note={'admission':'PENCIL_ONLY','scope':graph.scope})
    return {'status':'PENCIL_REVISION_ARCHIVED','node_id':identity,
            'training_cases':len(training),'heldout_cases':len(heldout),
            'authority':'NONE'}


def case_from_document(value: dict) -> Example:
    if not isinstance(value,dict) or set(value)!={'id','before','after','expected','source_root'}:
        raise ValueError('invalid example object')
    if not isinstance(value['before'],list) or not isinstance(value['after'],list):
        raise ValueError('example tokens must be arrays')
    return Example(value['id'],tuple(value['before']),tuple(value['after']),
                   value['expected'],value['source_root'])


def run_document(doc: dict) -> dict:
    if not isinstance(doc,dict) or set(doc)!={'parent_grammar','training','heldout','candidate_budget','seeds','targets','fork_budget'}:
        raise ValueError('unknown or missing document field')
    from living_graph import grammar_from_document
    parent=grammar_from_document(doc['parent_grammar'])
    train=[case_from_document(x) for x in doc['training']]
    held=[case_from_document(x) for x in doc['heldout']]
    candidate=propose_revision(parent,train,held,candidate_budget=doc['candidate_budget'])
    if candidate['status']!='PENCIL_GRAMMAR_REVISION_PROPOSED':
        return {'proposal':candidate,'fork':{'status':'HOLD','authority':'NONE'}}
    fork=compare_fork(parent,candidate['rule'],doc['seeds'],doc['targets'],
                      work_budget=doc['fork_budget'])
    return {'proposal':candidate,'fork':fork}
