"""LLM-004: falsification-oriented tests of source-bound reason hyperedges."""
import copy,json,unittest
from error_dividend import Owner,DEV,HELDOUT,INPUTS,outputs,accuracy
from hypermap import (ReasonHypermap,LENSES,SCHEMA,numbered,decision_gain,
                      bayes_accuracy,grade,canonical)
from free_graph_adapter import packet_from_hypermap,record_id,KIND,VERBS

class HypermapTests(unittest.TestCase):
    def make(self,seed=DEV[0],mode="truthful"):
        owner=Owner(seed,mode)
        return owner,ReasonHypermap(owner)
    def fire(self,seed=DEV[0],mode="truthful",policy="challenge_favorite"):
        owner,m=self.make(seed,mode)
        p=m.choose_test(policy,allow_costly=True)
        self.assertIsNotNone(p)
        before=list(m.weights)
        event=m.resolve(owner,p)
        return owner,m,p,event,before
    def test_01_source_contract_and_all_hypotheses(self):
        owner,m=self.make()
        self.assertEqual(len(m.hypotheses),8)
        self.assertEqual(len(m.sources),2)
        self.assertAlmostEqual(sum(m.weights),1)
    def test_02_hypothesis_prediction_is_pencil(self):
        _,m=self.make();p=m.choose_test()
        self.assertEqual(m.nodes[m.active["prediction"]]["status"],"proposed")
        self.assertNotIn("receipt",m.nodes[m.active["prediction"]]["kind"])
        self.assertEqual(m.events,[])
    def test_03_actual_simulated_receipt_is_called_once(self):
        o,m,p,e,_=self.fire()
        self.assertEqual(len(o.used),1)
        self.assertEqual(len(m.queries),1)
        self.assertEqual(e["response_kind"],"SOURCE_REPORT")
        self.assertTrue(e["independent"])
    def test_04_test_event_is_multiterminal(self):
        o,m,p,e,_=self.fire()
        link=m.edges[e["hyperedge"]]
        self.assertGreaterEqual(len(link["tails"]),3)
        self.assertGreaterEqual(len(link["heads"]),2)
        self.assertTrue(all(k in m.nodes for k in link["tails"]+link["heads"]))
    def test_05_no_feedback_is_hold_with_no_update(self):
        o,m,p,e,before=self.fire(mode="no_feedback")
        self.assertFalse(e["independent"])
        self.assertEqual(before,m.weights)
        self.assertEqual(e["response_kind"],"HOLD_NO_FEEDBACK")
        self.assertIsNone(e["reported_value"])
    def test_06_echo_root_cannot_create_another_source(self):
        o,m,p,e,before=self.fire(mode="echo_origin")
        self.assertFalse(e["independent"])
        self.assertEqual(len(m.sources),2)
        self.assertEqual(before,m.weights)
        self.assertEqual(e["response_kind"],"ECHO_ONLY")
    def test_07_graph_does_not_contain_hidden_truth(self):
        owner,m,p,e,before=self.fire()
        public=m.public_graph()
        self.assertTrue(public["owner_hidden_truth_excluded"])
        self.assertFalse(any("hidden_owner_rule" in str(n) for n in public["nodes"].values()))
        self.assertNotIn("truth_program_index",canonical(public))
        self.assertEqual(public["authority"],"none")
    def test_08_separate_grader_adds_trustworthy_truth(self):
        o,m,p,e,before=self.fire()
        score=grade(o,(before,m.weights),e)
        self.assertIn("accuracy_gain",score)
        self.assertTrue(score["hidden_owner_used_only_in_grader"])
        self.assertNotIn("accuracy_gain",m.events[-1])
    def test_09_provisional_wrong_not_automatically_paid(self):
        saw_wrong=False
        for seed in DEV:
            o,m,p,e,before=self.fire(seed=seed)
            s=grade(o,(before,m.weights),e)
            if s["actual_wrong_provisional"]:
                saw_wrong=True
                self.assertEqual(s["wrong_helpful_net"],s["net_gain"]>0)
        self.assertTrue(saw_wrong)
    def test_10_correct_prediction_can_still_inform(self):
        saw=False
        for seed in DEV:
            o,m,p,e,before=self.fire(seed=seed)
            s=grade(o,(before,m.weights),e)
            if not s["actual_wrong_provisional"] and s["accuracy_gain"]>0:
                saw=True;break
        self.assertTrue(saw)
    def test_11_wrong_can_cost_resources_with_no_gain(self):
        saw=False
        for seed in DEV:
            o,m,p,e,before=self.fire(seed=seed)
            s=grade(o,(before,m.weights),e)
            if s["actual_wrong_provisional"] and s["net_gain"]<=0:
                saw=True;break
        self.assertTrue(saw)
    def test_12_reported_contradiction_separate_from_truth(self):
        for seed in DEV:
            o,m,p,e,before=self.fire(seed=seed,mode="noise20")
            if e["independent"] and e["reported_value"]!=o.truth(tuple(e["x"])):
                s=grade(o,(before,m.weights),e)
                self.assertFalse(s["verified_counterexample"])
                return
        self.fail("No noisy false authored report in development seeds")
    def test_13_owner_mismatch_does_not_touch_state(self):
        o,m=self.make()
        p=m.choose_test()
        before=m.snapshot()
        with self.assertRaisesRegex(ValueError,"WRONG_SIMULATED_OWNER"):
            m.resolve(Owner(DEV[1],"truthful"),p)
        self.assertEqual(before,m.snapshot())
    def test_14_no_double_outstanding_proposal(self):
        o,m=self.make()
        m.choose_test()
        with self.assertRaisesRegex(ValueError,"ONE_OUTSTANDING_TEST"):m.choose_test()
    def test_15_replay_fails_closed(self):
        o,m,p,e,before=self.fire()
        with self.assertRaisesRegex(ValueError,"NO_ACTIVE_PROPOSAL"):m.resolve(o,p)
    def test_16_snapshots_are_immutable_values(self):
        o,m=self.make()
        prior=copy.deepcopy(m.snapshots[0])
        p=m.choose_test();m.resolve(o,p)
        self.assertEqual(m.snapshots[0],prior)
        self.assertNotEqual(m.snapshots[1]["state_id"],prior["state_id"])
    def test_17_imagined_forks_do_not_mutate_records(self):
        o,m=self.make()
        p=m.choose_test();before=m.public_graph()
        branches=m.imagined_outcomes(p)
        self.assertEqual(len(branches),2)
        self.assertAlmostEqual(sum(x["hypothetical_probability"] for x in branches),1,places=5)
        self.assertEqual(m.public_graph(),before)
        self.assertTrue(all("PENCIL_ONLY" in x["status"] for x in branches))
    def test_18_stale_imagined_fork_rejected(self):
        o,m,p,e,before=self.fire()
        with self.assertRaisesRegex(ValueError,"PROPOSAL_NOT_ACTIVE"):m.imagined_outcomes(p)
    def test_19_different_lens_preserves_immutable_identity(self):
        o,m,p,e,before=self.fire()
        res=[m.view(lens) for lens in LENSES]
        self.assertEqual(len({x["immutable_identity"] for x in res}),1)
        self.assertTrue(all(x["authority"]=="none" for x in res))
        self.assertTrue(all(x["source_roots"]==res[0]["source_roots"] for x in res))
    def test_20_lens_changes_navigation_not_evidence(self):
        o,m,p,e,before=self.fire()
        a,b=m.view("epistemic"),m.view("causal")
        self.assertNotEqual(a["selected_hyperedge_ids"],b["selected_hyperedge_ids"])
        self.assertEqual(a["nodes"],b["nodes"])
    def test_21_unknown_lens_refused(self):
        o,m=self.make()
        with self.assertRaisesRegex(ValueError,"UNKNOWN_LENS"):m.view("make-real")
    def test_22_free_graph_is_canonical_content_addressed(self):
        o,m,p,e,before=self.fire()
        packet=packet_from_hypermap(m)
        self.assertEqual(packet["schema"],"free-graph.packet/v0")
        self.assertEqual(packet["packet_id"],record_id("fgp",{k:v for k,v in packet.items() if k!="packet_id"}))
        for kind,prefix in (("sources","fgs"),("nodes","fgn"),("links","fgl")):
            self.assertTrue(all(x["id"]==record_id(prefix,x) for x in packet[kind]))
    def test_23_all_portable_links_use_only_existing_5_verbs(self):
        o,m,p,e,before=self.fire()
        packet=packet_from_hypermap(m)
        self.assertTrue(all(l["verb"] in VERBS for l in packet["links"]))
        self.assertFalse(any(l["verb"]=="constitutes" for l in packet["links"]))
        self.assertTrue(all(l["authority"]=="none" for l in packet["links"]))
    def test_24_hyperedges_reified_with_portable_membership(self):
        o,m,p,e,before=self.fire()
        packet=packet_from_hypermap(m)
        hyper=[n for n in packet["nodes"] if n.get("extensions",{}).get("reified_hyperedge")]
        self.assertEqual(len(hyper),len(m.edges))
        self.assertGreater(len(hyper),0)
        self.assertTrue(any(l["qualifier"]=="hyperedge-tail" for l in packet["links"]))
        self.assertTrue(any(l["qualifier"]=="hyperedge-head" for l in packet["links"]))
    def test_25_bearing_has_real_simulator_specimen_source(self):
        o,m,p,e,before=self.fire()
        packet=packet_from_hypermap(m)
        byid={s["id"]:s for s in packet["sources"]}
        for link in (l for l in packet["links"] if l["verb"]=="bears-on"):
            self.assertTrue(any(byid[s]["source_class"]=="specimen-receipt"
                                for s in link["source_ids"]))
            self.assertIn(link["bearing"],("supports","refuses","unresolved"))
    def test_26_active_unverified_test_not_exported(self):
        o,m=self.make();m.choose_test()
        with self.assertRaisesRegex(ValueError,"PROPOSED_TEST_NOT_YET_RESOLVED"):
            packet_from_hypermap(m)
    def test_27_no_feedback_packet_does_not_bear_on_claims(self):
        o,m,p,e,before=self.fire(mode="no_feedback")
        packet=packet_from_hypermap(m)
        self.assertFalse(any(l["verb"]=="bears-on" for l in packet["links"]))
        self.assertEqual(len(packet["sources"]),2)
    def test_28_echo_packet_does_not_bear_on_claims(self):
        o,m,p,e,before=self.fire(mode="echo_origin")
        self.assertFalse(any(l["verb"]=="bears-on" for l in packet_from_hypermap(m)["links"]))
    def test_29_decision_gain_nonnegative_information_prior(self):
        o,m=self.make()
        self.assertTrue(all(decision_gain(m.weights,x)>=-1e-9 for x in INPUTS))
    def test_30_decision_policy_budget_stops_when_not_worth_cost(self):
        o,m=self.make()
        p=m.choose_test("decision_gain")
        if p is not None:
            self.assertGreater(decision_gain(m.weights,p.x),m.cost)
    def test_31_missing_owner_cannot_be_substituted(self):
        o,m=self.make()
        p=m.choose_test()
        with self.assertRaisesRegex(ValueError,"WRONG_SIMULATED_OWNER"):m.resolve(None,p)
    def test_32_wrong_graph_type_fails_before_export(self):
        with self.assertRaisesRegex(ValueError,"NOT_REASON_HYPERMAP"):
            packet_from_hypermap({"fake":True})
    def test_33_all_links_refer_to_real_endpoints(self):
        o,m,p,e,before=self.fire()
        packet=packet_from_hypermap(m)
        ids={n["id"] for n in packet["nodes"]}
        self.assertTrue(all(l["from"] in ids and l["to"] in ids for l in packet["links"]))
    def test_34_source_root_not_falsely_doubled(self):
        o,m,p,e,before=self.fire()
        self.assertEqual(len(m.sources),3)
        self.assertEqual(len({s["root"] for s in m.sources.values()}),3)
    def test_36_cost_stopped_information_gain_selects_same_initial_test_as_ig(self):
        o,m=self.make()
        expected=m.choose_test("classical_ig")
        o2,m2=self.make()
        actual=m2.choose_test("classical_ig_stop",allow_costly=True)
        self.assertEqual(expected.x,actual.x)
    def test_37_stopped_baseline_uses_same_cost_threshold(self):
        o,m=self.make()
        p=m.choose_test("classical_ig_stop")
        if p is not None:
            self.assertGreater(decision_gain(m.weights,p.x),m.cost)
    def test_35_zero_probe_retains_initial_sourced_memory(self):
        o,m=self.make()
        self.assertIsNone(m.choose_test("no_probe"))
        self.assertEqual(m.events,[])
        self.assertEqual(len(m.snapshots),1)

if __name__=="__main__":unittest.main()
