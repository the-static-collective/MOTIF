"""MOTIF-032: review-only, explicitly inspectable shared concept codebook.

This is a typed *compression/translation interface*, not an invented executable
language. The source-owned semantics of every permissible operation are fixed.
"""
from __future__ import annotations
import copy, hashlib, json, re
from pathlib import Path

SCHEMA='motif.thought032.concept-word.v1'
RELATIONS=('DIFFERENCE','INTERSECTION','UNION','SECOND','COMPLEMENT','SYMMETRIC_DIFFERENCE')
GRAPH_PATTERNS=('NONE','DEPENDENCY_CHAIN','TENSION_EDGE','ASSOCIATION_BRIDGE')
GATES=('DEV_THEN_FROZEN_64',)
UNCERTAINTY=('TRANSFER_REQUIRES_NEW_EVIDENCE',)
EXPERIMENTS=('DISCRIMINATING_DEV_QUERIES',)
WORD_RE=re.compile(r'[A-Za-z][A-Za-z0-9_-]{1,15}\Z')
RESERVED={'eval','exec','python','read','write','delete','shell','final','catalog','search','graphs','neighbors','source','proof'}

class ConceptError(ValueError):pass

def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
def digest(obj):return hashlib.sha256(canonical(obj).encode()).hexdigest()

def validate_definition(value):
    if type(value) is not dict or set(value)!={'word','gloss','relation','graph_pattern','proof_gate','uncertainty','next_experiment'}:
        raise ConceptError('exact explicit definition fields required')
    word=value['word']
    if type(word) is not str or not WORD_RE.fullmatch(word) or word.lower() in RESERVED:
        raise ConceptError('invalid, reserved or opaque word')
    gloss=value['gloss']
    if type(gloss) is not str or not 10<=len(gloss)<=240 or any(ord(c)<32 for c in gloss):
        raise ConceptError('word must have a short human-readable explanation')
    for field,allowed in (('relation',RELATIONS),('graph_pattern',GRAPH_PATTERNS),
                          ('proof_gate',GATES),('uncertainty',UNCERTAINTY),
                          ('next_experiment',EXPERIMENTS)):
        if type(value[field]) is not str or value[field] not in allowed:
            raise ConceptError('unknown typed concept component: '+field)
    return copy.deepcopy(value)

def semantic_signature(relation):
    if relation not in RELATIONS:raise ConceptError('unknown mathematical relation')
    values=[]
    for a in range(8):
        for b in range(8):
            values.append({
               'DIFFERENCE':lambda:a & (~b&7),
               'INTERSECTION':lambda:a&b,
               'UNION':lambda:a|b,
               'SECOND':lambda:b,
               'COMPLEMENT':lambda:(~a)&7,
               'SYMMETRIC_DIFFERENCE':lambda:a^b
            }[relation]())
    return tuple(values)

class ConceptBook:
    def __init__(self,*,enabled=True):
        self.enabled=enabled;self.records={};self.use_receipts=[];self.rejections=[]
    def admit(self,definition):
        if not self.enabled:raise ConceptError('concept vocabulary not enabled')
        if len(self.records)>=6:raise ConceptError('maximum six model-coined words per session')
        d=validate_definition(definition)
        if d['word'].lower() in {x.lower() for x in self.records}:raise ConceptError('duplicate word')
        card={'schema':SCHEMA,'definition':d,
              'semantic_signature_sha256':digest(semantic_signature(d['relation'])),
              'source_owned_operators_not_model_code':True,
              'independently_verified_for_new_task':False,
              'source_scope':'FINITE_3_BIT_BOOLEAN_MODEL_PLUS_TYPED_GRAPH_PATTERN',
              'model_word_meaning_real_world_proven':False,
              'installed':False,'authority':'NONE'}
        card['card_sha256']=digest(card)
        self.records[d['word']]=card
        return copy.deepcopy(card)
    def expand(self,word):
        if not self.enabled or type(word) is not str or word not in self.records:
            raise ConceptError('unrecognized model-coined word')
        card=self.records[word]
        if card['card_sha256']!=digest({k:v for k,v in card.items() if k!='card_sha256'}):
            raise ConceptError('card integrity failure')
        d=card['definition']
        if digest(semantic_signature(d['relation']))!=card['semantic_signature_sha256']:
            raise ConceptError('operator fingerprint contradiction')
        self.use_receipts.append({'word':word,'expansion_hash':card['card_sha256'],
            'meaning_status':'TYPED_CANDIDATE_NOT_TARGET_PROOF'})
        return copy.deepcopy(d)
    def view(self):
        return {'schema':'motif.thought032.codebook-view.v1','enabled':self.enabled,
            'terms':copy.deepcopy(list(self.records.values())),
            'coined':len(self.records),'uses':len(self.use_receipts),
            'used_words':sorted(set(x['word'] for x in self.use_receipts)),
            'installed':False}

