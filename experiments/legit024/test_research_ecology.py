"""Adversarial LEGIT-024 tests: independent acceptance, fallback, provenance."""
from __future__ import annotations

from hashlib import sha256
from unittest.mock import patch
from pathlib import Path
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "legit021"))
sys.path.insert(0, str(HERE.parent / "legit022"))
sys.path.insert(0, str(HERE.parent / "legit023"))
sys.path.insert(0, str(HERE))
from portfolio import (
    METHODS, Refuse, native_poly, poly_value, sympy_poly, exhaustive_opt,
    try_method, verify, brute_isomorphic, execute_portfolio, NOT_INTEGRATED,
)
from fixtures import suite, A, C, M, P, X, sym_task, opt_task
# LEGIT-022 and this directory both have trial.py. The older module is
# intentionally imported by 023; load this experiment under a unique name.
from importlib.util import spec_from_file_location, module_from_spec
_spec=spec_from_file_location("legit024_ecology_trial", HERE / "trial.py")
_module=module_from_spec(_spec)
_spec.loader.exec_module(_module)
run, train_selector = _module.run, _module.train_selector


class ResearchEcologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.training, cls.heldout, cls.origin = suite()

    def test_four_distinct_goal_contracts_and_planned_held_adapters(self):
        self.assertEqual(set(METHODS), {
            "polynomial_identity", "bounded_integer_optimum",
            "graph_nonisomorphism", "graph_hom_witness"})
        self.assertIn("Lean4_mathlib_formal_certificates", NOT_INTEGRATED)
        self.assertNotIn("Lean4_mathlib_formal_certificates",
                         sum((list(x) for x in METHODS.values()), []))

    def test_no_untrusted_python_code_execution_from_poly_input(self):
        with self.assertRaises(Refuse):
            native_poly(["__import__", "os", "system", "echo BAD"])
        with self.assertRaises(Refuse):
            native_poly(["pow", X(), 1000000])
        with self.assertRaises(Refuse):
            native_poly(["const", True])

    def test_identity_and_counterexample_across_three_methods(self):
        true = sym_task("binomial", P(A(X(), C(2)), 2),
                        A(A(P(X(), 2), M(C(4), X())), C(4)),
                        "training")
        false = sym_task("not_binomial", P(A(X(), C(2)), 2),
                         A(A(P(X(), 2), M(C(4), X())), C(5)),
                         "training")
        for method in METHODS["polynomial_identity"]:
            yes = try_method(true, method)
            no = try_method(false, method)
            self.assertEqual(yes["status"], "VERIFIED", method)
            self.assertEqual(yes["certificate"]["verdict"], "IDENTITY")
            self.assertEqual(no["status"], "VERIFIED", method)
            self.assertEqual(no["certificate"]["verdict"], "COUNTEREXAMPLE")
            self.assertNotEqual(*no["certificate"]["values"])

    def test_symbolic_sample_agreement_never_promoted_as_proof(self):
        # x(x-1)(x-2) and zero agree at all three sample points,
        # but exact symbolic checks identify non-equivalence.
        p = M(M(X(), A(X(), C(-1))), A(X(), C(-2)))
        t = sym_task("sample_trap", p, C(0), "training")
        result = try_method(t, "motif_sample_then_certify")
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["certificate"]["verdict"], "COUNTEREXAMPLE")
        self.assertTrue(all(a == b for _,a,b in
                            result["certificate"]["observations"]))
        fake = {"verdict": "IDENTITY"}
        with self.assertRaises(Refuse):
            verify(t, "motif_sample_then_certify", fake)

    def test_native_sympy_polynomial_coefficients_independent_agreement(self):
        for task in [t for t in self.training + self.heldout
                     if t["kind"] == "polynomial_identity"]:
            self.assertEqual(native_poly(task["left"]),sympy_poly(task["left"]))
            self.assertEqual(native_poly(task["right"]),sympy_poly(task["right"]))

    def test_integer_optimization_all_three_adapters_exact(self):
        tasks = [
            opt_task("feasible", [[0,3],[0,3]], [2,1],
                     [{"a":[1,1], "op":">=", "b":3}], "training"),
            opt_task("infeasible", [[0,2],[0,2]], [2,-1],
                     [{"a":[1,1], "op":">=", "b":5}], "training"),
        ]
        for case in tasks:
            for method in METHODS["bounded_integer_optimum"]:
                response = try_method(case,method)
                self.assertEqual(response["status"], "VERIFIED",
                                 (case["id"],method,response))
                self.assertEqual(response["certificate"]["verdict"],
                                 exhaustive_opt(case)["verdict"])

    def test_false_optimality_or_invalid_sat_witness_rejected(self):
        case = opt_task("verify_false", [[0,2]], [1],
                        [{"a":[1], "op":">=", "b":1}], "training")
        wrong = {"verdict": "OPTIMUM", "value":2,"assignment":[2]}
        with self.assertRaises(Refuse):
            verify(case,"z3_optimize",wrong)
        malicious = {"verdict":"INFEASIBLE"}
        with self.assertRaises(Refuse):
            verify(case,"ortools_cp_sat",malicious)

    def test_large_integer_search_refuses_before_solver(self):
        bad = opt_task("bad", [[0,15]]*4,[1]*4,[],"training")
        r=try_method(bad,"z3_optimize")
        self.assertEqual(r["status"],"REJECTED")
        self.assertIn("too many",r["reason"])

    def test_wl_inconclusive_vs_exact_noniso(self):
        cyc = (6,tuple((i,(i+1)%6) for i in range(6)))
        dis = (6,((0,1),(1,2),(2,0),(3,4),(4,5),(5,3)))
        self.assertFalse(brute_isomorphic(cyc,dis))
        t={"id":"c6_two_triangles", "kind":"graph_nonisomorphism",
           "graphs":(cyc,dis)}
        wl=try_method(t,"joint_1wl")
        self.assertEqual(wl["status"],"ABSTAIN")
        fallback=execute_portfolio(t,("joint_1wl","vf2pp"))
        self.assertEqual(fallback["status"],"VERIFIED")
        self.assertEqual(fallback["method_count"],2)
        self.assertEqual(fallback["tried"][-1]["status"],"VERIFIED")

    def test_one_external_atlas_hom_witness_is_exactly_checked(self):
        case=next(t for t in self.heldout
                  if t["kind"]=="graph_hom_witness")
        for method in METHODS["graph_hom_witness"]:
            r=try_method(case,method)
            self.assertEqual(r["status"],"VERIFIED")
            self.assertNotEqual(*r["certificate"]["values"])

    def test_predeclared_external_graph_split_and_honest_authorship(self):
        self.assertEqual(self.origin["atlas_graphs"],1253)
        self.assertEqual(self.origin["atlas_data_sha256"],
            "73fc416df0164923607751cb759f4ae81deb5f6550bf25be59c86de3b747e41d")
        tr={t["id"] for t in self.training}
        ev={t["id"] for t in self.heldout}
        self.assertFalse(tr & ev)
        self.assertEqual(len([t for t in self.heldout
                              if t["kind"]=="graph_hom_witness"]),28)
        self.assertTrue(any(t["source"].startswith("ENGINEER_AUTHORED")
                            for t in self.heldout))

    def test_freeze_is_derived_from_training_only(self):
        ranking, receipt=train_selector(self.training)
        stamp=json.dumps(ranking,sort_keys=True,separators=(",",":")).encode()
        self.assertEqual(receipt["method_order_sha256"],
                         sha256(stamp).hexdigest())
        self.assertTrue(receipt["only_training_queries_used_for_ranking"])
        for kind in METHODS:
            self.assertEqual(set(ranking[kind]),set(METHODS[kind]))

    def test_all_staged_research_cases_evaluated_without_unverified_promotion(self):
        report=run()
        self.assertEqual(report["experiment"],"MOTIF-LEGIT-024")
        outcomes=report["matched_heldout_evaluations"]
        self.assertTrue(outcomes["fixed_classical_priority"]["all_verified"])
        self.assertTrue(outcomes["learned_training_only_priority"]["all_verified"])
        self.assertIn("multi-generation autonomous compounding",
                      report["criteria_for_future_ability_not_yet_measured"])
        # Previous investigations: inherited MOTIF sources need 60 questions;
        # the trained classical question-optimal source order needs 47.
        # The numbers are independently checked full attempted-query receipts,
        # not inferred only from the final successful graph source.
        self.assertEqual(outcomes["fixed_classical_priority"]["by_family"]
                         ["graph_hom_witness"]["total_explicit_source_questions"], 60)
        self.assertEqual(outcomes["learned_training_only_priority"]["by_family"]
                         ["graph_hom_witness"]["total_explicit_source_questions"], 47)
        for arm in outcomes.values():
            for row in arm["per_case"]:
                self.assertEqual(row["status"],"VERIFIED")
                self.assertTrue(row["tried"][-1]["verification"])
                self.assertGreaterEqual(row["method_count"],1)


if __name__ == "__main__":
    unittest.main()
