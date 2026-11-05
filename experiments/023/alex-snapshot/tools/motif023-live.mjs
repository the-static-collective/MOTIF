// ALEX-023: bounded public-only *live* GitHub research across new source collections.
// This is an ALEX source-owning discovery adapter, not the entire ALEX reading floor.
import {createHash} from 'node:crypto';

const ALLOWED=Object.freeze({
 'the-static-collective/MOTIF':['motif','reasoning','questions','method','uncertainty','logic'],
 'the-static-collective/ALEX.2':['alex','source','evidence','custody','witness','research','independent'],
 'the-static-collective/planZ':['planz','plan','classical','actions','priority','strategy'],
 'the-static-collective/GRAFT':['graft','capability','compose','compile','code','executable'],
 'the-static-collective/the-daily-slice':['madd','maxhinal','fiber','pressure','slice','creative']
});
const LIMITS=Object.freeze({max_repos:2,max_documents_per_repo:2,
 max_document_bytes:64000,max_hits:20,max_hits_per_doc:5,max_tree_items:6000,
 max_question_length:320});
const STOP=new Set('what which whose why how would could should can does that this there with about from were have been then them each sources source these those into only under over before after the and for are but have its any get use using'.split(' '));
const sha=x=>createHash('sha256').update(x).digest('hex');
const gitBlob=b=>createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
const words=s=>[...new Set(String(s).toLowerCase().split(/[^a-z0-9]+/).filter(x=>x.length>2&&!STOP.has(x)))];
const safeRepo=x=>typeof x==='string'&&Object.hasOwn(ALLOWED,x);
const allowPath=s=>typeof s==='string'&&s.length<180&&
 /^[a-zA-Z0-9][a-zA-Z0-9_./-]*\.md$/i.test(s)&&
 (s==='README.md'||s.startsWith('docs/')||
  s.startsWith('artifacts/maxhinal/')||s.startsWith('research/packets/'))&&
 !s.includes('..')&&!s.includes('//')&&!/(?:^|\/)(?:private|secrets|tokens|credentials)\b/i.test(s);
