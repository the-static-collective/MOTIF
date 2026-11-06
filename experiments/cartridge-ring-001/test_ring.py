"""RING-001 adversarial, reuse, budget and actual source-invocation tests."""
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import ring


class CartridgeRingTests(unittest.TestCase):
    def test_all_149_non_main_refs_are_visible_but_not_runnable(self):
        census = ring.inventory()
        self.assertEqual(len(census), 149)
        self.assertTrue(all(x["status"] == "DISCOVERED_ONLY" for x in census))
        self.assertEqual(len({x["ref"] for x in census}), 149)
        self.assertIn("experiment/geometry-013-self-redesigning-instrument",
                      {x["ref"] for x in census})
        self.assertIn("experiment/thought-014-native-language-selfdev",
                      {x["ref"] for x in census})

    def test_zero_cartridge_is_valid_and_has_no_side_effect(self):
        receipt = ring.run(())
        self.assertEqual(receipt["stage"], "IDLE")
        self.assertEqual(receipt["selected_cartridges"], [])
        self.assertEqual(receipt["waves"], [])
        self.assertEqual(receipt["artifacts"], {})
        self.assertFalse(receipt["external_action_executed"])

    def test_one_cartridge_only_when_one_is_needed(self):
        receipt = ring.run(("verbs",))
        self.assertEqual(receipt["stage"], "PROPOSED")
        self.assertEqual(len(receipt["selected_cartridges"]), 1)
        self.assertEqual(receipt["selected_cartridges"][0]["provides"], "verbs")
        self.assertGreater(receipt["artifacts"]["verbs"]["operator_count"], 0)

    def test_complementary_cartridges_share_actual_parallel_wave(self):
        r = ring.run(("frontier", "macro_replay"))
        self.assertEqual(len(r["selected_cartridges"]), 4)
        self.assertIn("frontier", r["artifacts"])
        self.assertIn("macro_replay", r["artifacts"])
        self.assertTrue(any(len(w) == 2 for w in r["waves"]))
        self.assertEqual(r["artifacts"]["macro_replay"]["expanded_primitive_steps"], 3)
        self.assertFalse(r["real_world_authority"])

    def test_full_door_reuses_actual_source_owned_organs(self):
        r = ring.run(("door",))
        self.assertEqual(len(r["selected_cartridges"]), 5)
        self.assertEqual(r["artifacts"]["door"]["stage"], "PROPOSED")
        self.assertEqual(
            {x["source"] for x in r["selected_cartridges"] if x["source"]},
            set(ring.door.SOURCE_LOCK))
        self.assertEqual(r["artifacts"]["door"]["schema"], "motif.door.v0")
        self.assertFalse(r["artifacts"]["door"]["external_action_executed"])

    def test_parallel_serial_reproduce_identical_receipt(self):
        par = ring.run(("frontier", "macro_replay"), parallel=True)
        seq = ring.run(("frontier", "macro_replay"), parallel=False)
        self.assertEqual(par, seq)

    def test_requesting_a_branch_name_is_not_execution(self):
        with self.assertRaisesRegex(ring.HOLD, "Unknown or uninstalled"):
            ring.run(("experiment/reason-cartridge-021-other-teaches-self",))

    def test_census_cannot_promote_a_branch(self):
        obj = json.loads((ring.HERE / "branch_inventory.json").read_text())
        obj["branches"][0]["status"] = "ADMIT_AND_EXECUTE"
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "bad.json"
            p.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ring.HOLD, "promoted"):
                ring.inventory(p)

    def test_changed_source_holds_before_invocation(self):
        with patch.object(ring.door, "git_blob", return_value="0" * 40):
            with self.assertRaisesRegex(ring.HOLD, "Pinned source"):
                ring.run(("verbs",))

    def test_missing_needed_installed_method_holds(self):
        caps = tuple(c for c in ring.door.registry()
                     if c.handler != "compile_original_006")
        with self.assertRaisesRegex(ring.HOLD, "No admitted"):
            ring.choose(("macro_replay",), caps)

    def test_budget_limits_are_real_and_explicit(self):
        with self.assertRaisesRegex(ring.HOLD, "No admitted"):
            ring.run(("door",), max_cost=5)
        with self.assertRaisesRegex(ring.HOLD, "Invalid cartridge budget"):
            ring.run(("door",), max_cost=101)
        with self.assertRaisesRegex(ring.HOLD, "No admitted"):
            ring.choose(("door",), ring.door.registry(), max_steps=4)

    def test_no_implicit_consent_from_graph(self):
        two, _, _ = ring.door.original_modules()
        no_permission = two.scene(permissions=False)
        with self.assertRaises(ring.HOLD):
            ring.run(("door",), world=no_permission)

    def test_branch_catalog_never_invents_outputs(self):
        r = ring.run(("frontier",))
        self.assertNotIn("external_mail_sent", r["artifacts"])
        self.assertEqual(len(r["selected_cartridges"]), 2)
        self.assertTrue(all(c["state"] in ("MAIN_VERIFIED",
                                           "EXPERIMENTAL_VERIFIED")
                            for c in r["selected_cartridges"]))

    def test_declared_cost_is_not_measured_energy(self):
        single = ring.run(("verbs",))
        two = ring.run(("frontier", "macro_replay"))
        all_ = ring.run(("door",))
        self.assertLess(single["declared_total_cost_units"],
                        two["declared_total_cost_units"])
        self.assertLess(two["declared_total_cost_units"],
                        all_["declared_total_cost_units"])


if __name__ == "__main__":
    unittest.main()
