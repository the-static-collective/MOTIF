/* FIELD-016 offline hypothesis visualizer. Scenario numbers invented. */
(function(root){'use strict';
const G=9.80665, RHO=1.225;
function finitePositive(x){return typeof x==='number' && Number.isFinite(x) && x>0}
function calculate(scene){
  const wind=Number(scene.wind);if(!Number.isFinite(wind)||wind<0||wind>60)throw Error('Wind scenario must be 0–60 m/s');
  const rows=[];
  for(const route of scene.routes){
    const span=Number(route.span);
    if(!finitePositive(span))continue;
    const pieces=scene.pieces;
    for(let mask=1;mask<(1<<pieces.length);mask++){
      const members=pieces.filter((p,i)=>mask>>i&1);
      if(members.length>3 || (members.length>1 && !scene.connections))continue;
      const coverage=members.reduce((a,p)=>a+Number(p.width||0),0);
      if(members.every(p=>finitePositive(Number(p.width))) && coverage+1e-6<span)continue;
      const warnings=[];const forces=[];let fails=false,forceSum=0;
      if(members.length>1)warnings.push('Connected does not mean stabilized; joint strength unknown');
      if(route.move)warnings.push('Repositioning feasibility and permissions unverified');
      if(route.access===null)warnings.push('Human access and gate requirements unverified');
      if(members.some(p=>!p.measured))warnings.push('One or more widths are still guesses');
      if(members.some(p=>!p.edges))warnings.push('Inspect sharp edges and snag points');
      if(members.some(p=>p.kind==='mesh'&&!p.entrapment))warnings.push('Loose mesh entrapment risk requires checking');
      members.forEach(p=>{
        let f=null;
        if([p.width,p.height,p.opacity].every(x=>x!==null&&Number.isFinite(Number(x)))){
          f=0.5*RHO*wind*wind*1.4*Number(p.width)*Number(p.height)*Number(p.opacity);
          forceSum+=f;
          if([p.mass,p.base,p.height].every(v=>v!==null&&Number.isFinite(Number(v))&&Number(v)>0)){
            if(f>Number(p.mass)*G*Number(p.base)/Number(p.height)+1e-7)fails=true;
            if(f>0.6*Number(p.mass)*G+1e-7)fails=true;
          }else warnings.push('Mass/base/support capacity unverified: '+p.id);
        } else warnings.push('Physics dimensions or drag inputs unknown: '+p.id);
        if(p.gap===null || p.gap===undefined)warnings.push('Ground clearance unknown: '+p.id);
        else if(p.gap>route.maxGap){fails=true;warnings.push('Gap exceeds user-stated tolerance: '+p.id);}
        forces.push({id:p.id,force:f});
      });
      rows.push({route:route.id,pieces:members.map(x=>x.id),members,span,coverage,
        status:fails?'MODEL REJECTS ASSUMED CASE':'HOLD — PHYSICAL SAFETY NOT VERIFIED',
        rejected:fails,forces,forceSum,warnings,effort:members.length*2+(route.move?4:0),
        assumptions:'Simplified uniform-wind scenario, guessed mass/friction/Cd, idealized 2D span; no soil, wind gusts or joint load distribution.'});
    }
  }
  rows.sort((a,b)=>Number(a.rejected)-Number(b.rejected)||a.warnings.length-b.warnings.length||a.effort-b.effort||a.forceSum-b.forceSum);
  return rows;
}
function initial(){return {revision:0,wind:8,connections:true,
  pieces:[{id:'privacy',kind:'privacy',width:1.5,height:1,mass:5,base:.35,opacity:1,gap:0,measured:false,edges:false,entrapment:false},
          {id:'cage',kind:'rigid',width:1,height:1,mass:4,base:.42,opacity:.55,gap:0,measured:false,edges:false,entrapment:false},
          {id:'porous',kind:'mesh',width:1.5,height:1,mass:5,base:.35,opacity:.2,gap:null,measured:false,edges:false,entrapment:false}],
  routes:[{id:'original',span:2.4,maxGap:.06,move:false,access:true},
          {id:'repositioned',span:1.5,maxGap:.06,move:true,access:null}],
  events:[],fixture:'SIMULATED: NOT USER PROPERTY',safety_certified:false};}
function update(scene,kind,details){const n=structuredClone(scene);n.revision++;
 if(kind==='piece'){
   const p=n.pieces.find(x=>x.id===details.id);if(!p)throw Error('Unknown piece');
   if(!['width','height','base','mass','gap','opacity','measured','edges','entrapment'].includes(details.field))throw Error('Unknown property');
   if(['measured','edges','entrapment'].includes(details.field))p[details.field]=Boolean(details.value);
   else {const val=details.value===''||details.value===null?null:Number(details.value);
     if(val!==null && (!Number.isFinite(val)||val<0||(['width','height','base','mass'].includes(details.field)&&val===0)))throw Error('Bad input');
     if(details.field==='opacity' && val!==null && val>1)throw Error('Opacity must be 0–1');
     p[details.field]=val;
   }
 } else if(kind==='route'){
   const p=n.routes.find(x=>x.id===details.id);if(!p)throw Error('Unknown route');
   if(!['span','maxGap'].includes(details.field))throw Error('Unknown route property');
   const v=Number(details.value);if(!Number.isFinite(v)||v<0||(details.field==='span'&&v===0))throw Error('Bad route dimension');
   p[details.field]=v;
 } else if(kind==='wind'){
   const v=Number(details.value);if(!Number.isFinite(v)||v<0||v>60)throw Error('Bad wind');n.wind=v;
 } else if(kind==='remove'){
   n.pieces=n.pieces.filter(x=>x.id!==details.id);
 } else if(kind==='connections') n.connections=Boolean(details.value);
 else throw Error('Unknown edit');
 n.events.push({revision:n.revision,kind,details,evidence:'LOCAL_USER_EDIT_NOT_FIELD_VERIFICATION'});
 return n;
}
const api={calculate,initial,update};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.Field016=api;
})(typeof window!=='undefined'?window:globalThis);
