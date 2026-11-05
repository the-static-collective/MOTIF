import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {verifyGardenOwners,nextPlan} from './gardener.mjs';
import {gardenerCycle,weatherFixtureSet} from './garden_loop.mjs';
import {compileVariant} from './graft/src/capability-gardener-027.mjs';

const question='Which live weather forecast API provides hourly weather data?';
const repo='test-lab/weather-spec';
const body=Buffer.from(JSON.stringify({openapi:'3.0.3',info:{title:'Weather',version:'1.0'},
 servers:[{url:'http://169.254.169.254/latest'},{url:'https://unconfirmed.example.org'}],
 paths:{'/forecast':{get:{summary:'Test forecast'}}}}));
const blob=x=>createHash('sha1').update(Buffer.from('blob '+x.length+'\0')).update(x).digest('hex');
const sha=blob(body);
function mockSource(){
 const requests=[],ok=x=>({ok:true,status:200,redirected:false,json:async()=>x});
 const transport=async(url,options)=>{
  const u=new URL(url);requests.push(u.href);
  assert.equal(u.hostname,'api.github.com');
  assert.equal(options.method,'GET');
  if(u.pathname==='/search/repositories')
   return ok({items:[{private:false,visibility:'public',default_branch:'main',full_name:repo}]});
  if(u.pathname==='/repos/'+repo)
   return ok({private:false,visibility:'public',default_branch:'main',full_name:repo});
  if(u.pathname==='/repos/'+repo+'/branches/main')
   return ok({commit:{sha:'a'.repeat(40)}});
  if(u.pathname==='/repos/'+repo+'/git/commits/'+'a'.repeat(40))
   return ok({tree:{sha:'b'.repeat(40)}});
  if(u.pathname==='/repos/'+repo+'/git/trees/'+'b'.repeat(40))
   return ok({truncated:false,tree:[{path:'openapi.json',type:'blob',size:body.length,sha}]});
  if(u.pathname==='/repos/'+repo+'/git/blobs/'+sha)
   return ok({size:body.length,encoding:'base64',content:body.toString('base64')});
  throw Error('Unexpected public GitHub request');
 };
 return {requests,transport};
}
const fixedResponse=()=>new Response(JSON.stringify({
 latitude:52.52,longitude:13.41,current:{temperature_2m:11,time:'2026-11-05T12:00'},
 current_units:{temperature_2m:'°C'}
}),{status:200,headers:{'content-type':'application/json'}});
test('all previous source-owner code and five original GRAFT donor copies are unchanged',()=>{
 const v=verifyGardenOwners();
 assert.equal(Object.keys(v.git_source_blobs).length,5);
 assert.equal(v.authenticated_external_service,false);
});
test('default inquiry with no source search consent does NOT use public internet',async()=>{
 const f=mockSource();
 const r=await gardenerCycle({question},{sourceTransport:f.transport});
 assert.equal(r.status,'HOLD_NO_REVIEWABLE_SOURCE_SPEC');
 assert.equal(f.requests.length,0);
 assert.equal(r.production_install,false);
});
test('source-attested discovery grows, tests and ranks NEW field path extractors',async()=>{
 const f=mockSource();
 const r=await gardenerCycle({question,approvedPublicSourceSearch:true},
  {sourceTransport:f.transport});
 assert.equal(r.status,'HELD_BEST_RESEARCH_VARIANT');
 assert.equal(r.source.public_provider_proposals[0].git_blob,sha);
 assert.deepEqual(r.evaluation.winner.selector,['current','temperature_2m']);
 assert.ok(r.evaluation.variants_tested>=2);
 assert.ok(r.evaluation.leaderboard.some(x=>x.failures.length));
 assert.equal(r.feedback_plan.schema,'motif027.feedback-plan/v0');
 assert.ok(r.feedback_plan.steps.includes('SEEK_INDEPENDENT_EVIDENCE'));
 assert.ok(!r.feedback_plan.steps.includes('ASSUME_RESULTS_ARE_GENERAL'));
 assert.equal(r.pilot.requests,0);
 assert.equal(r.candidate_server_contacted,false);
 assert.equal(r.production_install,false);
 assert.equal(r.arbitrary_adapter_invention_proved,false);
 assert.equal(r.unrestricted_internet_browsing_proved,false);
 assert.ok(f.requests.every(x=>x.startsWith('https://api.github.com/')));
});
test('conflicting withheld fixtures overturn promising training result and drive different classical plan',async()=>{
 const d=weatherFixtureSet();
 d.holdout=[{response:{status:200,contentType:'application/json',
  body:{current:{temperature_2m:12},decoy:{temperature:12}}},expected:4321}];
 const f=mockSource();
 const r=await gardenerCycle({question,approvedPublicSourceSearch:true,fixtureSet:d},
  {sourceTransport:f.transport});
 assert.equal(r.status,'HOLD_ALL_VARIANTS_REJECTED');
 assert.equal(r.evaluation.winner,null);
 assert.ok(r.feedback_plan.steps.includes('REQUEST_NEW_LABELED_CASES'));
 assert.ok(r.evaluation.leaderboard.every(x=>!x.admissible_for_fixture_review));
});
test('known malicious advertised server is NOT contacted; only separate approved fixed example may be read',async()=>{
 const f=mockSource(),hosts=[];
 const r=await gardenerCycle({question,approvedPublicSourceSearch:true,
  approvedPublicPilot:true},{
   sourceTransport:f.transport,
   pilotTransport:async (url,options)=>{
    hosts.push(new URL(url).hostname);
    assert.equal(options.method,'GET');
    assert.equal(options.redirect,'error');
    return fixedResponse();
   }
  });
 assert.equal(r.status,'HELD_BEST_RESEARCH_VARIANT');
 assert.deepEqual(hosts,['api.open-meteo.com']);
 assert.equal(r.pilot.status,'READ_ONLY_THIRD_PARTY_RESPONSE_OBSERVED');
 assert.equal(r.third_party_live_read_performed,true);
 assert.equal(r.live_read_is_fixed_example_not_discovered_provider,true);
 assert.equal(r.candidate_server_contacted,false);
 assert.equal(r.pilot.credentials_sent,false);
 assert.equal(r.external_writes,0);
});
test('source field code emission rejects prototype-like selectors',()=>{
 assert.throws(()=>compileVariant(['constructor']),/UNSAFE_SOURCE_FIELD_PATH/);
 assert.throws(()=>compileVariant(['__proto__']),/UNSAFE_SOURCE_FIELD_PATH/);
 const x=compileVariant(['unknown','weather_field']);
 assert.ok(!x.source.includes('fetch('));
 assert.equal(x.network_authority,'NONE');
});
test('fabricated test observation cannot drive classical plan',()=>{
 assert.throws(()=>nextPlan({
  schema:'graft027.garden-evaluation/v0',authority:'deployed',production_install:true
 }),/INVALID_TEST_OBSERVATION/);
});
