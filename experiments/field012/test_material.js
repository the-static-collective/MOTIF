const assert=require('assert');
const X=require('./material.js');
const M=require('../field010/core.js');
const base={schema:'motif.field010.v1',base:{source:'synthetic',coordinate_frame:'sketch_normalized',sketch_size:[1000,450],items:[
  {id:'desired',kind:'desired',status:'tentative',label:'Desired route',movable:false,points:[[.1,.4],[.8,.4]]},
  {id:'existing',kind:'current',status:'tentative',label:'Current fence',movable:true,points:[[.1,.1],[.8,.1]]}
]},events:[]};
let n=0;function test(label,fn){fn();console.log('ok',++n,label);}
const sha='a'.repeat(64);
const mat={id:'material-photo-01',label:'Cage panel',role:'boundary_module',status:'tentative',mobility:'unknown',
 source_frame:'photo_normalized',photo_id:'photo-0',photo_sha256:sha,bbox:[.1,.2,.6,.8],
 provenance:'LOCAL_VLM_TENTATIVE',registered_to_sketch:false,certified_safe:false,width:null};
const packet={schema:'motif.field012.materials.v1',coordinate_frame:'photo_normalized',source_kind:'USER_PHOTO',photo_id:'photo-0',photo_sha256:sha,
 photo_to_sketch_registration:false,physical_scale_inferred:false,safe_assembly_certified:false,items:[mat]};
test('accept bounded vision packet',()=>assert.equal(X.validatePacket(packet,'photo-0',sha),packet));
test('wrong photograph held',()=>assert.throws(()=>X.validatePacket(packet,'photo-1',sha)));
test('wrong pixel digest held',()=>assert.throws(()=>X.validatePacket(packet,'photo-0','b'.repeat(64))));
test('model cannot pretend user confirmation',()=>assert.throws(()=>X.validatePacket({...packet,items:[{...mat,status:'user_confirmed'}]},'photo-0',sha)));
test('model cannot assert measurement',()=>assert.throws(()=>X.validatePacket({...packet,items:[{...mat,width:{value:4,unit:'ft',quality:'user_measured'}}]},'photo-0',sha)));
test('model cannot forge photo coordinates into plan',()=>assert.throws(()=>X.validatePacket({...packet,photo_to_sketch_registration:true},'photo-0',sha)));
test('negative size box held',()=>assert.throws(()=>X.validateMaterial({...mat,bbox:[.5,.5,.3,.7]})));
test('unscaled board placement has separate evidence',()=>{
 const g=X.ghostPlacement(mat,base.base.items[0]);assert.equal(g.scale,'ILLUSTRATIVE_28_PERCENT_TARGET_NOT_PHYSICAL_SIZE');
 assert.equal(g.origin_frame,'photo_normalized');assert.equal(g.source_frame,'sketch_normalized');
 const i=X.materialToBoardItem(g,mat,'object-trial01');assert.equal(i.status,'tentative');
 assert.equal(i.evidence.photo_registered_to_plan,false);assert.equal(i.evidence.physical_fit_verified,false);
});
test('support candidate yields point ghost',()=>{
 const g=X.ghostPlacement({...mat,role:'support_candidate'},base.base.items[0]);assert.equal(g.points.length,1);assert.equal(g.kind,'support');
});
test('fixed and rejected candidates held for placement',()=>{
 for (const x of [{...mat,mobility:'fixed'},{...mat,status:'user_rejected'}])assert.throws(()=>X.ghostPlacement(x,base.base.items[0]));
});
test('not a movement from photo to map',()=>{
 assert.throws(()=>X.ghostPlacement(mat,{kind:'panel',points:[[.1,.2],[.5,.3]]}));
});
test('core records human/machine materials separately',()=>{
 const p=JSON.parse(JSON.stringify(base));p.events=[{type:'material_add',id:'event-1',material:mat}];const st=M.replay(p);
 assert.equal(st.materials.length,1);assert.equal(st.items.length,2);assert.equal(st.materials[0].photo_sha256,sha);
 assert(M.computeSolver(st).materialSuggestions.length>0);
 assert(M.computeInterface(st).actions.some(x=>x.tool==='material-preview'));
});
test('core update preserves original photo evidence',()=>{
 const p=JSON.parse(JSON.stringify(base));p.events=[{type:'material_add',id:'event-1',material:mat},
  {type:'material_set',id:'event-2',target:mat.id,prop:'status',value:'user_confirmed'},
  {type:'material_set',id:'event-3',target:mat.id,prop:'mobility',value:'movable'}];
 const st=M.replay(p);assert.equal(st.materials[0].status,'user_confirmed');assert.equal(st.materials[0].mobility,'movable');
 assert.equal(st.materials[0].provenance,'LOCAL_VLM_TENTATIVE');
});
test('core rejects forged confirmation as new object',()=>{
 const p=JSON.parse(JSON.stringify(base));p.events=[{type:'material_add',id:'e',material:{...mat,photo_sha256:'none'}}];assert.throws(()=>M.replay(p));
});
test('core revert restores material prior',()=>{
 const p=JSON.parse(JSON.stringify(base));p.events=[{type:'material_add',id:'e0',material:mat},
 {type:'material_set',id:'e1',target:mat.id,prop:'mobility',value:'movable'},
 {type:'revert',id:'e2',target_event:'e1'}];assert.equal(M.replay(p).materials[0].mobility,'unknown');
});
test('uncertainty-first interface asks for a visible object',()=>{
 const st=M.replay(base);assert(X.nextInteractions(st.materials,st).some(x=>x.kind==='photo-region'));
});
test('material role is possible use, not certification',()=>{
 const a=X.applications(mat);assert.equal(a.status,'HYPOTHESES_ONLY');assert.equal(a.risks.length,3);
});
test('single source bounding box remains normalized to photo',()=>{
 const g=X.ghostPlacement(mat,base.base.items[0]);assert.deepEqual(g.source_box,mat.bbox);
});
console.log(`${n} FIELD-012 JavaScript assertions passed.`);
