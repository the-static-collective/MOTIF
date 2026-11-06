"""MOTIF GEOM-005 — An optional geometric scratchpad for relational thoughts.

Coordinates are computed *views*, not evidence. Every edge is typed, sourced,
weighted and stamped as observed or hypothetical. Nothing causes an outside act.
"""
from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from math import cos, sin, tau, hypot, sqrt
import re

# This prototype is a relational instrument, not a natural-language model.
POSITIVE = frozenset({'associated', 'enables', 'requires', 'co_mentioned'})
DIRECTIONAL = frozenset({'enables','requires'})
ALL_RELATIONS = POSITIVE | {'contradicts'}
STOPWORDS = frozenset('the a an and but or is are to from in on this that of with it be by for as do does'.split())

@dataclass(frozen=True)
class Node:
    id: str
    label: str
    kind: str = 'concept'

@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    relation: str
    origin: str    # source witness, NOT cryptographically authenticated
    confidence: float = 1.0
    observed: bool = True

    def __post_init__(self):
        if self.relation not in ALL_RELATIONS:raise ValueError('unknown relation')
        if not self.origin:raise ValueError('missing provenance')
        if not 0 < self.confidence <= 1:raise ValueError('invalid confidence')

class ThoughtGraph:
    def __init__(self, nodes=(), edges=()):
        self.nodes:dict[str,Node]={}
        self.edges:list[Edge]=[]
        for n in nodes:self.add_node(n)
        for e in edges:self.add_edge(e)

    def add_node(self,node:Node):
        if not node.id or not node.label:raise ValueError('missing node name')
        if node.id in self.nodes and self.nodes[node.id]!=node:raise ValueError('id conflict')
        self.nodes[node.id]=node

    def add_edge(self,edge:Edge):
        if edge.source not in self.nodes or edge.target not in self.nodes or edge.source==edge.target:
            raise ValueError('edge endpoints must be distinct and observed')
        if edge not in self.edges:self.edges.append(edge)

    def positive_links(self,*, include_co_mention=False):
        return [e for e in self.edges if e.observed and e.relation in POSITIVE and
                (include_co_mention or e.relation!='co_mentioned')]

    def adjacency(self,*, include_co_mention=False):
        adj={x:[] for x in self.nodes}
        for e in self.positive_links(include_co_mention=include_co_mention):
            # requires direction: source is prerequisite seeker, target is prerequisite;
            # causal route traverses only authored edge direction.
            adj[e.source].append((e.target,e))
            if e.relation not in DIRECTIONAL:adj[e.target].append((e.source,e))
        for k in adj: adj[k].sort(key=lambda t:(t[0],t[1].relation,t[1].origin))
        return adj

    def route(self,start:str,goal:str,*, include_co_mention=False):
        if start not in self.nodes or goal not in self.nodes:
            return {'status':'HOLD','reason':'unknown anchor'}
        adj=self.adjacency(include_co_mention=include_co_mention)
        paths=deque([(start,[start],[])])
        seen={start}
        while paths:
            cur,nodes,used=paths.popleft()
            if cur==goal:
                return {'status':'PATH','nodes':nodes,'witnesses':[asdict(e) for e in used],
                        'inference':'structural connection, not causal proof', 'authority':'HOLD'}
            for nxt,e in adj[cur]:
                if nxt not in seen:
                    seen.add(nxt);paths.append((nxt,nodes+[nxt],used+[e]))
        return {'status':'HOLD','reason':'no witnessed typed path'}

    def components(self,*, include_co_mention=False):
        # Interpret connectivity undirected *for layout only*, without asserting
        # that directional prerequisites can be traversed backward.
        adj={n:set() for n in self.nodes}
        for e in self.positive_links(include_co_mention=include_co_mention):
            adj[e.source].add(e.target);adj[e.target].add(e.source)
        seen=set();out=[]
        for n in sorted(self.nodes):
            if n in seen:continue
            stack=[n];comp=[];seen.add(n)
            while stack:
                x=stack.pop();comp.append(x)
                for y in sorted(adj[x]):
                    if y not in seen:seen.add(y);stack.append(y)
            out.append(sorted(comp))
        return sorted(out,key=lambda c:(-len(c),c))

    def bridge_candidates(self,*,min_independent_origins=2):
        """Common-neighbor hypotheses; two origins must truly be distinct.

        A repeated quote with one root counts once. This is NOT a semantic
        entailment or a claim the new association exists.
        """
        neighbors=defaultdict(lambda:defaultdict(set))
        for e in self.positive_links():
            if e.relation!='associated':continue
            neighbors[e.source][e.target].add(e.origin)
            neighbors[e.target][e.source].add(e.origin)
        found=[]
        ids=sorted(self.nodes)
        existing={frozenset((e.source,e.target)) for e in self.positive_links()}
        for i,x in enumerate(ids):
            for y in ids[i+1:]:
                if frozenset((x,y)) in existing:continue
                commons=sorted(set(neighbors[x]) & set(neighbors[y]))
                # Evidence is a set of original edges; do not hallucinate a
                # direct link, or assume echoed origin strings independent.
                witness=[{'via':z,'left_origins':sorted(neighbors[x][z]),
                          'right_origins':sorted(neighbors[y][z])} for z in commons]
                roots={o for z in commons for o in neighbors[x][z]|neighbors[y][z]}
                if len(commons)>=2 and len(roots)>=min_independent_origins:
                    found.append({'nodes':[x,y], 'via':commons, 'witnesses':witness,
                                  'distinct_roots':len(roots),'status':'HYPOTHESIS_ONLY',
                                  'interpretation':'possible association; not an observed edge'})
        return sorted(found,key=lambda r:(-len(r['via']),-r['distinct_roots'],r['nodes']))

    def contradictions(self):
        return [asdict(e) for e in self.edges if e.observed and e.relation=='contradicts']

    def as_data(self):
        return {'nodes':[asdict(self.nodes[k]) for k in sorted(self.nodes)],
                'edges':[asdict(e) for e in sorted(self.edges,key=lambda x:(x.source,x.target,x.relation,x.origin))]}


