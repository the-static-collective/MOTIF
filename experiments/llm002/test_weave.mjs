import test from 'node:test';
import assert from 'node:assert/strict';
import {weave} from './weave.mjs';

function fixture(){
 return {schema:'motif.llm001.world.v0',id:'fixture-shared-scene',fixture_only:true,
   facts:['question_received','tool_selected','steward_opted_in'],
   unknown:['route_verified'],
   evidence:[
     {id:'observed-question',root:'fixture-original-request',kind:'observed',fact:'question_received'},
     {id:'observed-tool',root:'fixture-tool-inventory',kind:'observed',fact:'tool_selected'},
     {id:'observed-consent',root:'fixture-consent',kind:'observed',fact:'steward_opted_in'},
     {id:'missing-route',root:'fixture-unmeasured-route',kind:'unknown',fact:'route_verified'}],
   moves:[
     {id:'scan-layout',kind:'probe',requires:['question_received'],may_grant:['route_verified'],immediate:1},
     {id:'test-tool',kind:'simulate',requires:['tool_selected'],may_grant:['potential-repair'],immediate:2},
     {id:'simulate-invite',kind:'simulate',requires:['steward_opted_in'],may_grant:['draft-invite'],immediate:1},
     {id:'publish-now',kind:'external',requires:['draft-invite'],may_grant:['public-action'],immediate:1000}],
   history:[]};
}
test('default no-consent never invokes computation',()=>{
 let called=0;
 const r=weave(fixture(),{runner:()=>{called++;throw Error('should not run')}});
 assert.equal(r.status,'HOLD_NO_OFFLINE_MODEL_CONSENT');
 assert.equal(called,0);
});
test('non-fixture data cannot enter synthetic model',()=>{
 const w=fixture();delete w.fixture_only;
 assert.equal(weave(w,{consent:true}).status,'HOLD_NON_FIXTURE_DATA');
});
test('wrong cache tenant name fails closed',()=>{
 assert.equal(weave(fixture(),{consent:true,tenant:'private:someone'}).status,'HOLD_SCOPE');
});
test('numeric causal attention branches are sourced, equal and PENCIL only',()=>{
 const w=fixture(),before=JSON.stringify(w);
 const r=weave(w,{consent:true,tenant:'fixture-one',goal:['route_verified']});
 assert.equal(r.status,'PENCIL_PARALLEL_FORKS_ONLY');
 assert.equal(r.forks.length,3);
 assert(r.forks.every(f=>f.status==='PENCIL_SCORE_ONLY'&&f.cached_vs_full_delta<1e-11));
 assert(r.attention_qk_shared<r.attention_qk_full);
 assert.equal(r.side_effects,0);
 assert.equal(r.model_real,false);
 assert.equal(r.review_required,true);
 assert(!r.forks.some(x=>x.id==='publish-now'));
 assert.equal(JSON.stringify(w),before);
});
test('a changed source witness invalidates source-root identity',()=>{
 const w=fixture(),a=weave(w,{consent:true});
 w.evidence[0].root='fixture-changed-original-witness';
 const b=weave(w,{consent:true});
 assert.equal(a.status,'PENCIL_PARALLEL_FORKS_ONLY');
 assert.equal(b.status,'PENCIL_PARALLEL_FORKS_ONLY');
 assert.notEqual(a.source_root,b.source_root);
});
test('branch choices obey max fork budget',()=>{
 const r=weave(fixture(),{consent:true,maxForks:2});
 assert.equal(r.forks.length,2);
});
test('a missing unknown source enforces HOLD before running subprocess',()=>{
 const w=fixture();let called=0;
 const r=weave(w,{consent:true,budget:1,runner:()=>{called++;throw Error('should not run')}});
 assert.equal(r.status,'HOLD_INCOMPLETE_EVIDENCE');
 assert.equal(called,0);
});
test('cannot smuggle external move via a fabricated engine result',()=>{
 const r=weave(fixture(),{consent:true,runner:()=>({status:0,stdout:JSON.stringify({
   schema:'motif.llm002.weave-result.v0',world_id:'fixture-shared-scene',
   source_root:'forged',decision_authority:'NONE',external_actions:false,
   verified_equal:true,forks:[{id:'publish-now',status:'PENCIL_SCORE_ONLY',latent_logit:999,cached_vs_full_delta:0}]
 })})});
 assert.equal(r.status,'HOLD_INVALID_ENGINE_RECEIPT');
});
test('missing Python runtime produces HOLD rather than fake model numbers',()=>{
 const r=weave(fixture(),{consent:true,runner:()=>({status:1,stderr:'missing'})});
 assert.equal(r.status,'HOLD_NUMERIC_ENGINE');
});
test('no model-generated fact enters original source record',()=>{
 const w=fixture(),r=weave(w,{consent:true});
 assert.equal(r.status,'PENCIL_PARALLEL_FORKS_ONLY');
 assert.deepEqual(w.facts,['question_received','tool_selected','steward_opted_in']);
 assert.equal(w.history.length,0);
});
