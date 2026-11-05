"""Adversarial contracts for first-class classical lookup assimilation."""
import unittest

from desk import SCHEMA as DESK_SCHEMA, dispatch
from lookup import (
    Contract, LookupSkill, Reading, assimilate, independent_review,
    normalized, snapshot_id, vector
)
from source import FAMILIES, Source
from trial import benchmark, make_model, trial


class LookupAssimilationTests(unittest.TestCase):
    def test_source_contracts_differ_by_arity_and_never_reveal_laws(self):
        six = Source("any_three_paths").contract()
        seven = Source("seven_parity").contract()
        self.assertEqual(six.width, 6)
        self.assertEqual(seven.width, 7)
        self.assertNotEqual(six.id, seven.id)
        self.assertNotIn("parity", str(seven.packet()).lower())
        self.assertEqual(Contract.from_packet(six.packet()), six)
        self.assertEqual(Contract.from_packet(seven.packet()), seven)

    def test_full_table_is_a_real_reusable_first_class_skill(self):
        source = Source("exactly_one_path", 2)
        skill = assimilate(source.contract(), source.observations())
        self.assertIsInstance(skill, LookupSkill)
        self.assertTrue(skill.complete)
        self.assertEqual(skill.representation, "RAW_LOOKUP")
        self.assertEqual(len(skill.observations), 64)
        probe = (1, 1, 0, 0, 0, 0)
        row = skill.predict(probe, source.contract())
        self.assertEqual(row["status"], "SUPPORTED_SYNTHETIC_SNAPSHOT")
        self.assertEqual(row["value"], 1)
        self.assertEqual(LookupSkill.from_packet(skill.packet()), skill)

    def test_exact_compact_sensor_is_verified_against_every_lookup_cell(self):
        source = Source("any_three_paths", 3)
        skill = assimilate(source.contract(), source.observations())
        self.assertEqual(skill.representation, "COMPACT_EXACT")
        self.assertEqual(skill.program.clauses,
                         ((0, 1), (2, 3), (4, 5)))
        self.assertEqual(skill.corrections, ())
        for row in source.observations():
            self.assertEqual(skill.predict(row.vector, source.contract())["value"],
                             row.outcome)

    def test_sparse_exception_is_compiled_into_a_verified_patch(self):
        source = Source("sparse_exception_six", 3)
        skill = assimilate(source.contract(), source.observations())
        self.assertEqual(skill.representation, "COMPACT_WITH_EXCEPTIONS")
        self.assertGreater(len(skill.corrections), 0)
        self.assertLessEqual(len(skill.corrections), 3)
        for row in source.observations():
            self.assertEqual(skill.predict(row.vector, source.contract())["value"],
                             row.outcome)

    def test_uncompressible_parity_is_not_fabricated_as_new_instrument(self):
        source = Source("edge_parity", 2)
        model = assimilate(source.contract(), source.observations())
        self.assertEqual(model.representation, "RAW_LOOKUP")
        self.assertIsNone(model.program)
        self.assertEqual(model.packet()["status"], "PROPOSAL_ONLY")

    def test_new_seven_channel_contract_routes_to_exact_lookup(self):
        for family in ("seven_parity", "seven_last_channel", "seven_threshold"):
            with self.subTest(family=family):
                source = Source(family, 2)
                model = assimilate(source.contract(), source.observations())
                self.assertEqual(model.contract.width, 7)
                self.assertEqual(model.representation, "RAW_LOOKUP")
                self.assertTrue(independent_review(
                    model, source.contract(), source.observations("review")
                )["status"].startswith("ELIGIBLE"))
                self.assertEqual(trial(source)["test_incorrect"], 0)

    def test_unknown_configuration_never_extrapolates(self):
        source = Source("any_three_paths", 0)
        model = assimilate(source.contract(), source.observations(partial=True))
        self.assertFalse(model.complete)
        self.assertIsNone(model.program)
        self.assertEqual(model.predict((0, 0, 0, 0, 0, 1), source.contract())["status"],
                         "HOLD_UNOBSERVED_CONFIGURATION")
        self.assertEqual(independent_review(
            model, source.contract(), source.observations("review")
        )["status"], "HOLD_INCOMPLETE_SOURCE_SNAPSHOT")

    def test_changed_source_revision_forces_hold_even_with_same_channels(self):
        source = Source("any_three_paths", 2)
        model = assimilate(source.contract(), source.observations())
        replaced = Source("any_three_paths", 2, revision="source-rev-2")
        response = model.predict((1, 1, 0, 0, 0, 0), replaced.contract())
        self.assertEqual(response["status"], "HOLD_SOURCE_CONTRACT_CHANGED")
        self.assertEqual(independent_review(
            model, replaced.contract(), replaced.observations("review")
        )["status"], "HOLD_SOURCE_CONTRACT_CHANGED")

    def test_independent_shifted_worlds_are_falsified_without_patching(self):
        for family in ("phase_shift", "hidden_context", "seven_phase_shift"):
            with self.subTest(family=family):
                row = trial(Source(family, 2))
                self.assertEqual(row["independent_review"]["status"],
                                 "HOLD_INDEPENDENT_FALSIFIER")
                self.assertGreater(row["independent_review"]["contradictions"], 0)
                self.assertEqual(row["test_covered"], 0)
                self.assertIsNone(row["destination_review"])

    def test_strong_raw_lookup_baseline_has_same_review_and_coverage(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                source = Source(family, 4)
                hybrid = trial(source)
                raw = trial(source, "classical_full_lookup")
                self.assertEqual(hybrid["independent_review"],
                                 raw["independent_review"])
                self.assertEqual(hybrid["test_covered"], raw["test_covered"])
                self.assertEqual(hybrid["test_incorrect"], raw["test_incorrect"])

    def test_old_four_channel_baseline_misses_added_relations(self):
        source = Source("any_three_paths", 0)
        old = trial(source, "old_four_channel_only")
        hybrid = trial(source)
        self.assertEqual(old["independent_review"]["status"],
                         "HOLD_INADEQUATE_OLD_INTERFACE")
        self.assertEqual(old["test_covered"], 0)
        self.assertEqual(hybrid["test_covered"], 64)

    def test_duplicate_contradictory_and_foreign_evidence_refused(self):
        source = Source("any_three_paths")
        original = source.observations()[0]
        with self.assertRaises(ValueError):
            assimilate(source.contract(), (
                original, Reading(original.vector, 1 - original.outcome,
                                  original.contract_id)
            ))
        with self.assertRaises(ValueError):
            Reading(original.vector, True, original.contract_id)
        with self.assertRaises(ValueError):
            Reading(original.vector, original.outcome,
                    "0"*64, provenance="REAL_SENSOR")
        with self.assertRaises(ValueError):
            assimilate(Source("seven_parity").contract(),
                       source.observations())

    def test_cartridge_rejects_tampering_and_privileged_fields(self):
        model = assimilate(Source("sparse_exception_six").contract(),
                           Source("sparse_exception_six").observations())
        packet = model.packet()
        self.assertEqual(LookupSkill.from_packet(packet), model)
        mutations = [
            {"status": "APPROVED"},
            {"authority": "RUN_ANYTHING"},
            {"real_world_authority": True},
            {"callback": "https://untrusted.invalid"},
            {"source_digest": "0"*64},
            {"complete_domain": False},
            {"representation": "RAW_LOOKUP"},
            {"id": "lookup-" + "f"*24},
            {"program": {"operator": "EXEC", "clauses": [[0]],
                         "atoms": "READ_ONE_SYNTHETIC_LINK", "read_only": True}},
            {"corrections": [[list((0, 0, 0, 0, 0, 0)), True]]},
        ]
        for altered in mutations:
            with self.subTest(altered=altered), self.assertRaises(ValueError):
                LookupSkill.from_packet({**packet, **altered})

    def test_replayed_review_cells_are_not_independent_coverage(self):
        source = Source("any_three_paths")
        model = assimilate(source.contract(), source.observations())
        row = source.observations("review")[0]
        self.assertEqual(independent_review(
            model, source.contract(), (row,) * 64
        )["status"], "HOLD_INDEPENDENT_REVIEW_COVERAGE")

    def test_raw_lookup_and_derived_representation_disagree_never(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                source = Source(family, 1)
                model = assimilate(source.contract(), source.observations())
                for observation in source.observations():
                    self.assertEqual(
                        model.predict(observation.vector, source.contract())["value"],
                        observation.outcome
                    )

    def test_source_contract_parser_rejects_unauthorized_extensions(self):
        original = Source("any_three_paths").contract().packet()
        for change in ({"url": "https://untrusted.invalid"},
                       {"real_world_authority": True},
                       {"allowed_operation": "REMOTE_WRITE"},
                       {"channels": ["duplicate", "duplicate"]}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                Contract.from_packet({**original, **change})
        with self.assertRaises(ValueError):
            Contract("synthetic", "r1", tuple(f"ch{i}" for i in range(9)))

    def test_json_desk_is_callable_and_can_refuse_privileged_data(self):
        source = Source("any_three_paths", 2)
        contract = source.contract()
        observations = [
            {"inputs": list(r.vector), "outcome": r.outcome,
             "contract_id": r.contract_id, "provenance": r.provenance}
            for r in source.observations()
        ]
        accepted = dispatch({"schema": DESK_SCHEMA, "action": "assimilate",
                             "contract": contract.packet(),
                             "observations": observations})
        self.assertEqual(accepted["status"], "PROPOSE_ONLY")
        result = dispatch({"schema": DESK_SCHEMA, "action": "predict",
                           "cartridge": accepted["cartridge"],
                           "contract": contract.packet(),
                           "controls": [1, 1, 0, 0, 0, 0]})
        self.assertEqual(result["status"], "SUPPORTED_SYNTHETIC_SNAPSHOT")
        self.assertEqual(result["value"], 1)
        refused = dispatch({"schema": DESK_SCHEMA, "action": "predict",
                            "cartridge": accepted["cartridge"],
                            "contract": contract.packet(),
                            "controls": [1, 1, 0, 0, 0, 0],
                            "external_endpoint": "https://evil.invalid"})
        self.assertEqual(refused["status"], "REFUSE")

    def test_partial_contract_status_is_never_routed_to_test(self):
        model = trial(Source("seven_parity", 2), "partial_unobserved")
        self.assertEqual(model["model_status"], "RAW_LOOKUP")
        self.assertFalse(model["complete_source_snapshot"])
        self.assertEqual(model["independent_review"]["status"],
                         "HOLD_INCOMPLETE_SOURCE_SNAPSHOT")
        self.assertEqual(model["test_covered"], 0)

    def test_benchmark_preserves_classical_tie_and_nonpromotion(self):
        report = benchmark()
        final = report["evaluation"]
        self.assertEqual(final["assimilated_hybrid"]["worlds"], 65)
        self.assertEqual(final["assimilated_hybrid"]["review_eligible"], 50)
        self.assertEqual(final["assimilated_hybrid"]["held"], 15)
        self.assertEqual(final["assimilated_hybrid"]["test_incorrect"], 0)
        self.assertEqual(final["assimilated_hybrid"]["review_eligible"],
                         final["classical_full_lookup"]["review_eligible"])
        self.assertEqual(final["assimilated_hybrid"]["test_covered"],
                         final["classical_full_lookup"]["test_covered"])
        self.assertEqual(final["old_four_channel_only"]["review_eligible"], 5)
        self.assertGreater(final["assimilated_hybrid"]["compact_exact"], 0)
        self.assertGreater(final["assimilated_hybrid"]["compact_with_exceptions"], 0)
        self.assertGreater(final["assimilated_hybrid"]["raw_lookup_used"], 0)
        self.assertEqual(final["partial_unobserved"]["review_eligible"], 0)
        self.assertEqual(report["frozen_method_decision"], "NO_METHOD_PROMOTION")
        self.assertFalse(report["real_world_authority"])
        self.assertEqual(report["external_operations"], 0)


if __name__ == "__main__":
    unittest.main()
