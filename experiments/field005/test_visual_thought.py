import unittest, json
from pathlib import Path
from visual_thought import Object,Scene,think,critique,svg_sketch,run,load

class TestField005(unittest.TestCase):
    def setUp(self):
        self.panel=Object('p1','wire rack','animal cage',('delineate','support'),('rigid','flat'),'SYNTHETIC','YES',(.1,.1,.3,.4))
        self.panel2=Object('p2','rack two','animal cage',('delineate',),('rigid','flat'),'SYNTHETIC','UNKNOWN',(.35,.1,.5,.4))
        self.tie=Object('t1','ties','fastening',(),('connector',),'SYNTHETIC','YES')
        self.frame=Object('f1','trampoline','recreation',('support',),('frame',),'SYNTHETIC','NO')
        self.scene=Scene('visual boundary','delineate',(self.panel,self.panel2,self.tie,self.frame),((.1,.8),(.8,.8)),((.1,.6),(.8,.6)))
    def test_reassign(self):self.assertIn('REASSIGN_FUNCTION',[p.operation for p in think(self.scene)])
    def test_relocate(self):self.assertIn('RELOCATE_EXISTING',[p.operation for p in think(self.scene)])
    def test_move_fixed_not_suggested(self):
        self.assertFalse(any('f1' in x.ingredients and x.operation=='RELOCATE_EXISTING' for x in think(self.scene)))
    def test_compose(self):self.assertIn('COMPOSE_NETWORK',[p.operation for p in think(self.scene)])
    def test_opportunistic_support(self):self.assertIn('OPPORTUNISTIC_SUPPORT',[p.operation for p in think(self.scene)])
    def test_redraw(self):self.assertIn('REDRAW_PROBLEM',[p.operation for p in think(self.scene)])
    def test_no_connector_is_new_subproblem(self):
        s=Scene('boundary','delineate',(self.panel,self.panel2))
        self.assertIn('INVENT_MISSING_JOIN',[p.operation for p in think(s)])
    def test_missing_affordance_not_fabricated(self):
        o=Object('toy','toy','play',('hold',),('flexible',),'SYNTHETIC','YES')
        self.assertEqual(think(Scene('boundary','delineate',(o,))),())
    def test_unknown_mobility_not_true(self):
        holds=[r['holds'] for r in critique(self.scene,think(self.scene))]
        self.assertTrue(any('MOVABILITY_UNKNOWN' in h for h in holds))
    def test_bracing_no_guarantees(self):
        holds={r['proposal']:r['holds'] for r in critique(self.scene,think(self.scene))}
        self.assertTrue(any('NO_STRUCTURAL_VALIDATION' in h for n,h in holds.items() if n.startswith('COMPOSE_NETWORK:')))
    def test_repeated_result_deterministic(self):self.assertEqual(run(self.scene),run(self.scene))
    def test_no_proposal_executed(self):self.assertFalse(any(x['executed'] for x in run(self.scene)['critique']))
    def test_svg_hypothesis_and_solid(self):
        svg=svg_sketch(self.scene,think(self.scene))
        self.assertIn('stroke-dasharray',svg);self.assertIn('NOT TO SCALE',svg)
    def test_svg_escapes_untrusted_text(self):
        p=Object('x','<script>alert(1)</script>','play',('support',),('rigid',),'MODEL_TENTATIVE')
        self.assertNotIn('<script>',svg_sketch(Scene('support','support',(p,)),()))
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):think(Scene('goal','support',(self.panel,self.panel)))
    def test_bad_bbox_rejected(self):
        x=Object('x','x','hold',('support',),('rigid',),'SYNTHETIC',bbox=(.9,.9,.1,.1))
        with self.assertRaises(ValueError):think(Scene('x','support',(x,)))
    def test_bad_goal_rejected(self):
        with self.assertRaises(ValueError):think(Scene('goal','do_magic',(self.panel,)))
    def test_empty_still_has_receipt(self):
        self.assertEqual(run(Scene('repair','support',()))['scene_objects'],0)
    def test_tentative_model_is_not_safety_approval(self):
        o=Object('p','unknown panel','unknown',('support',),('rigid',),'MODEL_TENTATIVE')
        r=run(Scene('support','support',(o,)))
        self.assertTrue(all(x['status']!='VERIFIED' for x in r['critique']))
    def test_no_scale_from_bbox(self):
        self.assertIn('NOT TO SCALE',svg_sketch(self.scene,think(self.scene)))
    def test_loader_roundtrip(self):
        raw={'goal':'shelf','desired_function':'support','things':[{'id':'c','label':'crate','original_use':'shipping','capabilities':['support'],'features':['rigid'],'origin':'SYNTHETIC','source':'fixture'}]}
        self.assertEqual(load(raw).things[0].id,'c')
    def test_loader_rejects_unknown(self):
        with self.assertRaises(ValueError):load({'goal':'x','desired_function':'hold','things':[],'steal':'x'})

if __name__=='__main__':unittest.main()