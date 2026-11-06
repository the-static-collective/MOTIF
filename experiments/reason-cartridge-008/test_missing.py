import json
import unittest

from source import Case, TRAIN_MASKS, WITHHELD_MASKS, lessons, certification, deployment, bfs_truth
from discover import HOLD, LEGACY, EXPANDED, bits, old_eval, expanded_eval, detect_gap, synthesize, validate, digest
from receiver import Receiver
from market import Bid, DiscoveryMarket, make_receipt, validate_receipt, pin_ledger
from trial import run, certified, bids


class MissingPrimitiveTests(unittest.TestCase):
    def setUp(self):
        self.raw,self.receiver,self.cert=certified()

    def test_old_dsl_has_exhaustive_gap_not_a_failed_heuristic(self):
        gap=detect_gap(lessons())
        self.assertEqual(len(LEGACY),45)
        self.assertEqual(len(gap["refutations"]),45)
        self.assertTrue(gap["all_old_candidates_refuted"])
        for witness in gap["refutations"]:
            program=tuple(tuple(p) for p in witness["old_program"])
            self.assertIn(program,LEGACY)
            actual=old_eval(program,witness["counterexample_mask"])
            self.assertEqual(witness["old_prediction"],actual)
            self.assertNotEqual(actual,witness["source_reachable"])
        self.assertEqual(max(sum(old_eval(pg,m)==bfs_truth(Case(m))
                                 for m in TRAIN_MASKS) for pg in LEGACY),4)

    def test_minimal_new_typed_macro_recovered_uniquely(self):
        packet=validate(self.raw)
        self.assertEqual(len(EXPANDED),100)
        self.assertEqual(packet["proposed_extension"]["program"],
                         {"triple":[0,1,2],"pair":[3,4]})
        self.assertFalse(packet["proposed_extension"]["adds_new_fundamental_boolean_primitive"])
        self.assertEqual(packet["proposed_extension"]["programs_consistent_with_lessons"],1)

    def test_source_owner_independent_bfs_all_32_worlds(self):
        p=validate(self.raw)["proposed_extension"]["program"]
        pg=(tuple(p["triple"]),tuple(p["pair"]))
        for mask in range(32):
            for variant in ("cedar","quartz","willow"):
                with self.subTest(mask=mask,variant=variant):
                    self.assertEqual(expanded_eval(pg,mask),bfs_truth(Case(mask,variant)))

    def test_holdout_is_disjoint_and_admission_digest_bound(self):
        self.assertEqual(set(TRAIN_MASKS)&set(WITHHELD_MASKS),set())
        self.assertEqual((len(TRAIN_MASKS),len(WITHHELD_MASKS)),(5,27))
        rec=Receiver(self.raw)
        with self.assertRaises(HOLD):
            rec.suggest(Case(7,"quartz"))
        with self.assertRaises(HOLD):
            rec.preview(tuple(Case(m) for m in TRAIN_MASKS))
        preview=rec.preview(certification())
        self.assertEqual((preview["cases"],preview["errors"]),(27,0))
        with self.assertRaises(HOLD):
            rec.admit("ADMIT_READ_ONLY","stale")
        with self.assertRaises(HOLD):
            rec.admit("RUN_TOOL",preview["review_digest"])
        rec.admit("ADMIT_READ_ONLY",preview["review_digest"])
        self.assertFalse(rec.suggest(Case(7,"quartz"))["external_execution"])
        with self.assertRaises(HOLD):
            rec.suggest(Case(7,"cedar"))

    def test_missing_teaching_witness_or_mismatching_source_holds(self):
        with self.assertRaises(HOLD):
            synthesize(lessons()[:-1])
        damaged=[dict(x) for x in lessons()]
        damaged[0]["features"]=[0,0,0,0,0]
        with self.assertRaises(HOLD):
            synthesize(damaged)
        damaged=[dict(x) for x in lessons()]
        damaged[0]["source_revision"]="someone-else"
        with self.assertRaises(HOLD):
            synthesize(damaged)

    def test_altered_teacher_labels_do_not_silently_earn_authority(self):
        damaged=[dict(x) for x in lessons()]
        damaged[3]["reachable"]=False
        with self.assertRaises(HOLD):
            synthesize(damaged)

    def test_rehashed_legacy_refutation_or_new_macro_is_recomputed(self):
        raw=json.loads(self.raw)
        for kind in ("extension","refutation","source","permission","label"):
            p=json.loads(json.dumps(raw))
            if kind=="extension":
                p["proposed_extension"]["program"]["triple"]=[0,1,4]
            elif kind=="refutation":
                p["old_language_refutation"]["old_candidates_refuted"]=44
            elif kind=="source":
                p["source_owner_git_blob"]="0"*40
            elif kind=="permission":
                p["external_execution"]=True
            else:
                p["training_evidence"][0]["reachable"]=True
            p["checksum_sha256"]=digest({k:v for k,v in p.items()
                                         if k!="checksum_sha256"})
            with self.subTest(kind=kind),self.assertRaises(HOLD):
                validate(json.dumps(p))

    def test_one_off_bfs_is_cheaper_than_speculative_macro(self):
        r=DiscoveryMarket(self.raw,self.receiver,bids(),deployment(1)).evaluate()
        self.assertEqual(r["winning_method"],"DIRECT_CLASSICAL_BFS")
        self.assertEqual(r["independently_correct"],1)
        self.assertEqual(r["commonwealth_new_method_credit"],0)

    def test_thirty_two_tasks_justify_macro_amortization_on_declared_prices(self):
        r=DiscoveryMarket(self.raw,self.receiver,bids(),deployment(32)).evaluate()
        self.assertEqual(r["winning_method"],"GAP_REPAIR_MACRO")
        self.assertEqual(r["independently_correct"],32)
        self.assertEqual(r["direct_classical_hypothetical_cost"],48)
        self.assertEqual(r["winning_hypothetical_cost"],27)
        self.assertEqual(r["independent_evidence_gated_savings_points"],21)
        self.assertEqual(r["commonwealth_new_method_credit"],1)
        self.assertEqual(r["commonwealth_duplicate_credit"],0)
        self.assertEqual(r["commonwealth_new_source_facts"],0)

    def test_duplicate_bids_and_bogus_authority_refused(self):
        result=DiscoveryMarket(self.raw,self.receiver,bids(),deployment(32)).evaluate()
        self.assertEqual(result["duplicated_offers"],1)
        self.assertTrue(all(r["asserted_gain_ignored"] for r in result["offers"]))
        with self.assertRaises(HOLD):
            Bid("bad","x","RUN_EXTERNAL_CODE")
        with self.assertRaises(HOLD):
            Bid("c","x","GAP_REPAIR_MACRO",dependencies=("c",))
        with self.assertRaises(HOLD):
            DiscoveryMarket(self.raw,Receiver(self.raw),bids(),deployment(32))

    def test_market_refuses_bad_topology_cycles_and_repeated_portfolio(self):
        with self.assertRaises(ValueError):
            Case(1,"cedar","SIX_EDGE_BRIDGE")
        with self.assertRaises(HOLD):
            DiscoveryMarket(self.raw,self.receiver,bids(),
                            (Case(0,"quartz"),Case(0,"quartz")))
        with self.assertRaises(HOLD):
            DiscoveryMarket(self.raw,self.receiver,(
                Bid("a","x","GAP_REPAIR_MACRO",dependencies=("b",)),
                Bid("b","y","DIRECT_CLASSICAL_BFS",dependencies=("a",))),
                deployment(2))

    def test_market_receipts_reject_rehashed_false_scores(self):
        raw=make_receipt(self.raw,self.receiver,bids(),deployment(32))
        self.assertEqual(validate_receipt(raw,self.receiver)["market"]["independently_correct"],32)
        for kind in ("winner","gain","fake_truth","permissions"):
            p=json.loads(raw)
            if kind=="winner":
                p["market"]["winning_method"]="HOLD_NO_ANSWER"
            elif kind=="gain":
                p["market"]["independent_evidence_gated_savings_points"]=99999
            elif kind=="fake_truth":
                p["market"]["source_checked_answers"][0]["correct"]=False
            else:
                p["real_world_authority"]=True
            p["checksum_sha256"]=digest({k:v for k,v in p.items()
                                         if k!="checksum_sha256"})
            with self.subTest(kind=kind),self.assertRaises(HOLD):
                validate_receipt(json.dumps(p),self.receiver)

    def test_reproduced_experiment_receipt(self):
        r=run()
        self.assertEqual(r["legacy_programs_refuted_by_teaching"],45)
        self.assertEqual(r["expanded_grammar_candidates"],100)
        self.assertEqual(r["independent_source_certification"]["cases"],27)
        self.assertEqual(r["independent_source_certification"]["errors"],0)
        self.assertEqual(r["thirty_two_task_correct"],32)
        self.assertEqual(r["thirty_two_task_modeled_savings"],21)
        self.assertEqual(r["new_real_world_facts"],0)
        self.assertFalse(r["fundamental_boolean_primitive_invented"])
        self.assertFalse(r["outside_this_five_edge_structure_tested"])
        self.assertFalse(r["graft_or_cannon_invoked"])


if __name__=="__main__":
    unittest.main()
