"""GEOM-012 falsifiers: permission, missing measurements, synthesis, provenance."""
from __future__ import annotations
import copy
import json
import random
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent/'geometry-009'))
from instrument_lab import (Atom,Capability,Event,Instrument,InstrumentLab,TraceCase,
    case_from_document,event_from_document,instrument_from_data,run_document)
from demo import scenario,raw_events,SCOPE,WINDOWS,BUDGET
from benchmark import heldout,classical_truth_table


class InstrumentLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lab=scenario()
        cls.proposal=cls.lab.propose(work_budget=10000)
        cls.plan=cls.lab.validate_proposal(cls.proposal)

    def test_01_diagnosis_is_a_real_visible_collision(self):
        d=self.lab.diagnose()
        self.assertEqual(d['status'],'NEEDS_NEW_MEASUREMENT_DIMENSION')
        self.assertGreaterEqual(len(d['witnesses']),1)
        self.assertFalse(d['source_roots_authenticated'])

    def test_02_synthesized_multi_step_instrument(self):
        self.assertEqual(self.proposal['status'],'PENCIL_INSTRUMENT_PROPOSED')
        self.assertEqual(self.plan.operator,'XOR')
        self.assertEqual(self.proposal['development']['correct'],96)
        self.assertEqual(len(self.proposal['procedure']),7)
        self.assertEqual([s['step'] for s in self.proposal['procedure']],
                         ['FILTER_RECORDED_EVENTS','COUNT','ODD',
                          'FILTER_RECORDED_EVENTS','COUNT','ODD','XOR'])

    def test_03_two_individually_uninformative_parities(self):
        scores=[]
        for a in self.plan.atoms:
            single=Instrument('ID',(a,),SCOPE)
            scores.append(self.lab.score(single,self.lab.development)['correct'])
        self.assertEqual(scores,[48,48])

    def test_04_capability_denial_beats_perfect_leak(self):
        self.assertNotIn('answer-leak',str(self.proposal['instrument']))
        self.assertNotIn('unavailable-leak',str(self.proposal['instrument']))
        for channel in ('answer-leak','unavailable-leak'):
            p=Instrument('ID',(Atom(channel,0,8,'NONZERO'),),SCOPE)
            with self.assertRaisesRegex(ValueError,'nonpermitted capability'):
                p.measure(self.lab.development[0],self.lab.catalog,self.lab.windows,BUDGET)

    def test_05_absent_record_distinct_from_empty_event_log(self):
        x=self.lab.development[0]
        missing=TraceCase.make('none',x.before,x.after,dict(x.visible),x.expected,None,'claimed:none',SCOPE)
        empty=TraceCase.make('empty',x.before,x.after,dict(x.visible),x.expected,[],'claimed:empty',SCOPE)
        self.assertEqual(self.plan.measure(missing,self.lab.catalog,self.lab.windows,BUDGET)['status'],
                         'HOLD_NO_RECORDED_TRACE')
        self.assertEqual(self.plan.measure(empty,self.lab.catalog,self.lab.windows,BUDGET)['status'],
                         'LOCAL_TRACE_REPLAY')

    def test_06_frozen_heldout_correct_abstain(self):
        result=self.lab.evaluate_heldout(self.proposal,heldout())
        self.assertEqual(result['scores'],{'total':260,'correct':240,'wrong':0,'abstentions':20})
        self.assertFalse(result['live_measurement_performed'])

    def test_07_independent_classical_baseline_ties(self):
        test=heldout()
        self.assertEqual(self.lab.evaluate_heldout(self.proposal,test)['scores'],
                         classical_truth_table(self.lab.development,test))

    def test_08_tampered_score_refused(self):
        forged=copy.deepcopy(self.proposal);forged['development']['correct']=999
        with self.assertRaisesRegex(ValueError,'replay'):
            self.lab.validate_proposal(forged)

    def test_09_tampered_program_refused(self):
        forged=copy.deepcopy(self.proposal);forged['instrument']['operator']='AND'
        with self.assertRaisesRegex(ValueError,'replay'):
            self.lab.validate_proposal(forged)

    def test_10_tampered_permission_refused(self):
        forged=copy.deepcopy(self.proposal);forged['source_roots_authenticated']=True
        with self.assertRaisesRegex(ValueError,'replay'):
            self.lab.validate_proposal(forged)

    def test_11_wrong_dataset_replay_refused(self):
        others=list(self.lab.development)
        x=others[0]
        others[0]=TraceCase.make(x.identity,x.before,x.after,dict(x.visible),x.expected,x.events,
                                 'claimed:changed',SCOPE)
        other=InstrumentLab(others,self.lab.capabilities,WINDOWS,scope=SCOPE,budget=BUDGET)
        with self.assertRaisesRegex(ValueError,'forged'):
            other.validate_proposal(self.proposal)

    def test_12_scope_mismatch_refused(self):
        x=self.lab.development[0]
        shifted=TraceCase.make('shifted',x.before,x.after,dict(x.visible),x.expected,x.events,
                               'claimed:shifted','other-observer@other-cut')
        with self.assertRaisesRegex(ValueError,'scope'):
            self.lab.score(self.plan,[shifted])

    def test_13_restricted_budget_refuses_two_channel_program(self):
        with self.assertRaisesRegex(ValueError,'cost budget'):
            self.plan.validate(self.lab.catalog,self.lab.windows,1.5,SCOPE)

    def test_14_reduced_capability_grants_cannot_run_saved_plan(self):
        manifest=dict(self.lab.catalog)
        manifest['b']=Capability('b',1.,False,True,SCOPE)
        with self.assertRaisesRegex(ValueError,'nonpermitted'):
            self.plan.measure(self.lab.development[0],manifest,self.lab.windows,BUDGET)

    def test_15_window_scope_refused(self):
        with self.assertRaisesRegex(ValueError,'undeclared'):
            self.plan.validate(self.lab.catalog,((0,4),),BUDGET,SCOPE)

    def test_16_resume_from_small_slice(self):
        x=self.lab.propose(work_budget=2)
        self.assertEqual(x['status'],'CONTINUE_SEARCH')
        self.assertEqual(x['completeness'],'INCOMPLETE')
        done=self.lab.propose(work_budget=1000,cursor=x['cursor'])
        self.assertEqual(done,self.proposal)

    def test_17_forged_skip_past_winner_refused(self):
        fake={'domain':self.lab.domain,'offset':self.proposal['candidate_rank']}
        with self.assertRaisesRegex(ValueError,'earlier exact fit'):
            self.lab.propose(work_budget=100,cursor=fake)

    def test_18_changed_manifest_invalidates_cursor(self):
        x=self.lab.propose(work_budget=2)
        alt=[Capability(c.channel,2.0 if c.channel=='a' else c.cost,
                        c.permitted,c.available,c.scope) for c in self.lab.capabilities]
        other=InstrumentLab(self.lab.development,alt,WINDOWS,scope=SCOPE,budget=BUDGET)
        with self.assertRaisesRegex(ValueError,'mismatched'):
            other.propose(work_budget=20,cursor=x['cursor'])

    def test_19_refuse_nonpositive_or_bad_budget(self):
        for x in (0,-2,True,0.1):
            with self.assertRaises(ValueError): self.lab.propose(work_budget=x)
        for x in (float('inf'),float('nan'),0,-1):
            with self.assertRaises(ValueError):
                InstrumentLab(self.lab.development,self.lab.capabilities,WINDOWS,scope=SCOPE,budget=x)

    def test_20_hold_if_recorded_development_trace_missing(self):
        cases=list(self.lab.development)
        c=cases[0]
        cases[0]=TraceCase.make(c.identity,c.before,c.after,dict(c.visible),c.expected,
                                 None,c.source_root,c.scope)
        lab=InstrumentLab(cases,self.lab.capabilities,WINDOWS,scope=SCOPE,budget=BUDGET)
        self.assertEqual(lab.propose(work_budget=1000)['status'],'HOLD_NEEDS_RECORDED_PILOT_TRACE')

    def test_21_hold_for_only_one_claimed_root(self):
        cases=[TraceCase.make(c.identity,c.before,c.after,dict(c.visible),c.expected,c.events,
                              'same-claimed-root',SCOPE) for c in self.lab.development]
        lab=InstrumentLab(cases,self.lab.capabilities,WINDOWS,scope=SCOPE,budget=BUDGET)
        self.assertEqual(lab.propose(work_budget=1000)['status'],'HOLD_INSUFFICIENT_DECLARED_SOURCE_ROOTS')

    def test_22_hold_when_visible_features_already_distinguish_labels(self):
        cases=[]
        for c in self.lab.development:
            vis=dict(c.visible);vis['answer-visible']=str(c.expected)
            cases.append(TraceCase.make(c.identity,c.before,c.after,vis,c.expected,c.events,
                                        c.source_root,SCOPE))
        lab=InstrumentLab(cases,self.lab.capabilities,WINDOWS,scope=SCOPE,budget=BUDGET)
        self.assertEqual(lab.propose(work_budget=1000)['status'],
                         'HOLD_NO_DEMONSTRATED_REPRESENTATIONAL_GAP')

    def test_23_missing_transform_grammar_holds_not_hallucinated(self):
        caps=[Capability('noise',0.25,True,True,SCOPE)]
        lab=InstrumentLab(self.lab.development,caps,WINDOWS,scope=SCOPE,budget=BUDGET)
        self.assertEqual(lab.propose(work_budget=1000)['status'],
                         'HOLD_NO_EXACT_PROCEDURE_IN_DECLARED_GRAMMAR')

    def test_24_untrusted_extra_interface_field_refused(self):
        with self.assertRaisesRegex(ValueError,'unknown or missing'):
            run_document({'execute_shell':'anything'})

    def test_25_strict_nested_schema(self):
        with self.assertRaisesRegex(ValueError,'invalid event'):
            event_from_document({'tick':0,'channel':'a','execute':'bad'})
        with self.assertRaisesRegex(ValueError,'invalid case'):
            case_from_document({'id':'x'})

    def test_26_reject_identity_and_invalid_ticks(self):
        with self.assertRaises(ValueError):Event(True,'a')
        with self.assertRaises(ValueError):Event(-1,'a')
        with self.assertRaises(ValueError):TraceCase.make('id',('x',),('x',),{},True,[],
                                                         'claimed:x',SCOPE)

    def test_27_reject_admitted_instrument(self):
        payload=self.plan.data();payload['state']='PEN'
        with self.assertRaises(ValueError):instrument_from_data(payload)

    def test_28_independent_random_boolean_oracle_160(self):
        rng=random.Random(20261106)
        catalog={ch:Capability(ch,1.,True,True,SCOPE) for ch in ('a','b')}
        windows=((0,8),)
        for _ in range(160):
            events=tuple(Event(rng.randrange(9),rng.choice(('a','b'))) for _ in range(rng.randrange(25)))
            atoms=(Atom('a',0,8,rng.choice(('ODD','NONZERO'))),
                   Atom('b',0,8,rng.choice(('ODD','NONZERO'))))
            op=rng.choice(('AND','OR','XOR'))
            plan=Instrument(op,atoms,SCOPE)
            vals=[]
            for at in atoms:
                count=sum(1 for ev in events if ev.channel==at.channel and 0<=ev.tick<8)
                vals.append(bool(count%2) if at.transform=='ODD' else count>0)
            oracle={'AND':vals[0] and vals[1], 'OR':vals[0] or vals[1],
                    'XOR':vals[0]!=vals[1]}[op]
            case=TraceCase.make('random',('b','u'),('b','r'),{},True,events,'random',SCOPE)
            self.assertEqual(plan.measure(case,catalog,windows,10.)['value'],oracle)

    def test_29_heldout_labels_cannot_influence_synthesis(self):
        held=heldout()
        before=copy.deepcopy(self.proposal)
        mutated=[TraceCase.make(c.identity,c.before,c.after,dict(c.visible),not c.expected,
                                 c.events,c.source_root,c.scope) for c in held]
        self.lab.evaluate_heldout(self.proposal,mutated)
        self.assertEqual(before,self.lab.propose(work_budget=1000))

    def test_30_duplicate_ids_refused(self):
        with self.assertRaisesRegex(ValueError,'unique'):
            InstrumentLab(list(self.lab.development)+[self.lab.development[0]],
                          self.lab.capabilities,WINDOWS,scope=SCOPE,budget=BUDGET)
        with self.assertRaisesRegex(ValueError,'overlaps'):
            self.lab.evaluate_heldout(self.proposal,[self.lab.development[0]])

    def test_31_bound_raw_not_compressed_to_unknown(self):
        self.assertFalse(Atom('a',0,4,'NONZERO').run([Event(4,'a')]))
        self.assertTrue(Atom('a',4,8,'NONZERO').run([Event(4,'a')]))
        self.assertFalse(Atom('a',4,8,'NONZERO').run([Event(8,'a')]))

    def test_32_reproduced_json_interface(self):
        req={'scope':SCOPE,'development':[c.data() for c in self.lab.development],
             'capabilities':[c.data() for c in self.lab.capabilities],
             'windows':[list(w) for w in WINDOWS],
             'budget':BUDGET,'work_budget':1000}
        out=run_document(req)
        self.assertEqual(out['synthesis'],self.proposal)

    def test_33_optional_archive_uses_actual_geom008_graph(self):
        try:from living_graph import LivingGraph
        except ImportError:self.skipTest('stacked GEOM-009 dependency unavailable in standalone folder')
        with LivingGraph(scope=SCOPE) as graph:
            entry=self.lab.archive_pencil(graph,self.proposal)
            self.assertEqual(entry['status'],'ARCHIVED_PENCIL_ONLY')
            self.assertEqual(graph.verify()['integrity'],'ok')
            self.assertEqual(graph.counts()['nodes'],len(self.lab.development)+1)
            self.assertEqual(graph.counts()['relations'],1)
            # Raw forbidden answer-leak event must not be persisted.
            found=graph.db.execute("SELECT payload FROM nodes WHERE kind='declared_raw_trace_case'").fetchall()
            self.assertTrue(found)
            self.assertTrue(all('answer-leak' not in x['payload'] for x in found))
            self.assertTrue(all('unavailable-leak' not in x['payload'] for x in found))

    def test_34_archive_rejects_forged_receipt(self):
        try:from living_graph import LivingGraph
        except ImportError:self.skipTest('stacked GEOM-009 dependency unavailable')
        x=copy.deepcopy(self.proposal);x['development']['correct']=50000
        with LivingGraph(scope=SCOPE) as g:
            with self.assertRaisesRegex(ValueError,'replay'):
                self.lab.archive_pencil(g,x)
            self.assertEqual(g.counts()['nodes'],0)

    def test_35_archive_rejects_cross_scope(self):
        try:from living_graph import LivingGraph
        except ImportError:self.skipTest('stacked GEOM-009 dependency unavailable')
        with LivingGraph(scope='other') as g:
            with self.assertRaisesRegex(ValueError,'scope mismatch'):
                self.lab.archive_pencil(g,self.proposal)


if __name__=='__main__':unittest.main()
