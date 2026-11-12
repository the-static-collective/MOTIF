/* FIELD-014. A 3-D counterfactual scene. No photo -> yard pose, physical
 * scale, inferred height or mechanical safety claim is implicit here. */
(function (root) {'use strict';
 const TYPES = new Set(['current','desired','panel','support','access']);
 const QUAL = new Set(['diagram_assumption','human_rough','user_measured']);
 const finite = n=>typeof n==='number'&&Number.isFinite(n);
 const clamp = (x,a,b)=>Math.min(b,Math.max(a,x));
 const world = p=>({x:p[0]*10,z:p[1]*4.5});
 const toNorm = p=>[clamp(p.x/10,0,1),clamp(p.z/4.5,0,1)];
 const length = p=>p.length<2?0:Math.hypot((p[1][0]-p[0][0])*10,(p[1][1]-p[0][1])*4.5);
 function checkProject(project){
   if(!root.MOTIF010 || typeof root.MOTIF010.replay!=='function')throw Error('FIELD-010 core is required');
   return root.MOTIF010.replay(project);
 }
 function create(project){
   checkProject(project);
   return {schema:'motif.field014.v1',original:JSON.parse(JSON.stringify(project)),events:[],
     scale:{kind:'diagram_only',meters_per_unit:null,source:null,nonuniformity:null},
     source_note:'Original sketch and photos are separate coordinate frames. 3D extrusion is illustrative, not measured.'};
 }
 function validate(model){
   if(!model||model.schema!=='motif.field014.v1'||!Array.isArray(model.events)||model.events.length>3000)throw Error('Invalid FIELD-014 record');
   checkProject(model.original);
   const undone=new Set();
   model.events.forEach((e,i)=>{
     if(!e||!['position','height','clearance','thickness','annotation','calibrate','add_support','add_barrier','remove_support','confirm','revert'].includes(e.type)||e.index!==i+1)throw Error('Invalid event record');
     if(e.type==='revert'){
       if(!Number.isInteger(e.target_index)||e.target_index<1||e.target_index>i||
          model.events[e.target_index-1]?.type==='revert'||undone.has(e.target_index))throw Error('Invalid compensating event');
       undone.add(e.target_index);
     }
   });
   return model;
 }
 function build(model){
   validate(model);
   const state=checkProject(model.original), supports={};
   const reverted=new Set(model.events.filter(e=>e.type==='revert').map(e=>e.target_index));
   const objs = new Map();
   for(const it of state.items){
     if(!TYPES.has(it.kind)||it.status==='user_rejected')continue;
     objs.set(it.id, {id:it.id,label:it.label,kind:it.kind,points:it.points.map(p=>[...p]),movable:it.movable,
       status:it.status,source:'FIELD-010-'+it.id,
       height:it.kind==='support'?1.3:it.kind==='access'?0:1.1,
       clearance:0,thickness:it.kind==='support'?.13:.08,
       height_quality:'diagram_assumption',clearance_quality:'diagram_assumption',
       notes:'Default values are diagram units only. Not measured.'});
   }
   let scale={kind:'diagram_only',meters_per_unit:null,source:null,nonuniformity:null};
   for(const e of model.events){
     if(e.type==='revert'||reverted.has(e.index))continue;
     if(e.type==='calibrate'){
       if(e.known_segment===null){scale={kind:'diagram_only',meters_per_unit:null,source:null,nonuniformity:null};continue;}
       const o=objs.get(e.known_segment);
       if(!o||o.points.length!==2||!finite(e.meters)||e.meters<=0||e.meters>10000 ||!finite(e.nonuniformity)||e.nonuniformity<0||e.nonuniformity>.85||e.quality!=='user_measured' ||!e.sketch_proportional)
         throw Error('Scale requires measured reference, source-consistent segment and explicit sketch assumption');
       scale={kind:'conditional_reference',meters_per_unit:e.meters/length(o.points),source:o.id,nonuniformity:e.nonuniformity};
       continue;
     }
     if(e.type==='add_barrier'){
       if(!e.id||!/^stage-[0-9]{1,4}$/.test(e.id)||objs.has(e.id)||supports[e.id]||
          !state.materials.some(m=>m.id===e.material_id&&m.status!=='user_rejected'&&['boundary_module','support_candidate'].includes(m.role))||!Array.isArray(e.points)||e.points.length!==2||
          !e.points.every(p=>Array.isArray(p)&&p.length===2&&p.every(v=>finite(v)&&v>=0&&v<=1)))throw Error('Invalid material staging');
       supports[e.id]=true;
       objs.set(e.id,{id:e.id,kind:'panel',label:String(e.label||'Tentative salvage').slice(0,120),points:e.points.map(p=>[...p]),movable:true,status:'tentative',
          source:'PHOTO_MATERIAL_UNREGISTERED:'+e.material_id,height:1.1,clearance:0,thickness:.08,height_quality:'diagram_assumption',clearance_quality:'diagram_assumption',notes:'Staged by human; not automatically placed or scaled from photo.'});continue;
     }
     if(e.type==='add_support'){
       if(!e.id||!/^human-support-[0-9]{1,4}$/.test(e.id)||!Array.isArray(e.point)||e.point.length!==2||!e.point.every(n=>finite(n)&&n>=0&&n<=1)||objs.has(e.id)||supports[e.id])throw Error('Invalid support');
       supports[e.id]=true;
       objs.set(e.id,{id:e.id,kind:'support',label:e.label||'Added support?',points:[[...e.point]],movable:true,status:'tentative',source:'HUMAN_HYPOTHESIS',height:1.3,clearance:0,thickness:.12,height_quality:'diagram_assumption',clearance_quality:'diagram_assumption',notes:'Candidate only'});continue;
     }
     if(e.type==='remove_support'){
       if(!supports[e.id])throw Error('Can remove added supports only');delete supports[e.id];objs.delete(e.id);continue;
     }
     const o=objs.get(e.id); if(!o)throw Error('Unknown object in event '+e.id);
     if(e.type==='position'){
       if(!Array.isArray(e.points)||e.points.length!==o.points.length||!e.points.every(p=>Array.isArray(p)&&p.length===2&&p.every(n=>finite(n)&&n>=0&&n<=1)))throw Error('Invalid 3D world position');
       if(!o.movable)throw Error('Immovable object cannot be repositioned without an explicit override');
       o.points=e.points.map(p=>[...p]);o.status='tentative';
     }else if(['height','clearance','thickness'].includes(e.type)){
       if(!finite(e.value)||e.value<0||e.value>100||!QUAL.has(e.quality))throw Error('Invalid dimension');
       if(e.type==='height' && (e.value===0||o.kind==='access'))throw Error('Access gap has no barrier height');
       if(e.type==='thickness'&&e.value<.01)throw Error('Thickness too small for renderer');
       o[e.type]=e.value;o[e.type+'_quality']=e.quality;
     }else if(e.type==='annotation'){
       if(typeof e.value!=='string'||e.value.length>500)throw Error('Invalid annotation');o.notes=e.value;
     }else if(e.type==='confirm'){
       if(!['tentative','user_confirmed','user_rejected'].includes(e.status))throw Error('Invalid confirmation');o.status=e.status;
     }
   }
   return {objects:[...objs.values()].filter(x=>x.status!=='user_rejected'),scale,version:model.events.length,
      sketch_size:state.sketch_size,provenance:state.source,materials:state.materials,
      source_note:model.source_note};
 }
 function stamp(model,event){
   const next=JSON.parse(JSON.stringify(model));
   if(event.type==='revert' && (!Number.isInteger(event.target_index)||event.target_index<1||event.target_index>next.events.length||next.events[event.target_index-1].type==='revert'))throw Error('Invalid undo target');
   next.events.push({...event,index:next.events.length+1});build(next);return next;
 }
 function dist2(a,b){return Math.hypot(a.x-b.x,a.z-b.z);}
 function closestOnSegment(p,a,b){const dx=b.x-a.x,dz=b.z-a.z,L=dx*dx+dz*dz;
   const t=L<1e-8?0:clamp(((p.x-a.x)*dx+(p.z-a.z)*dz)/L,0,1);
   return {x:a.x+t*dx,z:a.z+t*dz,t};}
 function crosses(a,b,c,d){
  const o=(p,q,r)=>(q.x-p.x)*(r.z-p.z)-(q.z-p.z)*(r.x-p.x);
  const x=o(a,b,c),y=o(a,b,d),z=o(c,d,a),w=o(c,d,b);
  return x*y < -1e-6 && z*w < -1e-6;
 }
 function diagnose(scene){
   const barriers=scene.objects.filter(o=>['current','desired','panel'].includes(o.kind)&&o.points.length===2);
   const supports=scene.objects.filter(o=>o.kind==='support');
   const issues=[],cues=[];
   for(const o of barriers){
     const feet=o.points.map(world);
     const L=dist2(feet[0],feet[1]);
     if(o.clearance>.12)issues.push({id:o.id,kind:'GROUND_GAP',severity:'CHECK',description:`${o.label} is elevated ${o.clearance.toFixed(2)} diagram units; a top-down line hides that opening.`});
     if(o.height_quality==='diagram_assumption')issues.push({id:o.id,kind:'UNKNOWN_HEIGHT',severity:'UNKNOWN',description:`${o.label} height is illustrative, not verified.`});
     if(L>.8&&!supports.some(s=>s.points.some(p=>feet.some(f=>dist2(f,world(p))<.18))) && !scene.objects.some(q=>q!==o&&['current','desired','panel'].includes(q.kind)&&q.points.some(p=>feet.some(f=>dist2(f,world(p))<.12))))
       issues.push({id:o.id,kind:'UNVERIFIED_SUPPORT',severity:'UNKNOWN',description:`${o.label} lacks an identified endpoint support in this model. Physical anchoring not tested.`});
     if(o.kind==='desired')cues.push({id:o.id,kind:'GOAL',description:`${o.label}: intended geometry only; no fence assumed installed.`});
   }
   for(let i=0;i<barriers.length;i++)for(let j=i+1;j<barriers.length;j++){
     const a=barriers[i],b=barriers[j],A=a.points.map(world),B=b.points.map(world);
     if(crosses(A[0],A[1],B[0],B[1])){
       const noVerticalOverlap=a.clearance+a.height<=b.clearance||b.clearance+b.height<=a.clearance;
       issues.push({id:a.id+'+'+b.id,kind:noVerticalOverlap?'2D_CROSSING_DIFFERENT_HEIGHT':'CROSSING_COLLISION_HYPOTHESIS',severity:'CHECK',description:noVerticalOverlap?'Lines cross in top view but are at different elevations; verify actual clearance.':'Planar spans cross; inspect whether this is a joint, overlap, or collision.'});
     }
   }
   const observedReference=scene.scale.kind==='conditional_reference';
   issues.push({id:'scale',kind:observedReference?'CONDITIONAL_SCALE':'NO_PHYSICAL_SCALE',severity:'UNKNOWN',description:observedReference?'An entered measurement and a sketch-proportionality assumption yield conditional metric estimates only.':'Drawing ratios are available; actual dimensions remain unknown.'});
   issues.push({id:'safety',kind:'STRUCTURAL_HOLD',severity:'HOLD',description:'Connection strength, tipping, entanglement, sharp edges and safe dog containment are not established by a 3D sketch.'});
   return {issues,cues,verified_physical_safety:false,photo_registered:false,geometry_3d_measured:false,model_calls:0};
 }
 function alternatives(scene){
   const g=scene.objects.filter(o=>o.kind==='desired'&&o.points.length===2),stock=scene.objects.filter(o=>['current','panel'].includes(o.kind)&&o.movable);
   const out=[];
   for(const t of g.slice(0,3)){
     const target=t.points.map(world);const targetLen=dist2(...target);
     for(const s of stock.slice(0,3)){
       const span=s.points.map(world),stockLen=dist2(...span),difference=Math.abs(targetLen-stockLen);
       out.push({id:`${s.id}-${t.id}`,title:`Try ${s.label} near ${t.label}`,source:s.id,target:t.id,
         pseudo_fit_error_du:+difference.toFixed(3),reversible_preview:true,physical_fit_certified:false,
         explanation:'Superimpose a copy at the target in the 3D diagram; actual relocation, fit and connections unverified.'});
     }
   }
   return out.sort((a,b)=>a.pseudo_fit_error_du-b.pseudo_fit_error_du).slice(0,5);
 }
 function nextQuestions(scene,diagnosis=diagnose(scene)){
   const lines=scene.objects.filter(o=>o.points.length===2);
   const res=[];
   if(scene.scale.kind==='diagram_only')res.push({id:'reference',priority:90,kind:'measurement',target:lines[0]?.id||null,label:'Measure one accessible span, then confirm whether the drawing is approximately proportional.'});
   const unknown=diagnosis.issues.find(x=>x.kind==='GROUND_GAP');
   if(unknown)res.push({id:'clearance',priority:92,kind:'height',target:unknown.id,label:'Verify how high this section actually sits above the ground.'});
   if(lines.some(x=>x.height_quality==='diagram_assumption'))res.push({id:'height',priority:84,kind:'height',target:lines.find(x=>x.height_quality==='diagram_assumption').id,label:'Enter the approximate height of one panel, or explicitly leave it unknown.'});
   if(diagnosis.issues.some(x=>x.kind==='UNVERIFIED_SUPPORT'))res.push({id:'support',priority:86,kind:'anchor',target:diagnosis.issues.find(x=>x.kind==='UNVERIFIED_SUPPORT').id,label:'Mark actual support/attachment points (the trampoline is only a candidate).'});
   if(!res.length)res.push({id:'critique',priority:50,kind:'inspection',target:null,label:'Review the least certain connection and perform a reversible dry fit.'});
   return res.sort((a,b)=>b.priority-a.priority);
 }
 function exportObj(scene){
  let lines=['# MOTIF FIELD-014 schematic OBJ',' # not actual geometry, not scaled without evidence'];let count=0;
  for(const o of scene.objects){if(o.points.length!==2||o.kind==='access')continue;
    const [a,b]=o.points.map(world),bot=o.clearance,top=bot+o.height;
    lines.push(`# ${o.id} | ${o.status} | ${o.height_quality}`);
    [[a.x,bot,a.z],[b.x,bot,b.z],[b.x,top,b.z],[a.x,top,a.z]].forEach(v=>lines.push('v '+v.map(x=>x.toFixed(5)).join(' ')));
    lines.push(`f ${count+1} ${count+2} ${count+3} ${count+4}`);count+=4;
  }
  return lines.join('\n')+'\n';
 }
 const api={create,validate,build,stamp,world,toNorm,length,dist2,closestOnSegment,diagnose,alternatives,nextQuestions,exportObj};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;root.MOTIF014=api;
})(typeof window!=='undefined'?window:globalThis);
