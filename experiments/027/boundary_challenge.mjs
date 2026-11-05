// MOTIF-027 adversarial boundary challenge: three explicit claims under test.
// The candidate-spec search uses ONLY an in-memory GitHub API double.
// --public-pilot optionally makes one separately approved, fixed Open-Meteo read.
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {gardenerCycle,weatherFixtureSet} from './garden_loop.mjs';
const question='Which live weather forecast API provides hourly weather data?';
const repo='example-public/openapi-weather';
const bytes=Buffer.from(JSON.stringify({
 openapi:'3.0.0',info:{title:'Example Forecast API',version:'1'},
 servers:[{url:'https://unverified-service.example.org'}],
 paths:{'/forecast':{get:{summary:'Find weather'}}}
}));
const sha=bytes=>createHash('sha1')
 .update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
const blob=sha(bytes);
function fakeGitHub(){
 const calls=[],ok=x=>({ok:true,status:200,redirected:false,json:async()=>x});
 const transport=async(url,options)=>{
  const u=new URL(url);calls.push(u.hostname);
  if(u.hostname!=='api.github.com'||options.method!=='GET')
   throw Error('HOLD_PUBLIC_SOURCE_TRANSPORT_SCOPE');
  if(u.pathname==='/search/repositories')
   return ok({items:[{private:false,visibility:'public',
    default_branch:'main',full_name:repo}]});
  if(u.pathname==='/repos/'+repo)
   return ok({private:false,visibility:'public',
    default_branch:'main',full_name:repo});
  if(u.pathname==='/repos/'+repo+'/branches/main')
   return ok({commit:{sha:'a'.repeat(40)}});
  if(u.pathname==='/repos/'+repo+'/git/commits/'+'a'.repeat(40))
   return ok({tree:{sha:'b'.repeat(40)}});
  if(u.pathname==='/repos/'+repo+'/git/trees/'+'b'.repeat(40))
   return ok({truncated:false,tree:[{path:'openapi.json',
    type:'blob',sha:blob,size:bytes.length}]});
  if(u.pathname==='/repos/'+repo+'/git/blobs/'+blob)
   return ok({size:bytes.length,encoding:'base64',
    content:bytes.toString('base64')});
  throw Error('HOLD_OUTSIDE_MOCK_CATALOG');
 };
 return {calls,transport};
}
export async function challenge({publicPilot=false}={}){
 const a=fakeGitHub();
 const denied=await gardenerCycle({question},{sourceTransport:a.transport});
 if(denied.status!=='HOLD_NO_REVIEWABLE_SOURCE_SPEC'||a.calls.length)
  throw Error('CHALLENGE_FAILED_CONSENT');
 const b=fakeGitHub();
 const good=await gardenerCycle({question,approvedPublicSourceSearch:true},
  {sourceTransport:b.transport});
 if(good.status!=='HELD_BEST_RESEARCH_VARIANT'||
  good.evaluation.winner?.selector.join('.')!=='current.temperature_2m'||
  good.evaluation.leaderboard.every(x=>x.failures.length===0))
  throw Error('CHALLENGE_FAILED_VARIANT_SEPARATION');
 const c=fakeGitHub(),cases=weatherFixtureSet();
 cases.holdout=[{response:{
  status:200,contentType:'application/json',
  body:{current:{temperature_2m:22},decoy:{temperature:22}}
 },expected:999}];
 const counter=await gardenerCycle({question,approvedPublicSourceSearch:true,
  fixtureSet:cases},{sourceTransport:c.transport});
 if(counter.status!=='HOLD_ALL_VARIANTS_REJECTED'||
  !counter.feedback_plan.steps.includes('REQUEST_NEW_LABELED_CASES'))
  throw Error('CHALLENGE_FAILED_HOLDOUT_COUNTEREXAMPLE');
 if(!b.calls.length||b.calls.some(x=>x!=='api.github.com')||
  c.calls.some(x=>x!=='api.github.com'))
  throw Error('CHALLENGE_FAILED_SOURCE_SCOPE');
 let live=null;
 if(publicPilot){
  const d=fakeGitHub();
  const p=await gardenerCycle({question,approvedPublicSourceSearch:true,
   approvedPublicPilot:true},{sourceTransport:d.transport});
  if(p.pilot.status!=='READ_ONLY_THIRD_PARTY_RESPONSE_OBSERVED'||
   p.pilot.requests!==1||p.candidate_server_contacted)
   throw Error('CHALLENGE_FAILED_LIVE_BOUNDARY');
  live={status:p.pilot.status,source_host:p.pilot.endpoint_host,
   public_example:p.pilot.example_location,
   response_digest_sha256:p.pilot.actual_response_digest_sha256,
   candidate_server_contacted:p.candidate_server_contacted};
 }
 return {
  schema:'motif027.boundary-challenge/v0',
  status:'THREE_LIMITS_CHALLENGED_WITH_INTEGRITY',
  trials:{
   source_consent:{status:'HOLD_WITHOUT_OPERATOR_APPROVAL',network_requests:a.calls.length},
   executable_variants:{status:'NEW_FINITE_CODE_EXECUTED',count:good.evaluation.variants_tested,
    best_selector:good.evaluation.winner.selector,
    failed_variant_count:good.evaluation.leaderboard.filter(x=>x.failures.length>0).length,
    source_code_installed:false},
   contradiction:{status:'HOLD_FOR_BETTER_EVIDENCE',
    next_classical_action:counter.feedback_plan.steps.find(x=>x==='REQUEST_NEW_LABELED_CASES')},
   breadth:{status:'BOUNDED_PUBLIC_GITHUB_ONLY',unknown_host_requests:0,
    arbitrary_web_crawler_demonstrated:false},
   third_party:live??{status:'NOT_EXECUTED_NO_PILOT_APPROVAL'}
  },
  independent_source_trust_not_proven:true,
  full_arbitrary_program_invention_not_proven:true,
  unrestricted_browsing_not_proven:true,
  automatic_unknown_provider_install_not_proven:true,
  source_mutations:0,external_writes:0
 };
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 challenge({publicPilot:process.argv.includes('--public-pilot')})
 .then(r=>process.stdout.write(JSON.stringify(r,null,2)+'\n'))
 .catch(e=>{process.stderr.write(String(e.message)+'\n');process.exitCode=2});
}
