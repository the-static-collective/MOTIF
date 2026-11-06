"""No map, one map, many maps: the semantic evidence must remain identical."""
import copy
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'thought-007'))
from field import ThoughtField,canonical
# Prevent the sibling THOUGHT-007/demo.py from shadowing this experiment's demo.
sys.path.pop(0)
from multiview import ThoughtViews,ViewError,LENSES
from demo import synthetic,main
from render import render_board


class ParallelThoughtTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'events.jsonl'
        self.f,self.links=synthetic(self.path)
        self.snap=self.f.snapshot()
        self.engine=ThoughtViews(self.snap,self.links)

    def test_007_identities_preserved_under_all_projections(self):
        before=canonical(self.f.semantic_snapshot())
        result=self.engine.run(LENSES,anchor='m:volunteers')
        self.assertEqual(before,canonical(self.f.semantic_snapshot()))
        self.assertEqual(len(result['views']),6)
        self.assertEqual(len({v['source_evidence_digest'] for v in result['views']}),1)
        self.assertEqual(result['external_authority'],'NONE')

    def test_multi_instances_and_duplicate_same_view_placements(self):
        assoc=self.engine.project('association')
        home=[p for p in assoc['placements'] if p['manifestation_id']=='m:shelter-log']
        self.assertEqual(len(home),2)
        self.assertEqual(len({p['placement_id'] for p in home}),2)
        self.assertTrue(all(p['concept_id']=='c:home-shelter' for p in home))
        hex_v=self.engine.project('flower_hex')
        self.assertEqual(len({p['manifestation_id'] for p in hex_v['placements']}),len(self.f.manifestations))
        shelter=[p for p in hex_v['placements'] if p['concept_id']=='c:home-shelter']
        self.assertEqual(len(shelter),2)

    def test_none_is_not_a_layout_but_same_evidence_index(self):
        none=self.engine.project('NONE',anchor='m:volunteers')
        self.assertTrue(all(p['x'] is None and p['y'] is None for p in none['placements']))
        self.assertEqual(none['analysis'],self.engine.evidence_index('m:volunteers'))
        self.assertEqual(none['coordinate_authority'],'NONE')

    def test_questions_are_about_common_neighbors_not_screen_distance(self):
        questions=self.engine.association_questions()
        candidate=[q for q in questions if {q['source'],q['target']}=={'m:meal','m:food'}]
        self.assertEqual(len(candidate),1)
        self.assertEqual(candidate[0]['via'],['m:storage','m:volunteers'])
        self.assertEqual(candidate[0]['status'],'QUESTION_ONLY')
        self.assertNotIn('r:food-meal',[r['id'] for r in self.engine.relations])

    def test_position_moves_cannot_generate_semantic_link(self):
        old=self.engine.association_questions()
        source_fp=self.engine.input_digest
        self.f.move('p:home-one',-500000,600000,'change drawing',expected_revision=1)
        f2=ThoughtViews(self.f.snapshot(),self.links)
        self.assertEqual(old,f2.association_questions())
        self.assertEqual(source_fp,f2.input_digest)
        self.assertEqual(canonical(self.f.semantic_snapshot()),canonical(self.snap['semantic']))

    def test_conflict_is_not_association(self):
        c=self.engine.tensions()
        self.assertEqual(len(c),1)
        self.assertEqual(c[0]['relation_id'],'r:open-vs-closed')
        self.assertTrue(all(x['source']!='m:claim-open' and x['target']!='m:claim-open'
                            for x in self.engine._authored('associated')))

    def test_hypothetical_link_is_not_used_as_evidence(self):
        self.assertIn('r:shelter-belonging',self.engine.evidence_index()['hypothesis_links'])
        self.assertNotIn('r:shelter-belonging',self.engine.evidence_index()['associations'])
        self.assertEqual(self.engine.affordances('m:shelter-log')['conditional_reach'],[])

    def test_dependency_and_affordance_are_directional_and_conditional(self):
        dep=self.engine.dependencies('m:meal')
        self.assertEqual(set(dep['required_by_anchor']),{'m:volunteers','m:storage','m:van'})
        self.assertEqual(self.engine.dependencies('m:van')['required_by_anchor'],[])
        reach=self.engine.affordances('m:volunteers')['conditional_reach']
        self.assertEqual([x['manifestation_id'] for x in reach],['m:meal'])
        self.assertEqual(reach[0]['status'],'CONDITIONAL_ONLY')
        self.assertEqual(reach[0]['other_declared_requirements'],['m:storage','m:van'])

    def test_dependency_cycle_reports_not_silently_resolved(self):
        self.links.append(dict(id='cycle',source='m:volunteers',target='m:meal',
                               predicate='requires',origin='fixture:cycle',status='AUTHORED'))
        e=ThoughtViews(self.snap,self.links)
        self.assertEqual(e.dependencies()['cycles'],[['m:meal','m:volunteers','m:meal']])

    def test_no_layout_produces_same_typed_baseline_as_multi_layout(self):
        a=self.engine.run(['NONE'],anchor='m:volunteers')
        b=self.engine.run(LENSES,anchor='m:volunteers')
        self.assertEqual(a['baseline'],b['baseline'])
        self.assertEqual(a['source_evidence_digest'],b['source_evidence_digest'])

    def test_deterministic_replay_and_seed_control(self):
        self.assertEqual(self.engine.run(LENSES,seed=4),self.engine.run(LENSES,seed=4))
        self.assertEqual(self.f.snapshot(),ThoughtField(self.path).snapshot())
        changed=self.engine.project('association',seed=9)
        unchanged=self.engine.project('association',seed=8)
        self.assertNotEqual(changed['placements'],unchanged['placements'])
        self.assertEqual(changed['analysis'],unchanged['analysis'])
        self.assertEqual(changed['source_evidence_digest'],unchanged['source_evidence_digest'])

    def test_snapshot_is_copied_at_instantiation(self):
        before=self.engine.run(['association'])
        self.snap['semantic']['concepts'][0]['label']='tampered caller object'
        self.links[0]['origin']='tampered'
        self.assertEqual(before,self.engine.run(['association']))

    def test_source_labels_not_used_to_merge_concepts(self):
        self.assertEqual(self.engine.concepts['c:home-shelter']['label'],
                         self.engine.concepts['c:home-belong']['label'])
        self.assertNotEqual(self.engine.manifests['m:shelter-log']['concept_id'],
                            self.engine.manifests['m:belong-values']['concept_id'])

    def test_invalid_references_and_bounded_data_fail_closed(self):
        bad=copy.deepcopy(self.links)
        bad.append(dict(id='bad',source='no-such-manifest',target='m:food',predicate='enables',
                        origin='fixture:unknown',status='AUTHORED'))
        with self.assertRaises(ViewError):ThoughtViews(self.snap,bad)
        with self.assertRaises(ViewError):self.engine.project('telepathy')
        with self.assertRaises(ViewError):self.engine.project('association',anchor='missing')
        with self.assertRaises(ViewError):self.engine.run(['association','association'])
        with self.assertRaises(ViewError):ThoughtViews(self.snap,self.links*50)

    def test_escape_html_and_never_invent_extra_relations(self):
        self.f.revise_concept('c:home-shelter','<script>alert(1)</script>',
                              'still a concept','synthetic XSS fixture')
        e=ThoughtViews(self.f.snapshot(),self.links)
        run=e.run(LENSES,anchor='m:volunteers')
        svg=render_board(run,self.f.snapshot())
        self.assertNotIn('<script>',svg)
        self.assertIn('&lt;script&gt;',svg)
        for v in run['views']:
            self.assertEqual(v['relations'],e.relations)
            self.assertEqual(v['external_authority'],'NONE')

    def test_demo_synthetic_summary(self):
        report=main()
        self.assertTrue(report['same_source_digest_all_views'])
        self.assertTrue(report['semantic_snapshot_unchanged'])
        self.assertTrue(report['field_replay_exact'])
        self.assertEqual(report['simultaneous_assoc_home_occurrences'],2)
        self.assertEqual(report['external_authority'],'NONE')

