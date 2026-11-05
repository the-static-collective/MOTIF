// GRAFT-026: source-owned adapter composition from independently pinned ALEX.
// Only performs a bounded, in-memory JSON response fixture analysis.
// No arbitrary source to code, network calls, automatic installs or grants.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {verifyDiscovery} from '../vendor/alex/api-discovery-026.mjs';
const sha=x=>createHash('sha256').update(x).digest('hex');
const gitBlob=bytes=>createHash('sha1').update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
const PINS=Object.freeze({
 'api-discovery-026.mjs':'67b851c9ea58d4aa92ca159000e982c312cd2335',
 'eagle-eye-providers-025.mjs':'5c095be409d2ace0d39765c4316471702d88acb5'
});
export function verifyAlexSource(){
 for(const [path,expected] of Object.entries(PINS)){
  const bytes=readFileSync(new URL('../vendor/alex/'+path,import.meta.url));
  if(gitBlob(bytes)!==expected)throw Error('HOLD_CHANGED_ORIGINAL_ALEX_SOURCE');
 }
 return {source:'the-static-collective/ALEX.2',
  exact_git_blobs:PINS,external_authority:false};
}
const TEMPLATE="// GRAFT-026 fixed template. ONLY tested against an in-memory fixture.\nexport function runFixture(response) {\n if(!response||typeof response!=='object'||Array.isArray(response)||\n   response.status!==200||typeof response.contentType!=='string'||\n   !response.contentType.toLowerCase().includes('application/json')||\n   typeof response.body!=='object'||response.body===null||\n   Array.isArray(response.body))\n   throw Error('HOLD_FIXTURE_NOT_VALID_JSON_RESPONSE');\n const fields=Object.keys(response.body)\n  .filter(k=>/^[a-zA-Z][a-zA-Z0-9_-]{0,40}$/.test(k)).slice(0,5);\n return {schema:'graft026.fixture-adapter-observation/v0',\n  proposal_source_blob:CONFIG.blob,\n  declared_operation:CONFIG.method+' '+CONFIG.path,\n  declared_provider:CONFIG.title,\n  fixture_fields:fields,data_points_previewed:fields.length,\n  result:'LOCAL_FIXTURE_ONLY',actual_service_reachable:'NOT_TESTED',\n  response_schema_certified:false,source_owner_admission:false,\n  code_installed:false,outbound_requests:0,authority:'none'};\n}";

export function compileCandidate(packet,index=0){
 verifyAlexSource();verifyDiscovery(packet);
 if(packet.status!=='PROPOSED_NEW_PUBLIC_SOURCE_ADAPTER')
  throw Error('HOLD_NO_REVIEWABLE_DISCOVERY');
 if(!Number.isInteger(index)||index<0||index>=packet.public_provider_proposals.length)
  throw Error('HOLD_UNKNOWN_CANDIDATE');
 const p=packet.public_provider_proposals[index];
 if(p.schema!=='alex026.source-attested-api-proposal/v0'||
  p.spec_format!=='OPENAPI3_JSON_GIT_BLOB_VERIFIED'||
  !/^[a-f0-9]{40}$/.test(p.git_blob)||p.operation?.method!=='GET'||
  !/^\/[\w{}./-]{1,100}$/.test(p.operation?.path||'')||
  p.candidate_host_contact_authorized!==false||
  p.production_permissions!=='NONE')
  throw Error('HOLD_UNSAFE_API_PROPOSAL');
 const config={blob:p.git_blob,method:'GET',path:p.operation.path,
  title:p.provider_name.slice(0,100)};
 const program='const CONFIG='+JSON.stringify(config)+';\n'+TEMPLATE+'\n';
 if(program.length>10000)throw Error('HOLD_ADAPTER_SIZE_BUDGET');
 return {schema:'graft026.compiled-proposal/v0',
  status:'LOCAL_EXECUTABLE_FIXTURE_ADAPTER',
  original_alex_packet_sha256:packet.checksum_sha256,
  source_blob:p.git_blob,source_repository:p.repository,
  operation:p.operation.path,output_code:program,
  output_code_sha256:sha(program),
  compilation_kind:'AUDITED_CLOSED_TEMPLATE_WITH_GIT_PINNED_DECLARATIONS',
  live_endpoint_calls_compiled:false,network_authority:'NONE',
  deployed:false,source_owner_review_required:true,authority:'none'};
}
export async function evaluateFixture(packet,index,sample){
 const compiled=compileCandidate(packet,index);
 const duplicate=compileCandidate(packet,index);
 if(compiled.output_code!==duplicate.output_code)
  throw Error('HOLD_NONDETERMINISTIC_COMPOSITION');
 const module=await import('data:text/javascript;base64,'+
  Buffer.from(duplicate.output_code).toString('base64'));
 const observation=module.runFixture(sample);
 if(observation.outbound_requests!==0||
  observation.actual_service_reachable!=='NOT_TESTED'||
  observation.authority!=='none')
  throw Error('HOLD_EXECUTED_FIXTURE_ESCAPED_SCOPE');
 return {compiled:{
  schema:compiled.schema,source_blob:compiled.source_blob,
  output_code_sha256:compiled.output_code_sha256,
  output_code_bytes:Buffer.byteLength(compiled.output_code),
  network_authority:'NONE',deployed:false
 },observation};
}
