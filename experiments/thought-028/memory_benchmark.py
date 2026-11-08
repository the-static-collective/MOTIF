"""Offline evidence-memory research: source fixtures, no LLM calls.

No target policy labels or full-domain answers are supplied to candidate synthesis.
Synthetic 3-bit evaluator supplies bounded development observations only.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
for family in ('thought-025','thought-026','thought-027'):
    path=str(HERE.parent/family)
    if path not in sys.path:sys.path.insert(0,path)
from specimens import BY_KEY, Specimen
from stages import stage_trial
from stage_fixtures import DeterministicStages
from proof_memory import ProofLibrary
from weave import EvidenceStore, catalog, licenses, investigate, enumerate_compositions, digest

SCHEMA='motif.thought028.offline-proof-weave-benchmark.v1'


def new_cases():
    # New authored example reuses the mathematical XOR structure, with different
    # identifiers/phrasing; this is NOT a blind independent language test.
    return {
        'toggle_equipment': Specimen(
            'toggle_equipment',
            'The maintenance log lists equipment currently enabled and a second log of items to toggle. '
            'Each item named by the change log flips its enabled state; other items remain as before.',
            (('equipment_state','enabled equipment'),('change_log','toggles to perform')),
            'XOR',('equipment_state','change_log')),
        'reverse_recall': Specimen(
            'reverse_recall',
            'Return recalls that are not in the shelf inventory, not the converse.',
            (('shelf_register','shelf items'),('recall_register','recalled items')),
            'DIFF',('recall_register','shelf_register')),
        'ternary_unknown': Specimen(
            'ternary_unknown',
            'Statements may be true, false or unknown, and unknown must remain distinguishable from false.',
            (('beliefs','open-world beliefs'),('update','new facts')),
            'TERNARY',('beliefs','update'),False,'NON_BOOLEAN'),
    }


def seeds(keys=('food_safe','food_donations')):
    src=ProofLibrary()
    proof=[]
    for k in keys:
        trial=stage_trial(BY_KEY[k],DeterministicStages())
        proof.append(src.admit(BY_KEY[k],trial,origin='SCRIPTED_026_FIXTURE_NOT_GENERATIVE_LLM'))
    return EvidenceStore(proof,BY_KEY)


def run():
    new=new_cases()
    store=seeds()
    old_tasks=['cancel_or_add','food_recalled_elsewhere']
    # Run a trial independently per strategy; a frozen counterexample in one
    # arm is never returned as input to another arm's target-specific search.
    before=investigate(BY_KEY['cancel_or_add'],store,mode='direct')
    composed=investigate(BY_KEY['cancel_or_add'],store,mode='compose')
    evidence=None
    if composed['status']=='REVIEW_SCOPED_CANDIDATE_NOT_INSTALLED':
        evidence=store.add_derived(BY_KEY['cancel_or_add'],composed)
    store.add_task(new['toggle_equipment'])
    store.add_task(new['reverse_recall'])
    store.add_task(new['ternary_unknown'])
    transferred=investigate(new['toggle_equipment'],store,mode='retrieved')
    reversed_roles=investigate(new['reverse_recall'],store,mode='retrieved')
    cannot_booleanize=investigate(new['ternary_unknown'],store,mode='retrieved')
    # Deliberately source-owned threshold semantics. Existing 3-bit set grammar
    # cannot express an output where one output bit depends on another input bit;
    # here we instantiate a target only to test rejection, not model comprehension.
    from specimens import independent_target
    from weave import expression_signature
    grammar_signatures={tuple(x['signature']) for x in enumerate_compositions(licenses(store.sources))}
    threshold=tuple(7 if a.bit_count()>=2 else 0 for a in range(8) for _ in range(8))
    proof_bank=store.export()
    restored=EvidenceStore.load(proof_bank,store.registry)
    out={'schema':SCHEMA,'source_fixture_provenance':'SCRIPTED_SOURCE_OWNER_AWARE_NOT_LLM',
         'model_generations':0,'initial_source_proofs':2,
         'licensed_operators':sorted(licenses(store.sources)),
         'composition_candidate_semantics':len(grammar_signatures),
         'initial_direct_attempt':before,
         'new_compositional_attempt':composed,
         'derived_card':evidence,
         'retained_task_transfer':transferred,
         'reversed_role_transfer':reversed_roles,
         'non_boolean_hold':cannot_booleanize,
         'threshold_outside_licensed_grammar':threshold not in grammar_signatures,
         'serialized_store_reverified':restored.verify_all(),
         'serialized_proof_cards':len(restored.sources)+len(restored.derived),
         'store':proof_bank,
         'source_owner_oracle_required_for_new_task':True,
         'task_meaning_not_inferred_from_unfamiliar_language':True,
         'no_post_frozen_model_repair':True,
         'installed':False,'external_authority':'NONE'}
    out['receipt_digest']=digest(out)
    return out

if __name__=='__main__':
    p=Path(__file__).with_name('offline-results.json')
    result=run()
    p.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=True)+'\n',encoding='utf-8')
    print(json.dumps({'model_calls':0,'license':result['licensed_operators'],
       'candidate_semantics':result['composition_candidate_semantics'],
       'direct':(result['initial_direct_attempt']['status'],result['initial_direct_attempt']['development_queries']),
       'composition':(result['new_compositional_attempt']['status'],result['new_compositional_attempt']['development_queries']),
       'reused':(result['retained_task_transfer']['status'],result['retained_task_transfer']['development_queries']),
       'reversed_roles':(result['reversed_role_transfer']['status'],result['reversed_role_transfer']['development_queries']),
       'negative_hold':result['non_boolean_hold']['status'],
       'out_of_grammar':result['threshold_outside_licensed_grammar'],
       'saved':result['serialized_proof_cards'],
       'installed':False},indent=2))
