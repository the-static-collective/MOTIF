"""Explicit classical-conjunction baseline, frozen synthetic heldout & abstentions."""
from __future__ import annotations
from itertools import combinations
import json

from reason_lab import ConditionalRule, score, guarded_from_data
from demo import initial_grammar, development_rounds, heldout, SCOPE
from reason_lab import stage


def independent_classical_learner(base, feedback):
    """Separate direct bitmask search; does not invoke inventor or its generator."""
    pos=[c for c in feedback if c.expected]
    common=dict(pos[0].facts)
    for c in pos[1:]:
        common={k:v for k,v in common.items() if (k,v) in c.facts}
    candidates=[]
    items=sorted(common.items())
    for mask in range(2**len(items)):
        bits=[items[i] for i in range(len(items)) if mask & (1<<i)]
        # Direct string comparison; not ConditionalRule.decide, independent
        # of the main learner's scoring and candidate iterator.
        correct=0
        for case in feedback:
            applicable=any(out==case.after for _,out in base.outcomes(case.before))
            prediction=applicable and all(dict(case.facts).get(k)==v for k,v in bits)
            correct+=prediction==case.expected
        if correct==len(feedback):
            candidates.append((len(bits),tuple(bits)))
    return min(candidates)[1] if candidates else None


def run():
    parent,base,_=initial_grammar()
    early,later=development_rounds()
    a=stage(parent,base,early)
    early_guard=guarded_from_data(a['inventor']['rule'])
    feedback=early+later
    b=stage(parent,base,feedback,active=early_guard)
    final_guard=guarded_from_data(b['inventor']['rule'])
    classical=independent_classical_learner(base,feedback)
    frozen=heldout(seed=20261106)
    baseline=ConditionalRule(base,(),SCOPE)
    scores={
        'unconditional':score(baseline,frozen),
        'first_revision':score(early_guard,frozen),
        'second_revision':score(final_guard,frozen),
        'matched_classical_conjunction':score(ConditionalRule(base,classical,SCOPE),frozen),
        'always_false':{'correct':sum(not x.expected for x in frozen),'total':len(frozen)},
    }
    return {'experiment':'GEOM-010 paired classical conditional induction',
            'frozen_seed':20261106,'developer_authored_synthetic':True,
            'development_cases':len(feedback),'heldout_cases':len(frozen),
            'best_classical_conjunction':dict(classical),
            'proposed_conjunction':dict(final_guard.guard),
            'classical_match':tuple(final_guard.guard)==classical,
            'scores':scores,
            'interpretation':'Both methods tie on synthetic features. No novel algorithm or generalized self-improvement is demonstrated.',
            'authority':'NONE','instrument':'PENCIL'}

if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))
