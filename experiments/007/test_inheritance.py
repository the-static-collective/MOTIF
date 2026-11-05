"""MOTIF-007: tests for independent-world method inheritance without authority."""
import unittest
import json
from dataclasses import replace
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "002"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "006"))
from motif002 import F, induce, lessons, scene, Verb
from composition import two_level_training, Call, signature
from inheritance import (SCHEMA, HOLD, Receiver, export_method,
                         verify_packet, receiver_scene, extended_receiver_scene,
                         digest, demonstrate, RESERVED_EFFECTS)


class FederatedInheritanceTests(unittest.TestCase):
    def setUp(self):
        self.primitives = induce(lessons())
        _, self.inner, self.outer = two_level_training(self.primitives)
        self.catalog = dict(self.primitives)
        self.catalog[self.inner.id] = self.inner
        self.catalog[self.outer.id] = self.outer
        self.world, self.roles = extended_receiver_scene()
        self.artifact = export_method(self.outer.id, self.catalog)
        self.package = verify_packet(self.artifact)
        self.receiver = Receiver("LOCAL_B")

    def accept(self):
        ticket = self.receiver.offer(self.artifact)
        preview = self.receiver.preview(ticket, self.world, self.roles)
        decision = self.receiver.review(ticket, "ADMIT_PLAN_ONLY",
                                        "SYNTHETIC_LOCAL_B", preview.preview_digest)
        return ticket, preview, decision

    def repack(self, data):
        body = {k: v for k, v in data.items() if k != "checksum_sha256"}
        data["checksum_sha256"] = digest(body)
        return json.dumps(data, sort_keys=True)

    def test_export_is_only_abstract_source_closure(self):
        self.assertEqual(self.package.root, self.outer.id)
        self.assertEqual(len(self.package.catalog), 4)
        self.assertFalse(any(name in self.artifact for name in
                             ("Jo", "Mira", "bike1", "bike2")))
        self.assertEqual(self.package.origin_claim, "UNVERIFIED_FIXTURE_A")

    def test_no_origin_signature_in_schema(self):
        doc = json.loads(self.artifact)
        self.assertEqual(doc["schema"], SCHEMA)
        self.assertEqual(set(doc), {"schema", "origin_claim", "root",
                                    "operators", "checksum_sha256"})
        self.assertNotIn("signature", doc)
        self.assertNotIn("world", doc)
        self.assertNotIn("observations", doc)

    def test_donor_and_recipient_are_separately_scoped(self):
        local_before = self.world
        self.accept()
        after = self.receiver.simulate_admitted(self.package.checksum,
                                                self.world, self.roles)
        self.assertNotEqual(after, self.world)
        self.assertEqual(self.world, local_before)
        self.assertIn(F("usable", "wheelA"), after)
        self.assertNotIn(F("usable", "wheelA"), local_before)

    def test_default_hold_blocks_execution_simulation(self):
        self.receiver.offer(self.artifact)
        with self.assertRaisesRegex(HOLD, "Not locally admitted"):
            self.receiver.simulate_admitted(self.package.checksum,
                                            self.world, self.roles)

    def test_preview_does_not_admit_method(self):
        ticket = self.receiver.offer(self.artifact)
        preview = self.receiver.preview(ticket, self.world, self.roles)
        self.assertEqual(preview.status, "SIMULATED_NOT_ADMITTED")
        self.assertNotIn(ticket, self.receiver.admitted)
        self.assertEqual(len(self.receiver.decisions), 0)

    def test_admission_requires_exact_local_preview(self):
        ticket = self.receiver.offer(self.artifact)
        with self.assertRaises(HOLD):
            self.receiver.review(ticket, "ADMIT_PLAN_ONLY", "LOCAL_REVIEWER",
                                 preview_digest="forged")
        self.assertFalse(self.receiver.admitted)
        preview = self.receiver.preview(ticket, self.world, self.roles)
        result = self.receiver.review(ticket, "ADMIT_PLAN_ONLY",
                                      "LOCAL_REVIEWER", preview.preview_digest)
        self.assertEqual(result.decision, "ADMIT_PLAN_ONLY")
        self.assertIn(ticket, self.receiver.admitted)

    def test_refusal_never_autoadmits(self):
        ticket = self.receiver.offer(self.artifact)
        result = self.receiver.review(ticket, "REFUSE", "LOCAL_REVIEWER")
        self.assertEqual(result.decision, "REFUSE")
        self.assertEqual(self.receiver.decisions[-1], result)
        with self.assertRaises(HOLD):
            self.receiver.simulate_admitted(ticket, self.world, self.roles)

    def test_revocation_blocks_future_use(self):
        ticket, _, _ = self.accept()
        record = self.receiver.revoke(ticket, "LOCAL_REVIEWER")
        self.assertEqual(record.decision, "REVOKE_PLAN_ONLY")
        with self.assertRaises(HOLD):
            self.receiver.simulate_admitted(ticket, self.world, self.roles)

    def test_missing_permission_stops_local_preview(self):
        ticket = self.receiver.offer(self.artifact)
        without = frozenset(f for f in self.world if f[0] != "permits")
        with self.assertRaises(HOLD):
            self.receiver.preview(ticket, without, self.roles)
        self.assertNotIn(ticket, self.receiver.admitted)

    def test_local_missing_tool_stops_preview(self):
        ticket = self.receiver.offer(self.artifact)
        without = self.world - {F("tool", "Omar", "wrench")}
        with self.assertRaises(HOLD):
            self.receiver.preview(ticket, without, self.roles)

    def test_modified_bytes_fail_checksum(self):
        wrong = self.artifact.replace("UNVERIFIED_FIXTURE_A", "IMPERSONATOR_FIXTURE")
        with self.assertRaisesRegex(HOLD, "checksum"):
            verify_packet(wrong)

    def test_rehashed_impersonation_remains_unverified(self):
        # Core scientific limit: a plain checksum is not author authentication.
        document = json.loads(self.artifact)
        document["origin_claim"] = "IMPERSONATOR"
        rehashed = verify_packet(self.repack(document))
        self.assertEqual(rehashed.origin_claim, "IMPERSONATOR")
        self.assertNotEqual(rehashed.checksum, self.package.checksum)

    def test_unknown_payload_keys_rejected_even_if_rehashed(self):
        document = json.loads(self.artifact)
        document["private_world"] = [["owns", "Jo", "secret"]]
        with self.assertRaisesRegex(HOLD, "unexpected fields"):
            verify_packet(self.repack(document))

    def test_rewritten_permission_effect_rejected_even_if_rehashed(self):
        document = json.loads(self.artifact)
        primitive = next(x for x in document["operators"] if x["kind"]=="primitive")
        primitive["adds"] = [["permits", "?0", "?1", "ANYTHING"]]
        with self.assertRaisesRegex(HOLD, "permission relation"):
            verify_packet(self.repack(document))

    def test_semantic_drift_rejected_even_if_bundle_rehashed(self):
        document = json.loads(self.artifact)
        target = next(x for x in document["operators"] if x["kind"]=="primitive")
        target["adds"].append(["new_result", "?0"])
        with self.assertRaisesRegex(HOLD, "fingerprint"):
            verify_packet(self.repack(document))

    def test_dependency_missing_from_rehashed_bundle_rejected(self):
        document = json.loads(self.artifact)
        document["operators"] = [x for x in document["operators"]
                                  if x["id"] != self.inner.id]
        with self.assertRaises(HOLD):
            verify_packet(self.repack(document))

    def test_conflicting_operator_cannot_overwrite_receiver(self):
        source = next(v for v in self.primitives.values()
                      if F("usable", "?0") in v.adds)
        self.receiver.local_catalog[source.id] = replace(
            source, adds=frozenset({F("wrong", "?0")}))
        with self.assertRaisesRegex(HOLD, "overwrite"):
            self.receiver.offer(self.artifact)

    def test_post_admission_local_source_drift_is_held(self):
        ticket, _, _ = self.accept()
        repair = next(v for v in self.primitives.values()
                      if F("usable", "?0") in v.adds)
        self.receiver.local_catalog[repair.id] = replace(
            repair, adds=frozenset({F("fabricated", "?0")}))
        with self.assertRaisesRegex(HOLD, "drifted"):
            self.receiver.simulate_admitted(ticket, self.world, self.roles)

    def test_reviewed_macro_body_cannot_be_replaced_after_admission(self):
        ticket, _, _ = self.accept()
        self.receiver.local_catalog[self.outer.id] = replace(
            self.outer, adds=self.outer.adds | {F("fabricated", "?2")})
        with self.assertRaisesRegex(HOLD, "drifted"):
            self.receiver.simulate_admitted(ticket, self.world, self.roles)

    def test_wrong_local_roles_do_not_grant_ability(self):
        ticket = self.receiver.offer(self.artifact)
        with self.assertRaises(HOLD):
            self.receiver.preview(ticket, self.world,
                                  ("wheelA", "Omar", "Nina", "wheelB"))

    def test_local_trace_is_not_exported_during_simulation(self):
        ticket, preview, _ = self.accept()
        self.assertNotIn("wheelC", self.artifact)
        self.assertNotIn("Nina", self.artifact)
        self.assertNotIn("Omar", self.artifact)
        self.assertNotEqual(preview.local_world_sha256,
                            preview.predicted_world_sha256)
        self.assertEqual(self.package.checksum, ticket)

    def test_two_way_independent_inheritance(self):
        report = demonstrate()
        self.assertFalse(report["donor_world_exported"])
        self.assertFalse(report["packet_contains_entity_names"])
        self.assertTrue(report["receiver_held_by_default"])
        self.assertTrue(report["recipient_after_matches_local_replay"])
        self.assertTrue(report["reverse_transfer_independently_admitted"])
        self.assertTrue(report["return_matches_four_primitives"])
        self.assertEqual(report["recipient_improved_macro_depth"], 4)
        self.assertEqual(report["returned_bundle_dependency_count"], 5)
        self.assertFalse(report["receiver_claim_is_authenticated"])
        self.assertFalse(report["remote_action_performed"])


if __name__ == "__main__":
    unittest.main()
