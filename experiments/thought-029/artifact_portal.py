"""MOTIF-029 read-only, paginated, evidence-labeled artifact/graph portal.

All source text is untrusted *data*. Only files within the operator-chosen
MOTIF checkout's reviewed public source roots are catalogued. No filesystem
escapes, secrets, provider access, source mutation, network requests, arbitrary
model-controlled commands or authority transfer. All known file kinds are
inspectable as data, including graph snapshots, ASTs, proofs and ledgers.

The portal indexes an arbitrary number of artifacts and graph nodes; pagination
caps a *response*, not the size of the underlying graph.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from copy import deepcopy

OPAQUE={'.png','.jpeg','.jpg','.webp','.gif','.pdf','.zip','.ipynb','.parquet','.sqlite','.db'}
READABLE={'.json','.jsonl','.md','.txt','.py','.yml','.yaml','.diff','.dot','.graphml','.xml','.svg','.csv','.toml'}
ROOTS={'experiments','docs','README.md','.github/workflows'}
DENY=re.compile(r'(^|[./_-])(secret|password|credential|private[_-]?key|token[_-]?vault|\.env)([./_-]|$)',re.I)
MAX_BYTES=12_000_000
MAX_PAGE=30
SOURCE_LABEL='REPOSITORY_CONTENT_NOT_INDEPENDENT_TRUTH'

class PortalError(ValueError):pass

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def compact(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
def pointer(path):return '/'+str(path).replace('~','~0').replace('/','~1')
def unescape(path):return path.replace('~1','/').replace('~0','~')

def classify(path:str,data=None):
    name=path.lower()
    if 'proof' in name or 'verified-fragment' in name:return 'proof_or_evidence'
    if 'cartridge' in name:return 'reasoning_cartridge'
    if 'geometry' in name or 'thought-space' in name:return 'geometry_or_thought_space'
    if 'experiment-results' in name or 'offline-results' in name or 'benchmark' in name:return 'evaluation_receipt'
    if 'graph' in name or 'cartograph' in name:return 'graph_or_symbolic_structure'
    if name.endswith(('.yml','.yaml')):return 'workflow'
    if name.endswith(('.py','.diff')):return 'source_code_as_data'
    if name.endswith('.md'):return 'research_document'
    if isinstance(data,dict) and ('nodes' in data and 'edges' in data or 'sources' in data and 'links' in data):return 'graph_or_symbolic_structure'
    return 'structured_data' if name.endswith(('.json','.jsonl','.csv','.toml')) else 'textual_artifact'

def _pairs(obj,location='',depth=0):
    """Locate native graph packets, field relations, and semantic ASTs lazily.

    The file is parsed once but graph discovery itself walks only structurally
    meaningful JSON containers. Locations are exact JSON pointers.
    """
    if depth>35:return
    if type(obj) is dict:
        node_keys=(('nodes','edges'),('nodes','links'),('nodes','hyperedges'),('entities','hyperedges'),('manifestations','relations'),('sources','links'),('vertices','edges'))
        for nodes,edges in node_keys:
            if isinstance(obj.get(nodes),list) and isinstance(obj.get(edges),list):
                yield {'pointer':location or '', 'kind':'typed_graph', 'node_key':nodes,'edge_key':edges,
                       'node_count':len(obj[nodes]),'edge_count':len(obj[edges])}
                break
        if set(obj)=={'ref'} and type(obj['ref']) is str:
            yield {'pointer':location or '', 'kind':'symbolic_AST','node_count':1,'edge_count':0}
        elif set(obj)=={'op','args'} and type(obj['op']) is str and isinstance(obj['args'],list):
            yield {'pointer':location or '', 'kind':'symbolic_AST',
                   'node_count':_count_ast(obj),'edge_count':max(0,_count_ast(obj)-1)}
        # Do not index every nested AST child again: parent is sufficient,
        # but independent ASTs in a result collection remain discoverable.
        for k,v in obj.items():
            if isinstance(v,(dict,list)) and not (k=='args' and 'op' in obj):
                yield from _pairs(v,location+pointer(k),depth+1)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):
            if isinstance(v,(dict,list)):
                yield from _pairs(v,location+pointer(i),depth+1)

def _count_ast(obj):
    if type(obj) is not dict or 'op' not in obj:return 1
    if not isinstance(obj.get('args'),list):return 1
    return 1+sum(_count_ast(v) for v in obj['args'])

def locate(obj,path):
    if path in ('',None):return obj
    if type(path) is not str or not path.startswith('/') or len(path)>1024:
        raise PortalError('invalid JSON pointer')
    cur=obj
    for section in path[1:].split('/'):
        k=unescape(section)
        if type(cur) is dict:
            if k not in cur:raise PortalError('unknown JSON field')
            cur=cur[k]
        elif isinstance(cur,list):
            if not k.isdigit() or (len(k)>1 and k[0]=='0') or int(k)>=len(cur):
                raise PortalError('out-of-range JSON index')
            cur=cur[int(k)]
        else:raise PortalError('cannot traverse scalar')
    return cur

class ArtifactPortal:
    """Single-repository, read-only artifactual awareness, with typed graph queries.

    External project-specific adapters MAY supply explicitly approved local
    snapshots in a different checkout; this instance does not auto-cross repos.
    """
    def __init__(self,repo:Path):
        root=Path(repo).resolve()
        if not root.is_dir():raise PortalError('approved source directory missing')
        self.root=root;self._items={};self._graphs={};self._index()

    def _eligible(self,p):
        if p.is_symlink() or not p.is_file() or p.suffix.lower() not in (READABLE|OPAQUE):return False
        try:r=p.relative_to(self.root).as_posix()
        except ValueError:return False
        if DENY.search(r):return False
        if not (r=='README.md' or r.startswith('experiments/') or r.startswith('docs/') or r.startswith('.github/workflows/')):return False
        if '__pycache__' in p.parts or '/.git/' in r:return False
        if p.stat().st_size>MAX_BYTES and p.suffix.lower() not in OPAQUE:return False
        return True

    def _index(self):
        for p in sorted(self.root.rglob('*')):
            if not self._eligible(p):continue
            name=p.relative_to(self.root).as_posix()
            if p.suffix.lower() in OPAQUE:
                meta={'id':name,'kind':'OPAQUE_MEDIA_METADATA_ONLY','sha256':None,
                      'bytes':p.stat().st_size,'format':p.suffix.lower(),
                      'access':'BINARY_PIXELS_OR_BYTES_NOT_EXPOSED_TO_TEXT_ONLY_LLM',
                      'truth_status':SOURCE_LABEL}
                self._items[name]=(meta,None,None)
                continue
            bytes_=p.read_bytes()
            try:content=bytes_.decode('utf-8')
            except UnicodeDecodeError:continue
            item={'id':name,'kind':classify(name),'sha256':sha(bytes_),
                  'bytes':len(bytes_), 'format':p.suffix.lower(),
                  'access':'READ_ONLY_REVIEWED_REPOSITORY_SCOPE', 'truth_status':SOURCE_LABEL}
            parsed=None
            if p.suffix.lower()=='.json':
                try:parsed=json.loads(content)
                except ValueError:item['parse_error']='INVALID_JSON';parsed=None
            elif p.suffix.lower()=='.jsonl':
                try:parsed=[json.loads(line) for line in content.splitlines() if line.strip()]
                except ValueError:item['parse_error']='INVALID_JSONL';parsed=None
            self._items[name]=(item,content,parsed)
            if parsed is not None:
                for g in _pairs(parsed):
                    gid=name+'#'+g['pointer']
                    self._graphs[gid]={'id':gid,'artifact_id':name,**g,'truth_status':SOURCE_LABEL}
        self._derive_proof_lineage_graph()

    def _derive_proof_lineage_graph(self):
        '''Turn claimed proof ancestry into an explicitly *unverified* graph.'''
        nodes={};edges=[]
        def visit(value,source,location='',depth=0):
            if depth>35:return
            if type(value) is dict:
                child=value.get('proof_digest')
                if type(child) is str and re.fullmatch('[a-fA-F0-9]{64}',child):
                    nodes[child]={'id':child,'label':'declared proof '+child[:12],
                                  'kind':'CLAIMED_PROOF','origin_artifact':source,
                                  'pointer':location,'claim_not_authentication':True}
                    for parent in value.get('parent_proof_digests',[]):
                        if type(parent) is not str or not re.fullmatch('[a-fA-F0-9]{64}',parent):continue
                        nodes.setdefault(parent,{'id':parent,'label':'referenced proof '+parent[:12],
                                        'kind':'PARENT_PROOF_REFERENCE_NOT_VERIFIED'})
                        edges.append({'source':child,'target':parent,
                                     'relation':'CLAIMED_PARENT_PROOF', 'origin':source,
                                     'status':'DECLARED_UNVERIFIED_LINEAGE', 'observed':False})
                for k,v in value.items():
                    if isinstance(v,(dict,list)):visit(v,source,location+pointer(k),depth+1)
            elif type(value) is list:
                for i,v in enumerate(value):
                    if isinstance(v,(dict,list)):visit(v,source,location+pointer(i),depth+1)
        for meta,_,obj in list(self._items.values()):
            if obj is not None:visit(obj,meta['id'])
        if not nodes:return
        rel={'nodes':[nodes[k] for k in sorted(nodes)],
             'edges':sorted(edges,key=lambda e:(e['source'],e['target'],e['origin'])),
             'status':'DECLARED_LINEAGE_ONLY_NOT_PROOF',
             'derivation':'SOURCE_OWNED_INDEX_FROM_REPOSITORY_JSON'}
        content=compact(rel);id_='derived/claimed-proof-lineage.json'
        meta={'id':id_,'kind':'derived_claimed_proof_graph','sha256':sha(content.encode()),
              'bytes':len(content),'format':'.json',
              'access':'READ_ONLY_DERIVED_VIEW',
              'truth_status':'UNVERIFIED_DIGEST_LINEAGE_NOT_MATHEMATICAL_PROOF'}
        self._items[id_]=(meta,content,rel)
        self._graphs[id_+'#']={'id':id_+'#','artifact_id':id_,'pointer':'',
              'kind':'typed_graph','node_key':'nodes','edge_key':'edges',
              'node_count':len(rel['nodes']),'edge_count':len(rel['edges']),
              'truth_status':meta['truth_status']}

    def _page(self,items,cursor=0,limit=10):
        if type(cursor) is not int or cursor<0 or type(limit) is not int or not 1<=limit<=MAX_PAGE:
            raise PortalError('invalid pagination')
        n=len(items)
        return {'total':n,'offset':cursor,'items':deepcopy(items[cursor:cursor+limit]),
                'next_cursor':cursor+limit if cursor+limit<n else None,
                'response_only_paginated':True}

    def overview(self):
        counts={}
        for meta,_,_ in self._items.values():counts[meta['kind']]=counts.get(meta['kind'],0)+1
        graph_kinds={}
        for g in self._graphs.values():graph_kinds[g['kind']]=graph_kinds.get(g['kind'],0)+1
        exemplars=[]
        for kind in sorted(counts):
            ids=[m['id'] for m,_,_ in self._items.values() if m['kind']==kind]
            exemplars.extend(ids[:2])
        return {'artifacts':len(self._items),'graphs':len(self._graphs),
                'kinds':counts,'graph_kinds':graph_kinds,
                'example_artifact_ids':exemplars[:25],
                'example_graph_ids':list(self._graphs)[:5],
                'read_only_tools':['catalog','search','graphs','read','neighbors'],
                'pagination':'Every result page has next_cursor; no global arbitrary graph-count cap',
                'provenance':'Untrusted public source and expressly provided runtime snapshots',
                'not_available_without_adapter':'Disconnected external repositories, private apps, unmounted files and raw binary image/PDF perception',
                'not_owner_authentication':True}

    def catalog(self,kind=None,cursor=0,limit=10):
        if kind is not None and (type(kind) is not str or len(kind)>100):raise PortalError('invalid filter')
        a=[m for m,_,_ in self._items.values() if kind is None or kind==m['kind']]
        o=self._page(a,cursor,limit)
        o.update({'artifact_count':len(self._items),'graph_count':len(self._graphs),
                  'source_scope':str(self.root),'enumerates_full_source_collection':True})
        return o

    def search(self,term,cursor=0,limit=10,kind=None):
        if type(term) is not str or not 2<=len(term)<=100 or any(ord(x)<32 for x in term):
            raise PortalError('invalid bounded search')
        t=term.casefold();hits=[]
        for meta,content,_ in self._items.values():
            if kind and meta['kind']!=kind:continue
            m=re.search(re.escape(t),content or '',re.I)
            if t in meta['id'].casefold() or m:
                snippet=content[max(0,m.start()-90):m.start()+150] if m else ''
                hits.append({'id':meta['id'],'kind':meta['kind'],'excerpt':snippet,
                             'sha256':meta['sha256'],'truth_status':SOURCE_LABEL})
        return self._page(hits,cursor,limit)

    def read(self,artifact_id,pointer_path='',cursor=0,limit=10):
        if artifact_id not in self._items:raise PortalError('artifact not indexed/allowed')
        meta,content,parsed=self._items[artifact_id]
        if content is None:
            if pointer_path:raise PortalError('opaque media has no JSON pointer')
            return {'artifact':deepcopy(meta),'pointer':'','content_kind':'opaque_media_metadata_only',
                    'total':0,'offset':0,'items':[],'next_cursor':None,
                    'notice':'Binary file indexed; a text-only Ollama model cannot inspect pixels or binary payload. Use explicit authorized multimodal adapter.'}
        if pointer_path and parsed is None:raise PortalError('JSON pointer requires parsed document')
        if parsed is None:
            # Text units = lines, so source code is viewable only as data.
            value=content.splitlines();category='text_lines'
        else:
            value=locate(parsed,pointer_path);category='json'
        if isinstance(value,dict):
            parts=[{'key':k,'value':self._preview(v)} for k,v in sorted(value.items())]
            page=self._page(parts,cursor,limit)
        elif isinstance(value,list):
            page=self._page([{'index':i,'value':self._preview(v)} for i,v in enumerate(value)],cursor,limit)
        else:
            page={'total':1,'offset':0,'items':[self._preview(value)],'next_cursor':None}
        return {'artifact':deepcopy(meta),'pointer':pointer_path,'content_kind':category,**page,
                'model_access_is_read_only':True}

    @staticmethod
    def _preview(v):
        if type(v) is dict:
            short={k:copy for k,copy in list(v.items())[:12] if type(copy) in (str,int,float,bool,type(None))}
            return {'shape':'object','fields':list(v)[:25], 'shallow':short}
        if isinstance(v,list):return {'shape':'array','length':len(v)}
        if isinstance(v,str):return v[:900] + ('…' if len(v)>900 else '')
        return deepcopy(v)

    def graphs(self,cursor=0,limit=10):return self._page(list(self._graphs.values()),cursor,limit)

    def neighbors(self,graph_id,node_id,cursor=0,limit=10):
        if graph_id not in self._graphs:raise PortalError('unknown graph id')
        if type(node_id) is not str or not node_id or len(node_id)>180:raise PortalError('invalid node identifier')
        g=self._graphs[graph_id];o=self._items[g['artifact_id']][2]
        graph=locate(o,g['pointer'])
        if g['kind']=='symbolic_AST':
            nodes,edges=[],[]
            def visit(value,path=''):
                ident=path or '/';label=value.get('op',value.get('ref','unknown')) if isinstance(value,dict) else 'scalar'
                nodes.append({'id':ident,'label':label,'type':'AST_NODE'})
                for i,ch in enumerate(value.get('args',[])) if type(value) is dict else []:
                    nxt=path+'/args/'+str(i)
                    edges.append({'source':ident,'target':nxt,'relation':'ARGUMENT_'+str(i),'status':'SYNTAX_NOT_SEMANTIC_PROOF'})
                    visit(ch,nxt)
            visit(graph)
        else:
            nodes=graph[g['node_key']];edges=graph[g['edge_key']]
        eligible=[n for n in nodes if isinstance(n,dict) and str(n.get('id',n.get('name',n.get('concept_id'))))==node_id]
        joined=[]
        for e in edges:
            if not isinstance(e,dict):continue
            start=e.get('source',e.get('from'))
            end=e.get('target',e.get('to'))
            # Hyperedges can be represented by participants/member IDs.
            members=e.get('members',e.get('participants',[]))
            present=node_id in (str(start),str(end)) or isinstance(members,list) and node_id in [str(x) for x in members]
            if present:joined.append(self._preview(e))
        if not eligible and not joined:raise PortalError('node absent from selected graph')
        page=self._page(joined,cursor,limit)
        return {'graph_id':graph_id,'anchor_id':node_id,'nodes':eligible[:1],**page,
                'edges_not_reclassified_as_facts':True,'geometry_is_not_evidence':True}


    def mount_runtime_snapshot(self,name,object_data,*,operator_approved=False):
        """Explicit source-owner bridge for an in-memory graph or other artifact.

        Never model-callable. Supports graphs that have not been serialized to
        source files; no disk writes or delegated permissions. Every snapshot
        is source-provided and remains epistemically unverified.
        """
        if operator_approved is not True:raise PortalError('runtime ingestion requires source owner approval')
        if type(name) is not str or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',name):
            raise PortalError('invalid runtime snapshot name')
        text=compact(object_data)
        if len(text.encode())>MAX_BYTES:raise PortalError('snapshot exceeds operator per-artifact budget')
        id_='runtime/'+name+'.json'
        meta={'id':id_,'kind':'source_owner_supplied_runtime_snapshot',
              'sha256':sha(text.encode()),'bytes':len(text.encode()),'format':'.json',
              'access':'EXPLICIT_SOURCE_OWNER_SNAPSHOT_READ_ONLY',
              'truth_status':'RUNTIME_SOURCE_DECLARED_NOT_INDEPENDENTLY_VERIFIED'}
        self._items[id_]=(meta,text,deepcopy(object_data))
        self._graphs={k:v for k,v in self._graphs.items() if v['artifact_id']!=id_}
        for graph in _pairs(object_data):
            gid=id_+'#'+graph['pointer']
            self._graphs[gid]={'id':gid,'artifact_id':id_,**graph,
                                'truth_status':meta['truth_status']}
        return deepcopy(meta)

    def query(self,request):
        if type(request) is not dict or set(request)-{'tool','artifact_id','pointer','term','kind','graph_id','node_id','cursor','limit'}:
            raise PortalError('unrecognized portal request fields')
        tool=request.get('tool');cursor=request.get('cursor',0);limit=request.get('limit',10)
        if tool=='catalog':return self.catalog(request.get('kind'),cursor,limit)
        if tool=='search':return self.search(request.get('term'),cursor,limit,request.get('kind'))
        if tool=='read':return self.read(request.get('artifact_id'),request.get('pointer',''),cursor,limit)
        if tool=='graphs':return self.graphs(cursor,limit)
        if tool=='neighbors':return self.neighbors(request.get('graph_id'),request.get('node_id'),cursor,limit)
        raise PortalError('unknown read-only portal capability')
