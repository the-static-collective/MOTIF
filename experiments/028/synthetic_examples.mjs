// Synthetic, privacy-free MOTIF-028 test data. Never a claim that this
// GitHub repository or proposed OpenAPI provider exists in the real world.
import {createHash} from 'node:crypto';
const digest=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
export function syntheticSource(){
 const repository='example-fixture/weather-source',
  source_commit='b'.repeat(40),git_blob='a'.repeat(40);
 const body={
  schema:'alex026.api-discovery/v0',status:'PROPOSED_NEW_PUBLIC_SOURCE_ADAPTER',
  authority:'none',no_candidate_endpoint_contact:true,
  synthetic_fixture_not_a_verified_external_repository:true,
  unreviewed_spec_documents:[{
   repository,source_commit,path:'openapi.json',git_blob,
   complete_original_blob_verified:true
  }],
  public_provider_proposals:[{
   schema:'alex026.source-attested-api-proposal/v0',
   provider_name:'Synthetic Weather API',
   repository,source_commit,spec_path:'openapi.json',git_blob,
   operation:{method:'GET',path:'/weather'},
   declared_servers:['https://example.org'],
   spec_format:'OPENAPI3_JSON_GIT_BLOB_VERIFIED',
   candidate_host_contact_authorized:false,production_permissions:'NONE'
  }]
 };
 return {...body,checksum_sha256:digest(body)};
}
const response=body=>({status:200,contentType:'application/json',body});
export function normalCases(){
 return {
  hint:'temperature',
  train:[
   {response:response({current:{temperature_2m:24,humidity:44},wrong:{temperature:24}}),expected:24},
   {response:response({current:{temperature_2m:26,humidity:46},wrong:{temperature:26}}),expected:26}
  ],
  holdout:[
   {response:response({current:{temperature_2m:19,humidity:88},wrong:{temperature:-30}}),expected:19},
   {response:response({current:{temperature_2m:-2,humidity:90},wrong:{temperature:28}}),expected:-2}
  ],
  negative:[
   {response:response({current:{temperature_2m:'bad'}}),reject:true},
   {response:response({current:{humidity:50}}),reject:true},
   {response:{status:503,contentType:'application/json',
    body:{current:{temperature_2m:19}}},reject:true}
  ]
 };
}
export function failedCases(){
 const x=normalCases();
 x.holdout=[{response:response({
  current:{temperature_2m:22,humidity:77},wrong:{temperature:22}
 }),expected:999}];
 return x;
}
export function futureCases(){
 const x=normalCases();
 x.holdout=[{response:response({
  current:{temperature_2m:35,humidity:50},wrong:{temperature:-15}
 }),expected:35}];
 return x;
}
export function unrelatedCases(){
 return {hint:'population',
  train:[{response:response({region:{population:20}}),expected:20}],
  holdout:[{response:response({region:{population:21}}),expected:21}],
  negative:[{response:response({region:{population:'missing'}}),reject:true}]
 };
}
