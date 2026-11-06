"""LEGIT-006: falsifiers for evidence polarity, scope, echo and silent-world logic."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import unittest

from grammar import HOLD as GrammarHOLD, learn, parse
from ledger import HOLD as LedgerHOLD, inspect, evaluate, validate
from runner import examine, learned, example
from benchmark import all_cases, ledger_for, external_ood_probe, run
from classical_reference import parse_reference, reference_truth


class SemanticAdversaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grammar=learned()

    def _blank(self):
        return {"schema":"motif.synthetic-epistemic-ledger.v1",
                "id":"SilentWorld","scope":"SYNTHETIC_ONLY",
                "target":"hidden shelter","indicator":"sonar ping","reports":[]}

    def _report(self,ident,root,kind="NEGATIVE_SENSOR",assurance="DECLARED_VALID",
                coverage="PARTIAL",detection="UNKNOWN"):
        return {"id":ident,"root":root,"kind":kind,"assurance":assurance,
                "coverage":coverage,"detection":detection}

    def test_learned_eight_distinct_semantics_and_unseen_composition(self):
        self.assertEqual(self.grammar["teacher_count"],32)
        self.assertEqual(len(self.grammar["rules"]),32)
        self.assertEqual(self.grammar["unseen_full_pairs"],16)
        self.assertFalse(self.grammar["real_world_authority"])

    def test_training_source_words_absent_from_rules(self):
        rules=str(self.grammar["rules"])
        for phrase in ("underwater habitat","sonar echo","forest fire",
                       "radio burst","distant spacecraft","seismic pulse"):
            self.assertNotIn(phrase,rules)

    def test_one_negation_changes_what_is_claimed(self):
        base=self._blank()
        a=examine("there is no evidence that hidden shelter exists.",base,self.grammar)
        b=examine("there is evidence that hidden shelter does not exist.",base,self.grammar)
        self.assertEqual(a["claim"]["kind"],"NO_POSITIVE_EVIDENCE")
        self.assertEqual(b["claim"]["kind"],"HAS_NEGATIVE_EVIDENCE")
        self.assertIs(a["answer"],True)
        self.assertIs(b["answer"],False)
        self.assertEqual(a["proof"]["worlds"],[False,True])
        self.assertEqual(b["proof"]["worlds"],[False,True])

    def test_lack_of_negative_evidence_not_proof_of_presence(self):
        blank=self._blank()
        a=examine("there is no evidence that hidden shelter is absent.",blank,self.grammar)
        b=examine("there is evidence that hidden shelter exists.",blank,self.grammar)
        self.assertIs(a["answer"],True)
        self.assertIs(b["answer"],False)
        self.assertEqual(a["claim"]["kind"],"NO_NEGATIVE_EVIDENCE")
        self.assertEqual(b["claim"]["kind"],"HAS_POSITIVE_EVIDENCE")

    def test_negative_sensor_is_evidence_but_not_proof(self):
        packet=self._blank()
        packet["reports"].append(self._report("n1","root1"))
        negative=examine("there is evidence that hidden shelter is absent.",
                         packet,self.grammar)
        proof=examine("does a negative sonar ping prove hidden shelter is absent?",
                      packet,self.grammar)
        possible=examine("can hidden shelter exist despite a negative sonar ping?",
                         packet,self.grammar)
        self.assertIs(negative["answer"],True)
        self.assertIs(proof["answer"],False)
        self.assertIs(possible["answer"],True)
        self.assertEqual(proof["proof"]["worlds"],[False,True])

    def test_exhaustive_guaranteed_synthetic_sensor_changes_entailment(self):
        packet=self._blank()
        packet["reports"].append(self._report("n1","root1",
                          coverage="EXHAUSTIVE",detection="GUARANTEED"))
        self.assertIs(examine("does a negative sonar ping prove hidden shelter is absent?",
                              packet,self.grammar)["answer"],True)
        self.assertIs(examine("can hidden shelter exist despite a negative sonar ping?",
                              packet,self.grammar)["answer"],False)
        self.assertEqual(inspect(packet)["state"],"ABSENT_WITHIN_DECLARED_MODEL")

    def test_positive_witness_entails_presence_within_declaration_only(self):
        packet=self._blank()
        packet["reports"].append(self._report("p1","root1","POSITIVE_WITNESS",
                           coverage="UNSPECIFIED",detection="UNSPECIFIED"))
        self.assertIs(examine("does a positive sonar ping prove hidden shelter exists?",
                              packet,self.grammar)["answer"],True)
        self.assertIs(examine("can hidden shelter be absent despite a positive sonar ping?",
                              packet,self.grammar)["answer"],False)
        self.assertIs(examine("there is evidence that hidden shelter exists.",
                              packet,self.grammar)["answer"],True)
        self.assertEqual(inspect(packet)["state"],"PRESENT_WITHIN_DECLARED_MODEL")

    def test_unverified_source_does_not_manufacture_admitted_evidence(self):
        packet=self._blank()
        packet["reports"].append(self._report("n1","root1",
                         assurance="UNVERIFIED",coverage="EXHAUSTIVE",
                         detection="GUARANTEED"))
        self.assertEqual(inspect(packet)["unverified_roots"],1)
        self.assertIs(examine("there is no evidence that hidden shelter is absent.",
                              packet,self.grammar)["answer"],True)
        self.assertEqual(inspect(packet)["worlds"],[False,True])

    def test_echoes_do_not_multiply_sources(self):
        packet=self._blank()
        packet["reports"]=[self._report("p"+str(i),"root1","POSITIVE_WITNESS",
                                coverage="UNSPECIFIED",detection="UNSPECIFIED")
                           for i in range(1,10)]
        summary=inspect(packet)
        self.assertEqual(summary["distinct_root_count"],1)
        self.assertEqual(summary["echo_count"],8)
        self.assertEqual(summary["declared_valid_positive_roots"],1)

    def test_shared_root_conflict_must_hold(self):
        packet=self._blank()
        packet["reports"]=[
            self._report("r1","shared","NEGATIVE_SENSOR",
                         coverage="PARTIAL",detection="UNKNOWN"),
            self._report("r2","shared","POSITIVE_WITNESS",
                         coverage="UNSPECIFIED",detection="UNSPECIFIED")]
        with self.assertRaises(LedgerHOLD):
            inspect(packet)

    def test_independent_conflicting_sources_no_explosion(self):
        packet=self._blank()
        packet["reports"]=[
            self._report("p1","witness","POSITIVE_WITNESS",
                         coverage="UNSPECIFIED",detection="UNSPECIFIED"),
            self._report("n1","sensor","NEGATIVE_SENSOR",
                         coverage="EXHAUSTIVE",detection="GUARANTEED")]
        r=examine("there is evidence that hidden shelter exists.",packet,self.grammar)
        self.assertEqual(r["status"],"HOLD_CONFLICTING_EVIDENCE")
        self.assertIsNone(r["answer"])
        self.assertEqual(inspect(packet)["worlds"],[])
        self.assertEqual(evaluate(packet,"MUST_ABSENT")["verdict"],
                         "HOLD_INCONSISTENT_PREMISES")

    def test_unsupported_observer_trust_does_not_trick_router(self):
        packet=self._blank()
        packet["scope"]="LIVE_PATIENT_DIAGNOSIS"
        r=examine("there is evidence that hidden shelter exists.",packet,self.grammar)
        self.assertEqual(r["status"],"HOLD_INVALID_SOURCE_LEDGER")

    def test_report_invalid_kind_and_assurance_hold(self):
        for field,value in (("kind","OMNISCIENT"),
                            ("assurance","AUTHENTICATED_BY_GOD"),
                            ("coverage","INFINITE"),
                            ("detection","MAYBE")):
            packet=self._blank()
            report=self._report("n1","root1")
            report[field]=value
            packet["reports"]=[report]
            with self.assertRaises(LedgerHOLD):
                inspect(packet)

    def test_report_missing_or_extra_fields_hold(self):
        packet=self._blank()
        packet["reports"]=[self._report("n1","root1")]
        packet["reports"][0].pop("root")
        with self.assertRaises(LedgerHOLD):
            inspect(packet)
        packet=self._blank()
        packet["reports"]=[self._report("n1","root1")]
        packet["reports"][0]["hidden_truth"]=True
        with self.assertRaises(LedgerHOLD):
            inspect(packet)

    def test_duplicate_reports_not_unique_identifiers(self):
        packet=self._blank()
        packet["reports"]=[self._report("same","root1"),
                           self._report("same","root2")]
        with self.assertRaises(LedgerHOLD):
            inspect(packet)

    def test_data_only_cannot_set_actual_world_state(self):
        packet=self._blank()
        packet["world_actually_present"]=True
        with self.assertRaises(LedgerHOLD):
            inspect(packet)

    def test_teacher_unknown_semantic_operator_hold(self):
        source=json.loads((Path(__file__).with_name("teacher.json")).read_text())
        records=source["records"]
        records[0]["kind"]="GOD_PROVED_NEGATION"
        with self.assertRaises(GrammarHOLD):
            learn(records)

    def test_duplicate_teacher_provenance_hold(self):
        source=json.loads((Path(__file__).with_name("teacher.json")).read_text())
        records=source["records"]
        records[0]["id"]=records[1]["id"]
        with self.assertRaises(GrammarHOLD):
            learn(records)

    def test_unmatched_teacher_annotation_hold(self):
        source=json.loads((Path(__file__).with_name("teacher.json")).read_text())
        records=source["records"]
        records[0]["target"]="not a real phrase"
        with self.assertRaises(GrammarHOLD):
            learn(records)

    def test_valid_source_separated_full_phrase_pair_transfer(self):
        cases=[r for r in all_cases() if r["split"]=="learned_pair_new_topic"]
        self.assertEqual(len(cases),32)
        for case in cases:
            parsed=parse(case["sentence"],self.grammar)
            self.assertEqual(parsed["status"],"PARSE_PROPOSAL_ONLY",case["id"])
            self.assertEqual(parsed["kind"],case["gold_kind"])
            self.assertTrue(parsed["seen_pair_in_teacher"])

    def test_unseen_fragment_recombinations(self):
        cases=[r for r in all_cases() if r["split"]=="unseen_component_recomposition"]
        self.assertEqual(len(cases),32)
        for case in cases:
            parsed=parse(case["sentence"],self.grammar)
            self.assertEqual(parsed["status"],"PARSE_PROPOSAL_ONLY",case["id"])
            self.assertEqual(parsed["kind"],case["gold_kind"])
            self.assertFalse(parsed["seen_pair_in_teacher"],case["id"])

    def test_unseen_wording_refused_by_induced_grammar(self):
        cases=[r for r in all_cases() if r["split"]=="genuinely_unseen_lexicon"]
        self.assertEqual(len(cases),8)
        for case in cases:
            self.assertEqual(parse(case["sentence"],self.grammar)["status"],
                             "HOLD_UNKNOWN_SEMANTICS",case["id"])

    def test_hostile_minimal_pair_negation_rejected(self):
        cases=[r for r in all_cases() if r["split"]=="hostile_scope_or_negation"]
        self.assertEqual(len(cases),12)
        for case in cases:
            result=examine(case["sentence"],ledger_for(case),self.grammar)
            self.assertNotIn(result["status"],(
                "RESEARCH_PROPOSAL_ONLY","HOLD_CONFLICTING_EVIDENCE"),case["id"])

    def test_sensor_and_target_mismatch_hold(self):
        cases=[r for r in all_cases() if r["split"]=="source_target_or_sensor_mismatch"]
        self.assertEqual(len(cases),8)
        for case in cases:
            result=examine(case["sentence"],ledger_for(case),self.grammar)
            self.assertNotIn(result["status"],(
                "RESEARCH_PROPOSAL_ONLY","HOLD_CONFLICTING_EVIDENCE"),case["id"])

    def test_independent_exact_oracle_matches_every_accepted_truth(self):
        for case in all_cases():
            ledger=ledger_for(case)
            result=examine(case["sentence"],ledger,self.grammar)
            if result["status"] in ("RESEARCH_PROPOSAL_ONLY","HOLD_CONFLICTING_EVIDENCE"):
                self.assertEqual(result["claim"]["kind"],case["gold_kind"])
                self.assertEqual(result["answer"],
                                 reference_truth(ledger,case["gold_kind"]))

    def test_classical_comparator_is_genuinely_separate_and_stronger_on_lexicon(self):
        extra=[r for r in all_cases() if r["split"]=="genuinely_unseen_lexicon"]
        self.assertEqual(sum(parse_reference(r["sentence"],r["target"],
                           r["indicator"]) is not None for r in extra),4)

    def test_external_fraCas_is_real_unsupported_nli_not_faked_as_success(self):
        summary=external_ood_probe(self.grammar)
        self.assertGreater(summary["independently_authored_nli_pairs"],50)
        self.assertIn("NLI",summary["reason"])
        self.assertIsNone(summary["nli_accuracy"])
        self.assertEqual(summary["actual_nli_answers_issued"],0)
        self.assertEqual(summary["status"],"HOLD_UNSUPPORTED_NLI_TASK")

    def test_full_benchmark_preserves_classical_victory_and_failure_traces(self):
        outcome=run()
        self.assertEqual(outcome,run())
        self.assertEqual(outcome["registered_cases"],92)
        metrics=outcome["methods"]
        self.assertEqual(metrics["induced"]["ALL"]["correct_kind_and_truth"],64)
        self.assertEqual(metrics["rote"]["ALL"]["correct_kind_and_truth"],32)
        self.assertEqual(metrics["classical"]["ALL"]["correct_kind_and_truth"],68)
        self.assertEqual(metrics["always_hold"]["ALL"]["correct_kind_and_truth"],0)
        for method in metrics:
            self.assertEqual(metrics[method]["ALL"]["invalid_accepted"],0,method)
            self.assertEqual(metrics[method]["ALL"]["wrong_kind"],0,method)
            self.assertEqual(metrics[method]["ALL"]["wrong_logical_value"],0,method)
        self.assertGreater(metrics["induced"]["ALL"]["toy_selective_loss"],
                           metrics["classical"]["ALL"]["toy_selective_loss"])
        self.assertFalse(outcome["registered_author_independent"])
        self.assertFalse(outcome["real_world_authority"])

    def test_runtime_does_not_execute_message_or_external_action(self):
        result=examine("can hidden shelter exist despite a negative sonar ping?",
                       self._blank(),self.grammar)
        self.assertFalse(result["external_actions"])
        self.assertFalse(result["real_world_authority"])
        self.assertIsNone(result["actual_target_state"])
        self.assertIsNone(result["individual_probability"])

    def test_unrecognized_language_proposes_unsent_clarification(self):
        result=examine("what does existence mean?",
                       self._blank(),self.grammar)
        self.assertEqual(result["status"],"HOLD_UNKNOWN_MEANING")
        self.assertFalse(result["sent"])
        self.assertIsNone(result["answer"])

if __name__=="__main__":
    unittest.main()
