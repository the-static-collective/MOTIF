"""Frozen classical controls. Does not use held-out data to fit the adapter."""
import json
from dataclasses import replace
from adapterinvention import AdapterRefusal,check,invent,trusted_fixture
from selfmirror import Policy,preview_motif003


def benchmark() -> dict:
    training=trusted_fixture('train',64)
    validation=trusted_fixture('validation',64)
    adapter=invent(training,validation)
    test=trusted_fixture('test',200)
    exact=check(adapter,test)
    # The existing handwritten preview function provides the strong control.
    # It should tie a correct inferred adapter rather than be quietly omitted.
    manual_agreement=0
    emitted=0
    for start in range(0,200,4):
        rows=[dict(e.row,truncated=False) for e in test[start:start+4]]
        for j,row in enumerate(rows): row['roles']=('test-actor',f'object-{start+j}')
        proposal=adapter.transform(rows)
        actual=proposal[Policy(2,1).choose(proposal)].name
        expected=preview_motif003(rows,Policy(2,1))['selection']
        manual_agreement+=actual==expected
        emitted+=1
    # Strong negative control: field names and types remain intact, but an
    # upstream producer silently changes which numeric quantities occupy them.
    # No fixed schema/type adapter can detect this without semantic checks.
    semantic_shift=tuple(replace(e,row={**e.row,
                            'immediate_delta':e.row['reachable_after_first_move'],
                            'reachable_after_first_move':e.row['immediate_delta']})
                         for e in test if e.row['immediate_delta']>=0)
    # Remove negative-reach cases; all these inputs pass typed validation.
    shifted=check(adapter,semantic_shift)
    missing=0
    for e in test:
        row=dict(e.row)
        row.pop('new_affordances')
        try:
            adapter.transform([row])
        except AdapterRefusal:
            missing+=1
    return {
        'experiment':'ADAPTER-INVENTION-001',
        'scope':'supervised finite DSL, frozen synthetic splits, no external actions',
        'expressions_inspected':adapter.examined,
        'hidden_contract_match':{'synthesized':exact['matched'],'of':exact['tested'],
                                 'manual_reference':'explicit fixture labels'},
        'actual_downstream_policy_choice_agreement_with_existing_hand_adapter':
            {'synthesized':manual_agreement,'of':emitted},
        'naive_direct_feed':'HOLD_TYPE_MISMATCH',
        'adversarial_missing_field_refusals':{'held':missing,'of':len(test)},
        'adversarial_semantic_shift':{'matched_original_labels':shifted['matched'],
                                     'of':shifted['tested'],
                                     'detectable_from_shape_alone':False},
        'claims':{'novel_algorithm':False,'unrestricted_adapter_invention':False,
                  'semantic_robustness':False,'automated_deployment':False},
    }

if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
