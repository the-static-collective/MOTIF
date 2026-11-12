"""Independent falsifiers for Error Dividend; holdout never used for tuning."""
import math
import unittest
from error_dividend import (INPUTS,HELDOUT,DEV,POLICIES,REGIMES,BUDGETS,
    Owner,episode,experiment,initial_posterior,favorite,outputs,
    expected_ig,choose,update,accuracy,entropy)

class DividendTest(unittest.TestCase):
    def test_01_hidden_truth_not_provided_to_policy(self):
        o=Owner(DEV[0],"truthful")
        r=initial_posterior(o)
        self.assertEqual(len(r),8)
        self.assertAlmostEqual(sum(r),1.0)
    def test_02_owner_is_deterministic_across_identical_seeds(self):
        a,b=Owner(DEV[2],"truthful"),Owner(DEV[2],"truthful")
        self.assertEqual(a.initial,b.initial)
        self.assertEqual([a.truth(x) for x in INPUTS],[b.truth(x) for x in INPUTS])
    def test_03_policy_budgets_exhaustion(self):
        for policy in POLICIES:
            r=episode(DEV[3],"truthful",policy,3)
            self.assertLessEqual(r["probes"],3)
            self.assertEqual(r["probes"],0 if policy=="no_probe" else 3)
    def test_04_no_probe_computes_baseline_without_spending(self):
        r=episode(DEV[5],"truthful","no_probe",3)
        self.assertEqual(r["start_accuracy"],r["final_accuracy"])
        self.assertEqual(r["net_utility"],r["final_accuracy"])
    def test_05_classical_ig_is_maximizer(self):
        o=Owner(DEV[8],"truthful")
        w=initial_posterior(o)
        rem=tuple(x for x in INPUTS if x!=o.start_x)
        chosen=choose("classical_ig",w,rem,o.seed,0)
        self.assertAlmostEqual(expected_ig(w,chosen),max(expected_ig(w,x) for x in rem))
    def test_06_wrong_is_provisional_not_published(self):
        r=episode(DEV[1],"truthful","challenge_favorite",3)
        self.assertTrue(all("published" not in row for row in r["records"]))
        self.assertTrue(all(row["reported_kind"]=="SOURCE_REPORT" for row in r["records"]))
    def test_07_false_echo_never_double_counts(self):
        r=episode(DEV[7],"echo_origin","classical_ig",3)
        self.assertEqual(r["echo_ignored"],3)
        self.assertEqual(r["final_accuracy"],r["start_accuracy"])
    def test_08_absent_verification_does_not_move_posterior(self):
        r=episode(DEV[0],"no_feedback","challenge_favorite",3)
        self.assertEqual(r["hold_no_feedback"],3)
        self.assertEqual(r["final_accuracy"],r["start_accuracy"])
    def test_09_missing_feedback_must_not_earn_net_gain(self):
        r=episode(DEV[0],"no_feedback","classical_ig",2)
        self.assertLess(r["net_utility"],r["final_accuracy"])
    def test_10_source_report_may_be_inaccurate_in_noise_regime(self):
        vals=[episode(s,"noise20","uniform_random",3) for s in DEV]
        self.assertGreater(sum(r["false_reports"] for r in vals),0)
    def test_11_wrong_is_not_automatically_useful(self):
        vals=[episode(s,"truthful","challenge_favorite",3) for s in DEV]
        self.assertTrue(any(r["wrong_no_gain"] for r in vals))
    def test_12_credible_error_can_change_posterior(self):
        vals=[episode(s,"truthful","challenge_favorite",3) for s in DEV]
        self.assertGreater(sum(r["verified_wrong"] for r in vals),0)
        self.assertGreater(sum(r["wrong_helpful_net"] for r in vals),0)
    def test_13_strong_classical_can_be_equal_or_better(self):
        sample=experiment(DEV)
        self.assertTrue(any("classical_ig" in x["winner_ties"] for x in sample["winners"]))
        self.assertTrue(all(x["net_utility"]<=x["final_accuracy"]+1e-9
          for x in [episode(DEV[1],"truthful","classical_ig",2)]))
    def test_14_bayesian_posteriors_normalize(self):
        w=[1/8]*8
        for x in INPUTS:
            w,changed=update(w,x,0,.2)
            self.assertTrue(changed)
            self.assertAlmostEqual(sum(w),1.0)
            self.assertTrue(all(p>=0 for p in w))
    def test_15_not_revealing_hidden_truth_id_to_policy_api(self):
        o=Owner(DEV[9],"truthful")
        rem=tuple(x for x in INPUTS if x!=o.start_x)
        for policy in POLICIES[:-1]:
            chosen=choose(policy,initial_posterior(o),rem,o.seed,0)
            self.assertIn(chosen,rem)
    def test_16_holdout_seed_lists_are_disjoint(self):
        self.assertTrue(set(DEV).isdisjoint(HELDOUT))
    def test_17_not_rewarded_for_multiple_wrong_reports(self):
        r=episode(DEV[12],"truthful","challenge_favorite",3)
        self.assertLessEqual(r["wrong_helpful_net"],r["verified_wrong"])
    def test_18_all_runs_return_accuracy_and_net_utility(self):
        report=experiment(DEV)
        self.assertEqual(len(report["conditions"]),len(REGIMES)*len(BUDGETS)*len(POLICIES))
        self.assertTrue(all(0<=r["end_accuracy"]<=1 for r in report["conditions"]))
        self.assertEqual(report["real_model"],False)

if __name__=="__main__": unittest.main()
