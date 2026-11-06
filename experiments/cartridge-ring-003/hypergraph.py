"""RING-003: typed directed hypergraph of possible multi-use MOTIF cartridges.

The native hyperedge has MANY tails and MANY heads. A method can serve many
tasks, while a goal can require several jointly selected methods. Edges are
*declared hypotheses* about downstream usefulness, not measurements of success,
not actual cross-cartridge semantic interoperability, and never authority.

No branch code is executed here; native method execution still belongs to
RING-002's explicit pinned, isolated triad. Source-only future branches gain
nodes, not invented affordances or installation.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
import re
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'cartridge-ring-001'))

import triad

SCHEMA = "motif.cartridge-hypergraph.v1"
RESULT_SCHEMA = "motif.cartridge-hypergraph-selection.v1"
IDENT = re.compile(r"^[a-z][a-z0-9._:-]{0,95}$")
VERDICT = "DECLARED_DESIGN_HYPOTHESIS"
MAX_METHODS = 12
MAX_EDGES = 256
MAX_GOALS = 32
MAX_SOURCES = 2000
MAX_STATES = 4096


class HOLD(ValueError):
    pass


@dataclass(frozen=True)
class Method:
    id: str
    source_commit: str
    declared_cost: int
    executable: bool = True


@dataclass(frozen=True)
class Hyperedge:
    id: str
    tails: tuple[str, ...]      # 1..N method vertices, conjunctive
    heads: tuple[str, ...]      # 1..N affordance vertices, conjunctive products
    kind: str = "AFFORDANCE"   # AFFORDANCE or TENSION
    declared_penalty: int = 0 # applied only when kind == TENSION
    basis: str = VERDICT


@dataclass(frozen=True)
class Task:
    name: str
    goals: tuple[tuple[str, int], ...]  # (desired affordance, declared value)
    declared_budget: int
    max_methods: int = 3


def _ident(v):
    if type(v) is not str or not IDENT.fullmatch(v):
        raise HOLD("Bad typed graph identifier")
    return v


def _digest(data):
    return sha256(json.dumps(data, sort_keys=True,
        separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()).hexdigest()


class Hypergraph:
    def __init__(self, methods: tuple[Method, ...], edges: tuple[Hyperedge, ...]):
        if len(methods) > MAX_METHODS or len(edges) > MAX_EDGES:
            raise HOLD("Graph exceeds audited size")
        ms = set()
        for m in methods:
            _ident(m.id)
            if (m.id in ms or type(m.declared_cost) is not int
                    or not 1 <= m.declared_cost <= 100
                    or type(m.executable) is not bool
                    or not re.fullmatch("[0-9a-f]{40}", m.source_commit)):
                raise HOLD("Bad or duplicate method declaration")
            ms.add(m.id)
        es = set()
        for e in edges:
            _ident(e.id)
            if (e.id in es or e.kind not in ("AFFORDANCE", "TENSION")
                    or e.basis != VERDICT
                    or not e.tails or len(e.tails) > MAX_METHODS
                    or not e.heads or len(e.heads) > MAX_GOALS
                    or len(set(e.tails)) != len(e.tails)
                    or len(set(e.heads)) != len(e.heads)
                    or any(t not in ms for t in e.tails)
                    or any(_ident(h) != h for h in e.heads)
                    or any(not isinstance(t, str) for t in e.tails)
                    or type(e.declared_penalty) is not int
                    or not 0 <= e.declared_penalty <= 100
                    or (e.kind == "AFFORDANCE" and e.declared_penalty != 0)
                    or (e.kind == "TENSION" and e.declared_penalty == 0)):
                raise HOLD("Bad or duplicate hyperedge")
            es.add(e.id)
        self.methods = tuple(sorted(methods, key=lambda m: m.id))
        self.edges = tuple(sorted(edges, key=lambda e: e.id))
        self.ids = {m.id for m in self.methods}
        self._by_id = {m.id: m for m in self.methods}

    def audit(self):
        """A source-preserving, inspectable incidence graph, not a drawing."""
        vertices = [
            {"id":m.id, "type":"EXECUTABLE_METHOD",
             "source_commit":m.source_commit, "declared_cost":m.declared_cost,
             "verified_method_body_executed_by_this_organ":False}
            for m in self.methods
        ]
        affords = sorted({h for e in self.edges if e.kind == "AFFORDANCE"
                         for h in e.heads})
        vertices.extend({"id":a, "type":"HYPOTHETICAL_AFFORDANCE"}
                        for a in affords)
        return {
            "schema":SCHEMA, "vertices":vertices,
            "hyperedges":[{
                "id":e.id, "tails":list(e.tails), "heads":list(e.heads),
                "kind":e.kind, "declared_penalty":e.declared_penalty,
                "basis":e.basis,
                "source": "EXPLICIT_LOCAL_DESIGN_NOT_AN_INFERRED_CAUSAL_RELATION",
            } for e in self.edges],
            "many_to_many":True,
            "branch_source_appearance_grants_no_admission":True,
            "authority":"NONE",
        }

    def evaluate(self, selection: tuple[str, ...], task: Task):
        chosen = set(selection)
        if len(chosen) != len(selection) or not chosen.issubset(self.ids):
            raise HOLD("Uninstalled or repeated executable method")
        active = [e for e in self.edges if set(e.tails).issubset(chosen)]
        produced = {h for e in active if e.kind == "AFFORDANCE" for h in e.heads}
        goalmap = dict(task.goals)
        covered = tuple(sorted(goalmap.keys() & produced))
        missing = tuple(sorted(goalmap.keys() - produced))
        cost = sum(self._by_id[m].declared_cost for m in chosen)
        penalty = sum(e.declared_penalty for e in active if e.kind == "TENSION")
        benefit = sum(goalmap[g] for g in covered)
        return {
            "selected":sorted(chosen),
            "covered":list(covered), "missing":list(missing),
            "declared_benefit":benefit, "declared_cost":cost,
            "declared_tension_penalty":penalty,
            "declared_net_utility":benefit-cost-penalty,
            "triggered_hyperedges":[e.id for e in active],
            "coverage_is_not_evidence_of_task_success":True,
        }

    def solve(self, task: Task, *, baseline: bool = True):
        validate_task(task)
        if len(self.methods) > task.max_methods and task.max_methods > MAX_METHODS:
            raise HOLD("Invalid search bound")
        candidates = [m.id for m in self.methods if m.executable]
        if len(candidates) > MAX_METHODS:
            raise HOLD("Too many enabled methods for exact local search")
        if (1 << len(candidates)) > MAX_STATES:
            raise HOLD("Exact search budget exceeded")
        choices = []
        for count in range(min(len(candidates),task.max_methods)+1):
            for chosen in combinations(candidates,count):
                score = self.evaluate(chosen,task)
                if score["declared_cost"] <= task.declared_budget:
                    choices.append(score)
        # Higher utility, more covered value, lower cost/penalty/size, stable ID.
        key = lambda r:(-r["declared_net_utility"], -r["declared_benefit"],
                        r["declared_cost"], r["declared_tension_penalty"],
                        len(r["selected"]),r["selected"])
        if not choices:
            raise HOLD("No eligible method subset (even empty) fits budget")
        choices.sort(key=key)
        best = choices[0]
        result = {
            "schema":RESULT_SCHEMA,
            "task":task.name,
            "task_goals":dict(task.goals),
            "selected":best,
            "all_goals_covered":not best["missing"],
            "method_selection_policy":"EXACT_DECLARED_UTILITY_UNDER_BUDGET",
            "subsets_evaluated":len(choices),
            "scores_are_design_assumptions_not_measured_benefits":True,
            "joint_task_success_measured":False,
            "external_action_executed":False, "authority":"NONE",
        }
        if baseline:
            result["baselines"] = {
                "greedy_single_addition":self.greedy(task),
                "always_all_if_budgeted":self.always_all(task),
            }
        result["receipt_sha256"]=_digest(result)
        return result

    def greedy(self, task):
        """Strong transparent myopic control; never spend on zero/negative gain."""
        chosen = ()
        while len(chosen) < task.max_methods:
            current = self.evaluate(chosen,task)
            options = [
                self.evaluate(tuple(sorted(chosen+(m.id,))),task)
                for m in self.methods if m.executable and m.id not in chosen
            ]
            candidates = [x for x in options
                          if (x["declared_cost"]<=task.declared_budget
                              and x["declared_net_utility"] >
                              current["declared_net_utility"])]
            if not candidates:
                break
            candidates.sort(key=lambda x: (-x["declared_net_utility"],
                                            x["declared_cost"],x["selected"]))
            chosen=tuple(candidates[0]["selected"])
        return self.evaluate(chosen,task)

    def always_all(self, task):
        installed=tuple(m.id for m in self.methods if m.executable)
        if len(installed)>task.max_methods or sum(
            self._by_id[x].declared_cost for x in installed)>task.declared_budget:
            return {"status":"NOT_FEASIBLE_UNDER_DECLARED_BUDGET"}
        return self.evaluate(installed,task)


def validate_task(task):
    if (not isinstance(task,Task) or type(task.name) is not str
            or not 1<=len(task.name)<=96
            or type(task.declared_budget) is not int
            or not 0<=task.declared_budget<=100
            or type(task.max_methods) is not int
            or not 0<=task.max_methods<=MAX_METHODS
            or len(task.goals)>MAX_GOALS):
        raise HOLD("Malformed task / budget")
    names=[]
    for key,value in task.goals:
        _ident(key)
        if type(value) is not int or not 0<value<=100:
            raise HOLD("Declared goal value must be bounded positive integer")
        names.append(key)
    if len(names)!=len(set(names)):
        raise HOLD("Duplicate goal")


def current_graph():
    """Only the three previously PINNED native sources; not all indexed branches."""
    methods=(
        Method("geometry.procedure-repair",triad.BY_ID[
            "geometry.procedure-repair"].commit,2),
        Method("reason.proof-objection",triad.BY_ID[
            "reason.proof-objection"].commit,2),
        Method("thought.language-dev",triad.BY_ID[
            "thought.language-dev"].commit,2),
    )
    edges=(
        Hyperedge("geometry.many-uses",("geometry.procedure-repair",),
                  ("measurement-revision","duplicate-record-audit",
                   "procedure-counterexample-question")),
        Hyperedge("reason.many-uses",("reason.proof-objection",),
                  ("proof-review","objection-review","question-proposal")),
        Hyperedge("language.many-uses",("thought.language-dev",),
                  ("utterance-classification","language-rule-audit",
                   "ambiguity-question")),
        Hyperedge("language-and-reason.joint-bridge",
                  ("thought.language-dev","reason.proof-objection"),
                  ("interpretation-objection-bridge",
                   "language-evidence-skepticism")),
        Hyperedge("geometry-and-reason.joint-bridge",
                  ("geometry.procedure-repair","reason.proof-objection"),
                  ("measurement-proof-challenge",
                   "procedure-counterexample-bridge")),
        Hyperedge("language-and-geometry.joint-bridge",
                  ("geometry.procedure-repair","thought.language-dev"),
                  ("measurement-description-check",)),
        Hyperedge("all-three.joint-bridge",
                  ("geometry.procedure-repair","thought.language-dev",
                   "reason.proof-objection"),
                  ("cross-instrument-evidence-review",
                   "explain-measurement-objection")),
        # Risk: two synthetic test suites with no common source evidence may
        # offer mutually inconsistent descriptions; this is a declared
        # caution, not a measured conflict or claim that pairing is bad.
        Hyperedge("geometry-language.unsupported-crossworld",
                  ("geometry.procedure-repair","thought.language-dev"),
                  ("crossworld-scope-risk",),"TENSION",3),
    )
    return Hypergraph(methods,edges)


def add_discovered_sources(hypergraph: Hypergraph, catalog: dict):
    """Open-ended SOURCE nodes, no executable methods or fabricated use edges."""
    import discovery
    if catalog.get("schema")!=discovery.SCHEMA:
        raise HOLD("Wrong source inventory schema")
    rows=catalog.get("passports")
    if not isinstance(rows,list) or len(rows)>MAX_SOURCES:
        raise HOLD("Source census too large or malformed")
    known=set()
    nodes=[]
    for row in rows:
        ref=row.get("ref") if isinstance(row,dict) else None
        sha=row.get("commit") if isinstance(row,dict) else None
        if (type(ref) is not str or ref in known or not discovery.REF.fullmatch(ref)
                or type(sha) is not str or not discovery.SHA.fullmatch(sha)
                or row.get("status")!="INDEXED_NON_EXECUTABLE"
                or row.get("executable") is not False):
            raise HOLD("Unsafe unadmitted source candidate")
        known.add(ref)
        nodes.append({"type":"SOURCE_ONLY_BRANCH","ref":ref,"commit":sha,
                      "usable_for_source_inspection":True,
                      "admitted_reasoning_capabilities":[]})
    result=hypergraph.audit()
    result["indexed_source_candidates"]=nodes
    result["source_candidates_do_not_supply_affordances"]=True
    result["source_candidate_count"]=len(nodes)
    result["receipt_sha256"]=_digest(result)
    return result


def example_tasks():
    """Typed, synthetic user goals; scores are specified before selection."""
    return (
        Task("explain-uncertain-language",(
            ("interpretation-objection-bridge",12),),4,2),
        Task("test-duplicate-event-procedure",(
            ("measurement-proof-challenge",12),),4,2),
        Task("single-method-multiple-uses",(
            ("proof-review",5),("question-proposal",5)),3,3),
        Task("multimethod-cross-instrument",(
            ("cross-instrument-evidence-review",18),),6,3),
        Task("ignore-unhelpful-methods",(("utterance-classification",8),),6,3),
        Task("unsupported-target",(("unseen-goal",9),),6,3),
    )


def demo(catalog=None):
    g=current_graph()
    result={"schema":"motif.hypergraph-demo.v1",
            "graph":g.audit(),
            "trials":[g.solve(t) for t in example_tasks()],
            "synthetic_author_declared_goals":True,
            "independent_native_benchmarks_are_not_a_shared_task":True,
            "authority":"NONE"}
    if catalog is not None:
        result["discovered_sources"]=add_discovered_sources(g,catalog)
    result["receipt_sha256"]=_digest(result)
    return result


def main():
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--catalog",type=Path)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    cat=json.loads(a.catalog.read_text()) if a.catalog else None
    res=demo(cat)
    data=json.dumps(res,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(data)
        print(json.dumps({"status":"SYNTHETIC_DESIGN_TRIAL",
                          "receipt_sha256":res["receipt_sha256"],
                          "output":str(a.out)}))
    else:
        print(data,end="")


if __name__=="__main__":
    main()
