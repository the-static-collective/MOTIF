"""COGNITION-004 native-source, structural-transfer and owner-safety falsifiers."""
import json
import unittest
from copy import deepcopy

from analogy import (
    DEV_SEEDS,TEST_SEEDS,REGIMES,POLICIES,FIXES,UNSEEN_FIX,MAX_PROBES,
    RELATIONS,Owner,STATE,AppState,baseline,edit_cost,candidates,
    free_graph_proposal,_native_graph,native_motif_test_affordances,
    understory_envelope,validate_understory_owner,run_case,benchmark,seal
)


class UnwrittenAnalogyTests(unittest.TestCase):
    def test_frozen_seed_and_methods(self):
        self.assertEqual(len(TEST_SEEDS),32)
        self.assertTrue(set(TEST_SEEDS).isdisjoint(DEV_SEEDS))
        self.assertEqual(len(REGIMES),6)
        self.assertEqual(len(POLICIES),4)

    def test_all_case_nouns_are_disjoint(self):
        for regime in REGIMES:
            sources,event,_=baseline(DEV_SEEDS[0],regime)
            prior={x for r in sources for x in r["entities"]}
            self.assertFalse(prior.intersection(event["entities"]))
            self.assertFalse(event["has_explicit_memory_search_request"])

    def test_direction_and_relation_type_matter(self):
        a=RELATIONS[0]
        self.assertEqual(edit_cost(a,a)[0],0)
        reversed_direction=[(b,a,r) for a,b,r in a]
        self.assertGreater(edit_cost(a,reversed_direction)[0],0)
        modified=[(x,y,"wrong-rel" if i==1 else r) for i,(x,y,r) in enumerate(a)]
        self.assertGreater(edit_cost(a,modified)[0],0)

    def test_permuted_domain_has_witnessed_structural_analogy(self):
        for seed in DEV_SEEDS:
            lib,event,p=baseline(seed,"renamed_permuted")
            rows,_=candidates(lib,event)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["distance"],0)
            self.assertEqual(rows[0]["index"],p)
            self.assertTrue(rows[0]["independent"])
            self.assertEqual(rows[0]["status"],"PENCIL_HYPOTHETICAL_TRANSFER")

    def test_partial_edge_has_one_edit_not_a_claim_of_truth(self):
        lib,event,p=baseline(DEV_SEEDS[0],"partial_observation")
        rows,_=candidates(lib,event)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["distance"],1)
        self.assertEqual(rows[0]["index"],p)
        exact,_=candidates(lib,event,strict=True)
        self.assertEqual(exact,[])

    def test_false_friend_requires_test_and_correctly_fails(self):
        for policy in POLICIES[:3]:
            r=run_case(DEV_SEEDS[0],"false_friend",policy,full=True)
            self.assertFalse(r["verified_success"])
            if policy=="classical_exact_iso":
                self.assertEqual(r["owner_tests"],0)  # exact matching safely abstains
            else:
                self.assertGreater(r["owner_tests"],0)  # approximate false friend is probed
            self.assertEqual(r["owner_repairs"],0)
            self.assertEqual(r["unverified_repairs"],0)
            self.assertTrue(all(x["owner_test_receipt"]["positive"] is False
                                for x in r["detail"]))

    def test_echoed_witness_root_refused(self):
        for policy in POLICIES[:3]:
            r=run_case(DEV_SEEDS[0],"echo_source",policy)
            self.assertEqual(r["source_echo_rejections"],1)
            self.assertEqual(r["owner_tests"],0)
            self.assertFalse(r["verified_success"])

    def test_unknown_structure_abstains_not_guess(self):
        for policy in POLICIES[:3]:
            r=run_case(DEV_SEEDS[0],"unfamiliar_structure",policy)
            self.assertEqual(r["credible_candidates"],0)
            self.assertEqual(r["owner_tests"],0)
            self.assertFalse(r["verified_success"])

    def test_strong_graph_edit_method_same_outcomes_and_budget(self):
        for regime in REGIMES:
            m=run_case(DEV_SEEDS[0],regime,"motif_council")
            c=run_case(DEV_SEEDS[0],regime,"classical_graph_edit")
            self.assertEqual(m["verified_success"],c["verified_success"])
            self.assertEqual(m["owner_tests"],c["owner_tests"])
            self.assertEqual(m["trigger_comparison_ops"],c["trigger_comparison_ops"])
            self.assertEqual(m["idle_index_entries"],c["idle_index_entries"])

    def test_owner_requires_positive_test_before_any_repair(self):
        owner=Owner(FIXES[0])
        with self.assertRaises(ValueError):
            owner.repair(FIXES[0])
        self.assertFalse(owner.test(FIXES[1])["positive"])
        with self.assertRaises(ValueError):
            owner.repair(FIXES[1])
        self.assertTrue(owner.test(FIXES[0])["positive"])
        self.assertTrue(owner.repair(FIXES[0])["independently_verified"])
        with self.assertRaises(RuntimeError):
            owner.test(FIXES[2])
        self.assertEqual(len(owner.receipts),3)

    def test_real_native_free_graph_not_constituting(self):
        lib,event,pattern=baseline(DEV_SEEDS[0],"renamed_permuted")
        row=candidates(lib,event)[0][0]
        packet,neighbors=free_graph_proposal(lib[pattern],event,row)
        _,_,validate,_=_native_graph()
        self.assertEqual(validate(packet),[])
        self.assertEqual(validate(neighbors),[])
        self.assertEqual(packet["task_world_cut"]["status"],"unresolved")
        self.assertTrue(all(l["verb"]=="connects" and l["status"]=="unresolved"
                            and l["authority"]=="none" for l in packet["links"]))
        self.assertFalse("expected_action" in json.dumps(packet))

    def test_graph_tamper_rejected(self):
        lib,event,p=baseline(DEV_SEEDS[0],"renamed_permuted")
        candidate=candidates(lib,event)[0][0]
        packet,_=free_graph_proposal(lib[p],event,candidate)
        packet["links"][0]["authority"]="owner-local"
        self.assertTrue(_native_graph()[2](packet))

    def test_original_motif003_affordances_execute_on_questions(self):
        lib,event,_=baseline(DEV_SEEDS[0],"renamed_permuted")
        possible=candidates(lib,event)[0]
        self.assertEqual(native_motif_test_affordances(possible),1)
        self.assertEqual(native_motif_test_affordances([]),0)

    def test_private_understory_owner_hold_and_read_only_structure(self):
        lib,event,p=baseline(DEV_SEEDS[0],"renamed_permuted")
        envelope=understory_envelope(lib[p],event)
        self.assertEqual([r["family"] for r in envelope["records"]],
                         ["contact","contact","association","activation"])
        self.assertEqual(envelope["records"][-1]["trace_refs"],
                         [envelope["records"][2]["id"]])
        self.assertEqual(envelope["records"][2]["status"],"unresolved")
        self.assertFalse(validate_understory_owner(envelope,None)["validated"])
        self.assertFalse(any(r["family"]=="attention" for r in envelope["records"]))

    def test_no_user_permission_means_no_idle_contemplation(self):
        deny=AppState(False,False,0,True,11,False,88.,.9,"critical")
        r=run_case(DEV_SEEDS[0],"isomorphic","motif_council",state=deny)
        self.assertFalse(r["admitted_idle"])
        self.assertEqual(r["idle_index_entries"],0)
        self.assertEqual(r["native_motif003_test_affordances"],0)
        self.assertFalse(r["native_private_understory"]["validated"])
        # Task-directed conventional traversal may still run, not sleep work.
        self.assertTrue(r["verified_success"])

    def test_external_effects_are_always_zero(self):
        for policy in POLICIES:
            r=run_case(DEV_SEEDS[1],"renamed_permuted",policy)
            self.assertEqual(r["real_external_actions"],0)
            self.assertEqual(r["model_calls"],0)
            self.assertEqual(r["target_entity_overlap"],0)
            self.assertFalse(r["personal_data_processed"])
            self.assertFalse(r["app_deployed"])
            self.assertTrue(r["historical_archive_unchanged"])
            self.assertEqual(r["seal"],seal({k:v for k,v in r.items() if k!="seal"}))
            self.assertEqual(len(r["owner_receipts"]),r["owner_tests"]+r["owner_repairs"])
            for rec in r["owner_receipts"]:
                self.assertEqual(rec["seal"],seal({k:v for k,v in rec.items() if k!="seal"}))

    def test_dev_reproducibility_and_full_96(self):
        a=benchmark("development",full=False)
        b=benchmark("development",full=False)
        self.assertEqual(a["cases"],96)
        self.assertEqual(a["seal"],b["seal"])
        self.assertEqual(len(a["paired"]),24)
        self.assertTrue(all(x["motif_minus_strong_classical_success"]==0
                            and x["motif_minus_strong_classical_tests"]==0
                            for x in a["paired"]))


if __name__=="__main__":
    unittest.main()