def from_text(text:str,origin:str,*,max_terms=24) -> ThoughtGraph:
    """Explicitly weak co-mention extraction from prose, not concept understanding.

    No attempt is made to infer truth, causality, antonyms or entailment.
    """
    if not origin or not 1<=max_terms<=64:raise ValueError('origin/capacity required')
    terms=[t.lower() for t in re.findall(r"[A-Za-z][A-Za-z'-]*",text) if len(t)>2 and t.lower() not in STOPWORDS]
    ordered=list(dict.fromkeys(terms))[:max_terms]
    g=ThoughtGraph([Node(t,t,'word') for t in ordered])
    for a,b in zip(terms,terms[1:]):
        if a in g.nodes and b in g.nodes and a!=b:
            e=Edge(a,b,'co_mentioned',origin,0.1)
            g.add_edge(e)
    return g


def layout_spring(graph:ThoughtGraph,steps=150):
    """Deterministic Fruchterman-Reingold-like projection, for display only."""
    ids=sorted(graph.nodes);n=len(ids)
    if not n:return {}
    # Put nodes initially on a circle, deterministic but not semantic coordinates.
    pos={x:[cos(tau*i/n),sin(tau*i/n)] for i,x in enumerate(ids)}
    if n==1:return {ids[0]:(0.,0.)}
    positive=graph.positive_links(include_co_mention=True)
    all_links={(e.source,e.target):max(0.1,e.confidence) for e in positive}
    for k in range(steps):
        push={id:[0.,0.] for id in ids}
        for i,a in enumerate(ids):
            for b in ids[i+1:]:
                dx=pos[a][0]-pos[b][0];dy=pos[a][1]-pos[b][1]
                dist=max(0.02,hypot(dx,dy))
                strength=0.032/(dist*dist)
                vx,vy=dx/dist*strength,dy/dist*strength
                push[a][0]+=vx;push[a][1]+=vy
                push[b][0]-=vx;push[b][1]-=vy
        for e in positive:
            dx=pos[e.source][0]-pos[e.target][0]
            dy=pos[e.source][1]-pos[e.target][1]
            dist=max(0.02,hypot(dx,dy))
            strength=0.11*e.confidence*dist
            vx,vy=dx/dist*strength,dy/dist*strength
            push[e.source][0]-=vx;push[e.source][1]-=vy
            push[e.target][0]+=vx;push[e.target][1]+=vy
        temp=0.12*(1-k/steps)+0.005
        for x in ids:
            dx,dy=push[x]; d=hypot(dx,dy)
            if d:pos[x][0]+=dx/d*min(d,temp);pos[x][1]+=dy/d*min(d,temp)
    return {k:tuple(pos[k]) for k in ids}


