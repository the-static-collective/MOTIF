"""COGNITION-003: resurfacing, unchanged history, fair controls and owner truth."""
import copy
import json
import unittest
from unittest.mock import patch
from datetime import datetime

from resurface import (AppState,DEV_SEEDS,TEST_SEEDS,REGIMES,POLICIES,BUDGET,
                       DEFAULT_STATE,OWNER,archive,new_incident,RepairOwner,
                       packet_for,eligible_paths,_native_graph,_cached_paths,
                       _motif_hypothetical_order,owner_understory_envelope,
                       validate_understory_owner,run_case,benchmark,seal)


class ResurfacingTests(unittest.TestCase):
    def test_freeze_new_hidden_cohort_and_arms(self):
        self.assertEqual(len(TEST_SEEDS),32)
        self.assertTrue(set(TEST_SEEDS).isdisjoint(DEV_SEEDS))
        self.assertEqual(len(REGIMES),5)
        self.assertEqual(len(POLICIES),4)

    def test_true_two_hop_native_graph_is_unadmitted(self):
        seed=DEV_SEEDS[0]
        p=packet_for(archive(seed,"stable"),new_incident(seed,"stable"))
        _,_,validate,native_neighbors=_native_graph()
        self.assertEqual(validate(p),[])
        self.assertEqual(p["task_world_cut"]["status"],"unresolved")
        self.assertEqual(len(p["links"]),4)
        self.assertEqual(len(p["sources"]),5)
        self.assertTrue(all(x["authority"]=="none" and x["status"]=="unresolved"
                            and x["verb"]=="connects" for x in p["links"]))
        self.assertTrue(all(s["source_class"]=="unresolved-receipt" for s in p["sources"]))
        paths,work=eligible_paths(p,new_incident(seed,"stable")["cue"])
        self.assertEqual(len(paths),2)
        self.assertTrue(all(x["independent"] for x in paths))
        self.assertEqual([x["slot"] for x in paths],[0,1])
        self.assertTrue(work>=4)

    def test_association_is_not_evidence_of_causation(self):
        seed=DEV_SEEDS[0]
        p=packet_for(archive(seed,"stable"),new_incident(seed,"stable"))
        for node in p["nodes"]:
            self.assertNotEqual(node["status"],"supported")
            self.assertNotEqual(node["status"],"locally-adopted")
        self.assertTrue(all(l["verb"]!="constitutes" and l["verb"]!="descends-from"
                            for l in p["links"]))
        self.assertNotIn("true_fault",json.dumps(p))
        self.assertNotIn("independently_verified",json.dumps(p))

    def test_echo_roots_do_not_count_twice(self):
        seed=DEV_SEEDS[0]
        p=packet_for(archive(seed,"echo_source"),new_incident(seed,"echo_source"))
        paths,_=eligible_paths(p,new_incident(seed,"echo_source")["cue"])
        self.assertFalse(paths[0]["independent"])
        self.assertTrue(paths[1]["independent"])
        self.assertEqual(paths[0]["source_roots"][0],paths[0]["source_roots"][1])
        result=run_case(seed,"echo_source","motif_resurface")
        self.assertEqual(result["excluded_echo_paths"],1)
        self.assertEqual(result["probes"],1)
        self.assertTrue(result["verified_success"])

    def test_no_old_matching_cue_does_not_resurface(self):
        seed=DEV_SEEDS[0]
        p=packet_for(archive(seed,"unrelated_trigger"),
                     new_incident(seed,"unrelated_trigger"))
        paths,_=eligible_paths(p,new_incident(seed,"unrelated_trigger")["cue"])
        self.assertEqual(paths,[])
        r=run_case(seed,"unrelated_trigger","motif_resurface")
        self.assertFalse(r["resurfaced"])
        self.assertEqual(r["probes"],0)
        self.assertEqual(r["repair_attempts"],0)
        self.assertFalse(r["verified_success"])

    def test_independent_simulator_repair_requires_positive_probe(self):
        owner=RepairOwner(DEV_SEEDS[0],"stable")
        with self.assertRaises(ValueError):
            owner.repair("module-no-source")
        first=archive(DEV_SEEDS[0],"stable")
        unit=first[-1]["to"]
        r=owner.probe(unit)
        self.assertFalse(r["positive"])
        with self.assertRaises(ValueError):
            owner.repair(unit)
        self.assertFalse(owner.repaired)
        self.assertEqual(len(owner.receipts),1)

    def test_sim_owner_never_hands_hidden_fault_in_public_test(self):
        owner=RepairOwner(DEV_SEEDS[1],"drift_alternative")
        probe=owner.probe(archive(DEV_SEEDS[1],"drift_alternative")[1]["to"])
        self.assertNotIn("true_fault",probe)
        self.assertNotIn("_fault",probe)
        self.assertEqual(probe["source"],OWNER)
        data={k:v for k,v in probe.items() if k!="seal"}
        self.assertEqual(probe["seal"],seal(data))

    def test_two_probes_then_known_owner_fix_in_drift(self):
        for policy in POLICIES[:-1]:
            row=run_case(DEV_SEEDS[0],"drift_alternative",policy)
            self.assertTrue(row["verified_success"])
            self.assertEqual(row["probes"],2)
            self.assertEqual(row["repair_attempts"],1)
            self.assertEqual(row["unsafe_repairs"],0)

    def test_unknown_drift_abstains_safely_not_fabricate_success(self):
        for policy in POLICIES[:-1]:
            row=run_case(DEV_SEEDS[1],"drift_unmodeled",policy)
            self.assertFalse(row["verified_success"])
            self.assertEqual(row["probes"],2)
            self.assertEqual(row["repair_attempts"],0)
            self.assertEqual(row["unsafe_repairs"],0)
            self.assertTrue(row["abstained"])

    def test_genuinely_native_motif_affordance_candidates(self):
        seed=DEV_SEEDS[0]
        cache,ops=_cached_paths(archive(seed,"stable"))
        assert ops>0
        proposed,n=_motif_hypothetical_order(cache[new_incident(seed,"stable")["cue"]])
        self.assertEqual(n,2)
        self.assertEqual(len(proposed),2)
        self.assertTrue(all(x["status"]=="PENCIL_NOT_A_REPAIR" for x in proposed))

    def test_not_a_hidden_unlimited_app_service(self):
        seed=DEV_SEEDS[0]
        off=AppState(False,False,0,True,11,False,88,.90,"critical")
        x=run_case(seed,"stable","motif_resurface",state=off)
        self.assertFalse(x["resurfaced"])
        self.assertEqual(x["idle_operations"],0)
        self.assertEqual(x["native_motif003_options"],0)
        self.assertFalse(x["native_understory"]["validated"])
        self.assertTrue(x["verified_success"]) # task-directed foreground alternative
        self.assertGreaterEqual(x["wake_operations"],2)

    def test_native_owner_understory_envelope_temporal_and_nonconstituting(self):
        seed=DEV_SEEDS[0]
        facts=archive(seed,"stable")
        before=copy.deepcopy(facts)
        env=owner_understory_envelope(facts,new_incident(seed,"stable"))
        self.assertEqual(len(env["records"]),7)
        self.assertEqual([x["family"] for x in env["records"]],
                         ["contact"]*4+["association"]*2+["activation"])
        self.assertEqual(env["records"][-1]["trace_refs"],
                         [x["id"] for x in env["records"][4:6]])
        self.assertTrue(all(datetime.fromisoformat(r["recorded_at"].replace("Z","+00:00"))
                            for r in env["records"]))
        self.assertTrue(all(x.get("status")=="unresolved"
                            for x in env["records"] if x["family"]=="association"))
        self.assertEqual(before,facts)
        self.assertEqual(validate_understory_owner(env,None)["status"],
                         "HOLD_NATIVE_MEMENTO_UNAVAILABLE")
        self.assertFalse(any("attention"==x["family"] for x in env["records"]))

    def test_reject_tampered_source_packet(self):
        seed=DEV_SEEDS[0]
        p=packet_for(archive(seed,"stable"),new_incident(seed,"stable"))
        p["links"][0]["authority"]="owner-local"
        with self.assertRaisesRegex(ValueError,"UNTRUSTED_GRAPH_PACKET"):
            eligible_paths(p,new_incident(seed,"stable")["cue"])

    def test_equal_information_standards_with_strong_classical(self):
        for regime in REGIMES:
            m=run_case(DEV_SEEDS[0],regime,"motif_resurface")
            c=run_case(DEV_SEEDS[0],regime,"classical_cached")
            b=run_case(DEV_SEEDS[0],regime,"classical_online_bfs")
            self.assertEqual(m["verified_success"],c["verified_success"])
            self.assertEqual(m["verified_success"],b["verified_success"])
            self.assertEqual(m["probes"],c["probes"])
            self.assertEqual(m["probes"],b["probes"])
            self.assertEqual(m["wake_operations"],c["wake_operations"])
            self.assertGreaterEqual(b["wake_operations"],c["wake_operations"])

    def test_full_owner_action_audit_replayable(self):
        row=run_case(DEV_SEEDS[2],"drift_alternative","motif_resurface",full=True)
        self.assertEqual(row["seal"],seal({k:v for k,v in row.items() if k!="seal"}))
        self.assertEqual(len(row["owner_verified_receipts"]),row["probes"]+row["repair_attempts"])
        for i,r in enumerate(row["owner_verified_receipts"],1):
            self.assertEqual(r["sequence"],i)
            self.assertEqual(r["seal"],seal({k:v for k,v in r.items() if k!="seal"}))
        self.assertTrue(row["archive_unchanged"])

    def test_dev_reproducible_fixed_80_cases(self):
        one=benchmark("development")
        two=benchmark("development")
        self.assertEqual(one["seal"],two["seal"])
        self.assertEqual(one["n"],len(DEV_SEEDS)*len(REGIMES)*len(POLICIES))
        self.assertEqual(len(one["paired"]),len(DEV_SEEDS)*len(REGIMES))
        self.assertEqual(one["model_calls"],0)
        self.assertTrue(all(x["unsafe_repairs"]==0 for x in one["rows"]))


if __name__=="__main__":
    unittest.main()
