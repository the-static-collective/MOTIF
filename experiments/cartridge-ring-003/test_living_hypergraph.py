"""Live inventory + multi-use planner + optional native source benchmark integration."""
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'cartridge-ring-001'))

import living_ring


def fetched(page,size):
    rows=[{"name":"main","commit":{"sha":"a"*40}},
          {"name":"experiment/future-source","commit":{"sha":"b"*40}}]
    return rows[(page-1)*size:page*size]


class LivingHypergraphTests(unittest.TestCase):
    def test_hypergraph_plan_is_run_without_any_native_model(self):
        with patch.object(living_ring.triad,"run",
                          side_effect=AssertionError("no execution approved")):
            r=living_ring.session(
                fetch_page=fetched,
                hyper_goals=(("interpretation-objection-bridge",12),),
                hyper_budget=4,observed_at="FIXTURE")
        plan=r["hypergraph_plan"]
        self.assertEqual(plan["selected"]["selected"],
                         ["reason.proof-objection","thought.language-dev"])
        self.assertEqual(plan["live_source_only_branch_count"],1)
        self.assertIsNone(r["hypergraph_native_evidence"])
        self.assertEqual(r["authority"],"NONE")

    def test_unknown_goals_never_invent_a_new_method(self):
        r=living_ring.session(fetch_page=fetched,
            hyper_goals=(("some-unknown-problem",99),),observed_at="FIXTURE")
        self.assertEqual(r["hypergraph_plan"]["selected"]["selected"],[])
        self.assertFalse(r["hypergraph_plan"]["all_goals_covered"])

    def test_opt_in_is_required_before_native_method_execution(self):
        with self.assertRaisesRegex(living_ring.hypergraph.HOLD,"requires"):
            living_ring.session(fetch_page=fetched,
                hyper_goals=(("proof-review",7),),
                execute_hyper_selected=True,observed_at="FIXTURE")

    def test_native_executes_only_hypergraph_selected_methods(self):
        from test_receipt_bridge import native_fixture
        def mock_run(chosen,*,repo_root):
            self.assertEqual(chosen,("reason.proof-objection",))
            orig=native_fixture()
            orig["selected"]=list(chosen)
            orig["results"]=[x for x in orig["results"] if x["adapter"] in chosen]
            from test_receipt_bridge import digest
            orig["receipt_sha256"]=digest(orig)
            return orig
        with patch.object(living_ring.triad,"run",side_effect=mock_run):
            r=living_ring.session(fetch_page=fetched,
                 hyper_goals=(("proof-review",7),),hyper_budget=3,
                 execute_hyper_selected=True,native=True,
                 observed_at="FIXTURE")
        self.assertEqual(r["hypergraph_plan"]["selected"]["selected"],
                         ["reason.proof-objection"])
        self.assertEqual(len(r["hypergraph_native_evidence"]["evidence_vertices"]),1)
        self.assertEqual(r["hypergraph_native_evidence"]["admitted_new_affordance_edges"],0)


if __name__=="__main__":
    unittest.main()
