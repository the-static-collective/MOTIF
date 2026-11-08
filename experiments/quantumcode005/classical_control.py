"""QC-005 separate classical relational program synthesizer.

Receives exactly the same QC-004 synthetic TRAIN/VALIDATE rows and the same
AST grammar/cost order, but interprets candidates with NetworkX's graph and
transitive-closure machinery rather than MOTIF's set-relation interpreter.
This is a *matched sample/hypothesis/candidate budget* comparator, not a
matched wall-clock or compute-cost comparison. It is expected to tie.
"""
from __future__ import annotations

from collections import defaultdict, Counter
from itertools import product
import networkx as nx

from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "quantumcode004"))
from gardener import Expr, grammar, MAX_AST_COST
from aperture import Graph, Episode, infer_delta, edge, check_batch


def nx_rel(program: Expr, world: Graph, target: tuple[str, str]):
    """Independent interpreter over native NetworkX DiGraph operations."""
    source = nx.Graph()
    source.add_nodes_from(world.vertices)
    source.add_edges_from(world.edges)
    a,b = edge(*target)
    if not source.has_edge(a,b) or not program.well_typed():
        raise ValueError("Unrecognized program or absent candidate edge")
    def interpret(node: Expr):
        if node.op in ("E","CUT","ID"):
            if node.op == "ID":
                return {(i,i) for i in source.nodes}
            h=source.copy()
            if node.op == "CUT":
                h.remove_edge(a,b)
            return {(x,y) for u,v in h.edges for x,y in ((u,v),(v,u))}
        lhs=interpret(node.left)
        if node.op=="TC":
            dg=nx.DiGraph()
            dg.add_nodes_from(source.nodes)
            dg.add_edges_from(lhs)
            closed=nx.transitive_closure(dg)
            return set(closed.edges)
        rhs=interpret(node.right)
        if node.op=="UNION":
            return lhs|rhs
        if node.op=="INTER":
            return lhs&rhs
        if node.op=="DIFF":
            return lhs-rhs
        if node.op=="JOIN":
            dest=defaultdict(set)
            for m,z in rhs:
                dest[m].add(z)
            return {(x,z) for x,m in lhs for z in dest[m]}
        raise ValueError("Unknown typed operator")
    return (a,b) in interpret(program)


def effect_mapping(program: Expr, rows: tuple[Episode,...]):
    labels=defaultdict(set)
    used=defaultdict(set)
    for row in rows:
        target,effect=infer_delta(row)
        flag=nx_rel(program,row.before,target)
        labels[str(flag)].add(effect.seal())
        used[effect.seal()].add(str(flag))
    if (len(labels)!=2 or len(used)!=2
            or any(len(s)!=1 for s in labels.values())
            or any(len(s)!=1 for s in used.values())):
        return None
    return tuple(sorted((f,next(iter(values))) for f,values in labels.items()))


def train_control(train: tuple[Episode,...],valid: tuple[Episode,...]):
    """Freeze first TRAIN-consistent AST; then independent VALIDATE or HOLD."""
    check_batch(train,"TRAIN")
    check_batch(valid,"VALIDATE")
    if {e.evidence_id for e in train}&{e.evidence_id for e in valid}:
        raise ValueError("Cross-split evidence reused")
    candidate=None
    tested=0
    for expression in grammar(MAX_AST_COST):
        tested+=1
        mapping=effect_mapping(expression,train)
        if mapping:
            candidate=(expression,mapping)
            break
    if candidate is None:
        return {"status":"HOLD_UNEXPRESSIBLE","tested":tested,"program":None}
    expr,mapping=candidate
    if effect_mapping(expr,valid)!=mapping:
        return {"status":"HOLD_VALIDATION_CONTRADICTION",
                "tested":tested,"program":expr.code()}
    return {"status":"CLASSICAL_VALIDATED","tested":tested,
            "program":expr.code(),"ast":expr,"truth_table":mapping}


def external_control_accuracy(baseline, task, foreign):
    from foreign_worlds import oracle,topology
    if baseline["status"]!="CLASSICAL_VALIDATED":
        return {"correct":0,"held":sum(g.number_of_edges() for _,g in foreign)}
    matched=0
    total=0
    for _,graph in foreign:
        world=topology(graph)
        for target in graph.edges:
            total+=1
            matched+=int(nx_rel(baseline["ast"],world,target)
                         == oracle(task,graph,target))
    return {"correct":matched,"total":total}
