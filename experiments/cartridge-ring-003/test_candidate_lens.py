"""A branch can suggest many applications, never grant automatic authority."""
import unittest
from pathlib import Path
from unittest.mock import patch

import candidate_lens
import discovery
import hypergraph


def census():
    return discovery.snapshot(discovery._validate([
        {"name":"main","commit":{"sha":"a"*40}},
        {"name":"experiment/possible-new","commit":{"sha":"b"*40}},
    ]),observed_at="TEST")


class CandidateLensTests(unittest.TestCase):
    def test_one_source_can_have_multiple_uses_from_two_witnessed_terms(self):
        def reader(catalog,ref,term,*,repo_root,path_prefix,max_hits):
            self.assertEqual(ref,"experiment/possible-new")
            self.assertEqual(max_hits,5)
            return {
                "status":"BOUNDED_COMPLETE",
                "matches":[{"path":"experiments/new/DESIGN.md",
                            "line":7 if term=="graph" else 13,
                            "excerpt_untrusted_document_text":term+" synthetic sample"}]
            }
        with patch.object(candidate_lens.source_reader,"inspect",side_effect=reader):
            r=candidate_lens.analyze(census(),"experiment/possible-new",
                                     repo_root=Path.cwd(),terms=("graph","question"))
        self.assertEqual(len(r["proposed_uses"]),4)
        self.assertEqual(len(r["hyperedges"]),2)
        self.assertTrue(all(e["tails"][0].startswith("source:") for e in r["hyperedges"]))
        self.assertTrue(all(len(e["tails"])==2 and len(e["heads"])==2
                            for e in r["hyperedges"]))
        self.assertTrue(all(not e["admitted_for_execution"] for e in r["hyperedges"]))
        self.assertFalse(r["branch_code_executed"])
        self.assertEqual(r["authority"],"NONE")

    def test_missing_keyword_cannot_mean_missing_real_capability(self):
        with patch.object(candidate_lens.source_reader,"inspect",return_value={
                "status":"BOUNDED_COMPLETE","matches":[]}):
            r=candidate_lens.analyze(census(),"experiment/possible-new",
                                     repo_root=Path.cwd(),terms=("proof",))
        self.assertEqual(r["proposed_uses"],[])
        self.assertTrue(r["unsearched_terms_are_not_absent_capabilities"])

    def test_partial_source_scan_preserves_scope_uncertainty(self):
        with patch.object(candidate_lens.source_reader,"inspect",return_value={
                "status":"PARTIAL","matches":[{"path":"experiments/a.md","line":1,
                                        "excerpt_untrusted_document_text":"test"}]}):
            r=candidate_lens.analyze(census(),"experiment/possible-new",
                                     repo_root=Path.cwd(),terms=("test",))
        self.assertEqual(r["partial_term_searches"],["test"])
        self.assertFalse(r["hyperedges"][0]["verified_use"])

    def test_unknown_term_cannot_execute_command_or_create_source_fact(self):
        with self.assertRaisesRegex(hypergraph.HOLD,"analyst vocabulary"):
            candidate_lens.analyze(census(),"experiment/possible-new",
                                   repo_root=Path.cwd(),terms=("__import__('os')",))
        with self.assertRaisesRegex(hypergraph.HOLD,"analyst vocabulary"):
            candidate_lens.analyze(census(),"experiment/possible-new",
                                   repo_root=Path.cwd(),terms=("proof","proof"))

    def test_candidate_does_not_alter_native_registry(self):
        before=set(candidate_lens.hypergraph.triad.BY_ID)
        with patch.object(candidate_lens.source_reader,"inspect",return_value={
                "status":"BOUNDED_COMPLETE","matches":[]}):
            candidate_lens.analyze(census(),"experiment/possible-new",
                                   repo_root=Path.cwd(),terms=("model",))
        self.assertEqual(set(candidate_lens.hypergraph.triad.BY_ID),before)


if __name__=="__main__":
    unittest.main()
