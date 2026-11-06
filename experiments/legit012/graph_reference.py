"""LEGIT-012 independent finite graph search oracle and strong DP comparator.

A lattice node represents a partial truth-table assignment over 8 rows.
Every predecessor differs by exactly one additional observed row; DAGs may
have many parents. All 3**8 partial states are exhaustively enumerable.

This module never imports or constructs a generated transformation. It
contains a separately written conventional full scan and a conventional
dynamic-programming bitset solver. Both use the actual prior candidate
catalog as INPUT, not as a trusted semantic oracle.
"""
from __future__ import annotations
from itertools import product
from random import Random

SCHEMA="motif.synthetic-partial-truth-dag.v1"
ROWS=8

def all_states():
    for assignment in product((-1,0,1),repeat=ROWS):
        yield tuple((i,bool(value)) for i,value in enumerate(assignment)
                    if value!=-1)

def _parents(facts):
    return tuple(facts[:i]+facts[i+1:] for i in range(len(facts)))

def make_graph(name,selected):
    if not isinstance(name,str) or not name.isidentifier():
        raise ValueError("Unrecognized synthetic task ID")
    closure={()}
    for facts in selected:
        if (not isinstance(facts,tuple) or len(facts)>ROWS or
                tuple(sorted(facts))!=facts or
                len({i for i,v in facts})!=len(facts) or
                any(type(i) is not int or not 0<=i<ROWS or
                    type(v) is not bool for i,v in facts)):
            raise ValueError("Invalid selected lattice node")
        todo=[facts]
        while todo:
            k=todo.pop()
            if k in closure:continue
            closure.add(k)
            todo.extend(_parents(k))
    ordered=sorted(closure,key=lambda x:(len(x),x))
    return {"schema":SCHEMA,"id":name,
            "nodes":[{"id":"state_"+str(i),"facts":[[a,b] for a,b in item],
                      "parents":[] if not item else
                      [[list(pair) for pair in parent] for parent in _parents(item)]}
                     for i,item in enumerate(ordered)]}

def check_graph(graph):
    if (not isinstance(graph,dict) or set(graph)!={"schema","id","nodes"}
            or graph["schema"]!=SCHEMA or
            not isinstance(graph["id"],str) or
            not graph["id"].isidentifier()):
        raise ValueError("Unknown source graph")
    nodes=graph["nodes"]
    if not isinstance(nodes,list) or not 1<=len(nodes)<=6561:
        raise ValueError("Unexpected bounded DAG size")
    seen=set()
    seen_ids=set()
    normalized=[]
    for node in nodes:
        if not isinstance(node,dict) or set(node)!={"id","facts","parents"}:
            raise ValueError("Unknown node fields")
        if (not isinstance(node["id"],str) or
            not node["id"].isidentifier() or
            not isinstance(node["facts"],list) or
            not isinstance(node["parents"],list)):
            raise ValueError("Invalid node declaration")
        if node["id"] in seen_ids:
            raise ValueError("Duplicate source node ID")
        seen_ids.add(node["id"])
        parts=node["facts"]
        if any(not isinstance(p,list) or len(p)!=2 or
               type(p[0]) is not int or type(p[1]) is not bool or
               not 0<=p[0]<ROWS for p in parts):
            raise ValueError("Invalid source constraints")
        key=tuple((a,b) for a,b in parts)
        if len(key)>ROWS or key!=tuple(sorted(key)) or len(set(a for a,_ in key))!=len(key):
            raise ValueError("Repeated, reordered or contradictory source")
        if key in seen:
            raise ValueError("Duplicate state alias not allowed")
        seen.add(key)
        parents=[]
        for p in node["parents"]:
            if (not isinstance(p,list) or any(
                    not isinstance(x,list) or len(x)!=2 for x in p)):
                raise ValueError("Malformed parent")
            parents.append(tuple(tuple(y) for y in p))
        if (not key and parents) or (key and set(parents)!=set(_parents(key))):
            raise ValueError("Incomplete or invented evidence predecessor")
        if any(parent not in seen for parent in parents):
            raise ValueError("Parent has not been verified topologically")
        normalized.append((key,tuple(parents)))
    if not normalized or normalized[0][0]!=():
        raise ValueError("Missing empty observation origin")
    return normalized

def scan(rows,normalized):
    masks=[x["truth_mask"] for x in rows]
    if not masks or any(type(x) is not int or not 0<=x<=255 for x in masks):
        raise ValueError("No finite Boolean method catalog")
    outcomes={}
    probes=0
    for facts,_ in normalized:
        result=None
        for i,mask in enumerate(masks):
            good=True
            for row,value in facts:
                probes+=1
                if bool((mask>>row)&1)!=value:
                    good=False
                    break
            if good:
                result=i
                break
        outcomes[facts]=result
    return outcomes,{"candidate_bit_tests":probes}

def classical_dp(rows,normalized):
    """Strong conventional dynamic-programming indexed baseline."""
    size=len(rows)
    columns={}
    memberships=0
    for row in range(ROWS):
        for flag in (False,True):
            bits=0
            for i,entry in enumerate(rows):
                memberships+=1
                if bool(entry["truth_mask"]&(1<<row))==flag:
                    bits|=1<<i
            columns[row,flag]=bits
    memo={(): (1<<size)-1}
    updates=0
    for facts,parents in normalized:
        if not facts: continue
        parent=parents[0]
        added=next(v for v in facts if v not in parent)
        memo[facts]=memo[parent] & columns[added]
        updates+=1
        # Every other parent must lead to the same result.
        for alternate in parents[1:]:
            different=next(v for v in facts if v not in alternate)
            if memo[alternate]&columns[different]!=memo[facts]:
                raise AssertionError("Input lattice invalid or bitset recurrence failed")
    result={key:((value&-value).bit_length()-1 if value else None)
            for key,value in memo.items()}
    return result,{"preprocessing_membership_checks":memberships,
                   "graph_edge_merges":updates,
                   "additional_parent_consistency_checks":
                       sum(len(p)-1 for _,p in normalized if p)}

def cases(seed,n=32):
    rng=Random(seed)
    all_values=tuple(all_states())
    selected=[]
    for _ in range(n):
        key=all_values[rng.randrange(len(all_values))]
        selected.append(key)
    return make_graph("Case_"+str(seed),selected)


class StrongCachedDP:
    """Tuned conventional classical DP with index preprocessing amortized.

    Uses LAST parent, unlike the candidate compiler (which uses FIRST).
    It never imports generated source, and runs one bitset transition per
    nonempty graph state. A strong fair benchmark should tie the operation
    count; any measured time difference is local implementation detail.
    """
    def __init__(self,rows):
        self.n=len(rows)
        if not 1<=self.n<=3072:raise ValueError("Unknown library")
        self.cols={}
        self.setup_operations=0
        for row in range(ROWS):
            for flag in (False,True):
                survivors=0
                for i,entry in enumerate(rows):
                    self.setup_operations+=1
                    if ((entry["truth_mask"]>>row)&1)==int(flag):
                        survivors |= (1<<i)
                self.cols[row,flag]=survivors

    def solve(self,normalized):
        state={(): (1<<self.n)-1}
        count=0
        for facts,parents in normalized:
            if not facts:
                continue
            previous=parents[-1]
            delta=next(item for item in facts if item not in previous)
            state[facts]=state[previous]&self.cols[delta]
            count+=1
        return ({key:((mask&-mask).bit_length()-1 if mask else None)
                 for key,mask in state.items()},
                {"bitset_updates":count})
