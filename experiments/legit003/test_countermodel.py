"""LEGIT-003 falsifiers: partial identification, counterexamples, authority and
independent classical enumeration. Standard library only."""
from __future__ import annotations

from copy import deepcopy
import unittest

from countermodel import HOLD, compile_countermodels, validate, digest
from bridge import demonstrate, from_legit002
from challenge import challenge, brute_force_reference, report
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "legit002"))
from evidence_router import load_packet

class GrammarOfTheUnknownTests(unittest.TestCase):
    def test_neuroscience_research_constructs_actual_countermodels(self):
        r = demonstrate()["compiler_receipt"]
        self.assertEqual(r["total_observed"],353)
        self.assertEqual(r["negative_proxy_observed"],250)
        self.assertEqual(r["negative_proxy_latent_true_bounds"],[0,250])
        self.assertEqual(r["all_latent_true_bounds"],[0,353])
        self.assertEqual(r["verdict"],"NOT_IDENTIFIABLE_FROM_ADMITTED_EVIDENCE")
        low = r["countermodels"]["minimum_latent_target"]
        high = r["countermodels"]["maximum_latent_target"]
        self.assertEqual(sum(x["latent_true"] for x in low),0)
        self.assertEqual(sum(x["latent_true"] for x in high),353)
        self.assertEqual([x["observed"] for x in low],
                         [x["observed"] for x in high])

    def test_current_countermodels_are_logical_not_real_patient_claims(self):
        r=demonstrate()["compiler_receipt"]
        self.assertIsNone(r["individual_probability_of_latent_target"])
        self.assertIsNone(r["model_uncertainty_probability"])
        self.assertFalse(r["language_understanding"])
        self.assertFalse(r["method_learned"])
        self.assertFalse(r["source_authenticated"])
        self.assertFalse(r["real_world_authority"])
        self.assertEqual(r["status"],"RESEARCH_HOLD")
        self.assertEqual(r["next_question"]["route"],"SEEK_INDEPENDENT_MEASUREMENT_VALIDATION")
        self.assertFalse(r["next_question"]["issued"])

    def test_generic_non_neuroscience_transfer_with_opaque_symbols(self):
        case,_=challenge(17)
        result=compile_countermodels(case)
        renamed=deepcopy(case)
        renamed["id"]="DeepSeaProbe_017"
        renamed["latent_target"]="UNSEEN_ORGANISM_EXISTS"
        renamed["observed_proxy"]="SONAR_PATTERN_PRESENT"
        mapping={r["group"]:"deep_sea_sector_"+r["group"] for r in case["observations"]}
        for row in renamed["observations"]:
            row["group"]=mapping[row["group"]]
        for a in renamed["anchors"]:
            a["group"]=mapping[a["group"]]
        other=compile_countermodels(renamed)
        self.assertEqual(result["negative_proxy_latent_true_bounds"],
                         other["negative_proxy_latent_true_bounds"])
        self.assertEqual(result["all_latent_true_bounds"],other["all_latent_true_bounds"])
        self.assertEqual(result["verdict"],other["verdict"])

    def test_128_frozen_hidden_truths_with_independent_enumeration(self):
        r=report()
        self.assertEqual(r["synthetic_cases_checked_against_independent_brute_force"],128)
        self.assertEqual(sum(r["synthetic_breakdown"].values()),128)
        self.assertEqual(r["strong_classical_control"],"EXACT_TIE")

    def test_does_not_learn_latent_truth_from_task_identifier(self):
        task, hidden=challenge(4)
        r=compile_countermodels(task)
        x=deepcopy(task)
        x["id"]="AnotherName"
        s=compile_countermodels(x)
        self.assertEqual(r["all_latent_true_bounds"],s["all_latent_true_bounds"])

    def test_complete_synthetic_negative_falsification(self):
        x,_=challenge(0)
        row=x["observations"][0]
        row["proxy_negative"]=3
        x["anchors"]=[{"group":row["group"],"proxy":"negative",
                       "known_latent_true":1,"known_latent_false":2,
                       "origin":"SIMULATOR_TRUTH"}]
        result=compile_countermodels(x)
        self.assertEqual(result["verdict"],"COUNTEREXAMPLE_ENTAILED_IN_DECLARED_SAMPLE")
        self.assertEqual(result["negative_proxy_latent_true_bounds"][0],1)

    def test_complete_synthetic_exclusion_only_for_sample(self):
        x,_=challenge(0)
        x["anchors"]=[{"group":r["group"],"proxy":"negative",
                       "known_latent_true":0,"known_latent_false":r["proxy_negative"],
                       "origin":"SIMULATOR_TRUTH"}
                      for r in x["observations"]]
        result=compile_countermodels(x)
        self.assertEqual(result["verdict"],"ENTAILS_ABSENCE_ONLY_WITHIN_DECLARED_SAMPLE")
        self.assertEqual(result["negative_proxy_latent_true_bounds"][1],0)

    def test_no_negative_observations_not_a_global_proof(self):
        x,_=challenge(0)
        for row in x["observations"]:
            row["proxy_positive"]+=row["proxy_negative"]
            row["proxy_negative"]=0
        x["anchors"]=[]
        self.assertEqual(compile_countermodels(x)["verdict"],"NO_NEGATIVE_PROXY_CASES")

    def test_no_unauthorized_real_anchors_even_if_sounding_verified(self):
        x,_=from_legit002(load_packet())
        x["anchors"]=[{"group":x["observations"][0]["group"],
                       "proxy":"negative","known_latent_true":1,
                       "known_latent_false":0,"origin":"SIMULATOR_TRUTH"}]
        with self.assertRaises(HOLD):compile_countermodels(x)

    def test_forged_scope_refused(self):
        x,_=challenge(1)
        x["scope"]="CLINICAL_PATIENT_LIVE"
        with self.assertRaises(HOLD):compile_countermodels(x)

    def test_proxy_target_alias_refused(self):
        x,_=challenge(1)
        x["observed_proxy"]=x["latent_target"]
        with self.assertRaises(HOLD):compile_countermodels(x)

    def test_unknown_source_lineage_refused(self):
        x,_=challenge(1)
        x["observations"][0]["source_id"]="OTHER_SOURCE"
        with self.assertRaises(HOLD):compile_countermodels(x)

    def test_counts_reject_bool_float_and_negative(self):
        for bad in (True,1.3,-1,100001):
            x,_=challenge(1)
            x["observations"][0]["proxy_negative"]=bad
            with self.assertRaises(HOLD):compile_countermodels(x)

    def test_contradictory_anchors_refused(self):
        x,_=challenge(0)
        row=x["observations"][0]
        x["anchors"]=[{"group":row["group"],"proxy":"positive",
                       "known_latent_true":row["proxy_positive"],
                       "known_latent_false":1,
                       "origin":"SIMULATOR_TRUTH"}]
        with self.assertRaises(HOLD):compile_countermodels(x)

    def test_duplicate_anchor_refused(self):
        x,_=challenge(0)
        x["anchors"]=x["anchors"][:1]*2
        if not x["anchors"]:
            row=x["observations"][0]
            x["anchors"]=[{"group":row["group"],"proxy":"negative",
                           "known_latent_true":0,"known_latent_false":0,
                           "origin":"SIMULATOR_TRUTH"}]*2
        with self.assertRaises(HOLD):compile_countermodels(x)

    def test_duplicate_groups_refused(self):
        x,_=challenge(17)
        x["observations"].append(deepcopy(x["observations"][0]))
        with self.assertRaises(HOLD):compile_countermodels(x)

    def test_public_source_url_must_be_public_and_curated(self):
        x,_=from_legit002(load_packet())
        x["sources"][0]["url"]="synthetic://forged"
        with self.assertRaises(HOLD):compile_countermodels(x)

    def test_arbitrary_extra_fields_cannot_supply_hidden_truth(self):
        x,_=challenge(1)
        x["actual_consciousness"]=True
        with self.assertRaises(HOLD):compile_countermodels(x)

    def test_read_only_no_executed_questions(self):
        r=compile_countermodels(challenge(1)[0])
        self.assertFalse(r["automated_action"])
        self.assertTrue(r["next_question"] is None or
                        not r["next_question"]["issued"])

    def test_byte_stability(self):
        x,_=challenge(13)
        self.assertEqual(compile_countermodels(x),compile_countermodels(x))
        y=deepcopy(x)
        y["question"]+=" Additional evidence required."
        self.assertNotEqual(digest(x),digest(y))

    def test_independent_enumeration_specific_case(self):
        x,truth=challenge(2)
        bounds=brute_force_reference(x)
        got=compile_countermodels(x)
        for cell in got["cells"]:
            key=(cell["group"],cell["proxy"])
            self.assertEqual((cell["min_target_true"],cell["max_target_true"]),
                             bounds[key])
            self.assertLessEqual(bounds[key][0],truth[key])
            self.assertGreaterEqual(bounds[key][1],truth[key])

if __name__ == "__main__":
    unittest.main()
