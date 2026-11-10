"""LANGUAGE-GROWTH-001 bounded classical controls, fully reproducible."""
from languagegrowth import (trials, grow, diagnose, test, ablation,
                            measured_outcome, path_three_reference,
                            PATCHES, ORIGINAL_GRAMMAR)
import json


def benchmark():
    train,validation=trials('train'),trials('validation')
    test_data,ood=trials('test',30),trials('ood',30)
    main=grow(train,validation)
    train_diagnosis=diagnose(train)
    scored=test(main,test_data)
    scored_ood=test(main,ood)
    random={}
    for budget in (3,8):
        outcomes=[]
        for seed in range(10):
            candidate=grow(train,validation,budget=budget,selection='random',seed=seed)
            outcomes.append(candidate.status=='I_PATCH_VALIDATED')
        random[str(budget)]={'validated':sum(outcomes),'of':len(outcomes)}
    total=tuple(test_data)+tuple(ood)
    strong=sum(measured_outcome(e)==path_three_reference(e.probe.graph,e.probe.a,e.probe.b)
               for e in total)
    return {
        'experiment':'LANGUAGE-GROWTH-001',
        'scope':'synthetic graph edge addition; finite meta-grammar; no outside actions',
        'old_language_candidates':len(ORIGINAL_GRAMMAR),
        'old_language':{'status':train_diagnosis['status'],
                        'counterexample_after':train_diagnosis['inspections']},
        'patches_offered':tuple(PATCHES),
        'new_expressions_enumerated':main.examined,
        'selected_language_edit':main.operator,
        'selected_expression':main.formula.text() if main.formula else None,
        'interventions':main.observations,
        'validation_status':main.status,
        'new_language_test':scored,
        'new_language_ood':scored_ood,
        'constant_zero':{'matched':scored['constant_zero_matches']+scored_ood['constant_zero_matches'],
                         'of':len(total)},
        'handwritten_strong_classical':{'matched':strong,'of':len(total)},
        'random_selection_same_grammar':random,
        'operator_removed':ablation(train,validation)['COUNT_BINDING_PAIRS'],
        'general_math_invention':False,
        'novel_vs_classical_superiority':False,
    }

if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
