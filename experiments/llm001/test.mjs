import test from 'node:test';
import assert from 'node:assert/strict';
import {valid,available,imagined,search,rank,compile,gate,ownerTest,field014Aperture,keyOf,counterfactualImpact} from './loom.mjs';

const field = () => ({
 schema:'motif.llm001.world.v0',id:'field014-fixture',
 facts:['diagram_exists'],unknown:['gap_measured','height_measured','load_certified'],
 evidence:[
  {id:'sketch',root:'original-sketch',kind:'observed',fact:'diagram_exists'},
  {id:'gap',root:'measurement-missing-gap',kind:'unknown',fact:'gap_measured'},
  {id:'height',root:'measurement-missing-height',kind:'unknown',fact:'height_measured'},
  {id:'height-duplicate',root:'measurement-missing-height',kind:'unknown',fact:'height_measured'},
  {id:'strength',root:'unverified-engineering',kind:'unknown',fact:'load_certified'}
 ],
 moves:[
  {id:'annotate',kind:'simulate',requires:['diagram_exists'],may_grant:['note_added'],immediate:9},
  {id:'measure-gap',kind:'probe',requires:['diagram_exists'],may_grant:['gap_measured'],immediate:1},
  {id:'measure-height',kind:'probe',requires:['diagram_exists'],may_grant:['height_measured'],immediate:2},
  {id:'check-clearance',kind:'simulate',requires:['gap_measured'],may_grant:['clearance_hypothesis'],immediate:0},
  {id:'choose-route',kind:'simulate',requires:['clearance_hypothesis','height_measured'],may_grant:['tentative_route'],immediate:0},
  {id:'build-fence',kind:'external',requires:['tentative_route','load_certified'],may_grant:['actual_fence'],immediate:100}
 ],history:[]
});
const gym = () => ({
 schema:'motif.llm001.world.v0',id:'gym-fixture',facts:['action_blocked'],
 unknown:['new_tool_selected'],evidence:[
  {id:'native-failure',root:'native-owner-step1',kind:'observed',fact:'action_blocked'},
  {id:'missing-tool',root:'missing-inventory-trace',kind:'unknown',fact:'new_tool_selected'}
 ],
 moves:[
  {id:'give-up',kind:'simulate',requires:['action_blocked'],may_grant:['abandoned'],immediate:5},
  {id:'select-new-tool',kind:'probe',requires:['action_blocked'],may_grant:['new_tool_selected'],immediate:1},
  {id:'retry-blocked',kind:'simulate',requires:['new_tool_selected'],may_grant:['subgoal_recovered'],immediate:0},
  {id:'resume-original',kind:'simulate',requires:['subgoal_recovered'],may_grant:['goal_reached'],immediate:0}
 ],history:[]
});
const community = () => ({
 schema:'motif.llm001.world.v0',id:'community-fixture',facts:['neighbor_requested_help'],
 unknown:['steward_opted_in'],evidence:[
  {id:'request',root:'request-a',kind:'observed',fact:'neighbor_requested_help'},
  {id:'consent',root:'missing-permission',kind:'unknown',fact:'steward_opted_in'}
 ],moves:[
  {id:'draft-ask',kind:'probe',requires:['neighbor_requested_help'],may_grant:['steward_opted_in'],immediate:0},
  {id:'draft-match',kind:'simulate',requires:['steward_opted_in'],may_grant:['match_ready_for_review'],immediate:1},
  {id:'send-money',kind:'external',requires:['match_ready_for_review'],may_grant:['payment_sent'],immediate:999}
 ],history:[]
});

