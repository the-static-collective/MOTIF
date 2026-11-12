'use strict';
const assert=require('node:assert/strict');
globalThis.MOTIF010=require('../field010/core.js');
const S=require('./scene3d.js');
const {camera,project,rayGround,polygons}=require('./camera3d.js');
let tests=0;function test(name,cb){try{cb();tests++;console.log('PASS',name);}catch(e){console.log('FAIL',name);throw e;}}
const fixture={schema:'motif.field010.v1',base:{source:'synthetic',coordinate_frame:'sketch_normalized',sketch_size:[1000,450],items:[
{id:'line1',kind:'current',label:'old barrier',status:'tentative',movable:true,points:[[.15,.25],[.65,.25]]},
{id:'wish',kind:'desired',label:'desired boundary',status:'tentative',movable:true,points:[[.1,.5],[.7,.5]]},
{id:'post',kind:'support',label:'stake',status:'tentative',movable:false,points:[[.15,.25]]}
]},events:[]};
const model=()=>S.create(fixture);
test('construct from validated FIELD010',()=>{const x=S.build(model());assert.equal(x.objects.length,3);});
test('no fabricated physical scale',()=>{assert.equal(S.build(model()).scale.kind,'diagram_only');assert.equal(S.diagnose(S.build(model())).verified_physical_safety,false);});
test('extruded height is illustrative',()=>{const x=S.build(model());assert.equal(x.objects[0].height_quality,'diagram_assumption');});
test('actual 3D vertices have vertical dimensions',()=>{const x=S.build(model()),p=polygons(x.objects,S,camera(),900,540);assert.ok(p.length>3);assert.ok(p.some(q=>q.points.length===4));});
test('camera perspective responds to changing height',()=>{const c=camera(),p1=project({x:5,y:0,z:2},c,600,500),p2=project({x:5,y:2,z:2},c,600,500);assert.notEqual(p1.y,p2.y);});
test('camera ray meets ground',()=>{const c=camera(),p={x:4,y:0,z:1.8},s=project(p,c,800,500),q=rayGround(s.x,s.y,c,800,500);assert.ok(Math.hypot(q.x-p.x,q.z-p.z)<.00001);});
test('2D crossing can be different elevations',()=>{let m=model();m=S.stamp(m,{type:'position',id:'line1',points:[[.3,.3],[.7,.7]]});m=S.stamp(m,{type:'position',id:'wish',points:[[.3,.7],[.7,.3]]});m=S.stamp(m,{type:'clearance',id:'wish',value:1.5,quality:'human_rough'});const d=S.diagnose(S.build(m));assert.ok(d.issues.some(x=>x.kind==='2D_CROSSING_DIFFERENT_HEIGHT'));});
test('ground gap not hidden by top down map',()=>{let m=S.stamp(model(),{type:'clearance',id:'line1',value:.8,quality:'human_rough'});assert.ok(S.diagnose(S.build(m)).issues.some(x=>x.kind==='GROUND_GAP'));});
test('cannot move fixed support',()=>{assert.throws(()=>S.stamp(model(),{type:'position',id:'post',points:[[.5,.5]]}),/Immovable/);});
test('user edit does not mutate source snapshot',()=>{const m=model(),n=S.stamp(m,{type:'position',id:'line1',points:[[.33,.2],[.55,.2]]});assert.deepEqual(m.original,fixture);assert.deepEqual(n.original,fixture);assert.equal(n.events.length,1);});
test('missing measurements do not calibrate',()=>{const m=model();assert.equal(S.build(m).scale.meters_per_unit,null);});
test('rough guess cannot set physical scale',()=>{assert.throws(()=>S.stamp(model(),{type:'calibrate',known_segment:'line1',meters:2.5,quality:'human_rough',nonuniformity:.35,sketch_proportional:true}),/requires measured/);});
test('refuses one dimension without proportionality',()=>{assert.throws(()=>S.stamp(model(),{type:'calibrate',known_segment:'line1',meters:2.5,quality:'user_measured',nonuniformity:.35,sketch_proportional:false}),/requires measured/);});
test('calibrates only if source measured and approximation declared',()=>{let m=S.stamp(model(),{type:'calibrate',known_segment:'line1',meters:2.5,quality:'user_measured',nonuniformity:.4,sketch_proportional:true});assert.equal(S.build(m).scale.kind,'conditional_reference');assert.equal(S.build(m).scale.nonuniformity,.4);});
test('no photo to map registration',()=>{assert.equal(S.diagnose(S.build(model())).photo_registered,false);});
test('support hypothesis is not structural proof',()=>{const d=S.diagnose(S.build(model()));assert.ok(d.issues.some(x=>x.kind==='STRUCTURAL_HOLD'));});
test('suggestions flagged not certified',()=>{assert.ok(S.alternatives(S.build(model())).every(x=>x.physical_fit_certified===false));});
test('new support is source tagged',()=>{const m=S.stamp(model(),{type:'add_support',id:'human-support-1',point:[.5,.5],label:'chair?'});const x=S.build(m).objects.find(o=>o.id==='human-support-1');assert.equal(x.source,'HUMAN_HYPOTHESIS');});
test('removing source support rejected',()=>{assert.throws(()=>S.stamp(model(),{type:'remove_support',id:'post'}),/Can remove/);});
test('invalid negative height refused',()=>{assert.throws(()=>S.stamp(model(),{type:'height',id:'line1',value:-1,quality:'user_measured'}));});
test('export OBJ includes genuine z and height vertices',()=>{const txt=S.exportObj(S.build(model()));assert.ok(txt.includes('\nf '));assert.ok(txt.includes('\nv '));assert.ok(txt.includes('not actual geometry'));});
test('next best questions include height and scale',()=>{const q=S.nextQuestions(S.build(model()));assert.ok(q.some(x=>x.kind==='height'));assert.ok(q.some(x=>x.kind==='measurement'));});
test('event indexes are append only',()=>{let m=S.stamp(model(),{type:'height',id:'line1',value:2,quality:'human_rough'});m=S.stamp(m,{type:'clearance',id:'line1',value:.2,quality:'human_rough'});assert.deepEqual(m.events.map(x=>x.index),[1,2]);});
console.log(`PASS ${tests} FIELD-014 tests`);
