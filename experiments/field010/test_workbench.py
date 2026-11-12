import copy,json,unittest
from pathlib import Path
from workbench import replay,think,span,valid_item
BASE=json.loads((Path(__file__).parent/'fixture.json').read_text())

class Field010Tests(unittest.TestCase):
    def setUp(self):self.p=copy.deepcopy(BASE)
    def do(self,typ,**fields):
        self.p['events'].append(dict(id=f'e{len(self.p["events"])+1}',type=typ,source='USER_BOARD_EDIT',**fields))
        return replay(self.p)
    def test_fixture_load(self):self.assertEqual(len(replay(self.p)['items']),6)
    def test_two_branches_read_version(self):
        r=think(self.p);self.assertEqual(r['solver']['version'],r['interface']['version'])
        self.assertEqual(r['state_version'],0)
    def test_no_auto_truth(self):
        r=think(self.p);self.assertFalse(r['solver']['verified_physical_assembly'])
        self.assertFalse(r['solver']['auto_placed_photo_coordinates'])
        self.assertEqual(r['status'],'HYPOTHETICAL_EDITABLE_SKETCH_NOT_ENGINEERING_PLAN')
    def test_add_desired(self):
        state=self.do('add',item={'id':'z','kind':'desired','label':'New trace','status':'tentative','movable':True,'points':[[.2,.4],[.6,.6]]})
        self.assertEqual(len(state['items']),7)
    def test_source_immutable_after_move(self):
        before=copy.deepcopy(self.p['base'])
        self.do('move',target='current-west',delta=[.1,.02]);self.assertEqual(self.p['base'],before)
    def test_move_can_be_negative(self):
        s=self.do('move',target='current-west',delta=[-.02,-.02]);self.assertAlmostEqual(s['items'][0]['points'][0][0],.11)
    def test_move_rejects_outside_image(self):
        with self.assertRaises(ValueError):self.do('move',target='current-west',delta=[-.9,0])
    def test_endpoint_change(self):
        s=self.do('endpoint',target='target-one',index=1,point=[.7,.33]);self.assertEqual(s['items'][2]['points'][1],[.7,.33])
    def test_invalid_pixel_coordinate_rejected(self):
        with self.assertRaises(ValueError):self.do('endpoint',target='target-one',index=1,point=[123,15])
    def test_support_must_be_one_point(self):
        with self.assertRaises(ValueError):self.do('add',item={'id':'bad','kind':'support','label':'X','status':'tentative','movable':False,'points':[[.1,.1],[.2,.2]]})
    def test_rough_guess_cannot_calibrate(self):
        self.do('measure',target='target-one',value=4,unit='ft',quality='rough_guess')
        self.do('proportional',value=True,tolerance=.4)
        self.assertFalse(think(self.p)['solver']['estimates'])
    def test_one_measured_anchor_only_conditional(self):
        self.do('measure',target='target-one',value=4,unit='ft',quality='user_measured')
        self.do('proportional',value=True,tolerance=.4)
        sol=think(self.p)['solver'];self.assertEqual(len(sol['estimates']),2)
        self.assertEqual(sol['estimates'][0]['status'],'human_entered_reference')
        self.assertEqual(sol['estimates'][0]['low'],4)
        self.assertLess(sol['estimates'][1]['low'],sol['estimates'][1]['high'])
    def test_no_sketch_proportionality_no_scale(self):
        self.do('measure',target='target-one',value=4,unit='ft',quality='user_measured')
        sol=think(self.p)['solver'];self.assertFalse(sol['estimates']);self.assertTrue(sol['warnings'])
    def test_contradictory_same_unit_anchors_hold(self):
        self.do('measure',target='target-one',value=4,unit='ft',quality='user_measured')
        self.do('measure',target='target-two',value=30,unit='ft',quality='user_measured')
        self.do('proportional',value=True,tolerance=.4)
        sol=think(self.p)['solver'];self.assertFalse(sol['estimates']);self.assertTrue(sol['warnings'])
    def test_mixed_units_hold(self):
        self.do('measure',target='target-one',value=4,unit='ft',quality='user_measured')
        self.do('measure',target='target-two',value=5,unit='m',quality='user_measured')
        self.do('proportional',value=True,tolerance=.4)
        self.assertFalse(think(self.p)['solver']['estimates'])
    def test_rejection_filters_suggestions(self):
        self.do('set',target='target-two',prop='status',value='user_rejected')
        self.assertEqual(len(think(self.p)['solver']['ratios']),0)
    def test_ratio_propagates_only_as_hypothesis(self):
        self.do('ratio',target='target-two',other='target-one',value=2)
        self.do('measure',target='target-one',value=4,unit='ft',quality='user_measured')
        result=think(self.p)['solver']
        self.assertEqual(result['ratio_cues'][0]['implied_nominal'],8)
        self.assertFalse(result['estimates'])
    def test_ratio_is_user_relational_not_metric(self):
        s=self.do('ratio',target='target-one',other='target-two',value=2)
        self.assertEqual(s['relations'][0]['status'],'user_relation_not_measured')
        self.assertFalse(think(self.p)['solver']['estimates'])
    def test_undo_preserves_event_evidence(self):
        self.do('move',target='current-west',delta=[.04,0])
        st=self.do('revert',target_event='e1')
        self.assertEqual(st['items'][0]['points'],self.p['base']['items'][0]['points']);self.assertEqual(len(self.p['events']),2)
    def test_remove_only_from_projection(self):
        self.do('remove',target='target-one');self.assertNotIn('target-one',[x['id'] for x in replay(self.p)['items']])
        self.assertIn('target-one',[x['id'] for x in self.p['base']['items']])
    def test_choose_low_friction_interaction(self):
        self.p['base']['items']=[x for x in self.p['base']['items'] if x['kind']!='desired']
        prompts=think(self.p)['interface']['actions']
        self.assertEqual(prompts[0]['action'],'trace_desired')
    def test_no_user_answer_required_to_start(self):
        self.assertTrue(think(self.p)['interface']['never_required_to_answer'])
    def test_schema_mismatch(self):
        self.p['schema']='wrong'
        with self.assertRaises(ValueError):replay(self.p)
    def test_duplicate_base_id(self):
        self.p['base']['items'].append(copy.deepcopy(self.p['base']['items'][0]))
        with self.assertRaises(ValueError):replay(self.p)
    def test_missing_source_frame(self):
        self.p['base']['coordinate_frame']='photo_registered'
        with self.assertRaises(ValueError):replay(self.p)
    def test_invalid_event_unknown(self):
        with self.assertRaises(ValueError):self.do('auto_approve_fence',target='target-one')
    def test_document_source_cannot_be_changed_by_user_edit(self):
        before=copy.deepcopy(self.p['base'])
        self.do('set',target='panel-one',prop='label',value='Different label')
        self.assertEqual(self.p['base'],before)

if __name__=='__main__': unittest.main()