if __name__=='__main__':unittest.main()

class LegacyPenCrossingTests(unittest.TestCase):
    def test_explicit_bindings_preserve_pen_and_pencil_separation(self):
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'thought-006'))
        from ledger import ThoughtLedger
        from interop import from_ledger_snapshot
        with TemporaryDirectory() as d:
            f,links=synthetic(Path(d)/'field.jsonl')
            l=ThoughtLedger(Path(d)/'ledger.jsonl')
            for name in ('shelf','meal','storage'):
                l.register_node(name,name)
            l.register_source('thought','origin:hyp','inference','idea only')
            l.register_source('a','origin:a','validated_fixture','first synthetic source')
            l.register_source('b','origin:b','validated_fixture','second synthetic source')
            l.sketch('draft','shelf','enables','meal','fixture:one','a thought','thought')
            l.sketch('reviewed','storage','enables','meal','fixture:one','a working conclusion','thought')
            l.support('reviewed','a','first')
            l.support('reviewed','b','second')
            l.commit('reviewed','fixture:reviewer','strict local fixture review')
            before=l.snapshot()
            relation_packet,skipped=from_ledger_snapshot(before,f.snapshot(),{
                'shelf':'m:shelter-log','meal':'m:meal','storage':'m:storage'})
            self.assertEqual([r['status'] for r in relation_packet],
                             ['HYPOTHESIS_ONLY','AUTHORED'])
            self.assertEqual(len(skipped),0)
            self.assertEqual(l.snapshot(),before)
            e=ThoughtViews(f.snapshot(),relation_packet)
            e.run(LENSES)
            self.assertEqual(l.snapshot(),before)
            l.challenge('reviewed','b','fixture counterexample')
            challenged,_=from_ledger_snapshot(l.snapshot(),f.snapshot(),{
                'shelf':'m:shelter-log','meal':'m:meal','storage':'m:storage'})
            self.assertEqual(challenged[1]['status'],'HYPOTHESIS_ONLY')

    def test_dangerous_implicit_node_merge_rejected(self):
        from interop import from_ledger_snapshot
        with TemporaryDirectory() as d:
            f,_=synthetic(Path(d)/'f.jsonl')
            legacy={'schema':'motif.thought-ledger.snapshot.v1',
                    'nodes':[{'id':'one'},{'id':'two'}], 'sources':[],'assertions':[]}
            with self.assertRaisesRegex(ViewError,'conflation'):
                from_ledger_snapshot(legacy,f.snapshot(),{'one':'m:food','two':'m:food'})
