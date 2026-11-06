import json
import unittest
from source import Case, TRAIN, CERT, training, deployment, bfs_truth
from compiler import HOLD, PROGRAMS, infer, propose, validate, classify, digest
from receiver import Receiver
from market import Bid, DiscoveryMarket, packet, validate_packet
from trial import certified, offers, run

class DiscoveryMarketTests(unittest.TestCase):
    def setUp(self):
        self.raw,self.receiver,self.review=certified()

    def test_induced_sensor_unique_and_full_graph_domain(self):
        self.assertEqual(len(PROGRAMS),15)
        self.assertEqual(infer(training()),((0,1),(2,3)))
        self.assertEqual(validate(self.raw)["program"],[[0,1],[2,3]])
        self.assertEqual((len(TRAIN),len(CERT)),(5,11))
        for name in ("cedar","quartz","willow"):
            for mask in range(16):
                self.assertEqual(classify(infer(training()),mask),
                                 bfs_truth(Case(mask,name)))

    def test_receiver_holds_before_independent_certification(self):
        rec=Receiver(self.raw)
        with self.assertRaises(HOLD):
            rec.suggest(deployment(1)[0])
        with self.assertRaises(HOLD):
            rec.preview(tuple(Case(m) for m in TRAIN))
        result=rec.preview(tuple(Case(m) for m in CERT))
        self.assertEqual((result["cases"],result["errors"]),(11,0))
        with self.assertRaises(HOLD):
            rec.admit("ADMIT_READ_ONLY","old")
        rec.admit("ADMIT_READ_ONLY",result["review_digest"])
        with self.assertRaises(HOLD):
            rec.suggest(Case(3,"cedar"))

    def test_one_off_vs_many_task_payoff_reversal(self):
        tiny=DiscoveryMarket(self.raw,self.receiver,offers(),deployment(1)).evaluate()
        large=DiscoveryMarket(self.raw,self.receiver,offers(),deployment(16)).evaluate()
        self.assertEqual(tiny["winning_kind"],"DIRECT_CLASSICAL_QUERY")
        self.assertEqual(large["winning_kind"],"COMPILE_SENSOR")
        self.assertEqual(large["independently_verified_correct"],16)
        self.assertEqual(large["winner_hypothetical_cost"],14.0)
        self.assertEqual(large["direct_query_hypothetical_cost"],24.0)
        self.assertEqual(large["marginal_verified_savings_points"],10.0)

    def test_duplicate_bid_has_zero_merit_even_with_advertised_gain(self):
        report=DiscoveryMarket(self.raw,self.receiver,offers(),deployment(16)).evaluate()
        self.assertEqual(report["duplicate_offers"],1)
        self.assertEqual(sum(x["earned_nontransferable_utility_points"] for x
            in report["offers"] if not x["new_validated_offer"]),0)
        self.assertTrue(all(x["advertised_gain_ignored"] for x in report["offers"]))
        self.assertFalse(report["real_money_or_tradeable_credits"])

    def test_circular_and_external_bids_are_refused(self):
        with self.assertRaises(HOLD):
            Bid("a","critic","SHELL_EXEC")
        with self.assertRaises(HOLD):
            Bid("a","critic","COMPILE_SENSOR",depends_on=("a",))
        with self.assertRaises(HOLD):
            DiscoveryMarket(self.raw,self.receiver,
                (Bid("a","x","COMPILE_SENSOR",depends_on=("b",)),
                 Bid("b","y","DIRECT_CLASSICAL_QUERY",depends_on=("a",))),
                deployment(2))
        with self.assertRaises(HOLD):
            DiscoveryMarket(self.raw,self.receiver,offers(),(Case(0,"cedar"),))
        with self.assertRaises(HOLD):
            DiscoveryMarket(self.raw,Receiver(self.raw),offers(),deployment(16))

    def test_rehashed_program_forgery_and_privilege_escalation_fail(self):
        for kind in ("method","external","source","label"):
            obj=json.loads(self.raw)
            if kind=="method":obj["program"]=[[0,2],[1,3]]
            elif kind=="external":obj["external_execution"]=True
            elif kind=="source":obj["source_owner_blob"]="0"*40
            else:obj["training_receipts"][0]["reachable"]=True
            obj["checksum_sha256"]=digest({k:v for k,v in obj.items()
                                           if k!="checksum_sha256"})
            with self.subTest(kind=kind),self.assertRaises(HOLD):
                validate(json.dumps(obj))

    def test_wrong_training_or_changed_teacher_contract_hold(self):
        with self.assertRaises(HOLD):
            propose(training()[:-1])
        altered=[dict(x) for x in training()]
        altered[0]["source_revision"]="unexpected-source"
        with self.assertRaises(HOLD):
            propose(altered)

    def test_replayed_market_receipt_rejects_tampering(self):
        raw=packet(self.raw,self.receiver,offers(),deployment(16))
        doc=validate_packet(raw,self.receiver)
        self.assertEqual(doc["receipt"]["independently_verified_correct"],16)
        for change in ("winner","score","truth","authority"):
            obj=json.loads(raw)
            if change=="winner":obj["receipt"]["winning_kind"]="ABSTAIN"
            elif change=="score":obj["receipt"]["independently_verified_correct"]=100
            elif change=="truth":obj["receipt"]["reviewed_tasks"][0]["correct"]=False
            else:obj["real_world_authority"]=True
            obj["checksum_sha256"]=digest({k:v for k,v in obj.items()
                                          if k!="checksum_sha256"})
            with self.subTest(change=change),self.assertRaises(HOLD):
                validate_packet(json.dumps(obj),self.receiver)

    def test_bounded_renamed_graph_transfer(self):
        result=DiscoveryMarket(self.raw,self.receiver,offers(),deployment(32)).evaluate()
        self.assertEqual(result["independently_verified_correct"],32)
        self.assertTrue(result["classical_optimizing_planner_may_tie_or_outperform"])
        self.assertFalse(result["any_external_actions"])

    def test_reproducible_trial(self):
        result=run()
        self.assertEqual(result["heldout_errors"],0)
        self.assertEqual(result["portfolio_errors"],0)
        self.assertEqual(result["hypothetical_marginal_savings"],10.0)
        self.assertFalse(result["new_primitive_invented"])
        self.assertFalse(result["external_actions"])

if __name__=="__main__":
    unittest.main()
