"""Bounded grammar invention: independent corrections and adversarial cases."""
import json
import unittest

from source import (Case,SourceOwner,lessons,heldout,future,
                    INITIAL,HOLDOUT,ACQUISITION,bfs)
from grammar import (HOLD,Grammar,digest,discovery,validate,interpret,
                     pin_source,family_shape,LEVELS)
from receiver import Receiver
from trial import invention,fixed_family_accuracy,cost_model,run


class GrammarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.long=invention("LONG_SHORT")
        cls.bridge=invention("BRIDGE")

    def test_no_preselected_macro_extension_family(self):
        grammar=Grammar()
        self.assertEqual(len(grammar.by_cost[1]),5)
        self.assertEqual(len(grammar.by_cost[3]),20)
        self.assertEqual(len(grammar.by_cost[5]),80)
        self.assertEqual(len(grammar.by_cost[7]),260)
        self.assertEqual(len(grammar.by_cost[9]),542)
        self.assertEqual(len(grammar.by_cost[11]),820)
        self.assertEqual(len(grammar.expressions),1727)
        self.assertEqual(len(pin_source()),40)

    def test_source_two_nonisomorphic_graphs_and_sealed_holdout(self):
        one=Case(31,"LONG_SHORT").graph()
        two=Case(31,"BRIDGE").graph()
        self.assertNotEqual(one[1],two[1])
        self.assertEqual(len(one[1]),5)
        self.assertEqual(len(two[1]),5)
        self.assertEqual(len(INITIAL),5)
        self.assertEqual(len(HOLDOUT),8)
        self.assertTrue(set(INITIAL).isdisjoint(HOLDOUT))
        self.assertEqual(len(ACQUISITION),24)
        for c in heldout("BRIDGE"):
            with self.assertRaises(ValueError):
                SourceOwner("BRIDGE").query(c.mask)

    def test_general_ast_finds_distinct_shapes_9_and_11_nodes(self):
        a=validate(self.long[0])
        b=validate(self.bridge[0])
        self.assertEqual(a["program"]["binary_ast_nodes"],9)
        self.assertEqual(b["program"]["binary_ast_nodes"],11)
        self.assertNotEqual(a["program"]["inferred_typed_macro_shape"],
                            b["program"]["inferred_typed_macro_shape"])
        self.assertFalse(a["program"]["new_fundamental_boolean_operator"])
        self.assertFalse(b["program"]["new_fundamental_boolean_operator"])
        self.assertEqual(a["grammar"],"BINARY_AND_OR_OVER_FIVE_EDGE_VARIABLES")

    def test_rejected_tiers_supply_finite_refutation_certificates(self):
        grammar=Grammar()
        for family,bundle,expected in (
            ("LONG_SHORT",self.long,365),("BRIDGE",self.bridge,907)):
            p=validate(bundle[0])
            labels={x["mask"]:x["reachable"] for x in p["public_observations"]}
            proof=p["rejected_smaller_grammar_tiers"][-1]
            self.assertEqual(proof["candidate_functions_refuted"],expected)
            self.assertEqual(proof,grammar.gaps(proof["max_binary_ast_nodes"],labels))
            self.assertIsNone(grammar.gaps(p["first_verified_complexity"],labels))

    def test_active_cegis_did_not_expose_sealed_holdout(self):
        for _,_,_,owner in (self.long,self.bridge):
            self.assertTrue(all(entry.get("mask") not in HOLDOUT
                                for entry in owner.history))
            self.assertTrue(all(entry["source_world_only"] for entry in owner.history))
            self.assertTrue(owner.calls<=24)
            self.assertEqual(owner.history[-1]["mechanism"],"ACQUISITION_PASS")

    def test_independent_owner_heldout_and_complete_post_synthesis_world(self):
        for raw,_,review,_ in (self.long,self.bridge):
            self.assertEqual(review["heldout_cases"],8)
            self.assertEqual(review["heldout_errors"],0)
            self.assertEqual(review["post_synthesis_acquisition_errors"],0)
            self.assertTrue(review["all_32_feature_states_match"])
            p=validate(raw)
            for mask in range(32):
                self.assertEqual(interpret(p["program"]["ast"],mask),
                                 bfs(Case(mask,p["family"])))

    def test_receiver_refuses_unreviewed_and_wrong_source(self):
        raw=self.bridge[0]
        rec=Receiver(raw)
        with self.assertRaises(HOLD):
            rec.suggest(Case(7,"BRIDGE","quartz"))
        with self.assertRaises(HOLD):
            rec.preview(heldout("LONG_SHORT"))
        with self.assertRaises(HOLD):
            rec.preview(tuple(Case(m,"BRIDGE") for m in INITIAL))
        preview=rec.preview(heldout("BRIDGE"))
        with self.assertRaises(HOLD):
            rec.admit("ADMIT_READ_ONLY","stale")
        with self.assertRaises(HOLD):
            rec.admit("SEND_MESSAGE",preview["review_digest"])
        rec.admit("ADMIT_READ_ONLY",preview["review_digest"])
        with self.assertRaises(HOLD):
            rec.suggest(Case(3,"BRIDGE"))
        self.assertFalse(rec.suggest(Case(3,"BRIDGE","quartz"))["external_execution"])

    def test_premature_grammar_budget_holds(self):
        with self.assertRaises(HOLD):
            discovery("BRIDGE",lessons("BRIDGE"),
                      SourceOwner("BRIDGE"),max_cost=9)
        with self.assertRaises(HOLD):
            discovery("LONG_SHORT",lessons("LONG_SHORT"),
                      SourceOwner("LONG_SHORT",max_queries=0),max_calls=0)
        with self.assertRaises(HOLD):
            discovery("BRIDGE",lessons("BRIDGE"),
                      SourceOwner("BRIDGE",max_queries=1),max_calls=1)

    def test_source_traces_refuse_fake_counterexamples(self):
        class Liar:
            def query(self,mask):
                row=dict(lessons("BRIDGE")[0])
                row["mask"]=mask
                row["reachable"]=True
                return row
            def refute_or_pass(self,signature):
                return {"status":"PASS_ACQUISITION",
                        "does_not_certify_heldout":False}
        with self.assertRaises(HOLD):
            discovery("BRIDGE",lessons("BRIDGE"),Liar())

    def test_source_family_mismatch_and_bogus_mask_refuse(self):
        with self.assertRaises(HOLD):
            discovery("BRIDGE",lessons("LONG_SHORT"),
                      SourceOwner("BRIDGE"))
        with self.assertRaises(ValueError):
            SourceOwner("BRIDGE").query(HOLDOUT[0])
        with self.assertRaises(HOLD):
            interpret(["EVAL","shell"],3)
        with self.assertRaises(HOLD):
            interpret(["VAR",9],3)

    def test_recipient_replays_rehashed_artifact(self):
        original=json.loads(self.bridge[0])
        for variant in ("method","shape","proof","scope","authority","observation"):
            changed=json.loads(json.dumps(original))
            if variant=="method":
                changed["program"]["ast"]=["VAR",0]
            elif variant=="shape":
                changed["program"]["inferred_typed_macro_shape"]="ANYTHING"
            elif variant=="proof":
                changed["rejected_smaller_grammar_tiers"][-1]["candidate_functions_refuted"]=1
            elif variant=="scope":
                changed["scope"]="UNRESTRICTED"
            elif variant=="authority":
                changed["real_world_authority"]=True
            else:
                changed["public_observations"][0]["reachable"]^=True
            changed["checksum_sha256"]=digest({k:v for k,v in changed.items()
                                               if k!="checksum_sha256"})
            with self.subTest(variant=variant),self.assertRaises(HOLD):
                validate(json.dumps(changed))


    def test_rehashed_false_counterexample_trace_is_not_a_proof(self):
        original=json.loads(self.bridge[0])
        for mode in ("query_order","missing_counterexample","invented_pass"):
            document=json.loads(json.dumps(original))
            if mode=="query_order":
                event=next(e for e in document["source_challenge_trace"]
                           if e["kind"] in ("QUERY","COUNTEREXAMPLE"))
                event["asked"]=9 if event["asked"]!=9 else 10
            elif mode=="missing_counterexample":
                document["source_challenge_trace"].pop(0)
                document["source_oracle_calls"]-=1
            else:
                document["source_challenge_trace"][-1]["signature"]="ffffffff"
            document["checksum_sha256"]=digest({
                k:v for k,v in document.items() if k!="checksum_sha256"})
            with self.subTest(mode=mode),self.assertRaises(HOLD):
                validate(json.dumps(document))

    def test_local_observer_never_leaks_heldout_even_on_refutation(self):
        observer=SourceOwner("LONG_SHORT",max_queries=24)
        with self.assertRaises(ValueError):
            observer.query(HOLDOUT[-1])
        self.assertFalse(any(m in HOLDOUT for m in observer.issued))
        # An obviously false constant-true candidate may be refuted, but only
        # using the source-owner acquisition set and with an attributed receipt.
        response=observer.refute_or_pass((1<<32)-1)
        self.assertEqual(response["status"],"COUNTEREXAMPLE")
        self.assertNotIn(response["observation"]["mask"],HOLDOUT)
        self.assertFalse(response["observation"]["real_world_authority"])

    def test_fixed_008_grammar_fails_different_bridge_topology(self):
        a=fixed_family_accuracy("LONG_SHORT")
        b=fixed_family_accuracy("BRIDGE")
        self.assertEqual(a["fixed_008_best_correct"],32)
        self.assertLess(b["fixed_008_best_correct"],32)
        self.assertLess(b["fixed_007_best_correct"],32)
        self.assertEqual(b["classical_exact_BFS_correct"],32)

    def test_composition_cost_is_explicit_and_one_off_favors_BFS(self):
        for _,_,_,owner in (self.long,self.bridge):
            tiny=cost_model(owner.calls,1)
            big=cost_model(owner.calls,64)
            self.assertEqual(tiny["winner"],"DIRECT_BFS")
            self.assertEqual(big["winner"],"COMPILED_GRAMMAR")
            self.assertFalse(tiny["real_money"])

    def test_full_two_family_benchmark(self):
        report=run()
        self.assertTrue(report["two_nonisomorphic_source_graphs"])
        self.assertFalse(report["invented_mathematically_new_boolean_operator"])
        for family,c in report["families"].items():
            self.assertEqual((c["sealed_holdout_cases"],c["sealed_holdout_errors"]),(8,0))
            self.assertEqual(c["renamed_future_correct"],64)
            self.assertEqual(c["renamed_future_cases"],64)
            self.assertTrue(c["read_only_admitted"])
        self.assertEqual(report["families"]["LONG_SHORT"]["found_expression_node_count"],9)
        self.assertEqual(report["families"]["BRIDGE"]["found_expression_node_count"],11)


if __name__=="__main__":
    unittest.main()
