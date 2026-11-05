// MOTIF-027 staged capability-gardener study.
// Sample response cases are explicitly synthetic, not live candidate API data.
import {createHash} from 'node:crypto';
import {verifyGardenOwners,nextPlan} from './gardener.mjs';
import {discoverMissingProvider} from '../026/alex/api-discovery-026.mjs';
import {cultivate} from './graft/src/capability-gardener-027.mjs';
import {probePublicExample} from './graft/src/live-pilot-027.mjs';
const sha=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const response=body=>({status:200,contentType:'application/json',body});
export function weatherFixtureSet(){
 return {hint:'temperature',train:[
  {response:response({current:{temperature_2m:22,humidity:55},decoy:{temperature:22}}),expected:22},
  {response:response({current:{temperature_2m:17,humidity:64},decoy:{temperature:17}}),expected:17}
 ],holdout:[
  {response:response({current:{temperature_2m:1,humidity:89},decoy:{temperature:19}}),expected:1},
  {response:response({current:{temperature_2m:-8,humidity:62},decoy:{temperature:28}}),expected:-8}
 ],negative:[
  {response:response({current:{temperature_2m:'invalid'}}),reject:true},
  {response:response({current:{humidity:44}}),reject:true},
  {response:{status:502,contentType:'application/json',
   body:{current:{temperature_2m:22}}},reject:true}
 ]};
}
export async function gardenerCycle({question,approvedPublicSourceSearch=false,
 approvedPublicPilot=false,fixtureSet=null}={},options={}){
 const owners=verifyGardenOwners();
 const source=await discoverMissingProvider({
  question,approvedPublicGithubSearch:approvedPublicSourceSearch
 },{transport:options.sourceTransport??options.transport,githubToken:options.githubToken});
 if(source.status!=='PROPOSED_NEW_PUBLIC_SOURCE_ADAPTER')
  return {schema:'motif027.gardener-study/v0',
   status:'HOLD_NO_REVIEWABLE_SOURCE_SPEC',source,owners,
   evaluation:null,feedback_plan:null,pilot:null,production_install:false};
 const weather=source.gap?.identified_domain==='weather';
 const fixtures=fixtureSet??(weather?weatherFixtureSet():null);
 if(!fixtures)return {schema:'motif027.gardener-study/v0',
  status:'HOLD_REQUIRES_LABELED_FIXTURES',source,owners,
  evaluation:null,feedback_plan:null,pilot:null,production_install:false};
 const evaluation=await cultivate(source,fixtures);
 const feedback_plan=nextPlan(evaluation);
 const pilot=approvedPublicPilot?await probePublicExample({approvedPublicPilot:true},
  {transport:options.pilotTransport??globalThis.fetch}):
  {schema:'graft027.public-live-read/v0',
   status:'HOLD_LIVE_CONTACT_NOT_APPROVED',requests:0};
 const body={
  schema:'motif027.gardener-study/v0',
  status:evaluation.winner?'HELD_BEST_RESEARCH_VARIANT':
   'HOLD_ALL_VARIANTS_REJECTED',
  source,owners,evaluation,feedback_plan,pilot,
  sample_training_evidence:'SYNTHETIC_LABELED_FIXTURES',
  candidate_server_contacted:false,
  live_read_is_fixed_example_not_discovered_provider:true,
  third_party_live_read_performed:pilot.status==='READ_ONLY_THIRD_PARTY_RESPONSE_OBSERVED',
  arbitrary_adapter_invention_proved:false,
  unrestricted_internet_browsing_proved:false,
  automatically_connected_unknown_services:false,
  production_install:false,external_writes:0,
  review_required:true};
 return {...body,checksum_sha256:sha(body)};
}
