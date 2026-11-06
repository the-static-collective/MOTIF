"""Negative controls for source-backed multi-answer reasoning.

These tests deliberately distinguish:
  (a) multiple source-supported answers with no single defensible selection,
  (b) explicit positive AND negative evidence for one scoped proposition,
  (c) simple missing evidence (not false),
  (d) the permission to ask one question (not permission to act).
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from source_graph import (compile_graph,verify_graph,original_022,pin,
                          HOLD as GraphHold)
from inquiry import (SyntheticClarifier,select_question,investigate,
                     HOLD as InquiryHold)
from polarity import all_cases,reason,prior011,pin as pin011,HOLD as PolarityHold
from polarity_cases import CASES,case
from mirror_bridge import reflect,pin as pin019
from trial import synthetic_source,fixed_full_graph_baseline,run

SOURCE_DIR=Path("reason-023-sources")


def question(query="What did Bill give to Mary?",events=None):
    return {
        "source_id":"TEST-ARTIFICIAL",
        "question":query,
        "facts":events if events is not None else [
            {"line":1,"text":"Bill gave the apple to Mary."},
            {"line":2,"text":"Anna gave the bread to Bill."},
            {"line":9,"text":"Bill passed the football to Mary."},
        ],
    }


class ManyTruthTests(unittest.TestCase):
    def test_real_022_engine_sha_is_pinned_and_both_answers_have_actual_source_lines(self):
        self.assertEqual(len(pin()),40)
        raw=question()
        graph=compile_graph(raw)
        self.assertTrue(verify_graph(raw,graph))
        self.assertEqual(graph["status"],"HOLD")
        self.assertEqual(graph["reason"],"NON_UNIQUE_SOURCE_SUPPORTED_ANSWERS")
        self.assertEqual(graph["selected_answer"],None)
        self.assertEqual({x["answer"] for x in graph["candidates"]},
                         {"apple","football"})
        self.assertEqual({x["original_line"] for x in graph["proof_edges"]},
                         {1,9})
        self.assertFalse(graph["permission_to_execute"])

    def test_the_original_single_answer_algorithms_were_overconfident(self):
        original=original_022(question())
        self.assertEqual(original["status"],"ANSWER")
        self.assertEqual(original["answer"],"football")
        graph=compile_graph(question())
        self.assertEqual(len(graph["assumptions_considered"]),2)
        alternatives={x["rule"]:x["answer"] for x in graph["assumptions_considered"]}
        self.assertEqual(alternatives,{
            "EARLIEST_EVENT":"apple","LATEST_EVENT":"football"})
        self.assertTrue(all(x["unverified_relevance_assumption"]
                            for x in graph["assumptions_considered"]))

    def test_same_answer_with_multiple_witnesses_is_not_ambiguity(self):
        source=question(events=[
            {"line":1,"text":"Bill gave the apple to Mary."},
            {"line":6,"text":"Bill passed the apple to Mary."},
        ])
        graph=compile_graph(source)
        self.assertEqual(graph["status"],"ANSWER")
        self.assertEqual(graph["selected_answer"],"apple")
        self.assertEqual(graph["candidates"][0]["source_lines"],[1,6])

    def test_unknown_grammar_no_source_or_unknown_query_never_make_up_an_answer(self):
        unknown=question("Does Mary want a hug?")
        a=compile_graph(unknown)
        self.assertEqual(a["status"],"HOLD")
        self.assertEqual(a["reason"],"UNKNOWN_QUERY_GRAMMAR")
        no_match=question(events=[
            {"line":1,"text":"John gave the apple to Alice."}])
        b=compile_graph(no_match)
        self.assertEqual(b["status"],"HOLD")
        self.assertEqual(b["reason"],"NO_SOURCE_GROUNDED_TRANSFER")
        self.assertEqual(b["candidates"],[])

    def test_all_five_transfer_query_shapes_are_source_witnessed(self):
        queries={
            "What did Bill give to Mary?":{"apple","football"},
            "Who gave the football to Mary?":{"Bill"},
            "Who gave the apple?":{"Bill"},
            "Who did Bill give the football to?":{"Mary"},
            "Who received the football?":{"Mary"},
        }
        for q,answers in queries.items():
            with self.subTest(question=q):
                graph=compile_graph(question(q))
                self.assertEqual({x["answer"] for x in graph["candidates"]},answers)
                self.assertTrue(verify_graph(question(q),graph))

    def test_rehashed_forged_source_evidence_is_rejected_by_replay(self):
        original=compile_graph(question())
        for name in ("invented_answer","altered_source","changed_provenance",
                     "forced_uniqueness"):
            forged=deepcopy(original)
            if name=="invented_answer":
                forged["candidates"].append({
                    "answer":"ghost","support":["FABRICATED"],"source_lines":[500],
                    "assumption":"SPURIOUS","explicit_refutation":[],
                    "confidence_not_calibrated":False})
            if name=="altered_source":
                forged["proof_edges"][0]["original_text"]="A fake claim."
            if name=="changed_provenance":
                forged["original_022_blob"]="0"*40
            if name=="forced_uniqueness":
                forged["selected_answer"]="football";forged["status"]="ANSWER"
            with self.subTest(name=name),self.assertRaises(GraphHold):
                verify_graph(question(),forged)

    def test_mutating_lines_and_duplicate_line_ids_are_not_accepted(self):
        forged=question()
        forged["facts"][1]["line"]=1
        with self.assertRaises(GraphHold):
            compile_graph(forged)

    def test_strong_classical_all_evidence_reference_ties_not_beaten(self):
        source=question()
        self.assertEqual(
            fixed_full_graph_baseline(source),
            sorted(c["answer"] for c in compile_graph(source)["candidates"]))

    def test_balanced_questions_reduce_unknowns_under_explicit_uniform_assumption(self):
        s=select_question(["apple","bread","football","map"])
        self.assertEqual(len(s["if_yes"]),2)
        self.assertEqual(len(s["if_no"]),2)
        self.assertEqual(s["binary_question_information_gain_bits"],1.0)
        self.assertEqual(s["source_contact_permitted_by_question_selection"],False)
        smaller=select_question(["apple","football","map"])
        self.assertEqual(len(smaller["if_yes"]),1)
        self.assertAlmostEqual(smaller["binary_question_information_gain_bits"],
                               0.918296,places=5)

    def test_scripted_owner_can_clarify_without_rewriting_external_source(self):
        graph=compile_graph(synthetic_source())
        simulated=SyntheticClarifier("football",maximum_questions=3)
        result=investigate(graph,simulated)
        self.assertEqual(result["stage"],"CLARIFIED_SYNTHETIC_READ_ONLY")
        self.assertEqual(result["current_source_hypothesis"],"football")
        self.assertEqual(len(result["questions"]),1)
        self.assertTrue(result["provenance_for_clarified_choice"])
        self.assertTrue(result["not_an_historical_dataset_author_clarification"])
        self.assertFalse(result["permission_to_execute"])

    def test_owner_may_refuse_and_motif_must_hold(self):
        graph=compile_graph(synthetic_source())
        person=SyntheticClarifier("apple",refuse=True)
        result=investigate(graph,person)
        self.assertEqual(result["stage"],"HOLD_SOURCE_REFUSED")
        self.assertIsNone(result["current_source_hypothesis"])
        self.assertEqual(len(result["questions"]),1)

    def test_no_contact_and_unpermitted_questions_do_not_contact_person(self):
        graph=compile_graph(synthetic_source())
        for opts in ({"contact":False,"question_permission":True},
                     {"contact":True,"question_permission":False}):
            person=SyntheticClarifier("apple",**opts)
            result=investigate(graph,person)
            self.assertEqual(result["stage"],"HOLD_NO_QUESTION_PERMISSION")
            self.assertEqual(result["questions"],[])
            self.assertEqual(person.asked,0)

    def test_no_owner_is_not_permission_to_ask(self):
        graph=compile_graph(synthetic_source())
        receipt=investigate(graph)
        self.assertEqual(receipt["stage"],"HOLD_AMBIGUITY_NEEDS_SOURCE_PERMISSION")
        self.assertEqual(receipt["questions"],[])

    def test_budget_limit_protects_sources_even_with_supported_answers(self):
        source=question(events=[
            {"line":1,"text":"Bill gave the apple to Mary."},
            {"line":2,"text":"Bill gave the football to Mary."},
            {"line":3,"text":"Bill gave the bread to Mary."},
        ])
        graph=compile_graph(source)
        person=SyntheticClarifier("football",maximum_questions=0)
        response=investigate(graph,person)
        self.assertEqual(response["stage"],"HOLD_QUESTION_BUDGET")
        self.assertEqual(response["questions"],[])

    def test_contradictory_signed_testimony_is_BOTH_not_multiple_answers(self):
        outcomes={x["case"]:x for x in all_cases()}
        self.assertEqual(outcomes["BOTH"]["status"],"BOTH")
        self.assertEqual(outcomes["BOTH"]["support_source_ids"],["S3"])
        self.assertEqual(outcomes["BOTH"]["refute_source_ids"],["S4"])
        self.assertEqual(outcomes["BOTH"]["original_011_verdict"],"BOTH")
        self.assertTrue(outcomes["BOTH"][
            "distinct_possible_answers_are_not_a_four_valued_BOTH"])

    def test_unknown_does_not_mean_refuted(self):
        results={x["case"]:x["status"] for x in all_cases()}
        self.assertEqual(results["AFFIRMED"],"SUPPORTED")
        self.assertEqual(results["DENIED"],"REFUTED")
        self.assertEqual(results["MISSING"],"UNDETERMINED")

    def test_other_people_and_prior_revisions_never_become_local_contradictions(self):
        outcomes={x["case"]:x for x in all_cases()}
        self.assertEqual(outcomes["DIFFERENT_SPEAKER"]["status"],"SUPPORTED")
        self.assertEqual(outcomes["CHANGED_REVISION"]["status"],"REFUTED")
        self.assertEqual(len(outcomes["CHANGED_REVISION"][
            "unrelated_scoped_source_claims"]),1)

    def test_original_011_logic_is_imported_from_an_exact_source_blob(self):
        p=pin011()
        self.assertEqual(len(p["real_reason011"]),40)
        engine=prior011()
        self.assertTrue(callable(engine.verdict))
        self.assertEqual(reason(case("BOTH"))["status"],"BOTH")

    def test_original_019_elves_check_permission_independent_of_self_preference(self):
        pin019()
        allowed=reflect(contact=True,question_permission=True,
                        self_would_ask=False)
        self.assertEqual(allowed["recommended_read_only_question_or_wait"],
                         "ASK_PREFERENCE")
        blocked=reflect(contact=True,question_permission=False,
                        self_would_ask=True)
        self.assertEqual(blocked["recommended_read_only_question_or_wait"],"WAIT")
        self.assertIn("NO_QUESTION_PERMISSION",
                      blocked["four_original_subprocess_reports"]["CRITIC"][
                          "judgments"]["ASK_PREFERENCE"]["refusals"])

    def test_no_contact_original_019_critic_blocks_asking(self):
        report=reflect(contact=False,question_permission=False)
        self.assertEqual(report["recommended_read_only_question_or_wait"],"WAIT")
        self.assertFalse(report["external_actions"])
        self.assertFalse(report["permission_to_execute"])
        self.assertEqual(set(report["four_original_subprocess_reports"]),{
            "SELF","OTHER","MIRROR","CRITIC"})

    def test_external_source_query_never_contains_gold_or_annotated_support(self):
        if not SOURCE_DIR.is_dir():self.skipTest("External source acquisition required")
        from acquire import SOURCES
        from corpus import read,query_input
        q=read(SOURCE_DIR/SOURCES["TRANSFER"]["test"][0],
               "TRANSFER","test",limit=1,skip=500)[0]
        src=query_input(q)
        self.assertEqual(set(src),{"facts","question","source_id"})
        self.assertNotIn("answer",src)
        self.assertNotIn("supporting_ids",src)
        self.assertTrue(verify_graph(src,compile_graph(src)))

    def test_full_new_250_question_external_audit_balances_unique_hold_wrong(self):
        if not SOURCE_DIR.is_dir():self.skipTest("External source acquisition required")
        r=run(source_dir=SOURCE_DIR)
        o=r["external_test_counts"]
        self.assertEqual(o["total"],250)
        self.assertEqual(o["strong_classical_equivalence"],250)
        self.assertEqual(o["source_single_answer"]+o["source_non_unique"]+
                         o["source_no_answer"],250)
        self.assertEqual(o["source_single_answer"],
                         o["single_answer_correct"]+o["single_answer_wrong"])
        self.assertEqual(o["source_non_unique"],
                         o["non_unique_gold_supported"]+
                         o["non_unique_gold_not_supported"])
        self.assertEqual(r["independent_test_first_ordinal"],501)
        self.assertEqual(r["independent_test_last_ordinal"],750)
        self.assertFalse(r["permission_to_execute"])
        self.assertEqual(r["scripted_ambiguous_case"]["owner_declined"][
                         "stage"],"HOLD_SOURCE_REFUSED")


if __name__=="__main__":
    unittest.main()
