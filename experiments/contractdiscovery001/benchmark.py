"""Frozen classical and adversarial controls for CONTRACT-DISCOVERY-001."""
import json
from contractdiscovery import (
    CHANNELS, trials, discover, measure, check_relation,
    exhaustive_classical_control, test_heldout, primitive,
)


def benchmark() -> dict:
    learner=discover(trials('train'),trials('validation'))
    if learner.relation is None:
        raise RuntimeError('fixture does not identify a unique finite linear contract')
    test=trials('test')
    ood=trials('ood')
    classical=exhaustive_classical_control(measure(t) for t in trials('train'))
    limited=discover(tuple(t for t in trials('train') if t.operation in
                           {'isolated','leaf','subdivide'}),trials('validation'),min_probe_count=3)
    adversarial_detected=0
    adversarial_undetectable=0
    for t in test:
        sample=measure(t)
        for i in range(len(CHANNELS)):
            modified=list(sample)
            modified[i]+=1
            if check_relation(learner,tuple(modified)):
                adversarial_undetectable+=1
            else:
                adversarial_detected+=1
    # Joint, coordinated errors can preserve any single linear relation.
    correlated=list(measure(test[0]))
    i=next(k for k,c in enumerate(learner.relation) if c)
    j=next(k for k,c in enumerate(learner.relation) if c and k!=i)
    correlated[i]+=learner.relation[j]
    correlated[j]-=learner.relation[i]
    return {
        'experiment':'CONTRACT-DISCOVERY-001',
        'training_probes_executed':learner.inspections,
        'independent_rank':learner.rank,
        'candidate_relation':learner.relation,
        'classical_bruteforce_candidates':len(classical),
        'classical_bruteforce_equal':classical==(learner.relation,),
        'underdiverse_training_status':limited.status,
        'test':test_heldout(learner,test),
        'ood_unseen_interventions':test_heldout(learner,ood),
        'single_coordinate_type_correct_mutations':{
             'detected':adversarial_detected,
             'not_detected':adversarial_undetectable,
             'total':len(test)*len(CHANNELS)},
        'coordinated_two_channel_attack_detected':not check_relation(learner,tuple(correlated)),
        'candidate_contract_status':learner.status,
        'universal_proof':False,
        'new_mathematics':False,
        'real_world_actions':0,
        'external_evidence_acquired':False,
    }


if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
