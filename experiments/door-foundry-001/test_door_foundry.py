"""DOOR-FOUNDRY-001 integration, adversarial and control tests."""
import json
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import door_foundry as door


class DoorFoundryTests(unittest.TestCase):
    def test_source_owner_modules_really_exist_and_are_pinned(self):
        door.verify_sources()
        self.assertEqual(len(door.SOURCE_LOCK), 3)
        self.assertTrue(all(len(v) == 40 for v in door.SOURCE_LOCK.values()))

    def test_actual_cross_organ_composition(self):
        result = door.run()
        self.assertEqual(result["stage"], "PROPOSED")
        self.assertEqual(result["schema"], "motif.door.v0")
        self.assertEqual(len(result["composition"]), 5)
        self.assertEqual({r["source"] for r in result["composition"] if r["source"]},
                         set(door.SOURCE_LOCK))
        self.assertTrue(result["fixed_classical_baseline"]["original_002_goal_reached"])
        self.assertGreaterEqual(result["replayed_macro"]["expanded_primitive_steps"], 3)
        self.assertGreaterEqual(result["replayed_macro"]["synthetic_trace_demonstrations"], 2)
        self.assertFalse(result["real_world_authority"])
        self.assertFalse(result["external_action_executed"])
        self.assertIsNone(result["observed_outcome"])

    def test_goal_reached_only_in_hypothetical_replay(self):
        result = door.run()
        self.assertEqual(len(result["goal_facts"]), 3)
        self.assertEqual(len(result["predicted_new_facts"]), 3)
        self.assertEqual(result["predicted_new_facts"], result["goal_facts"])
        self.assertIn("Hypothetical replay is not an observed outcome.",
                      result["limitations"])

    def test_planner_is_derived_from_signatures_not_hardcoded_order(self):
        caps = door.registry()
        a = door.compose(caps, {"world", "goal"})
        b = door.compose(tuple(reversed(caps)), {"world", "goal"})
        self.assertEqual(a, b)
        self.assertEqual(len(a), 5)
        self.assertEqual(a[-1], "motif.door.assemble")
        self.assertEqual(len(set(a)), 5)

    def test_missing_compiler_holds(self):
        caps = tuple(c for c in door.registry()
                     if c.handler != "compile_original_006")
        with self.assertRaisesRegex(door.HOLD, "No eligible"):
            door.compose(caps, {"world", "goal"})

    def test_missing_affordance_organ_holds(self):
        caps = tuple(c for c in door.registry()
                     if c.handler != "frontier_original_003")
        with self.assertRaises(door.HOLD):
            door.compose(caps, {"world", "goal"})

    def test_experimental_candidates_are_eligible_if_contract_present(self):
        caps = door.registry()
        self.assertEqual(next(x for x in caps
                              if x.handler == "assemble_local_door").state,
                         "EXPERIMENTAL_VERIFIED")
        self.assertIn("motif.door.assemble", door.compose(caps, {"world", "goal"}))

    def test_unavailable_blocks_regardless_of_branch_status(self):
        caps = tuple(replace(c, state="UNAVAILABLE") if
                     c.handler == "assemble_local_door" else c
                     for c in door.registry())
        with self.assertRaises(door.HOLD):
            door.compose(caps, {"world", "goal"})

    def test_budget_failure_is_a_hold_not_a_truncated_success(self):
        with self.assertRaisesRegex(door.HOLD, "No eligible"):
            door.compose(door.registry(), {"world", "goal"}, max_steps=4)
        with self.assertRaisesRegex(door.HOLD, "depth"):
            door.compose(door.registry(), {"world", "goal"}, max_steps=100)

    def test_simulated_permissions_missing_holds(self):
        two, _, _ = door.original_modules()
        with self.assertRaises(door.HOLD):
            door.run(world=two.scene(permissions=False))

    def test_synthetic_domain_renaming_survives(self):
        two, _, six = door.original_modules()
        renamed = six.rename_world(two.scene(), {
            "Jo": "NewOwner", "Mira": "NewHelper",
            "bike1": "NewCycleA", "bike2": "NewCycleB"})
        target = frozenset({
            two.F("skill", "NewOwner", "repair"),
            two.F("usable", "NewCycleA"),
            two.F("usable", "NewCycleB")})
        result = door.run(world=renamed, goal=target)
        self.assertEqual(result["stage"], "PROPOSED")
        self.assertEqual(set(map(tuple, result["goal_facts"])), target)

    def test_actual_source_mismatch_holds_before_import(self):
        with patch.object(door, "git_blob", return_value="0" * 40):
            with self.assertRaisesRegex(door.HOLD, "Pinned source"):
                door.run()

    def test_malicious_registry_handler_refused(self):
        source = json.loads((door.HERE / "registry.json").read_text())
        source[0]["handler"] = "__import__('os').system"
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "evil.json"
            p.write_text(json.dumps(source))
            with self.assertRaisesRegex(door.HOLD, "Unknown capability handler"):
                door.registry(p)

    def test_false_output_claim_refused(self):
        source = json.loads((door.HERE / "registry.json").read_text())
        source[0]["provides"] = "external_mail_sent"
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "false.json"
            p.write_text(json.dumps(source))
            with self.assertRaisesRegex(door.HOLD, "signature"):
                door.registry(p)

    def test_fake_external_authority_refused(self):
        source = json.loads((door.HERE / "registry.json").read_text())
        source[0]["scope"] = "UNRESTRICTED"
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "authority.json"
            p.write_text(json.dumps(source))
            with self.assertRaisesRegex(door.HOLD, "signature"):
                door.registry(p)

    def test_duplicate_handler_refused(self):
        source = json.loads((door.HERE / "registry.json").read_text())
        source.append(dict(source[0], id="duplicate"))
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "dup.json"
            p.write_text(json.dumps(source))
            with self.assertRaisesRegex(door.HOLD, "Duplicate capability handler"):
                door.registry(p)

    def test_deterministic_receipt_and_explicit_no_improvement_claim(self):
        first, second = door.run(), door.run()
        self.assertEqual(first["content_sha256"], second["content_sha256"])
        self.assertIn("No claimed advantage",
                      first["fixed_classical_baseline"]["note"])
        self.assertEqual(len(first["content_sha256"]), 64)

    def test_bad_goal_not_silently_accepted(self):
        two, _, _ = door.original_modules()
        with self.assertRaises(door.HOLD):
            door.run(goal=frozenset({two.F("magic", "impossible")}))

    def test_already_satisfied_goal_not_new_door(self):
        two, _, _ = door.original_modules()
        with self.assertRaises(door.HOLD):
            door.run(goal=frozenset({two.F("person", "Jo")}))

    def test_never_treat_absent_facts_as_implicit_permissions(self):
        two, _, _ = door.original_modules()
        world = two.scene() - {two.F("permits", "Jo", "Jo", "bike2")}
        with self.assertRaises(door.HOLD):
            door.run(world=world)


if __name__ == "__main__":
    unittest.main()
