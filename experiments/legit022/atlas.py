"""LEGIT-022 independently ORIGINATED graph carriers: Read/Wilson Atlas.

Source data come from Ronald C. Read and Robin J. Wilson's 1998
Atlas of Graphs, distributed as 1253 distinct unlabelled graphs in the
open-source NetworkX 3.4.2 package. The data were not authored by
MOTIF. The *challenge selection procedure* and all evaluation code
ARE authored by MOTIF; this is NOT externally blind adjudication.

Pair selection uses only graph order, seven vertices and exact degree
multisets, NEVER candidate probe/homomorphism outcomes. A frozen,
deterministic split is enforced before any training or test measurements.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from random import Random
import json

VERSION="3.4.2"
SEED=22022
TRAIN_SIZE=14
TEST_SIZE=28
class HOLD(ValueError):pass

@dataclass(frozen=True)
class Task:
    atlas_ids: tuple[int,int]
    graphs: tuple[tuple,tuple]
    degree_signature: tuple[int,...]

def _networkx():
    import networkx as nx
    from networkx.generators import atlas
    if nx.__version__!=VERSION:
        raise HOLD("External graph source version changed")
    data=Path(atlas.__file__).with_name("atlas.dat.gz")
    if not data.is_file():
        raise HOLD("Missing external original atlas data file")
    raw=data.read_bytes()
    if len(raw)<6000 or len(raw)>30000:
        raise HOLD("Unexpected atlas source data size")
    return nx,sha256(raw).hexdigest(),len(raw)

def _carrier(graph):
    nodes=tuple(sorted(graph.nodes()))
    if nodes!=tuple(range(len(nodes))):
        raise HOLD("Unexpected source labelling")
    edges=tuple(sorted(tuple(sorted((int(a),int(b))))
                       for a,b in graph.edges()))
    n=len(nodes)
    if n!=7 or any(a==b or not 0<=a<b<n for a,b in edges):
        raise HOLD("Not a simple seven-node external graph")
    return (n,edges)

def cohort():
    nx,digest,size=_networkx()
    graphs=nx.graph_atlas_g()
    if len(graphs)!=1253 or sum(len(g)==7 for g in graphs)!=1044:
        raise HOLD("NetworkX atlas number of graphs changed")
    groups=defaultdict(list)
    for idx,graph in enumerate(graphs):
        if len(graph)!=7:continue
        key=tuple(sorted(degree for node,degree in graph.degree()))
        groups[key].append((idx,_carrier(graph)))
    pairs=[]
    for signature,items in sorted(groups.items()):
        # No probes are evaluated when deciding which comparisons exist.
        for a,b in zip(items[::2],items[1::2]):
            pairs.append(Task((a[0],b[0]),(a[1],b[1]),signature))
    rng=Random(SEED)
    rng.shuffle(pairs)
    if len(pairs)<TRAIN_SIZE+TEST_SIZE:
        raise HOLD("Not enough atlas-matched independent carriers")
    selected=tuple(pairs[:TRAIN_SIZE+TEST_SIZE])
    train=selected[:TRAIN_SIZE]
    test=selected[TRAIN_SIZE:]
    if len(set(t.atlas_ids for t in selected))!=len(selected):
        raise HOLD("Duplicate Atlas comparison")
    if any(t.degree_signature!=tuple(sorted(
           sum(1 for u,v in graph[1] if x in (u,v))
           for x in range(7))) for t in selected for graph in t.graphs):
        raise HOLD("Degree signature mismatch")
    # Strict internal protocol split, not cryptographically sealed:
    # everyone can open the public Atlas and reconstruct all queries.
    protocol={
        "source":"Read-Wilson, An Atlas of Graphs (1998), via NetworkX",
        "networkx_version":VERSION,
        "atlas_data_sha256":digest,
        "atlas_data_bytes":size,
        "atlas_graphs":len(graphs),
        "seven_node_graphs":1044,
        "pair_rule":"match exact degree multisets; adjacent index pairs",
        "pair_shuffle_seed":SEED,
        "selected_candidate_pair_count":len(pairs),
        "train_task_ids":[list(t.atlas_ids) for t in train],
        "heldout_task_ids":[list(t.atlas_ids) for t in test],
        "challenge_pairs_selected_without_probing_homomorphism_outcomes":True,
        "original_carrier_authorship_independent_of_MOTIF":True,
        "challenge_pairing_and_split_authored_by_MOTIF":True,
        "benchmark_is_public_and_not_externally_blind":True,
    }
    return train,test,protocol

def verify_prepared(train,test,source):
    if len(train)!=TRAIN_SIZE or len(test)!=TEST_SIZE:
        raise HOLD("Mutated registered sizes")
    seen=set()
    for item in train+test:
        if item.atlas_ids in seen:
            raise HOLD("Overlapping training and test comparison")
        seen.add(item.atlas_ids)
        if item.graphs[0]==item.graphs[1]:
            raise HOLD("Trivially identical source carriers")
    if source["benchmark_is_public_and_not_externally_blind"] is not True:
        raise HOLD("Invalid source provenance")
    return True
