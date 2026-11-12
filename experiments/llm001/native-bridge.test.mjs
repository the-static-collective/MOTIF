import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {rank,available} from './loom.mjs';
const field=()=>({schema:'motif.llm001.world.v0',id:'field-native-bridge',
 facts:['diagram_exists'],unknown:['gap_measured','height_measured'],
 evidence:[{id:'sketch',root:'author-fixture',kind:'observed',fact:'diagram_exists'},
  {id:'gap',root:'missing-1',kind:'unknown',fact:'gap_measured'},
  {id:'height',root:'missing-2',kind:'unknown',fact:'height_measured'}],
 moves:[
  {id:'annotate',kind:'simulate',requires:['diagram_exists'],may_grant:['note_added'],immediate:9},
  {id:'measure-gap',kind:'probe',requires:['diagram_exists'],may_grant:['gap_measured'],immediate:1},
  {id:'measure-height',kind:'probe',requires:['diagram_exists'],may_grant:['height_measured'],immediate:2},
  {id:'check-clearance',kind:'simulate',requires:['gap_measured'],may_grant:['clearance_hypothesis'],immediate:0},
  {id:'choose-route',kind:'simulate',requires:['clearance_hypothesis','height_measured'],may_grant:['tentative_route'],immediate:0},
  {id:'build',kind:'external',requires:['tentative_route'],may_grant:['physical_construction'],immediate:500}
 ],history:[]});
test('actual original Python MOTIF-003 agrees on source-scoped first move',()=>{
 const w=field(),r=spawnSync('python3',['experiments/llm001/native_bridge.py'],
    {input:JSON.stringify(w),encoding:'utf8',timeout:10000});
 assert.equal(r.status,0,r.stderr);
 const output=JSON.parse(r.stdout);
 assert.equal(output.native,'experiments/003/affordance.py');
 assert.match(output.source_sha256,/^[0-9a-f]{64}$/);
 assert.equal(output.preferred,'measure-gap');
 assert.equal(rank(w,'affordance',['tentative_route']).preferred.id,output.preferred);
 assert(output.ranked.some(x=>x.move==='measure-gap'&&x.new_choices>=1));
 assert(!output.ranked.some(x=>x.move==='build'));
});
test('original native bridge rejects fake schema before native execution',()=>{
 const w=field();w.schema='invented';
 const r=spawnSync('python3',['experiments/llm001/native_bridge.py'],
    {input:JSON.stringify(w),encoding:'utf8',timeout:10000});
 assert.notEqual(r.status,0);assert.match(r.stderr,/BAD_FIXTURE/);
});
