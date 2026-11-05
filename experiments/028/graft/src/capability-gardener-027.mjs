// GRAFT-027 — capability gardener grows novel numeric-field extractors from
// source-verified candidate + training examples, tests withheld and negative
// cases, retains failed variants, and proposes a better source question.
import {createHash} from 'node:crypto';
import {verifyDiscovery} from '../vendor/alex/api-discovery-026.mjs';
import {verifyAlexSource} from './discovered-adapter-026.mjs';
const hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const sourceHash=x=>createHash('sha256').update(x).digest('hex');
const BAD=new Set(['__proto__','constructor','prototype','then','toString']);
const MAX={train:12,validation:12,negative:12,paths:80,depth:4,variants:8,source:5000};
function validateCases(cases,max,label){
 if(!Array.isArray(cases)||cases.length<1||cases.length>max)throw Error('HOLD_'+label+'_BUDGET');
 for(const f of cases){
  if(!f||typeof f!=='object'||Array.isArray(f)||
    !f.response||typeof f.response!=='object'||
    !Number.isSafeInteger(f.response.status)||
    !f.response.body||typeof f.response.body!=='object'||
    (f.reject!==true&&(!Number.isFinite(f.expected)||typeof f.expected!=='number')))
    throw Error('HOLD_INVALID_'+label+'_FIXTURE');
  if(JSON.stringify(f).length>14000)throw Error('HOLD_OVERSIZE_'+label+'_FIXTURE');
 }
}
function paths(value){
 const all=[];
 const walk=(o,parts)=>{
  if(parts.length>=MAX.depth||!o||typeof o!=='object'||Array.isArray(o))return;
  for(const key of Object.keys(o).slice(0,35)){
   if(!/^[a-zA-Z][a-zA-Z0-9_]{0,40}$/.test(key)||BAD.has(key))continue;
   const here=[...parts,key],v=o[key];
   if(typeof v==='number'&&Number.isFinite(v))all.push(here);
   else if(v&&typeof v==='object'&&!Array.isArray(v))walk(v,here);
  }
 };
 walk(value,[]);
 return all.slice(0,MAX.paths);
}
function pathIsSafe(a){
 return Array.isArray(a)&&a.length>=1&&a.length<=MAX.depth&&
 a.every(k=>typeof k==='string'&&/^[a-zA-Z][a-zA-Z0-9_]{0,40}$/.test(k)&&!BAD.has(k));
}
const TEMPLATE="// GRAFT-027 closed-template numeric projection. No network, shell or writes.\nexport function execute(input){\n if(!input||typeof input!=='object'||Array.isArray(input)||\n  input.status!==200||typeof input.contentType!=='string'||\n  !input.contentType.toLowerCase().includes('application/json')||\n  !input.body||typeof input.body!=='object'||Array.isArray(input.body))\n  return {status:'HOLD_INVALID_RESPONSE',value:null};\n let cursor=input.body;\n for(const key of FIELD_PATH){\n  if(!cursor||typeof cursor!=='object'||Array.isArray(cursor)||\n     !Object.prototype.hasOwnProperty.call(cursor,key))\n   return {status:'HOLD_MISSING_FIELD',value:null};\n  cursor=cursor[key];\n }\n if(typeof cursor!=='number'||!Number.isFinite(cursor))\n  return {status:'HOLD_WRONG_FIELD_TYPE',value:null};\n return {status:'OBSERVED_NUMERIC_FIELD',value:cursor};\n}";

