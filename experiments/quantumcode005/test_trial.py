"""QC-005: adversarial foreign-world and impossible-problem controls."""
from __future__ import annotations

from dataclasses import replace
import unittest
import networkx as nx

from foreign_worlds import (
    UnsupportedDomain, hosts, normalize_native, topology, oracle,
    expected_graph, count_external, native_signature,
)
from classical_control import train_control, nx_rel, effect_mapping
from trial import (
    TASKS, STATUS, freeze_models, foreign_evaluation,
    paired_isolation_unsupported, unsupported_certificate, run,
)
from gardener import (
    discover, review, fixtures, query, apply, replay, Expr,
    equivalent_new,
)
from aperture import Graph, edge, infer_delta, apply_template


class ForeignWorldChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models = freeze_models()
        cls.foreign = hosts()
        cls.report = run()

    def test_frozen_models_are_prior_qc004_models(self):
        self.assertEqual(
            {task: self.models[task].proposal.program.code() for task in TASKS},
            {"alternate_path":"TC(CUT)",
             "triangle":"JOIN(CUT,CUT)",
             "square":"JOIN(CUT,JOIN(CUT,CUT))"},
        )

    def test_none_of_foreign_test_graphs_is_a_training_or_validation_graph(self):
        internal = {
            e.before.receipt()
            for task in TASKS for split in fixtures(task)[:2] for e in split
        }
        external = {topology(graph).receipt() for _, graph in self.foreign}
        self.assertFalse(internal & external)
        self.assertEqual(len(external),len(self.foreign))

    def test_third_party_hosts_have_diverse_topology(self):
        self.assertEqual(len(self.foreign),12)
        vcounts = {len(g.nodes) for _,g in self.foreign}
        degrees = {tuple(sorted(d for _,d in g.degree)) for _,g in self.foreign}
        self.assertGreaterEqual(len(vcounts),8)
        self.assertGreaterEqual(len(degrees),8)

    def test_undirected_import_normalizes_mixed_node_types(self):
        native = nx.grid_2d_graph(3,4)
        translated=normalize_native(native)
        result=topology(translated)
        self.assertEqual(len(result.vertices),12)
        self.assertEqual(len(result.edges),17)
        self.assertTrue(all(str(v).startswith("foreign-") for v in result.vertices))

    def test_structural_import_does_not_smuggle_native_metadata(self):
        native=nx.karate_club_graph()
        imported=normalize_native(native)
        self.assertFalse(any(dict(fields) for _,fields in imported.nodes(data=True)))
        self.assertFalse(any(dict(fields) for *_,fields in imported.edges(data=True)))

    def test_directed_graph_domain_holds(self):
        direct=nx.DiGraph([(0,1),(1,2)])
        with self.assertRaises(UnsupportedDomain):
            normalize_native(direct)
        with self.assertRaises(UnsupportedDomain):
            topology(direct)

    def test_multigraph_domain_holds(self):
        multi=nx.MultiGraph([(0,1),(0,1)])
        with self.assertRaises(UnsupportedDomain):
            normalize_native(multi)

    def test_self_loop_domain_holds(self):
        source=nx.Graph([(0,0),(0,1)])
        with self.assertRaises(UnsupportedDomain):
            normalize_native(source)

    def test_oracle_is_not_synonym_for_generic_reachability(self):
        path=nx.Graph([(0,1),(1,2),(2,3)])
        cycle3=nx.cycle_graph(3)
        cycle4=nx.cycle_graph(4)
        self.assertFalse(oracle("alternate_path",path,(0,1)))
        self.assertTrue(oracle("alternate_path",cycle3,(0,1)))
        self.assertTrue(oracle("triangle",cycle3,(0,1)))
        self.assertFalse(oracle("triangle",cycle4,(0,1)))
        self.assertTrue(oracle("square",cycle4,(0,1)))
        self.assertFalse(oracle("square",cycle3,(0,1)))

    def test_foreign_oracle_is_not_learners_graph_relation_interpreter(self):
        for task in TASKS:
            for _,graph in self.foreign:
                before=topology(graph)
                model=self.models[task]
                for ab in graph.edges:
                    ab=edge(*ab)
                    self.assertEqual(
                        query(model.proposal.program,before,ab),
                        oracle(task,graph,ab),
                    )

    def test_foreign_geometry_equals_independently_constructed_oracle(self):
        for task in TASKS:
            for _,graph in self.foreign:
                before=topology(graph)
                for target in graph.edges:
                    answer=apply(before,edge(*target),self.models[task])
                    self.assertIsNotNone(answer)
                    expected=expected_graph(task,graph,edge(*target))
                    self.assertTrue(equivalent_new(before,expected,answer.graph))

    def test_heldout_mixed_host_accuracy(self):
        for task,result in self.report["foreign_performance"].items():
            self.assertEqual(result["wrong"],0,task)
            self.assertEqual(result["held"],0,task)
            self.assertEqual(result["correct_relation"],result["edges"],task)
            self.assertEqual(result["correct_result_graph"],result["edges"],task)

    def test_each_oracle_class_occurs_externally(self):
        for task,result in self.report["foreign_performance"].items():
            self.assertGreater(result["oracle_positive"],0,task)
            self.assertGreater(result["oracle_negative"],0,task)

    def test_symbol_names_not_explanations(self):
        _,graph=self.foreign[-1]
        relabeled=nx.relabel_nodes(graph,{node:"stranger::"+node for node in graph.nodes})
        for task in TASKS:
            original=foreign_evaluation(task,self.models[task],(("a",graph),))
            renamed=foreign_evaluation(task,self.models[task],(("b",relabeled),))
            for k in ("edges","correct_relation","correct_result_graph","wrong","held"):
                self.assertEqual(original[k],renamed[k])

    def test_no_training_update_from_foreign_benchmark(self):
        pins={name:model.pin() for name,model in self.models.items()}
        for task in TASKS:
            foreign_evaluation(task,self.models[task],self.foreign[:2])
        self.assertEqual(pins,{name:model.pin() for name,model in self.models.items()})

    def test_external_graph_manifest_is_stable_with_fixed_seeds(self):
        manifest=count_external()
        self.assertEqual(len(manifest),12)
        self.assertEqual(len({r["sha256"] for r in manifest}),12)
        self.assertTrue(all(len(r["sha256"])==64 for r in manifest))

    def test_isolated_node_parity_counterexamples_have_opposite_effects(self):
        data=paired_isolation_unsupported()
        self.assertEqual(len(data),6)
        for i in range(0,len(data),2):
            one,two=data[i:i+2]
            a,delta_a=infer_delta(one)
            b,delta_b=infer_delta(two)
            self.assertEqual(a,b)
            self.assertNotEqual(delta_a,delta_b)
            self.assertEqual(len(two.before.vertices),len(one.before.vertices)+1)

    def test_entire_declared_dsl_cannot_detect_isolated_node(self):
        result=unsupported_certificate(paired_isolation_unsupported())
        self.assertEqual(result["status"],"HOLD_UNEXPRESSIBLE_IN_DECLARED_DSL")
        self.assertFalse(result["candidate_admitted"])
        self.assertEqual(result["accidental_distinguishing_programs"],[])
        self.assertGreater(result["programs_checked"],100)
        self.assertEqual(result["indistinguishable_relational_programs"],
                         result["programs_checked"])

    def test_unsupported_problem_does_not_trigger_expansion_without_approval(self):
        self.assertIsNone(discover(paired_isolation_unsupported()))

    def test_no_unknown_semantics_silently_guessed(self):
        graph=self.foreign[0][1]
        target=next(iter(graph.edges))
        with self.assertRaises(UnsupportedDomain):
            oracle("edge_weight_is_large",graph,edge(*target))
        with self.assertRaises(UnsupportedDomain):
            expected_graph("molecular_bond_direction",graph,edge(*target))

    def test_forged_review_pin_invalidates_prediction_replay(self):
        model=self.models["square"]
        before=topology(self.foreign[0][1])
        chosen=next(iter(before.edges))
        generated=apply(before,chosen,model)
        self.assertEqual(replay(before,generated,model),generated)
        fake=replace(model,validation_hash="new-evidence-not-reviewed")
        self.assertIsNone(replay(before,generated,fake))

    def test_validation_with_conflict_refuses_selected_rule(self):
        train,valid,_=fixtures("triangle")
        candidate=discover(train)
        original=valid[0]
        ab,_=infer_delta(original)
        contra=infer_delta(valid[1])[1]
        wrong_after=apply_template(original.before,ab,contra)
        corrupted=(replace(original,after=wrong_after),)+valid[1:]
        self.assertIsNone(review(candidate,train,corrupted))

    def test_malformed_expression_cannot_be_executed(self):
        graph=topology(self.foreign[0][1])
        chosen=next(iter(graph.edges))
        with self.assertRaises(ValueError):
            query(Expr("EVAL_STRING"),graph,chosen)

    def test_matched_data_classical_program_search_matches_frozen_learner(self):
        for task in TASKS:
            train, valid, _ = fixtures(task)
            classical=train_control(train,valid)
            ours=self.models[task]
            self.assertEqual(classical["status"],"CLASSICAL_VALIDATED",task)
            self.assertEqual(classical["program"],ours.proposal.program.code(),task)
            self.assertEqual(classical["tested"],ours.proposal.examined,task)

    def test_separately_interpreted_classical_learner_ties_on_all_foreign_edges(self):
        baseline=self.report["matched_grammar_classical_learner"]
        for task in TASKS:
            result=baseline[task]
            self.assertEqual(result["status"],"CLASSICAL_VALIDATED")
            self.assertTrue(result["matches_MOTIF_program"])
            self.assertEqual(result["foreign"]["correct"],
                             result["foreign"]["total"])
            self.assertEqual(result["foreign"]["total"],
                             self.report["foreign_performance"][task]["edges"])

    def test_classical_control_is_independent_evaluator_not_our_query(self):
        world=topology(self.foreign[0][1])
        for task in TASKS:
            expr=self.models[task].proposal.program
            for pair in list(world.edges)[:12]:
                self.assertEqual(nx_rel(expr,world,pair),query(expr,world,pair))

    def test_cross_split_refused_by_independent_classical_learner(self):
        train, valid, _=fixtures("triangle")
        corrupted=(replace(valid[0],evidence_id=train[0].evidence_id),)+valid[1:]
        with self.assertRaises(ValueError):
            train_control(train,corrupted)

    def test_detailed_failure_and_fairness_provenance_preserved(self):
        x=self.report
        self.assertEqual(x["status"],STATUS)
        self.assertTrue(x["baseline_receives_semantic_task_name"])
        self.assertTrue(x["equal_sample_and_AST_budget_classical_learner"])
        self.assertFalse(x["equal_cpu_or_wallclock_budget"])
        self.assertFalse(x["production_installation"])
        self.assertFalse(x["quantum_execution"])
        self.assertEqual(x["external_actions"],0)


if __name__=="__main__":
    unittest.main()
