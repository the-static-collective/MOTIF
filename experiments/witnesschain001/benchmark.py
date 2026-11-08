"""Equal-cost synthetic comparison; entirely predetermined independent cases.

Reference correctness is an ASSUMPTION. A tampered reference is an adversary.
All results remain classical finite-model simulations, not authenticated truth.
"""
from __future__ import annotations
import json
from witnesschain import HYPOTHESES, State, TruthReceipt, flip, name, synthetic_cases


def benchmark(seeds_per_regime: int = 25) -> dict:
    if not isinstance(seeds_per_regime, int) or seeds_per_regime < 1:
        raise ValueError('positive integer seeds required')
    results = []
    for mechanism in HYPOTHESES:
        for seed in range(seeds_per_regime):
            # 100 observed events, then 16 ordinary observations or 4 synthetic
            # truth receipts for 4 already recorded events. Both cost 16.
            cases = synthetic_cases(mechanism, seed, 116)
            base = State()
            for event, _ in cases[:100]:
                base = base.add(event)
            repeated = base
            for event, _ in cases[100:]:
                repeated = repeated.add(event)
            verified, compromised = base, base
            for event, truth in cases[:4]:
                verified = verified.verify(TruthReceipt(event.id, truth, 'fixture-oracle-assumed'))
                compromised = compromised.verify(TruthReceipt(event.id, flip(truth), 'tampered-fixture'))
            classify = lambda s: s.decision('absolute_polarity')
            r_base, r_verified, r_compromised = map(classify,(repeated,verified,compromised))
            relative=base.decision('primary_audit_alignment')
            expected_relative='same' if mechanism[0]==mechanism[1] else 'opposite'
            results.append({
                'true':name(mechanism),
                'ordinary_forced_correct':r_base['candidate']==name(mechanism),
                'ordinary_held':r_base['status']=='HOLD_GLOBAL_FLIP_SYMMETRY',
                'reference_forced_correct':r_verified['candidate']==name(mechanism),
                'reference_issued':r_verified['status']=='I_CONDITIONAL_ON_FIXTURE_REFERENCE',
                'reference_issued_correct':(r_verified['status']=='I_CONDITIONAL_ON_FIXTURE_REFERENCE'
                                            and r_verified['candidate']==name(mechanism)),
                'tampered_forced_correct':r_compromised['candidate']==name(mechanism),
                'tampered_issued_wrong':(r_compromised['status']=='I_CONDITIONAL_ON_FIXTURE_REFERENCE'
                                         and r_compromised['candidate']!=name(mechanism)),
                'relative_correct':relative['candidate']==expected_relative,
                'relative_issued':relative['status']=='I_RELATIVE_MODEL_ONLY',
            })
    n=len(results)
    rate=lambda key:round(sum(int(row[key]) for row in results)/n,6)
    return {
        'experiment':'WITNESS-CHAIN-001',
        'scenario_count':n,
        'synthetic_regimes':len(HYPOTHESES),
        'observed_before_budget':100,
        'equal_extra_budget':16,
        'ordinary_extra_triplets':16,
        'fixture_truth_receipts':4,
        'without_reference_forced_top1_accuracy':rate('ordinary_forced_correct'),
        'without_reference_hold_rate':rate('ordinary_held'),
        'fixture_reference_forced_top1_accuracy':rate('reference_forced_correct'),
        'fixture_reference_issued_fraction':rate('reference_issued'),
        'fixture_reference_issued_correct_fraction_all':rate('reference_issued_correct'),
        'tampered_reference_forced_top1_accuracy':rate('tampered_forced_correct'),
        'tampered_reference_issued_wrong_fraction_all':rate('tampered_issued_wrong'),
        'relative_alignment_top1_accuracy':rate('relative_correct'),
        'relative_alignment_issued_fraction':rate('relative_issued'),
        'reference_authentication_verified':False,
        'real_experiments_run':0,
        'claim':'Known independent channel likelihoods + reliable synthetic truth fixture are assumed; no real-world source validity established',
    }


if __name__=='__main__':
    print(json.dumps(benchmark(), indent=2,sort_keys=True))
