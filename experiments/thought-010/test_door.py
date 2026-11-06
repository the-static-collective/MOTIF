"""Synthetic contract, privacy and source-authority adversarial tests."""
import copy
import json
import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from door import DoorError, handle, _infer_goals
from free_graph import canonical, record

SAMPLE = json.loads((Path(__file__).parent / 'example-ideas.json').read_text())


class DoorTests(unittest.TestCase):
    def case(self, **overrides):
        data = copy.deepcopy(SAMPLE)
        data.update(overrides)
        return data

    def test_jarvis_local_ideas_route_and_questions(self):
        out = handle(self.case())
        self.assertEqual(out['schema'], 'motif.thought-door.reply.v1')
        self.assertEqual(out['selected_lenses'], ['association'])
        self.assertEqual(out['export']['status'], 'HOLD')
        self.assertTrue(out['questions'])
        self.assertEqual(out['questions'][0]['status'], 'QUESTION_ONLY')
        self.assertEqual(out['external_authority'], 'NONE')
        self.assertEqual(out['pen_status'], 'UNCHANGED')

    def test_no_link_from_words_or_layout_alone(self):
        q = self.case(ideas=['home', 'home', 'belonging'], relationships=[], goals=['association'])
        out = handle(q)
        self.assertEqual(out['selected_lenses'], [])
        self.assertEqual(out['questions'], [])
        self.assertIn('zero relations', out['warnings'][-1])
        self.assertEqual(out['source_only_answers']['association'], [])

    def test_nonfungible_same_word_maintained_in_one_view(self):
        q = self.case(ideas=['home', 'home'], relationships=[], goals=['inventory'],
                      include_views=True)
        out = handle(q)
        self.assertEqual(out['selected_lenses'], [])
        self.assertEqual(out['source_only_answers']['inventory']['concepts'], 2)
        self.assertEqual(out['source_only_answers']['inventory']['manifestations'], 2)

    def test_authored_edge_does_not_become_pen_or_truth(self):
        out = handle(self.case(include_views=True))
        self.assertEqual(out['views'][0]['relations'][0]['status'], 'AUTHORED')
        self.assertTrue(all(x['external_authority'] == 'NONE' for x in out['views']))
        self.assertEqual(out['pen_status'], 'UNCHANGED')

    def test_no_map_still_answers_identically(self):
        a = handle(self.case(max_views=0))
        b = handle(self.case(max_views=2))
        self.assertEqual(a['source_only_answers'], b['source_only_answers'])
        self.assertEqual(a['questions'], b['questions'])
        self.assertEqual(a['source_evidence_digest'], b['source_evidence_digest'])
        self.assertEqual(a['view_cost_units'], 0)

    def test_pen_review_makes_no_geometry_and_no_commit(self):
        out = handle(self.case(phase='PEN_REVIEW', max_views=3))
        self.assertEqual(out['selected_lenses'], [])
        self.assertEqual(out['pen_status'], 'UNCHANGED')

    def test_private_export_requires_both_consents(self):
        for override in (
            {'privacy': 'PRIVATE_LOCAL', 'allow_export': True},
            {'privacy': 'PUBLIC_FIXTURE', 'allow_export': False},
        ):
            response = handle(self.case(**override))
            self.assertEqual(response['export']['status'], 'HOLD')
            self.assertNotIn('packet', response['export'])

    def test_public_free_graph_seed_structurally_matches_contract(self):
        out = handle(self.case(privacy='PUBLIC_FIXTURE', allow_export=True))
        packet = out['export']['packet']
        self.assertEqual(packet['schema'], 'free-graph.packet/v0')
        self.assertEqual(packet['task_world_cut']['status'], 'unresolved')
        self.assertEqual(packet['modes'], ['seed', 're-enter'])
        self.assertTrue(all(x['status'] == 'proposed' for x in packet['nodes']))
        self.assertTrue(all(x['status'] == 'proposed' for x in packet['links']))
        self.assertTrue(all(x['verb'] == 'connects' for x in packet['links']))
        self.assertTrue(all(x['authority'] == 'none' for x in packet['links']))
        self.assertTrue(all('constitutes' != x['verb'] for x in packet['links']))
        self.assertEqual(len(packet['nodes']), 6)
        self.assertEqual(len(packet['links']), 5)
        # Verify content-addressed records against the owning project's algorithm.
        for kind, key in [('source', 'sources'), ('node', 'nodes'), ('link', 'links')]:
            for item in packet[key]:
                self.assertEqual(record(kind, item)['id'], item['id'])
        import hashlib
        self.assertEqual('fgp:sha256:' + hashlib.sha256(canonical(packet,'packet_id')).hexdigest(), packet['packet_id'])
        self.assertEqual(len(set(x['id'] for x in packet['nodes'])), 6)
        # Multiple appearances of the same label do not merge into one node.
        self.assertEqual(len([n for n in packet['nodes'] if n['label'].startswith('Home ')]), 2)

    def test_owner_validator_when_checked_out(self):
        # CI may supply an exact-pinned, separate public Free Graph source tree.
        core = os.environ.get('FREE_GRAPH_CORE')
        if not core:
            self.skipTest('owner validator not installed; CI separately checks out pinned Free Graph')
        import importlib.util
        spec = importlib.util.spec_from_file_location('source_owner_fg_core', core)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        packet = handle(self.case(privacy='PUBLIC_FIXTURE', allow_export=True))['export']['packet']
        self.assertEqual(module.validate_packet(packet), [])

    def test_missing_relationship_reference_fails_closed(self):
        q = self.case(relationships=[{'from':0,'to':99,'predicate':'associated',
                                     'origin':'x','status':'AUTHORED'}])
        with self.assertRaisesRegex(DoorError, 'indices'):handle(q)

    def test_inferred_goal_falls_back_to_inventory(self):
        self.assertEqual(_infer_goals('wonder about these'), ('inventory',))
        self.assertEqual(_infer_goals('what do these require'), ('dependency',))
        out = handle(self.case(goals=['inventory'],max_views=3))
        self.assertEqual(out['selected_lenses'],[])

    def test_hypothetical_relationship_never_used_for_inference(self):
        q = self.case(ideas=['a','b'], relationships=[{'from':0,'to':1,
             'predicate':'associated','origin':'fixture','status':'HYPOTHESIS_ONLY'}],
             goals=['association'],include_views=True)
        out=handle(q)
        self.assertEqual(out['selected_lenses'],[])
        self.assertEqual(out['source_only_answers']['association'],[])

    def test_malformed_requests_rejected_without_mutation(self):
        for bad in (
            {'schema':'unknown'},
            {'caller':'remote-executor'},
            {'privacy':'PUBLIC'},
            {'mode':'scripts'},
            {'ideas':['a']*25},
            {'ideas':['bad']*2, 'max_views':True},
            {'goals':['not_a_goal']},
            {'include_views':'true'},
            {'allow_export':1},
            {'seed':float('nan')},
            {'extra_instruction':'connect automatically'},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises((DoorError, ValueError, TypeError)):
                    handle(self.case(**bad))

    def test_snapshot_path_reuses_actual_007_and_009_without_mutating(self):
        from fixtures import make_engine
        with TemporaryDirectory() as tmp:
            # Build separate source snapshot via public THOUGHT-009 fixture.
            engine=make_engine(Path(tmp)/'source.jsonl')
            source=copy.deepcopy(engine._original)
            relations=copy.deepcopy(engine.relations)
            q=self.case(mode='snapshot',ideas=None,relationships=None)
            del q['ideas'],q['relationships']
            q['field_snapshot']=source
            q['relations']=relations
            q['anchor']='m:volunteers'
            q['goals']=['dependency','affordance','association']
            q['max_views']=2
            before=json.dumps(source,sort_keys=True)
            out=handle(q)
            self.assertEqual(json.dumps(source,sort_keys=True),before)
            self.assertEqual(out['view_cost_units'],2)
            self.assertIn('dependency',out['selected_lenses'])
            self.assertTrue(out['source_only_answers']['affordance']['conditional_reach'])
            self.assertEqual(out['source_evidence_digest'],engine.input_digest)

    def test_snapshot_unknown_binding_no_auto_word_matching(self):
        from fixtures import make_engine
        with TemporaryDirectory() as d:
            engine=make_engine(Path(d)/'source.jsonl')
            q=self.case(mode='snapshot',ideas=None,relationships=None)
            del q['ideas'],q['relationships']
            q.update(field_snapshot=engine._original, relations=engine.relations, anchor='Home')
            with self.assertRaisesRegex(DoorError,'unknown manifestation anchor'):handle(q)

    def test_declared_private_labels_not_in_response_unless_views_requested(self):
        q=self.case(ideas=['super-secret-phrase-123','another-private-idea'],relationships=[],
                    goals=['inventory'],max_views=0,include_views=False)
        text=json.dumps(handle(q))
        self.assertNotIn('super-secret-phrase-123',text)
        self.assertNotIn('another-private-idea',text)

    def test_repeated_call_is_deterministic(self):
        self.assertEqual(handle(self.case()),handle(self.case()))


if __name__=='__main__': unittest.main()
