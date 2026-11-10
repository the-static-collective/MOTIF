"""CONFLUENCE-001 scope, provenance, branch, time and real-method regression."""
import copy
import unittest

from adapter003 import assess, original_motif003
from confluence import Confluence, SyntheticOwner, WORLDS, Ledger, digest


class ConfluenceTests(unittest.TestCase):
    def test_source_owned_hinge_and_early_stop(self):
        owner = SyntheticOwner(2, False)
        run = Confluence(owner)
        report = run.run()
        self.assertEqual(report["status"], "PLAN_SIMULATED")
        self.assertEqual(report["plan"], "PANEL_AND_CHAIR")
        self.assertEqual(report["ink_count"], 2)  # permission + panel only
        self.assertEqual(report["pencil_count"], 1)
        self.assertEqual(len(report["remaining_conditional_worlds"]), 2)
        self.assertEqual(owner._issued[-1]["sensor"], "measure_panel")
        self.assertTrue(run.ledger.valid(owner))
        self.assertEqual(report["proof_chain"][-1]["kind"], "PLAN_PREVIEW")
        first = next(e for e in run.ledger.events if e["kind"] == "PENCIL_PROPOSAL")
        self.assertEqual(first["payload"]["status"], "PENCIL")
        self.assertEqual(len(first["payload"]["alternatives"]), 4)

    def test_second_hinge_and_mesh_plan(self):
        owner = SyntheticOwner(1, True)
        run = Confluence(owner)
        report = run.run()
        self.assertEqual(report["plan"], "MESH_AND_CHAIR")
        self.assertEqual(report["ink_count"], 3)
        self.assertEqual(report["pencil_count"], 2)
        self.assertEqual([x["sensor"] for x in owner._issued],
                         ["permission", "measure_panel", "inspect_mesh"])
        self.assertEqual(len(report["remaining_conditional_worlds"]), 1)

    def test_genuine_unknown_not_a_plan(self):
        report = Confluence(SyntheticOwner(1, False)).run()
        self.assertEqual(report["status"], "HOLD")
        self.assertIsNone(report["plan"])
        self.assertEqual(report["steps"], [])

    def test_budget_zero_preserves_unknown(self):
        owner = SyntheticOwner(2, True)
        report = Confluence(owner).run(0)
        self.assertEqual(report["status"], "HOLD")
        self.assertEqual(report["pencil_count"], 0)
        self.assertEqual(report["ink_count"], 1)
        self.assertEqual(len(report["remaining_conditional_worlds"]), 4)

    def test_permission_denied_cannot_preview(self):
        owner = SyntheticOwner(2, True, permission=False)
        report = Confluence(owner).run(2)
        self.assertEqual(report["status"], "HOLD")
        self.assertEqual(len(owner._issued), 1)
        self.assertEqual(report["reason"], "PERMISSION_UNVERIFIED_OR_DENIED")
        self.assertFalse(any(e["kind"] == "PLAN_PREVIEW" for e in report["proof_chain"]))

    def test_past_observation_not_erased_on_revision(self):
        owner = SyntheticOwner(2, False)
        run = Confluence(owner)
        before = run.run()
        self.assertEqual(before["plan"], "PANEL_AND_CHAIR")
        old_receipt = copy.deepcopy(owner._issued[1])
        owner.change(panel_span=1, mesh_safe=True)
        owner.advance(4)
        after = run.run()
        self.assertEqual(after["plan"], "MESH_AND_CHAIR")
        self.assertEqual(after["ink_count"], 5)  # old permission+span, new permission+span+mesh
        self.assertTrue(owner.verify(old_receipt))  # history remains historical INK
        self.assertTrue(run.ledger.valid(owner))
        self.assertEqual(run.candidates(), (WORLDS[1],))
        self.assertNotEqual(before["proof_chain_tip"], after["proof_chain_tip"])

    def test_revoked_permission_not_inherited(self):
        owner = SyntheticOwner(2, True)
        run = Confluence(owner)
        self.assertEqual(run.run()["status"], "PLAN_SIMULATED")
        owner.change(permission=False)
        owner.advance(2)
        second = run.run()
        self.assertEqual(second["status"], "HOLD")
        self.assertEqual(second["reason"], "PERMISSION_UNVERIFIED_OR_DENIED")
        self.assertEqual(owner._issued[-1]["sensor"], "permission")

    def test_owner_checks_membership_not_only_hash(self):
        owner = SyntheticOwner()
        receipt = owner.read("measure_panel")
        forged = {**receipt, "value": 1}
        forged["sha256"] = digest({k: v for k, v in forged.items() if k != "sha256"})
        self.assertFalse(owner.verify(forged))
        self.assertTrue(owner.verify(receipt))

    def test_cannot_launder_pencil_as_ink(self):
        owner = SyntheticOwner()
        run = Confluence(owner)
        run.run()
        event = run.ledger.events[1]
        event["kind"] = "INK_OBSERVATION"
        self.assertFalse(run.ledger.valid(owner))

    def test_rehashed_receipt_cannot_pass_source_gate(self):
        owner = SyntheticOwner()
        run = Confluence(owner)
        run.run()
        target = run.ledger.events[2]["payload"]
        target["value"] = 1  # in-place tampering of source observation
        target["sha256"] = digest({k: v for k, v in target.items() if k != "sha256"})
        self.assertFalse(run.ledger.valid(owner))

    def test_stale_report_reopens_worlds_without_declaring_change(self):
        owner = SyntheticOwner(2, True)
        run = Confluence(owner)
        run.run()
        owner.advance(5)
        self.assertEqual(len(run.candidates()), 4)
        self.assertIsNone(run._fresh("permission"))
        self.assertEqual(run.report("HOLD", None, "RECHECK")["review_due_keys"],
                         ["permission", "panel_span", "mesh_safe"])

    def test_original_motif003_executed(self):
        original, pin = original_motif003()
        self.assertTrue(callable(original.analyze_first_moves))
        self.assertEqual(len(pin), 64)
        panel = assess("PANEL_AND_CHAIR", (WORLDS[2],))
        self.assertTrue(panel["goal_reached"])
        self.assertEqual(panel["first_suggested"], "brace_panel")
        self.assertEqual(set(panel["exact_classical_route"]),
                         {"brace_panel", "place_panel", "place_chair"})
        mesh = assess("MESH_AND_CHAIR", (WORLDS[1],))
        self.assertEqual(mesh["first_suggested"], "prepare_mesh")
        with self.assertRaises(ValueError):
            assess("MESH_AND_CHAIR", (WORLDS[0],))

    def test_invalid_sensor_and_clock(self):
        owner = SyntheticOwner()
        with self.assertRaises(ValueError):
            owner.read("arbitrary_external_api")
        with self.assertRaises(ValueError):
            owner.advance(-1)
        with self.assertRaises(ValueError):
            owner.change(panel_span=99)
        with self.assertRaises(ValueError):
            Confluence(owner).run(-1)

    def test_lack_of_independent_origins_is_explicit(self):
        owner = SyntheticOwner(1, True)
        result = Confluence(owner).run()
        self.assertEqual(result["source_origins"], ["ONE_SYNTHETIC_OWNER"])
        self.assertTrue(all(
            e["payload"]["source_origin_count"] == 1
            for e in result["proof_chain"] if e["kind"] == "PENCIL_PROPOSAL"
        ))
        self.assertIn("no construction, physical measurement, or external action",
                      result["limitations"])


if __name__ == "__main__":
    unittest.main()
