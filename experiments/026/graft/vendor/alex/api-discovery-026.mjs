// ALEX-026: discovery OF potential public API providers by original source.
// Search public GitHub for OpenAPI descriptions, verify immutable Git blobs,
// extract *candidate* GET operations. Never contact any advertised API host.
import {createHash} from 'node:crypto';
import {discoverProviders} from './eagle-eye-providers-025.mjs';
const sha=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const blobHash=b=>createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
const DOMAIN=Object.freeze({
 weather:['weather','forecast','meteorology','temperature','precipitation'],
 air_quality:['pollution','air quality','aqi','particulate','airquality'],
 transit:['transit','transport','bus','train','realtime','schedule'],
 environment:['earthquake','seismic','river','water','flood','environmental'],
 maps:['geospatial','geolocation','coordinates','mapping','satellite'],
 finance:['exchange rate','financial','currency','forex','economic']
});
const BASE='https://api.github.com';
const LIMIT=Object.freeze({question:320,searchResults:8,inspectRepos:3,
 treeItems:4000,bytes:36000,filesPerRepo:2,requests:18,timeout:6500});
const sanitize=s=>String(s||'').slice(0,140).replace(/[\x00-\x1f]/g,'');
const pathAllowed=p=>typeof p==='string'&&p.length<=180&&
 /^[\w./-]+$/.test(p)&&!p.includes('..')&&
 !/(?:^|\/)(?:secrets?|private|node_modules|\.git)(?:\/|$)/i.test(p)&&
 /(?:^|\/)(?:openapi|swagger|api-spec|specification)[\w.-]*\.(?:json|yaml|yml)$/i.test(p);
