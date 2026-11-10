"""QC-015: falsifiers for multi-action loops and progress/novelty guards."""
import unittest
from cycle_field import FieldState,FieldStep,CycleMonitor


def state(i,xy,food=9,wood=1,cap=()):
    return FieldState(tuple(xy),(('wood',wood),),tuple(cap),
                      (('food',food),('drink',9),('health',9)),i)


def sequence(locations,actions,info=None,food=9):
    if info is None:info=[0]*len(actions)
    result=[]
    for i,a in enumerate(actions):
        result.append(FieldStep(state(i,locations[i],food=food-i//3),a,
                                state(i+1,locations[i+1],food=food-(i+1)//3),
                                info[i],f'synthetic:{i}'))
    return result


class Cycles(unittest.TestCase):
    def test_two_tile_pendulum_detected(self):
        seq=sequence([(0,0),(1,0),(0,0),(1,0),(0,0)],
                     ['move_right','move_left']*2)
        m=CycleMonitor()
        self.assertIsNone(m.observe(seq[0]))
        self.assertIsNone(m.observe(seq[1]))
        self.assertIsNone(m.observe(seq[2]))
        a=m.observe(seq[3])
        self.assertEqual(a.period,2)
        self.assertEqual(a.detected_step,4)
        self.assertEqual(a.status,'CONFIRMED_NO_INFORMATION_CYCLE')
        self.assertIn(('food',-1),a.vital_debt)

    def test_four_action_loop_detected(self):
        loc=[(0,0),(1,0),(1,1),(0,1),(0,0),(1,0),(1,1),(0,1),(0,0)]
        actions=['move_right','move_down','move_left','move_up']*2
        m=CycleMonitor(max_period=5)
        res=[m.observe(x) for x in sequence(loc,actions)]
        self.assertEqual(res[-1].period,4)

    def test_progressive_walking_is_not_stuck(self):
        seq=sequence([(i,0) for i in range(25)],['move_right']*24)
        m=CycleMonitor()
        self.assertEqual([m.observe(x) for x in seq],[None]*24)

    def test_new_information_prevents_false_alarm(self):
        seq=sequence([(0,0),(1,0),(0,0),(1,0),(0,0)],
                     ['move_right','move_left']*2,[0,0,1,0])
        m=CycleMonitor()
        self.assertFalse(any(m.observe(x) for x in seq))

    def test_vital_debt_doesnt_prevent_cycle_detection(self):
        seq=sequence([(0,0),(1,0),(0,0),(1,0),(0,0)],
                     ['move_right','move_left']*2,food=5)
        m=CycleMonitor()
        for x in seq:a=m.observe(x)
        self.assertEqual(a.period,2)
        self.assertLess(dict(a.vital_debt)['food'],0)

    def test_unknown_scene_information_is_suspected_not_confirmed(self):
        seq=sequence([(0,0),(1,0),(0,0),(1,0),(0,0)],
                     ['move_right','move_left']*2,[None]*4)
        m=CycleMonitor()
        for x in seq:a=m.observe(x)
        self.assertEqual(a.status,'SUSPECTED_CYCLE_VIEW_UNKNOWN')

    def test_inventory_gain_prevents_loop_mark(self):
        v=[(0,0),(1,0),(0,0),(1,0),(0,0)]
        seq=sequence(v,['move_right','move_left']*2)
        seq[1]=FieldStep(seq[1].before,seq[1].action,
                         state(2,v[2],wood=2),0,'gain')
        seq[2]=FieldStep(state(2,v[2],wood=2),seq[2].action,
                         state(3,v[3],wood=2),0,'continue')
        seq[3]=FieldStep(state(3,v[3],wood=2),seq[3].action,
                         state(4,v[4],wood=2),0,'continue')
        m=CycleMonitor()
        self.assertFalse(any(m.observe(x) for x in seq))

    def test_state_discontinuity_refuses(self):
        m=CycleMonitor()
        m.observe(sequence([(0,0),(1,0)],['move_right'])[0])
        with self.assertRaises(ValueError):
            m.observe(sequence([(20,0),(21,0)],['move_right'])[0])

    def test_a_b_a_loop_not_reduced_to_same_action(self):
        seq=sequence([(0,0),(1,0),(2,0),(0,0),(1,0),(2,0),(0,0)],
                     ['move_right','move_right','move_left']*2)
        m=CycleMonitor()
        for x in seq:a=m.observe(x)
        self.assertEqual(a.period,3)

    def test_hysteresis_never_spams_same_repeat(self):
        seq=sequence([(0,0),(1,0)]*8+[(0,0)],
                     ['move_right','move_left']*8)
        m=CycleMonitor()
        emitted=[m.observe(x) for x in seq]
        self.assertLessEqual(len([x for x in emitted if x]),3)

    def test_unknown_input_no_bare_negative_claims(self):
        with self.assertRaises(ValueError):
            FieldStep(state(0,(0,0)),'x',state(1,(1,0)),-1,'fixture')

    def test_hard_bounded_period(self):
        with self.assertRaises(ValueError):CycleMonitor(max_period=200)

    def test_false_positive_if_static_but_new_achievement(self):
        seq=sequence([(0,0),(1,0),(0,0),(1,0),(0,0)],
                     ['move_right','move_left']*2)
        seq[1]=FieldStep(seq[1].before,seq[1].action,
                         state(2,(0,0),cap=('achievement:a',)),0,'gained')
        seq[2]=FieldStep(state(2,(0,0),cap=('achievement:a',)),seq[2].action,
                         state(3,(1,0),cap=('achievement:a',)),0,'cont')
        seq[3]=FieldStep(state(3,(1,0),cap=('achievement:a',)),seq[3].action,
                         state(4,(0,0),cap=('achievement:a',)),0,'cont')
        m=CycleMonitor()
        self.assertFalse(any(m.observe(x) for x in seq))

if __name__=='__main__':unittest.main()
