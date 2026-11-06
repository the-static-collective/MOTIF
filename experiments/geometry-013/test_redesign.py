"""GEOM-013 unit, adversarial, and randomized independent procedural oracles."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import copy
import json
import random
import sys
import tempfile
import unittest

from redesign import (RecordedCase, RecordedEvent, IdentifierAccess, Revision,
                      RedesignLab, revision_from_data, run_document, GRAMMAR)
from demo import SCOPE, WINDOWS, BUDGET, examples, scenario, two_revisions, predecessor_instrument, capabilities
from instrument_lab import Event, TraceCase, Capability, Atom, Instrument
from benchmark import independent_measure, independent_select

sys.path.append(str(Path(__file__).resolve().parent.parent / 'geometry-009'))
from living_graph import LivingGraph


class ProcedureRedesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.initial,cls.first,cls.second,cls.p1,cls.r1,cls.p2,cls.r2=two_revisions()

    def test_actual_geom012_instrument_reused(self):
        self.assertIs(self.initial.parent,predecessor_instrument())
        self.assertEqual(self.initial.parent.operator,'XOR')
        self.assertEqual({a.channel for a in self.initial.parent.atoms},{'a','b'})

    def test_parent_inherits_012_raw_count_semantics(self):
        for case in self.first.development[:12]:
            input012=TraceCase.make(case.identity,case.before,case.after,dict(case.visible),
                      case.expected,[Event(e.tick,e.channel) for e in case.records],case.source_root,case.scope)
            pred012=self.initial.parent.measure(input012,self.first.catalog,self.first.windows,self.first.budget)
            pred013=self.initial.measure(case,self.first.catalog,self.first.windows,self.first.budget,
                                        self.first.identifier_access)
            self.assertEqual(pred013['value'],pred012['value'])

    def test_first_critic_detects_duplicate_record_failure(self):
        diag=self.first.critic(self.initial)
        self.assertEqual(diag['scores']['wrong'],32)
        self.assertEqual(len(diag['counterexamples']),32)
        self.assertTrue(all('a' in x['candidate_duplicate_channels'] for x in diag['counterexamples']))

    def test_first_revision_changes_instrument_procedure_not_just_label(self):
        self.assertEqual(set(self.r1.distinct),{False,True})
        flags={a.channel:d for a,d in zip(self.r1.parent.atoms,self.r1.distinct)}
        self.assertEqual(flags,{'a':True,'b':False})
        self.assertEqual(sum(x['step']=='DISTINCT_BY_DECLARED_EVENT_ID' for x in self.r1.recipe()),1)
        self.assertEqual(self.first.critic(self.r1)['scores']['wrong'],0)

    def test_second_revision_detects_new_shift(self):
        diag=self.second.critic(self.r1)
        self.assertEqual(diag['scores']['wrong'],32)
        self.assertTrue(all('b' in w['candidate_duplicate_channels'] for w in diag['counterexamples']))
        self.assertEqual(diag['scores']['total'],128)

    def test_second_revision_adds_distinct_on_other_branch(self):
        self.assertEqual(self.r2.distinct,(True,True))
        self.assertEqual(sum(x['step']=='DISTINCT_BY_DECLARED_EVENT_ID' for x in self.r2.recipe()),2)
        self.assertEqual(self.second.critic(self.r2)['status'],'DEVELOPMENT_FIT')

    def test_counterfactual_path_preserves_parent(self):
        self.assertEqual(self.initial.distinct,(False,False))
        self.assertEqual(self.r1.distinct,(True,False))
        self.assertEqual(self.r2.distinct,(True,True))
        self.assertEqual(self.initial.parent.data(),self.r2.parent.data())

    def test_source_root_labels_unverified_and_state_pencil(self):
        for proposal in (self.p1,self.p2):
            self.assertFalse(proposal['roots_authenticated'])
            self.assertFalse(proposal['live_measurement_performed'])
            self.assertEqual(proposal['authority'],'NONE')
            self.assertEqual(proposal['state'],'PENCIL')

    def test_no_rewriting_of_inherited_parent_grammar(self):
        self.assertEqual(self.p2['from'],self.r1.data())
        self.assertEqual(self.p2['to'],self.r2.data())
        self.assertEqual(self.p2['to']['parent'],self.p1['to']['parent'])

    def test_first_slice_resumes_exactly(self):
        a=self.first.propose(self.initial,work_budget=1)
        self.assertEqual(a['status'],'CONTINUE_SEARCH')
        b=self.first.propose(self.initial,work_budget=10,cursor=a['cursor'])
        self.assertEqual(b,self.p1)

    def test_cross_dataset_cursor_rejected(self):
        a=self.first.propose(self.initial,work_budget=1)
        with self.assertRaisesRegex(ValueError,'cursor'):
            self.second.propose(self.initial,work_budget=10,cursor=a['cursor'])

    def test_forged_cursor_beyond_candidates_rejected(self):
        a=self.first.propose(self.initial,work_budget=1)
        f=copy.deepcopy(a['cursor']);f['offset']=999
        with self.assertRaisesRegex(ValueError,'cursor'):
            self.first.propose(self.initial,work_budget=10,cursor=f)

    def test_forged_cursor_skipping_earliest_fit_rejected(self):
        a=self.first.propose(self.initial,work_budget=1)
        f=copy.deepcopy(a['cursor']);f['offset']=3
        with self.assertRaisesRegex(ValueError,'skipped'):
            self.first.propose(self.initial,work_budget=10,cursor=f)

    def test_budget_refusal_or_unknown_input(self):
        for work in (True,0,-5,0.5):
            with self.assertRaises(ValueError):self.first.propose(self.initial,work_budget=work)

    def test_cost_budget_fences(self):
        access=self.first.identifier_access
        with self.assertRaisesRegex(ValueError,'cost budget'):
            self.r2.validate(self.first.catalog,self.first.windows,2.45,access,SCOPE)

    def test_permission_false_refuses_uid_operator(self):
        access=IdentifierAccess(SCOPE,False,True,0.25)
        lab=RedesignLab(self.initial.parent,self.first.capabilities,self.first.windows,
                        access,self.first.development,budget=BUDGET)
        self.assertEqual(lab.propose(self.initial,work_budget=10)['status'],'HOLD_NO_PERMITTED_REDESIGN')
        with self.assertRaisesRegex(ValueError,'permitted'):
            self.r1.measure(self.first.development[0],lab.catalog,lab.windows,lab.budget,access)

    def test_permission_false_for_channel_in_base_also_refused(self):
        caps=[Capability(x.channel,x.cost,False,x.available,x.scope) if x.channel=='a' else x
              for x in capabilities()]
        with self.assertRaisesRegex(ValueError,'nonpermitted'):
            RedesignLab(self.initial.parent,caps,WINDOWS,IdentifierAccess(SCOPE,True,True,0.25),
                        self.first.development,budget=BUDGET)

    def test_uid_unavailable_refuses_procedure(self):
        access=IdentifierAccess(SCOPE,True,False,0.25)
        lab=RedesignLab(self.initial.parent,self.first.capabilities,self.first.windows,
                        access,self.first.development,budget=BUDGET)
        self.assertEqual(lab.propose(self.initial,work_budget=10)['status'],'HOLD_NO_PERMITTED_REDESIGN')

    def test_missing_uid_is_explicit_hold(self):
        case=examples(12,1,'missing',duplicate_a=lambda i:True,duplicate_b=lambda i:False,missing_ids=1)[0]
        pred=self.r2.measure(case,self.first.catalog,WINDOWS,BUDGET,self.first.identifier_access)
        self.assertEqual(pred['status'],'HOLD_NO_DECLARED_EVENT_ID')
        self.assertIsNone(pred['value'])

    def test_missing_entire_recording_is_not_zero(self):
        case=examples(12,1,'missing',duplicate_a=lambda i:False,duplicate_b=lambda i:False,missing_traces=1)[0]
        self.assertEqual(self.r2.measure(case,self.first.catalog,WINDOWS,BUDGET,
                         self.first.identifier_access)['status'],'HOLD_NO_RECORDED_TRACE')

    def test_observed_empty_trace_is_not_missing(self):
        case=RecordedCase.make('empty',['a'],['b'],{},False,[], 'claimed:obs',SCOPE)
        p=self.r2.measure(case,self.first.catalog,WINDOWS,BUDGET,self.first.identifier_access)
        self.assertEqual((p['status'],p['value']),('LOCAL_SYNTHETIC_REPLAY',False))

    def test_colliding_record_identity_hold(self):
        case=RecordedCase.make('collision',['a'],['b'],{},False,[RecordedEvent(0,'a','same'),
                          RecordedEvent(1,'a','same')],'claimed:c',SCOPE)
        self.assertEqual(self.r2.measure(case,self.first.catalog,WINDOWS,BUDGET,
                         self.first.identifier_access)['status'],'HOLD_CONFLICTING_EVENT_ID')

    def test_duplicate_identical_record_counted_once(self):
        x=RecordedEvent(1,'a','x');y=RecordedEvent(2,'b','y')
        case=RecordedCase.make('dup',['a'],['b'],{},True,[x,x,y],'claimed:dup',SCOPE)
        original=self.initial.measure(case,self.first.catalog,WINDOWS,BUDGET,self.first.identifier_access)
        revised=self.r2.measure(case,self.first.catalog,WINDOWS,BUDGET,self.first.identifier_access)
        self.assertEqual(original['value'],True)
        self.assertEqual(revised['value'],False)

    def test_out_of_window_duplicate_ignored(self):
        x=RecordedEvent(10,'a','duplicate')
        case=RecordedCase.make('outside',['a'],['b'],{},False,[x,x], 'claimed:test',SCOPE)
        self.assertIs(self.r2.measure(case,self.first.catalog,WINDOWS,BUDGET,
                     self.first.identifier_access)['value'],False)

    def test_conflicting_identical_records_do_not_trigger_invention(self):
        case=self.first.development[0]
        opposite=RecordedCase.make('opposite',case.before,case.after,dict(case.visible),
                      not case.expected,case.records,'claimed:different',SCOPE)
        lab=RedesignLab(self.initial.parent,self.first.capabilities,WINDOWS,self.first.identifier_access,
                        [case,opposite],budget=BUDGET)
        self.assertEqual(lab.propose(self.initial,work_budget=100)['status'],'HOLD_CONTRADICTORY_RECORDS')

    def test_insufficient_declared_independent_roots_holds(self):
        altered=[replace(x,source_root='echo-root') for x in self.first.development]
        lab=RedesignLab(self.initial.parent,self.first.capabilities,WINDOWS,self.first.identifier_access,
                        altered,budget=BUDGET)
        self.assertEqual(lab.propose(self.initial,work_budget=10)['status'],'HOLD_DECLARED_SOURCE_ROOTS')

    def test_no_feedback_gap_refuses_new_invention(self):
        self.assertEqual(self.first.propose(self.r1,work_budget=10)['status'],'HOLD_NO_FEEDBACK_GAP')

    def test_recorded_dev_missing_hold(self):
        bad=list(self.first.development);bad[-1]=replace(bad[-1],records=None)
        lab=RedesignLab(self.initial.parent,self.first.capabilities,WINDOWS,self.first.identifier_access,
                        bad,budget=BUDGET)
        self.assertEqual(lab.propose(self.initial,work_budget=10)['status'],'HOLD_NEEDS_RECORDED_DEVELOPMENT')

    def test_heldout_development_identity_overlap_refused(self):
        with self.assertRaisesRegex(ValueError,'contamination'):
            self.second.heldout(self.r1,self.p2,[self.second.development[0]])

    def test_heldout_scoped_separately(self):
        c=replace(self.second.development[0],scope='other-world')
        with self.assertRaisesRegex(ValueError,'scope'):
            self.second.evaluation(self.r2,[c])

    def test_synthetic_answer_leak_does_not_influence_measurement(self):
        original=self.first.development[0]
        stripped=replace(original,records=tuple(e for e in original.records
                                  if e.channel not in {'answer-leak','unavailable-leak'}))
        for r in (self.initial,self.r1,self.r2):
            self.assertEqual(r.measure(original,self.first.catalog,WINDOWS,BUDGET,
                self.first.identifier_access)['value'],r.measure(stripped,self.first.catalog,WINDOWS,BUDGET,
                self.first.identifier_access)['value'])

    def test_validate_proposal_rejects_forged_score(self):
        forged=copy.deepcopy(self.p2);forged['development']['correct']=999999
        with self.assertRaisesRegex(ValueError,'forged'):
            self.second.validate_proposal(self.r1,forged)

    def test_validate_proposal_rejects_forged_source_domain(self):
        forged=copy.deepcopy(self.p1);forged['dataset']='imagined'
        with self.assertRaisesRegex(ValueError,'forged'):
            self.first.validate_proposal(self.initial,forged)

    def test_instrument_wont_claim_promotion(self):
        invalid=copy.deepcopy(self.r2.data());invalid['state']='PEN'
        with self.assertRaisesRegex(ValueError,'authority'):
            revision_from_data(invalid)

    def test_reject_invalid_input_schema(self):
        with self.assertRaises(ValueError):run_document({'execute_shell':'echo fake'})
        with self.assertRaises(ValueError):Revision(self.initial.parent,(True,1))
        with self.assertRaises(ValueError):RecordedEvent(-1,'a','x')
        with self.assertRaises(ValueError):IdentifierAccess(SCOPE,True,True,float('inf'))

    def test_graph_archive_is_pencil_only_and_does_not_mutate_grammar(self):
        with LivingGraph(scope=SCOPE) as graph:
            prior=graph.counts()
            receipt=self.second.archive_pencil(graph,self.r1,self.p2)
            self.assertEqual(receipt['status'],'ARCHIVED_PENCIL_ONLY')
            row=graph.db.execute('SELECT status,payload FROM nodes WHERE id=?',(receipt['node_id'],)).fetchone()
            self.assertEqual(row['status'],'PENCIL')
            self.assertIn('PENCIL_ONLY',row['payload'])
            self.assertEqual(graph.verify()['integrity'],'ok')
            self.assertEqual(graph.counts()['nodes']-prior['nodes'],129)
            self.assertEqual(graph.counts()['relations']-prior['relations'],1)
            self.assertIsNone(graph.db.execute("SELECT value FROM meta WHERE key='grammar'").fetchone())

    def test_graph_archive_rejects_forged_proposal(self):
        forged=copy.deepcopy(self.p2);forged['recipe']=[]
        with LivingGraph(scope=SCOPE) as graph:
            with self.assertRaisesRegex(ValueError,'forged'):
                self.second.archive_pencil(graph,self.r1,forged)
            self.assertEqual(graph.counts()['nodes'],0)

    def test_archive_cross_scope_refuses(self):
        with LivingGraph(scope='another') as graph:
            with self.assertRaisesRegex(ValueError,'scope'):
                self.second.archive_pencil(graph,self.r1,self.p2)

    def test_randomized_independent_counting_oracle(self):
        rng=random.Random(20261106)
        from benchmark import independent_measure
        for i in range(200):
            records=[]
            for ch in ('a','b'):
                raw=[RecordedEvent(rng.randrange(8),ch,f'{i}:{ch}:{j}')
                     for j in range(rng.randrange(8))]
                records.extend(raw)
                if raw and rng.getrandbits(1):records.append(rng.choice(raw))
            case=RecordedCase.make(f'property-{i}',('a',),('b',),{},False,records,'claimed:property',SCOPE)
            for r in (self.initial,self.r1,self.r2):
                ours=r.measure(case,self.first.catalog,WINDOWS,BUDGET,self.first.identifier_access)['value']
                truth=independent_measure(case,r.distinct)
                self.assertEqual(ours,truth,case.identity)

    def test_independent_classical_search_ties_stages(self):
        self.assertEqual(independent_select(self.first.development),self.r1.distinct)
        self.assertEqual(independent_select(self.second.development,self.r1.distinct),self.r2.distinct)

    def test_deterministic_replay(self):
        self.assertEqual(self.first.propose(self.initial,work_budget=10),self.p1)
        self.assertEqual(self.second.propose(self.r1,work_budget=10),self.p2)

if __name__=='__main__':unittest.main()
