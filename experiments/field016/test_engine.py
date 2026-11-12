import unittest
from dataclasses import replace
from engine import Piece, Route, Scene, Observation, invented_scene, propose, reenter, evaluate, to_json_report

class Field016Test(unittest.TestCase):
    def setUp(self): self.scene=invented_scene()
    def test_initial_has_options(self): self.assertGreater(propose(self.scene)['candidates_total'],0)
    def test_first_uses_relocation_and_porous_as_conditional_hypothesis(self):
        top=propose(self.scene)['candidates'][0]
        self.assertEqual(top['route_id'],'repositioned')
        self.assertEqual(top['pieces'],['porous'])
        self.assertEqual(top['status'],'HOLD_PHYSICAL_INSTALLATION_UNVERIFIED')
    def test_measured_width_can_falsify_first(self):
        n=reenter(self.scene,Observation('evt1','MEASURED','piece_width','porous',1.32,1))
        top=propose(n)['candidates'][0]
        self.assertNotEqual(top['pieces'],['porous'])
        self.assertFalse(any(x['pieces']==['porous'] for x in propose(n)['candidates']))
    def test_measuring_width_does_not_certify_other_properties(self):
        n=reenter(self.scene,Observation('evt1','MEASURED','piece_width','porous',1.32,1))
        p=next(x for x in n.pieces if x.id=='porous')
        self.assertTrue(p.measured_width)
        self.assertEqual(p.evidence,'HYPOTHETICAL')
    def test_guessed_width_does_not_count_as_measured(self):
        n=reenter(self.scene,Observation('evt1','MODEL_TENTATIVE','piece_width','porous',1.32,1))
        self.assertFalse(n.pieces[2].measured_width)
    def test_route_shortening_avoids_second_panel(self):
        a=propose(self.scene)
        self.assertEqual(a['candidates'][0]['route_id'],'repositioned')
        self.assertTrue(all(len(x['pieces'])>=2 for x in a['candidates'] if x['route_id']=='original'))
    def test_connections_do_not_certify_bracing(self):
        a=propose(self.scene)
        two=next(x for x in a['candidates'] if len(x['pieces'])==2)
        self.assertFalse(two['joint_topology']['load_sharing_solved'])
        self.assertFalse(two['safety_certified'])
    def test_no_capacity_from_zip_ties(self):
        a=propose(self.scene)
        self.assertTrue(any('uncharacterized_joints_and_mutual_bracing' in x['uncertainties'] for x in a['candidates']))
        self.assertTrue(all(x['pet_containment_certified']==False for x in a['candidates']))
    def test_wind_changes_results(self):
        low=propose(replace(self.scene,wind_mps=4))
        high=propose(replace(self.scene,wind_mps=12))
        def selected(rows,route,piece):
            return next(x for x in rows['candidates'] if x['route_id']==route and x['pieces']==[piece])
        self.assertGreater(selected(high,'repositioned','privacy')['model_wind_force_n'],
                           selected(low,'repositioned','privacy')['model_wind_force_n'])
    def test_physical_safety_not_verified_even_if_model_screen_holds(self):
        self.assertFalse(any(x['safety_certified'] for x in propose(self.scene)['candidates']))
    def test_mismatched_3d_gap_flagged(self):
        n=reenter(self.scene,Observation('evt1','MEASURED','clearance','porous',.12,1))
        x=next(a for a in propose(n)['candidates'] if a['route_id']=='repositioned' and a['pieces']==['porous'])
        self.assertEqual(x['status'],'MODEL_FAILS_STATED_SCENARIO')
    def test_clearance_none_holds(self):
        x=propose(self.scene)['candidates'][0]
        self.assertIn('ground_clearance_unknown:porous',x['uncertainties'])
    def test_unmeasured_dog_gap_limit_does_not_invent_threshold(self):
        routes=tuple(replace(r,maximum_ground_clearance_m=None) for r in self.scene.routes)
        n=replace(self.scene,routes=routes)
        x=propose(n)['candidates'][0]
        self.assertFalse(x['pet_containment_certified'])
    def test_wrong_provenance_rejected(self):
        with self.assertRaises(ValueError):reenter(self.scene,Observation('x','VERIFIED_BY_MAGIC','piece_width','porous',1.2,1))
    def test_replayed_revision_required(self):
        with self.assertRaises(ValueError):reenter(self.scene,Observation('x','MEASURED','piece_width','porous',1.2,9))
    def test_empty_id_rejected(self):
        with self.assertRaises(ValueError):replace(self.scene,pieces=(replace(self.scene.pieces[0],id=''),)).validate()
    def test_bad_dimensions_rejected(self):
        with self.assertRaises(ValueError):replace(self.scene,pieces=(replace(self.scene.pieces[0],width_m=-1),)).validate()
    def test_bool_dimension_rejected(self):
        with self.assertRaises(ValueError):replace(self.scene,pieces=(replace(self.scene.pieces[0],width_m=True),)).validate()
    def test_unknown_masses_dont_invent_safe_conclusion(self):
        n=replace(self.scene,pieces=tuple(replace(p,mass_kg=None) for p in self.scene.pieces))
        self.assertTrue(all(x['status']=='HOLD_PHYSICAL_INSTALLATION_UNVERIFIED' for x in propose(n)['candidates']))
    def test_unknown_width_has_only_held_coverage(self):
        n=replace(self.scene,pieces=tuple(replace(p,width_m=None) for p in self.scene.pieces))
        self.assertTrue(all(x['span_status']=='HOLD_WIDTH_UNKNOWN' for x in propose(n)['candidates']))
    def test_no_link_without_connector(self):
        n=replace(self.scene,salvage_connections_available=False)
        self.assertTrue(all(len(x['pieces'])==1 for x in propose(n)['candidates']))
    def test_no_world_coordinate_inferred(self):
        for x in propose(self.scene)['candidates']:
            for p in x['local_3d_schematic']:
                self.assertEqual(p['coordinate_status'],'HYPOTHETICAL_LOCAL_FRAME_NOT_SITE_REGISTERED')
    def test_separate_human_access_unknowns(self):
        x=propose(self.scene)['candidates'][0]
        self.assertIn('human_access_route_unknown',x['uncertainties'])
    def test_photo_source_not_transferred_into_site(self):
        n=replace(self.scene,pieces=(replace(self.scene.pieces[0],source_id='photo-1'),)+self.scene.pieces[1:])
        self.assertTrue(all('site_xy' not in p for x in propose(n)['candidates'] for p in x['local_3d_schematic']))
    def test_user_revisions_change_receipt(self):
        event=Observation('m1','MEASURED','piece_width','porous',1.32,1)
        report=to_json_report(self.scene,(event,))
        self.assertNotEqual(report['initial']['digest_sha256'],report['final']['digest_sha256'])
        self.assertEqual(len(report['timeline']),2)
    def test_unknown_route_span_produces_hold(self):
        n=replace(self.scene,routes=(replace(self.scene.routes[0],span_m=None),))
        report=propose(n)
        self.assertEqual(report['next_probe']['kind'],'MEASUREMENT')
    def test_too_many_items_bounded(self):
        n=replace(self.scene,pieces=tuple(replace(self.scene.pieces[0],id='p%d'%i) for i in range(11)))
        with self.assertRaises(ValueError):propose(n)
    def test_unknown_event_rejected(self):
        with self.assertRaises(ValueError):reenter(self.scene,Observation('evt1','MEASURED','set_safety','porous',True,1))
    def test_opaque_vs_mesh_separately_screened(self):
        from engine import _panel
        from physics import wind_load
        opaque=wind_load(_panel(self.scene.pieces[0]),8)['force_n']
        porous=wind_load(_panel(self.scene.pieces[2]),8)['force_n']
        self.assertAlmostEqual(opaque,porous*5)
    def test_next_probe_is_targeted_counterfactual(self):
        probe=propose(self.scene)['next_probe']
        self.assertEqual(probe['kind'],'DECISION_CHANGING_MEASUREMENT')
        self.assertEqual(probe['subject'],'porous')
        self.assertTrue(probe['would_eliminate_current_best_if_true'])
    def test_deterministic(self):
        self.assertEqual(propose(self.scene)['digest_sha256'],propose(self.scene)['digest_sha256'])

if __name__=='__main__':unittest.main()
