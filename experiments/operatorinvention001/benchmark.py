"""Frozen tests for explicit source-code synthesis; no test split informs fitting."""
from __future__ import annotations
import json
from operatorinvention import Program,grammar,discover,heldout,trials
from languagegrowth import diagnose


def benchmark() -> dict:
    train=trials('train',36)
    valid=trials('validation',24)
    four=discover(train,valid)
    triangle=discover(train,valid,task='triangles')
    t=heldout(four,trials('test',30))
    o=heldout(four,trials('ood',25))
    u=heldout(triangle,trials('ood',25))
    no_second=discover(train,valid,candidates=grammar(allow_two_binders=False))
    random_three=[discover(train,valid,selection='random',seed=i,budget=3)
                  for i in range(20)]
    random_eight=[discover(train,valid,selection='random',seed=i,budget=8)
                  for i in range(20)]
    return {
        'experiment':'OPERATOR-INVENTION-001',
        'scope':'finite AST grammar, synthetic simple undirected graphs; local code generation only',
        'old_237_expression_grammar':diagnose(train)['status'],
        'candidate_loop_programs':four.candidate_count,
        'active_probes':four.interventions,
        'learned_code_ast':{'binders':four.program.binders,'edge_atoms':four.program.atoms,
                            'distinct':four.program.distinct},
        'old_family_hidden':t,
        'larger_ood':o,
        'second_task_triangle_ood':u,
        'no_two_loop_grammar':no_second.status,
        'random_probes_three':{'validated':sum(d.usable for d in random_three),'of':len(random_three)},
        'random_probes_eight':{'validated':sum(d.usable for d in random_eight),'of':len(random_eight)},
        'strong_baseline':'prewritten path_three_reference ties synthesized result',
        'claimed_historical_novelty':False,
        'can_synthesize_unrestricted_python':False,
        'new_real_world_actions':0,
    }

if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
