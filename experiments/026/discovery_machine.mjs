// MOTIF-026: gap -> ALEX source discovery -> original planZ classical plan ->
// GRAFT closed-template executable fixture -> next evidence question or HOLD.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {verifyOrgans as verify023} from '../023/open_field.mjs';
import {solve,replaySteps} from '../023/planz-snapshot/scripts/motif-classical.mjs';
import {discoverMissingProvider,verifyDiscovery}
 from './alex/api-discovery-026.mjs';
import {compileCandidate,evaluateFixture,verifyAlexSource}
 from './graft/src/discovered-adapter-026.mjs';
const hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const gitBlob=b=>createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
const sourcePins=Object.freeze({
 'alex/api-discovery-026.mjs':'67b851c9ea58d4aa92ca159000e982c312cd2335',
 'alex/eagle-eye-providers-025.mjs':'5c095be409d2ace0d39765c4316471702d88acb5',
 'graft/src/discovered-adapter-026.mjs':'3227361a543fbfaa19cc445edfa64757f2b52c71',
 'graft/vendor/alex/api-discovery-026.mjs':'67b851c9ea58d4aa92ca159000e982c312cd2335',
 'graft/vendor/alex/eagle-eye-providers-025.mjs':'5c095be409d2ace0d39765c4316471702d88acb5'
});
export function verifySourceOwners(){
 verify023();
 verifyAlexSource();
 for(const [path,expected] of Object.entries(sourcePins)){
  const b=readFileSync(new URL(path,import.meta.url));
  if(gitBlob(b)!==expected)throw Error('HOLD_MOTIF026_SOURCE_DRIFT_'+path);
 }
 return {original_source_git_blobs:sourcePins,
  source_owners:['ALEX.2','planZ','GRAFT'],
  independent_authentication_of_service:false};
}
const action=(name,cost,pre,add)=>({name,cost,pre,add,del:[]});
export function classicalProviderPlan(packet){
 verifyDiscovery(packet);
 if(packet.status!=='PROPOSED_NEW_PUBLIC_SOURCE_ADAPTER')
  return {status:'HOLD_NO_VERIFIED_SPEC_CANDIDATE',steps:[],cost:null};
 const choices=[
  action('ACKNOWLEDGE_DISCOVERED_SPEC',1,['CANDIDATE_OBSERVED'],['CANDIDATE_RECORDED']),
  action('VERIFY_SOURCE_CUSTODY_BOUNDARY',1,['CANDIDATE_RECORDED'],['SOURCE_PINS_ACKNOWLEDGED']),
  action('REVIEW_AUTHORIZATION_GAPS',1,['SOURCE_PINS_ACKNOWLEDGED'],['UNGRANTED_AUTHORITY_NOTED']),
  action('COMPILE_OFFLINE_FIXTURE_ADAPTER',2,['UNGRANTED_AUTHORITY_NOTED'],['FIXTURE_READY']),
  action('ASSUME_HOST_IS_TRUSTED',9,['UNGRANTED_AUTHORITY_NOTED'],['FIXTURE_READY']),
  action('EXECUTE_ONLY_LOCAL_FIXTURE',1,['FIXTURE_READY'],['FIXTURE_RESULT_READY']),
  action('RETAIN_SOURCE_OWNER_REVIEW',1,['FIXTURE_RESULT_READY'],['REVIEW_RECEIPT_READY'])
 ];
 const optimum=solve(choices,['CANDIDATE_OBSERVED'],['REVIEW_RECEIPT_READY']);
 if(optimum.status!=='PLAN_FOUND')throw Error('HOLD_CLASSICAL_DISCOVERY_PLAN_FAILED');
 const trace=replaySteps(choices,optimum.steps,['CANDIDATE_OBSERVED']);
 if(trace.cost!==optimum.cost||!trace.final_facts.includes('REVIEW_RECEIPT_READY'))
  throw Error('HOLD_UNREPLAYABLE_SOURCE_DISCOVERY_PLAN');
 return {schema:'motif026.classical-review-plan/v0',status:'PLAN_READY_BUT_NOT_AUTHORIZED',
  steps:optimum.steps,cost:optimum.cost,trace:trace.trace,
  optimized_with:'ORIGINAL_PLANZ_STRIPS_DIJKSTRA',
  source_receipt_sha256:packet.checksum_sha256,
  field_actions_executed:0,authority:'none'};
}
export async function investigateUnknownProvider(question,options={}){
 const source_owners=verifySourceOwners();
 const discovery=await discoverMissingProvider({
  question,approvedPublicGithubSearch:options.approvedPublicGithubSearch===true
 },{transport:options.transport,githubToken:options.githubToken});
 verifyDiscovery(discovery);
 if(discovery.status!=='PROPOSED_NEW_PUBLIC_SOURCE_ADAPTER')
  return {
   schema:'motif026.discovery-of-discovery/v0',
   status:'HOLD_NO_REVIEWABLE_NEW_PROVIDER',question,source_owners,
   discovery,plan:classicalProviderPlan(discovery),
   executable:null,next_question:'Where could an attributable original API specification be recovered?',
   candidate_service_contacted:false,
   code_deployed:false,actual_credential_authority:'NONE',
   external_write_actions:0
  };
 const plan=classicalProviderPlan(discovery);
 const chosen=discovery.public_provider_proposals[0];
 const sample=options.sample??{
  status:200,contentType:'application/json',
  body:{example:'SYNTHETIC_NOT_REAL_DATA',records:[1,2,3]}
 };
 const {compiled,observation}=await evaluateFixture(discovery,0,sample);
 if(observation.proposal_source_blob!==chosen.git_blob||
  compiled.network_authority!=='NONE'||
  observation.code_installed!==false||
  observation.actual_service_reachable!=='NOT_TESTED')
  throw Error('HOLD_OFFLINE_FIXTURE_BOUNDARY');
 const result={
  schema:'motif026.discovery-of-discovery/v0',
  status:'NEW_PROVIDER_DISCOVERED_AND_OFFLINE_ADAPTER_TESTED',
  question,source_owners,discovery,plan,
  executable:{compiled,observation},
  next_question:'Which independent official API owner, license terms, authentication rules, and safe endpoint checks would justify an operator-reviewed live connector for '+chosen.provider_name+'?',
  observational_gap:'SOURCE_SPEC_BLOB_VERIFIED_BUT_PROVIDER_IDENTITY_AND_SERVICE_NOT_VERIFIED',
  source_spec_immutable_blob:chosen.git_blob,
  original_source_owners_not_modified:true,
  candidate_service_contacted:false,
  code_deployed:false,actual_credential_authority:'NONE',
  external_write_actions:0
 };
 return {...result,receipt_sha256:hash(result)};
}
