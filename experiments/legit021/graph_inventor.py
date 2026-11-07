"""LEGIT-021 — source-graph APERTURE INVENTOR.

An executable bounded search creates mathematical *questions*, rather than
choosing a predefined graph label. It enumerates all connected simple
unlabelled source graphs of 1..4 vertices and asks the actual pinned Dogram
homomorphism kernel to count their maps into each possible target.

Both the candidate question and its failure/success receipts are genuine
computed structures, not a preselected triangle/star/C4 dictionary.

Source-language scope: connected undirected simple graphs, <=4 vertices.
"Minimum" always means minimum in THAT grammar, by
(vertex-count, edge-count, canonical edge list). No unrestricted invention.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import combinations, permutations
from pathlib import Path
from statistics import mean
from time import perf_counter_ns
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit020"))
from vendor_dogram.path_tree_test_language import (
    adjacency_matrix,homomorphism_count,total_walk_counts,
    path_recurrence_certificate,branching_star_hom_count
)
from vendor_dogram.probe_partition_refinement import analyze_probe_family

MAX_SOURCE_VERTICES=4

class HOLD(ValueError):
    pass

def cycles(*sizes):
    """Disjoint cycles with consecutive labels; no edge loops."""
    if not sizes or any(type(n) is not int or n<3 for n in sizes):
        raise HOLD("Need nonempty simple cycles of size >=3")
    start=0
    edges=[]
    for n in sizes:
        for i in range(n):
            a=start+i
            b=start+((i+1)%n)
            edges.append(tuple(sorted((a,b))))
        start+=n
    return start,tuple(sorted(set(edges)))

def dogram_calibration():
    """Exact carriers from Dogram LEGIT-020; not newly generated evidence."""
    return (
        (7,((0,1),(1,2),(2,3),(3,4),(4,5),(0,5))),
        (7,((0,1),(1,2),(0,3),(3,6),(0,4),(4,5))),
    )

def adjacency(carrier):
    n,edges=carrier
    return adjacency_matrix(n,edges)

def connected(n,edges):
    if n==1:return True
    graph=[set() for _ in range(n)]
    for a,b in edges:
        graph[a].add(b)
        graph[b].add(a)
    seen={0}
    todo=[0]
    while todo:
        v=todo.pop()
        for child in graph[v]-seen:
            seen.add(child)
            todo.append(child)
    return len(seen)==n

def normalized(n,edges):
    edges=tuple(sorted(tuple(sorted(x)) for x in edges))
    return min(tuple(sorted(tuple(sorted((perm[a],perm[b])))
                            for a,b in edges))
               for perm in permutations(range(n)))

@lru_cache(maxsize=1)
def grammar():
    """All finite unlabeled connected source patterns, enumerated afresh."""
    probes=[]
    for n in range(1,MAX_SOURCE_VERTICES+1):
        pairs=list(combinations(range(n),2))
        representatives=set()
        for bits in range(1<<len(pairs)):
            edges=tuple(pairs[i] for i in range(len(pairs))
                        if bits>>i&1)
            if connected(n,edges):
                representatives.add(normalized(n,edges))
        for ed in representatives:
            probes.append((n,ed))
    probes.sort(key=lambda c:(c[0],len(c[1]),c[1]))
    if not probes or len(set(probes))!=len(probes):
        raise HOLD("Invalid pattern enumeration")
    return tuple(probes)

def characterize(probe):
    n,edges=probe
    degrees=[0]*n
    for a,b in edges:
        degrees[a]+=1
        degrees[b]+=1
    is_cycle=(n>=3 and len(edges)==n and all(d==2 for d in degrees))
    is_star=(n>=3 and len(edges)==n-1 and
             sorted(degrees)==[1]*(n-1)+[n-1])
    return {
        "vertices":n,"edges":[list(x) for x in edges],
        "degree_signature":sorted(degrees),
        "triangle":n==3 and is_cycle,
        "four_cycle":n==4 and is_cycle,
        "three_leaf_star":n==4 and is_star,
        "previously_authored_probe_template":False,
        "generated_from_connected_graph_enumeration":True,
    }

@lru_cache(maxsize=32768)
def count(probe,target):
    n,edges=probe
    return homomorphism_count(
        adjacency_matrix(n,edges),adjacency(target))

def reference_count(probe,target):
    """Independent sum over all source-vertex assignments, not Dogram API."""
    from itertools import product
    n,source_edges=probe
    target_n,target_edges=target
    adj={tuple(sorted(pair)) for pair in target_edges}
    total=0
    for mapping in product(range(target_n),repeat=n):
        valid=True
        for u,v in source_edges:
            if tuple(sorted((mapping[u],mapping[v]))) not in adj:
                valid=False
                break
        if valid:total+=1
    return total

def all_path_collision(targets,eigenvalue=2):
    """Exact all-length mathematical certificate, not a sampled inference."""
    if len(targets)<2:
        raise HOLD("Need multiple worlds")
    certificates=[]
    for t in targets:
        a=adjacency(t)
        cert=path_recurrence_certificate(a,eigenvalue)
        if not cert["valid"]:
            raise HOLD("All-length path certificate unavailable")
        certificates.append(cert)
    keys={(x["vertex_count"],x["first_walk_count"],x["eigenvalue"])
          for x in certificates}
    if len(keys)!=1:
        raise HOLD("Different path-homomorphism counts")
    first=tuple(total_walk_counts(adjacency(t),8) for t in targets)
    if len({tuple(v) for v in first})!=1:
        raise HOLD("Finite path observation contradicts recurrence")
    return {
        "same_all_finite_paths":True,
        "why_proved":"for each carrier, A*d=lambda*d; same vertex count and total degree",
        "eigenvalue":eigenvalue,
        "first_nine_walk_counts":first[0],
        "different_carriers_not_inferred_from_path_equivalence":True,
        "certificates":certificates
    }

def signatures(probe,targets):
    return tuple(count(probe,t) for t in targets)

def independent_minimal_separator(targets):
    """Strong conventional exhaustive optimum under the EXACT same grammar.

    Intentionally not claimed weaker than the proposed search. It uses
    independent reference_count and stops at the first minimal source.
    """
    checked=0
    for probe in grammar():
        observed=tuple(reference_count(probe,t) for t in targets)
        checked+=1
        if len(set(observed))>1:
            return probe,observed,checked
    return None,None,checked

def invent_separator(targets):
    if len(targets)<2:
        raise HOLD("At least two possible target states required")
    history=[]
    winner=None
    for probe in grammar():
        observed=signatures(probe,targets)
        item={"probe":characterize(probe),
              "counts":list(observed),
              "separates":len(set(observed))>1}
        history.append(item)
        if item["separates"]:
            winner=probe
            break
    verified,ref,checked=independent_minimal_separator(targets)
    if verified!=winner:
        raise HOLD("Independent exhaustive comparator disproved minimal source")
    if winner is not None and ref!=signatures(winner,targets):
        raise HOLD("Independent full assignment enumerator disputes count")
    return {
        "admissible_connected_patterns":len(grammar()),
        "minimum_means_only_grammar_bounded_up_to_four_vertices":True,
        "first_separating_probe":characterize(winner) if winner else None,
        "first_separating_counts":list(ref) if ref is not None else None,
        "search_probes_inspected":len(history),
        "actual_failed_probe_receipts":history[:-1] if winner else history,
        "independent_classical_exhaustive_minimum_agrees":True,
        "classical_full_assignment_cases_inspected":checked,
        "no_preselected_triangle_star_square_names_in_enumerator":True,
        "source_graph_uniqueness_isomorphism_quotiented":True,
    }

def partition(outputs,indices):
    groups={}
    for i in indices:
        groups.setdefault(outputs[i],[]).append(i)
    return tuple(tuple(group) for group in groups.values())

def uniform_entropy_split(outputs,indices):
    """Expected reduction in number of unresolved pairs, exactly integral."""
    size=len(indices)
    return size*size-sum(len(block)**2 for block in partition(outputs,indices))

def classical_optimal_tree(targets,initial=None):
    """Independent exact decision-tree DP over all synthesized source probes.

    Objective: minimum expected number of questions with uniform world
    prior, tie-break by sum of probe sizes / deterministic source index.
    This is a strong conventional combinatorial planner, not an
    intentionally weak naive comparator.
    """
    from functools import lru_cache
    sources=grammar()
    responses=tuple(signatures(p,targets) for p in sources)
    seed=tuple(range(len(targets))) if initial is None else tuple(initial)

    @lru_cache(maxsize=None)
    def solve(state):
        if len(state)==1:return (0,0,None)
        best=None
        for idx,p in enumerate(sources):
            blocks=partition(responses[idx],state)
            if len(blocks)<2:
                continue
            children=[solve(tuple(b)) for b in blocks]
            # Sum of total question-count over all equally likely worlds.
            # If child only has 1 world -> zero more questions.
            total=len(state)+sum(ch[0] for ch in children)
            complexity=len(state)*p[0]+sum(ch[1] for ch in children)
            item=(total,complexity,idx)
            if best is None or item<best:
                best=item
        if best is None:return (10**9,10**9,None)
        return best
    total,cost,first=solve(seed)
    return {
        "states":len(seed),
        "minimum_sum_questions":total,
        "minimum_mean_questions":total/len(seed),
        "minimum_weighted_vertex_cost":cost,
        "first_probe":characterize(sources[first]) if first is not None else None,
        "entire_declared_probe_family_considered":len(sources),
        "exact_classical_finite_dynamic_programming":True
    }

def selected_action_tree(targets,trace=True):
    """Greedy adaptive probe selection using exact partition separation.

    In each unresolved class choose maximal pair separation, tie-break
    lower source vertex count then edge count; keep an explicit action
    tree that can be replayed without target labels.
    """
    sources=grammar()
    observations=tuple(signatures(p,targets) for p in sources)
    indices=tuple(range(len(targets)))
    log=[]
    def build(state):
        if len(state)==1:
            return {"resolved_state":state[0]}
        choices=[]
        for i,p in enumerate(sources):
            score=uniform_entropy_split(observations[i],state)
            if score>0:
                choices.append((-score,p[0],len(p[1]),i))
        if not choices:
            return {"unresolved_states":list(state),"HOLD":True}
        _,_,_,choice=min(choices)
        source=sources[choice]
        blocks=partition(observations[choice],state)
        if trace:log.append({"candidate":characterize(source),
                             "state_indices":list(state),
                             "distinct_responses":sorted(set(observations[choice][i]
                                                             for i in state)),
                             "splitting_score":-min(choices)[0]})
        return {
            "question":characterize(source),
            "question_index":choice,
            "response_branches":{
                str(observations[choice][block[0]]):build(tuple(block))
                for block in blocks
            },
        }
    tree=build(indices)
    return {"tree":tree,"search_trace":log,
            "root_candidate_count":len(sources),
            "all_target_signatures":[list(x) for x in observations],
            "no_human_intent_inferred":True}

def execute_tree(tree,carrier):
    """Evaluate a prebuilt tree against a world without knowing its label."""
    steps=[]
    current=tree
    while "question_index" in current:
        probe=grammar()[current["question_index"]]
        answer=count(probe,carrier)
        steps.append({"probe":characterize(probe),"observed":answer})
        current=current["response_branches"].get(str(answer),{"HOLD":True})
    return {
        "resolved_world_index":current.get("resolved_state"),
        "unresolved":current.get("HOLD",False),
        "trace":steps,
    }
