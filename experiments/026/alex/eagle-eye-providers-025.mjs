// ALEX-025 — Eagle Eye public provider discovery, query-aware routing and opt-in search.
// Provider choices are *proposals*. Only explicitly selected booleans permit egress.
// This is metadata discovery, not article/full-text reading or authenticated evidence.
import {createHash} from 'node:crypto';

const CATALOG=Object.freeze({
 github:{label:'Collective GitHub',group:'code',description:'Public Static Collective source files',host:'api.github.com',existing:true},
 wikipedia:{label:'Wikipedia',group:'general',description:'Public encyclopedia search index',host:'en.wikipedia.org',existing:true},
 scholarly:{label:'OpenAlex',group:'scholarly',description:'Scholarly bibliography and DOI leads',host:'api.openalex.org',existing:true},
 githubglobal:{label:'Global GitHub',group:'code',description:'Public repository search across GitHub',host:'api.github.com',existing:false},
 crossref:{label:'Crossref',group:'scholarly',description:'Publisher DOI and publication metadata',host:'api.crossref.org',existing:false},
 openlibrary:{label:'Open Library',group:'books',description:'Public book and author catalog',host:'openlibrary.org',existing:false},
 europepmc:{label:'Europe PMC',group:'biomed',description:'Biomedical paper and preprint metadata',host:'www.ebi.ac.uk',existing:false}
});
const TERMS={
 code:['code','repository','github','software','program','api','function','tool','javascript','python','open','source','build','debug','developer','compile','implementation','motif','jarvis','jar;vis','graft','planz'],
 scholarly:['paper','papers','study','studies','research','science','scientific','evidence','scholar','doi','journal','experiment','analysis','statistical','causal','independent','correlation'],
 general:['history','historical','person','meaning','concept','explain','overview','what','when','where','religion','philosophy'],
 books:['book','books','author','library','novel','reading','literature','text','edition','published','publishing','isbn'],
 biomed:['medical','medicine','disease','health','gene','cancer','clinical','biology','biomedical','patient','diagnosis','trial','pubmed','treatment']
};
const MAX={question:320,selected:4,resultsPerProvider:5,total:20,timeout:8500};
const hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const tokens=s=>[...new Set(s.toLowerCase().split(/[^a-z0-9]+/).filter(x=>x.length>2))];
function parseQuestion(q){
 if(typeof q!=='string'||q.trim().length<10||q.length>MAX.question||/[\x00-\x1f]/.test(q))
  throw Error('HOLD_ROUTER_INVALID_QUESTION');
 return {question:q.trim(),tokens:tokens(q)};
}
export function discoverProviders(question){
 const q=parseQuestion(question);
 const overlap=(group)=>TERMS[group].filter(w=>q.tokens.includes(w));
 const matched=Object.fromEntries(Object.keys(TERMS).map(k=>[k,overlap(k)]));
 const strong=Object.values(matched).every(x=>x.length===0);
 const weights={
  github:matched.code.length*3+1,
  githubglobal:matched.code.length*3,
  wikipedia:matched.general.length*3+1,
  scholarly:matched.scholarly.length*3+1,
  crossref:matched.scholarly.length*3,
  openlibrary:matched.books.length*4,
  europepmc:matched.biomed.length*5
 };
 const ranked=Object.entries(CATALOG).map(([id,data])=>({
   id,label:data.label,group:data.group,description:data.description,
   provider_host:data.host,existing:data.existing,
   score:weights[id],
   why:matched[data.group].length?
    'Question contains '+matched[data.group].slice(0,3).join(', '):
    'General discovery fallback',
   recommendation_only:true,
   query_sent:false
 })).sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id));
 const suggested=ranked.filter(x=>x.score>=2).slice(0,MAX.selected);
 return {
  schema:'alex.eagle-eye-provider-recommendation/v0',
  question:q.question,
  recommended:suggested.map(x=>x.id),
  ranked,
  status:suggested.length?'LOCAL_PROVIDER_RECOMMENDATIONS':'NO_STRONG_PROVIDER_MATCH',
  routing:'DETERMINISTIC_LOCAL_TERMS',
  no_remote_request:true,
  explicit_operator_source_selection_required:true,
  source_wide_coverage_not_guaranteed:true
 };
}
function enforceScope(scopes){
 if(!scopes||typeof scopes!=='object'||Array.isArray(scopes)||
   Object.entries(scopes).some(([k,v])=>!Object.hasOwn(CATALOG,k)||typeof v!=='boolean'))
  throw Error('HOLD_ROUTER_UNKNOWN_SOURCE_SCOPE');
 const selected=Object.entries(scopes).filter(([,v])=>v).map(([k])=>k);
 if(selected.length<1||selected.length>MAX.selected)
  throw Error('HOLD_ROUTER_SOURCE_LIMIT_OR_CONSENT');
 return selected;
}
const clean=s=>String(s||'').replace(/<[^>]+>/g,' ').replace(/[\x00-\x1f]/g,' ').slice(0,220);
const doiUrl=s=>typeof s==='string'&&/^10\.\d{4,9}\/[^\s<>"#?]+$/i.test(s)&&s.length<130?
 'https://doi.org/'+encodeURI(s):null;
async function getJson(url,transport,githubToken){
 const u=new URL(url);
 const hosts=['api.github.com','api.crossref.org','openlibrary.org','www.ebi.ac.uk'];
 if(u.protocol!=='https:'||!hosts.includes(u.hostname))
  throw Error('HOLD_PROVIDER_NOT_ALLOWLISTED');
 const headers={'Accept':'application/json','User-Agent':'JARVIS-Eagle-Eye-025-public-discovery'};
 if(u.hostname==='api.github.com'){
  headers.Accept='application/vnd.github+json';
  headers['X-GitHub-Api-Version']='2022-11-28';
  if(githubToken)headers.Authorization='Bearer '+githubToken;
 }
 const response=await transport(u.href,{method:'GET',redirect:'error',headers,
  signal:AbortSignal.timeout(MAX.timeout)});
 if(!response?.ok||response.redirected)
  throw Error('HOLD_PROVIDER_HTTP_'+(response?.status??'UNAVAILABLE'));
 return response.json();
}
async function one(provider,question,transport,token){
 let url,mapper,extractor;
 if(provider==='githubglobal'){
  url=new URL('https://api.github.com/search/repositories');
  url.search=new URLSearchParams({q:question,per_page:String(MAX.resultsPerProvider)}).toString();
  extractor=x=>x?.items;
  mapper=x=>{
   if(x?.private!==false||!/^[-\w.]+\/[-\w.]+$/.test(x.full_name||''))return null;
   return {title:clean(x.full_name),url:'https://github.com/'+x.full_name,
    excerpt:clean(x.description),reference:x.full_name,
    provenance:'GITHUB_PUBLIC_REPOSITORY_INDEX_NOT_FILE_AUDIT'};
  };
 }else if(provider==='crossref'){
  url=new URL('https://api.crossref.org/works');
  url.search=new URLSearchParams({'query.bibliographic':question,
   rows:String(MAX.resultsPerProvider),'select':'DOI,title,published'}).toString();
  extractor=x=>x?.message?.items;
  mapper=x=>{
   const link=doiUrl(x?.DOI);
   return link?{title:clean(x.title?.[0]),url:link,reference:x.DOI,
    year:x.published?.['date-parts']?.[0]?.[0]??null,
    provenance:'CROSSREF_DOI_INDEX_NOT_ARTICLE_VERIFICATION'}:null;
  };
 }else if(provider==='openlibrary'){
  url=new URL('https://openlibrary.org/search.json');
  url.search=new URLSearchParams({q:question,limit:String(MAX.resultsPerProvider),
   fields:'key,title,author_name,first_publish_year'}).toString();
  extractor=x=>x?.docs;
  mapper=x=>{
   if(!/^\/works\/OL\d+W$/.test(x?.key||''))return null;
   return {title:clean(x.title),url:'https://openlibrary.org'+x.key,
    reference:x.key,year:x.first_publish_year??null,
    excerpt:clean(x.author_name?.slice(0,2).join(', ')),
    provenance:'OPEN_LIBRARY_BOOK_INDEX_NOT_FULL_TEXT'};
  };
 }else if(provider==='europepmc'){
  url=new URL('https://www.ebi.ac.uk/europepmc/webservices/rest/search');
  url.search=new URLSearchParams({query:question,format:'json',
   resultType:'lite',pageSize:String(MAX.resultsPerProvider)}).toString();
  extractor=x=>x?.resultList?.result;
  mapper=x=>{
   const link=doiUrl(x?.doi);
   const id=typeof x?.id==='string'&&/^[a-zA-Z0-9_-]{1,24}$/.test(x.id)?x.id:null;
   const source=/^[A-Z]{3}$/.test(x?.source||'')?x.source:null;
   const url=link||(id&&source?
    'https://europepmc.org/article/'+source+'/'+id:null);
   return url?{title:clean(x.title),url,reference:x.doi||id,
    year:Number(x.pubYear)||null,excerpt:clean(x.authorString),
    provenance:'EUROPEPMC_BIOMED_METADATA_NOT_FULL_TEXT'}:null;
  };
 }else throw Error('HOLD_PROVIDER_NOT_IMPLEMENTED');
 const payload=await getJson(url,transport,token);
 const items=extractor(payload);
 if(!Array.isArray(items))throw Error('HOLD_PROVIDER_UNEXPECTED_SCHEMA');
 return items.slice(0,MAX.resultsPerProvider).map(mapper).filter(Boolean)
  .map(item=>({...item,kind:'external_public_index',provider,
   source_host:CATALOG[provider].host,access:'PUBLIC_METADATA_ONLY'}));
}
export async function searchSelectedProviders({question,scopes},options={}){
 const q=parseQuestion(question),selected=enforceScope(scopes);
 const supplemental=selected.filter(id=>!CATALOG[id].existing);
 if(!supplemental.length){
  const obj={schema:'alex.eagle-eye-supplemental-packet/v0',question:q.question,
   selected,providers_queried:[],hits:[],failures:[],
   status:'NO_SUPPLEMENTAL_PROVIDERS_SELECTED',
   query_was_sent_only_to_selected_hosts:true,remote_writes:0,
   private_sources_accessed:false,authority:'none'};
  return {...obj,checksum_sha256:hash(obj)};
 }
 const transport=options.transport??globalThis.fetch;
 const token=options.githubToken??null;
 if(typeof transport!=='function'||token!==null&&typeof token!=='string')
  throw Error('HOLD_PROVIDER_TRANSPORT');
 const hits=[],failures=[];
 for(const provider of supplemental){
  try{hits.push(...await one(provider,q.question,transport,token))}
  catch(e){failures.push({provider,status:String(e.message||e).slice(0,120)})}
 }
 const obj={schema:'alex.eagle-eye-supplemental-packet/v0',question:q.question,
   selected,providers_queried:supplemental,
   hits:hits.slice(0,MAX.total),failures,
   status:hits.length?'PUBLIC_INDEX_LEADS':
    'HOLD_NO_SUPPLEMENTAL_PUBLIC_RESULTS',
   query_was_sent_only_to_selected_hosts:true,
   search_is_bounded_and_not_general_web_crawling:true,
   source_independence_verified:false,remote_writes:0,
   private_sources_accessed:false,authority:'none'};
 return {...obj,checksum_sha256:hash(obj)};
}
export function verifySupplemental(packet){
 if(!packet||packet.schema!=='alex.eagle-eye-supplemental-packet/v0'||
   packet.authority!=='none'||packet.private_sources_accessed!==false||
   packet.remote_writes!==0||!Array.isArray(packet.hits)||packet.hits.length>MAX.total)
  throw Error('HOLD_INVALID_SUPPLEMENTAL_PACKET');
 const {checksum_sha256,...body}=packet;
 if(hash(body)!==checksum_sha256)throw Error('HOLD_TAMPERED_SUPPLEMENTAL_PACKET');
 for(const hit of packet.hits){
  if(!Object.hasOwn(CATALOG,hit.provider)||CATALOG[hit.provider].existing||
    hit.kind!=='external_public_index'||typeof hit.url!=='string')
    throw Error('HOLD_UNTRUSTED_SUPPLEMENTAL_HIT');
  const u=new URL(hit.url);
  if(u.protocol!=='https:'||!['github.com','doi.org','openlibrary.org','europepmc.org'].includes(u.hostname))
    throw Error('HOLD_UNTRUSTED_SUPPLEMENTAL_DESTINATION');
 }
 return true;
}
export const PUBLIC_PROVIDER_CATALOG=Object.freeze(Object.entries(CATALOG).map(([id,x])=>({
 id,label:x.label,group:x.group,description:x.description,host:x.host,existing:x.existing
})));
