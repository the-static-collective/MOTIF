"""All trial fixtures in this file are fabricated for schema tests ONLY."""
import copy
import unittest
from gap_gate import audit,SCHEMA,REQUIRED,PRIMARY

PIN="0ad2cbb656177f76ff29f86793269b14879d9b89"

def fake(n=20):
    """Synthetic fixture never represents actual NovelGym task evidence."""
    rows=[]
    for seed in range(85001,85001+n):
        for policy in REQUIRED:
            rows.append({
                "seed":seed,"policy":policy,"novelty":"fire",
                "pre_solved":True,"immediate_post_solved":False,
                "post_solved_by_budget":policy in ("strong_adaptive_classical","upstream_hybrid_rapidlearn","motif_cognition"),
                "actions_used":5,"cpu_seconds":3.5,
                "owner_receipt":{"independent_environment_owner":True,"synthetic_mock":True},
                "environment_sha":PIN,"action_budget":20,
            })
    return {"schema":SCHEMA,"source":"EXTERNALLY_EXECUTED_NOVELGYM",
            "predeclared_task":PRIMARY,"source_pin":PIN,"protocol_frozen":True,
            "rows":rows}


class GateFalsifiers(unittest.TestCase):
    def test_no_runtime_results_means_explicit_hold(self):
        self.assertEqual(audit({"schema":SCHEMA,"rows":[]})["status"],"HOLD_NO_EXTERNAL_TRIALS")
    def test_no_fake_external_runner(self):
        e=fake();e["source"]="AUTHOR_WRITTEN_SIMULATOR"
        self.assertEqual(audit(e)["status"],"HOLD_NOT_EXTERNAL_ENVIRONMENT")
    def test_no_moving_goalposts(self):
        e=fake();e["predeclared_task"]="an-easier-task"
        self.assertEqual(audit(e)["status"],"HOLD_UNREGISTERED_PRIMARY_TASK")
    def test_source_pin_must_match(self):
        e=fake();e["rows"][0]["environment_sha"]="changed"
        self.assertEqual(audit(e)["status"],"HOLD_WRONG_ENVIRONMENT_SOURCE")
    def test_original_protocol_frozen(self):
        e=fake();e["protocol_frozen"]=False
        self.assertEqual(audit(e)["status"],"HOLD_UNVERIFIED_PROTOCOL_OR_PIN")
    def test_no_missing_owner_receipts(self):
        e=fake();e["rows"][0].pop("owner_receipt")
        self.assertEqual(audit(e)["status"],"HOLD_MISSING_OUTCOME_OR_OWNER_RECEIPT")
    def test_owner_receipt_must_claim_independent(self):
        e=fake();e["rows"][0]["owner_receipt"]={"synthetic_mock":True}
        self.assertEqual(audit(e)["status"],"HOLD_NO_OWNER_VERIFICATION")
    def test_all_strong_arms_must_have_same_seeds(self):
        e=fake();e["rows"].pop(0)
        self.assertEqual(audit(e)["status"],"HOLD_UNMATCHED_ARMS")
    def test_deduplicate_cases(self):
        e=fake();e["rows"].append(copy.deepcopy(e["rows"][0]))
        self.assertEqual(audit(e)["status"],"HOLD_DUPLICATE_CASE")
    def test_action_budgets_identical(self):
        e=fake();e["rows"][1]["action_budget"]=15
        self.assertEqual(audit(e)["status"],"HOLD_UNMATCHED_ACTION_BUDGET")
    def test_no_budget_override(self):
        e=fake();e["rows"][0]["actions_used"]=21
        self.assertEqual(audit(e)["status"],"HOLD_OVER_BUDGET")
    def test_not_enough_independent_seeds(self):
        self.assertEqual(audit(fake(5))["status"],"HOLD_TOO_FEW_MATCHED_SEEDS")
    def test_equal_good_adaptive_is_not_motif_superiority(self):
        r=audit(fake())
        self.assertEqual(r["status"],"SCORABLE_DESCRIPTIVE_ONLY")
        self.assertEqual(r["motif_minus_adaptive_pairwise"],
                         {"wins":0,"losses":0,"ties":20})
        self.assertIsNone(r["motif_outperformed_strong_classical"])
        self.assertEqual(r["wins"]["static_pddl"],0)
    def test_even_motif_win_remains_unverified_descriptive_only(self):
        e=fake()
        for row in e["rows"]:
            if row["policy"]=="strong_adaptive_classical" and row["seed"]==85001:
                row["post_solved_by_budget"]=False
        r=audit(e)
        self.assertEqual(r["status"],"SCORABLE_DESCRIPTIVE_ONLY")
        self.assertEqual(r["motif_minus_adaptive_pairwise"]["wins"],1)
        self.assertIsNone(r["motif_outperformed_strong_classical"])

if __name__=="__main__":
    unittest.main()
