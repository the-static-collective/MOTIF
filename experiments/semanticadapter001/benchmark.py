"""Frozen comparison: schema-only vs contract-gated adapter; synthetic only."""
import json
from semanticadapter import (invent, probes, observe, target_contract, SemanticRefusal,
                              adversarial_shift, preview_policy, check)
from selfmirror import Policy, preview_motif003


def benchmark():
    bridge=invent(probes('train'),probes('validation'))
    tests=probes('test')
    hold=check(bridge,tests)
    chosen=matched=complete=0
    for p in tests:
        rows=observe(p)
        if any(x['truncated'] for x in rows):
            continue
        for policy in (Policy(0,0),Policy(2,1)):
            result=preview_policy(bridge,p,policy)
            if result['status']=='I_VERIFIED_LOCAL_PROPOSAL':
                chosen+=1
                matched+=result['choice']==preview_motif003(list(rows),policy)['selection']
            complete+=1
    schema_only_accept=semantic_hold=eligible=equal=bad_type=0
    for p in probes('ood'):
        for row in observe(p):
            if row['immediate_delta']==row['reachable_after_first_move']:
                equal+=1; continue
            if row['immediate_delta']<0:
                bad_type+=1; continue
            result=adversarial_shift(bridge,p,row)
            eligible+=1
            schema_only_accept+=result['typed_only_accepts']
            semantic_hold+=result['semantic_gate'].startswith('HOLD')
    return {
        'experiment':'SEMANTIC-ADAPTER-001',
        'hypothesis_grammar':'22 predeclared expressions, 5 Move outputs',
        'observed_worlds':{'train':len(probes('train')),'validation':len(probes('validation')),
                           'test':len(tests),'ood_attack':len(probes('ood'))},
        'target_labeled_Move_examples_supplied':0,
        'behavioral_contracts_hand_declared':True,
        'same_synthetic_module_dynamics_in_train_and_test':True,
        'unmodified_test':hold,
        'strong_manual_bridge_agreement':{'matched':matched,'out_of':complete},
        'semantic_swap_attack':{'eligible_noncollision_type_valid':eligible,
                                'type_only_accepts':schema_only_accept,
                                'contract_gate_refuses':semantic_hold,
                                'value_collisions':equal,
                                'negative_reach_type_refusals_excluded':bad_type},
        'classical_method':'finite DSL enumeration + independent recomputation/metamorphic contract tests',
        'known_common_mode_limit':'Same incorrect simulator/contract can agree and remain undetected',
        'external_actions':0,'novel_general_algorithm':False,
    }


if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2,sort_keys=True,default=str))
