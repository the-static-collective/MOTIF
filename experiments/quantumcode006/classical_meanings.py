"""QC-006 matched-data classical typed-expression synthesizer.

Shares only the *public grammar AST inventory* and before/after receipts with
MOTIF; independently interprets each term using NetworkX graph operations.
Matched examples, validation and syntax candidate enumeration, NOT CPU budget
or task semantic access. This is an expected classical tie control.
"""
from collections import defaultdict

import networkx as nx
from remix import enumerate_meanings, Expression, MAX_COST
from aperture import infer_delta


def separate(program: Expression, episodes):
    observed=defaultdict(set)
    byeffect=defaultdict(set)
    for row in episodes:
        anchors, effect=infer_delta(row)
        truth=native_interpret(program,row.before,anchors)
        observed[str(truth)].add(effect.seal())
        byeffect[effect.seal()].add(str(truth))
    if (len(observed) != 2 or len(byeffect) != 2
            or any(len(s)!=1 for s in observed.values())
            or any(len(s)!=1 for s in byeffect.values())):
        return None
    return tuple(sorted((k,next(iter(v))) for k,v in observed.items()))


def native_interpret(expr, graph, anchors):
    """A separately coded interpreter over NetworkX sets, not MOTIF interpreter."""
    if not expr.valid() or expr.cost>MAX_COST or not graph.vertices.issuperset(anchors):
        raise ValueError("Ill typed, overbudget or missing anchor")
    native=nx.Graph()
    native.add_nodes_from(graph.vertices)
    native.add_edges_from(graph.edges)
    def rec(node):
        if node.op=="ALL":
            return set(native.nodes)
        if node.op=="ANCHORS":
            return set(anchors)
        if node.op=="ADJ":
            return {v for u in rec(node.args[0]) for v in native.neighbors(u)}
        if node.op=="MINUS":
            return rec(node.args[0])-rec(node.args[1])
        if node.op=="UNION":
            return rec(node.args[0])|rec(node.args[1])
        if node.op=="INTER":
            return rec(node.args[0])&rec(node.args[1])
        if node.op=="ANY":
            return bool(rec(node.args[0]))
        if node.op=="EVEN":
            return not (len(rec(node.args[0]))%2)
        if node.op=="NOT":
            return not rec(node.args[0])
        raise ValueError("Unknown AST constructor")
    return rec(expr)


def learn_classically(train, validate):
    first=None
    examined=0
    for expr in enumerate_meanings():
        examined+=1
        mapping=separate(expr,train)
        if mapping is not None:
            first=(expr,mapping)
            break
    if first is None:
        return {"status":"HOLD_NO_EXPRESSION","examined":examined}
    program,mapping=first
    if separate(program,validate)!=mapping:
        return {"status":"HOLD_VALIDATION_MISMATCH",
                "examined":examined,"program":program.notation()}
    return {"status":"CLASSICAL_REVIEWED","examined":examined,
            "program":program.notation(),"expression":program,
            "truth_table":mapping}


def predict_classically(model,test):
    if model["status"]!="CLASSICAL_REVIEWED":
        return {"correct":0,"held":len(test)}
    correct=0
    for row in test:
        anchor,effect=infer_delta(row)
        flag=native_interpret(model["expression"],row.before,anchor)
        prediction=dict(model["truth_table"]).get(str(flag))
        correct+=int(prediction==effect.seal())
    return {"correct":correct,"total":len(test)}
