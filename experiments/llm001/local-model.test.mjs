import test from 'node:test';
import assert from 'node:assert/strict';
import {compile} from './loom.mjs';
import {loopbackURL,parseProposal,proposeLocal} from './local-model.mjs';
const w=()=>({schema:'motif.llm001.world.v0',id:'local-model-fixture',facts:['question_received'],
  unknown:['answer_verified'],evidence:[
    {id:'q1',root:'public-fixture-question',kind:'observed',fact:'question_received'},
    {id:'q2',root:'missing-public-answer',kind:'unknown',fact:'answer_verified'}],
  moves:[{id:'test-answer',kind:'probe',requires:['question_received'],may_grant:['answer_verified'],immediate:1},
         {id:'publish-answer',kind:'external',requires:['answer_verified'],may_grant:[],immediate:99}],history:[]});
test('no local call without explicit opt-in',async()=>{
 let called=0;const x=w(),r=await proposeLocal({world:x,compiled:compile(x),model:'mock:small',
  fetchImpl:async()=>{called++;throw Error('should not call');}});
 assert.equal(r.status,'HOLD_NO_LOCAL_MODEL_CONSENT');assert.equal(called,0);
});
test('loopback URL allowlist rejects external origins, userinfo, alternate paths',()=>{
 assert.equal(loopbackURL('http://127.0.0.1:11434/api/chat'),'http://127.0.0.1:11434/api/chat');
 for(const s of ['https://localhost/api/chat','http://127.0.0.2/api/chat',
   'http://example.com/api/chat','http://foo@localhost/api/chat','http://localhost/other',
   'http://localhost/api/chat?secret=1'])assert.throws(()=>loopbackURL(s));
});
test('strict JSON rejects prose, markdown and extra fields',()=>{
 assert.deepEqual(parseProposal('{"action_id":"a","cite":["b"],"hypothesis":"c"}'),
 {action_id:'a',cite:['b'],hypothesis:'c'});
 for(const x of ['Here is JSON: {"action_id":"a"}','MARKDOWN NOT JSON','{"action_id":"a","proof":"done"}','[{}]'])
   assert.throws(()=>parseProposal(x));
});
test('local model request is scoped and returns PENCIL only',async()=>{
 const x=w(),p=compile(x);let sent;
 const f=async(url,req)=>{
   sent={url,req:JSON.parse(req.body)};
   return {ok:true,json:async()=>({message:{content:JSON.stringify(
      {action_id:'test-answer',cite:['q1'],hypothesis:'Try verifying the public fixture.'})}})};
 };
 const out=await proposeLocal({world:x,compiled:p,consent:true,model:'mock:small',fetchImpl:f});
 assert.equal(sent.url,'http://127.0.0.1:11434/api/chat');
 assert.equal(sent.req.stream,false);assert.equal(sent.req.options.temperature,0);
 assert.equal(sent.req.messages[0].role,'system');assert.equal(sent.req.messages[1].role,'user');
 assert.equal(out.status,'PENCIL_REVIEW_ONLY');assert.equal(x.history.length,0);
});
test('model cannot turn external act into available action',async()=>{
 const x=w(),p=compile(x),f=async()=>({ok:true,json:async()=>({message:{content:
  '{"action_id":"publish-answer","cite":["q1"],"hypothesis":"do it"}'}})});
 const r=await proposeLocal({world:x,compiled:p,consent:true,model:'mock',fetchImpl:f});
 assert.equal(r.status,'REJECT_NOT_AVAILABLE');
});
test('model cannot claim non-existent witness',async()=>{
 const x=w(),p=compile(x),f=async()=>({ok:true,json:async()=>({message:{content:
  '{"action_id":"test-answer","cite":["madeup"],"hypothesis":"test"}'}})});
 const r=await proposeLocal({world:x,compiled:p,consent:true,model:'mock',fetchImpl:f});
 assert.equal(r.status,'REJECT_UNSOURCED');
});
test('truncated unknown context blocks model request',async()=>{
 const x=w(),p=compile(x,{budget:1});let count=0;
 const f=async()=>{count++;throw Error('must hold');};
 const r=await proposeLocal({world:x,compiled:p,consent:true,model:'mock',fetchImpl:f});
 assert.equal(r.status,'HOLD_CONTEXT_NO_MODEL_CALL');assert.equal(count,0);
});
test('transport and malformed generated output hold',async()=>{
 const x=w(),p=compile(x),a=await proposeLocal({world:x,compiled:p,consent:true,model:'mock',
  fetchImpl:async()=>({ok:false})});
 assert.equal(a.status,'HOLD_MODEL_TRANSPORT');
 const b=await proposeLocal({world:x,compiled:p,consent:true,model:'mock',
  fetchImpl:async()=>({ok:true,json:async()=>({message:{content:'not-json'}})})});
 assert.equal(b.status,'HOLD_MODEL_FORMAT_OR_EVIDENCE');
});
