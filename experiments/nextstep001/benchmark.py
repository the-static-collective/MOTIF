"""Deterministic fixture sweep. Measures protocol behavior, NOT intelligence."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "witnesschain001"))
from witnesschain import State, HYPOTHESES, synthetic_cases, TruthReceipt
from nextstep import Goal, advance, fingerprint


def benchmark():
    counters = dict(worlds=0, automatically_executed_local_analyses=0,
                    external_actions=0, ledger_mutations=0,
                    conditional_or_held_unchanged=0,
                    verification_proposed_not_collected=0,
                    symmetry_detected=0)
    for mechanism in HYPOTHESES:
        for seed in range(5):
            world = State()
            fixtures = synthetic_cases(mechanism, seed, 60)
            for event, _ in fixtures:
                world = world.add(event)
            original = fingerprint(world)
            r = advance(world, Goal('absolute_polarity',budget=3,max_steps=3))
            counters['worlds'] += 1
            counters['automatically_executed_local_analyses'] += len(r['steps'])
            counters['external_actions'] += r['real_world_actions']
            counters['ledger_mutations'] += int(fingerprint(world) != original)
            counters['conditional_or_held_unchanged'] += int(
                r['orientation']['requested_answer']['status']=='HOLD_GLOBAL_FLIP_SYMMETRY')
            counters['verification_proposed_not_collected'] += sum(
                s['action_executed']=='DESIGN_PROBE' and
                not s['result']['truth_attestation_collected'] for s in r['steps'])
            counters['symmetry_detected'] += sum(
                s['action_executed']=='TEST_SYMMETRY' and
                s['result']['result']=='GLOBAL_FLIP_INVARIANCE_VERIFIED_IN_DECLARED_MODEL'
                for s in r['steps'])
    return dict(experiment='NEXT-STEP-001', scope='8 hypothesized synthetic regimes × 5 seeds',
                protocol=counters,
                note='No new independent evidence or real action; counted executions are local read-only analyses.')


if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
