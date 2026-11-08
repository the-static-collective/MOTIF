"""Matched synthetic evidence-cost benchmark; no test labels enter proposal choice.

This is a model-matched diagnostic of identifiability, not a general scientific
breakthrough or validation of claimed real-world provenance/anchors.
"""
from hashlib import sha256
from random import Random
import json
from provenanceprobe import (Belief, HYPOTHESES, sample_case, propose_inquiry)


def trial(hypothesis: str, seed: int, *, active: bool) -> bool:
    rng = Random(int.from_bytes(sha256(f'probe001:benchmark:{hypothesis}:{seed}'.encode()).digest()[:8], 'big'))
    belief = Belief()
    for j in range(100):
        row,_ = sample_case(hypothesis, f'pre-{seed}-{j}', rng)
        belief = belief.ingest(row)
    # Freeze the inquiry decision BEFORE generating subsequent evidence.
    proposed = propose_inquiry(belief, frozenset({'AUDIT_PAIR','VERIFY_ANCHOR'}), 6)
    if active and proposed.query != 'VERIFY_ANCHOR':
        raise AssertionError('the frozen ambiguous posterior should nominate a truth anchor')
    # Equal information-acquisition budget: 2 verified anchors at cost 3 each,
    # versus 6 conventional pair readings at cost 1 each.
    for j in range(2 if active else 6):
        row,_ = sample_case(hypothesis, f'post-{seed}-{j}',rng,anchor=active)
        belief = belief.ingest(row)
    # Only the independent evaluator knows the hypothesis here.
    return belief.classification()['leading_model'] == hypothesis


def benchmark(repeats: int = 50) -> dict:
    if repeats < 1:
        raise ValueError('positive repeats required')
    result = {}
    for h in HYPOTHESES:
        active = sum(trial(h,s,active=True) for s in range(repeats))
        pair_only = sum(trial(h,s,active=False) for s in range(repeats))
        result[h] = {'anchor_success':active,'pair_only_success':pair_only,'trials':repeats}
    n = repeats*len(HYPOTHESES)
    return {'scope':'fixed-known-accuracy four-polarity synthetic matched-model test',
            'cases':n, 'query_cost_budget':6,'anchor_queries':2,'pair_queries':6,
            'with_informative_anchor_accuracy':sum(x['anchor_success'] for x in result.values())/n,
            'matched_cost_pairs_only_accuracy':sum(x['pair_only_success'] for x in result.values())/n,
            'by_family':result,'real_queries':0}


if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
