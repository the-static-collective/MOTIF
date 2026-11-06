"""REASON-018 source-owned *unlabeled* relational worlds.

The concept under study does not exist as a primitive relation. The learner is
given relations and concrete graph examples, not the formula connecting them.
All nodes and interactions are fictional: no actual people, love or welfare.

Source-owner hidden reference semantics live in oracle.py (never imported by
inventor.py). Test/heldout graph topologies have more nodes and extra decoys,
not just new personal names. The public source still discloses the alphabet
and world generator; this is NOT a cryptographically sealed benchmark.
"""
from __future__ import annotations

from random import Random

SCHEMA="motif.reason.living-concept.world.v1"
RELATIONS=("OFFER","OPEN","RELEASE","FREE","CLAIM","LINK")
MODES=("PRESENT","NO_OFFER","NO_OPEN","NO_RELEASE","SPLIT_WITNESS",
       "WRONG_DIRECTION","NO_FREE","CLAIM_ONLY","UNKNOWN_GATE",
       "CONFLICT_GATE","DISTRACTOR")
MODES=list(MODES)


def make(index,split="TRAIN"):
    if split not in ("TRAIN","HELDOUT"):
        raise ValueError("Unrecognized source split")
    seed=104729+index*101+(0 if split=="TRAIN" else 271828)
    rng=Random(seed)
    mode=MODES[index%len(MODES)]
    count=3+(index%4) if split=="TRAIN" else 5+(index%12)
    nodes=["A","B"]+["W"+str(n) for n in range(count)]
    assert len(nodes)==len(set(nodes))
    edges=set()
    good="W0"
    edges.update({
        ("OFFER","A","B"),
        ("OPEN","B",good),
        ("RELEASE",good,"A"),
        ("FREE","A","B"),
    })
    if mode=="NO_OFFER":edges.remove(("OFFER","A","B"))
    elif mode=="NO_OPEN":edges.remove(("OPEN","B",good))
    elif mode=="NO_RELEASE":edges.remove(("RELEASE",good,"A"))
    elif mode=="SPLIT_WITNESS":
        edges.remove(("RELEASE",good,"A"))
        edges.add(("RELEASE","W1","A"))
    elif mode=="WRONG_DIRECTION":
        edges.remove(("OPEN","B",good))
        edges.add(("OPEN","A",good))
    elif mode=="NO_FREE":edges.remove(("FREE","A","B"))
    elif mode=="CLAIM_ONLY":
        edges.remove(("FREE","A","B"))
        edges.add(("CLAIM","A","B"))
    elif mode=="UNKNOWN_GATE":
        edges.remove(("FREE","A","B"))
    elif mode=="CONFLICT_GATE":edges.add(("CLAIM","A","B"))
    elif mode=="DISTRACTOR":
        edges.add(("CLAIM","A","W0"))
    # Distractor edges are additive; never artificially erase the required
    # source evidence. We inject unrelated joins, misleading directions and
    # claims about unrelated people to disambiguate the learned clause.
    for j in range(count*2+index%7):
        left=rng.choice(nodes)
        right=rng.choice(nodes)
        rel=rng.choice(RELATIONS)
        if left==right:continue
        # Do not fill missing defining edges, turning controlled negatives
        # into positives. All labels are still determined by the oracle.
        if rel in ("OFFER","FREE","CLAIM") and (left,right)==("A","B"):
            continue
        if rel=="OPEN" and left=="B" and right=="W0":continue
        if rel=="RELEASE" and left=="W0" and right=="A":continue
        edges.add((rel,left,right))
    # Heldout graphs introduce genuinely new finite topologies and many
    # distractor entities, not merely synonym substitution.
    if split=="HELDOUT":
        for j in range(count):
            u="W"+str(j)
            edges.add(("LINK",u,"B"))
            if j+1<count:
                edges.add(("LINK",u,"W"+str(j+1)))
    return {
        "schema":SCHEMA,
        "id":("TR-" if split=="TRAIN" else "HO-")+str(index).zfill(3),
        "source_partition":split,
        "seed":seed,
        "actor":"A","recipient":"B","nodes":nodes,
        "edges":[list(t) for t in sorted(edges)],
        "relations":list(RELATIONS),
        "source_kind":"SYNTHETIC_FINITE_RELATIONAL_GRAPH",
        "new_concept_not_a_relation_primitive":True,
        "real_person_welfare_not_observed":True,
    }


def train_worlds():
    return tuple(make(i) for i in range(88))


def heldout_worlds():
    return tuple(make(i,"HELDOUT") for i in range(55))
