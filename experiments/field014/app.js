/* FIELD-014: shared interactive plan / actual 3-D geometry in a local-only canvas.
   No hidden inference / server / WebGL dependency. */
(()=>{'use strict';
 const S=window.MOTIF014,C=window.MOTIF014_CAMERA;
 let model=S.create(window.MOTIF010_FIXTURE),scene=S.build(model),selected=null,mode='orbit',camera=C.camera();
 let drag=null,ghost=null,photos=[],sketch=null,seq=1,lastDiagnosis=null;
 const $=x=>document.getElementById(x);
 const fmt=x=>Number.isFinite(x)?Number(x.toFixed(2)).toString():'?';
 const status=t=>{$('feedback').textContent=t;};
 const plan=$('plan'),three=$('view3d');
 function canvasSetup(canvas){let dpr=Math.max(1,Math.min(2,window.devicePixelRatio||1)),r=canvas.getBoundingClientRect();if(!r.width||!r.height)return null;
  let w=Math.round(r.width*dpr),h=Math.round(r.height*dpr);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
  let ctx=canvas.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);return {ctx,w:r.width,h:r.height};}
 const ink={current:'#7ad7b1',desired:'#edcd7d',panel:'#89bbf5',support:'#dda7e7',access:'#c5a7a2'};
 function normalized(e,canvas){let b=canvas.getBoundingClientRect();return {x:e.clientX-b.left,y:e.clientY-b.top,w:b.width,h:b.height};}
 function to2D(p,w,h){return{x:p[0]*w,y:p[1]*h};}
 function drawPlan(){const env=canvasSetup(plan);if(!env)return;const {ctx,w,h}=env;
  ctx.fillStyle='#10222d';ctx.fillRect(0,0,w,h);ctx.strokeStyle='#213a46';ctx.lineWidth=1;
  for(let i=0;i<=20;i++){let x=w*i/20;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke();}
  for(let j=0;j<=10;j++){let y=h*j/10;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();}
  ctx.lineCap='round';
  for(const o of scene.objects){let pts=o.points.map(p=>to2D(p,w,h)),picked=selected===o.id;
   ctx.strokeStyle=ink[o.kind]||'#ccc';ctx.fillStyle=ink[o.kind]||'#ccc';ctx.lineWidth=picked?5:3;
   ctx.setLineDash(o.kind==='desired'?[9,7]:o.status==='tentative'?[5,4]:[]);
   if(pts.length===2){ctx.beginPath();ctx.moveTo(pts[0].x,pts[0].y);ctx.lineTo(pts[1].x,pts[1].y);ctx.stroke();}
   else{ctx.beginPath();ctx.arc(pts[0].x,pts[0].y,picked?9:6,0,Math.PI*2);ctx.fill();}
   ctx.setLineDash([]);if(picked)for(let i=0;i<pts.length;i++){ctx.beginPath();ctx.arc(pts[i].x,pts[i].y,5,0,2*Math.PI);ctx.fillStyle='#f7f8d9';ctx.fill();}
   let mid=pts.length===2?{x:(pts[0].x+pts[1].x)/2,y:(pts[0].y+pts[1].y)/2}:pts[0];ctx.font='11px system-ui';ctx.fillStyle='#fff4dd';ctx.fillText(o.label.slice(0,20),Math.min(mid.x+7,w-120),Math.max(14,mid.y-9));
  }
  ctx.setLineDash([]);ctx.fillStyle='#a8bbbd';ctx.font='11px system-ui';ctx.fillText('2D drawing / source coordinate plane — NOT surveyed',11,h-12);
 }
 function canvasLine(ctx,a,b,col='#476371',width=1){ctx.strokeStyle=col;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}
 function draw3D(){const env=canvasSetup(three);if(!env)return;const {ctx,w,h}=env;
   let g=ctx.createLinearGradient(0,0,0,h);g.addColorStop(0,'#0d1723');g.addColorStop(1,'#21383a');ctx.fillStyle=g;ctx.fillRect(0,0,w,h);
   // The x-z horizontal plane is genuine world geometry at y=0.
   for(let x=0;x<=10;x+=.5){const a=C.project({x,y:0,z:0},camera,w,h),b=C.project({x,y:0,z:4.5},camera,w,h);if(a&&b)canvasLine(ctx,a,b,x%1===0?'#42606a':'#344d57',x%1===0?1.2:.5);}
   for(let z=0;z<=4.5;z+=.5){const a=C.project({x:0,y:0,z},camera,w,h),b=C.project({x:10,y:0,z},camera,w,h);if(a&&b)canvasLine(ctx,a,b,z%1===0?'#466069':'#344d57',z%1===0?1.1:.6);}
   const polys=C.polygons(scene.objects,S,camera,w,h);for(const face of polys){
     const col=ink[face.kind]||'#fff';let alpha=face.kind==='desired'?.16:face.status==='tentative'?.36:.63;
     ctx.beginPath();face.points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();ctx.fillStyle=hexAlpha(col,alpha);ctx.fill();
     ctx.strokeStyle=face.id===selected?'#fff5bd':col;ctx.lineWidth=face.id===selected?2:1;
     ctx.setLineDash(face.kind==='desired'?[5,4]:[]);ctx.stroke();ctx.setLineDash([]);
   }
   if(ghost){const o=scene.objects.find(x=>x.id===ghost.source);const target=scene.objects.find(x=>x.id===ghost.target);
      if(o&&target&&target.points.length===2){const hO={...o,points:target.points,status:'tentative',kind:'panel'};
        for(const face of C.polygons([hO],S,camera,w,h)){
          ctx.beginPath();face.points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();ctx.fillStyle='#ffffff11';ctx.fill();ctx.strokeStyle='#fff19c';ctx.lineWidth=1;ctx.setLineDash([5,5]);ctx.stroke();ctx.setLineDash([]);
        }
      }
   }
   for(const o of scene.objects){let p=o.points.length===2?S.world(o.points[0]):S.world(o.points[0]);p.y=o.clearance+o.height;
      let q=C.project(p,camera,w,h);if(q){ctx.font='11px system-ui';ctx.fillStyle=o.id===selected?'#fff9cf':'#c6d4d7';ctx.fillText(o.label.slice(0,16),q.x+6,q.y-5);}
   }
   ctx.font='11px system-ui';ctx.fillStyle='#9ab6bc';ctx.fillText('Perspective projection · x, y (height), z · NOT a site scan',12,h-13);
 }
 function hexAlpha(hex,alpha){if(!/^#[0-9a-f]{6}$/i.test(hex))return `rgba(140,180,195,${alpha})`;let n=parseInt(hex.slice(1),16);return `rgba(${n>>16},${(n>>8)&255},${n&255},${alpha})`;}
 function pickPlan(p){let best=null,dmin=22;
   for(const o of scene.objects){const v=o.points.map(x=>to2D(x,p.w,p.h));let d;
     if(v.length===2){let ax=v[0],bx=v[1],dx=bx.x-ax.x,dy=bx.y-ax.y;let t=Math.max(0,Math.min(1,((p.x-ax.x)*dx+(p.y-ax.y)*dy)/(dx*dx+dy*dy||1)));
       d=Math.hypot(p.x-(ax.x+t*dx),p.y-(ax.y+t*dy));}else d=Math.hypot(p.x-v[0].x,p.y-v[0].y);
     if(d<dmin){dmin=d;best=o;}
   }return best;
 }
 function pick3D(p){let best=null,min=32;
   for(const o of scene.objects){let m=o.points.length===2?[(o.points[0][0]+o.points[1][0])/2,(o.points[0][1]+o.points[1][1])/2]:o.points[0],w=S.world(m);
     let q=C.project({x:w.x,y:o.height/2+o.clearance,z:w.z},camera,p.w,p.h);if(q){let d=Math.hypot(q.x-p.x,q.y-p.y);if(d<min){min=d;best=o;}}
   }return best;
 }
 function highlight(id){selected=id;ghost=null;refresh();}
 function handleEdit(event,why){try{model=S.stamp(model,event);scene=S.build(model);ghost=null;refresh();status(why||`${event.type} recorded as an editable hypothesis. No physical action performed.`);return true;}
   catch(ex){status('HELD: '+ex.message);return false;}}
 function latestActiveEvent(){const suppressed=new Set(model.events.filter(e=>e.type==='revert').map(e=>e.target_index));return [...model.events].reverse().find(e=>e.type!=='revert'&&!suppressed.has(e.index));}
 function undo(){const event=latestActiveEvent();if(!event){status('No edits to undo.');return;}handleEdit({type:'revert',target_index:event.index},`Reverted revision ${event.index} using a new event.`);}
 function planPoint(e){let p=normalized(e,plan);return {raw:p, norm:[Math.max(0,Math.min(1,p.x/p.w)),Math.max(0,Math.min(1,p.y/p.h))]};}
 plan.addEventListener('pointerdown',e=>{
   const {raw,norm}=planPoint(e),o=pickPlan(raw);
   if(o){selected=o.id;drag={view:'plan',id:o.id,start:norm,points:o.points.map(p=>[...p])};plan.setPointerCapture(e.pointerId);status(o.movable?'Drag to move '+o.label:'Fixed annotation. Change ownership/mobility in the 2D board if this is wrong.');refresh();}
   else {selected=null;refresh();}
 });
 plan.addEventListener('pointerup',e=>{
   if(!drag||drag.view!=='plan')return;const {norm}=planPoint(e),o=scene.objects.find(x=>x.id===drag.id);
   const dx=norm[0]-drag.start[0],dy=norm[1]-drag.start[1],pts=drag.points.map(p=>[p[0]+dx,p[1]+dy]);
   if(o?.movable&&Math.hypot(dx,dy)>.004)handleEdit({type:'position',id:drag.id,points:pts},'2D correction synchronized into 3D geometry and both reasoning branches.');
   drag=null;refresh();
 });
 plan.addEventListener('pointercancel',()=>{drag=null;refresh();});
 three.addEventListener('pointerdown',e=>{
  const p=normalized(e,three);const hit=pick3D(p);if(mode==='move'&&hit){selected=hit.id;
     const ground=C.rayGround(p.x,p.y,camera,p.w,p.h);drag={view:'3d',id:hit.id,start:ground,points:hit.points.map(v=>[...v])};
   }else drag={view:'orbit',start:{x:p.x,y:p.y},yaw:camera.yaw,pitch:camera.pitch};
   three.setPointerCapture(e.pointerId);refresh();
 });
 three.addEventListener('pointermove',e=>{
   if(!drag)return;const p=normalized(e,three);
   if(drag.view==='orbit'){
     camera.yaw=drag.yaw+(p.x-drag.start.x)*.009;camera.pitch=Math.max(.1,Math.min(1.52,drag.pitch+(p.y-drag.start.y)*.009));draw3D();
   }
 });
 three.addEventListener('pointerup',e=>{
   if(!drag)return;const p=normalized(e,three);
   if(drag.view==='3d'){
     const o=scene.objects.find(x=>x.id===drag.id),newGround=C.rayGround(p.x,p.y,camera,p.w,p.h);
     if(newGround&&drag.start&&o?.movable){const diff={x:newGround.x-drag.start.x,z:newGround.z-drag.start.z};
       if(Math.hypot(diff.x,diff.z)>.04){const points=drag.points.map(v=>{
          const w=S.world(v);return S.toNorm({x:w.x+diff.x,z:w.z+diff.z});});
          handleEdit({type:'position',id:drag.id,points},'3D ground-plane drag updated both visual projections.');
       }else {selected=o.id;refresh();}
     }
   }drag=null;refresh();
 });
 three.addEventListener('pointercancel',()=>{drag=null;refresh();});
 three.addEventListener('wheel',e=>{e.preventDefault();camera.distance=Math.max(5,Math.min(65,camera.distance*Math.exp(e.deltaY*.001)));draw3D();},{passive:false});
 function buttons(){
   $('orbit').classList.toggle('active',mode==='orbit');$('move3d').classList.toggle('active',mode==='move');$('cameraLabel').textContent=mode==='orbit'?'Orbit · wheel to zoom':'Drag selected objects on ground plane';
 }
 $('orbit').onclick=()=>{mode='orbit';buttons();};$('move3d').onclick=()=>{mode='move';buttons();};
 $('top').onclick=()=>{camera=C.camera(.05,1.52,18);draw3D();};$('iso').onclick=()=>{camera=C.camera();draw3D();};
 $('newSupport').onclick=()=>{const id='human-support-'+seq++;handleEdit({type:'add_support',id,point:[.5,.5],label:'Candidate support'},'Support added at schematic midpoint. Drag it and verify what it physically represents.');selected=id;refresh();};
 $('undo').onclick=undo;$('rethink').onclick=()=>{refresh();status('Both branches recomputed from the latest event-replayed geometry.');};
 function renderObjects(){const host=$('objects');host.replaceChildren();scene.objects.forEach(o=>{
   const b=document.createElement('button');b.className='small'+(selected===o.id?' active':'');
   b.textContent=(o.kind==='desired'?'◇ ':o.kind==='support'?'◉ ':'▰ ')+o.label+' · '+o.kind;
   b.addEventListener('click',()=>highlight(o.id));host.append(b);
 });$('chosenId').textContent=selected||'None';}
 function elem(tag,attrs,text){const e=document.createElement(tag);if(attrs)for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=String(text);return e;}
 function renderInspector(){const host=$('inspector');host.replaceChildren();const o=scene.objects.find(x=>x.id===selected);
   if(!o){host.append(elem('p',{class:'muted'},'Select an object in either drawing.'));return;}
   host.append(elem('div',{class:'box'},`${o.label} · ${o.kind} · ${o.status}\nSource: ${o.source}`));
   const fields=[['height','Height (illustrative 3D units)'],['clearance','Bottom gap from ground (diagram units)'],['thickness','Thickness (diagram units)']];
   for(const [field,title] of fields){if(o.kind==='access')continue;
     const label=elem('label',{class:'field'},title);const input=elem('input',{type:'number',step:'.05',min:'0',max:'100',value:String(o[field]),id:'input-'+field});label.append(input);host.append(label);
     input.addEventListener('change',()=>{handleEdit({type:field,id:o.id,value:Number(input.value),quality:'human_rough'},'Updated 3D hypothesis. The numeric value is not a surveyed dimension.');});
   }
   host.append(elem('div',{class:'minihelp muted'},'These values control the rendered shape, not its engineering validity. Dimensions are expressed in schematic units.'));
   const row=elem('div',{class:'row'});for(const [s,label] of [['user_confirmed','Confirm as an intentional drawing'],['user_rejected','Reject candidate']]){
       const b=elem('button',{class:'small'},label);b.addEventListener('click',()=>{handleEdit({type:'confirm',id:o.id,status:s},'Changed interpretation status, not physical construction status.');if(s==='user_rejected')selected=null;refresh();});row.append(b);
     }host.append(row);
   if(o.source==='HUMAN_HYPOTHESIS'){const b=elem('button',{class:'small'},'Remove added support');b.onclick=()=>{handleEdit({type:'remove_support',id:o.id});selected=null;refresh();};host.append(b);}
 }
 function renderThinking(){lastDiagnosis=S.diagnose(scene);let host=$('issues');host.replaceChildren();for(const issue of lastDiagnosis.issues.slice(0,10)){
    const b=elem('div',{class:'box '+(issue.severity==='HOLD'?'hold':'status')});b.append(elem('strong',{},issue.kind.replaceAll('_',' ')));b.append(elem('span',{},issue.description));host.append(b);
   }
   host=$('questions');host.replaceChildren();S.nextQuestions(scene,lastDiagnosis).slice(0,4).forEach((q,i)=>{
     const b=elem('button',{class:'box small',style:'width:100%;text-align:left'},q.label);b.onclick=()=>{
        if(q.target)selected=q.target;refresh();if(q.kind==='measurement')$('meters').focus();
        else if(q.kind==='height')$('input-'+(q.id==='clearance'?'clearance':'height'))?.focus();
        else if(q.kind==='anchor')$('newSupport').focus();
     };host.append(b);
   });
   host=$('alternatives');host.replaceChildren();const opts=S.alternatives(scene);if(!opts.length)host.append(elem('p',{class:'muted'},'No movable inventory and desired span can be paired yet.'));
   opts.slice(0,3).forEach(x=>{const b=elem('button',{class:'box small',style:'width:100%;text-align:left'},x.title+'\nDrawing-length difference ≈ '+fmt(x.pseudo_fit_error_du)+' units · NOT a physical fit');
     b.onclick=()=>{ghost=x;selected=x.source;draw3D();status('Ghost preview only. No relocation or attachment has occurred.');};host.append(b);});
 }
 function renderCalibration(){let segments=scene.objects.filter(o=>o.points.length===2&&o.kind!=='access'),sl=$('knownSegment');const old=sl.value;sl.replaceChildren();segments.forEach(x=>sl.append(elem('option',{value:x.id},x.label+' · '+x.id)));
   if(segments.some(x=>x.id===old))sl.value=old;
   $('scalePill').textContent=scene.scale.kind==='diagram_only'?'Ratio-only · no meters':'Conditional meter scale';
   $('calibrationNote').textContent=scene.scale.kind==='diagram_only'?'No metric site scale is known. 3D panel heights are deliberately assumed.':`Measured ${scene.scale.source} gives ${fmt(scene.scale.meters_per_unit)} meters/diagram-unit, provided this sketch is approximately proportional (assumed ±${Math.round(scene.scale.nonuniformity*100)}%).`;
 }
 $('applyScale').onclick=()=>handleEdit({type:'calibrate',known_segment:$('knownSegment').value,meters:Number($('meters').value),quality:'user_measured',sketch_proportional:$('proportional').checked,nonuniformity:Number($('distortion').value)/100},'Source-declared measurement enables conditional geometry. No camera calibration or structural validation.');
 $('resetScale').onclick=()=>handleEdit({type:'calibrate',known_segment:null},'Reset to drawing ratios only.');
 function renderMaterials(){const host=$('materials');host.replaceChildren();const materials=scene.materials.filter(m=>m.status!=='user_rejected');
   if(!materials.length){host.append(elem('p',{class:'muted'},'Import a FIELD-012/013 board to inspect candidate photo materials. No photo recognition runs automatically.'));return;}
   for(const m of materials.slice(0,35)){
     const tile=elem('div',{class:'box'}),txt=elem('strong',{},m.label+' · '+m.role);
     tile.append(txt);tile.append(elem('span',{class:'minihelp muted'},'Photo region only. No yard coordinates, lengths, or support capacity.'));
     if(m.role==='boundary_module'||m.role==='support_candidate'){
       const b=elem('button',{class:'small'},'Stage tentative 3D panel');b.addEventListener('click',()=>{
          const id='stage-'+seq++,pts=[[.40,.54],[.53,.54]];
          handleEdit({type:'add_barrier',id,material_id:m.id,label:m.label,points:pts},'Staged as a hypothetical panel at an arbitrary diagram location, not registered from the photo.');selected=id;refresh();
       });tile.append(b);
     }
     host.append(tile);
   }
 }
 function renderLedger(){$('revision').textContent='3D edits '+model.events.length;
   $('ledger').textContent=model.events.slice(-8).map(e=>`#${e.index} ${e.type}: ${e.id||e.known_segment||e.target_index||''}`).join('\n')||'No manual 3D revisions yet.';
 }
 function refresh(){scene=S.build(model);drawPlan();draw3D();renderObjects();renderInspector();renderThinking();renderCalibration();renderMaterials();renderLedger();}
 window.addEventListener('resize',()=>{drawPlan();draw3D();});
 function saveBlob(content,name,mime){const url=URL.createObjectURL(new Blob([content],{type:mime}));const a=elem('a',{href:url,download:name});document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1400);}
 $('exportState').onclick=()=>saveBlob(JSON.stringify(model,null,2),'motif-field014-3d-ledger.json','application/json');
 $('exportObj').onclick=()=>{saveBlob(S.exportObj(scene),'motif-field014-schematic.obj','text/plain');status('Exported actual 3D vertex coordinates in diagram units. Not a construction plan.');};
 $('boardFile').addEventListener('change',async e=>{const file=e.target.files?.[0];if(!file)return;if(file.size>4000000){status('Refused oversized board JSON.');return;}
   try{const p=JSON.parse(await file.text());let next=p.schema==='motif.field014.v1'?p:S.create(p);S.build(next);
       model=next;selected=null;seq=1+Math.max(0,...model.events.filter(x=>x.type==='add_support'||x.type==='add_barrier').map(x=>Number((x.id||'').split('-').at(-1))||0));refresh();status('Imported validated event-replayed board. Reattach original sketch/photos separately; export JSON excludes pixels.');
   }catch(err){status('HELD: Could not import board: '+err.message);}
 });
 function setSourceData(source){sketch=source;$('sourcePreview').src=source;$('sourcePreview').style.display='block';}
 $('sourceFile').addEventListener('change',async e=>{const f=e.target.files?.[0];if(!f)return;
   if(f.size>15e6||!/^image\/(png|jpeg|webp)$/.test(f.type)){status('Unsupported sketch file or >15MB.');return;}
   setSourceData(URL.createObjectURL(f));status('Reference sketch loaded separately. No automatic transfer of paper ink to the 3D model. Import the editable 2D board JSON for alignment.');
 });
 function addPhoto(name,url){const image=new Image();image.src=url;image.alt=name;image.title=name;$('photos').append(image);photos.push({name,url});}
 $('photoFiles').addEventListener('change',e=>{for(const f of Array.from(e.target.files||[])){
   if(/^image\/(png|jpeg|webp)$/.test(f.type)&&f.size<10e6)addPhoto(f.name,URL.createObjectURL(f));
 }status('Photo witnesses added; not automatically registered to the 3D scene.');});
 if(window.MOTIF014_PRIVATE_SOURCE)setSourceData(window.MOTIF014_PRIVATE_SOURCE);
 if(Array.isArray(window.MOTIF014_PRIVATE_PHOTOS))window.MOTIF014_PRIVATE_PHOTOS.forEach(p=>addPhoto(p.name,p.url));
 if(window.MOTIF014_PRIVATE_PROJECT){try{model=S.create(window.MOTIF014_PRIVATE_PROJECT);scene=S.build(model);}catch(err){status('Private board failed validation: '+err.message);}}
 window.MOTIF014_DEBUG={getModel:()=>JSON.parse(JSON.stringify(model)),getScene:()=>JSON.parse(JSON.stringify(scene)),getDiagnosis:()=>S.diagnose(scene),getCamera:()=>({...camera}),apply:handleEdit,select:highlight,setMode:(m)=>{mode=m;buttons();},exportObj:()=>S.exportObj(scene)};
 buttons();refresh();
})();