def graph_match(pattern, graph):
    """Finite structural signature, no inference of real causality or truth.

    Inputs from the source-owned, explicitly declared graph snapshot only.
    Every candidate is a QUESTION, not a newly verified edge or claim.
    """
    if pattern not in GRAPH_PATTERNS:raise ConceptError('unlicensed graph pattern')
    if type(graph) is not dict or type(graph.get('nodes')) is not list or type(graph.get('edges')) is not list:
        raise ConceptError('typed graph snapshot required')
    nodes={n['id'] for n in graph['nodes'] if type(n) is dict and type(n.get('id')) is str}
    if len(nodes)>400 or len(graph['edges'])>1500:raise ConceptError('graph size bound')
    edges=[]
    for edge in graph['edges']:
        if type(edge) is not dict or not {'source','target','relation','origin','observed'}<=set(edge):
            raise ConceptError('edge must be sourced and typed')
        if edge['source'] not in nodes or edge['target'] not in nodes or type(edge['observed']) is not bool:
            raise ConceptError('invalid graph edge')
        if edge['observed'] and edge['relation'] in ('requires','contradicts','associated'):
            edges.append(edge)
    matched=[]
    if pattern=='DEPENDENCY_CHAIN':
        for a in edges:
            if a['relation']!='requires':continue
            for b in edges:
                if b['relation']=='requires' and a['target']==b['source'] and a['source']!=b['target']:
                    matched.append({'nodes':[a['source'],a['target'],b['target']], 'edge_origins':[a['origin'],b['origin']]})
    if pattern=='TENSION_EDGE':
        matched=[{'nodes':[x['source'],x['target']],'edge_origins':[x['origin']]} for x in edges if x['relation']=='contradicts']
    if pattern=='ASSOCIATION_BRIDGE':
        # Requires two different common neighbors and at least two stated origins.
        adj={n:{} for n in nodes}
        existing=set()
        for e in edges:
            if e['relation']!='associated':continue
            a,b=e['source'],e['target']
            existing.add(frozenset((a,b)))
            adj[a].setdefault(b,set()).add(e['origin']);adj[b].setdefault(a,set()).add(e['origin'])
        for a in sorted(nodes):
            for b in sorted(nodes):
                if a>=b or frozenset((a,b)) in existing:continue
                via=sorted(set(adj[a])&set(adj[b]))
                origins=set().union(*(adj[a][n]|adj[b][n] for n in via)) if via else set()
                if len(via)>=2 and len(origins)>=2:
                    matched.append({'nodes':[a,b], 'via':via,'edge_origins':sorted(origins)})
    return {'pattern':pattern,'matches':matched[:60], 'total_found':len(matched),
            'source_edges_used':len(edges),'status':'STRUCTURAL_CANDIDATES_NOT_NEW_EVIDENCE',
            'coordinates_as_evidence':False, 'authority':'NONE'}
