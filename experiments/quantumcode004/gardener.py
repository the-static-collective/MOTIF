"""QC-004 Grammar Gardener: bounded synthesis of typed relational graph questions.

Every case is researcher-authored synthetic classical mathematics. The engine
enumerates ASTs from a finite typed grammar instead of using the one
pre-selected CUT-EDGE/REACH feature of QC-003. It sees unlabelled before/after
graphs, infers boundary anchors and anonymous effects, searches the DSL for
a separating yes/no relation, checks untouched validation graphs, and keeps
source-pinned local-only question cartridges. It NEVER runs generated Python,
calls outside tools, or installs itself in MOTIF.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quantumcode003"))
from aperture import (
    Graph, Episode, World, Template, infer_delta, apply_template,
    equivalent_new, sample_graph, edge, check_batch,
)

STATUS = "LOCAL_PREVIEW_ONLY"
PROVENANCE = "SYNTHETIC_QC004"
MAX_AST_COST = 5
# E and CUT are binary relations over vertices. ID is typed identity.
# TC takes a relation and returns a relation. JOIN / UNION / INTER / DIFF
# each take two relations and return a relation.
ATOMS = ("E", "CUT", "ID")
UNARY = ("TC",)
BINARY = ("JOIN", "UNION", "INTER", "DIFF")


def seal(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Expr:
    op: str
    left: "Expr | None" = None
    right: "Expr | None" = None

    @property
    def cost(self):
        return 1 + (self.left.cost if self.left else 0) + (
            self.right.cost if self.right else 0)

    def code(self):
        if self.op in ATOMS:
            return self.op
        if self.op in UNARY:
            return f"{self.op}({self.left.code()})"
        return f"{self.op}({self.left.code()},{self.right.code()})"

    def well_typed(self):
        if self.op in ATOMS:
            return self.left is None and self.right is None
        if self.op in UNARY:
            return self.left is not None and self.left.well_typed() and self.right is None
        if self.op in BINARY:
            return (self.left is not None and self.right is not None
                    and self.left.well_typed() and self.right.well_typed())
        return False


def grammar(max_cost=MAX_AST_COST):
    """Enumerate generic AST constructors bottom-up; no named task templates."""
    if not 1 <= max_cost <= 7:
        raise ValueError("Invalid bounded grammar cost")
    by_cost = {1: [Expr(t) for t in ATOMS]}
    for cost in range(2, max_cost+1):
        pool = {}
        for root in UNARY:
            for prior in by_cost[cost-1]:
                if root == "TC" and prior.op == "TC":  # standard idempotence
                    continue
                expression = Expr(root, prior)
                pool[expression.code()] = expression
        for root in BINARY:
            for leftcost in range(1, cost-1):
                for lhs in by_cost[leftcost]:
                    for rhs in by_cost[cost-1-leftcost]:
                        lc, rc = lhs.code(), rhs.code()
                        if root in ("UNION", "INTER") and lc > rc:
                            continue  # commutative formula quotient
                        if lhs == rhs and root in ("DIFF", "UNION", "INTER"):
                            continue  # a-a, a+a, a∩a
                        expression = Expr(root, lhs, rhs)
                        pool[expression.code()] = expression
        by_cost[cost] = [pool[k] for k in sorted(pool)]
    for cost in sorted(by_cost):
        yield from by_cost[cost]


@lru_cache(maxsize=100000)
def relation(program: Expr, graph: Graph, target: tuple[str, str]):
    """Interpret a data-only typed AST as a finite binary relation."""
    if not program.well_typed() or program.cost > MAX_AST_COST:
        raise ValueError("Untrusted or over-budget expression")
    nodes = graph.vertices
    anchor = edge(*target)
    if anchor not in graph.edges:
        raise ValueError("Target query needs an existing graph edge")
    if program.op == "E":
        return frozenset((a, b) for a, b in graph.edges for a, b in ((a, b), (b, a)))
    if program.op == "CUT":
        return frozenset((a, b) for a, b in graph.edges if (a, b) != anchor
                         for a, b in ((a, b), (b, a)))
    if program.op == "ID":
        return frozenset((a, a) for a in nodes)
    lhs = relation(program.left, graph, anchor)
    if program.op == "TC":
        adj = defaultdict(set)
        for a, b in lhs:
            adj[a].add(b)
        output = set()
        for start in nodes:
            frontier, visited = list(adj[start]), set()
            while frontier:
                point = frontier.pop()
                if point in visited:
                    continue
                visited.add(point)
                frontier.extend(adj[point] - visited)
            output.update((start, v) for v in visited)
        return frozenset(output)
    rhs = relation(program.right, graph, anchor)
    if program.op == "UNION":
        return lhs | rhs
    if program.op == "INTER":
        return lhs & rhs
    if program.op == "DIFF":
        return lhs - rhs
    if program.op == "JOIN":
        end = defaultdict(set)
        for b, c in rhs:
            end[b].add(c)
        return frozenset((a, c) for a, b in lhs for c in end[b])
    raise ValueError("Unknown typed relation")


def query(program: Expr, graph: Graph, target: tuple[str, str]):
    """A graph question: does this relation connect the anchor endpoints?"""
    a, b = edge(*target)
    return (a, b) in relation(program, graph, (a, b))


def episode_id(records):
    return seal(sorted((r.evidence_id, r.before.receipt(), r.after.receipt())
                       for r in records))


def labelled(records):
    out = []
    for row in records:
        anchors, delta = infer_delta(row)
        out.append((row.before, anchors, delta))
    return tuple(out)


def separate(program: Expr, data):
    """Return two Boolean-to-effect bindings iff the relation classifies ALL."""
    effects = {delta.seal() for _, _, delta in data}
    if len(effects) != 2:
        return None
    outcomes = defaultdict(set)
    by_effect = defaultdict(set)
    for graph, anchors, delta in data:
        val = query(program, graph, anchors)
        outcomes[val].add(delta.seal())
        by_effect[delta.seal()].add(val)
    if (len(outcomes) != 2 or len(by_effect) != 2 or
            any(len(v) != 1 for v in outcomes.values()) or
            any(len(v) != 1 for v in by_effect.values())):
        return None
    return tuple(sorted((str(key), next(iter(value)))
                        for key, value in outcomes.items()))


@dataclass(frozen=True)
class Proposal:
    program: Expr
    effects: tuple[Template, ...]
    truth_table: tuple[tuple[str, str], ...]
    evidence_hash: str
    examined: int
    max_cost: int
    status: str = "CANDIDATE_ONLY"

    def selected(self, value: bool):
        return dict(self.truth_table).get(str(value))


@dataclass(frozen=True)
class Reviewed:
    proposal: Proposal
    validation_hash: str
    validation_count: int
    status: str = STATUS

    def pin(self):
        return seal((self.proposal.program.code(),
                     self.proposal.truth_table, self.proposal.evidence_hash,
                     self.validation_hash, self.validation_count, self.status))


def discover(train: tuple[Episode, ...], max_cost=MAX_AST_COST):
    check_batch(train, "TRAIN")
    if not 1 <= max_cost <= MAX_AST_COST:
        raise ValueError("Cost outside authenticated local grammar")
    records = labelled(train)
    effects = tuple(sorted({row[2] for row in records}))
    if len(effects) != 2 or any(
        sum(delta == effect for _, _, delta in records) < 2
        for effect in effects
    ):
        return None
    examined = 0
    for program in grammar(max_cost):
        examined += 1
        table = separate(program, records)
        if table is not None:
            return Proposal(program, effects, table, episode_id(train), examined, max_cost)
    return None


def review(candidate: Proposal | None, train: tuple[Episode, ...],
           valid: tuple[Episode, ...]):
    check_batch(train, "TRAIN")
    check_batch(valid, "VALIDATE")
    if {r.evidence_id for r in train} & {r.evidence_id for r in valid}:
        raise ValueError("Reused training receipt in independent validation")
    original = discover(train, max_cost=candidate.max_cost if candidate else MAX_AST_COST)
    if candidate is None or candidate != original or candidate.status != "CANDIDATE_ONLY":
        raise ValueError("Unreconstructible relational query candidate")
    rows = labelled(valid)
    if len(rows) < 4 or any(
        sum(effect == candidate_effect for _, _, effect in rows) < 2
        for candidate_effect in candidate.effects
    ):
        return None
    if separate(candidate.program, rows) != candidate.truth_table:
        return None
    return Reviewed(candidate, episode_id(valid), len(valid))


@dataclass(frozen=True)
class Witness:
    program_hash: str
    original: str
    target: tuple[str, str]
    classification: bool
    effect_hash: str
    outcome: str


@dataclass(frozen=True)
class Result:
    graph: Graph
    evidence: Witness


def apply(graph: Graph, target: tuple[str, str], reviewed: Reviewed | None):
    """No arbitrary code execution, no fabricated observed action claim."""
    if reviewed is None:
        return None
    if reviewed.status != STATUS or reviewed.proposal.status != "CANDIDATE_ONLY":
        raise ValueError("Invalid local authority")
    if not reviewed.proposal.program.well_typed():
        raise ValueError("Ill-typed question AST")
    target = edge(*target)
    if target not in graph.edges:
        return None
    choice = query(reviewed.proposal.program, graph, target)
    effect = next((x for x in reviewed.proposal.effects
                   if x.seal() == reviewed.proposal.selected(choice)), None)
    if effect is None:
        return None
    new_graph = apply_template(graph, target, effect)
    if new_graph is None:
        return None
    receipt = Witness(reviewed.pin(), graph.receipt(), target, choice,
                      effect.seal(), new_graph.receipt())
    return Result(new_graph, receipt)


def replay(start: Graph, result: Result, current: Reviewed | None):
    if current is None or current.status != STATUS:
        return None
    reconstructed = apply(start, result.evidence.target, current)
    if reconstructed is None or reconstructed.evidence != result.evidence:
        return None
    if reconstructed.graph != result.graph:
        return None
    return reconstructed


@dataclass(frozen=True)
class Garden:
    """A catalog of independently reviewed question programs, not live authority."""
    # Explicit task domains are problem declarations, not "secret user needs".
    entries: tuple[tuple[str, Reviewed], ...] = ()

    def keep(self, question: str, certified: Reviewed):
        if (not question or not isinstance(certified, Reviewed)
                or certified.status != STATUS or
                certified.proposal.status != "CANDIDATE_ONLY"):
            raise ValueError("Only reviewed local question cartridges are retainable")
        if any(q == question for q, _ in self.entries):
            raise ValueError("Question already admitted, need explicit revision")
        return Garden(self.entries+((question, certified),))

    def use(self, question: str, graph: Graph, target: tuple[str, str]):
        rule = dict(self.entries).get(question)
        if rule is None:
            return None
        return apply(graph, target, rule)


def oracle_semantics(question: str, graph: Graph, target: tuple[str, str]) -> bool:
    """Source owner evaluation, deliberately separate from the learned AST."""
    a, b = edge(*target)
    if question == "alternate_path":
        # Classical union-find on graph with query edge omitted.
        parent = {x: x for x in graph.vertices}
        def find(x):
            while x != parent[x]:
                x = parent[x]
            return x
        for u, v in graph.edges:
            if (u, v) == (a, b):
                continue
            parent[find(u)] = find(v)
        return find(a) == find(b)
    if question == "triangle":
        adj = {x: set() for x in graph.vertices}
        for u, v in graph.edges:
            adj[u].add(v)
            adj[v].add(u)
        return bool(adj[a] & adj[b])
    if question == "square":
        # Independent simple 3-edge path after deleting target. A BFS for
        # mere reachability would be WRONG for this family.
        nbr = defaultdict(set)
        for u, v in graph.edges:
            if (u, v) != (a, b):
                nbr[u].add(v)
                nbr[v].add(u)
        def walk(current, length, seen):
            if length == 0:
                return current == b
            return any(walk(next_node, length-1, seen|{next_node})
                       for next_node in nbr[current]
                       if next_node not in seen or
                       (length == 1 and next_node == b))
        return walk(a, 3, {a})
    raise ValueError("Unsupported oracle question")


def evaluator_graph(question, prefix: str, length: int,
                    chord=False, extra_tail=False):
    """Researcher-authored synthetic world with paired contrasting targets."""
    ring = [f"{prefix}_r{i}" for i in range(length)]
    edges = {edge(ring[i], ring[(i+1) % length]) for i in range(length)}
    vertices = set(ring)
    if question == "alternate_path":
        tail = [f"{prefix}_t{i}" for i in range(length)]
        vertices.update(tail)
        edges.add(edge(ring[0], tail[0]))
        edges.update(edge(tail[i], tail[i+1]) for i in range(length-1))
        if chord:
            edges.add(edge(ring[1], ring[7]))
        if extra_tail:
            q = [f"{prefix}_q{i}" for i in range(5)]
            vertices.update(q)
            edges.add(edge(ring[0], q[0]))
            edges.update(edge(q[i], q[i+1]) for i in range(4))
        targets = (edge(ring[length//2],ring[length//2+1]),
                   edge(tail[length//2],tail[length//2+1]))
    elif question == "triangle":
        edges.add(edge(ring[0], ring[2]))
        if chord:
            edges.add(edge(ring[5], ring[7]))
        if extra_tail:
            t = [f"{prefix}_t{i}" for i in range(6)]
            vertices.update(t)
            edges.add(edge(ring[3],t[0]))
            edges.update(edge(t[i],t[i+1]) for i in range(5))
        targets = (edge(ring[0],ring[1]),
                   edge(ring[length//2],ring[length//2+1]))
    elif question == "square":
        sq = [f"{prefix}_s{i}" for i in range(4)]
        vertices.update(sq)
        edges.update(edge(sq[i],sq[(i+1)%4]) for i in range(4))
        edges.add(edge(ring[0],sq[0]))
        if chord:
            edges.add(edge(ring[3],ring[8]))
        if extra_tail:
            t = [f"{prefix}_t{i}" for i in range(5)]
            vertices.update(t)
            edges.add(edge(ring[0],t[0]))
            edges.update(edge(t[i],t[i+1]) for i in range(4))
        targets = (edge(sq[1],sq[2]),
                   edge(ring[length//2],ring[length//2+1]))
    else:
        raise ValueError("Unknown synthetic question")
    graph = Graph.of(vertices, edges)
    assert oracle_semantics(question,graph,targets[0]) is True
    assert oracle_semantics(question,graph,targets[1]) is False
    return graph, targets


def oracle_edit(question, graph: Graph, target: tuple[str, str], marker: str):
    """EVALUATOR ONLY: two-new-node local edits with two different deltas."""
    a, b = target
    names = (marker+"_f0",marker+"_f1")
    if set(names)&graph.vertices:
        raise ValueError("Bad evaluator names")
    path = {edge(a,names[0]),edge(names[0],names[1]),edge(names[1],b)}
    remove = {target} if oracle_semantics(question,graph,target) else set()
    return Graph.of(graph.vertices | set(names), (graph.edges - remove) | path)


def fixtures(question: str):
    layout = {
        "TRAIN": [(16,False,False),(18,False,False),(20,False,False)],
        "VALIDATE": [(22,False,False),(24,False,False)],
        "TEST": [(26,False,False),(28,True,False),
                 (30,False,True),(32,True,True)],
    }
    result = {}
    for split, cases in layout.items():
        records = []
        for index,(length,chord,extra_tail) in enumerate(cases):
            graph, edges = evaluator_graph(question,
                             f"{question}_{split}_{index}",length,
                             chord=chord,extra_tail=extra_tail)
            for slot,target in enumerate(edges):
                outcome = oracle_edit(question,graph,target,
                                      f"{question}_{split}_{index}_{slot}")
                records.append(Episode(f"{question}/{split}/{index}/{slot}",
                                       split,graph,outcome))
        result[split] = tuple(records)
    return result["TRAIN"],result["VALIDATE"],result["TEST"]


def evaluate(question, model: Reviewed | None, test: tuple[Episode, ...]):
    check_batch(test,"TEST")
    if model is None:
        return {"total":len(test),"correct":0,"covered":0,
                "held":len(test),"wrong":0}
    covered=correct=0
    for row in test:
        # EVALUATOR has after-graph and can find which edge is the target.
        # At deployment this is not a claim about a hidden actor's choice.
        target,_=infer_delta(row)
        generated=apply(row.before,target,model)
        if generated is None:
            continue
        covered+=1
        correct+=int(equivalent_new(row.before,row.after,generated.graph))
    return {"total":len(test),"covered":covered,"correct":correct,
            "held":len(test)-covered,"wrong":covered-correct}


def all_edges(question, model: Reviewed, graphs: tuple[Graph,...]):
    measured=[]
    for graph in graphs:
        correct=0
        for target in graph.edges:
            outcome=apply(graph,target,model)
            expected=oracle_edit(question,graph,target,
                                 "independent_ground_truth")
            correct+=int(outcome is not None and
                          equivalent_new(graph,expected,outcome.graph))
        measured.append({"edges":len(graph.edges),"correct":correct})
    return tuple(measured)


def report():
    garden=Garden()
    runs={}
    for question in ("alternate_path","triangle","square"):
        train,valid,test=fixtures(question)
        candidate=discover(train)
        model=review(candidate,train,valid) if candidate else None
        if model is not None:
            garden=garden.keep(question,model)
        graphs=tuple(test[i].before for i in range(0,len(test),2))
        counter=all_edges(question,model,graphs) if model else ()
        runs[question]={
            "train":len(train),"validate":len(valid),"test":len(test),
            "proposed":candidate is not None,
            "reviewed":model is not None,
            "selected_program":candidate.program.code() if candidate else None,
            "program_cost":candidate.program.cost if candidate else None,
            "candidate_programs_examined":candidate.examined if candidate else None,
            "heldout":evaluate(question,model,test),
            "all_edge_classical_baseline_ties":bool(counter) and all(
                x["edges"]==x["correct"] for x in counter),
            "all_edge_counts":counter,
        }
    return {"experiment":"QC-004","status":"SYNTHETIC_RESEARCH_ONLY",
            "grammar_primitives":ATOMS+UNARY+BINARY,"cost_limit":MAX_AST_COST,
            "task_outcomes":runs,
            "reviewed_question_cartridges":len(garden.entries),
            "external_actions":0,
            "produced_executable_source":False,
            "quantum_execution":False}


if __name__=="__main__":
    print(json.dumps(report(),indent=2,sort_keys=True))