export function compileVariant(selector){
 if(!pathIsSafe(selector))throw Error('HOLD_UNSAFE_SOURCE_FIELD_PATH');
 const source='const FIELD_PATH='+JSON.stringify(selector)+';\n'+TEMPLATE+'\n';
 if(source.length>MAX.source)throw Error('HOLD_GENERATED_SOURCE_BUDGET');
 return {selector:[...selector],source,source_sha256:sourceHash(source),
  generated_from:'DECLARED_JSON_FIELD_GRAMMAR_WITH_CLOSED_EXECUTOR',
  code_installed:false,network_authority:'NONE'};
}
async function evaluate(source,fixtures){
 const mod=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
 return fixtures.map(f=>{
  const got=mod.execute(f.response);
  return {status:got.status,satisfied:f.reject===true?
    got.status!=='OBSERVED_NUMERIC_FIELD':
    got.status==='OBSERVED_NUMERIC_FIELD'&&Object.is(got.value,f.expected),
    observed_value:got.value};
 });
}
export function proposeVariants(packet,{train,holdout,negative,hint}){
 verifyAlexSource();verifyDiscovery(packet);
 if(packet.status!=='PROPOSED_NEW_PUBLIC_SOURCE_ADAPTER'||
  !packet.public_provider_proposals.length)throw Error('HOLD_NO_SUPPORTED_SOURCE_PROPOSAL');
 validateCases(train,MAX.train,'TRAIN');
 validateCases(holdout,MAX.validation,'HOLDOUT');
 validateCases(negative,MAX.negative,'NEGATIVE');
 if(typeof hint!=='string'||hint.length<3||hint.length>60)
  throw Error('HOLD_UNCLEAR_EXTRACTION_TARGET');
 const all=new Map();
 for(const f of train){
  for(const p of paths(f.response.body)){
   const key=JSON.stringify(p);
   if(!all.has(key))all.set(key,p);
  }
 }
 const names=hint.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
 const ranked=[...all.values()].map(selector=>{
  const last=selector[selector.length-1].toLowerCase();
  return {selector,relevance:names.filter(w=>last.includes(w)).length};
 }).sort((a,b)=>b.relevance-a.relevance||
  a.selector.length-b.selector.length||
  JSON.stringify(a.selector).localeCompare(JSON.stringify(b.selector)));
 const variants=ranked.slice(0,MAX.variants).map((v,i)=>({
  ...compileVariant(v.selector),candidate_id:'G027-'+String(i+1).padStart(2,'0'),
  label:'Numeric field '+v.selector.join('.'),semantic_hint_overlap:v.relevance
 }));
 const body={schema:'graft027.garden-proposal/v0',
  status:variants.length?'REVIEWABLE_VARIANTS':'HOLD_NO_NUMERIC_FIELD_CANDIDATES',
  source_alex_receipt:packet.checksum_sha256,
  source_spec_blob:packet.public_provider_proposals[0].git_blob,
  target_hint:hint,variants,
  training_fixture_count:train.length,withheld_fixture_count:holdout.length,
  negative_fixture_count:negative.length,source_grammar:'FINITE_NUMERIC_JSON_PATHS',
  source_owner_admission:false,live_connectors_installed:0,authority:'none'};
 return {...body,checksum_sha256:hash(body)};
}
export async function cultivate(packet,cases){
 const proposal=proposeVariants(packet,cases),results=[];
 for(const candidate of proposal.variants){
  const expected=compileVariant(candidate.selector);
  if(candidate.source!==expected.source||candidate.source_sha256!==expected.source_sha256)
   throw Error('HOLD_CHANGED_GRAFT_CANDIDATE');
  const training=await evaluate(candidate.source,cases.train);
  const holdout=await evaluate(candidate.source,cases.holdout);
  const negative=await evaluate(candidate.source,cases.negative);
  const count=arr=>arr.filter(x=>x.satisfied).length;
  const training_pass=count(training),withheld_pass=count(holdout),
   negative_pass=count(negative);
  const admission=training_pass===training.length&&
   withheld_pass===holdout.length&&negative_pass===negative.length;
  results.push({candidate_id:candidate.candidate_id,
   selector:candidate.selector,source_sha256:candidate.source_sha256,
   training_pass,training_total:training.length,
   withheld_pass,withheld_total:holdout.length,
   negative_pass,negative_total:negative.length,
   score:training_pass+withheld_pass*3+negative_pass*2,
   admissible_for_fixture_review:admission,
   real_world_accuracy_not_established:true,
   failures:[
    ...training.flatMap((x,i)=>x.satisfied?[]:['train:'+i]),
    ...holdout.flatMap((x,i)=>x.satisfied?[]:['holdout:'+i]),
    ...negative.flatMap((x,i)=>x.satisfied?[]:['negative:'+i])
   ],source_code_still_not_installed:true});
 }
 results.sort((a,b)=>Number(b.admissible_for_fixture_review)-
  Number(a.admissible_for_fixture_review)||b.score-a.score||
  a.candidate_id.localeCompare(b.candidate_id));
 const winner=results.find(r=>r.admissible_for_fixture_review)||null;
 const body={schema:'graft027.garden-evaluation/v0',
  status:winner?'HELD_BEST_FIXTURE_CANDIDATE':'HOLD_ALL_VARIANTS_FAIL',
  proposal_checksum:proposal.checksum_sha256,source_blob:proposal.source_spec_blob,
  variants_tested:results.length,leaderboard:results,
  winner:winner?{candidate_id:winner.candidate_id,
   selector:winner.selector,source_sha256:winner.source_sha256}:null,
  failure_driven_next_question:winner?
   'Which independently sourced live response would establish that this projection generalizes?':
   'Which new independently labeled fixtures would distinguish the rejected field paths?',
  automated_tests_executed:results.length*(cases.train.length+
   cases.holdout.length+cases.negative.length),
  source_owner_review_required:true,live_server_contacted:false,
  source_writes:0,production_install:false,authority:'none'};
 return {...body,checksum_sha256:hash(body)};
}
