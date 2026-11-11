"""VOID-004 research invariants; fixture semantics only, no independent validation claim."""
from copy import deepcopy
import unittest
from waves import (MAP, HUB, WAVES, MAX_ATTEMPTS, PREP_STEPS,
                   DEV_SEEDS, TEST_SEEDS, RELAY_COVERAGE, POLICIES, POSITIONS,
                   FortOwner, Knowledge, public_route, verified, seal, native003,
                   choose_motif, choose_classical, expected_progress, run_case,
                   benchmark)

class WaveTests(unittest.TestCase):
    def test_map_and_wave_design(self):
        self.assertEqual(WAVES, 24)
        self.assertEqual(len(MAP), 9)
        self.assertEqual(len(POSITIONS), 4)
        self.assertEqual(len(TEST_SEEDS), 24)
        self.assertTrue(set(DEV_SEEDS).isdisjoint(TEST_SEEDS))
        self.assertTrue(all(len(public_route(r)) <= PREP_STEPS for r in RELAY_COVERAGE))
        self.assertEqual(len(set(w for slots in RELAY_COVERAGE.values() for w in slots)), 12)

    def test_public_view_hides_attack_directions(self):
        owner=FortOwner(DEV_SEEDS[0]); view=owner.public_view()
        self.assertNotIn("_lanes",view)
        self.assertEqual(view["wave_count"] if "wave_count" in view else view["waves"],WAVES)
        self.assertFalse(any(d in str(view) for d in ("actual_gate", "gate_schedule")))

    def test_no_remote_relay_intel(self):
        owner=FortOwner(DEV_SEEDS[0]);owner.begin()
        with self.assertRaises(RuntimeError):owner.read_relay()
        with self.assertRaises(ValueError):owner.walk("diagonal")

    def test_relay_and_sonar_share_one_battery(self):
        owner=FortOwner(DEV_SEEDS[0]);owner.begin()
        for action in public_route("A"):
            self.assertTrue(verified(owner.walk(action)))
        relay=owner.read_relay()
        self.assertTrue(verified(relay)); self.assertEqual(owner.sonar_left,0)
        owner.start_waves()
        with self.assertRaises(RuntimeError):owner.sonar()
        # Next attempt requires actually failing (or clearing) this one.
        owner.defend(next(x for x in ("N","E","S","W") if x != owner._lanes[1]))
        owner.begin(); self.assertEqual(owner.sonar_left,1)

    def test_reported_failure_learns_fact_but_does_not_forge_success(self):
        owner=FortOwner(DEV_SEEDS[0]);memory=Knowledge()
        memory.learn(owner.begin());memory.learn(owner.start_waves())
        threat=owner.sonar();memory.learn(threat)
        wrong=next(x for x in ("N","E","S","W") if x != threat["gate"])
        result=owner.defend(wrong)
        memory.learn(result)
        self.assertFalse(result["held"]);self.assertEqual(owner.phase,"failed")
        self.assertEqual(memory.gates[1],threat["gate"])

    def test_source_hash_detects_unsealed_tampering(self):
        o=FortOwner(DEV_SEEDS[0]);r=o.begin()
        forged=deepcopy(r);forged["wave"]=999
        self.assertFalse(verified(forged))
        with self.assertRaises(ValueError):Knowledge().learn(forged)
        self.assertEqual(r["seal"],seal({k:v for k,v in r.items() if k!="seal"}))

    def test_cannot_use_unvisited_intel(self):
        owner=FortOwner(DEV_SEEDS[0]); memory=Knowledge()
        memory.learn(owner.begin())
        self.assertEqual(memory.gates,{})
        for move in public_route("B"):memory.learn(owner.walk(move))
        self.assertEqual(memory.gates,{})
        memory.learn(owner.read_relay())
        self.assertEqual(set(memory.gates),set(RELAY_COVERAGE["B"]))

    def test_native_actual_affordance_analysis_loads_and_selects(self):
        native=native003()
        self.assertTrue(callable(native.analyze_first_moves))
        self.assertIn(choose_motif(Knowledge(),MAX_ATTEMPTS),(None,"A","B","C","D"))
        self.assertIn(choose_classical(Knowledge(),True),(None,"A","B","C","D"))

    def test_classical_does_not_need_hidden_seed(self):
        for seed in DEV_SEEDS:
            o=FortOwner(seed)
            self.assertEqual(choose_classical(Knowledge(),True),
                             choose_classical(Knowledge(),True))
        self.assertGreater(expected_progress(set(range(1,WAVES+1))),
                           expected_progress(set()))

    def test_repeat_until_goal_or_budget_and_receipts(self):
        for policy in POLICIES:
            row=run_case(DEV_SEEDS[0],policy)
            self.assertLessEqual(row["attempts_used"],MAX_ATTEMPTS)
            self.assertEqual(row["attempts_used"],len(row["attempts"]))
            for attempt in row["attempts"]:
                self.assertTrue(attempt["receipts"])
                self.assertTrue(all(verified(r) for r in attempt["receipts"]))
                if attempt["completed"]:
                    self.assertEqual(attempt["waves_survived"],WAVES)
                else:
                    self.assertIsNotNone(attempt["first_breach_wave"])
            if policy=="classical_no_memory":
                self.assertIsNone(row["completed_at"])
            else:
                self.assertLessEqual(row["completed_at"],MAX_ATTEMPTS)

    def test_dev_reproduction(self):
        a=benchmark("development")
        b=benchmark("development")
        self.assertEqual(a["seal"],b["seal"])
        self.assertEqual(len(a["cases"]),len(DEV_SEEDS)*len(POLICIES))
        self.assertTrue(a["actual_native_motif003"])
        self.assertFalse(a["source_is_independently_authored"])

if __name__ == "__main__":
    unittest.main()
