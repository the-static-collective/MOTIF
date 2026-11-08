"""RING-012: ambiguity as a native output, not forced error or forced certainty.

These tests check source/authority boundaries and an actual 120-case source-
matched ambiguity benchmark. Every test label is authored; none corresponds
to ground truth about private persons or the connected manuscript.
"""
from __future__ import annotations
import ast
from copy import deepcopy
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import unittest

import lattice,calibration,world

# The stacked RING-011 module is also named benchmark.py and imported by
# lattice; explicitly load this experiment's benchmark under its own name.
SCRIPT=Path(__file__).resolve().parent/"benchmark.py"
spec=spec_from_file_location("ring012_ambiguity_trial",SCRIPT)
trial=module_from_spec(spec)
spec.loader.exec_module(trial)


class AmbiguityNativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy=calibration.calibrate()
        cls.source=trial.frozen_verified(cls.policy)
        cls.public=world.generate(
            "OPEN_READING_CRYPTOGRAMMAR",seed=2026111212,rounds=4)

    def test_frozen_selection_uses_prior_dev_only_not_new_test_semantics(self):
        self.assertEqual(self.policy["schema"],calibration.SCHEMA)
        self.assertEqual(self.policy["calibration_candidates_executed"],32)
        self.assertFalse(self.policy["test_meanings_consulted_to_select_policy"])
        self.assertFalse(self.policy["novel_world_module_imported_during_selection"])
        self.assertTrue(self.policy["open_world_always"])
        for name in ("calibration.py","lattice.py"):
            imported=[]
            source=(Path(__file__).resolve().parent/name).read_text()
            for node in ast.walk(ast.parse(source)):
                if isinstance(node,ast.Import):
                    imported += [item.name for item in node.names]
                if isinstance(node,ast.ImportFrom):
                    imported.append(node.module)
            self.assertNotIn("world",imported)

    def test_ambiguous_true_readings_are_explicitly_multiple_and_distinct(self):
        world.validate(self.public)
        ambiguous=[c for c in self.public["cases"]
                   if c["author_tag"]=="AMBIGUOUS"]
        self.assertEqual(len(ambiguous),24)
        for c in ambiguous:
            self.assertGreaterEqual(c["reading_count"],2)
            self.assertEqual(len({
                lattice.digest(v) for v in c["admissible_graphs"]
            }),c["reading_count"])

    def test_open_world_even_when_all_methods_agree_on_one_graph(self):
        # A single candidate is NEVER an authenticated assertion or permission.
        packet=world.generate(
            "KNOWN_SHAPES_NEW_SOURCE_EVENTS",seed=2026111211,rounds=1)
        result=[lattice.combine(c["text"],c["observed_event"],
                                c["carrier"],self.source,self.policy)
                for c in packet["cases"]]
        self.assertTrue(all(r["other_unmodeled_readings_remain_possible"] for r in result))
        self.assertTrue(all(r["root_action_authorized"] is False for r in result))
        self.assertTrue(all(r["authority"]=="NONE" for r in result))
        self.assertTrue(all(r["external_action_executed"] is False for r in result))

    def test_conflicting_methods_are_not_silently_forced_to_one(self):
        witnesses=[lattice.combine(c["text"],c["observed_event"],
                                   c["carrier"],self.source,self.policy)
                   for c in self.public["cases"]]
        contradictions=[x for x in witnesses if x.get("source_disagreements")]
        self.assertGreater(len(contradictions),0)
        self.assertTrue(any(x.get("supported_world_count",0)>1
                            for x in contradictions))
        self.assertTrue(all(x.get(
            "method_agreement_is_independent_corroboration") is False
                            for x in contradictions))

    def test_can_reason_about_invariants_without_forcing_one_reading(self):
        # The carrier and some semantic properties can be stable across
        # competing models; only source-CONDITIONAL conclusions are allowed.
        case=next(x for x in self.public["cases"] if x["author_tag"]=="AMBIGUOUS")
        result=lattice.combine(case["text"],case["observed_event"],
                               case["carrier"],self.source,self.policy)
        self.assertGreater(len(result["supported_worlds"]),1)
        self.assertTrue(result["invariants_are_not_authenticated_world_facts"])
        self.assertFalse(result["auto_interrupt_user_for_ambiguity"])
        self.assertFalse(result["root_action_authorized"])
        self.assertTrue(result["other_unmodeled_readings_remain_possible"])
        stable=result["conditional_invariants_within_modeled_worlds"]
        if "ROOT_FORCE" in stable:
            self.assertTrue(all(lattice.corpus.graph_map(g)[
                ("ROOT","FORCE")]==stable["ROOT_FORCE"]
                for g in result["supported_worlds"]))
        self.assertIn(result["optional_discriminator_question_kind"],
                      (None,"WHO_IF_ANY_REQUESTED_THIS_EVENT",
                       "WHICH_SCOPE_OWNS_THE_EVENT",
                       "IS_THIS_DIRECT_SPEECH_OR_REPORTED_SPEECH",
                       "DOES_NEGATION_APPLY_TO_THIS_EVENT"))

    def test_ungrounded_cryptic_text_is_unresolved_not_false_graph(self):
        unbound=[x for x in self.public["cases"] if x["author_tag"]=="UNBOUND"]
        self.assertEqual(len(unbound),12)
        for item in unbound:
            result=lattice.combine(item["text"],item["observed_event"],
                                   item["carrier"],self.source,self.policy)
            self.assertEqual(result["status"],"UNRESOLVED_SOURCE")
            self.assertEqual(result["supported_worlds"],[])
            self.assertTrue(result["other_unmodeled_readings_remain_possible"])

    def test_carrier_preserved_across_all_competing_hypotheses(self):
        case=next(x for x in self.public["cases"] if x["author_tag"]=="AMBIGUOUS")
        out=lattice.combine(case["text"],case["observed_event"],
                            case["carrier"],self.source,self.policy)
        self.assertFalse(out["carrier_truth_authenticated"])
        for g in out["supported_worlds"]:
            m=lattice.corpus.graph_map(g)
            self.assertEqual(m[("DOCUMENT","CARRIER")],case["carrier"])
            self.assertEqual(m[("DOCUMENT","EVIDENCE_STATUS")],
                             lattice.corpus.EPISTEMIC[case["carrier"]])

    def test_tampered_open_world_flag_fails_even_if_rehashed(self):
        fake=deepcopy(self.policy)
        fake["open_world_always"]=False
        fake["receipt_sha256"]=lattice.digest({
            k:v for k,v in fake.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(lattice.HOLD,"overauthorized"):
            lattice.validate_policy(fake)

    def test_rehashed_source_vocabulary_change_not_admissible(self):
        fake=deepcopy(self.policy)
        fake["source_vocabulary"]+=["fabricatednewword"]
        fake["source_vocabulary"].sort()
        fake["receipt_sha256"]=lattice.digest({
            k:v for k,v in fake.items() if k!="receipt_sha256"})
        case=self.public["cases"][0]
        with self.assertRaisesRegex(lattice.HOLD,"Unmatched original"):
            lattice.combine(case["text"],case["observed_event"],
                            case["carrier"],self.source,fake)

    def test_carrier_is_not_a_source_truth_weight(self):
        cases=[c for c in self.public["cases"] if c["author_tag"]=="UNIQUE"]
        self.assertGreater(len(cases),0)
        case=cases[0]
        for carrier in lattice.corpus.CARRIERS:
            row=lattice.combine(case["text"],case["observed_event"],
                                carrier,self.source,self.policy)
            self.assertFalse(row.get("carrier_truth_authenticated",False))
            self.assertFalse(row["root_action_authorized"])

    def test_full_trial_records_all_models_and_nonzero_ambiguity(self):
        result=trial.test(self.policy)
        self.assertEqual(result["schema"],trial.SCHEMA)
        self.assertEqual(len(result["test_packets"]),2)
        self.assertEqual(result["combined"]["open_perspective_lattice"]["cases"],120)
        self.assertTrue(result["meaning_is_set_valued_and_not_forced_to_one"])
        self.assertTrue(result["all_interpretations_remain_open_world"])
        self.assertEqual(result["new_executable_methods_installed"],0)
        self.assertFalse(result["external_actions_executed"])
        for packet in result["test_packets"]:
            self.assertEqual(packet["cases"],60)
            self.assertEqual(packet["author_tag_distribution"],{
                "UNIQUE":24,"AMBIGUOUS":24,"UNBOUND":12})
            self.assertEqual(len(packet["case_witnesses"]),60)
            self.assertTrue(all(x["open_world_always"]
                                for x in packet["case_witnesses"]))

    def test_hold_and_all_24_baselines_show_coverage_cost(self):
        doc=trial.test(self.policy)
        totals=doc["combined"]
        self.assertEqual(totals["always_hold"]["concrete_readings_total"],0)
        self.assertGreater(totals["all_24_possible_graphs"][
            "concrete_readings_total"],totals["open_perspective_lattice"][
                "concrete_readings_total"])
        self.assertGreater(totals["open_perspective_lattice"][
            "multi_world_outputs"],0)


if __name__=="__main__":
    unittest.main()
