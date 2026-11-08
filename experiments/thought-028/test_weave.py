"""THOUGHT-028 proof-carrying search tests. All scripted; no LLM claims."""
import copy
import json
import sys
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
for family in ('thought-025','thought-026','thought-027'):
    sibling=str(HERE.parent/family)
    if sibling not in sys.path:sys.path.insert(0,sibling)
if str(HERE) in sys.path:sys.path.remove(str(HERE))
sys.path.insert(0,str(HERE))
from specimens import BY_KEY, Specimen
from proof_memory import ProofError,digest
from weave import (EvidenceStore, normalize_sources, licenses, catalog,
                   enumerate_compositions, expression_signature, investigate,
                   best_probe, DERIVED_SCHEMA)
from memory_benchmark import seeds, new_cases, run

class WeaveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store=seeds()

    def test_source_proofs_revalidated_on_every_catalog_read(self):
        self.assertTrue(self.store.verify_all())
        c=catalog(BY_KEY['cancel_or_add'],self.store)
        self.assertGreater(len(c),0)
        original=next(iter(self.store.sources))
        altered=copy.deepcopy(self.store.sources[original])
        altered['relation']='UNION'
        with self.assertRaises(ProofError):normalize_sources([altered],BY_KEY)
        self.assertFalse(any(x['origin']=='RETRIEVED_PROOF' for x in c.values()))

    def test_operator_licenses_require_correctly_certified_prior_math(self):
        found=licenses(self.store.sources)
        self.assertEqual(set(found),{'difference','union'})
        only_difference=seeds(('food_safe',))
        self.assertEqual(set(licenses(only_difference.sources)),{'difference'})
        for x in enumerate_compositions(licenses(only_difference.sources)):
            self.assertNotIn('union',json.dumps(x['expression']))

    def test_composition_enumeration_does_not_ask_target_oracle(self):
        allowed=licenses(self.store.sources)
        entries=enumerate_compositions(allowed)
        self.assertEqual(len(entries),8)
        self.assertEqual(len({tuple(x['signature']) for x in entries}),8)
        for x in entries:
            self.assertEqual(tuple(x['signature']),expression_signature(x['expression']))

    def test_direct_reuse_can_pass_dev_and_fail_frozen(self):
        r=investigate(BY_KEY['cancel_or_add'],self.store,mode='direct')
        self.assertEqual(r['status'],'HOLD_FROZEN_COUNTEREXAMPLE_NO_POST_AUDIT_REPAIR')
        self.assertEqual(r['development_queries'],2)
        self.assertEqual(r['frozen']['correct'],27)
        self.assertIsNone(r['trusted_runtime'])
        self.assertFalse(r['installed'])

    def test_composed_candidate_is_independently_verified(self):
        out=investigate(BY_KEY['cancel_or_add'],self.store,mode='compose')
        self.assertEqual(out['status'],'REVIEW_SCOPED_CANDIDATE_NOT_INSTALLED')
        self.assertEqual(out['selected_origin'],'LICENSED_COMPOSITION')
        self.assertEqual(out['development_queries'],2)
        self.assertEqual(out['frozen']['correct'],64)
        self.assertEqual(out['trusted_runtime']['correct'],64)
        self.assertEqual(set(out['source_proof_digests']),set(self.store.sources))

    def test_derived_card_preserves_provenance_and_remains_scoped(self):
        store=seeds()
        target=BY_KEY['cancel_or_add']
        run=investigate(target,store,mode='compose')
        card=store.add_derived(target,run)
        self.assertEqual(card['schema'],DERIVED_SCHEMA)
        self.assertEqual(card['task_key'],target.key)
        self.assertEqual(len(card['parent_proof_digests']),2)
        self.assertTrue(store.verify_all())
        self.assertFalse(card['origin_authenticated'])
        self.assertFalse(card['installed'])

    def test_persistent_memory_roundtrip_never_certifies_new_story_by_itself(self):
        store=seeds()
        derived=store.add_derived(BY_KEY['cancel_or_add'],
                                  investigate(BY_KEY['cancel_or_add'],store,mode='compose'))
        for target in new_cases().values():store.add_task(target)
        packet=store.export()
        restored=EvidenceStore.load(json.loads(json.dumps(packet)),store.registry)
        self.assertTrue(restored.verify_all())
        self.assertEqual(len(restored.sources),2)
        self.assertEqual(len(restored.derived),1)
        # New task still requires source-owner oracle calls even with a matching proof.
        found=investigate(new_cases()['toggle_equipment'],restored,mode='retrieved')
        self.assertEqual(found['status'],'REVIEW_SCOPED_CANDIDATE_NOT_INSTALLED')
        self.assertEqual(found['development_queries'],2)
        self.assertEqual(found['selected_origin'],'RETRIEVED_PROOF')
        self.assertEqual(found['source_proof_digests'],[derived['proof_digest']])
        self.assertEqual(found['frozen']['correct'],64)

    def test_explicitly_reversed_roles_revalidated(self):
        store=seeds()
        t=new_cases()['reverse_recall'];store.add_task(t)
        out=investigate(t,store,mode='direct')
        self.assertEqual(out['proposal']['bindings'],
                         {'current':'recall_register','event':'shelf_register'})
        self.assertEqual(out['frozen']['correct'],64)

    def test_unknown_and_three_valued_data_fail_closed_without_oracle(self):
        task=new_cases()['ternary_unknown']
        out=investigate(task,self.store,mode='compose')
        self.assertEqual(out['development_queries'],0)
        self.assertTrue(out['status'].startswith('HOLD_'))
        for fake in ('freeform','arbitrary exec','all'):
            with self.assertRaises(ProofError):catalog(BY_KEY['cancel_or_add'],self.store,mode=fake)

    def test_derived_card_tamper_rejected_even_if_digest_is_recomputed(self):
        st=seeds()
        legit=st.add_derived(BY_KEY['cancel_or_add'],
                             investigate(BY_KEY['cancel_or_add'],st,mode='compose'))
        tamper=copy.deepcopy(legit)
        tamper['proposal']['expression']={'ref':'state.on'}
        tamper['proposal_digest']=digest(tamper['proposal'])
        tamper['function_sha256']=digest(expression_signature(tamper['proposal']['expression']))
        tamper['proof_digest']=digest({k:v for k,v in tamper.items() if k!='proof_digest'})
        st.derived={tamper['proof_digest']:tamper}
        with self.assertRaises(ProofError):st.verify_all()

    def test_missing_parent_certificate_refused(self):
        st=seeds()
        card=st.add_derived(BY_KEY['cancel_or_add'],
                             investigate(BY_KEY['cancel_or_add'],st,mode='compose'))
        st.sources.pop(next(iter(st.sources)))
        with self.assertRaises(ProofError):st.verify_all()

    def test_non_verified_attempt_cannot_enter_memory(self):
        st=seeds()
        r=investigate(BY_KEY['cancel_or_add'],st,mode='direct')
        with self.assertRaises(ProofError):st.add_derived(BY_KEY['cancel_or_add'],r)
        # Source validator rejects a fake correct status when source receipt disagrees.
        r['status']='REVIEW_SCOPED_CANDIDATE_NOT_INSTALLED'
        with self.assertRaises(ProofError):st.add_derived(BY_KEY['cancel_or_add'],r)

    def test_task_key_mutation_fails(self):
        st=seeds()
        from dataclasses import replace
        changed=replace(BY_KEY['food_safe'],description='Materially changed meaning!')
        with self.assertRaises(ProofError):st.add_task(changed)

    def test_bounded_call_budget_and_type_validation(self):
        for n in (0,1,7,True):
            with self.assertRaises(ProofError):investigate(BY_KEY['cancel_or_add'],self.store,query_budget=n)
        for d in (0,4,True):
            with self.assertRaises(ProofError):enumerate_compositions(licenses(self.store.sources),max_depth=d)

    def test_separating_queries_are_chosen_without_target_truth(self):
        c=catalog(BY_KEY['cancel_or_add'],self.store,mode='compose')
        probe=best_probe(c,set())
        self.assertEqual(len(probe),2)
        self.assertTrue(all(0<=i<=7 for i in probe))

    def test_grammar_cannot_express_cross_category_majority(self):
        ops=licenses(self.store.sources)
        got={tuple(e['signature']) for e in enumerate_compositions(ops)}
        target=tuple(7 if a.bit_count()>=2 else 0 for a in range(8) for _ in range(8))
        self.assertNotIn(target,got)

    def test_full_offline_benchmark_receipts(self):
        report=run()
        self.assertEqual(report['model_generations'],0)
        self.assertEqual(report['initial_direct_attempt']['frozen']['correct'],27)
        self.assertEqual(report['new_compositional_attempt']['frozen']['correct'],64)
        self.assertEqual(report['retained_task_transfer']['frozen']['correct'],64)
        self.assertEqual(report['reversed_role_transfer']['frozen']['correct'],64)
        self.assertEqual(report['serialized_proof_cards'],3)
        self.assertFalse(report['installed'])

if __name__=='__main__':unittest.main()
