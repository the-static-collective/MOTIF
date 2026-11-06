"""Fixed synthetic heldout comparison; intentionally includes OOD exceptions.

A memorize-exact-pairs baseline and the original grammar are matched controls.
This is developer-authored data, not an independently sourced benchmark.
"""
import json
import random
from demo import scenario
from grammar_invention import Example, propose_revision, rule_from_proposal, score, predicts


def run(seed=20261106):
    parent,train,_=scenario()
    rng=random.Random(seed)
    held=[]
    for i in range(100):
        label='unseen-'+str(i)+'-'+str(rng.randrange(1000000))
        held.append(Example('new-positive-'+str(i),(label,'bud'),(label,'branch'),True,
                            'synthetic:test-positive'))
        held.append(Example('new-negative-'+str(i),(label,'bud'),(label,'leaf'),False,
                            'synthetic:test-negative'))
    # Context restrictions absent from the candidate vocabulary. This is a
    # deliberately adversarial control; we should report its false positives.
    for i in range(20):
        name='exception-'+str(i)
        held.append(Example('unmodeled-exception-'+str(i),(name,'bud'),(name,'branch'),False,
                            'synthetic:unmodeled-context-exception'))
    candidate=propose_revision(parent,train,held,candidate_budget=10**6)
    assert candidate['status']=='PENCIL_GRAMMAR_REVISION_PROPOSED'
    rule=rule_from_proposal(candidate['rule'])
    parent_correct=sum(any(predicts(r,c) for r in parent.rules)==c.expected for c in held)
    memorized={(e.before,e.after) for e in train if e.expected}
    memorization_correct=sum(((e.before,e.after) in memorized)==e.expected for e in held)
    return {'experiment':'GEOM-009 fixed-seed synthetic grammar induction vs controls',
            'seed':seed,'train_cases':len(train),'heldout_cases':len(held),
            'clean_positive':100,'clean_negative':100,'unmodelled_context_negatives':20,
            'proposed_rule':candidate['rule'],
            'parent_grammar_heldout_correct':parent_correct,
            'memorize_training_exact_pairs_heldout_correct':memorization_correct,
            'induced_rule_heldout_correct':candidate['heldout']['correct'],
            'induced_rule_heldout_false_positives':candidate['heldout']['false_positives'],
            'induced_rule_heldout_true_positives':candidate['heldout']['true_positives'],
            'baseline_context':'same synthetic generator; trivial classical inductive baseline could match the rule',
            'interpretation':'exceptions expose unmodeled context; withheld results do not authorize changing any live graph',
            'authority':'NONE','instrument':'PENCIL'}

if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))
