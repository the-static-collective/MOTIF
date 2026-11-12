"""LLM-005 fail-closed tests, including a fully executed long causal chain."""
import copy,json,unittest
from error_dividend import Owner,DEV,INPUTS
from hypermap import ReasonHypermap,grade
from odyssey import (LongChain,GateError,BudgetError,SECTORS,GATES_PER_SECTOR,
   REQUIRED_GATES,MINIMUM_ACTIONS,SCENARIO_SEEDS,DEV_SEEDS,POLICIES,
   problem_order,independent_owner_seed,digest,experiment)

class OdysseyTest(unittest.TestCase):
    def make(self,policy="classical_bayes",seed=DEV_SEEDS[0],**kw):
        return LongChain(seed,policy,**kw)
    def progress_first_cell(self,m):
        m.survey()
        m.decide()
        if m.repair_needed:
            m.repair();m.retry(m.expected_retry)
    def wrong_first_fixture(self):
        for seed in DEV_SEEDS:
            m=self.make("static",seed)
            x=m.order[0][0]
            if x!=m.owner[0].start_x and m._prediction(0,x)[0]!=m.owner[0].truth(x):
                return m
        self.fail("The preregistered dev seeds contain no initially wrong fixed gate")
    def test_01_chain_has_exact_96_dependent_decisions(self):
        self.assertEqual(SECTORS,GATES_PER_SECTOR+4)
        self.assertEqual(REQUIRED_GATES,96)
    def test_02_minimum_serial_chain_219(self):
        self.assertEqual(MINIMUM_ACTIONS,219)
    def test_03_independent_sector_hidden_source_owners(self):
        m=self.make()
        self.assertEqual(len({o.seed for o in m.owner}),12)
        self.assertEqual(len({o.initial["root"] for o in m.owner}),12)
    def test_04_every_stage_permutation_has_all_eight_inputs(self):
        m=self.make()
        self.assertTrue(all(set(order)==set(INPUTS) and len(order)==8 for order in m.order))
    def test_05_phases_change_author_owned_rules_not_global_memory(self):
        m=self.make()
        self.assertEqual(len({id(g) for g in m.maps}),12)
        self.assertTrue(all(len(g.events)==0 for g in m.maps))
    def test_06_wrong_order_is_blocked(self):
        m=self.make()
        with self.assertRaisesRegex(GateError,"OUT_OF_ORDER_DEPENDENCY"):
            m._survey(1,0)
    def test_07_survey_must_precede_commit(self):
        m=self.make()
        with self.assertRaisesRegex(GateError,"SURVEY_REQUIRED"):m.decide()
    def test_08_cannot_survey_same_gate_twice(self):
        m=self.make();m.survey()
        with self.assertRaisesRegex(GateError,"ALREADY_SURVEYED"):m.survey()
    def test_09_survey_cannot_leak_true_owner_answer(self):
        m=self.make()
        m.survey()
        last=m.events[-1]
        self.assertEqual(last["kind"],"survey")
        self.assertNotIn("owner_true_answer",last["meta"])
        self.assertEqual(last["meta"]["hint_status"],"UNVERIFIED_ECHO_IGNORE")
    def test_10_mistake_requires_real_repair_before_retry(self):
        m=self.wrong_first_fixture()
        m.survey();m.decide()
        self.assertTrue(m.repair_needed)
        self.assertEqual(m.gate,0)
        with self.assertRaisesRegex(GateError,"REPAIR_AND_VERIFIED_RECEIPT_REQUIRED"):
            m.retry(m.expected_retry)
    def test_11_repair_requires_mistake(self):
        m=self.make()
        with self.assertRaisesRegex(GateError,"NO_REPAIR_NEEDED"):m.repair()
    def test_12_wrong_guess_cannot_be_retried(self):
        m=self.wrong_first_fixture()
        m.survey();m.decide();m.repair()
        with self.assertRaisesRegex(GateError,"RETRY_MUST_USE_VERIFIED_RESULT"):
            m.retry(1-m.expected_retry)
        self.assertEqual(len(m.completed),0)
    def test_13_repaired_guess_preserves_failed_commit(self):
        m=self.wrong_first_fixture()
        m.survey();m.decide();m.repair();m.retry(m.expected_retry)
        self.assertIn((0,0),m.completed)
        self.assertEqual([e["kind"] for e in m.events],
                         ["survey","commit_wrong","repair","commit_repaired"])
    def test_14_no_hypothetical_shortcut_past_half_audit(self):
        m=self.make()
        for _ in range(4):self.progress_first_cell(m)
        self.assertEqual(m.gate,4)
        with self.assertRaisesRegex(GateError,"HALFWAY_AUDIT_REQUIRED"):
            m._survey(0,4)
    def test_15_half_audit_rejects_before_four_verified_gates(self):
        m=self.make();self.progress_first_cell(m)
        with self.assertRaisesRegex(GateError,"AUDIT_REQUIRES_COMPLETE_VERIFIED_GATES"):
            m.audit("half")
    def test_16_audit_is_required_and_independently_scoped(self):
        m=self.make()
        for _ in range(4):self.progress_first_cell(m)
        m.audit("half")
        self.assertEqual(m.events[-1]["kind"],"half_audit")
        self.assertEqual(m.events[-1]["meta"]["distinct_source_roots"],4)
    def test_17_initial_calibration_may_occur_in_second_half(self):
        candidates=[seed for seed in DEV_SEEDS if
            LongChain(seed).order[0].index(LongChain(seed).owner[0].start_x)>=4]
        self.assertTrue(candidates)
        m=self.make(seed=candidates[0])
        for _ in range(4):self.progress_first_cell(m)
        m.audit("half")
        self.assertEqual(m.events[-1]["meta"]["distinct_source_roots"],4)
    def test_18_stage_audit_cannot_happen_without_all_eight(self):
        m=self.make()
        for _ in range(4):self.progress_first_cell(m)
        m.audit("half")
        with self.assertRaisesRegex(GateError,"AUDIT_REQUIRES_COMPLETE_VERIFIED_GATES"):
            m.audit("terminal")
    def test_19_stage_rule_family_distinct_sources(self):
        m=self.make()
        self.assertTrue(all(g.initial_x in m.order[i] for i,g in enumerate(m.maps)))
    def test_20_probe_receipt_matches_exact_staged_input(self):
        m=self.make()
        x=next(q for q in m.order[0] if q!=m.maps[0].initial_x)
        p=m.maps[0].propose_query(x)
        self.assertEqual(p.x,x)
        self.assertTrue(m.maps[0].imagined_outcomes(p))
    def test_21_repeating_calibration_query_not_independent(self):
        m=self.make()
        with self.assertRaisesRegex(ValueError,"INVALID_OR_REPEATED_QUERY"):
            m.maps[0].propose_query(m.maps[0].initial_x)
    def test_22_one_outstanding_source_test(self):
        m=self.make()
        xs=[q for q in m.order[0] if q!=m.maps[0].initial_x]
        m.maps[0].propose_query(xs[0])
        with self.assertRaisesRegex(ValueError,"ONE_OUTSTANDING_TEST"):
            m.maps[0].propose_query(xs[1])
    def test_23_proposal_does_not_update_without_owner_test(self):
        m=self.make()
        before=list(m.maps[0].weights)
        x=next(q for q in m.order[0] if q!=m.maps[0].initial_x)
        m.maps[0].propose_query(x)
        self.assertEqual(m.maps[0].weights,before)
    def test_24_optional_verification_means_one_owner_report_not_two(self):
        m=self.make("hypermap_voi")
        summary=m.execute()
        self.assertTrue(summary["completed"])
        self.assertEqual(len(m.maps),12)
        self.assertEqual(sum(len(g.events) for g in m.maps),84)
        self.assertEqual(summary["metrics"]["source_verified"],96)
    def test_25_preregistered_minimum_actions_under_full_success(self):
        m=self.make()
        s=m.execute()
        self.assertTrue(s["completed"])
        self.assertGreaterEqual(s["actions"],219)
    def test_26_all_required_audits_relay_events_and_96_gates(self):
        m=self.make()
        s=m.execute()
        self.assertEqual(len(m.completed),96)
        self.assertEqual(s["metrics"]["half_audits"],12)
        self.assertEqual(s["metrics"]["terminal_audits"],12)
        self.assertEqual(s["metrics"]["relays"],3)
    def test_27_calibration_is_reused_once_per_sector(self):
        m=self.make()
        s=m.execute()
        self.assertEqual(s["metrics"]["calibration_reuses"],12)
        self.assertEqual(sum(len(m.maps[i].events) for i in range(12)),84)
    def test_28_heldout_trajectory_hash_replays_exactly(self):
        a=self.make().execute()
        b=self.make().execute()
        self.assertEqual(a["final_chain_hash"],b["final_chain_hash"])
        self.assertEqual(a["actions"],b["actions"])
    def test_29_all_action_records_chain_to_previous_digest(self):
        m=self.make();m.execute()
        prev="0"*64
        for i,e in enumerate(m.events,1):
            self.assertEqual(e["prior_hash"],prev)
            self.assertEqual(e["action"],i)
            self.assertEqual(e["hash"],digest({k:v for k,v in e.items() if k!="hash"}))
            prev=e["hash"]
    def test_30_no_owner_rule_or_private_person_in_export(self):
        m=self.make();m.execute()
        p=m.public_trace()
        self.assertTrue(p["hidden_owner_truth_excluded"])
        self.assertFalse(p["external_actions"])
        self.assertNotIn("_truth",json.dumps(p))
        self.assertTrue(all(g["owner_hidden_rule_excluded"] for g in p["per_sector"]))
    def test_31_mutating_copy_never_modifies_record_history(self):
        m=self.make();m.execute()
        obj=m.public_trace()
        obj["events"][0]["meta"]["x"][0]=23
        self.assertNotEqual(obj["events"][0],m.events[0])
    def test_32_echoed_rumor_roots_are_ignored_84_times(self):
        m=self.make()
        s=m.execute()
        self.assertEqual(s["metrics"]["root_echoes_ignored"],12*(8-1))
        self.assertEqual(s["metrics"]["rumor_was_used_as_evidence"],0)
    def test_33_each_owner_receipt_is_used_once(self):
        m=self.make();m.execute()
        for i,g in enumerate(m.maps):
            self.assertEqual(len(g.queries),7)
            self.assertEqual(len(m.per_sector_receipts[i]),8)
    def test_34_action_budget_is_a_real_halt(self):
        m=self.make(action_limit=9)
        s=m.execute()
        self.assertEqual(s["state"],"BUDGET_EXHAUSTED")
        self.assertFalse(s["completed"])
        self.assertLessEqual(s["actions"],9)
        self.assertLess(s["completed_gates"],96)
    def test_35_cost_budget_is_a_real_halt(self):
        m=self.make(cost_limit=7)
        s=m.execute()
        self.assertEqual(s["state"],"BUDGET_EXHAUSTED")
        self.assertFalse(s["completed"])
        self.assertLessEqual(s["cost"],7.0)
    def test_36_invalid_policy_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_POLICY"):
            self.make("model-hallucinates")
    def test_37_wrong_seed_rejected(self):
        with self.assertRaisesRegex(ValueError,"SEED_NOT_REGISTERED"):
            LongChain(900001)
    def test_38_model_replacement_is_not_claimed(self):
        m=self.make()
        s=m.execute()
        self.assertFalse(s["real_llm_used"])
        self.assertEqual(s["side_effects"],0)
    def test_39_baselines_receive_equal_initial_information(self):
        a=self.make("static")
        b=self.make("classical_bayes")
        c=self.make("hypermap_voi")
        self.assertEqual([o.initial for o in a.owner],[o.initial for o in b.owner])
        self.assertEqual([o.initial for o in b.owner],[o.initial for o in c.owner])
        self.assertEqual(a.order,b.order)
    def test_40_real_probe_is_differentiated_from_unverified_rumor(self):
        m=self.make("hypermap_voi")
        s=m.execute()
        self.assertGreater(s["metrics"]["optional_probes"],0)
        self.assertEqual(s["metrics"]["rumor_was_used_as_evidence"],0)
    def test_41_hypermap_has_material_error_events(self):
        m=self.make()
        m.execute()
        self.assertGreater(len(m.information_gains),0)
        self.assertTrue(all(g["source_root"] in m.per_sector_receipts[g["sector"]]
            for g in m.information_gains))
    def test_42_finished_chain_has_no_unknown_remaining(self):
        m=self.make()
        m.execute()
        self.assertEqual(m.next_action(),"DONE")
        self.assertEqual(m.phase,12)
        self.assertEqual(m.completed_stage_hashes.__len__(),12)
    def test_43_relay_requires_stage_terminal(self):
        m=self.make()
        with self.assertRaisesRegex(GateError,"TERMINAL_BRIDGE_DEPENDENCY_MISSING"):
            m.relay()
    def test_44_survey_and_commit_counts_are_distinct(self):
        m=self.make()
        s=m.execute()
        self.assertEqual(s["metrics"]["surveys"],96)
        self.assertEqual(s["metrics"]["correct_commits"],96)
        self.assertEqual(s["metrics"]["wrong_commits"],s["metrics"]["repair_actions"])
    def test_45_wrong_guess_cannot_be_promoted_without_correct_retry(self):
        m=self.wrong_first_fixture();m.survey();m.decide()
        self.assertNotIn((0,0),m.completed)
        self.assertEqual(m.events[-1]["kind"],"commit_wrong")
        self.assertTrue(m.events[-1]["meta"]["source_root"])
    def test_46_different_policies_produce_distinct_paths_without_relabeling_truth(self):
        a=self.make("static");b=self.make("classical_bayes")
        x=a.order[0][0]
        self.assertEqual(a.owner[0].truth(x),b.owner[0].truth(x))
        s1=a.execute();s2=b.execute()
        self.assertNotEqual(s1["final_chain_hash"],s2["final_chain_hash"])
    def test_47_dev_mini_suite_reports_all_competitors(self):
        r=experiment(seeds=DEV_SEEDS[:2])
        self.assertEqual(len(r["arms"]),4)
        self.assertEqual(set(a["policy"] for a in r["arms"]),set(POLICIES))
        self.assertEqual(r["sequential_required_actions"],219)

if __name__=="__main__":unittest.main()
