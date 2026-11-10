"""QC-016: cycle-of-cycle patterns, evidence uncertainty and bounded hierarchy."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"quantumcode015"))
from cycle_field import FieldState,FieldStep
from meta_cycles import NestedMonitor,primitive_from,audit_qc015


def state(t,xy=(0,0),wood=1,food=10,abilities=()):
    return FieldState(tuple(xy),(('wood',wood),),tuple(abilities),
                      (('food',food),('health',9)),t)


def motif(pattern,rounds=2,info_at=None,ability_at=None,
          food_loss_at=None):
    """Synthetic independent loops, each from a shared anchor to a spoke."""
    result=[]
    current=state(0)
    n=0
    for _ in range(rounds):
        for k in pattern:
            n+=1
            after=state(n,(k,0),food=10)
            result.append(FieldStep(current,'go_'+str(k),after,
                                    0 if n!=info_at else 1,
                                    'fixture:'+str(n)))
            current=after
            n+=1
            abilities=('achievement:useful',) if ability_at is not None and n>=ability_at else ()
            food=9 if food_loss_at is not None and n>=food_loss_at else 10
            after=state(n,(0,0),food=food,abilities=abilities)
            result.append(FieldStep(current,'back_'+str(k),after,
                                    0 if n!=info_at else 1,
                                    'fixture:'+str(n)))
            current=after
    return result


class NestedCycleTests(unittest.TestCase):
    def test_two_distinct_base_cycles_multiply_into_meta(self):
        m=NestedMonitor()
        alerts=[m.observe(s) for s in motif([1,2],2)]
        found=[x for x in alerts if x]
        self.assertEqual(len(found),1)
        self.assertEqual(found[0].primitive_motif_length,2)
        self.assertEqual(found[0].motif_repetitions,2)
        self.assertEqual(found[0].total_action_steps,8)
        self.assertEqual(found[0].detected_step,8)
        self.assertEqual(found[0].layer,2)

    def test_meta_three_distinct_motifs(self):
        m=NestedMonitor()
        for x in motif([1,2,3],2):
            a=m.observe(x)
        self.assertIsNotNone(a)
        self.assertEqual(a.primitive_motif_length,3)
        self.assertEqual(a.total_primitive_loops,6)

    def test_seven_distinct_inner_cycles_is_detectable(self):
        m=NestedMonitor()
        alerts=[m.observe(s) for s in motif(list(range(1,8)),2)]
        self.assertEqual(len([x for x in alerts if x]),1)
        x=[x for x in alerts if x][0]
        self.assertEqual(x.primitive_motif_length,7)
        self.assertEqual(x.total_action_steps,28)
        self.assertEqual(len(x.source_receipts),28)

    def test_all_2_to_7_macro_motif_lengths(self):
        for p in range(2,8):
            with self.subTest(motif_length=p):
                m=NestedMonitor()
                alerts=[m.observe(x) for x in motif(list(range(1,p+1)),2)]
                self.assertEqual(len([a for a in alerts if a]),1)
                self.assertEqual([a for a in alerts if a][0].primitive_motif_length,p)

    def test_two_to_seven_repetitions_have_one_debounced_alert(self):
        for rounds in range(2,8):
            with self.subTest(rounds=rounds):
                m=NestedMonitor(max_macro_repetitions=7)
                alerts=[m.observe(x) for x in motif([1,2],rounds)]
                self.assertEqual(len([a for a in alerts if a]),1)

    def test_seven_repeated_cycles_are_counted_without_seven_alerts(self):
        m=NestedMonitor()
        alerts=[m.observe(s) for s in motif([1,2],7)]
        self.assertEqual(len([x for x in alerts if x]),1)
        self.assertIsNotNone(m.active_metacycle)
        self.assertEqual(m.active_metacycle['primitive_motif_length'],2)
        self.assertEqual(m.active_metacycle['repetitions'],7)
        self.assertEqual(m.active_metacycle['total_cycle_units'],14)
        self.assertEqual(m.active_metacycle['last_step'],28)

    def test_positive_information_gain_in_second_round_vetoes_metacycle(self):
        m=NestedMonitor()
        alerts=[m.observe(x) for x in motif([1,2],2,info_at=6)]
        self.assertFalse(any(alerts))
        self.assertEqual(m.resets_due_to_information,1)

    def test_new_capability_in_second_round_blocks_unchanged_cycle(self):
        m=NestedMonitor()
        alerts=[m.observe(x) for x in motif([1,2],2,ability_at=6)]
        self.assertFalse(any(alerts))

    def test_unknown_visibility_is_suspected_not_confirmed(self):
        trace=motif([1,2],2)
        trace=[FieldStep(s.before,s.action,s.after,None,s.source_ref)
               for s in trace]
        m=NestedMonitor()
        alerts=[m.observe(x) for x in trace]
        a=[x for x in alerts if x][0]
        self.assertEqual(a.status,'SUSPECTED_META_CYCLE_VIEW_UNKNOWN')
        self.assertIsNone(a.new_information)

    def test_confirmed_zero_terrain_gain_not_same_as_physical_safety(self):
        m=NestedMonitor()
        alerts=[m.observe(x) for x in motif([1,2],2)]
        a=[x for x in alerts if x][0]
        self.assertEqual(a.status,'CONFIRMED_NO_NEW_SCENE_FACTS_META_CYCLE')
        self.assertFalse(a.action_taken)

    def test_no_alert_for_unbounded_forward_progress(self):
        m=NestedMonitor()
        x=state(0)
        results=[]
        for t in range(30):
            y=state(t+1,(t+1,0))
            results.append(m.observe(FieldStep(x,'move_right',y,0,'fixture:'+str(t))))
            x=y
        self.assertFalse(any(results))

    def test_invalid_window_size_refuses_infinite_compute(self):
        with self.assertRaises(ValueError):
            NestedMonitor(max_macro_period=8)
        with self.assertRaises(ValueError):
            NestedMonitor(max_macro_repetitions=8)
        with self.assertRaises(ValueError):
            NestedMonitor(max_primitive_actions=50)

    def test_noncontiguous_source_refuses(self):
        m=NestedMonitor()
        m.observe(motif([1],1)[0])
        wrong=FieldStep(state(1,(50,0)),'back',
                        state(2,(0,0)),0,'wrong')
        with self.assertRaises(ValueError):
            m.observe(wrong)

    def test_alternating_one_step_action_does_not_qualify_as_two_cycle_motif(self):
        m=NestedMonitor()
        trace=motif([1],4)
        for s in trace:a=m.observe(s)
        self.assertFalse(m.alerts) # same primitive cycle, not two-part meta

    def test_reset_allows_new_episode_after_actual_new_information(self):
        m=NestedMonitor()
        for s in motif([1,2],2):
            m.observe(s)
        self.assertEqual(len(m.alerts),1)
        t=8
        # Observed a new environmental fact; new meta episode must start fresh.
        m.observe(FieldStep(state(t), 'new_info',state(t+1),1,'verified:new'))
        # Construct a fresh traced metacycle from that new time.
        trace=motif([1,2],2)
        for x in trace:
            b=FieldStep(state(x.before.step+9,x.before.xy),
                        x.action,state(x.after.step+9,x.after.xy),
                        x.observed_new_facts,'new:'+x.source_ref)
            m.observe(b)
        self.assertEqual(len(m.alerts),2)

    def test_reanchor_after_new_information_avoids_false_phase(self):
        start=state(0)
        m=NestedMonitor(preferred_anchor=start.structural)
        m.observe(FieldStep(start,"first_exploration",
                            state(1,(1,0)),1,"fixture:first_seen"))
        self.assertTrue(m.awaiting_anchor)
        m.observe(FieldStep(state(1,(1,0)),"return_to_anchor",
                            state(2),0,"fixture:return"))
        self.assertFalse(m.awaiting_anchor)
        results=[]
        for x in motif([1,2],2):
            q=FieldStep(
                state(x.before.step+2,x.before.xy),
                x.action,
                state(x.after.step+2,x.after.xy),
                x.observed_new_facts,"anchored:"+x.source_ref)
            results.append(m.observe(q))
        hits=[x for x in results if x]
        self.assertEqual(len(hits),1)
        self.assertEqual(hits[0].detected_step,10)
        self.assertEqual(hits[0].primitive_motif_length,2)

    def test_audit_does_not_issue_external_actions(self):
        r=audit_qc015(motif([1,2],2))
        self.assertEqual(r['meta_alert_count'],1)
        self.assertEqual(r['automatic_real_world_actions'],0)

if __name__=='__main__':
    unittest.main()
