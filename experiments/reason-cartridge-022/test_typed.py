"""REASON-022: independent external benchmark, real typed machines, Golden Rule gates.

The independent source files come from a *third-party-authored* bAbI task
repository pinned by exact Git blob. This isn't an independent ethical
evaluation. The hand-written typed programs may fail; report those failures
rather than silently treating abstention as correctness.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
import unittest

from acquire import SOURCES,get_sources,git_blob,COMMIT
from corpus import read,query_input
from engines import solve,count_before_source_repair
from router import discover,infer,boolean_projection_witness,question_family
from obligations import CASES,all_proofs,source_proof,contradiction,old_binary_projection
from mirror_bridge import four_elves,run_all,pin
from trial import run
from ambiguity import transfer_source_audit

ROOT=Path("reason-022-sources")


def request(facts,question):
    return {"source_id":"UNIT-001","question":question,
            "facts":[{"line":i+1,"text":t} for i,t in enumerate(facts)]}


class TypedConceptTests(unittest.TestCase):
    def test_distinct_typed_machines_are_not_a_single_boolean_slot(self):
        self.assertEqual(set(SOURCES),{"COUNT","TIME","TRANSFER"})
        self.assertEqual(question_family("How many objects is Mary carrying?"),
                         "CARDINALITY_QUERY")
        self.assertEqual(question_family("Where was Mary before the cinema?"),
                         "PREDECESSOR_QUERY")
        self.assertEqual(question_family("Who gave the apple to Jeff?"),
                         "TRIADIC_QUERY")
        self.assertEqual(question_family("Do this for me tomorrow?"),"UNRECOGNIZED")

    def test_quantity_tracks_item_ownership_across_transfer_not_only_presence(self):
        q=request(["Mary got the milk there.",
                   "Mary grabbed the apple there.",
                   "Mary gave the milk to Sandra."],
                  "How many objects is Mary carrying?")
        self.assertEqual(solve("QUANTITY",q)["answer"],"one")
        other=deepcopy(q)
        other["question"]="How many objects is Sandra carrying?"
        self.assertEqual(solve("QUANTITY",other)["answer"],"one")
        self.assertEqual(len(solve("QUANTITY",q)["premises"]),1)

    def test_quantity_handles_zero_and_multiple_distinct_items(self):
        q=request(["Mary got the milk there.","Mary grabbed the apple there."],
                  "How many objects is Mary carrying?")
        self.assertEqual(solve("QUANTITY",q)["answer"],"two")
        q["facts"].append({"line":3,"text":"Mary left the apple."})
        q["facts"].append({"line":4,"text":"Mary left the milk."})
        self.assertEqual(solve("QUANTITY",q)["answer"],"none")

    def test_source_discovered_discard_variants_repair_old_count_failure(self):
        q=request(["John grabbed the apple there.",
                   "John discarded the apple."],
                  "How many objects is John carrying?")
        self.assertEqual(count_before_source_repair(q)["answer"],"one")
        self.assertEqual(solve("QUANTITY",q)["answer"],"none")
        q["facts"][-1]["text"]="John dropped the apple there."
        self.assertEqual(count_before_source_repair(q)["answer"],"one")
        self.assertEqual(solve("QUANTITY",q)["answer"],"none")

    def test_temporal_ordering_ignores_narration_line_order(self):
        q=request([
            "This afternoon Mary moved to the cinema.",
            "Yesterday Mary journeyed to the school.",
            "This morning Mary moved to the kitchen.",
        ],"Where was Mary before the cinema?")
        p=solve("ORDERED_TIME",q)
        self.assertEqual(p["answer"],"kitchen")
        self.assertEqual([x[0] for x in p["premises"]],[3,1])

    def test_three_party_relationship_distinguishes_giver_receiver_object(self):
        q=request([
            "Fred gave the apple to Mary.",
            "Mary handed the apple to Bill.",
        ],"Who gave the apple to Bill?")
        self.assertEqual(solve("TRIADIC_TRANSFER",q)["answer"],"Mary")
        q["question"]="Who did Fred give the apple to?"
        self.assertEqual(solve("TRIADIC_TRANSFER",q)["answer"],"Mary")
        q["question"]="Who received the apple?"
        self.assertEqual(solve("TRIADIC_TRANSFER",q)["answer"],"Bill")

    def test_unsupported_questions_cannot_be_forced_through_wrong_type(self):
        q=request(["This morning Mary moved to the cinema."],
                  "Please change somebody's preferences?")
        for kind in ("QUANTITY","ORDERED_TIME","TRIADIC_TRANSFER"):
            p=solve(kind,q)
            self.assertEqual(p["status"],"HOLD")
            self.assertFalse(p["actions_permitted"])

    def test_source_receipts_cite_only_actual_source_lines(self):
        q=request(["Fred handed the apple to Mary."],
                  "Who received the apple?")
        s=solve("TRIADIC_TRANSFER",q)
        self.assertEqual(s["premises"],[(1,"Fred handed the apple to Mary.")])
        self.assertEqual(s["status"],"ANSWER")
        self.assertFalse(s["actions_permitted"])

    def test_obligation_capacity_conflict_is_a_different_kind_of_distinction(self):
        a=source_proof(CASES[0]);b=source_proof(CASES[1])
        self.assertEqual(a["state"],"SUGGEST_DISCUSSION_ONLY")
        self.assertEqual(b["state"],"HOLD_PRIOR_DUTIES")
        self.assertEqual(old_binary_projection(CASES[0]),
                         old_binary_projection(CASES[1]))
        self.assertEqual(contradiction()["case_a_result"],a["state"])

    def test_deadlines_mathematically_constrain_possible_offers(self):
        # D05 has enough TOTAL units, but zero time to complete one by 12.
        d=source_proof(CASES[4])
        self.assertEqual(d["state"],"HOLD_DEADLINE_CAPACITY")
        self.assertEqual(d["reason"],"SOURCE_COMMITMENTS_CANNOT_FIT_TIME_ORDERED_CAPACITY")
        self.assertEqual(d["current_hour"],12)
        self.assertEqual(d["new_request_deadline"],12)
        # Multiple competing third-party promises cannot be collapsed into
        # one binary "already owes someone" flag.
        self.assertEqual(len(source_proof(CASES[5])["relevant_deadlines"]),2)

    def test_scope_refusal_and_no_contact_are_hard_not_weighted_gates(self):
        self.assertEqual(source_proof(CASES[2])["state"],"HOLD_NO_SCOPED_PERMISSION")
        self.assertEqual(source_proof(CASES[3])["state"],"HOLD_NO_CONTACT")
        self.assertTrue(all(s["permission_to_execute"] is False for s in all_proofs()))

    def test_source_contract_does_not_let_operator_forge_new_consent(self):
        f=deepcopy(CASES[2]);f["options_discussion_allowed"]=True
        with self.assertRaises(ValueError):source_proof(f)
        g=deepcopy(CASES[0]);g["real_world_permission"]=True
        with self.assertRaises(ValueError):source_proof(g)

    def test_prior_real_golden_mirror_elves_reject_an_unsafe_duty(self):
        prior=pin()
        self.assertEqual(len(prior),40)
        cases=run_all()
        self.assertEqual(len(cases),7)
        for result in cases:
            p=result["typed_proof"]
            self.assertEqual(result["critic_eligible_for_read_only_discussion"],
                             p["state"]=="SUGGEST_DISCUSSION_ONLY")
            self.assertEqual(set(result["original_019_four_processes"]),
                             {"SELF","OTHER","MIRROR","CRITIC"})
            self.assertFalse(result["external_actions"])

    def test_gold_answers_and_official_support_indices_are_hidden_from_the_solver(self):
        if not ROOT.is_dir():self.skipTest("External datasets not acquired")
        path=ROOT/SOURCES["TRANSFER"]["test"][0]
        if not path.exists():self.skipTest("External datasets not acquired")
        rows=read(path,"TRANSFER","test",limit=3)
        self.assertGreaterEqual(len(rows),3)
        for row in rows:
            obj=query_input(row)
            self.assertEqual(set(obj),{"facts","question","source_id"})
            self.assertNotIn("answer",str(obj.keys()))
            self.assertNotIn("supporting_ids",str(obj.keys()))

    def test_external_data_are_immutable_pinned_third_party_authored_files(self):
        if not ROOT.is_dir():self.skipTest("External datasets not acquired")
        for kind,parts in SOURCES.items():
            for split,(filename,sha) in parts.items():
                raw=(ROOT/filename).read_bytes()
                self.assertEqual(git_blob(raw),sha)
        self.assertEqual(len(COMMIT),40)

    def test_external_gold_can_choose_one_answer_when_two_are_supported(self):
        if not ROOT.is_dir():self.skipTest("External dataset not acquired")
        rows=read(ROOT/SOURCES["TRANSFER"]["test"][0],"TRANSFER","test",
                  limit=250,skip=250)
        audit=transfer_source_audit(rows)
        self.assertEqual(len(audit),1)
        ambiguity=audit[0]
        self.assertEqual(ambiguity["official_dataset_gold"],"football")
        self.assertEqual(ambiguity["model_latest_matching_transfer"],"apple")
        self.assertEqual(set(ambiguity["all_source_supported_distinct_answer_options"]),
                         {"apple","football"})
        self.assertIn(22,ambiguity["official_supporting_line_ids_for_scoring"])
        self.assertEqual(ambiguity["posthoc_finding"],
                         "MULTIPLE_EXPLICITLY_SUPPORTED_ANSWERS")
        self.assertTrue(ambiguity["model_was_overconfident_about_a_non_unique_answer"])
        self.assertTrue(ambiguity["gold_used_only_in_posthoc_audit_not_in_engine"])

    def test_real_independent_babi_eval_respects_coverage_and_reports_errors(self):
        if not ROOT.is_dir():self.skipTest("External datasets not acquired")
        result=run(source_dir=ROOT,train_limit=60,test_limit=250)
        self.assertEqual(result["training_questions"],180)
        self.assertEqual(result["test_questions"],750)
        self.assertEqual(result["inspected_development_questions"],750)
        self.assertEqual(result["first_run_counting_development_exact_before_repair"],226)
        self.assertEqual(result["same_inspected_counting_development_exact_after_repair"],250)
        self.assertTrue(result["prospective_external_test_starts_after_first_250_per_family"])
        self.assertEqual(len(result["external_test"]),3)
        self.assertEqual(len(result["independent_external_posthoc_ambiguous_gold_cases"]),1)
        self.assertEqual(set(result["trained_question_type_router"][
                            "question_grammar_to_typed_engine"].values()),
                         {"QUANTITY","ORDERED_TIME","TRIADIC_TRANSFER"})
        for family,score in result["external_test"].items():
            self.assertEqual(score["independently_authored_test_questions"],250)
            self.assertEqual(score["exact_source_answers"]+
                             score["incorrect_confident_answers"]+
                             score["explicit_abstentions"],250)
            self.assertEqual(score["source_bound_evidence_receipts"],
                             score["exact_source_answers"]+
                             score["incorrect_confident_answers"])
        self.assertGreaterEqual(len(result[
            "source_training_boolean_projection_impossibilities"]),3)
        self.assertFalse(result["external_actions"])
        self.assertTrue(result[
            "independent_external_QA_is_not_independent_human_ethics_evaluation"])


if __name__=="__main__":
    unittest.main()
