"""COGNITION-001 falsifiers — actual upstream GHoT decision, native MOTIF-003."""
import unittest
from unittest.mock import patch

from circuit import (AppState, DayBook, FourSpeedMind, Record,
                     MAX_DAILY_UNITS, CAPABILITY, native_ghot,
                     native_affordance, admission, demo_book, demonstration)


def power(**kwargs):
    return AppState(True,True,50,False,95,True,40.,.14,"abundant").__class__(**{
        **{"visible":True,"opted_in":True,"idle_seconds":50,
           "user_task_active":False,"battery_percent":95,
           "charging":True,"thermal_c":40.,"cpu_pressure":.14,
           "power_willingness":"abundant"},**kwargs})


class FourMindTests(unittest.TestCase):
    def test_loaded_actual_motif_and_ghot(self):
        self.assertTrue(callable(native_affordance().analyze_first_moves))
        self.assertTrue(callable(native_ghot()))
        self.assertEqual(admission(power(),3)["ghot_action"],"run_here")

    def test_ghot_normal_battery_background_heavy_holds(self):
        result=admission(power(charging=False,power_willingness="normal"),3)
        self.assertEqual(result["action"],"hold")
        self.assertEqual(result.get("ghot_action"),"hold")

    def test_no_implicit_contemplation_or_hidden_app(self):
        for p in (power(opted_in=False),power(visible=False),
                  power(idle_seconds=0),power(user_task_active=True)):
            self.assertEqual(admission(p,3)["action"],"hold")

    def test_resource_scarcity_holds(self):
        samples=(power(thermal_c=None),power(thermal_c=84.),
                 power(cpu_pressure=.89),power(charging=False,battery_percent=12),
                 power(charging=False,battery_percent=None),
                 power(power_willingness="critical"))
        for state in samples:
            self.assertEqual(admission(state,5)["action"],"hold")

    def test_no_ghot_fallback(self):
        with patch("circuit.native_ghot",side_effect=RuntimeError("NO_NATIVE_GHOT")):
            with self.assertRaisesRegex(RuntimeError,"NO_NATIVE_GHOT"):
                admission(power(),5)

    def test_bounded_daybook_and_immutability(self):
        book=demo_book()
        with self.assertRaises(ValueError):
            book.append(book.rows[0])
        self.assertEqual(book.rows[0].status,"verified_failure")
        assert len(book.identifiers)==len(book.rows)

    def test_reflex_requires_two_successes_and_is_proposal(self):
        book=demo_book()
        self.assertIsNone(book.reflex("review","count_reports"))
        reflex=book.reflex("delivery","route_fast")
        self.assertTrue(reflex["automatic_candidate"])
        self.assertEqual(len(reflex["source_ids"]),2)
        self.assertIs(reflex["effect_executed"],False)

    def test_reflection_preserves_provenance_and_no_causal_assertions(self):
        book=demo_book()
        x=book.reflection("2026-11-11")
        self.assertEqual(x["mode"],"REFLECTION")
        self.assertEqual(x["prior_days"],1)
        self.assertTrue(x["changed_reports"])
        self.assertTrue(all(c["classification"]=="UNRESOLVED_DISAGREEMENT_NOT_CAUSE"
                            for c in x["changed_reports"]))
        self.assertEqual(book.rows[0].status,"verified_failure")

    def test_two_day_cross_origin_multi_lens_and_native003(self):
        mind=FourSpeedMind(demo_book(),"2026-11-11")
        seen=[]
        for _ in range(MAX_DAILY_UNITS):
            r=mind.tick(power())
            self.assertEqual(r["status"],"PROPOSED_NOT_ADMITTED")
            self.assertEqual(r["ghot_decision"],"run_here")
            self.assertTrue(r["native_motif003_executed"])
            card=r["proposal"]
            self.assertEqual(card["status"],"PENCIL_UNTESTED")
            self.assertNotEqual(*card["source_roots"])
            self.assertTrue(card["falsifier"])
            seen.append(tuple(card["source_ids"]+[card["perspective"]]))
        self.assertEqual(len(set(seen)), MAX_DAILY_UNITS)
        self.assertEqual(mind.remaining_units,0)
        self.assertEqual(mind.tick(power())["status"],"HOLD")
        self.assertTrue(mind.saw_native)

    def test_immediate_pause_no_use_of_hidden_app(self):
        mind=FourSpeedMind(demo_book(),"2026-11-11")
        before=mind.remaining_units
        self.assertEqual(mind.tick(power(visible=False))["status"],"HOLD")
        self.assertEqual(mind.remaining_units,before)
        self.assertEqual(len(mind.cards),0)
        self.assertEqual(mind.tick(power())["status"],"PROPOSED_NOT_ADMITTED")
        self.assertEqual(mind.tick(power(user_task_active=True))["status"],"HOLD")
        self.assertEqual(len(mind.cards),1)

    def test_no_independent_origin_no_bridge(self):
        book=DayBook()
        book.append(Record("one","2026-11-10","copy-root","a","x",
                           "reported","First apparent source."))
        book.append(Record("two","2026-11-11","copy-root","a","y",
                           "reported","Repeated same source."))
        mind=FourSpeedMind(book,"2026-11-11")
        r=mind.tick(power())
        self.assertEqual(r["why"],"NO_INDEPENDENT_CROSS_DAY_PAIRS")
        self.assertEqual(mind.remaining_units,MAX_DAILY_UNITS)

    def test_self_optimization_is_hold_not_mutation(self):
        mind=FourSpeedMind(demo_book(),"2026-11-11")
        proposal=mind.proposal_for_optimization()
        self.assertEqual(proposal["status"],"HOLD_FOR_OWNER_REVIEW")
        self.assertFalse(proposal["code_changed"])
        self.assertIsNone(proposal["measured_perf_gain"])
        self.assertEqual(mind.remaining_units,MAX_DAILY_UNITS)

    def test_demo_has_four_modes_and_no_external_action(self):
        x=demonstration()
        self.assertIsNotNone(x["four_modes"]["reflex"])
        self.assertEqual(x["four_modes"]["deliberation"]["mode"],"DELIBERATION")
        self.assertEqual(x["four_modes"]["reflection"]["mode"],"REFLECTION")
        self.assertEqual(x["contemplation"][0]["mode"],"CONTEMPLATION")
        self.assertTrue(x["executed_original_motif003"])
        self.assertEqual(x["external_actions"],x["llm_calls"])
        self.assertFalse(x["app_integration_deployed"])


if __name__=="__main__":
    unittest.main()
