/* FIELD-017 live browser app: no external calls, no field operations. */
(()=>{'use strict';
const el=id=>document.getElementById(id);const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let scene=Field016.initial(),history=[],budget=16,current=null,picked=null,orbit=.6,zoom=83,photoURL=null,sketchURL=null;
const stamp=new Date().toISOString();
function edit(kind,details){try{history.push(structuredClone(scene));scene=Field016.update(scene,kind,details);rerun();}catch(err){history.pop();alert(err.message)}}
function drawPieceEditor(){let html='';for(const p of scene.pieces){html+=`<div class="box fieldgroup"><strong>${escape(p.id)} · ${escape(p.kind)}</strong><div class="fieldgrid">`;
for(const [key,label] of [['width','Width m'],['height','Height m'],['mass','Mass kg'],['base','Base depth m'],['opacity','Solidity'],['gap','Ground gap m']])html+=`<label>${label}<input type="number" min="0" step=".01" data-piece="${escape(p.id)}" data-field="${key}" value="${p[key]===null?'':p[key]}"></label>`;
html+=`</div><label class="mini"><input type="checkbox" data-piece="${escape(p.id)}" data-field="measured" ${p.measured?'checked':''}> Width supplied as measured</label></div>`;}
el('materialInputs').innerHTML=html;
el('materialInputs').querySelectorAll('[data-piece]').forEach(inp=>inp.addEventListener('change',()=>edit('piece',{id:inp.dataset.piece,field:inp.dataset.field,value:inp.type==='checkbox'?inp.checked:inp.value})));
}
function chooseTrial(n){if(!current)return;picked=n;drawUI()}
function rerun(){try{current=Field017.run(scene,{route:scene.routes[0].id,pieces:[scene.pieces[0].id]},budget);picked=null;drawPieceEditor();drawUI()}catch(err){el('summary').textContent='Planning error: '+err.message;console.error(err)}}
function drawUI(){const selected=current.selected;const plan=el('view').value==='initial'?current.initial:(picked?current.trace.find(x=>x.step===picked)||selected:selected);
el('version').textContent='REV '+scene.revision;el('badge').textContent=plan.verdict==='REJECTED_UNDER_STATED_MODEL'?'FAILS MODEL':'HOLD · NOT CERTIFIED';el('badge').className='pill '+(plan.failures.length?'fail':'held');
el('overlayTitle').textContent=`${escape(plan.route)} / ${plan.pieces.join(' + ')} · ${plan.operation||'INITIAL'}`;
el('evaluated').textContent=current.evaluated;el('windForce').textContent=plan.force===null?'unknown':plan.force.toFixed(1);el('score').textContent=plan.score.slice(0,3).join('/');
el('iterationCount').textContent=`${current.evaluated} / ${budget} SCREENED`;
el('summary').innerHTML=`<div><strong>${current.improved?'LOWER DECLARED HEURISTIC COST':'NO IMPROVEMENT ESTABLISHED'}</strong><p class="mini">Initial: ${escape(current.initial.id)} (${escape(current.initial.verdict)})<br>After ${current.evaluated} critiques: ${escape(current.selected.id)} (${escape(current.selected.verdict)})</p><p class="mini">An improvement is a change in hypothetical ranking, <b>not</b> a passed construction safety test.</p></div>`;
el('critique').innerHTML=([...(plan.failures||[]),...(plan.warnings||[])].map(x=>`<li>${escape(x)}</li>`).join('')||'<li>No known model failure detected. Real-world safety remains unverified.</li>');
el('timeline').innerHTML=current.trace.map(t=>`<button class="trial ${t.step===picked?'selected':''} ${t.failures.length?'failtrial':'heldtrial'}" data-step="${t.step}"><span class="line1"><b>${t.step}. ${escape(t.operation.replaceAll('_',' ').toLowerCase())}</b><span class="pill ${t.failures.length?'fail':'held'}">${t.failures.length?'FAIL':'HOLD'}</span></span><span class="line2">${escape(t.id)} · ${t.warnings.length} unresolved</span></button>`).join('');
el('timeline').querySelectorAll('[data-step]').forEach(b=>b.onclick=()=>chooseTrial(Number(b.dataset.step)));
el('nextQuestion').textContent=current.nextInput.text;
const c=el('nextControls');c.innerHTML='';const q=current.nextInput;
if(q.kind==='VERIFY_ACCESS'){
 for(const [txt,v] of [['Yes, access remains',true],['No, blocked',false],['Unknown',null]]){
  const b=document.createElement('button');b.textContent=txt;b.onclick=()=>{history.push(structuredClone(scene));const n=structuredClone(scene);const r=n.routes.find(x=>x.id===q.subject);r.access=v;n.revision++;n.events.push({revision:n.revision,kind:'USER_ACCESS_REPORT',route:r.id,value:v});scene=n;rerun()};c.appendChild(b);}
}else if(q.kind==='MEASURE_WIDTH'){
 const inp=document.createElement('input');inp.type='number';inp.min='.01';inp.step='.01';inp.placeholder='Width (meters)';inp.setAttribute('aria-label','Measured width in meters');
 const button=document.createElement('button');button.className='primary';button.textContent='Apply entered width';button.onclick=()=>{if(inp.value){edit('piece',{id:q.subject,field:'width',value:inp.value})}};c.append(inp,button);
}else{
 const btn=document.createElement('button');btn.textContent='Record a new observation (material panel left)';btn.onclick=()=>el('materialInputs').scrollIntoView({behavior:'smooth'});c.append(btn);
}
render3d(plan);
}
function render3d(plan){const cv=el('world'),rect=cv.getBoundingClientRect(),d=Math.min(devicePixelRatio||1,2),W=Math.max(150,rect.width),H=Math.max(210,rect.height);cv.width=Math.round(W*d);cv.height=Math.round(H*d);const ctx=cv.getContext('2d');ctx.setTransform(d,0,0,d,0,0);ctx.clearRect(0,0,W,H);
const pieces=plan.pieces.map(id=>scene.pieces.find(p=>p.id===id)).filter(Boolean);const span=scene.routes.find(r=>r.id===plan.route)?.span||2;const w=pieces.reduce((x,p)=>x+(p.width||0),0);const sc=zoom*(Math.min(W/700,1.15));const center=Math.max(span,w,1.5)/2;
function proj(x,y,z){const xx=x-center,a=xx*Math.cos(orbit)-z*Math.sin(orbit),b=xx*Math.sin(orbit)+z*Math.cos(orbit);return {x:W*.5+a*sc,y:H*.64-y*sc+b*sc*.4}}
function line(a,b,col,width=1,dash=[]){ctx.beginPath();ctx.strokeStyle=col;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();ctx.setLineDash([])}
function quad(points,fill,stroke){ctx.beginPath();ctx.moveTo(points[0].x,points[0].y);for(const v of points.slice(1))ctx.lineTo(v.x,v.y);ctx.closePath();ctx.fillStyle=fill;ctx.fill();ctx.lineWidth=1.4;ctx.strokeStyle=stroke;ctx.stroke()}
for(let x=-1;x<=Math.max(w,span)+1;x+=.5)line(proj(x,0,-2),proj(x,0,2),'#2c565d',.8);
for(let z=-2;z<=2;z+=.5)line(proj(-1,0,z),proj(Math.max(w,span)+1,0,z),'#2c565d',.8);
line(proj(0,0,-.15),proj(span,0,-.15),'#eac087',3,[7,5]);
let x=0;
for(const p of pieces){let width=p.width||0.55,height=p.height||1,gap=p.gap??.15;
const isPrivacy=p.kind==='privacy';const isMesh=p.kind==='mesh';const fill=isPrivacy?'rgba(221,159,126,.78)':isMesh?'rgba(105,190,155,.21)':'rgba(122,158,195,.23)';const col=isPrivacy?'#ebb98d':isMesh?'#92d9ba':'#a7bde6';
quad([proj(x,gap,0),proj(x+width,gap,0),proj(x+width,gap+height,0),proj(x,gap+height,0)],fill,col);
if(!isPrivacy){for(let i=.12;i<1;i+=.12)line(proj(x+width*i,gap,0),proj(x+width*i,gap+height,0),'#b9dcd2',.7)}
line(proj(x,gap,0),proj(x,gap+height,0),col,2);line(proj(x+width,gap,0),proj(x+width,gap+height,0),col,2);
if(gap>0){line(proj(x,0,0),proj(x,gap,0),'#f29a93',2,[3,3]);line(proj(x+width,0,0),proj(x+width,gap,0),'#f29a93',2,[3,3])}
const label=proj(x+width/2,gap+height+.16,0);ctx.textAlign='center';ctx.fillStyle='#d9e9dc';ctx.font='12px monospace';ctx.fillText(p.id,label.x,label.y);
x+=width}
ctx.fillStyle='#d4b489';ctx.font='12px monospace';ctx.textAlign='left';ctx.fillText(`TARGET ${span.toFixed(2)} m (HYPOTHETICAL)`,14,H-32);
ctx.fillStyle='#a2c9c5';ctx.fillText('x = span, y = height, z = illustrative depth',14,H-15);
}
let dragging=false,lastX=0;el('world').addEventListener('pointerdown',e=>{dragging=true;lastX=e.clientX;el('world').setPointerCapture(e.pointerId)});el('world').addEventListener('pointermove',e=>{if(!dragging)return;orbit+=(e.clientX-lastX)*.01;lastX=e.clientX;if(current)drawUI()});el('world').addEventListener('pointerup',()=>dragging=false);
function input(id,apply){el(id).addEventListener('change',e=>{try{apply(e.target.value)}catch(err){alert(err.message)}})}
input('wind',v=>edit('wind',{value:Number(v)}));input('routeOriginal',v=>edit('route',{id:'original',field:'span',value:v}));input('routeMoved',v=>edit('route',{id:'repositioned',field:'span',value:v}));
input('budget',v=>{budget=Number(v);rerun()});
el('accessKnown').onchange=e=>{history.push(structuredClone(scene));const s=structuredClone(scene);s.routes.find(x=>x.id==='repositioned').access=e.target.checked?true:null;s.events.push({revision:++s.revision,kind:'USER_ACCESS_REPORT',value:e.target.checked});scene=s;rerun()};
el('run').onclick=rerun;
for(const n of [1,4,8,16])el('step'+n).onclick=()=>{budget=n;el('budget').value=n;document.querySelectorAll('[id^=step]').forEach(b=>b.classList.toggle('active',b.id==='step'+n));rerun()};
el('reveal').onclick=()=>{edit('piece',{id:'porous',field:'width',value:1.32});el('nextContext').textContent='An invented simulated measurement of 1.32 m was entered. This is NOT a verified width of your materials.'};
el('undo').onclick=()=>{if(!history.length)return;scene=history.pop();rerun()};el('reset').onclick=()=>{scene=Field016.initial();history=[];picked=null;budget=16;el('budget').value=16;el('wind').value=8;el('routeOriginal').value=2.4;el('routeMoved').value=1.5;el('accessKnown').checked=false;el('nextContext').textContent='A measurement or correction triggers another search; it does not prove safe construction.';rerun()};
el('orbitLeft').onclick=()=>{orbit-=.3;drawUI()};el('orbitRight').onclick=()=>{orbit+=.3;drawUI()};el('zoom').oninput=e=>{zoom=Number(e.target.value);drawUI()};el('view').onchange=drawUI;
el('export').onclick=()=>{const payload={kind:'FIELD017_LOCAL_EVIDENCE_AND_TRIALS',source:'local-user-entered-hypotheses',scene,analysis:current,generated_at:stamp,site_geometry_verified:false,safety_certified:false};const a=document.createElement('a');const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});a.href=URL.createObjectURL(blob);a.download='MOTIF_FIELD017_evidence.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),2000)};
el('imgAdd').onchange=e=>{const file=e.target.files?.[0];if(!file||!file.type.startsWith('image/'))return;if(sketchURL)URL.revokeObjectURL(sketchURL);sketchURL=URL.createObjectURL(file);el('sketchBlock').classList.remove('source-hidden');el('sketch').src=sketchURL};
el('jsonAdd').onchange=async e=>{const file=e.target.files?.[0];if(!file)return;try{const o=JSON.parse(await file.text());let input=o.scene||o;if(!Array.isArray(input.routes)||!Array.isArray(input.pieces)||!Number.isFinite(input.wind))throw Error('Expected FIELD-016/017 JSON scene');Field017.assertWorld(input);history.push(structuredClone(scene));scene=input;rerun()}catch(err){alert('Import rejected: '+err.message)}};
window.addEventListener('resize',()=>{if(current)render3d(picked?current.trace.find(x=>x.step===picked)||current.selected:current.selected)});
if(!el('sketch').getAttribute('src'))el('sketchBlock').classList.add('source-hidden');if(!el('photo').getAttribute('src'))el('photoBlock').classList.add('source-hidden');rerun();
})();
