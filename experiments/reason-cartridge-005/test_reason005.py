import json
import unittest
from dataclasses import replace

from engine import (HOLD, Objection, Model, ToyOwner, owner4, pinned_owner,
                    OWNER_GIT_BLOB, build_record, validate, hashed, stress)
from critic import Critic, Receiver, Memory
from trial import (redundant, fragile, false_negative, heldout, run)


def basic():
    return Objection("basic", "RETRACT_PRESENT", (("A","T"),))


class MetaObjectionTest(unittest.TestCase):
    def test_exact_owner_revision_is_pinned(self):
        self.assertEqual(pinned_owner(), OWNER_GIT_BLOB)
        self.assertEqual(len(OWNER_GIT_BLOB), 40)

    def test_counterobjection_rejects_single_edge_attack_with_alternate_proof(self):
        q=redundant()
        candidate=Objection("attacker","RETRACT_PRESENT",(("S","A"),))
        result=stress(q,candidate)
        self.assertEqual(result["classification"],"DEFENSE")
        self.assertEqual(result["alternate_proof"]["kind"],"WITNESSED_PATH")
        self.assertEqual(result["alternate_proof"]["nodes"],["S","B","T"])
        packet=validate(build_record(q,candidate,"DEFENSE"))
        self.assertEqual(packet["outcome"]["status"],"DEFENSE_ONLY_WITHIN_DECLARED_SCOPE")
        self.assertFalse(packet["outcome"]["source_witness_changed"])

    def test_challenging_all_confirmed_routes_is_material_not_fact(self):
        q=redundant()
        obj=Objection("both","RETRACT_PRESENT",(("S","A"),("S","B")))
        result=stress(q,obj)
        self.assertEqual(result["classification"],"MATERIAL_OBJECTION")
        self.assertTrue(result["counterfactual_is_not_evidence"])
        with self.assertRaises(HOLD):
            build_record(q,obj,"DEFENSE")

    def test_corrigible_positive_proof_and_owner_fixture_receipt(self):
        q=fragile()
        obj=basic()
        simulated=ToyOwner("toy-1",{("A","T"):False})
        output=Critic(q,(obj,)).run(simulated)
        self.assertEqual(output["status"],"CORRECTION")
        self.assertEqual(simulated.calls,1)
        doc=validate(json.dumps(output["outcome_cartridge"]))
        self.assertEqual(doc["outcome"]["new_conclusion"],"PROVED_UNREACHABLE")
        self.assertEqual(doc["outcome"]["new_certificate"]["kind"],"FINITE_CUT")
        self.assertEqual(doc["synthetic_owner_receipt"]["status"],
                         "FIXTURE_ONLY_NOT_WORLD_AUTHENTICATION")
        self.assertFalse(doc["real_world_authority"])

    def test_owner_can_disprove_objection_without_changing_conclusion(self):
        q=fragile()
        obj=basic()
        tool=ToyOwner("toy-2",{("A","T"):True})
        answer=Critic(q,(obj,)).run(tool)
        self.assertEqual(answer["status"],"OWNER_DEFENSE")
        doc=validate(json.dumps(answer["outcome_cartridge"]))
        self.assertEqual(doc["outcome"]["new_conclusion"],"PROVED_REACHABLE")
        with self.assertRaises(HOLD):
            build_record(q,obj,"CORRECTION", after=owner4.decode(doc["revised_inquiry"]),
                         owner_receipt=doc["synthetic_owner_receipt"])

    def test_correction_can_reverse_false_negative_claim(self):
        q=false_negative()
        challenge=Objection("test-a","REVIEW_ABSENCE",(("A","T"),))
        oracle=ToyOwner("toy-3",{("A","T"):True})
        answer=Critic(q,(challenge,)).run(oracle)
        self.assertEqual(answer["status"],"CORRECTION")
        doc=validate(json.dumps(answer["outcome_cartridge"]))
        self.assertEqual(doc["outcome"]["new_conclusion"],"PROVED_REACHABLE")

    def test_value_of_more_reasoning_holds_when_review_cost_high(self):
        obj=basic()
        costly=Model(chance_of_correction=.2,benefit_if_corrected=2.0,
                     verification_cost=3.0,reasoning_cost=.1)
        self.assertLess(costly.value()["net_value_of_further_reasoning"],0)
        tool=ToyOwner("expensive",{("A","T"):False})
        answer=Critic(fragile(),(obj,),model=costly).run(tool)
        self.assertEqual(answer["status"],"STOP_NO_POSITIVE_VALUE")
        self.assertEqual(answer["owner_reviews"],0)
        self.assertEqual(tool.calls,0)

    def test_without_source_owner_no_actual_observation(self):
        out=Critic(fragile(),(basic(),)).run()
        self.assertEqual(out["status"],"HOLD_OWNER_REVIEW_REQUIRED")
        self.assertTrue(out["no_external_queries"])
        self.assertIsNone(out.get("outcome_cartridge"))

    def test_budget_zero_and_duplicate_objections_prevent_recursive_spin(self):
        out=Critic(fragile(),(basic(),),budget=0).run(ToyOwner("no-call",{("A","T"):False}))
        self.assertEqual(out["status"],"STOP_BUDGET_EXHAUSTED")
        self.assertEqual(out["owner_reviews"],0)
        with self.assertRaises(HOLD):
            Critic(redundant(),(basic(),basic()))
        with self.assertRaises(HOLD):
            Critic(redundant(),(basic(),Objection("other","RETRACT_PRESENT",(("A","T"),))))
        with self.assertRaises(HOLD):
            Critic(fragile(),(basic(),),budget=2)

    def test_open_world_unknown_holds_without_invented_inquiry(self):
        q=fragile()
        open_unknown=owner4.Inquiry(q.nodes,q.universe,(q.claims[0],),
                                    q.removed,False)
        response=stress(open_unknown,basic())
        self.assertEqual(response["classification"],"HOLD_UNPROVED_OR_OPEN_WORLD")
        self.assertTrue(response["no_external_review"])

    def test_unsupported_or_stale_objection_refuses(self):
        q=fragile()
        with self.assertRaises(HOLD):
            stress(q,Objection("bad","RETRACT_PRESENT",(("S","T"),)))
        with self.assertRaises(HOLD):
            stress(q,Objection("bad","RETRACT_PRESENT",(("T","A"),)))
        with self.assertRaises(HOLD):
            stress(q,Objection("bad","REVIEW_ABSENCE",(("A","T"),)))
        with self.assertRaises(HOLD):
            Objection("../path","RETRACT_PRESENT",(("A","T"),))

    def test_forged_correction_fails_even_with_new_content_hash(self):
        q=fragile()
        objected=basic()
        x=Critic(q,(objected,)).run(ToyOwner("origin",{("A","T"):False}))
        raw=x["outcome_cartridge"]
        for mode in ("authority","future","outcome","premise","receipt","owner"):
            c=json.loads(json.dumps(raw))
            if mode=="authority": c["real_world_authority"]=True
            elif mode=="future": c["outcome"]["new_conclusion"]="PROVED_REACHABLE"
            elif mode=="outcome": c["classification"]="OWNER_DEFENSE"
            elif mode=="premise": c["original_inquiry"]["closed_scope"]=False
            elif mode=="receipt": c["synthetic_owner_receipt"]["reviewed_truth"][0]["present"]=True
            else: c["owner_reason004_blob"]="outdated"
            c["checksum_sha256"]=hashed({k:v for k,v in c.items()
                                         if k!="checksum_sha256"})
            with self.subTest(mode=mode),self.assertRaises(HOLD):
                validate(json.dumps(c))

    def test_defenses_are_exact_context_reusable_not_general_laws(self):
        q=redundant()
        obj=Objection("challenge","RETRACT_PRESENT",(("S","A"),))
        cache=Memory()
        raw=build_record(q,obj,"DEFENSE")
        cache.store(raw)
        self.assertEqual(cache.recall(q,obj)["status"],"EXACT_CONTEXT_ONLY")
        self.assertEqual(cache.recall(fragile(),obj)["status"],"HOLD_NO_REUSABLE_CONTEXT")
        self.assertEqual(cache.recall(q,Objection("different","RETRACT_PRESENT",(("S","A"),)))["status"],
                         "HOLD_NO_REUSABLE_CONTEXT")

    def test_independent_receiver_review_and_admission(self):
        out=Critic(fragile(),(basic(),)).run(ToyOwner("test-owner",{("A","T"):False}))
        r=Receiver(json.dumps(out["outcome_cartridge"]))
        with self.assertRaises(HOLD):
            r.suggest()
        with self.assertRaises(HOLD):
            r.preview((heldout()[0],))
        result=r.preview(heldout())
        self.assertEqual((result["cases"],result["errors"]),(4,0))
        with self.assertRaises(HOLD):
            r.admit("ADMIT_READ_ONLY","wrong")
        with self.assertRaises(HOLD):
            r.admit("RUN_TOOL",result["review_digest"])
        r.admit("ADMIT_READ_ONLY",result["review_digest"])
        self.assertEqual(r.suggest()["stage"],"SUGGEST_ONLY")
        self.assertFalse(r.suggest()["external_execution"])

    def test_end_to_end_benchmark_economy_and_correctness(self):
        r=run()
        self.assertEqual(r["redundant_objection_defenses"],2)
        self.assertEqual(r["redundant_owner_reviews"],0)
        self.assertEqual(r["real_premise_error_corrections_in_synthetic_fixture"],2)
        self.assertEqual(r["source_rebuttals_after_fixture_review"],1)
        self.assertEqual(r["meta_critic_source_reviews"],3)
        self.assertEqual(r["naive_always_review_count"],6)
        self.assertEqual(r["independent_review"],{"cases":4,"errors":0})
        self.assertEqual(r["repaired_positive_claim"],"PROVED_UNREACHABLE")
        self.assertEqual(r["repaired_negative_claim"],"PROVED_REACHABLE")
        self.assertEqual(r["changed_context_memory_status"],"HOLD_NO_REUSABLE_CONTEXT")
        self.assertEqual(r["external_observations_performed"],0)


if __name__=="__main__":
    unittest.main()
