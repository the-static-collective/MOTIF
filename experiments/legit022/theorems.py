"""LEGIT-022 — generated graph-hom conjectures and mathematical falsifiers.

An empirical symbolic search identifies the product law for homomorphism
counts of disconnected source graphs. A separate *human-inspectable
combinatorial bijection argument* explains why the product identity
holds for arbitrary finite target graphs. The experiment tests the law
with a separately implemented exact assignment enumerator.

This is known mathematics. The argument is encoded in the program by
the researcher; neither formal completeness nor historical originality
was autonomously proved by MOTIF.

An intentionally broader tempting conjecture, "matching degree
multisets implies every tree-hom count agrees", is challenged on
independently sourced Atlas graph pairs with exact counterexamples.
"""
from __future__ import annotations
from itertools import combinations,permutations
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit021"))
from graph_inventor import (grammar,connected,normalized,
    characterize,count,reference_count,adjacency)

class HOLD(ValueError):pass

@lru_cache(maxsize=1)
def all_unlabeled_sources_up_to_four():
    results=[]
    for n in range(1,5):
        all_edges=tuple(combinations(range(n),2))
        reps=set()
        for bits in range(1<<len(all_edges)):
            edges=tuple(e for i,e in enumerate(all_edges) if bits&(1<<i))
            reps.add((n,normalized(n,edges)))
        results+=sorted(reps,key=lambda x:(x[0],len(x[1]),x[1]))
    # 1+2+4+11 unlabelled graphs, including disconnected graphs
    if len(results)!=18 or len([p for p in results if connected(*p)])!=10:
        raise HOLD("Incorrect exhaustive graph-source grammar")
    return tuple(results)

def components(source):
    n,edges=source
    nbr=[set() for _ in range(n)]
    for a,b in edges:
        nbr[a].add(b);nbr[b].add(a)
    unseen=set(range(n))
    result=[]
    while unseen:
        stack=[min(unseen)]
        unseen.remove(stack[0])
        comp=[]
        while stack:
            a=stack.pop()
            comp.append(a)
            for b in sorted(nbr[a]&unseen):
                unseen.remove(b);stack.append(b)
        comp=sorted(comp)
        lookup={old:i for i,old in enumerate(comp)}
        ce=tuple(sorted((lookup[a],lookup[b]) for a,b in edges
                        if a in lookup and b in lookup))
        result.append((len(comp),ce))
    return tuple(result)

def correct_product(source,graph):
    value=1
    for part in components(source):
        value*=count(part,graph)
    return value

def propose_composition_rule(training,limit=8):
    """Search a small symbolic arithmetic rule DSL, not a hardcoded answer.

    Candidate operation selection uses actual counts for the
    DISCONNECTED source graphs, evaluated on a preregistered training
    subset. Future test labels are not used.
    """
    if not training or len(training)<limit:
        raise HOLD("Need independent-origin training carriers")
    candidates={
        "PRODUCT":lambda values:prod(values),
        "SUM":lambda values:sum(values),
        "MAX":lambda values:max(values),
        "MIN":lambda values:min(values),
    }
    disconnected=tuple(x for x in all_unlabeled_sources_up_to_four()
                       if len(components(x))>1)
    graphs=tuple(t.graphs[i] for t in training[:limit] for i in (0,1))
    statuses={}
    for name,function in candidates.items():
        mismatches=[]
        for source in disconnected:
            parts=components(source)
            for graph in graphs:
                actual=count(source,graph)
                proposal=function([count(p,graph) for p in parts])
                if actual!=proposal:
                    mismatches.append({
                        "source":[source[0],[list(e) for e in source[1]]],
                        "component_order":[p[0] for p in parts],
                        "observed":actual,"proposed":proposal,
                        "target_node_count":graph[0],
                    })
                    break
            if mismatches:break
        statuses[name]={
            "training_pairs":limit,"training_graphs":len(graphs),
            "disconnected_source_types":len(disconnected),
            "survived_training":not mismatches,
            "first_counterexample":mismatches[0] if mismatches else None,
        }
    accepted=[name for name,row in statuses.items()
              if row["survived_training"]]
    if accepted!=["PRODUCT"]:
        raise HOLD("Expression miner failed to isolate factorization")
    return {
        "candidate_operation_language":list(candidates),
        "disconnected_source_graphs":len(disconnected),
        "selected":"PRODUCT",
        "failed_hypotheses":[name for name in candidates if name not in accepted],
        "genuinely_computed_training_spectra":statuses,
        "all_cases_user_experiment_selected":True,
        "formal_proof_autonomously_generated":False,
        "historically_novel_mathematics":False,
    }

def prod(values):
    result=1
    for x in values:result*=x
    return result

def certify_factorization(pair_tasks):
    """Mathematical certificate plus independent finite regression.

    Generic proof: a homomorphism from disjoint source components is
    uniquely a tuple of independent component homomorphisms, since
    there are no cross-component edges. Taking cardinalities gives
    a product. The proof scheme is already mathematical knowledge
    supplied by the engineer, not independent theorem invention.
    """
    disconnected=tuple(x for x in all_unlabeled_sources_up_to_four()
                       if len(components(x))>1)
    graphs=tuple(t.graphs[i] for t in pair_tasks for i in (0,1))
    checked=0
    for source in disconnected:
        for graph in graphs:
            observed=reference_count(source,graph)
            parts=components(source)
            expected=prod(reference_count(part,graph) for part in parts)
            if observed!=expected or observed!=correct_product(source,graph):
                raise HOLD("Independent finite enumerator disproves factorization")
            checked+=1
    return {
        "known_identity":
            "hom(disjoint_union(F_i), G) = product_i hom(F_i, G)",
        "combinatorial_argument":
            "every adjacency-preserving map from a disconnected source "
            "uniquely restricts to one independent map per component; "
            "independent component maps uniquely glue to one full map",
        "universal_proof_argument_written_by_researcher":True,
        "independent_exhaustive_assignment_comparisons":checked,
        "unlabeled_sources_total":len(all_unlabeled_sources_up_to_four()),
        "connected_sources_kept":len(grammar()),
        "disconnected_sources_mathematically_redundant_for_separation":
            len(disconnected),
        "finite_assignment_checks_not_independent_new_theorem_proof":True,
        "literature_novelty_not_claimed":True,
    }

def challenge_degree_conjecture(training):
    """Try to refute over-generalization from equal degrees + short trees.

    Paths/stars with <=3 vertices are degree-multiset determined. The
    four-vertex path counts depend also on correlations of degrees at
    neighbouring vertices. Search only the preregistered TRAIN pairs.
    """
    path4=next(p for p in grammar() if p[0]==4 and
              sorted(sum(1 for edge in p[1] if i in edge)
                     for i in range(4))==[1,1,2,2])
    wrong=None
    for item in training:
        a,b=item.graphs
        s0=reference_count(path4,a)
        s1=reference_count(path4,b)
        if s0!=s1:
            wrong={
                "atlas_ids":list(item.atlas_ids),
                "equal_degree_multisets":list(item.degree_signature),
                "source_probe":characterize(path4),
                "observed_path4_homomorphisms":[s0,s1],
                "actual_counterexample_to_overgeneralization":True,
            }
            break
    return {
        "speculative_broad_conjecture":
            "identical degree multisets imply identical all-tree hom counts",
        "basis":"degree-matched graph carriers and simpler tree probes",
        "test_source":"independently originated Read/Wilson Atlas training graphs",
        "counterexample":wrong,
        "hypothesis_refuted":wrong is not None,
        "no_general_all_tree_equivalence_theorem_claimed":True,
        "is_known_graph_theory_not_historically_new":True,
    }
