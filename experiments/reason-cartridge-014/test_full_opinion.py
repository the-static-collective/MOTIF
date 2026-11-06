"""Protect full-corpus integrity and avoid manufactured legal conclusions.

These tests run against actual downloaded opinion bodies in reason-014-sources;
the source downloader pins the original Cornell HTML and every paragraph.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import os
import unittest

from acquire import CASES,extract
from contract import SHA,DEVELOPMENT,UNSEEN
from reader import (HOLD,read_source,attributed,retrieve,validate_receipt,
                    tokens,new_voice)
from review_keys import HELDOUT_QUESTIONS,NEGATIVE_QUESTIONS
from trial import evaluate


ROOT=os.environ.get("MOTIF_REASON014_SOURCES","reason-014-sources")


class FullOpinionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs={key:read_source(ROOT,key) for key in CASES}

    def test_two_unseen_cases_and_all_four_url_pins(self):
        self.assertEqual(set(DEVELOPMENT),{"MCBOYLE","NIX"})
        self.assertEqual(set(UNSEEN),{"KIRBY","BALLARD"})
        self.assertTrue(set(DEVELOPMENT).isdisjoint(UNSEEN))
        for case,doc in self.docs.items():
            self.assertEqual(doc["raw_page_sha256"],SHA[case]["raw"])
            self.assertEqual(doc["opinion_body_sha256"],SHA[case]["body"])
            self.assertTrue(doc["full_page_not_a_signed_official_court_feed"])
            self.assertTrue(doc["complete_source_body_not_manually_selected_quotes"])

    def test_full_bodies_not_just_cherry_picked_quotes(self):
        self.assertGreater(self.docs["KIRBY"]["word_count"],1000)
        self.assertGreater(self.docs["BALLARD"]["word_count"],5000)
        self.assertGreaterEqual(self.docs["BALLARD"]["paragraph_count"],50)
        self.assertGreaterEqual(self.docs["KIRBY"]["paragraph_count"],25)
        text=" ".join(p["text"] for p in self.docs["BALLARD"]["full_untrimmed_body_paragraphs"])
        for phrase in ("Justice DOUGLAS","Chief Justice STONE","Justice JACKSON"):
            self.assertIn(phrase,text)

    def test_court_voice_splits_majority_stone_and_jackson_dissents(self):
        rows=attributed(self.docs["BALLARD"])
        voices={(p["judge"],p["voice_role"]) for p in rows}
        for expected in (
            ("DOUGLAS","OPINION_OF_COURT"),
            ("STONE","DISSENT"),
            ("JACKSON","DISSENT"),
        ):
            self.assertIn(expected,voices)

    def test_kirby_surgeon_analogy_does_not_create_second_court_author(self):
        rows=attributed(self.docs["KIRBY"])
        self.assertTrue(any("surgeon who opened the vein" in p["text"] for p in rows))
        self.assertIn(("FIELD","OPINION_OF_COURT"),
                      {(p["judge"],p["voice_role"]) for p in rows})
        self.assertFalse(any(p["judge"]=="MILLER" for p in rows))

    def test_complete_text_retrieval_retains_citation_anchors(self):
        for case in UNSEEN:
            outcome=retrieve(ROOT,case,"What did this Court decide about the statute and judgment?")
            self.assertEqual(outcome["searched_paragraphs"],
                             self.docs[case]["paragraph_count"])
            self.assertFalse(outcome["no_legal_outcome_inferred"] is False)
            for row in outcome["results"]:
                self.assertEqual(row["citation"],self.docs[case]["citation"])
                self.assertTrue(row["source_url"].startswith(self.docs[case]["url"]))
                source=self.docs[case]["full_untrimmed_body_paragraphs"]
                canonical=source[row["paragraph_ordinal"]-1]
                self.assertEqual(row["excerpt"],canonical["text"])
                self.assertEqual(row["text_sha256"],canonical["sha256"])

    def test_no_source_for_cheese_court_claim(self):
        for q in NEGATIVE_QUESTIONS:
            outcome=retrieve(ROOT,q["case"],q["question"])
            self.assertEqual(outcome["status"],"HOLD_NO_ANCHORED_EVIDENCE")
            self.assertEqual(outcome["results"],[])
            self.assertFalse(outcome["legal_advice"])

    def test_relevant_religious_supernatural_question_is_not_answered_as_truth(self):
        result=retrieve(ROOT,"BALLARD",
            "Did the Supreme Court prove supernatural spiritual healings really occurred?")
        self.assertTrue(result["no_legal_outcome_inferred"])
        self.assertFalse(result["real_world_authority"])
        self.assertNotIn("verdict",result)

    def test_independently_curated_relevant_passages_exist_in_unabridged_source(self):
        for review in HELDOUT_QUESTIONS:
            rows=attributed(self.docs[review["case"]])
            match=[row for row in rows if review["target"].lower() in row["text"].lower()]
            self.assertGreaterEqual(len(match),1,review["id"])
            self.assertTrue(any(x["voice_role"]==review["voice"] for x in match),
                            review["id"])

    def test_bm25_retrieval_and_overlap_baselines_deterministic(self):
        for algorithm in ("BM25","OVERLAP"):
            r1=retrieve(ROOT,"BALLARD",
                "What was Justice Jackson's view about dismissing an indictment?",
                method=algorithm,k=3)
            self.assertEqual(r1,retrieve(ROOT,"BALLARD",
                "What was Justice Jackson's view about dismissing an indictment?",
                method=algorithm,k=3))
            self.assertEqual(validate_receipt(ROOT,r1),r1)

    def test_forged_opinion_year_quote_author_or_url_cannot_be_replayed(self):
        r=retrieve(ROOT,"KIRBY",
            "What happened when a sheriff arrested the carrier of the mail?",k=3)
        self.assertGreater(len(r["results"]),0)
        for mode in ("role","quote","source","authority","year"):
            changed=deepcopy(r)
            if mode=="role":changed["results"][0]["voice_role"]="DISSENT"
            elif mode=="quote":changed["results"][0]["excerpt"]="Court was made of cheese"
            elif mode=="source":changed["results"][0]["source_url"]="https://evil.invalid"
            elif mode=="authority":changed["real_world_authority"]=True
            else:changed["results"][0]["citation"]="2026 U.S. 999"
            with self.subTest(mode=mode),self.assertRaises(HOLD):
                validate_receipt(ROOT,changed)

    def test_source_mutation_is_rejected_even_when_manually_rehashed(self):
        case="KIRBY"
        with TemporaryDirectory() as directory:
            original=Path(ROOT)
            dest=Path(directory)
            for suffix in (".raw.html",".full.json"):
                (dest/(case.lower()+suffix)).write_bytes(
                    (original/(case.lower()+suffix)).read_bytes())
            doc=json.loads((dest/(case.lower()+".full.json")).read_text())
            doc["full_untrimmed_body_paragraphs"][0]["text"]="False judicial quote"
            content=json.dumps(doc,sort_keys=True,indent=2)
            (dest/(case.lower()+".full.json")).write_text(content)
            with self.assertRaises(HOLD):
                read_source(dest,case)

    def test_unsupported_case_missing_court_source_fails_closed(self):
        with self.assertRaises(HOLD):
            read_source(ROOT,"FUTURE_COURT_2099")
        with TemporaryDirectory() as d:
            with self.assertRaises(HOLD):
                read_source(d,"BALLARD")

    def test_unbounded_questions_methods_and_retrieval_depth_refused(self):
        with self.assertRaises(HOLD):retrieve(ROOT,"KIRBY","")
        with self.assertRaises(HOLD):retrieve(ROOT,"KIRBY","legal"*90)
        with self.assertRaises(HOLD):retrieve(ROOT,"KIRBY","what happened?",k=100)
        with self.assertRaises(HOLD):retrieve(ROOT,"KIRBY","what happened?",method="CALL_LLM")

    def test_source_owner_benchmark_preserves_measured_outcomes(self):
        result=evaluate(ROOT)
        self.assertEqual(result["heldout_question_count"],11)
        self.assertEqual(result["total_source_words"],
                         sum(d["word_count"] for d in self.docs.values()))
        self.assertTrue(result["plain_BM25_is_a_strong_classical_retrieval_baseline"])
        self.assertFalse(result["legal_holding_from_text_automatically_inferred"])
        self.assertFalse(result["real_world_authority"])
        self.assertEqual(len(result["heldout_questions"]),11)
        self.assertEqual(len(result["out_of_source_questions"]),2)
        self.assertTrue(all(x["status"]=="HOLD_NO_ANCHORED_EVIDENCE"
                            for x in result["out_of_source_questions"]))

    def test_gold_labels_never_imported_by_reader(self):
        import inspect,reader
        code=inspect.getsource(reader)
        self.assertNotIn("review_keys",code)
        self.assertNotIn("HELDOUT_QUESTIONS",code)
        self.assertNotIn("GOLD",code)

if __name__=="__main__":
    unittest.main()