const networkCandidates=s=>{
 if(typeof s!=='string'||s.length>180)return false;
 try{
  const u=new URL(s);
  return u.protocol==='https:'&&!u.username&&!u.password&&!u.port&&
   !(/^(localhost|127\.|10\.|192\.168\.|169\.254\.|0\.|172\.(1[6-9]|2\d|3[01])\.|[0-9.]+$)/.test(u.hostname))&&
   !u.hostname.endsWith('.local')&&!u.hostname.endsWith('.internal')&&!u.hostname.includes('..');
 }catch{return false}
};
export function identifyGap(question){
 if(typeof question!=='string'||question.trim().length<12||
  question.length>LIMIT.question||/[\x00-\x1f]/.test(question))
  throw Error('HOLD_INVALID_DISCOVERY_QUESTION');
 const q=question.trim().toLowerCase();
 const matched=Object.entries(DOMAIN).map(([k,terms])=>({
  domain:k,hits:terms.filter(t=>q.includes(t))
 })).filter(x=>x.hits.length);
 const ranked=matched.sort((a,b)=>b.hits.length-a.hits.length||a.domain.localeCompare(b.domain));
 const suggested=discoverProviders(question);
 const domain=ranked[0]?.domain??null;
 return {
  schema:'alex026.provider-gap/v0',question:question.trim(),
  identified_domain:domain,
  status:domain?'NEEDS_SPECIALIZED_SOURCE':'HOLD_UNRECOGNIZED_DOMAIN',
  baseline_seven_provider_recommendations:suggested.recommended,
  why:domain?'A domain-specific live data interface is not provided by the seven existing public metadata adapters.':
   'The query does not match a predeclared specialized source family.',
  scientific_or_article_index_not_equivalent_to_live_data:true,
  autonomy:'PROPOSE_DISCOVERY_NOT_USE_PROVIDER',
  approval_to_contact_candidate_host:false
 };
}
async function github(url,transport,token,state){
 const u=new URL(url);
 if(u.origin!==BASE)throw Error('HOLD_GITHUB_HOST_BOUNDARY');
 if(++state.requests>LIMIT.requests)throw Error('HOLD_PROVIDER_DISCOVERY_CALL_BUDGET');
 const headers={'Accept':'application/vnd.github+json',
  'X-GitHub-Api-Version':'2022-11-28',
  'User-Agent':'ALEX-026-public-openapi-discovery'};
 if(token)headers.Authorization='Bearer '+token;
 const r=await transport(u.href,{method:'GET',redirect:'error',headers,
  signal:AbortSignal.timeout(LIMIT.timeout)});
 if(!r?.ok||r.redirected)throw Error('HOLD_GITHUB_DISCOVERY_HTTP_'+(r?.status??'UNKNOWN'));
 return r.json();
}
function selectedOperation(raw,name,repo,shaCommit,p,blobSha){
 if(typeof raw!=='object'||raw===null||Array.isArray(raw)||
  typeof raw.openapi!=='string'||!/^3\.[0-9.]+$/.test(raw.openapi)||
  typeof raw.info?.title!=='string'||typeof raw.paths!=='object'||raw.paths===null)
  throw Error('HOLD_NOT_VALID_OPENAPI3_JSON');
 const entries=Object.entries(raw.paths)
  .filter(([p,v])=>typeof p==='string'&&p.startsWith('/')&&p.length<=100&&
    /^[\w{}./-]+$/.test(p)&&v&&typeof v==='object'&&v.get&&typeof v.get==='object')
  .slice(0,20);
 const first=entries[0];
 if(!first)throw Error('HOLD_NO_DECLARED_GET_OPERATION');
 const [opPath,op]=first;
 const servers=(raw.servers||[]).filter(x=>typeof x?.url==='string'&&networkCandidates(x.url))
  .slice(0,3).map(x=>x.url);
 const hasSecurity=!!(op.security?.length||raw.security?.length);
 return {
  schema:'alex026.source-attested-api-proposal/v0',
  provider_name:sanitize(raw.info.title),
  repository:name,source_commit:shaCommit,
  spec_path:p,git_blob:blobSha,
  operation:{method:'GET',path:opPath,
   summary:sanitize(op.summary||op.description||'Unreviewed GET operation'),
   declared_parameters:Array.isArray(op.parameters)?op.parameters.length:0},
  declared_servers:servers,
  authentication_declared:hasSecurity,
  operation_selected_by:'FIRST_SAFE_PATH_WITH_GET_NOT_SEMANTIC_PROOF',
  spec_format:'OPENAPI3_JSON_GIT_BLOB_VERIFIED',
  source_license_verified:false,
  service_endpoint_tested:false,
  service_claims_independently_verified:false,
  candidate_host_contact_authorized:false,
  production_permissions:'NONE'
 };
}
export function inspectSpec(bytes,meta){
 if(!Buffer.isBuffer(bytes)||bytes.length>LIMIT.bytes||bytes.length===0)
  throw Error('HOLD_SPEC_BYTES_BUDGET');
 if(blobHash(bytes)!==meta.git_blob)throw Error('HOLD_SPEC_GIT_BLOB_CHANGED');
 let raw;
 try{raw=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes))}
 catch{throw Error('HOLD_SPEC_NOT_PARSEABLE_JSON');}
 return selectedOperation(raw,meta.repo,meta.repo,meta.commit,meta.path,meta.git_blob);
}
export async function discoverMissingProvider({question,approvedPublicGithubSearch=false},options={}){
 const gap=identifyGap(question);
 if(!approvedPublicGithubSearch)return{
  schema:'alex026.api-discovery/v0',
  status:'HOLD_PUBLIC_DISCOVERY_NOT_APPROVED',gap,
  origin_searches_executed:0,public_provider_proposals:[],
  unreviewed_spec_documents:[],errors:[],
  no_candidate_endpoint_contact:true,authority:'none'
 };
 if(gap.status!=='NEEDS_SPECIALIZED_SOURCE')return{
  schema:'alex026.api-discovery/v0',
  status:'HOLD_UNRECOGNIZED_DOMAIN',gap,
  origin_searches_executed:0,public_provider_proposals:[],
  unreviewed_spec_documents:[],errors:[],
  no_candidate_endpoint_contact:true,authority:'none'
 };
 const transport=options.transport??globalThis.fetch,token=options.githubToken??null;
 if(typeof transport!=='function'||(token!==null&&typeof token!=='string'))
  throw Error('HOLD_NO_APPROVED_PUBLIC_TRANSPORT');
 const state={requests:0},proposals=[],sources=[],errors=[];
 const term=gap.identified_domain==='air_quality'?'air quality':
  gap.identified_domain==='environment'?'environment':
  gap.identified_domain==='maps'?'geospatial':
  gap.identified_domain==='finance'?'exchange rates':gap.identified_domain;
 const query=term+' openapi in:name,description,readme';
 let catalog;
 try{
  const u=BASE+'/search/repositories?q='+encodeURIComponent(query)+
   '&per_page='+LIMIT.searchResults;
  catalog=await github(u,transport,token,state);
 }catch(e){
  const body={
   schema:'alex026.api-discovery/v0',
   status:'HOLD_SOURCE_CATALOG_UNAVAILABLE',gap,
   query_sent_to:'api.github.com',search_query:query,
   origin_searches_executed:state.requests,
   public_provider_proposals:[],unreviewed_spec_documents:[],
   errors:[sanitize(e.message)],no_candidate_endpoint_contact:true,
   authority:'none',search_results_incomplete:true
  };
  return {...body,checksum_sha256:sha(body)};
 }
 if(!Array.isArray(catalog.items))throw Error('HOLD_PUBLIC_GITHUB_CATALOG_SHAPE');
 const eligible=catalog.items.filter(x=>x?.private===false&&x.visibility==='public'&&
  /^[\w.-]+\/[\w.-]+$/.test(x.full_name||'')&&
  /^[a-zA-Z0-9./_-]{1,70}$/.test(x.default_branch||'')).slice(0,LIMIT.inspectRepos);
 for(const record of eligible){
  const repo=record.full_name,root=BASE+'/repos/'+repo;
  try{
   // Visibility is verified again at the exact repository before reading files.
   const meta=await github(root,transport,token,state);
   if(meta.private!==false||meta.visibility!=='public'||meta.full_name!==repo)
    throw Error('HOLD_NOT_VERIFIED_PUBLIC_REPO');
   const head=await github(root+'/branches/'+encodeURIComponent(meta.default_branch),transport,token,state);
   const commit=head?.commit?.sha;
   if(!/^[a-f0-9]{40}$/.test(commit||''))throw Error('HOLD_UNPINNED_REPO_COMMIT');
   const co=await github(root+'/git/commits/'+commit,transport,token,state);
   const treeSHA=co?.tree?.sha;
   if(!/^[a-f0-9]{40}$/.test(treeSHA||''))throw Error('HOLD_UNPINNED_REPO_TREE');
   const tree=await github(root+'/git/trees/'+treeSHA+'?recursive=1',transport,token,state);
   if(tree.truncated!==false||!Array.isArray(tree.tree)||tree.tree.length>LIMIT.treeItems)
    throw Error('HOLD_INCOMPLETE_SPEC_SOURCE_TREE');
   const files=tree.tree.filter(x=>x.type==='blob'&&pathAllowed(x.path)&&
    Number.isSafeInteger(x.size)&&x.size<=LIMIT.bytes&&x.size>0&&
    /^[a-f0-9]{40}$/.test(x.sha))
    .sort((a,b)=>a.path.length-b.path.length||a.path.localeCompare(b.path))
    .slice(0,LIMIT.filesPerRepo);
   for(const file of files){
    try{
     const b=await github(root+'/git/blobs/'+file.sha,transport,token,state);
     if(b.encoding!=='base64'||typeof b.content!=='string'||b.size!==file.size)
      throw Error('HOLD_INVALID_SOURCE_BLOB');
     const bytes=Buffer.from(b.content.replace(/\s/g,''),'base64');
     if(bytes.length!==file.size||blobHash(bytes)!==file.sha)
      throw Error('HOLD_INTACT_SOURCE_REQUIRED');
     sources.push({repository:repo,source_commit:commit,path:file.path,
      git_blob:file.sha,size:file.size,format:file.path.endsWith('.json')?'json':'yaml',
      complete_original_blob_verified:true});
     if(!file.path.endsWith('.json'))continue; // YAML is recorded, not falsely parsed.
     const p=inspectSpec(bytes,{repo,commit,path:file.path,git_blob:file.sha});
     proposals.push(p);
    }catch(e){errors.push({repository:repo,path:file.path,error:sanitize(e.message)})}
   }
  }catch(e){errors.push({repository:repo,error:sanitize(e.message)})}
 }
 const body={
  schema:'alex026.api-discovery/v0',
  status:proposals.length?'PROPOSED_NEW_PUBLIC_SOURCE_ADAPTER':
   'HOLD_NO_REVIEWABLE_OPENAPI_SPEC',
  gap,query_sent_to:'api.github.com',search_query:query,
  origin_searches_executed:state.requests,
  candidate_repositories_screened:eligible.length,
  public_provider_proposals:proposals.slice(0,4),
  unreviewed_spec_documents:sources,
  errors,
  search_results_incomplete:true,
  yaml_sources_not_parsed_as_json:true,
  spec_blob_identity_not_service_authenticity:true,
  no_candidate_endpoint_contact:true,
  candidate_requires_source_owner_review:true,
  automatically_installed_capabilities:0,
  authority:'none'
 };
 return {...body,checksum_sha256:sha(body)};
}
export function verifyDiscovery(packet){
 if(!packet||packet.schema!=='alex026.api-discovery/v0'||
  packet.authority!=='none'||packet.no_candidate_endpoint_contact!==true||
  !Array.isArray(packet.public_provider_proposals)||
  packet.public_provider_proposals.length>4||
  !Array.isArray(packet.unreviewed_spec_documents)||
  packet.unreviewed_spec_documents.length>6)
  throw Error('HOLD_INVALID_PROVIDER_DISCOVERY');
 if(packet.status==='HOLD_PUBLIC_DISCOVERY_NOT_APPROVED'||
   packet.status==='HOLD_UNRECOGNIZED_DOMAIN')return true;
 const {checksum_sha256,...body}=packet;
 if(checksum_sha256!==sha(body))throw Error('HOLD_PROVIDER_DISCOVERY_TAMPERED');
 const refs=new Set(packet.unreviewed_spec_documents.map(x=>x.repository+'@'+x.source_commit+'#'+x.git_blob));
 for(const p of packet.public_provider_proposals){
  if(!refs.has(p.repository+'@'+p.source_commit+'#'+p.git_blob)||
   p.operation?.method!=='GET'||p.production_permissions!=='NONE'||
   p.candidate_host_contact_authorized!==false)
   throw Error('HOLD_UNSUPPORTED_API_SOURCE_CUSTODY');
 }
 return true;
}
export const DISCOVERY_LIMITS=LIMIT;
