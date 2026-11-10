"""MOTIF FIELD-008: evidence-rooted conditional hypotheses, no assumption promotion.

Read & Wilson's independently authored Atlas of Graphs is an archive of
historical mathematical objects. Our selection grammar, utility targets and
benchmark are authored. This is finite classical version-space research.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
import hashlib
import json
import math
import networkx as nx
from grounding import BlanchLedger

SCHEMA = 'motif.field008.blanch.v1'
NETWORKX_VERSION = '3.6.1'
SOURCE = 'Read-Wilson-Atlas-1998-via-NetworkX-3.6.1'
# Validated before any scored experiment; code refuses a drift in Atlas bytes.
ATLAS_SHA256 = '17f940be3d89a623bc291e0e3eb64b108987cd68a2c4f0a82b98b3294153bad9'
TARGETS = ('connected', 'triangles', 'four_cycles', 'bridges', 'articulations')
BUDGET = 4
AUDIT_7_COUNT = 96


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Probe:
    kind: str
    vertices: tuple[int, ...]
    depth: int

    @property
    def key(self):
        return ':'.join([self.kind] + [str(x) for x in self.vertices])

    @property
    def thought_path(self):
        paths = {
            'edge': ('condition-on-graph', 'assume adjacency'),
            'degree': ('condition-on-graph', 'collect incident edges', 'count'),
            'common': ('condition-on-graph', 'trace both endpoints', 'intersect neighbors', 'count'),
            'triangles': ('condition-on-graph', 'enumerate triples', 'compose adjacency', 'count'),
            'four_cycles': ('condition-on-graph', 'enumerate shared neighbors', 'compose length-four closures', 'deduplicate cycles', 'count'),
            'connected': ('condition-on-graph', 'create adjacency', 'follow all reachable vertices', 'test complete coverage'),
            'bridges': ('condition-on-graph', 'enumerate edges', 'remove one conditionally', 'recount components', 'sum bridge witnesses'),
            'articulations': ('condition-on-graph', 'enumerate vertices', 'remove one conditionally', 'recount components', 'sum cut vertices'),
        }
        return paths[self.kind]


def catalog(n):
    probes = [Probe('edge', (i, j), 1) for i, j in combinations(range(n), 2)]
    probes += [Probe('degree', (i,), 2) for i in range(n)]
    probes += [Probe('common', (i, j), 3) for i, j in combinations(range(n), 2)]
    probes += [Probe('triangles', (), 3), Probe('four_cycles', (), 4),
               Probe('connected', (), 4), Probe('bridges', (), 5),
               Probe('articulations', (), 5)]
    assert len({p.key for p in probes}) == len(probes)
    assert all(len(p.thought_path) >= p.depth for p in probes)
    return tuple(probes)


def from_graph(G, p):
    """Hypothetical, pencil-only evaluation; never an independent observation."""
    n = len(G)
    if p.kind == 'edge':
        return int(G.has_edge(*p.vertices))
    if p.kind == 'degree':
        return sum(int(G.has_edge(p.vertices[0], j)) for j in range(n))
    if p.kind == 'common':
        a, b = p.vertices
        return sum(int(G.has_edge(a, k) and G.has_edge(b, k)) for k in range(n))
    if p.kind == 'triangles':
        return sum(int(G.has_edge(a, b) and G.has_edge(b, c) and G.has_edge(a, c))
                   for a, b, c in combinations(range(n), 3))
    if p.kind == 'four_cycles':
        # Each simple four-cycle has exactly two opposite-vertex pairs.
        return sum(math.comb(sum(G.has_edge(a, t) and G.has_edge(b, t)
                                 for t in range(n)), 2)
                   for a, b in combinations(range(n), 2)) // 2
    if p.kind == 'connected':
        if n == 0: return 0
        found = {0}
        frontier = [0]
        while frontier:
            a = frontier.pop()
            for v in range(n):
                if v not in found and G.has_edge(a, v):
                    found.add(v); frontier.append(v)
        return int(len(found) == n)
    if p.kind in ('bridges', 'articulations'):
        initial = nx.number_connected_components(G)
        if p.kind == 'bridges':
            count = 0
            for a,b in list(G.edges()):
                H = G.copy(); H.remove_edge(a, b)
                count += nx.number_connected_components(H) > initial
            return int(count)
        count = 0
        for a in G.nodes():
            H = G.copy(); H.remove_node(a)
            count += nx.number_connected_components(H) > initial
        return int(count)
    raise ValueError('unsupported hypothetical predicate')


def owner_answer(G, p):
    """Source-owner recomputation using independent NetworkX routines where possible.

    This independence is algorithmic, NOT a separate human or organization.
    """
    if p.kind == 'edge': return int(p.vertices[1] in G[p.vertices[0]])
    if p.kind == 'degree': return int(G.degree[p.vertices[0]])
    if p.kind == 'common': return len(set(G.neighbors(p.vertices[0])) & set(G.neighbors(p.vertices[1])))
    if p.kind == 'triangles': return sum(nx.triangles(G).values()) // 3
    if p.kind == 'four_cycles':
        all_cycles = set()
        for four in combinations(G.nodes, 4):
            for cycle in ((four[0], four[1], four[2], four[3]),
                          (four[0], four[1], four[3], four[2]),
                          (four[0], four[2], four[1], four[3])):
                if all(G.has_edge(cycle[i], cycle[(i+1)%4]) for i in range(4)):
                    all_cycles.add((four, tuple(sorted(tuple(sorted((cycle[i],cycle[(i+1)%4]))) for i in range(4)))))
        return len(all_cycles)
    if p.kind == 'connected': return int(nx.is_connected(G))
    if p.kind == 'bridges': return sum(1 for _ in nx.bridges(G))
    if p.kind == 'articulations': return sum(1 for _ in nx.articulation_points(G))
    raise ValueError('unreviewed source probe')


def corpus_digest(graphs):
    return sha([(i, len(G), sorted(tuple(sorted(e)) for e in G.edges())) for i, G in enumerate(graphs)])


@lru_cache(maxsize=1)
def atlas():
    if nx.__version__ != NETWORKX_VERSION:
        raise RuntimeError('SOURCE_VERSION_DRIFT; expected networkx=='+NETWORKX_VERSION)
    graphs = tuple(nx.graph_atlas_g())
    if len(graphs) != 1253:
        raise RuntimeError('CORPUS_COUNT_DRIFT')
    actual = corpus_digest(graphs)
    if actual != ATLAS_SHA256:
        raise RuntimeError('SOURCE_BYTES_DRIFT '+actual)
    return graphs


class Owner:
    """One simulated archive owner; model never receives hidden target ID.

    Same-process access is NOT cryptographically isolated. Receipts have stable
    content digests but are independently recomputed against source archive.
    """
    def __init__(self, graph_id, corpus=None):
        self.graphs = atlas() if corpus is None else corpus
        self._id = graph_id
        self._G = self.graphs[graph_id]
        self.probes = {p.key:p for p in catalog(len(self._G))}
        self.source_revision = ATLAS_SHA256
        self.history = []

    def root(self):
        packet = dict(schema=SCHEMA, kind='SOURCE_OBSERVATION', source=SOURCE,
                      source_revision=self.source_revision, probe='initial_edge_count',
                      answer=self._G.number_of_edges(), vertex_count=len(self._G),
                      provenance_origin='one_atlas_corpus', status='INK')
        return {**packet,'sha256':sha(packet)}

    def ask(self, question_key):
        if question_key not in self.probes: raise ValueError('UNREVIEWED_PROBE')
        if any(x['probe']==question_key for x in self.history):
            raise ValueError('DUPLICATE_SOURCE_QUERY')
        p = self.probes[question_key]
        packet = dict(schema=SCHEMA, kind='SOURCE_OBSERVATION',
                      source=SOURCE, source_revision=self.source_revision,
                      probe=question_key, answer=owner_answer(self._G, p),
                      provenance_origin='one_atlas_corpus', status='INK',
                      source_query_sequence=len(self.history)+1)
        receipt = {**packet,'sha256':sha(packet)}
        self.history.append(receipt)
        return receipt

    def verify(self, packet):
        if not isinstance(packet,dict): return False
        payload = {k:v for k,v in packet.items() if k!='sha256'}
        if packet.get('sha256') != sha(payload): return False
        if payload.get('source_revision') != self.source_revision or payload.get('source') != SOURCE:
            return False
        if payload.get('schema') != SCHEMA or payload.get('kind') != 'SOURCE_OBSERVATION':
            return False
        if payload.get('status') != 'INK' or payload.get('provenance_origin')!='one_atlas_corpus':
            return False
        if payload.get('probe')=='initial_edge_count':
            return packet == self.root()
        key = payload.get('probe')
        if key not in self.probes or not isinstance(payload.get('source_query_sequence'), int):
            return False
        if payload['source_query_sequence'] not in range(1, BUDGET+1):
            return False
        return (payload.get('answer')==owner_answer(self._G, self.probes[key]) and
                payload.get('vertex_count') is None and packet in self.history)


@dataclass
class SourceCatalog:
    n: int
    ids: tuple[int, ...]
    probes: tuple[Probe, ...]
    predictions: dict[str,dict[int,int]]
    properties: dict[str,dict[int,int]]
    edge_counts: dict[int,int]


@lru_cache(maxsize=2)
def source_catalog(n):
    if n not in (6,7): raise ValueError('bound n=6 or n=7')
    all_graphs = atlas()
    ids = tuple(i for i,G in enumerate(all_graphs) if len(G)==n)
    probes = catalog(n)
    pred = {p.key:{i:from_graph(all_graphs[i], p) for i in ids} for p in probes}
    props = {k:pred[k] for k in TARGETS}
    # all target predicate names are in the all-probe catalog
    return SourceCatalog(n, ids, probes, pred, props,
                         {i: all_graphs[i].number_of_edges() for i in ids})


def choices_after(root, observations, c):
    if root['status'] != 'INK' or root['probe'] != 'initial_edge_count':
        raise ValueError('UNSUPPORTED_ROOT')
    survivors = [i for i in c.ids if c.edge_counts[i] == root['answer']]
    for r in observations:
        if r.get('kind')!='SOURCE_OBSERVATION' or r.get('status')!='INK':
            raise ValueError('UNVERIFIED_OBSERVATION')
        survivors = [i for i in survivors if c.predictions[r['probe']][i] == r['answer']]
    return tuple(survivors)


def partitions(ids, p, c):
    part = defaultdict(list)
    for i in ids: part[c.predictions[p.key][i]].append(i)
    return dict(part)


def discriminated_pairs(parts):
    n=sum(len(g) for g in parts.values())
    return (n*n - sum(len(g)**2 for g in parts.values()))//2


def entropy(parts):
    n = sum(len(v) for v in parts.values())
    return -sum((len(v)/n)*math.log2(len(v)/n) for v in parts.values())


def expected_target_resolution(parts, c):
    """How many downstream structural attributes one observation might fix.

    No probabilities of *reality*: this is an exactly enumerated uniform
    possible-world catalogue. Numerator is integer over n candidate worlds.
    """
    solved=0
    for name in TARGETS:
        for grp in parts.values():
            if len({c.properties[name][i] for i in grp}) == 1:
                solved += len(grp)
    return solved


def propose(policy, candidates, observed_keys, c):
    if policy not in ('near','entropy','gini','blanch','value_control'):
        raise ValueError('unsupported search policy')
    if not candidates: return None
    allowed = [p for p in c.probes if p.key not in observed_keys and (policy!='near' or p.depth==1)]
    ranked=[]
    for p in allowed:
        groups=partitions(candidates,p,c)
        separated=discriminated_pairs(groups)
        if separated==0: continue
        solved=expected_target_resolution(groups,c)
        # minus depth prevents a deeper operation winning a tie on information.
        if policy in ('blanch','value_control'): score=(solved,separated,-p.depth)
        elif policy=='entropy': score=(round(entropy(groups),12),-p.depth,separated)
        else: score=(separated,-p.depth,solved)
        ranked.append((score,p,groups))
    if not ranked:return None
    # Deterministic ordering; not dependent on the actual hidden graph identity.
    best=max(ranked,key=lambda row:(row[0], tuple(-ord(ch) for ch in row[1].key)))
    score,p,groups=best
    # Blanch several mutually incompatible possibilities. All remain PENCIL.
    branches = []
    for hypothetical_id in (candidates[:min(4,len(candidates))] if policy=='blanch' else ()):
        branches.append(dict(conditional_world=f'atlas-model-{hypothetical_id}',
                             status='PENCIL_BLANCHED_NOT_FACT',
                             conditional_prediction=c.predictions[p.key][hypothetical_id],
                             trace=list(p.thought_path),
                             source_root_origins=['one_atlas_corpus']))
    return dict(schema=SCHEMA,status='PROPOSED_BEFORE_SOURCE_QUERY',policy=policy,
                question=p.key,query_depth=p.depth,score=score,
                candidate_count=len(candidates),
                outcome_partition_sizes={str(k):len(v) for k,v in sorted(groups.items())},
                indistinguishable_pairs=discriminated_pairs(groups),
                expected_resolved_target_units=expected_target_resolution(groups,c),
                blanched_branches=branches,
                considered_probe_count=len(allowed),
                conditional_model_probe_evaluations=len(candidates)*len(allowed))


def resolved_targets(ids,c):
    return {name:len({c.properties[name][i] for i in ids}) == 1 for name in TARGETS}


def run_case(graph_id, policy, budget=BUDGET, full_trace=False):
    graphs=atlas(); n=len(graphs[graph_id]); c=source_catalog(n)
    owner=Owner(graph_id, graphs)
    root=owner.root()
    assert owner.verify(root)
    live=choices_after(root,[],c)
    history=[]; received=[]; work=0; seen=set()
    ledger=BlanchLedger() if policy=='blanch' else None
    if ledger is not None: ledger.ink('root', root, owner)
    for step in range(budget):
        if len(live)<=1: break
        question = propose(policy, live, seen, c)
        if question is None: break
        # Commit a logically complete BEFORE-answer packet, including current
        # evidence and conditional paths, before the independent source call.
        source_ancestry = [root['sha256']] + [r['sha256'] for r in received]
        frozen=dict(**question,step=step,ink_source_receipt_digests=source_ancestry,
                    source_query_count_before=len(owner.history),
                    source_origin_count=1, model_ids_before=list(live))
        frozen['proposal_sha256']=sha(frozen)
        work+=question['conditional_model_probe_evaluations']
        staged=[]
        if ledger is not None:
            for j, conditional in enumerate(frozen['blanched_branches']):
                model_id=int(conditional['conditional_world'].split('-')[-1])
                hypothesis_key=f'hyp_{step}_{j}'
                prediction_key=f'prediction_{step}_{j}'
                existing_evidence=['root']+[f'ink_{t}' for t in range(step)]
                support=ledger.blanch(hypothesis_key,[existing_evidence])
                ledger.claim(prediction_key,[[hypothesis_key]],claim_kind='LOCAL_PREDICTION')
                staged.append((model_id,hypothesis_key,prediction_key,support))
        prior=live
        raw=owner.ask(question['question'])
        if not owner.verify(raw): raise RuntimeError('SOURCE_VERIFICATION_FAILED')
        received.append(raw); seen.add(question['question'])
        local_branch_receipts=[]
        if ledger is not None:
            ledger.ink(f'ink_{step}',raw,owner)
            for model_id,hypothesis_key,prediction_key,support in staged:
                verdict=('OBSERVED_MATCH' if
                         c.predictions[question['question']][model_id]==raw['answer']
                         else 'REFUTED_LOCAL_PREDICTION')
                ledger.resolve(prediction_key,verdict)
                downstream=f'after_{prediction_key}'
                child=ledger.blanch(downstream,[[prediction_key]])
                local_branch_receipts.append(dict(world=f'atlas-model-{model_id}',
                    grounding_before=support, local_prediction_verdict=verdict,
                    downstream_epistemic_status=child['state'],
                    source_origin_count=child['independent_origin_count']))
        live=choices_after(root,received,c)
        if graph_id not in live: raise RuntimeError('TRUE_GRAPH_RETRACTED')
        # Critically: conditional predictions are never source observations.
        falsified=[i for i in prior if i not in live]
        record=dict(proposal=frozen,verified_source=raw,
                    retracted_conditional_worlds=list(falsified),
                    retained_alternative_worlds=list(live),
                    verified_properties=resolved_targets(live,c),
                    blanched_lineage=local_branch_receipts)
        if full_trace: history.append(record)
        else: history.append(dict(proposal_sha256=frozen['proposal_sha256'],
                                  question=question['question'],depth=question['query_depth'],
                                  source_digest=raw['sha256'],retracted_count=len(falsified),
                                  alternatives_remaining=len(live),
                                  status='INK_SOURCE_PLUS_SEPARATE_PENCIL_BRANCHES'))
    results=dict(schema=SCHEMA,source_scope=SOURCE,corpus_sha256=ATLAS_SHA256,
                 n=n,world_id_for_evaluator_only=graph_id,policy=policy,
                 original_source_root_sha256=root['sha256'],
                 initial_candidate_count=sum(v==root['answer'] for v in c.edge_counts.values()),
                 extra_queries=len(received),conditional_probe_evaluations=work,
                 total_conditional_branches_retracted=sum(x.get('retracted_count',len(x.get('retracted_conditional_worlds',[]))) for x in history),
                 remaining_models=len(live),unique_identified=len(live)==1,
                 properties_resolved=sum(resolved_targets(live,c).values()),
                 resolved_property_names=[name for name,ok in resolved_targets(live,c).items() if ok],
                 max_executed_depth=max([x.get('depth',x.get('proposal',{}).get('query_depth',0)) for x in history],default=0),
                 proof_steps=history,authority='RESEARCH_HOLD_NO_REAL_WORLD_AUTHORITY')
    results['packet_sha256']=sha(results)
    return results


def audit_ids(n):
    c=source_catalog(n)
    if n==6:return c.ids
    return tuple(sorted(c.ids,key=lambda i:sha(['FIELD008/7-node/audit/ID',i]))[:AUDIT_7_COUNT])


def benchmark():
    rows=[]
    for n in (6,7):
        for id in audit_ids(n):
            for policy in ('near','entropy','gini','blanch','value_control'):
                rows.append(run_case(id,policy))
    summary=[]
    for n in (6,7):
        for policy in ('near','entropy','gini','blanch','value_control'):
            group=[r for r in rows if r['n']==n and r['policy']==policy]
            summary.append(dict(n=n,policy=policy,cases=len(group),
                 unique=sum(r['unique_identified'] for r in group),
                 total_resolved_attributes=sum(r['properties_resolved'] for r in group),
                 total_extra_source_queries=sum(r['extra_queries'] for r in group),
                 total_conditional_probe_evaluations=sum(r['conditional_probe_evaluations'] for r in group),
                 deepest_executed=max(r['max_executed_depth'] for r in group)))
    lookup={(r['n'],r['policy']):r for r in summary}
    strict_6=(lookup[(6,'blanch')]['unique']>max(lookup[(6,'entropy')]['unique'],lookup[(6,'gini')]['unique']))
    return dict(experiment='FIELD-008',schema=SCHEMA,corpus_sha256=ATLAS_SHA256,
                protocol='experiments/field008/PREREGISTRATION.md',
                summary=summary,primary_strict_beats_classical_6=strict_6,
                seven_vertex_transfer_strict_beats_classical=(lookup[(7,'blanch')]['unique']>
                     max(lookup[(7,'entropy')]['unique'],lookup[(7,'gini')]['unique'])),
                proof_digest=sha([{k:v for k,v in row.items() if k not in ('proof_steps','packet_sha256')} for row in rows]),
                warnings=['all Atlas candidate model structures available; target is simulated source-owned index',
                          'one Atlas corpus provenance origin, not independent witness corroboration',
                          'all source queries same nominal unit cost; computation unequal',
                          'multi-hop conditional expansion is authored classical search, not original mathematics',
                          'classical exhaustive baselines see the same entire probe menu',
                          'research HOLD; no deployment or real-world action'])


if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
