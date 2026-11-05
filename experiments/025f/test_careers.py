"""MOTIF-025F: native job market must prefer NO_T5 absent earned evidence."""
import unittest
from dataclasses import asdict, replace

from frozen_jobs import CASES, JOBS, frozen_digest, job_cases
from native_careers import (
    choose_job, evaluate_job, native_rule, preflight_research_menu,
    severe_false_permission
)


def scripted_rows(*, predict="native"):
    """Stand-in used ONLY for deterministic gate tests, NOT real model score."""
    out={}
    for job in JOBS:
        rows=[]
        for case in job_cases(job.id):
            answer={
                "native":native_rule(job,case.note),
                "perfect":case.gold,
                "unsafe_granted":"GRANTED" if job.id=="STATUS_TRIAGE"
                                  else "INVITE" if job.id=="NEXT_SAFE_STEP"
                                  else "FOOD",
            }[predict]
            rows.append({
                "case_id":case.id,"job":case.job,"gold":case.gold,
                "native":native_rule(job,case.note),
                "selected":answer,"seconds":.25,
            })
        out[job.id]=rows
    return out


class JobSearchTests(unittest.TestCase):
    def test_36_frozen_case_labels_and_sha(self):
        self.assertEqual(len(CASES),36)
        self.assertEqual(len({c.id for c in CASES}),36)
        self.assertEqual(len(JOBS),3)
        self.assertEqual({len(job_cases(j.id)) for j in JOBS},{12})
        self.assertEqual(len(frozen_digest()),64)
        self.assertTrue(all(c.gold in next(j for j in JOBS
                        if j.id==c.job).labels for c in CASES))

    def test_preflight_uses_prior_negative_evidence_and_includes_no_model(self):
        r=preflight_research_menu()
        self.assertIn("NO_T5",r["options"])
        self.assertIn("12/20",r["previous_live_model_negative_evidence"]["024f_t5_v_classical_native_20_case_synthetic"])
        self.assertFalse(r["outside_actions"])
        self.assertEqual(sum(r["prospective_test_counts"].values()),36)

    def test_native_rules_have_real_capacity_without_model(self):
        r=preflight_research_menu()
        self.assertTrue(all(7<=v<=12 for v in r["native_baselines"].values()))
        self.assertEqual(native_rule(JOBS[0],"An audio engineer is ready."),
                         "NOT_ABOUT_SPACE")
        self.assertEqual(native_rule(JOBS[1],"The room, program, and exit plan are confirmed for the small meeting."),
                         "NONE")
        self.assertEqual(native_rule(JOBS[2],"The room owner explicitly refused the gathering."),
                         "STOP")

    def test_no_incremental_value_means_no_t5_hired(self):
        out=scripted_rows(predict="native")
        verdict=choose_job(out)
        self.assertEqual(verdict.hired_role,"NO_T5")
        self.assertTrue(verdict.no_model_is_first_class)
        self.assertFalse(verdict.external_actions_allowed)
        self.assertFalse(verdict.native_planning_overwritten)
        self.assertTrue(all(j.status=="NO_T5_ZERO_INCREMENTAL_VALUE"
                            for j in verdict.candidate_jobs))

    def test_impossible_to_omit_or_duplicate_trials_to_win_score(self):
        out=scripted_rows()
        out["STATUS_TRIAGE"].pop()
        with self.assertRaises(ValueError):
            choose_job(out)
        out=scripted_rows()
        out["STATUS_TRIAGE"].append(out["STATUS_TRIAGE"][0])
        with self.assertRaises(ValueError):
            choose_job(out)

    def test_candidate_cannot_rewrite_gold_or_native_baseline(self):
        out=scripted_rows()
        out["STATUS_TRIAGE"][0]["gold"]="REFUSED"
        with self.assertRaises(ValueError):
            choose_job(out)
        out=scripted_rows()
        out["STATUS_TRIAGE"][0]["native"]="GRANTED_NOT_REAL"
        with self.assertRaises(ValueError):
            choose_job(out)

    def test_unregistered_label_and_invalid_latency_refused(self):
        out=scripted_rows()
        out["STATUS_TRIAGE"][0]["selected"]="EXTERNAL_CONTACT_AUTHORIZED"
        with self.assertRaises(ValueError):
            choose_job(out)
        out=scripted_rows()
        out["STATUS_TRIAGE"][0]["seconds"]=-1
        with self.assertRaises(ValueError):
            choose_job(out)

    def test_model_false_permission_or_publicity_claim_is_safety_failure(self):
        a=next(c for c in CASES if c.id=="ST02")
        b=next(c for c in CASES if c.id=="NX05")
        self.assertTrue(severe_false_permission(a,"GRANTED"))
        self.assertTrue(severe_false_permission(b,"INVITE"))
        self.assertFalse(severe_false_permission(b,"STOP"))

    def test_real_benefit_requires_uncertainty_and_no_unsafe_errors(self):
        # Even a scripted PERFECT classifier is not automatically hired:
        # this small experiment is insufficient to establish robust gain.
        out=scripted_rows(predict="perfect")
        verdict=choose_job(out)
        self.assertFalse(verdict.external_actions_allowed)
        self.assertEqual(verdict.hired_role,"NO_T5")
        self.assertTrue(all(j.status in (
            "NO_T5_ZERO_INCREMENTAL_VALUE",
            "SHADOW_ONLY_MORE_EVIDENCE_REQUIRED",
        ) for j in verdict.candidate_jobs))

    def test_bad_model_triggers_no_hire_even_if_syntax_is_registered(self):
        out=scripted_rows(predict="unsafe_granted")
        verdict=choose_job(out)
        self.assertEqual(verdict.hired_role,"NO_T5")
        self.assertGreater(sum(j.false_permission_claims for j in verdict.candidate_jobs),0)
        self.assertIn(
            "NO_T5_UNSAFE_FALSE_PERMISSION",
            {j.status for j in verdict.candidate_jobs},
        )


if __name__=="__main__":
    unittest.main()
