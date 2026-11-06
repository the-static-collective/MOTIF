"""RING-003: many-to-many hyperedges, subset synergy and abstention tests."""
import json
import unittest
from dataclasses import replace
from itertools import combinations

import hypergraph as h
import discovery


class HypergraphTests(unittest.TestCase):
    def setUp(self):
        self.g=h.current_graph()

    def test_one_method_can_satisfy_multiple_distinct_uses(self):
        t=h.Task("proof-multi-use",(("proof-review",5),
                                    ("question-proposal",5)),3,3)
        r=self.g.solve(t)
        self.assertEqual(r["selected"]["selected"],["reason.proof-objection"])
        self.assertEqual(len(r["selected"]["covered"]),2)
        self.assertEqual(r["selected"]["declared_benefit"],10)
        self.assertTrue(r["all_goals_covered"])

    def test_hyperedge_can_have_three_tails_and_two_heads(self):
        edges=self.g.audit()["hyperedges"]
        a=next(e for e in edges if e["id"]=="all-three.joint-bridge")
        self.assertEqual(len(a["tails"]),3)
        self.assertEqual(len(a["heads"]),2)
        self.assertEqual(a["basis"],h.VERDICT)

    def test_individual_methods_do_not_forge_joint_capabilities(self):
        task=h.example_tasks()[0]
        no=self.g.evaluate(("reason.proof-objection",),task)
        self.assertEqual(no["covered"],[])
        self.assertIn("interpretation-objection-bridge",no["missing"])
        both=self.g.evaluate(("reason.proof-objection","thought.language-dev"),task)
        self.assertEqual(both["covered"],["interpretation-objection-bridge"])

    def test_complementarity_beats_a_greedy_single_step_on_constructed_example(self):
        task=h.example_tasks()[0]
        actual=self.g.solve(task)
        self.assertEqual(actual["selected"]["selected"],
                         ["reason.proof-objection","thought.language-dev"])
        self.assertEqual(actual["baselines"]["greedy_single_addition"]["selected"],[])
        self.assertEqual(actual["selected"]["declared_net_utility"],8)
        self.assertEqual(actual["baselines"]["greedy_single_addition"]["declared_net_utility"],0)
        self.assertFalse(actual["joint_task_success_measured"])

    def test_second_pair_reuses_proof_for_different_application(self):
        task=h.example_tasks()[1]
        actual=self.g.solve(task)
        self.assertEqual(actual["selected"]["selected"],
                         ["geometry.procedure-repair","reason.proof-objection"])
        self.assertEqual(actual["selected"]["declared_net_utility"],8)

    def test_all_three_only_when_joint_goal_requested(self):
        t=h.example_tasks()[3]
        r=self.g.solve(t)
        self.assertEqual(len(r["selected"]["selected"]),3)
        self.assertEqual(r["selected"]["covered"],["cross-instrument-evidence-review"])
        self.assertTrue(r["all_goals_covered"])

    def test_skip_unused_modules_is_better_than_always_all_under_assumed_costs(self):
        t=h.example_tasks()[4]
        r=self.g.solve(t)
        self.assertEqual(r["selected"]["selected"],["thought.language-dev"])
        self.assertGreater(r["selected"]["declared_net_utility"],
                           r["baselines"]["always_all_if_budgeted"]["declared_net_utility"])

    def test_crossworld_tension_deducted_only_when_both_methods_used(self):
        t=h.Task("avoid-unchecked-mixing",(
            ("measurement-description-check",6),),6,3)
        pair=self.g.evaluate(("geometry.procedure-repair","thought.language-dev"),t)
        self.assertIn("geometry-language.unsupported-crossworld",
                      pair["triggered_hyperedges"])
        self.assertEqual(pair["declared_tension_penalty"],3)
        self.assertEqual(pair["declared_net_utility"],-1)
        self.assertEqual(self.g.solve(t)["selected"]["selected"],[])
        # The "tension" is a precaution hypothesis, not measured harm.

    def test_unknown_goal_causes_abstention_not_invented_relation(self):
        r=self.g.solve(h.example_tasks()[-1])
        self.assertEqual(r["selected"]["selected"],[])
        self.assertEqual(r["selected"]["covered"],[])
        self.assertEqual(r["selected"]["missing"],["unseen-goal"])
        self.assertFalse(r["all_goals_covered"])

    def test_no_double_count_when_distinct_edges_propose_same_affordance(self):
        methods=self.g.methods
        edges=self.g.edges + (h.Hyperedge("another-proof",(
            "reason.proof-objection",),("proof-review",)),)
        g=h.Hypergraph(methods,edges)
        t=h.Task("single-credit",(("proof-review",10),),3)
        r=g.evaluate(("reason.proof-objection",),t)
        self.assertEqual(r["declared_benefit"],10)

    def test_budget_keeps_joint_target_uncovered(self):
        t=h.Task("cannot-buy-the-pair",(
            ("interpretation-objection-bridge",12),),3,2)
        r=self.g.solve(t)
        self.assertEqual(r["selected"]["selected"],[])
        self.assertFalse(r["all_goals_covered"])

    def test_unsupported_or_duplicate_methods_are_hold(self):
        t=h.example_tasks()[0]
        with self.assertRaisesRegex(h.HOLD,"Uninstalled"):
            self.g.evaluate(("fake.method",),t)
        with self.assertRaisesRegex(h.HOLD,"repeated"):
            self.g.evaluate(("reason.proof-objection","reason.proof-objection"),t)

    def test_source_identity_never_comes_from_a_branch_name(self):
        g=self.g.audit()
        self.assertEqual(len(g["vertices"]),3+len({
            head for x in self.g.edges if x.kind=="AFFORDANCE" for head in x.heads
        }))
        self.assertTrue(all("source_commit" in x for x in g["vertices"]
                            if x["type"]=="EXECUTABLE_METHOD"))
        self.assertEqual(g["authority"],"NONE")

    def test_future_branches_become_source_only_vertices_no_affordance(self):
        seeds=[
            {"name":"main","commit":{"sha":"a"*40}},
            {"name":"experiment/brand-new-001","commit":{"sha":"b"*40}},
            {"name":"experiment/brand-new-002","commit":{"sha":"c"*40}},
        ]
        pairs=discovery._validate(seeds)
        cat=discovery.snapshot(pairs,observed_at="TEST")
        result=h.add_discovered_sources(self.g,cat)
        self.assertEqual(result["source_candidate_count"],2)
        self.assertEqual(len(result["indexed_source_candidates"]),2)
        self.assertTrue(all(x["admitted_reasoning_capabilities"]==[]
                            for x in result["indexed_source_candidates"]))
        self.assertEqual(self.g.solve(h.example_tasks()[0])["selected"]["selected"],
                         ["reason.proof-objection","thought.language-dev"])

    def test_fake_automatic_promotion_fails_closed(self):
        c=discovery.snapshot(discovery._validate([
            {"name":"main","commit":{"sha":"a"*40}},
            {"name":"experiment/danger","commit":{"sha":"b"*40}},
        ]),observed_at="TEST")
        c["passports"][0]["executable"]=True
        with self.assertRaisesRegex(h.HOLD,"Unsafe"):
            h.add_discovered_sources(self.g,c)

    def test_exact_deterministic_receipt(self):
        t=h.example_tasks()[0]
        self.assertEqual(self.g.solve(t),self.g.solve(t))
        self.assertEqual(len(self.g.solve(t)["receipt_sha256"]),64)

    def test_malformed_edges_and_undeclared_permissions_rejected(self):
        m=self.g.methods
        with self.assertRaisesRegex(h.HOLD,"Bad or duplicate hyperedge"):
            h.Hypergraph(m,(h.Hyperedge("fake",("future.untrusted",),("email-sent",)),))
        with self.assertRaisesRegex(h.HOLD,"Bad or duplicate hyperedge"):
            h.Hypergraph(m,(h.Hyperedge("fake",("reason.proof-objection",),
                                               ("email-sent",),basis="VERIFIED_REAL"),))

    def test_stated_upper_bounds_are_enforced(self):
        with self.assertRaises(h.HOLD):
            self.g.solve(h.Task("too-many",(("proof-review",1),),3,100))
        with self.assertRaises(h.HOLD):
            self.g.solve(h.Task("bad-weight",(("proof-review",0),),3))
        with self.assertRaises(h.HOLD):
            self.g.solve(h.Task("duplicate-goal",(("proof-review",2),
                                                  ("proof-review",3)),3))


if __name__=="__main__":
    unittest.main()