test('schema source evidence required and unique',()=>{
 assert.equal(valid(field()).id,'field014-fixture');
 const w=field();w.evidence.push({...w.evidence[0]});assert.throws(()=>valid(w),/DUPLICATE_ID/);
 const z=field();z.evidence[0].fact='invented';assert.throws(()=>valid(z),/INVALID_EVIDENCE/);
});
test('reject observed/unknown contradiction',()=>{
 const w=field();w.facts.push('gap_measured');assert.throws(()=>valid(w),/INVALID_WORLD/);
});
test('real installation never enters available moves',()=>{
 assert(!available(field()).some(m=>m.id==='build-fence'));
 const w=field();w.facts.push('tentative_route','load_certified');w.unknown=w.unknown.filter(x=>!w.facts.includes(x));w.evidence=w.evidence.filter(e=>e.kind!=='unknown'||!w.facts.includes(e.fact));
 assert(!available(w).some(m=>m.id==='build-fence'));
});
test('native style blocked action: new action appears after hypothetical tool selection',()=>{
 const w=gym();
 assert(!available(w).some(m=>m.id==='retry-blocked'));
 assert(available(imagined(w,w.moves[1])).some(m=>m.id==='retry-blocked'));
 assert(!w.facts.includes('new_tool_selected'));
});
test('myopic action may disagree with action-affordance ranking',()=>{
 assert.equal(rank(field(),'greedy',['tentative_route']).preferred.id,'annotate');
 assert.equal(rank(field(),'affordance',['tentative_route']).preferred.id,'measure-gap');
});
test('strong classical search is explicit and allowed to tie or beat MOTIF-style policy',()=>{
 const w=gym();assert.deepEqual(search(w,['goal_reached'],3),['select-new-tool','retry-blocked','resume-original']);
 assert.equal(rank(w,'classical',['goal_reached'],3).preferred.id,'select-new-tool');
});
test('rank does not imply model generated a new operator',()=>{
 const r=rank(field(),'affordance',['tentative_route']);assert.equal(r.rows.length,3);
 assert(r.rows.every(x=>available(field()).some(m=>m.id===x.id)));
});
test('compiler deduplicates root rather than counting echoed sources',()=>{
 const p=compile(field(),{budget:8});const a=p.packet.witnesses;
 assert.equal(a.filter(e=>e.root==='measurement-missing-height').length,1);
 assert(p.omitted.some(e=>e.reason==='SAME_ORIGIN'));
});
test('unknown facts survive prompt compaction and exhausted budget causes HOLD',()=>{
 const p=compile(field(),{budget:1});assert.equal(p.packet.status,'HOLD_MISSING_UNKNOWNS');
 assert(p.packet.unknown_facts.includes('load_certified'));
});
test('prompt gives structured choices and deterministic reusable cache key',()=>{
 const a=compile(gym(),{budget:4,goal:['goal_reached']}),b=compile(gym(),{budget:4,goal:['goal_reached']});
 assert.equal(a.cache_key,b.cache_key);assert(a.pseudo_tokens>0);
 assert(a.packet.possible_moves.some(m=>m.id==='select-new-tool'));
 assert.equal(a.packet.task.includes('real act'),true);
});
test('cache key is not claimed cryptographic source authority',()=>{
 assert.match(keyOf({a:1}),/^cache-only:/);
 assert.notEqual(keyOf({a:1}),keyOf({a:2}));
});
test('invalid model result is rejected, not applied',()=>{
 const w=community(),c=compile(w);
 assert.equal(gate(w,c,{action_id:'send-money',cite:['request'],hypothesis:'do it'}).status,'REJECT_NOT_AVAILABLE');
 assert.equal(gate(w,c,{action_id:'draft-ask',cite:['invented'],hypothesis:'ask'}).status,'REJECT_UNSOURCED');
 assert.equal(gate(w,c,{action_id:'draft-ask',cite:[],hypothesis:'ask'}).status,'REJECT_FORMAT');
 assert.deepEqual(w.history,[]);
});
test('model proposal is PENCIL even with valid evidence',()=>{
 const w=community(),c=compile(w),p=gate(w,c,{action_id:'draft-ask',cite:['request'],hypothesis:'Permission could unlock a draft match.'});
 assert.equal(p.status,'PENCIL_REVIEW_ONLY');assert.equal(p.receipt,'NO_STATE_CHANGE');
 assert.equal(w.history.length,0);
});
test('cannot bypass incomplete context by citing known evidence',()=>{
 const w=field(),p=compile(w,{budget:1});
 assert.equal(gate(w,p,{action_id:'measure-gap',cite:['sketch'],hypothesis:'measure'}).status,'HOLD_CONTEXT');
});
test('synthetic owner receipt advances fork, never original',()=>{
 const w=community(),c=compile(w),p=gate(w,c,{action_id:'draft-ask',cite:['request'],hypothesis:'ask'});
 const next=ownerTest(w,p,{id:'owner-001',authority:'INDEPENDENT_SYNTHETIC_TEST_OWNER',action_id:'draft-ask',passed:true,grants:['steward_opted_in']});
 assert(!w.facts.includes('steward_opted_in'));assert.equal(w.history.length,0);
 assert(next.facts.includes('steward_opted_in'));assert(available(next).some(m=>m.id==='draft-match'));
 assert(!available(next).some(m=>m.id==='send-money'));
 assert(next.history[0].scope==='SIMULATION_ONLY');
});
test('no state mutation on a negative owner test',()=>{
 const w=gym(),c=compile(w),p=gate(w,c,{action_id:'select-new-tool',cite:['native-failure'],hypothesis:'try'});
 const next=ownerTest(w,p,{id:'owner-neg',authority:'INDEPENDENT_SYNTHETIC_TEST_OWNER',action_id:'select-new-tool',passed:false,grants:[]});
 assert.deepEqual(next.facts,w.facts);assert.equal(next.history.length,1);
});
test('reject unsanctioned new facts or forged owner',()=>{
 const w=community(),c=compile(w),p=gate(w,c,{action_id:'draft-ask',cite:['request'],hypothesis:'ask'});
 assert.throws(()=>ownerTest(w,p,{id:'owner-003',authority:'MODEL',action_id:'draft-ask',passed:true,grants:['steward_opted_in']}),/RECEIPT_HOLD/);
 assert.throws(()=>ownerTest(w,p,{id:'owner-004',authority:'INDEPENDENT_SYNTHETIC_TEST_OWNER',action_id:'draft-ask',passed:true,grants:['paid_money']}),/RECEIPT_HOLD/);
 assert.throws(()=>ownerTest(w,p,{id:'owner-005',authority:'INDEPENDENT_SYNTHETIC_TEST_OWNER',action_id:'draft-ask',passed:false,grants:['steward_opted_in']}),/RECEIPT_HOLD/);
});
test('duplicate owner receipt is not reusable',()=>{
 const w=community(),c=compile(w),p=gate(w,c,{action_id:'draft-ask',cite:['request'],hypothesis:'ask'});
 const receipt={id:'owner-repeat',authority:'INDEPENDENT_SYNTHETIC_TEST_OWNER',action_id:'draft-ask',passed:false,grants:[]};
 const next=ownerTest(w,p,receipt);assert.throws(()=>ownerTest(next,p,receipt),/RECEIPT_HOLD/);
});
test('FIELD-014 adapter cannot infer physical safety or measured dimensions',()=>{
 const a=field014Aperture({schema:'motif.field014.v1',events:[],scale:{kind:'diagram_only'}});
 assert.equal(a.source_kind,'UNMERGED_SEPARATE_DIAGRAM');assert.equal(a.measured_reference,false);
 assert.equal(a.physical_load_certified,false);assert.equal(a.assembly_authorized,false);
});
test('conditional reference is still not a construction permit',()=>{
 const a=field014Aperture({schema:'motif.field014.v1',events:[{type:'height'}],scale:{kind:'conditional_reference',meters_per_unit:1.2}});
 assert(a.measured_reference);assert(!a.physical_load_certified);
 assert.throws(()=>field014Aperture({schema:'fake',events:[],scale:{kind:'diagram_only'}}),/NOT_FIELD014/);
});

test('counterfactual impact is real two-step graph difference, not topical word count',()=>{
 const w=field();
 const diagram=w.evidence.find(e=>e.id==='sketch'),weight=w.evidence.find(e=>e.id==='strength');
 assert(counterfactualImpact(w,diagram)>counterfactualImpact(w,weight));
 assert.equal(counterfactualImpact(w,weight),0);
 assert(compile(w).packet.witnesses.some(e=>e.counterfactual_action_impact>0));
});
test('tentative assumed information never silently becomes observed in counterfactual',()=>{
 const w=field();w.evidence.push({id:'assumption',root:'author-guess',kind:'assumed',fact:'future_part'});
 assert.doesNotThrow(()=>compile(w));
 assert(!w.facts.includes('future_part'));
});
