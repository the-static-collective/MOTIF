/* FIELD-017 browser budgeted co-sketch search. Imports the ACTUAL FIELD-016 numeric
 * screen. No world-model inference, field actions or claims of safe containment.
 */
(function(root){'use strict';
const Parent = typeof require === 'function' && typeof module !== 'undefined' ? require('../field016/ui.js') : root.Field016;
if(!Parent)throw Error('FIELD-016 numeric critic unavailable');
const validNum=v=>typeof v==='number' && Number.isFinite(v);
function assertWorld(s){
 if(!s || !Array.isArray(s.routes) || !Array.isArray(s.pieces) || !s.routes.length || !s.pieces.length || s.routes.length>12 || s.pieces.length>10)throw Error('Bounded scene required');
 if(new Set(s.pieces.map(p=>p.id)).size!==s.pieces.length || new Set(s.routes.map(r=>r.id)).size!==s.routes.length)throw Error('Duplicate identifiers');
 if(!validNum(s.wind)||s.wind<0||s.wind>60)throw Error('Wind outside stated scenario');
 for(const p of s.pieces){if(!p.id)throw Error('Missing piece id');for(const key of ['width','height','mass','base','gap'])if(p[key]!==null&&p[key]!==undefined&&(!validNum(p[key])||p[key]<0))throw Error('Invalid '+key)}
 return s;
}
const id=l=>l.route+'|'+l.pieces.join(',');
function inspect(scene,layout){
 assertWorld(scene);
 const route=scene.routes.find(r=>r.id===layout.route);const parts=layout.pieces.map(pid=>scene.pieces.find(p=>p.id===pid));
 if(!route || !layout.pieces.length || layout.pieces.length>3 || parts.includes(undefined) || new Set(layout.pieces).size!==layout.pieces.length)throw Error('Candidate references unknown material');
 let failures=[],warnings=[],coverage=0,force=null;
 if(parts.length>1 && !scene.connections)failures.push('No connectors available');
 const widthsKnown=parts.every(p=>validNum(p.width)&&p.width>0);
 if(!widthsKnown)warnings.push('Panel widths are not all known');
 else {coverage=parts.reduce((n,p)=>n+p.width,0);if(coverage+1e-9<route.span)failures.push('Nominal boundary coverage too short')}
 if(route.access===false)failures.push('Human access blocked');
 const plan=Parent.calculate({...scene,pieces:parts,routes:[route]});
 const match=plan.find(x=>x.route===route.id&&x.pieces.length===parts.length&&layout.pieces.every(x=>parts.some(p=>p.id===x)));
 if(match){if(match.rejected)failures.push('FIELD-016 physics or clearance model fails');warnings.push(...match.warnings);force=match.forceSum;}
 else warnings.push('No full grouping accepted by the FIELD-016 numeric screen');
 if(route.access===null)warnings.push('Access status unknown');
 if(parts.some(p=>!p.measured))warnings.push('Dimensions not independently confirmed');
 if(parts.some(p=>!p.edges))warnings.push('Edges not checked');
 if(parts.some(p=>p.kind==='mesh'&&!p.entrapment))warnings.push('Entrapment risk not checked');
 if(parts.length>1)warnings.push('Actual joint capacity and bracing unknown');
 for(const p of parts){if(p.gap==null)warnings.push('Ground clearance unknown: '+p.id);}
 warnings=[...new Set(warnings)];failures=[...new Set(failures)];
 const effort=parts.length*2+(route.move?4:0);
 const score=[Number(failures.length>0),failures.length,warnings.length,effort,force===null?100000:Math.round(force*10)];
 return {id:id(layout),route:layout.route,pieces:[...layout.pieces],parent:layout.parent||null,operation:layout.operation||'SEED',
  verdict:failures.length?'REJECTED_UNDER_STATED_MODEL':'CONDITIONAL_HOLD_NOT_CERTIFIED',
  failures,warnings,score,effort,force,coverage:widthsKnown?coverage:null,
  safety_certified:false,model_is_not_physical_verification:true};
}
function neighbors(scene,l){
 let out=[];
 for(const route of scene.routes)if(route.id!==l.route)out.push({route:route.id,pieces:[...l.pieces],parent:id(l),operation:'MOVE_BOUNDARY'});
 for(const pid of l.pieces)for(const p of scene.pieces)if(!l.pieces.includes(p.id))out.push({route:l.route,pieces:l.pieces.map(x=>x===pid?p.id:x),parent:id(l),operation:'SUBSTITUTE_MATERIAL'});
 if(scene.connections&&l.pieces.length<Math.min(3,scene.pieces.length))for(const p of scene.pieces)if(!l.pieces.includes(p.id))out.push({route:l.route,pieces:[...l.pieces,p.id],parent:id(l),operation:'COMPOSE_PANELS'});
 if(l.pieces.length>1)for(const pid of l.pieces)out.push({route:l.route,pieces:l.pieces.filter(x=>x!==pid),parent:id(l),operation:'REMOVE_PIECE'});
 const order={MOVE_BOUNDARY:0,SUBSTITUTE_MATERIAL:1,COMPOSE_PANELS:2,REMOVE_PIECE:3};
 return out.sort((a,b)=>(order[a.operation]-order[b.operation])||id(a).localeCompare(id(b)));
}
function better(a,b){for(let i=0;i<a.score.length;i++)if(a.score[i]!==b.score[i])return a.score[i]<b.score[i];return a.id<b.id}
function nextInput(scene,selected){const route=scene.routes.find(r=>r.id===selected.route);
 if(route?.access==null)return {kind:'VERIFY_ACCESS',text:'Will the moved boundary preserve a usable access route?',widget:'yes-no-unknown',subject:route.id};
 const p=scene.pieces.find(x=>selected.pieces.includes(x.id)&&!x.measured);
 if(p)return {kind:'MEASURE_WIDTH',text:'What is the actual usable width of '+p.id+'?',widget:'measurement',subject:p.id};
 return {kind:'INSPECT_CONNECTION',text:'What actual anchors, joints, and ground gaps need verification?',widget:'photo-note',subject:selected.id};
}
function run(scene,seed,budget=16){assertWorld(scene);if(!Number.isInteger(budget)||budget<1||budget>250)throw Error('Budget 1–250');
 const original=JSON.stringify(scene),initial=inspect(scene,seed),evaluated=new Map([[initial.id,initial]]),frontier=[initial];
 const trace=[{step:1,...initial,changed:false}];let expansions=0;
 while(frontier.length && trace.length<budget){frontier.sort((a,b)=>better(a,b)?-1:better(b,a)?1:0);const now=frontier.shift();expansions++;
 for(const l of neighbors(scene,{route:now.route,pieces:now.pieces})){
  if(evaluated.has(id(l)))continue;if(trace.length>=budget)break;
  const row=inspect(scene,l),previous=evaluated.get(l.parent);evaluated.set(row.id,row);frontier.push(row);
  trace.push({step:trace.length+1,...row,changed:previous?previous.verdict!==row.verdict:false});
 }
 }
 let selected=initial;for(const x of evaluated.values())if(better(x,selected))selected=x;
 if(JSON.stringify(scene)!==original)throw Error('World state unexpectedly mutated');
 return {initial,selected,trace,budget,evaluated:trace.length,expansions,remaining:frontier.length,improved:better(selected,initial),
   nextInput:nextInput(scene,selected),safety_certified:false,real_world_actions:0,actual_3d_reconstruction:false};
}
const api={run,inspect,neighbors,nextInput,better,assertWorld};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.Field017=api;
})(typeof window!=='undefined'?window:globalThis);
