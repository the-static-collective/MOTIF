"""025F: second job interview is actual T5 encoder, not decoder/hype output."""
import unittest
from frozen_jobs import CASES,JOBS
from semantic_holdout import SEMANTIC_QUERIES
from encoder_interview import (
    sparse_features,sparse_reference_vectors,
    sparse_sim,choose_nearest,
)
from native_careers import native_rule


class SilentSemanticSensorTests(unittest.TestCase):
    def test_frozen_queries_separate_from_reference_texts_and_balance(self):
        self.assertEqual(len(CASES),36)
        self.assertEqual(len(SEMANTIC_QUERIES),24)
        self.assertEqual(len({c.id for c in SEMANTIC_QUERIES}),24)
        self.assertEqual(len({c.note for c in SEMANTIC_QUERIES}),24)
        self.assertTrue(all(len([c for c in SEMANTIC_QUERIES
                        if c.job==j.id])==8 for j in JOBS))
        self.assertFalse(set(c.id for c in CASES)&
                         set(c.id for c in SEMANTIC_QUERIES))
        self.assertTrue(all(c.note not in set(x.note for x in CASES)
                            for c in SEMANTIC_QUERIES))

    def test_novel_synthetic_paraphrases_expose_ruleblindspots(self):
        cases=SEMANTIC_QUERIES
        status=next(j for j in JOBS if j.id=="STATUS_TRIAGE")
        self.assertNotEqual(native_rule(status,cases[0].note),cases[0].gold)
        self.assertNotEqual(native_rule(status,cases[2].note),cases[2].gold)

    def test_tfidf_is_a_real_language_aware_baseline_with_same_references(self):
        refs=["the hall is available","the venue denied our request"]
        queries=["the hall is available","they denied our request"]
        a,b=sparse_reference_vectors(refs,queries)
        self.assertEqual(len(a),2)
        self.assertEqual(len(b),2)
        self.assertGreater(sparse_sim(a[0],b[0]),sparse_sim(a[1],b[0]))

    def test_zero_similarity_still_has_deterministic_refusal_safe_fallback(self):
        self.assertEqual(choose_nearest([0.,0.],["A","B"],k=1),"A")
        with self.assertRaises(ValueError):
            choose_nearest([],[],k=1)

    def test_gold_is_only_separate_evaluation_field(self):
        for q in SEMANTIC_QUERIES:
            job=next(j for j in JOBS if j.id==q.job)
            self.assertIn(q.gold,job.labels)
            self.assertTrue(q.note)
            self.assertNotIn("TEST_ID=",q.note)
            self.assertNotIn("@",q.note)


if __name__=="__main__":
    unittest.main()
