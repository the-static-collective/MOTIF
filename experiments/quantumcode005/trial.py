"""MOTIF QC-005: frozen grammar gardener meets foreign topologies.

No TEST-driven program selection. "Foreign" = NetworkX graph implementations
outside QC-004's hand-constructed ring/tail teaching distribution.
The tasks are still researcher-selected and independently known; the result
must not be described as autonomous cross-domain concept acquisition.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quantumcode004"))
from gardener import (
    MAX_AST_COST, Expr, Garden, apply, discover, fixtures, grammar, query,
    review, oracle_edit, evaluator_graph, equivalent_new,
)
from aperture import Episode, infer_delta, Graph, edge
from foreign_worlds import (
    UnsupportedDomain, count_external, expected_graph, hosts,
    normalize_native, oracle, topology,
)
import networkx as nx
from classical_control import train_control, external_control_accuracy

TASKS = ("alternate_path", "triangle", "square")
STATUS = "FROZEN_MODEL_FOREIGN_GRAPH_EVALUATION_ONLY"


def freeze_models():
    """Never import foreign test graphs into the learner or review gates."""
    models = {}
    for task in TASKS:
        train, valid, _internal_test = fixtures(task)
        proposal = discover(train)
        if proposal is None:
            raise AssertionError("Frozen internal learner unexpectedly failed")
        model = review(proposal, train, valid)
        if model is None:
            raise AssertionError("Frozen independent validation failed")
        models[task] = model
    return models


def paired_isolation_unsupported():
    """A typed expressivity gap the entire QC-004 grammar cannot repair.

    Add one completely isolated vertex to the same graph, same old anchor.
    Every allowed binary relation expression has identical truth on the
    original endpoints, by induction on AST structure. The evaluator asks
    for different edit effects depending on the isolated vertex. No finite
    instance of the declared DSL can represent the requested classification.
    """
    records = []
    for i in range(3):
        # Three different conventional path lengths; same anchor per pair.
        original = [f"p{i}_{n}" for n in range(4+i)]
        edges = [edge(original[j],original[j+1])
                 for j in range(len(original)-1)]
        for condition in (False, True):
            before = Graph.of(set(original) | ({f"isolated_{i}"} if condition else set()),
                              edges)
            a,b = edge(original[0],original[1])
            n0,n1=f"added_{i}_{condition}_0",f"added_{i}_{condition}_1"
            added = {edge(a,n0),edge(n0,n1),edge(n1,b)}
            after = Graph.of(before.vertices | {n0,n1},
                             (before.edges - ({edge(a,b)} if condition else set())) |
                             added)
            records.append(Episode(f"TRAIN/isolation/{i}/{condition}",
                                   "TRAIN", before, after))
    return tuple(records)


def unsupported_certificate(records: tuple[Episode, ...]):
    # The structural oracle labels the paired examples differently.
    # Exhaust the full *finite* QC-004 AST grammar up to cost 5; each query
    # gives exactly equal values in each same-anchor pair.
    cases = []
    for i in range(0,len(records),2):
        a,b = records[i:i+2]
        anchor_a, effect_a = infer_delta(a)
        anchor_b, effect_b = infer_delta(b)
        assert anchor_a == anchor_b and effect_a != effect_b
        cases.append((a.before,b.before,anchor_a))
    considered = 0
    counterexamples = []
    for expr in grammar(MAX_AST_COST):
        considered += 1
        for left,right,anchor in cases:
            if query(expr,left,anchor) != query(expr,right,anchor):
                counterexamples.append(expr.code())
                break
    candidate = discover(records)
    return {
        "status": "HOLD_UNEXPRESSIBLE_IN_DECLARED_DSL" if (
            not counterexamples and candidate is None) else "FALSIFIED",
        "programs_checked": considered,
        "paired_worlds": len(cases),
        "indistinguishable_relational_programs": considered-len(counterexamples),
        "accidental_distinguishing_programs": counterexamples[:5],
        "candidate_admitted": candidate is not None,
        "reason": "isolated-component presence invisible to old-component endpoint-relation DSL",
    }


def foreign_evaluation(task, model, host_list):
    total = correct_relation = correct_graph = held = 0
    by_host = []
    positives = negatives = 0
    for label, native in host_list:
        before = topology(native)
        count = matched_relation = matched_graph = held_here = 0
        plus = minus = 0
        for a,b in native.edges:
            target=edge(a,b)
            total += 1
            count += 1
            expected_bool = oracle(task, native, target)
            positives += int(expected_bool)
            negatives += int(not expected_bool)
            plus += int(expected_bool)
            minus += int(not expected_bool)
            try:
                answer = apply(before,target,model)
            except (ValueError, TypeError):
                answer = None
            if answer is None:
                held += 1
                held_here += 1
                continue
            relation_correct = answer.evidence.classification == expected_bool
            geometry_correct = equivalent_new(
                before, expected_graph(task,native,target),answer.graph)
            correct_relation += int(relation_correct)
            correct_graph += int(geometry_correct)
            matched_relation += int(relation_correct)
            matched_graph += int(geometry_correct)
        by_host.append({
            "name": label, "source_edges": count,
            "positives": plus, "negatives": minus,
            "classified_correct": matched_relation, "graphs_correct": matched_graph,
            "held": held_here,
        })
    return {
        "edges": total, "correct_relation": correct_relation,
        "correct_result_graph": correct_graph, "held": held,
        "wrong": total-correct_graph-held,
        "oracle_positive": positives,"oracle_negative": negatives,
        "by_host": by_host,
    }


def run():
    models = freeze_models()
    external = hosts()
    frozen = {task:{"program":m.proposal.program.code(),
                    "program_cost":m.proposal.program.cost,
                    "review_pin":m.pin(),
                    "training_rows":6,"validation_rows":4}
              for task,m in models.items()}
    findings = {
        task: foreign_evaluation(task,models[task],external) for task in TASKS
    }
    # Separately coded NetworkX synthesis over identical TRAIN/VALIDATE rows,
    # same hypothesis grammar and same enumerated-candidate budget.
    # This does NOT equalize CPU cost or prove a performance advantage.
    controls = {}
    for task in TASKS:
        tr,va,_ = fixtures(task)
        classical = train_control(tr,va)
        external_score = external_control_accuracy(classical,task,external)
        controls[task] = {
            "status":classical["status"],
            "program":classical["program"],
            "candidates_tested":classical["tested"],
            "foreign":external_score,
            "matches_MOTIF_program":classical["program"] == frozen[task]["program"],
        }
    unexpressible = unsupported_certificate(paired_isolation_unsupported())
    return {
        "experiment":"MOTIF-QC-005",
        "status":STATUS,
        "networkx_version":nx.__version__,
        "source_worlds":count_external(),
        "source_world_count":len(external),
        "frozen_models":frozen,
        "foreign_performance":findings,
        "unsupported_expressivity":unexpressible,
        "matched_grammar_classical_learner":controls,
        "directional_graphs": "HOLD_UNSUPPORTED_DOMAIN",
        "weighted_graph_semantics": "HOLD_UNSUPPORTED_DOMAIN",
        "baseline":"independent NetworkX connectivity/neighbor/path oracle",
        "baseline_receives_semantic_task_name":True,
        "equal_sample_and_AST_budget_classical_learner":True,
        "equal_cpu_or_wallclock_budget":False,
        "task_labels_are_provided_to_evaluator":True,
        "external_actions":0,
        "quantum_execution":False,
        "production_installation":False,
    }


if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
