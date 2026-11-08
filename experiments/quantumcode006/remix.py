"""MOTIF QC-006: remix a symbolic carrier's meaning under typed context.

The same abstract symbol can bind to different *validated* predicates in
different decoder worlds. Before/after synthetic edits teach which candidate
semantic program fits. A previously unexpressible graph-global observation
is generated using a small typed VertexSet/Boolean grammar. Local context
reuses the reviewed QC-004 triangle predicate.

Classical program synthesis. Synthetic source owner. Local research only.
No new physics, language understanding or production authority.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quantumcode003"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quantumcode004"))
from aperture import Episode, Graph, edge, infer_delta, apply_template, equivalent_new
import gardener

SYMBOL = "◈"
WHOLE = "WHOLE_GRAPH"
LOCAL = "EDGE_LOCAL"
STATUS = "LOCAL_PREVIEW_ONLY"
MAX_COST = 5
SET_ATOMS = ("ALL", "ANCHORS")
SET_UNARY = ("ADJ",)
SET_BINARY = ("MINUS", "UNION", "INTER")
BOOL_UNARY = ("ANY", "EVEN", "NOT")
PROVENANCE = "SYNTHETIC_QC003"  # inherited QC003 episode schema


def seal(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Expression:
    """AST carries an enforced return type, not ambiguous string execution."""
    kind: str
    op: str
    args: tuple["Expression", ...] = ()

    @property
    def cost(self):
        return 1 + sum(x.cost for x in self.args)

    def notation(self):
        return self.op if not self.args else (
            f"{self.op}({','.join(x.notation() for x in self.args)})")

    def valid(self):
        if self.op in SET_ATOMS:
            return self.kind == "VERTEX_SET" and not self.args
        if self.op in SET_UNARY:
            return (self.kind == "VERTEX_SET" and len(self.args) == 1
                    and self.args[0].kind == "VERTEX_SET"
                    and self.args[0].valid())
        if self.op in SET_BINARY:
            return (self.kind == "VERTEX_SET" and len(self.args) == 2
                    and all(x.kind == "VERTEX_SET" and x.valid()
                            for x in self.args))
        if self.op in ("ANY", "EVEN"):
            return (self.kind == "BOOL" and len(self.args) == 1
                    and self.args[0].kind == "VERTEX_SET"
                    and self.args[0].valid())
        if self.op == "NOT":
            return (self.kind == "BOOL" and len(self.args) == 1
                    and self.args[0].kind == "BOOL"
                    and self.args[0].valid())
        return False


def enumerate_meanings(max_cost=MAX_COST):
    """Generate all typed programs to fixed budget: no target-specific template."""
    if not 1 <= max_cost <= MAX_COST:
        raise ValueError("Untrusted search budget")
    by_cost = {"VERTEX_SET": {1: [Expression("VERTEX_SET", x)
                                 for x in SET_ATOMS]},
               "BOOL": {1: []}}
    for length in range(2, max_cost + 1):
        sets, bools = {}, {}
        for expression in by_cost["VERTEX_SET"].get(length-1, ()):
            for op in SET_UNARY:
                e = Expression("VERTEX_SET", op, (expression,))
                sets[e.notation()] = e
            for op in ("ANY", "EVEN"):
                e = Expression("BOOL", op, (expression,))
                bools[e.notation()] = e
        for expression in by_cost["BOOL"].get(length-1, ()):
            e = Expression("BOOL", "NOT", (expression,))
            if expression.op != "NOT":
                bools[e.notation()] = e
        for l in range(1, length-1):
            for x in by_cost["VERTEX_SET"].get(l, ()):
                for y in by_cost["VERTEX_SET"].get(length-1-l, ()):
                    if x == y and "MINUS" in SET_BINARY:
                        pass
                    for op in SET_BINARY:
                        if op in ("UNION", "INTER") and x.notation() > y.notation():
                            continue
                        if op in ("UNION", "INTER", "MINUS") and x == y:
                            continue
                        e = Expression("VERTEX_SET", op, (x, y))
                        sets[e.notation()] = e
        by_cost["VERTEX_SET"][length] = [sets[k] for k in sorted(sets)]
        by_cost["BOOL"][length] = [bools[k] for k in sorted(bools)]
    for length in range(2, max_cost+1):
        yield from by_cost["BOOL"].get(length, ())


def interpret(program: Expression, world: Graph,
              anchors: tuple[str, str]):
    """Pure typed AST interpreter. It never evaluates untrusted Python."""
    if not program.valid() or program.cost > MAX_COST:
        raise ValueError("Invalid or over-budget semantic program")
    if (len(anchors) != 2 or len(set(anchors)) != 2 or
            not set(anchors).issubset(world.vertices) or
            edge(*anchors) not in world.edges):
        raise ValueError("Missing source edge context")
    if program.op == "ALL":
        return world.vertices
    if program.op == "ANCHORS":
        return frozenset(anchors)
    if program.op == "ADJ":
        prior = interpret(program.args[0], world, anchors)
        return frozenset(v for a,b in world.edges for v in (
            (b,) if a in prior else ()) + ((a,) if b in prior else ()))
    if program.op in SET_BINARY:
        left = interpret(program.args[0], world, anchors)
        right = interpret(program.args[1], world, anchors)
        if program.op == "MINUS":
            return left - right
        if program.op == "UNION":
            return left | right
        return left & right
    value = interpret(program.args[0], world, anchors)
    if program.op == "ANY":
        return bool(value)
    if program.op == "EVEN":
        return len(value) % 2 == 0
    if program.op == "NOT":
        return not value
    raise ValueError("Unknown meaning operator")


def role_rows(rows: tuple[Episode,...], split: str):
    if len({r.evidence_id for r in rows}) != len(rows):
        raise ValueError("Duplicate synthetic witness")
    observed=[]
    for record in rows:
        record.check(split)
        anchors, effect = infer_delta(record)
        observed.append((record, anchors, effect))
    return tuple(observed)


def evidence_digest(rows):
    return seal(sorted((r.evidence_id, r.before.receipt(), r.after.receipt())
                       for r in rows))


def semantics_table(program, labelled):
    effects = {effect.seal() for _, _, effect in labelled}
    if len(effects) != 2:
        return None
    observed=defaultdict(set)
    reverse=defaultdict(set)
    for row, anchors, effect in labelled:
        outcome = interpret(program, row.before, anchors)
        observed[str(outcome)].add(effect.seal())
        reverse[effect.seal()].add(str(outcome))
    if (len(observed) != 2 or len(reverse) != 2 or
            any(len(x) != 1 for x in observed.values()) or
            any(len(x) != 1 for x in reverse.values())):
        return None
    return tuple(sorted((k,next(iter(v))) for k,v in observed.items()))


@dataclass(frozen=True)
class Proposal:
    program: Expression
    effects: tuple
    table: tuple[tuple[str,str],...]
    train_digest: str
    examined: int
    status: str = "PROPOSAL_ONLY"


@dataclass(frozen=True)
class Reviewed:
    proposal: Proposal
    validation_digest: str
    validation_count: int
    status: str = STATUS

    @property
    def pin(self):
        return seal((self.proposal.program.notation(),self.proposal.table,
                     self.proposal.train_digest,self.validation_digest,
                     self.validation_count,self.status))


def discover(train: tuple[Episode,...], max_cost=MAX_COST):
    labelled=role_rows(train,"TRAIN")
    effects=tuple(sorted({effect for _,_,effect in labelled}))
    if len(effects)!=2 or any(
        sum(effect == one for _,_,effect in labelled) < 3 for one in effects
    ):
        return None
    for count, program in enumerate(enumerate_meanings(max_cost),1):
        result=semantics_table(program,labelled)
        if result is not None:
            return Proposal(program,effects,result,evidence_digest(train),count)
    return None


def review(candidate: Proposal | None, train: tuple[Episode,...],
           valid: tuple[Episode,...]):
    role_rows(train,"TRAIN")
    labelled=role_rows(valid,"VALIDATE")
    if {r.evidence_id for r in train} & {r.evidence_id for r in valid}:
        raise ValueError("TRAIN evidence reused in VALIDATE")
    generated=discover(train)
    if candidate is None or candidate != generated or candidate.status != "PROPOSAL_ONLY":
        raise ValueError("Feature source and meaning not reconstructible")
    if len(labelled)<6 or any(
        sum(effect == one for _,_,effect in labelled) < 3
        for one in candidate.effects
    ):
        return None
    if semantics_table(candidate.program,labelled) != candidate.table:
        return None
    return Reviewed(candidate,evidence_digest(valid),len(valid))


@dataclass(frozen=True)
class Meaning:
    symbol: str
    decoder: str
    meaning: str
    pin: str
    status: str = STATUS


@dataclass(frozen=True)
class Lexicon:
    """One carrier may have *different tested meanings* in distinct worlds."""
    entries: tuple[tuple[Meaning,object],...] = ()

    def admit_global(self, symbol: str, decoder: str, record: Reviewed,
                     train: tuple[Episode,...], valid: tuple[Episode,...]):
        if decoder != WHOLE or review(record.proposal,train,valid) != record:
            raise ValueError("Global meaning must be revalidated from its receipts")
        return self._insert(Meaning(symbol,decoder,
                                    record.proposal.program.notation(),record.pin),
                            record)

    def admit_local(self, symbol: str, decoder: str, record: gardener.Reviewed,
                    train: tuple[Episode,...], valid: tuple[Episode,...]):
        if decoder != LOCAL or gardener.review(record.proposal,train,valid) != record:
            raise ValueError("Local meaning must be revalidated from its receipts")
        return self._insert(Meaning(symbol,decoder,
                                    record.proposal.program.code(),record.pin()),
                            record)

    def _insert(self,meaning,record):
        if not meaning.symbol or any(
            old.symbol == meaning.symbol and old.decoder == meaning.decoder
            for old,_ in self.entries
        ):
            raise ValueError("Unmarked or duplicate semantic binding")
        return Lexicon(self.entries+((meaning,record),))

    def ask(self, symbol: str, decoder: str | None, graph: Graph,
            anchors: tuple[str,str]):
        if decoder is None:
            # Do not silently collapse polysemy into a preferred meaning.
            return {"status":"HOLD_AMBIGUOUS_DECODER"}
        matching = [(meaning, model) for meaning,model in self.entries
                    if meaning.symbol == symbol and meaning.decoder == decoder]
        if len(matching)!=1:
            return {"status":"HOLD_UNKNOWN_SYMBOL_OR_DECODER"}
        meaning, model=matching[0]
        if meaning.status != STATUS:
            return {"status":"HOLD_UNAUTHORIZED_MEANING"}
        if decoder==WHOLE and isinstance(model,Reviewed):
            if meaning.pin!=model.pin:
                return {"status":"HOLD_SOURCE_REVOKED"}
            truth=interpret(model.proposal.program,graph,anchors)
            effect = dict(model.proposal.table).get(str(truth))
        elif decoder==LOCAL and isinstance(model,gardener.Reviewed):
            if meaning.pin!=model.pin():
                return {"status":"HOLD_SOURCE_REVOKED"}
            truth=gardener.query(model.proposal.program,graph,anchors)
            effect=dict(model.proposal.truth_table).get(str(truth))
        else:
            return {"status":"HOLD_TYPE_MISMATCH"}
        return {"status":STATUS,"symbol":symbol,"decoder":decoder,
                "semantic_program":meaning.meaning,
                "meaning_pin":meaning.pin,
                "value":truth,"effect":effect}


def make_before(prefix: str, length: int, isolates: int):
    nodes=[f"{prefix}_p{i}" for i in range(length)]
    old_edges={edge(nodes[i],nodes[i+1]) for i in range(length-1)}
    old_vertices=set(nodes)|{f"{prefix}_isolated_{i}" for i in range(isolates)}
    graph=Graph.of(old_vertices,old_edges)
    return graph,edge(nodes[0],nodes[1])


def owner_effect(graph: Graph, anchors: tuple[str,str], marker: str):
    """EVALUATOR ONLY: has-any-isolate semantics, never imported by search."""
    used={v for e in graph.edges for v in e}
    has_isolate=bool(graph.vertices-used)
    a,b=anchors
    n0,n1=f"{marker}_fresh0",f"{marker}_fresh1"
    add={edge(a,n0),edge(n0,n1),edge(n1,b)}
    remove={edge(a,b)} if has_isolate else set()
    return Graph.of(graph.vertices|{n0,n1},(graph.edges-remove)|add)


def fixture():
    result={}
    for split, lengths in (("TRAIN",(7,8,9)),
                           ("VALIDATE",(11,12,13)),
                           ("TEST",(15,17,19,21))):
        records=[]
        for index,length in enumerate(lengths):
            for isolates in (0,1,2,3):
                before, anchors=make_before(f"{split}_{index}",length,isolates)
                after=owner_effect(before,anchors,f"{split}_{index}_{isolates}")
                records.append(Episode(f"QC006/{split}/{index}/{isolates}",
                                       split,before,after))
        result[split]=tuple(records)
    return result["TRAIN"],result["VALIDATE"],result["TEST"]


def report():
    train,valid,test=fixture()
    candidate=discover(train)
    certified=review(candidate,train,valid)
    local_train, local_valid, _=gardener.fixtures("triangle")
    local_candidate=gardener.discover(local_train)
    local_certified=gardener.review(local_candidate,local_train,local_valid)
    lex=Lexicon().admit_global(SYMBOL,WHOLE,certified,train,valid)
    lex=lex.admit_local(SYMBOL,LOCAL,local_certified,local_train,local_valid)
    correct=0
    for row in test:
        anchors,expected=infer_delta(row)
        finding=lex.ask(SYMBOL,WHOLE,row.before,anchors)
        correct+=int(finding["effect"]==expected.seal())
    old_binary_collision=True
    # An isolated vertex doesn't affect original-component relation queries.
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"quantumcode005"))
    from trial import paired_isolation_unsupported, unsupported_certificate
    hold=unsupported_certificate(paired_isolation_unsupported())
    return {
        "experiment":"QC-006",
        "status":"SYNTHETIC_REPRESENTATION_REMIX_REVIEW_ONLY",
        "train":len(train),"valid":len(valid),"test":len(test),
        "selected_world_program":candidate.program.notation() if candidate else None,
        "synthetic_meaning_programs_examined":candidate.examined if candidate else None,
        "previous_language_collision":hold["status"],
        "heldout_world_meaning_correct":correct,
        "heldout_world_meaning_total":len(test),
        "shared_symbol":SYMBOL,
        "decoders":{
            WHOLE:certified.proposal.program.notation(),
            LOCAL:local_certified.proposal.program.code(),
        },
        "without_decoder":lex.ask(SYMBOL,None,test[0].before,
                                   infer_delta(test[0])[0])["status"],
        "external_actions":0,
        "production_installation":False,
        "quantum_experiment":False,
    }


if __name__=="__main__":
    print(json.dumps(report(),indent=2,sort_keys=True))
