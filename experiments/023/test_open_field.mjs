import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {runOpenField,verifyOrgans,demonstrate} from './open_field.mjs';
const bHash=x=>createHash('sha1').update(Buffer.from('blob '+x.length+'\0')).update(x).digest('hex');
const seed='Which original Maxhinal Fiber and Pressure chambers preserve source custody?';
function fakeApi({corrupt=false,privateNames=[]}={}){
 const calls=[];
 const lines={
 'the-static-collective/MOTIF':[
  ['README.md','MOTIF source questions reason about independent observers and method changes.'],
  ['docs/THE-OUTERMOST-CIRCLE.md','Source reasoning and source provenance remain unresolved questions.']
 ],
 'the-static-collective/ALEX.2':[
  ['README.md','ALEX source custody distinguishes original witnesses from independent reference records.'],
  ['docs/MOTIF-023.md','Original source evidence is not automatically independently verified.']
 ],
 'the-static-collective/planZ':[
  ['README.md','planZ classical planning builds source review plans and tracks uncertainty.'],
  ['docs/ATTENTION-001.md','Plan observations are not a grant of authority.']
 ],
 'the-static-collective/GRAFT':[
  ['README.md','GRAFT composes executable source review capabilities with owner approval.'],
  ['docs/MOTIF-023.md','GRAFT source custody contract and executable capability receipt.']
 ],
 'the-static-collective/the-daily-slice':[
  ['README.md','Maxhinal MADD original source machine for creative research.'],
  ['artifacts/maxhinal/README.md','Original Maxhinal Fiber and Pressure chambers preserve source custody.']
 ]
 };
 const transport=async(url,opts)=>{
  const u=new URL(url),ps=u.pathname.split('/').filter(Boolean);
  assert.equal(u.hostname,'api.github.com');
  assert.equal(opts.method,'GET');
  calls.push(url);
  const repo=ps[1]+'/'+ps[2],records=lines[repo];
  if(!records)return{ok:false,status:404};
  const docs=records.map(([path,txt])=>({
   path,bytes:Buffer.from(txt),sha:bHash(Buffer.from(txt))
  }));
  let result;
  const rest=ps.slice(3).join('/');
  if(!rest){
   const pr=privateNames.includes(repo);
   result={full_name:repo,default_branch:'main',private:pr,
    visibility:pr?'private':'public'};
  }else if(rest==='branches/main')result={commit:{sha:'a'.repeat(40)}};
  else if(rest==='git/commits/'+'a'.repeat(40))result={tree:{sha:'b'.repeat(40)}};
  else if(rest==='git/trees/'+'b'.repeat(40))result={truncated:false,
    tree:docs.map(d=>({path:d.path,type:'blob',
      sha:d.sha,size:d.bytes.length}))};
  else if(rest.startsWith('git/blobs/')){
   const d=docs.find(x=>x.sha===rest.slice('git/blobs/'.length));
   if(!d)return{ok:false,status:404};
   const bytes=corrupt?Buffer.from(d.bytes.toString()+'!'):d.bytes;
   result={encoding:'base64',size:d.bytes.length,
     content:bytes.toString('base64')};
  }else return{ok:false,status:404};
  return{ok:true,status:200,json:async()=>result};
 };
 return{transport,calls};
}
test('new 023 originals are content-pinned and inherited 021/022 source orgs still verify',()=>{
 const proof=verifyOrgans();
 assert.equal(Object.keys(proof.source_blobs).length,6);
 assert.equal(proof.source_blobs['alex-snapshot/tools/motif023-live.mjs'],
  '00690d5b8f540f5a59719f97349710eba17254f5');
 assert.equal(proof.source_blobs['planz-snapshot/scripts/motif023-replan.mjs'],
  '5e4073cd245714eaca63036d60190780feb22171');
});
test('a single fresh question conducts two DIFFERENT repo collection searches and TWO generated executable capabilities',async()=>{
 const api=fakeApi();
 const r=await runOpenField(seed,{transport:api.transport});
 assert.equal(r.status,'TWO_LIVE_PUBLIC_INQUIRIES_AND_TWO_LOCAL_CAPABILITIES');
 assert.ok(r.first.packet.sources.length>0);
 assert.ok(r.first.packet.hits.length>0);
 assert.equal(r.first.plan.mode,'LINEAGE');
 assert.equal(r.first.execution.mode,'LINEAGE');
 assert.equal(r.first.candidate.production_installed,false);
 assert.equal(r.first.execution.independent_custody_confirmed,false);
 assert.equal(r.first.execution.authority,'none');
 assert.equal(r.feedback_plan.status,'HELD_PROPOSED_NEXT_RESEARCH');
 assert.equal(r.feedback_plan.new_collection_not_in_initial_query,true);
 assert.equal(r.second.status,'EXECUTED_LOCAL_SOURCE_REVIEW');
 assert.equal(r.second.execution.external_actions,0);
 assert.equal(r.actually_found_new_public_source_collection,true);
 assert.ok(api.calls.some(x=>x.includes('/git/blobs/')));
 assert.equal(r.external_actions,0);
});
test('fresh initial source selection is not the same for unrelated questions',async()=>{
 const api=fakeApi();
 const p=await runOpenField(
  'How does classical planZ use GRAFT to compose an executable capability?',
  {transport:api.transport,secondPass:false});
 assert.equal(p.first.plan.mode,'COMPOSITION');
 assert.equal(p.first.execution.mode,'COMPOSITION');
 assert.equal(p.second,null);
 assert.equal(p.status,'FIRST_INQUIRY_EXECUTED_NEXT_PROPOSED');
 assert.notDeepEqual(p.first.packet.selection.repositories,
  ['the-static-collective/the-daily-slice','the-static-collective/ALEX.2']);
 assert.equal(p.production_installed,false);
});
test('one-source observed gap produces a distinct new classical plan and collection',async()=>{
 const api=fakeApi();
 const r=await runOpenField(seed,{collections:['the-static-collective/the-daily-slice'],
  transport:api.transport});
 assert.equal(r.first.packet.sources.length,1);
 assert.equal(r.feedback_plan.selected_next_discriminator,
  'EXPAND_BOUNDED_PUBLIC_SOURCE_COVERAGE');
 assert.deepEqual(r.feedback_plan.next_source_collections,
  ['the-static-collective/planZ','the-static-collective/GRAFT']);
 assert.equal(r.actually_found_new_public_source_collection,true);
});
test('a declared private repo is refused before it can be queried',async()=>{
 const api=fakeApi();
 await assert.rejects(runOpenField(seed,{
  collections:['the-static-collective/MEMENTO'],
  transport:api.transport}),/UNAUTHORIZED_SOURCE_COLLECTION/);
 assert.equal(api.calls.length,0);
});
test('public-repo metadata that proves PRIVATE stays outside source study',async()=>{
 const api=fakeApi({privateNames:['the-static-collective/the-daily-slice']});
 const r=await runOpenField(seed,{
  collections:['the-static-collective/the-daily-slice'],
  transport:api.transport});
 assert.equal(r.status,'HOLD_SOURCE_ACQUISITION_OR_COVERAGE');
 assert.equal(r.first.packet.sources.length,0);
 assert.match(r.first.packet.errors[0].reason,/NOT_VERIFIED_PUBLIC/);
 assert.equal(r.first.candidate,null);
 assert.equal(r.external_actions,0);
});
test('public body corruption and unverifiable source SHA force HOLD',async()=>{
 const r=await runOpenField(seed,{
  collections:['the-static-collective/the-daily-slice'],
  transport:fakeApi({corrupt:true}).transport});
 assert.equal(r.status,'HOLD_SOURCE_ACQUISITION_OR_COVERAGE');
 assert.equal(r.first.packet.hits.length,0);
 assert.equal(r.first.plan.status,'HOLD_NO_ADMISSIBLE_SOURCE_LEADS');
 assert.equal(r.first.execution,null);
});
test('actual synthetic MADD ride remains preserved but never changes live source authority',async()=>{
 const r=await demonstrate({transport:fakeApi().transport});
 assert.ok(r.premise.original_madd_ride_id.startsWith('ride-'));
 assert.equal(r.experiment.status,'TWO_LIVE_PUBLIC_INQUIRIES_AND_TWO_LOCAL_CAPABILITIES');
 assert.equal(r.experiment.source_custody_proved,false);
 assert.equal(r.experiment.production_installed,false);
});
