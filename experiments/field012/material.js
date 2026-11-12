/* FIELD-012: Source-scoped material candidates, hypothetical use and board placement.
 * NEVER equates photo pixels with plan pixels, and never certifies structural safety.
 */
(function(root){'use strict';
 const ROLES=['boundary_module','support_candidate','flexible_barrier','visual_cue','unknown'];
 const STATUS=['tentative','user_confirmed','user_rejected'];
 const MOBILITY=['unknown','movable','fixed'];
 const hash=s=>typeof s==='string'&&/^[0-9a-f]{64}$/.test(s);
 const numeric=x=>typeof x==='number'&&Number.isFinite(x);
 const bounded=x=>numeric(x)&&x>=0&&x<=1;
 const clone=x=>JSON.parse(JSON.stringify(x));
 function validateMaterial(x){
   if(!x||typeof x.id!=='string'||!/^material-[a-zA-Z0-9_-]{1,80}$/.test(x.id)||
      typeof x.label!=='string'||!x.label.trim()||x.label.length>120||
      !ROLES.includes(x.role)||!STATUS.includes(x.status)||!MOBILITY.includes(x.mobility)||
      x.source_frame!=='photo_normalized'||typeof x.photo_id!=='string'||!x.photo_id||x.photo_id.length>120||
      !hash(x.photo_sha256)||!['HUMAN_REGION_TAG','LOCAL_VLM_TENTATIVE','LOCAL_CV_TENTATIVE'].includes(x.provenance)||
      !Array.isArray(x.bbox)||x.bbox.length!==4||!x.bbox.every(bounded)||
      !(x.bbox[2]-x.bbox[0]>.005&&x.bbox[3]-x.bbox[1]>.005)||
      x.registered_to_sketch!==false||x.certified_safe!==false||
      (x.width!==null&&x.width!==undefined&&(!x.width||!numeric(x.width.value)||x.width.value<=0||x.width.value>1000||
        !['ft','m','cm','in'].includes(x.width.unit)||!['rough_guess','user_measured'].includes(x.width.quality))))
        throw Error('Material candidate has unsupported provenance, geometry, status or measurements');
   return x;
 }
 function validatePacket(packet,photo_id,photo_sha256){
   if(!packet||packet.schema!=='motif.field012.materials.v1'||packet.coordinate_frame!=='photo_normalized'||
      packet.source_kind!=='USER_PHOTO'||packet.photo_id!==photo_id||packet.photo_sha256!==photo_sha256||
      !hash(packet.photo_sha256)||packet.photo_to_sketch_registration!==false||packet.physical_scale_inferred!==false||
      packet.safe_assembly_certified!==false||!Array.isArray(packet.items)||packet.items.length>24)throw Error('Vision packet incompatible with current photo');
   const seen=new Set();
   packet.items.forEach(x=>{
     validateMaterial(x);
     if(x.provenance!=='LOCAL_VLM_TENTATIVE'||x.status!=='tentative'||x.mobility!=='unknown'||
        x.width!==null&&x.width!==undefined||x.photo_sha256!==packet.photo_sha256||x.photo_id!==photo_id||seen.has(x.id))
         throw Error('Model cannot confirm or measure inventory');
     seen.add(x.id);
   });
   return packet;
 }
 function applications(material){
   validateMaterial(material);
   const roles={
     boundary_module:['Test as a movable boundary section','Test a short opening with a rigid candidate'],
     support_candidate:['Examine as a potential support node','Compare a connection with another panel'],
     flexible_barrier:['Investigate a visual infill role','Check snagging, tension and entanglement before use'],
     visual_cue:['Investigate a supervised visual boundary cue','Consider relocating the desired boundary'],
     unknown:['Inspect and identify the object before assigning an engineering role']};
   return {id:material.id,possible_uses:roles[material.role],status:'HYPOTHESES_ONLY',
     risks:['Actual mobility unknown until checked','Joint geometry and strength not validated','Dog entrapment / tipping / sharp-edge hazards not cleared']};
 }
 function ghostPlacement(material,target,center=.5){
   validateMaterial(material);
   if(material.status==='user_rejected'||material.mobility==='fixed')throw Error('Rejected/fixed material is unavailable for move hypotheses');
   if(!target||!['desired','current'].includes(target.kind)||!Array.isArray(target.points)||target.points.length!==2||
      !target.points.every(p=>Array.isArray(p)&&p.length===2&&p.every(bounded))||!numeric(center)||center<.1||center>.9)
      throw Error('Target is not an eligible board trace');
   const [a,b]=target.points;
   // Pure schematic placeholder: 28% of the drawn target, *not* estimated material width.
   const portion=.28, lo=Math.max(0,center-portion/2),hi=Math.min(1,center+portion/2);
   const xy=t=>a.map((v,k)=>Math.max(0,Math.min(1,+(v+(b[k]-v)*t).toFixed(6))));
   const points=material.role==='support_candidate'?[xy(center)]:[xy(lo),xy(hi)];
   return {material_id:material.id,target_id:target.id,points,
     kind:material.role==='support_candidate'?'support':'panel',
     source_frame:'sketch_normalized',
     origin_frame:'photo_normalized',
     status:'HYPOTHETICAL_NOT_FITTED',
     scale:'ILLUSTRATIVE_28_PERCENT_TARGET_NOT_PHYSICAL_SIZE',
     source_box:clone(material.bbox),photo_id:material.photo_id,photo_sha256:material.photo_sha256,
     certified_assembly:false};
 }
 function materialToBoardItem(ghost,material,id){
   validateMaterial(material);
   if(!ghost||ghost.material_id!==material.id||!/^object-[a-zA-Z0-9_-]{1,100}$/.test(id))throw Error('Missing hypothesis or board item identity');
   return {id,kind:ghost.kind,label:material.label+' · tentative',status:'tentative',movable:material.mobility==='movable',points:clone(ghost.points),
     evidence:{kind:'HYPOTHETICAL_PHOTO_OBJECT_PLACEMENT',photo_id:material.photo_id,photo_sha256:material.photo_sha256,
       photo_bbox:clone(material.bbox),material_id:material.id,target_id:ghost.target_id,
       photo_registered_to_plan:false,actual_width_applied:false,physical_fit_verified:false,safe_to_use_verified:false}};
 }
 function nextInteractions(materials,board){
   const active=materials.filter(m=>m.status!=='user_rejected');
   const targets=board.items.filter(i=>i.kind==='desired'&&i.status!=='user_rejected');
   const v=[];
   if(!active.length)v.push({id:'mark-photo',title:'Mark an object directly on a photo',kind:'photo-region',score:100});
   if(active.some(m=>m.role==='unknown'))v.push({id:'identify',title:'Identify what an unclassified object could do',kind:'role',score:96});
   if(active.some(m=>m.mobility==='unknown'))v.push({id:'mobility',title:'Check which pictured materials can actually move',kind:'mobility',score:86});
   if(active.some(m=>!m.width))v.push({id:'material-width',title:'Add an approximate width for one material',kind:'dimension',score:72});
   if(active.length&&!targets.length)v.push({id:'target',title:'Trace the desired route on the sketch',kind:'desired',score:89});
   if(active.length&&targets.length)v.push({id:'preview',title:'Preview a piece against the desired route',kind:'preview',score:77});
   return v.sort((a,b)=>b.score-a.score);
 }
 const api={ROLES,STATUS,MOBILITY,validateMaterial,validatePacket,applications,ghostPlacement,materialToBoardItem,nextInteractions};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 root.MOTIF012=api;
})(typeof window!=='undefined'?window:globalThis);
