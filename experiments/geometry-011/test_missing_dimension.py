"""GEOM-011 adversarial tests; all worlds explicitly synthetic."""
from __future__ import annotations

import copy
import itertools
import json
import random
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

from missing_dimension import (Case, Sensor, PilotReading, SynthesizedDimension,
    MissingDimensionLab, run_document, _matches_rewrite)
from demo import scenario, SCOPE, BASE
from benchmark import heldout, independent_truth_table


class FakeGraph:
    """PENCIL-only graph double; real SQLite graph tested when repo stack is available."""
    def __init__(self, scope=SCOPE):
        self.scope = scope
        self.nodes = {}
        self.relations = []

    def add_node(self, identity, *, kind, label, payload, source_root):
        self.nodes[identity] = dict(kind=kind, label=label, payload=payload,
                                    source_root=source_root)

    def add_relation(self, kind, participants, *, source_root, note):
        self.relations.append((kind, participants, source_root, note))


class MissingDimensionTests(unittest.TestCase):
    def setUp(self):
        self.lab = scenario()
        self.proposal = self.lab.invent(find=BASE['find'], replace=BASE['replace'],
                                        budget=3., work_budget=100)

    def test_detects_exact_ambiguous_visible_inputs(self):
        d = self.lab.diagnose()
        self.assertEqual(d['status'], 'MISSING_DISTINCTION_CERTIFICATE')
        self.assertEqual(len(d['conflict_witnesses']), 6)
        self.assertEqual(d['authority'], 'NONE')
        self.assertNotEqual(d['conflict_witnesses'][0]['positive_case'],
                            d['conflict_witnesses'][0]['negative_case'])

    def test_pilot_sensors_individually_uninformative_but_jointly_informative(self):
        p = self.lab.probe_options(budget=3.)
        self.assertEqual(p['best']['sensors'], ['signal-a', 'signal-b'])
        self.assertAlmostEqual(p['best']['pilot_information_gain_bits'], 1.)
        self.assertAlmostEqual(p['best']['synergy_bits_above_best_single'], 1.)
        singles = [x for x in p['options'] if len(x['sensors']) == 1]
        self.assertTrue(singles)
        self.assertTrue(all(x['pilot_information_gain_bits'] == 0 for x in singles))

    def test_cannot_use_forbidden_perfect_leak_even_with_pilot(self):
        opts = self.lab.probe_options(budget=3.)['options']
        self.assertTrue(all('forbidden-leak' not in x['sensors'] for x in opts))
        self.assertTrue(all('unavailable' not in x['sensors'] for x in opts))
        self.assertNotIn('forbidden-leak', self.proposal['cartridge']['signals'])

    def test_perfect_pilot_without_authorization_still_holds(self):
        only = [Sensor('forbidden-leak', 0.01, False, True, SCOPE)]
        lab = MissingDimensionLab(self.lab.cases, only,
                 [x for x in self.lab.pilot if x.sensor_id == 'forbidden-leak'], scope=SCOPE)
        self.assertEqual(lab.probe_options(budget=3.)['status'], 'HOLD_NO_PERMITTED_SENSOR')
        self.assertEqual(lab.invent(find=['bud'], replace=['branch'],
                                    budget=3., work_budget=100)['status'], 'HOLD_NO_PERMITTED_SENSOR')

    def test_missing_pilot_produces_hold_not_predicted_outcome(self):
        lab = MissingDimensionLab(self.lab.cases,
            [Sensor('signal-a',1.,True,True,SCOPE)], [], scope=SCOPE)
        self.assertEqual(lab.probe_options(budget=3.)['status'], 'HOLD_NEEDS_PILOT')
        self.assertEqual(lab.invent(find=['bud'], replace=['branch'],
                                   budget=3., work_budget=100)['status'], 'HOLD_NEEDS_PILOT')

    def test_missing_pilot_count_is_exact(self):
        p = self.lab.probe_options(budget=3.)
        self.assertEqual(p['unmeasured_development_cases_by_sensor']['missing-sensor'], 24)

    def test_invents_a_new_derived_xor_dimension_from_pilots(self):
        self.assertEqual(self.proposal['status'], 'PENCIL_DIMENSION_PROPOSED')
        self.assertEqual(self.proposal['cartridge']['operator'], 'XOR')
        self.assertEqual(self.proposal['cartridge']['signals'], ['signal-a','signal-b'])
        self.assertEqual(self.proposal['development']['correct'], 24)
        self.assertEqual(self.proposal['development']['wrong'], 0)
        self.assertEqual(self.proposal['authority'], 'NONE')
        self.assertEqual(self.proposal['cartridge']['instrument'], 'PENCIL')

    def test_budgeted_search_requires_resumption(self):
        r = self.lab.invent(find=['bud'], replace=['branch'], budget=3., work_budget=2)
        self.assertEqual(r['status'], 'CONTINUE_SEARCH')
        self.assertEqual(r['completeness'], 'INCOMPLETE')
        final = self.lab.invent(find=['bud'], replace=['branch'], budget=3.,
                                 work_budget=100, cursor=r['cursor'])
        self.assertEqual(final, self.proposal)

    def test_cursor_cannot_cross_a_changed_dataset(self):
        r = self.lab.invent(find=['bud'], replace=['branch'], budget=3., work_budget=1)
        changed = list(self.lab.cases)
        c = changed[0]
        changed[0] = Case.make(c.identity, c.before, c.after, dict(c.visible),
                               not c.expected, c.source_root, c.scope)
        another = MissingDimensionLab(changed, self.lab.sensors, self.lab.pilot, scope=SCOPE)
        with self.assertRaisesRegex(ValueError, 'cursor'):
            another.invent(find=['bud'],replace=['branch'],budget=3., work_budget=100,
                           cursor=r['cursor'])

    def test_cursor_cannot_skip_past_success(self):
        r = self.lab.invent(find=['bud'],replace=['branch'],budget=3.,work_budget=1)
        invalid = dict(r['cursor'], offset=100)
        with self.assertRaisesRegex(ValueError, 'cursor'):
            self.lab.invent(find=['bud'],replace=['branch'],budget=3.,
                            work_budget=100,cursor=invalid)

    def test_missing_measurement_abstains_on_heldout(self):
        test, pilot = heldout()
        outcome = self.lab.evaluate_new_cases(self.proposal,test,pilot)
        self.assertEqual(outcome['scores'],
          {'total':260,'correct':240,'wrong':0,'abstentions':20})

    def test_unmodified_train_selection_is_independent_of_heldout_labels(self):
        test, pilot = heldout()
        wrong_labels = [Case.make(x.identity, x.before, x.after, dict(x.visible),
                     not x.expected, x.source_root, x.scope) for x in test]
        # Evaluation can differ, but re-running the learner must not see these labels.
        self.lab.evaluate_new_cases(self.proposal,wrong_labels,pilot)
        self.assertEqual(self.lab.invent(find=['bud'],replace=['branch'],
            budget=3.,work_budget=100),self.proposal)

    def test_classical_two_signal_lookup_ties_on_heldout(self):
        test, pilot = heldout()
        score=self.lab.evaluate_new_cases(self.proposal,test,pilot)['scores']
        self.assertEqual(score,independent_truth_table(self.lab,test,pilot))

    def test_heldout_overlap_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'overlap'):
            self.lab.evaluate_new_cases(self.proposal,[self.lab.cases[0]], [])

    def test_wrong_scope_is_refused(self):
        bad = list(self.lab.cases)
        first = bad[0]
        bad[0] = Case.make(first.identity,first.before,first.after,
            dict(first.visible),first.expected,first.source_root,'different:cut')
        with self.assertRaisesRegex(ValueError, 'scope'):
            MissingDimensionLab(bad,self.lab.sensors,self.lab.pilot,scope=SCOPE)

    def test_invalid_pilot_values_are_rejected(self):
        for val in ('unknown', '2', '-1', ''):
            with self.subTest(val=val), self.assertRaises(ValueError):
                PilotReading('a','s',val,'root',SCOPE)

    def test_development_requires_unique_case_ids(self):
        with self.assertRaisesRegex(ValueError,'unique'):
            MissingDimensionLab([self.lab.cases[0]]*2,self.lab.sensors,self.lab.pilot,scope=SCOPE)

    def test_duplicate_pilot_even_if_identical_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate pilot'):
            MissingDimensionLab(self.lab.cases,self.lab.sensors,
                                list(self.lab.pilot)+[self.lab.pilot[0]],scope=SCOPE)

    def test_unseen_pilot_case_is_rejected(self):
        extra = PilotReading('not-real','signal-a','0','source',SCOPE)
        with self.assertRaisesRegex(ValueError,'unknown case'):
            MissingDimensionLab(self.lab.cases,self.lab.sensors,
                                list(self.lab.pilot)+[extra],scope=SCOPE)

    def test_heldout_forbidden_sensor_cannot_be_consumed(self):
        test,_=heldout()
        forbidden=[PilotReading(test[0].identity,'forbidden-leak','0','s',SCOPE)]
        with self.assertRaisesRegex(ValueError,'unpermitted'):
            self.lab.evaluate_new_cases(self.proposal,test[:1],forbidden)

    def test_forged_cartridge_score_or_gate_is_refused(self):
        for field in ('development','cartridge'):
            altered=copy.deepcopy(self.proposal)
            if field=='development':altered['development']['correct']=99
            else:altered['cartridge']['operator']='AND'
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'selected'):
                self.lab.evaluate_new_cases(altered,*heldout())

    def test_missing_measurement_budget_receipt_is_refused(self):
        altered=copy.deepcopy(self.proposal)
        altered.pop('measurement_budget')
        with self.assertRaisesRegex(ValueError,'budget'):
            self.lab.evaluate_new_cases(altered,*heldout())

    def test_declared_distinct_roots_required(self):
        revised = [Case.make(x.identity,x.before,x.after,dict(x.visible),
                    x.expected,'one-echo-root',x.scope) for x in self.lab.cases]
        lab=MissingDimensionLab(revised,self.lab.sensors,self.lab.pilot,scope=SCOPE)
        self.assertEqual(lab.invent(find=['bud'],replace=['branch'],budget=3.,work_budget=100)['status'],'HOLD')

    def test_no_visible_collision_does_not_force_new_sensor(self):
        one = self.lab.cases[0]
        opposite = [c for c in self.lab.cases if c.expected != one.expected][0]
        altered = [Case.make(one.identity,one.before,one.after,{'x':'a'},
                    one.expected,one.source_root,one.scope),
                   Case.make(opposite.identity,opposite.before,opposite.after,{'x':'b'},
                    opposite.expected,opposite.source_root,opposite.scope)]
        lab=MissingDimensionLab(altered,self.lab.sensors,
                        [x for x in self.lab.pilot if x.case_id in {one.identity,opposite.identity}],scope=SCOPE)
        self.assertEqual(lab.diagnose()['status'],'NO_VISIBLE_COLLISION')
        self.assertEqual(lab.invent(find=['bud'],replace=['branch'],budget=3.,work_budget=100)['status'],'HOLD')

    def test_rewrite_applies_only_to_correct_before_and_after(self):
        op = SynthesizedDimension(('signal-a','signal-b'),'XOR',('bud',),('branch',),SCOPE)
        self.assertTrue(_matches_rewrite(('bud',),('branch',),('oak','bud'),('oak','branch')))
        self.assertFalse(_matches_rewrite(('bud',),('branch',),('oak','bud'),('oak','leaf')))
        wrong = Case.make('wrong',('oak','bud'),('oak','leaf'),{},True,'root',SCOPE)
        self.assertIs(op.decide(wrong,{}),False)

    def test_all_binary_gates_match_an_independent_truth_table(self):
        gates = ('AND','OR','XOR','XNOR','NAND','NOR')
        oracle = {'AND':lambda a,b:a and b,'OR':lambda a,b:a or b,
                  'XOR':lambda a,b:(a!=b),'XNOR':lambda a,b:(a==b),
                  'NAND':lambda a,b:not (a and b),'NOR':lambda a,b:not (a or b)}
        rng = random.Random(20261106)
        for _ in range(80):
            a,b = rng.choice((False,True)),rng.choice((False,True))
            for gate in gates:
                op=SynthesizedDimension(('a','b'),gate,('bud',),('branch',),SCOPE)
                self.assertEqual(op.value({'a':str(int(a)),'b':str(int(b))}),oracle[gate](a,b))

    def test_single_sensor_is_insufficient_for_xor(self):
        sensors = [s for s in self.lab.sensors if s.identity == 'signal-a']
        lab=MissingDimensionLab(self.lab.cases,sensors,
                [x for x in self.lab.pilot if x.sensor_id=='signal-a'],scope=SCOPE)
        self.assertEqual(lab.invent(find=['bud'],replace=['branch'],budget=3.,work_budget=100)['status'],'HOLD')

    def test_measurement_budget_cannot_be_ignored(self):
        p=self.lab.probe_options(budget=0.5)
        self.assertFalse(any('signal-a' in o['sensors'] for o in p.get('options',[])))
        self.assertEqual(self.lab.invent(find=['bud'],replace=['branch'],
            budget=0.5,work_budget=100)['status'],'HOLD')

    def test_archive_is_pencil_and_replays_evidence(self):
        graph=FakeGraph()
        receipt=self.lab.archive_pencil(graph,self.proposal,measurement_budget=3.)
        self.assertEqual(receipt['status'],'ARCHIVED_PENCIL_ONLY')
        self.assertTrue(graph.nodes)
        self.assertEqual(len(graph.relations),1)
        self.assertEqual(graph.relations[0][-1]['admission'],'PENCIL_ONLY')
        self.assertFalse(any(v['kind']=='authorized_operation' for v in graph.nodes.values()))

    def test_archive_rejects_forged_scores(self):
        graph=FakeGraph()
        altered=copy.deepcopy(self.proposal)
        altered['development']['wrong']=99
        with self.assertRaisesRegex(ValueError,'selected'):
            self.lab.archive_pencil(graph,altered,measurement_budget=3.)
        self.assertEqual(graph.nodes,{})

    def test_archive_wrong_scope_is_refused(self):
        with self.assertRaisesRegex(ValueError,'scope'):
            self.lab.archive_pencil(FakeGraph('another-scope'),self.proposal,
                                    measurement_budget=3.)

    def test_read_only_adapter_preserves_geom010_field_claims(self):
        fake=[SimpleNamespace(identity=c.identity,before=c.before,after=c.after,
                facts=c.visible,expected=c.expected,source_root=c.source_root,scope=c.scope)
              for c in self.lab.cases]
        adapter=MissingDimensionLab.from_geom010_cases(fake,self.lab.sensors,self.lab.pilot,scope=SCOPE)
        self.assertEqual(adapter.domain,self.lab.domain)

    def test_strict_document_interface_no_shell_or_network(self):
        with self.assertRaisesRegex(ValueError,'unknown or missing'):
            run_document({'shell':'rm -rf /'})

    def test_document_interface_replays_demo(self):
        doc={'scope':SCOPE,'development':[x.data() for x in self.lab.cases],
            'candidate_sensors':[x.data() for x in self.lab.sensors],
            'pilot_readings':[x.data() for x in self.lab.pilot],
            'base_rewrite':BASE,'measurement_budget':3.,'work_budget':100}
        result=run_document(doc)
        self.assertEqual(result['invention'],self.proposal)
        self.assertEqual(result['diagnosis']['status'],'MISSING_DISTINCTION_CERTIFICATE')

    def test_archives_to_actual_geom008_sqlite_if_stack_installed(self):
        previous=Path(__file__).resolve().parent.parent / 'geometry-009'
        if not (previous / 'living_graph.py').exists():
            self.skipTest('GEOM-009 dependency available in GitHub branch but not standalone local bundle')
        sys.path.insert(0,str(previous))
        from living_graph import LivingGraph
        with LivingGraph(scope=SCOPE) as graph:
            receipt=self.lab.archive_pencil(graph,self.proposal,measurement_budget=3.)
            self.assertEqual(receipt['status'],'ARCHIVED_PENCIL_ONLY')
            self.assertEqual(graph.verify()['integrity'],'ok')
            rows=graph.db.execute('SELECT DISTINCT status FROM nodes').fetchall()
            self.assertEqual([r['status'] for r in rows],['PENCIL'])


if __name__=='__main__': unittest.main()