function validateQuestion(q){
 if(typeof q!=='string'||q.length<18||q.length>LIMITS.max_question_length||
   /[\r\n\x00-\x1f]/.test(q))throw Error('HOLD_INVALID_QUESTION');
 const terms=words(q);
 if(terms.length<2||terms.length>22)throw Error('HOLD_QUESTION_OUTSIDE_BUDGET');
 return {question:q.trim(),terms};
}
export function selectCollections(question,requested=null){
 const q=validateQuestion(question);
 if(requested!==null){
  if(!Array.isArray(requested)||!requested.length||
   requested.length>LIMITS.max_repos||
   new Set(requested).size!==requested.length||
   !requested.every(safeRepo))throw Error('HOLD_UNAUTHORIZED_SOURCE_COLLECTION');
  return {selection:'EXPLICIT_PUBLIC_ALLOWLIST',repositories:requested,
    selection_not_identity_authorization:true};
 }
 const ranking=Object.entries(ALLOWED).map(([repo,terms])=>({
  repo,score:terms.reduce((n,t)=>n+(q.terms.includes(t)?1:0),0)
 }));
 ranking.sort((a,b)=>b.score-a.score||a.repo.localeCompare(b.repo));
 const matches=ranking.filter(r=>r.score>0).slice(0,LIMITS.max_repos);
 return {selection:'AUTOROUTED_PREDECLARED_PUBLIC_CATALOG',
  repositories:matches.map(x=>x.repo),
  selection_not_identity_authorization:true};
}
function requiredJson(raw,url){
 if(!raw||!raw.ok)throw Error('HOLD_GITHUB_HTTP_'+(raw?.status??'UNKNOWN'));
 return raw.json();
}
function safeOrigin(url){
 const parsed=new URL(url);
 if(parsed.protocol!=='https:'||parsed.hostname!=='api.github.com')
  throw Error('HOLD_UNAUTHORIZED_HTTP_ORIGIN');
}
async function apiGet(url,transport,token){
 safeOrigin(url);
 const headers={'Accept':'application/vnd.github+json',
  'X-GitHub-Api-Version':'2022-11-28','User-Agent':'ALEX-MOTIF-023-research'};
 if(token)headers.Authorization='Bearer '+token;
 const response=await transport(url,{method:'GET',headers,redirect:'error'});
 return requiredJson(response,url);
}
async function readRepo(repo,terms,transport,token){
 const prefix='https://api.github.com/repos/'+repo;
 const meta=await apiGet(prefix,transport,token);
 // Verify public status even with a privileged token. Do NOT accept a
 // readable private resource just because a credential can retrieve it.
 if(meta.private!==false||meta.visibility!=='public'||
   meta.full_name!==repo||typeof meta.default_branch!=='string'||
   !/^[a-zA-Z0-9._/-]{1,70}$/.test(meta.default_branch))
   throw Error('HOLD_NOT_VERIFIED_PUBLIC_REPOSITORY');
 const branch=await apiGet(prefix+'/branches/'+encodeURIComponent(meta.default_branch),transport,token);
 const commit=branch?.commit?.sha;
 if(typeof commit!=='string'||!/^[a-f0-9]{40}$/.test(commit))
  throw Error('HOLD_UNPINNED_PUBLIC_BRANCH');
 const commitObject=await apiGet(prefix+'/git/commits/'+commit,transport,token);
 const treeSHA=commitObject?.tree?.sha;
 if(!/^[a-f0-9]{40}$/.test(treeSHA||''))
  throw Error('HOLD_NO_COMMIT_TREE');
 const tree=await apiGet(prefix+'/git/trees/'+treeSHA+'?recursive=1',transport,token);
 if(tree.truncated!==false||!Array.isArray(tree.tree)||
    tree.tree.length>LIMITS.max_tree_items)
  throw Error('HOLD_TRUNCATED_SOURCE_TREE');
 const files=tree.tree.filter(x=>x.type==='blob'&&allowPath(x.path)&&
  Number.isSafeInteger(x.size)&&x.size<=LIMITS.max_document_bytes &&
  /^[a-f0-9]{40}$/.test(x.sha));
 const scored=files.map(x=>{
  const normalized=words(x.path);
  const score=terms.reduce((n,w)=>n+(normalized.includes(w)?6:0),0)+
    (x.path==='README.md'?2:0)+
    (x.path.startsWith('artifacts/maxhinal/')&&terms.includes('maxhinal')?4:0);
  return {...x,score};
 });
 scored.sort((a,b)=>b.score-a.score||a.path.localeCompare(b.path));
 const selected=scored.slice(0,LIMITS.max_documents_per_repo);
 if(!selected.length)throw Error('HOLD_NO_ELIGIBLE_MARKDOWN');
 const docs=[];
 for(const s of selected){
  const blob=await apiGet(prefix+'/git/blobs/'+s.sha,transport,token);
  if(blob.encoding!=='base64'||typeof blob.content!=='string'||
    blob.size!==s.size||blob.size>LIMITS.max_document_bytes)
   throw Error('HOLD_INVALID_OR_OVERSIZE_BLOB');
  const bytes=Buffer.from(blob.content.replace(/\s/g,''),'base64');
  if(bytes.length!==s.size||gitBlob(bytes)!==s.sha)
   throw Error('HOLD_CHANGED_SOURCE_BLOB');
  let text;
  try{text=new TextDecoder('utf-8',{fatal:true}).decode(bytes)}
  catch{throw Error('HOLD_UNREADABLE_PUBLIC_TEXT')}
  docs.push({path:s.path,git_blob:s.sha,size:s.size,
   source_commit:commit,text});
 }
 return {repo,source_commit:commit,default_branch:meta.default_branch,
  tree_sha:treeSHA,documents:docs,
  eligible_count:files.length,tree_items:tree.tree.length,
  selection_truncated:files.length>selected.length,
  public_eligibility_verified:true};
}
export async function investigatePublic({question,collections=null},options={}){
 const q=validateQuestion(question),selection=selectCollections(question,collections);
 const transport=options.transport??globalThis.fetch;
 const token=options.token??null;
 if(typeof transport!=='function')throw Error('HOLD_NO_SOURCE_TRANSPORT');
 if(token!==null&&(typeof token!=='string'||token.length>1024))
  throw Error('HOLD_INVALID_READ_TOKEN');
 if(selection.repositories.length===0){
  return {schema:'alex.motif023.live-public-evidence/v0',
   status:'HOLD_NO_REGISTERED_PUBLIC_COLLECTION',
   question:q.question,selection,
   hits:[],sources:[],errors:[],
   query_terms:q.terms,remote_requests_attempted:0,
   evidence_admission:'NONE',independent_origins_authenticated:false,
   source_custody_authenticated:false,private_material_accessed:false,
   remote_writes:0,authority:'none'};
 }
 const sources=[],errors=[],hits=[];
 for(const repo of selection.repositories){
  try{
   const fetched=await readRepo(repo,q.terms,transport,token);
   sources.push({
    repository:fetched.repo,source_commit:fetched.source_commit,
    tree_sha:fetched.tree_sha,default_branch:fetched.default_branch,
    eligible_files:fetched.eligible_count,tree_items:fetched.tree_items,
    selection_truncated:fetched.selection_truncated,
    public_eligibility_verified:true,
    selected_documents:fetched.documents.map(x=>({
      path:x.path,git_blob:x.git_blob,size:x.size}))
   });
   for(const d of fetched.documents){
    const lines=d.text.split('\n');const matches=[];
    for(let i=0;i<lines.length;i++){
     // Avoid leaking strings that look like private contact details or secrets
     // into a public research receipt despite the host repo being public.
     if(/(?:[\w.+-]+@[\w.-]+\.[a-z]{2,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN PRIVATE KEY-----)/i.test(lines[i]))
      continue;
     const matched=q.terms.filter(t=>words(lines[i]).includes(t));
     if(matched.length)matches.push({line:i+1,matched});
    }
    matches.sort((a,b)=>b.matched.length-a.matched.length||a.line-b.line);
    for(const m of matches.slice(0,LIMITS.max_hits_per_doc)){
     const sourceLine=lines[m.line-1];
     hits.push({
       repository:repo,source_commit:d.source_commit,path:d.path,
       git_blob:d.git_blob,line:m.line,
       matched_terms:m.matched,lexical_score:m.matched.length,
       excerpt:sourceLine.slice(0,150),
       support:'SEARCH_LEAD_NOT_ADMITTED_SOURCE_EVIDENCE'
     });
    }
   }
  }catch(error){
   errors.push({repository:repo,reason:String(error?.message||error).slice(0,120),
    collection_status:'HOLD_SOURCE_UNAVAILABLE_OR_UNVERIFIED'});
  }
 }
 hits.sort((a,b)=>b.lexical_score-a.lexical_score||
   a.repository.localeCompare(b.repository)||
   a.path.localeCompare(b.path)||a.line-b.line);
 const retained=hits.slice(0,LIMITS.max_hits);
 const result={
  schema:'alex.motif023.live-public-evidence/v0',
  status:retained.length?'HELD_SOURCE_RESEARCH_PACKET':
   'HOLD_NO_MATCHING_VERIFIED_SOURCE',
  question:q.question,selection,query_terms:q.terms,
  hits:retained,sources,errors,
  exact_commit_pinning:true,
  fetched_from_live_github_api:true,
  searched_beyond_original_five_documents:true,
  source_coverage:'PARTIAL_BOUNDED_PUBLIC_ALLOWLIST',
  source_tree_selection_based_on_path_relevance:true,
  source_line_ranked_after_original_blob_verification:true,
  total_selected_source_documents:sources.reduce((n,s)=>n+s.selected_documents.length,0),
  no_match_is_not_evidence_of_absence:true,
  independent_origins_authenticated:false,
  source_custody_authenticated:false,
  private_material_accessed:false,
  evidence_admission:'NONE',remote_writes:0,
  authority:'none'
 };
 return {...result,receipt_sha256:sha(JSON.stringify(result))};
}
export function verifyPacket(p){
 if(!p||p.schema!=='alex.motif023.live-public-evidence/v0'||
  !['HELD_SOURCE_RESEARCH_PACKET','HOLD_NO_MATCHING_VERIFIED_SOURCE'].includes(p.status)||
  !Array.isArray(p.sources)||p.sources.length>LIMITS.max_repos||
  !Array.isArray(p.hits)||p.hits.length>LIMITS.max_hits||
  !Array.isArray(p.errors)||p.errors.length>LIMITS.max_repos||
  p.authority!=='none'||p.private_material_accessed!==false||
  p.evidence_admission!=='NONE'||p.remote_writes!==0||
  p.source_custody_authenticated!==false)
   throw Error('HOLD_INVALID_PUBLIC_RESEARCH_PACKET');
 const {receipt_sha256,...body}=p;
 if(sha(JSON.stringify(body))!==receipt_sha256)
  throw Error('HOLD_RESEARCH_RECEIPT_TAMPERED');
 const sources=new Map(p.sources.map(s=>[s.repository,s]));
 for(const h of p.hits){
  const s=sources.get(h.repository);
  if(!s||h.source_commit!==s.source_commit||
   !s.selected_documents.some(d=>d.path===h.path&&d.git_blob===h.git_blob)||
   !Number.isSafeInteger(h.line)||h.line<=0||
   h.support!=='SEARCH_LEAD_NOT_ADMITTED_SOURCE_EVIDENCE')
   throw Error('HOLD_UNSUPPORTED_SEARCH_HIT');
 }
 return true;
}
export const AVAILABLE_COLLECTIONS=Object.freeze(Object.keys(ALLOWED));
if(process.argv[1]&&process.argv[1].endsWith('/motif023-live.mjs')){
 const question=process.argv.slice(2).join(' ');
 investigatePublic({question},{token:process.env.GITHUB_TOKEN||null})
  .then(result=>process.stdout.write(JSON.stringify(result,null,2)+'\n'))
  .catch(e=>{process.stderr.write(String(e.message)+'\n');process.exitCode=2});
}
