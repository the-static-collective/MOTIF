import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {verifySourceOwners,classicalProviderPlan,investigateUnknownProvider}
 from './discovery_machine.mjs';

const q='Which live weather forecast API provides hourly weather data?';
const r='public-weather/openapi',hash=x=>createHash('sha1').update(
 Buffer.from('blob '+x.length+'\0')).update(x).digest('hex');
const content=Buffer.from(JSON.stringify({openapi:'3.0.3',info:{title:'Weather Test',version:'1'},
 servers:[{url:'https://weather.example.org'}],
 paths:{'/forecast':{get:{summary:'Get forecast'}}}}));
const blob=hash(content);
function fake(){
 const calls=[],ok=x=>({ok:true,status:200,redirected:false,json:async()=>x});
 const transport=async(url,options)=>{
  const u=new URL(url);calls.push(u.href);
  assert.equal(options.method,'GET');
  assert.equal(u.hostname,'api.github.com');
  if(u.pathname==='/search/repositories')
   return ok({items:[{full_name:r,private:false,visibility:'public',default_branch:'main'}]});
  if(u.pathname==='/repos/'+r)
   return ok({full_name:r,private:false,visibility:'public',default_branch:'main'});
  if(u.pathname==='/repos/'+r+'/branches/main')return ok({commit:{sha:'a'.repeat(40)}});
  if(u.pathname==='/repos/'+r+'/git/commits/'+'a'.repeat(40))
   return ok({tree:{sha:'b'.repeat(40)}});
  if(u.pathname==='/repos/'+r+'/git/trees/'+'b'.repeat(40))
   return ok({truncated:false,tree:[{path:'openapi.json',type:'blob',size:content.length,sha:blob}]});
  if(u.pathname==='/repos/'+r+'/git/blobs/'+blob)
   return ok({encoding:'base64',content:content.toString('base64'),size:content.length});
  throw Error('unexpected fake request');
 };
 return {transport,calls};
}
test('all inherited MOTIF-023 machinery and five new source-owner copies are Git blob verified',()=>{
 const p=verifySourceOwners();
 assert.equal(Object.keys(p.original_source_git_blobs).length,5);
 assert.deepEqual(p.source_owners,['ALEX.2','planZ','GRAFT']);
});
test('without approval there is no search, no adapter, and HOLD',async()=>{
 const f=fake();
 const p=await investigateUnknownProvider(q,{transport:f.transport});
 assert.equal(p.status,'HOLD_NO_REVIEWABLE_NEW_PROVIDER');
 assert.equal(p.executable,null);
 assert.equal(p.discovery.origin_searches_executed,0);
 assert.equal(f.calls.length,0);
});
test('unknown domain produces HOLD rather than invented source',async()=>{
 const f=fake();
 const p=await investigateUnknownProvider('How can a miracle become a true kindness?',
  {approvedPublicGithubSearch:true,transport:f.transport});
 assert.equal(p.status,'HOLD_NO_REVIEWABLE_NEW_PROVIDER');
 assert.equal(f.calls.length,0);
});
test('NEW API spec -> native original classical plan -> genuine GRAFT offline executable, then next question',async()=>{
 const f=fake();
 const x=await investigateUnknownProvider(q,{
  approvedPublicGithubSearch:true,transport:f.transport,
  sample:{status:200,contentType:'application/json',
   body:{hourly:[1,2],temperature:4,wind:8}}
 });
 assert.equal(x.status,'NEW_PROVIDER_DISCOVERED_AND_OFFLINE_ADAPTER_TESTED');
 assert.equal(x.discovery.public_provider_proposals[0].git_blob,blob);
 assert.equal(x.plan.status,'PLAN_READY_BUT_NOT_AUTHORIZED');
 assert.equal(x.plan.optimized_with,'ORIGINAL_PLANZ_STRIPS_DIJKSTRA');
 assert.ok(x.plan.steps.includes('COMPILE_OFFLINE_FIXTURE_ADAPTER'));
 assert.ok(!x.plan.steps.includes('ASSUME_HOST_IS_TRUSTED'));
 assert.ok(x.plan.cost>0);
 assert.deepEqual(x.executable.observation.fixture_fields,['hourly','temperature','wind']);
 assert.equal(x.executable.observation.actual_service_reachable,'NOT_TESTED');
 assert.equal(x.candidate_service_contacted,false);
 assert.equal(x.code_deployed,false);
 assert.equal(x.external_write_actions,0);
 assert.match(x.next_question,/authentication rules/i);
 assert.ok(f.calls.every(url=>url.startsWith('https://api.github.com/')));
});
test('no plan can use a fabricated ALEX receipt',()=>{
 assert.throws(()=>classicalProviderPlan({
  schema:'alex026.api-discovery/v0',
  status:'PROPOSED_NEW_PUBLIC_SOURCE_ADAPTER',
  authority:'deployed',no_candidate_endpoint_contact:true,
  public_provider_proposals:[],unreviewed_spec_documents:[]
 }),/INVALID_PROVIDER_DISCOVERY/);
});