def layout_radial(graph:ThoughtGraph, anchor:str):
    """Anchor-centered BFS circles; unreachable nodes remain on outer ring."""
    if anchor not in graph.nodes:raise ValueError('missing anchor')
    adj={n:set() for n in graph.nodes}
    for e in graph.positive_links(include_co_mention=True):
        adj[e.source].add(e.target);adj[e.target].add(e.source)
    depths={anchor:0};todo=deque([anchor])
    while todo:
        x=todo.popleft()
        for y in sorted(adj[x]):
            if y not in depths:depths[y]=depths[x]+1;todo.append(y)
    out={anchor:(0.,0.)}
    by_ring=defaultdict(list)
    for n in graph.nodes:
        if n==anchor:continue
        by_ring[depths.get(n,max(depths.values(),default=0)+2)].append(n)
    for depth,members in sorted(by_ring.items()):
        for i,n in enumerate(sorted(members)):
            a=tau*i/len(members)
            out[n]=(depth*cos(a),depth*sin(a))
    return out


def layout_hex(graph:ThoughtGraph, anchor:str):
    """Optional flower-of-life prior; display-only spiral packing.

    NOT evidence that concepts 'are' points on a sacred lattice.
    """
    if anchor not in graph.nodes:raise ValueError('missing anchor')
    rest=sorted(n for n in graph.nodes if n!=anchor)
    coords=[(0,0)]
    radius=1
    while len(coords)<len(graph.nodes):
        coords += sorted([(q,r) for q in range(-radius,radius+1)
                          for r in range(-radius,radius+1)
                          if max(abs(q),abs(r),abs(q+r))==radius])
        radius+=1
    return {n:(q+r/2,sqrt(3)*r/2) for n,(q,r) in zip([anchor,*rest],coords)}


def edge_stress(graph:ThoughtGraph, coords):
    """Comparable display compactness score. No epistemic meaning."""
    active=graph.positive_links(include_co_mention=True)
    if not active:return 0.0
    return round(sum(e.confidence*(hypot(coords[e.source][0]-coords[e.target][0],
                                       coords[e.source][1]-coords[e.target][1])-0.8)**2
                     for e in active)/len(active),6)


def choose_thought_space(graph:ThoughtGraph,question:str='',anchors=(),*,allow_geometry=True, geometry_preference='auto'):
    """Small, explainable metareasoning router. Never claims free-form thought.

    A graph may choose not to draw a geometric view. A task may use several
    representations without equating distance to semantic similarity.
    """
    if geometry_preference not in ('auto','spring','radial','flower_hex'):
        raise ValueError('unsupported geometry preference')
    question=question.lower()
    route_words=('path','connect','route','from','to','reach','depend','how')
    contrast_words=('conflict','contradict','compare','tension','opposite')
    cluster_words=('cluster','group','themes','organize')
    valid=tuple(x for x in anchors if x in graph.nodes)
    conflicts=graph.contradictions()
    candidates=graph.bridge_candidates()
    chosen='trace' if len(valid)>=2 and any(w in question.split() for w in route_words) else (
        'contrast' if conflicts and any(w in question for w in contrast_words) else (
        'cluster' if any(w in question for w in cluster_words) else (
        'bridge' if candidates else 'trace' if len(valid)>=2 else 'inventory')))
    if len(valid)>=2 and chosen=='trace':answer=graph.route(valid[0],valid[1])
    elif chosen=='bridge':answer={'status':'HYPOTHESES','proposals':candidates}
    elif chosen=='contrast':answer={'status':'CONFLICTS','witnesses':conflicts}
    elif chosen=='cluster':answer={'status':'GROUPS','components':graph.components()}
    else:answer={'status':'INVENTORY','nodes':len(graph.nodes),'edges':len(graph.edges)}
    if not allow_geometry or not graph.nodes or not graph.positive_links(include_co_mention=True):
        return {'thought_mode':chosen,'projection':'NONE','reason':'geometry optional or structurally unsupported',
                'answer':answer,'coordinates':{},'authority':'HOLD'}
    anchor=valid[0] if valid else sorted(graph.nodes)[0]
    layouts={'spring':layout_spring(graph),'radial':layout_radial(graph,anchor),
             'flower_hex':layout_hex(graph,anchor)}
    scores={k:edge_stress(graph,p) for k,p in layouts.items()}
    # Task has priority over attractive graphics. Geometry is a working view.
    projection = (geometry_preference if geometry_preference!='auto' else
        min(scores,key=lambda x:(scores[x],x)) if chosen in ('bridge','cluster','inventory') else 'radial')
    return {'thought_mode':chosen,'projection':projection,'projection_scores':scores,
            'reason':'task-conditioned reasoning; positions are non-evidentiary',
            'answer':answer,'coordinates':layouts[projection],'authority':'HOLD'}
