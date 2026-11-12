const assert=require('node:assert/strict');
const {scanRGBA,materialRegion,iou}=require('./scan.js');
const M=require('../field012/material.js');
const Core=require('../field010/core.js');
const Plan=require('./plan.js');
function img(w=192,h=144,shape=true){
 const a=new Uint8ClampedArray(w*h*4);
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){
   const j=(y*w+x)*4;
   let c=shape&&x>35&&x<135&&y>20&&y<120?32:215;
   if(shape && x>35&&x<135 && y>20&&y<120 &&((x%11===0)||(y%16===0)))c=170;
   a[j]=c;a[j+1]=c;a[j+2]=c;a[j+3]=255;
 }
 return a;
}
const hash='a'.repeat(64);
const re=scanRGBA(img(),192,144);
assert.ok(re.length>0,'must return nonempty visual-region proposals on structured synthetic image');
assert.ok(re.every(x=>x.kind==='VISUAL_REGION_NOT_OBJECT_IDENTIFIED'));
assert.ok(re.every(x=>x.bbox.every(v=>v>=0&&v<=1)));
assert.ok(re.length<=5);
assert.deepEqual(scanRGBA(img(),192,144),re,'should be deterministic');
assert.ok(iou([.1,.1,.2,.2],[.1,.1,.2,.2])>.99);
assert.equal(iou([0,0,.2,.2],[.5,.5,.7,.7]),0);
const packet=materialRegion(re[0],'photo-0',hash,'material-cv-1');
M.validateMaterial(packet);
const state={items:[{id:'target',kind:'desired',points:[[.1,.1],[.4,.4]],status:'tentative'}],materials:[packet]};
assert.deepEqual(Plan.evaluate(state).candidates.map(x=>x.material_id).filter(Boolean),[],
 'unclassified pixel regions cannot become planned fence pieces');
assert.ok(Plan.evaluate(state).questions.length>0);
packet.role='boundary_module';
assert.equal(Plan.evaluate(state).candidates[0].material_id,packet.id);
assert.equal(Plan.evaluate(state).candidates[0].physical_scale_known,false);
assert.equal(Plan.evaluate(state).real_fitted_layouts,0);
assert.equal(Plan.evaluate(state).automatic_safety_clearances,0);
assert.equal(Plan.evaluate(state).unconfirmed_photo_map_matches,0);
const fixed={...packet,mobility:'fixed'};
assert.equal(Plan.evaluate({...state,materials:[fixed]}).candidates.filter(x=>x.material_id).length,0);
assert.throws(()=>scanRGBA(new Uint8Array(5),192,144));
assert.throws(()=>materialRegion(re[0],'photo-0','bad','material-cv-1'));
assert.throws(()=>Plan.evaluate({items:[],materials:[{...packet,role:'teleport'}]}));
console.log('FIELD-013: 17 source, safety, deterministic behavior, and alternative-layout assertions passed');
