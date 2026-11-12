/* FIELD-010 offline workbench: no network, no automatic photos-to-plan registration. */
(() => {
  'use strict';
  const M = window.MOTIF010;
  let project = JSON.parse(JSON.stringify(window.MOTIF010_FIXTURE));
  let state = M.replay(project);
  let tool = 'select', selected = null, pending = null, drag = null, seq = 1;
  let sketchSrc = window.MOTIF010_PRIVATE_SOURCE || '';
  let solverData = null, interfaceData = null, latest = 0;
  const photos = [];
  const byId = id => document.getElementById(id);
  const svg = byId('board'), svgNS = 'http://www.w3.org/2000/svg';
  const root = byId('objects'), draft = byId('draft');
  const notify = txt => { byId('toast').textContent = txt; };
  const round = x => Math.round(Math.max(0,Math.min(1,x))*1e6)/1e6;
  const signedRound = x => Math.round(x*1e6)/1e6;
  const newElt = (name, attrs={}) => { const e = document.createElementNS(svgNS,name); for(const [k,v] of Object.entries(attrs)) e.setAttribute(k,String(v));return e; };
  const add = (parent,child) => {parent.appendChild(child); return child;};
  const dom = (tag,attrs={},label) => {const el=document.createElement(tag);for(const [k,v] of Object.entries(attrs)){if(k==='class')el.className=v;else el.setAttribute(k,v);}if(label!==undefined)el.textContent=label;return el;};
  const D = obj => JSON.parse(JSON.stringify(obj));
  function uid(prefix='event'){return `${prefix}-${Date.now().toString(36)}-${(seq++).toString(36)}`;}
  function stamp(ev){const entry={id:uid('e'),time:new Date().toISOString(),source:'HUMAN_BOARD_EDIT_NOT_PHYSICAL_OBSERVATION',...ev};project.events.push(entry);
    try {state=M.replay(project);} catch(error){project.events.pop();state=M.replay(project);render();notify('Edit rejected: '+error.message);return;}
    recompute();render();notify(`Recorded ${ev.type} as editable evidence. Physical installation remains unverified.`);}
  function pos(evt){const pt=svg.createSVGPoint();pt.x=evt.clientX;pt.y=evt.clientY;const ctm=svg.getScreenCTM();if(!ctm)return null;const v=pt.matrixTransform(ctm.inverse());return [round(v.x/1000),round(v.y/450)];}
  function ptPixels(p){return [p[0]*1000,p[1]*450];}
  function draw(){root.replaceChildren(); draft.replaceChildren();
    state.items.forEach(i=>{
      const g=add(root,newElt('g',{'data-id':i.id,'class': selected===i.id?'picked':''}));
      const pts=i.points.map(ptPixels),color={current:'#77dfb8',desired:'#f3d282',panel:'#89c0e9',support:'#d5a5ef',access:'#ef9a9a'}[i.kind];
      if(i.kind==='support') {
        const [x,y]=pts[0];add(g,newElt('circle',{cx:x,cy:y,r:11,fill:'#1b2c39',stroke:color,'stroke-width':4,'data-id':i.id,'data-act':'move','class':'node'}));
        add(g,newElt('circle',{cx:x,cy:y,r:4,fill:color,'pointer-events':'none'}));
        const label=add(g,newElt('text',{x:x+14,y:y-10,fill:'#f0f3eb','font-size':17,'pointer-events':'none'}));label.textContent=i.label;
      } else {
        const [[x1,y1],[x2,y2]]=pts;
        add(g,newElt('line',{x1,y1,x2,y2,stroke:'transparent','stroke-width':30,'data-id':i.id,'data-act':'move','class':'item-hit'}));
        const line=add(g,newElt('line',{x1,y1,x2,y2,stroke:color,'stroke-width':i.kind==='desired'?5:4,
          'stroke-dasharray':i.kind==='desired'?'14 7':i.status==='tentative'?'7 6':'',
          'data-id':i.id,'data-act':'move','class':'item-hit'}));
        if(i.kind==='panel')line.setAttribute('stroke-width','9');
        if(i.status==='user_rejected')line.setAttribute('opacity','.27');
        const label=add(g,newElt('text',{x:(x1+x2)/2+6,y:(y1+y2)/2-10,fill:'#f7f3e6','font-size':15,
          'paint-order':'stroke','stroke':'#172431','stroke-width':3,'pointer-events':'none'}));label.textContent=i.label;
        if(selected===i.id){pts.forEach(([x,y],idx)=>add(g,newElt('circle',{cx:x,cy:y,r:8,fill:'#132e37',stroke:'#f8ecc8',
          'stroke-width':3,'data-id':i.id,'data-act':'endpoint','data-index':idx,'class':'endpoint'})));}
      }
    });
    if(pending){const [x,y]=ptPixels(pending);add(draft,newElt('circle',{cx:x,cy:y,r:8,fill:'#d7e57f'}));
      const text=add(draft,newElt('text',{x:x+15,y:y-12,fill:'#e9f8d7','font-size':17}));text.textContent='Choose second endpoint';}
  }
  function setTool(value){tool=value;pending=null;byId('tools').querySelectorAll('[data-tool]').forEach(b=>b.classList.toggle('active',b.dataset.tool===tool));
    notify(tool==='select'?'Drag a segment to move it, or drag a white endpoint handle to reshape it.':
      tool==='support'?'Tap to mark an *unverified candidate* support.':`Tap the beginning and end of a ${tool} segment.`);draw();}
  function moveStart(evt){if(tool!=='select')return;
    const element=evt.target.closest('[data-id]');if(!element)return;
    const id=element.dataset.id; const item=state.items.find(i=>i.id===id);if(!item)return;
    selected=id;renderInspector();draw();
    const start=pos(evt);if(!start)return;
    drag={pointerId:evt.pointerId,target:id,start,last:start,act:element.dataset.act||'move',index:Number(element.dataset.index||0),original:D(item.points)};
    svg.setPointerCapture(evt.pointerId);evt.preventDefault();
  }
  svg.addEventListener('pointerdown', e=>{
    if(tool==='select') {moveStart(e);return;}
    if(e.target.closest('[data-id]'))return;
    const p=pos(e);if(!p)return;
    if(tool==='support') {
      const id=uid('support');stamp({type:'add',item:{id,kind:'support',status:'tentative',label:'Candidate support',movable:false,points:[p]}});
      selected=id;render();return;
    }
    if(!pending){pending=p;draw();notify('Starting point set. Tap the ending point.');return;}
    if(Math.hypot((pending[0]-p[0])*1000,(pending[1]-p[1])*450)<5){notify('Please choose a distinct second endpoint.');return;}
    const id=uid(tool),kind=tool;
    stamp({type:'add',item:{id,kind,label:{current:'Existing section',desired:'Desired boundary',panel:'Salvaged panel',access:'Human access opening'}[kind],
      movable:kind!=='access',status:'tentative',points:[pending,p]}});
    selected=id;pending=null;setTool('select');render();
  });
  svg.addEventListener('pointermove',e=>{
    if(!drag || e.pointerId!==drag.pointerId)return;
    const current=pos(e);if(!current)return;drag.last=current;
    const item=state.items.find(i=>i.id===drag.target);if(!item)return;
    // transient illustration only; no event until release.
    const pts=D(drag.original), dx=current[0]-drag.start[0],dy=current[1]-drag.start[1];
    if(drag.act==='endpoint')pts[drag.index]=[round(current[0]),round(current[1])];
    else pts.forEach(p=>{p[0]=round(p[0]+dx);p[1]=round(p[1]+dy);});
    state.items=state.items.map(i=>i.id===item.id?{...i,points:pts}:i);draw();
    e.preventDefault();
  });
  function finishDrag(e){if(!drag || e.pointerId!==drag.pointerId)return;
    const d=drag;drag=null;try{svg.releasePointerCapture(e.pointerId);}catch(_){}
    state=M.replay(project);
    const p=d.last, delta=[signedRound(p[0]-d.start[0]),signedRound(p[1]-d.start[1])];
    if(Math.hypot(delta[0]*1000,delta[1]*450)<2){render();return;}
    if(d.act==='endpoint')stamp({type:'endpoint',target:d.target,index:d.index,point:p});
    else stamp({type:'move',target:d.target,delta});
  }
  svg.addEventListener('pointerup',finishDrag);
  svg.addEventListener('pointercancel',e=>{drag=null;state=M.replay(project);render();});
  function inputField(name,type,value,callback,extras={}){
    const l=dom('label',{class:'field'});l.append(dom('span',{},name));const inp=dom('input',{type,...extras});inp.value=value??'';
    inp.addEventListener('change',()=>callback(inp.value));l.append(inp);return l;
  }
  function selectField(name,opts,val,callback){const l=dom('label',{class:'field'});l.append(dom('span',{},name));const inp=dom('select');
    opts.forEach(([k,text])=>{const o=dom('option',{value:k},text);inp.append(o);});inp.value=val;inp.addEventListener('change',()=>callback(inp.value));l.append(inp);return l;}
  function renderInspector(){const host=byId('inspector');host.replaceChildren(); const item=state.items.find(i=>i.id===selected);
    if(!item){host.append(dom('p',{class:'small'},'Tap a line, endpoint or support to inspect. Create or correct the visual model without describing it in words.'));return;}
    host.append(dom('strong',{},item.label));host.append(inputField('Name','text',item.label,v=>stamp({type:'set',target:item.id,prop:'label',value:v.slice(0,120)})));
    const nudges=dom('div',{class:'row',style:'margin:10px 0'});nudges.append(dom('span',{class:'small'},'Nudge:'));
    [['←',-.015,0],['→',.015,0],['↑',0,-.03],['↓',0,.03]].forEach(([txt,dx,dy])=>{const b=dom('button',{type:'button',class:'mini','aria-label':'Move '+txt},txt);
      b.addEventListener('click',()=>stamp({type:'move',target:item.id,delta:[dx,dy]}));nudges.append(b);});host.append(nudges);
    host.append(selectField('Role',[['desired','Desired (new route)'],['current','Existing fence'],['panel','Salvaged panel'],['access','Access gap'],['support','Support node']],item.kind,
      v=>stamp({type:'set',target:item.id,prop:'kind',value:v})));
    host.append(selectField('Evidence status',[['tentative','Tentative / not confirmed'],['user_confirmed','Confirmed by you (drawing only)'],['user_rejected','Rejected'] ],item.status,
      v=>stamp({type:'set',target:item.id,prop:'status',value:v})));
    const check=dom('label',{class:'check'});const cb=dom('input',{type:'checkbox'});cb.checked=item.movable;
    cb.addEventListener('change',()=>stamp({type:'set',target:item.id,prop:'movable',value:cb.checked}));check.append(cb,dom('span',{},'Moveable / reusable module'));host.append(check);
    if(item.points.length===2) {
      const endpoints=dom('div',{class:'split'});item.points.forEach((p,idx)=>{const field=dom('label',{class:'field'},'Endpoint '+(idx+1)+' (x,y %)');
        const inp=dom('input',{type:'text','aria-label':'Endpoint '+(idx+1)+' coordinates as percent'});inp.value=(p[0]*100).toFixed(1)+', '+(p[1]*100).toFixed(1);
        inp.addEventListener('change',()=>{const xy=inp.value.split(',').map(v=>Number(v.trim())/100);
          if(xy.length!==2||xy.some(v=>!Number.isFinite(v)||v<0||v>1)){notify('Enter x%, y% values from 0 to 100.');return;}
          stamp({type:'endpoint',target:item.id,index:idx,point:xy});});
        field.append(inp);endpoints.append(field);});host.append(endpoints);
      const measurement=state.measurements[item.id];host.append(dom('div',{class:'separate'}));
      host.append(dom('span',{class:'micro'},`Drawn span ≈ ${M.span(item,state.sketch_size).toFixed(0)} sketch pixels · not feet.`));
      const measureRow=dom('div',{class:'split'});
      const lengthBox=dom('label',{class:'field'},'Length (optional)'); const lenInput=dom('input',{id:'lenInput',type:'number',min:'0.01',step:'.1',placeholder:'unknown'});
      lenInput.value=measurement?measurement.value:'';lengthBox.append(lenInput);measureRow.append(lengthBox);
      const unitBox=dom('label',{class:'field'},'Unit');const unitInput=dom('select',{id:'unitInput'});[['ft','ft'],['m','m']].forEach(([id,name])=>unitInput.append(dom('option',{value:id},name)));
      unitInput.value=measurement?measurement.unit:'ft';unitBox.append(unitInput);measureRow.append(unitBox);host.append(measureRow);
      const qualityBox=dom('label',{class:'field'},'Basis');const quality=dom('select',{id:'qualityInput'});
      [['rough_guess','Rough estimate (cannot calibrate)'],['user_measured','Personally measured (conditional anchor)']].forEach(([id,txt])=>quality.append(dom('option',{value:id},txt)));
      quality.value=measurement?measurement.quality:'rough_guess';qualityBox.append(quality);host.append(qualityBox);
      const submit=dom('button',{type:'button',class:'primary'},'Record length');submit.addEventListener('click',()=>{
        const n=Number(lenInput.value);if(!Number.isFinite(n)||n<=0){notify('Enter a positive length or leave the measurement unknown.');return;}
        stamp({type:'measure',target:item.id,value:n,unit:unitInput.value,quality:quality.value});});host.append(submit);
    }
    const rm=dom('button',{type:'button',class:'danger mini',style:'margin:12px 0 0'},'Remove from editable board');
    rm.addEventListener('click',()=>{stamp({type:'remove',target:item.id});selected=null;render();});host.append(rm);
    host.append(dom('div',{class:'note warn'},'Board edits are human statements about a digital model, not evidence that a physical fence has been built or tested.'));
  }
  function renderRatioControls(){const lines=state.items.filter(i=>i.points.length===2),target=byId('ratioTarget'),other=byId('ratioOther');
    const oldA=target.value,oldB=other.value;target.replaceChildren(dom('option',{value:''},'— select target —'));
    other.replaceChildren(dom('option',{value:''},'— reference —'));
    lines.forEach(i=>{target.append(dom('option',{value:i.id},i.label));other.append(dom('option',{value:i.id},i.label));});
    target.value=lines.some(i=>i.id===oldA)?oldA:'';other.value=lines.some(i=>i.id===oldB)?oldB:'';
    byId('proportional').checked=state.proportional;
    if(state.tolerance!==null)byId('tolerance').value=Math.round(state.tolerance*100);
    byId('ratios').textContent=state.relations.length?state.relations.map(r=>`${r.target} ≈ ${r.ratio}× ${r.other} (human relation, not measured)`).join(' · '):'No relative-length constraints entered.';
  }
  function renderMeasurementQueue(){const host=byId('measurementQueue');host.replaceChildren();const lines=state.items.filter(i=>i.points.length===2);
    if(!lines.length){host.append(dom('span',{class:'micro'},'No segments available yet.'));return;}
    lines.slice(0,30).forEach(i=>{const row=dom('div',{class:'row',style:'padding:4px 0;border-bottom:1px solid #314854'});
      const m=state.measurements[i.id];row.append(dom('span',{class:'small',style:'flex:1'},i.label+': '+(m?m.value+' '+m.unit+' ['+m.quality+']':'_____ ft / m')));
      const b=dom('button',{class:'mini',type:'button'},'Edit');b.addEventListener('click',()=>{selected=i.id;render();byId('lenInput')?.focus();});row.append(b);host.append(row);});
  }
  function renderEvents(){byId('version').textContent=`Edit ${state.version}`;byId('editCount').textContent=`${project.events.length} ledger entries`;
    const container=byId('events');container.replaceChildren();
    project.events.slice().reverse().slice(0,16).forEach(e=>container.append(dom('div',{},`${e.id.slice(-5)} · ${e.type} ${e.target||e.item?.id||''}`)));
  }
  function tile(title,body,footer){const div=dom('div',{class:'tile'});div.append(dom('strong',{},title),dom('p',{},body));if(footer)div.append(dom('small',{},footer));return div;}
  function renderSolver(v){const root=byId('solverTiles');root.replaceChildren();v.hypotheses.forEach(h=>root.append(tile(h.title,h.why,'HOLD: '+h.hold)));
    const est=v.estimates;if(est.length){const desc=est.map(e=>`${e.id}: ${e.low}–${e.high} ${e.unit}`).join(' · ');
      root.append(tile('Reference / conditional lengths',desc,'Human-entered reference is direct; other figures assume approximate proportionality. Not surveyed.'));}
    else if(v.ratios.length)root.append(tile('Drawn length ratios',v.ratios.map(x=>`${x.id} ≈ ${x.value}× ${x.ref}`).join(' · '),'Paper geometry only.'));
    if(v.ratioCues?.length) root.append(tile('Your rough ratio relationships',v.ratioCues.map(r=>r.implied_nominal?`${r.target} ≈ ${r.implied_nominal} ${r.unit}`:`${r.target} ≈ ${r.ratio}× ${r.other}`).join(' · '),'Hypothetical relation; no independent physical verification.'));
    v.warnings.forEach(w=>root.append(tile('Scale unresolved',w,'No physical length claim.')));
    byId('solverState').textContent=`v${v.version}`;
  }
  function actionHandler(toolName){
    if(toolName==='proportions'){byId('proportional').focus();byId('proportional').scrollIntoView({block:'center',behavior:'smooth'});return;}
    if(toolName==='measure'){
      const first=state.items.find(i=>i.points.length===2);
      if(first){selected=first.id;render();byId('lenInput')?.focus();}else notify('Add a segment before measuring it.');return;
    }
    if(toolName==='select'||toolName==='mobility'){setTool('select');notify('Select an existing section to mark it movable or fixed.');return;}
    setTool(toolName);
  }
  function renderInterface(v){const root=byId('interfaceTiles');root.replaceChildren();v.actions.forEach(a=>{
    const t=tile(a.title,a.why,'Optional · ranked by relevance, not validated information gain');
    const b=dom('button',{class:'mini',type:'button'},'Use this input');b.addEventListener('click',()=>actionHandler(a.tool));t.append(b);root.append(t);
    });byId('interfaceState').textContent=`v${v.version}`;
  }
  function updateSummary(){const v=solverData,host=byId('scaleSummary');if(!v)return;
    if(v.estimates.length){host.textContent=`Conditional estimates for ${v.estimates.length} desired span(s). No installed dimensions verified.`;host.className='note';}
    else {host.textContent=state.proportional?'No independently entered measured span; geometry remains unscaled.':'Drawn proportions only. The sketch is not asserted to be at physical scale.';host.className='note warn';}
  }
  function render(){state=M.replay(project);if(selected && !state.items.some(i=>i.id===selected))selected=null;
    draw();renderInspector();renderRatioControls();renderMeasurementQueue();renderEvents();updateSummary();}
  const workers=[];
  function makeWorker(fn){
    const source=`const span=${M.span.toString()};const compute=${fn.toString()};onmessage=e=>{try{postMessage({version:e.data.version,value:compute(e.data.state)})}catch(err){postMessage({version:e.data.version,error:String(err)})}};`;
    const url=URL.createObjectURL(new Blob([source],{type:'text/javascript'}));
    const worker=new Worker(url);URL.revokeObjectURL(url);return worker;
  }
  try {workers.push(makeWorker(M.computeSolver),makeWorker(M.computeInterface));}
  catch(ex){workers.forEach(w=>w.terminate());workers.length=0;}
  const branchFns=[M.computeSolver,M.computeInterface];
  function receive(idx,msg){if(msg.version!==latest)return;
    if(msg.error){notify('Reasoning branch '+idx+' error: '+msg.error);return;}
    if(idx===0){solverData=msg.value;renderSolver(solverData);updateSummary();}
    else{interfaceData=msg.value;renderInterface(interfaceData);}
  }
  workers.forEach((w,idx)=>w.onmessage=e=>receive(idx,e.data));
  function recompute(){latest=state.version;const v=latest;const snapshot=D(state);
    [0,1].forEach(idx=>{
      if(workers.length===2)workers[idx].postMessage({version:v,state:snapshot});
      else setTimeout(()=>{try{receive(idx,{version:v,value:branchFns[idx](snapshot)});}catch(ex){notify(String(ex));}},idx*7);
    });
  }
  document.querySelectorAll('[data-tool]').forEach(b=>b.addEventListener('click',()=>setTool(b.dataset.tool)));
  byId('undoBtn').addEventListener('click',()=>{const reverted=new Set(project.events.filter(e=>e.type==='revert').map(e=>e.target_event));
    const prior=project.events.slice().reverse().find(e=>e.type!=='revert' && !reverted.has(e.id));
    if(!prior){notify('No active edit to undo.');return;}
    stamp({type:'revert',target_event:prior.id});});
  byId('proportional').addEventListener('change',()=>stamp({type:'proportional',value:byId('proportional').checked,
    tolerance:Math.min(.85,Math.max(0,Number(byId('tolerance').value)/100||0))}));
  byId('tolerance').addEventListener('change',()=>{if(state.proportional)stamp({type:'proportional',value:true,
    tolerance:Math.min(.85,Math.max(0,Number(byId('tolerance').value)/100||0))});});
  byId('ratioBtn').addEventListener('click',()=>{
    const target=byId('ratioTarget').value,other=byId('ratioOther').value,value=Number(byId('ratioValue').value);
    if(!target||!other||target===other||!Number.isFinite(value)||value<.05||value>20){notify('Choose two distinct segments and a valid positive multiplier.');return;}
    stamp({type:'ratio',target,other,value});});
  byId('exportBtn').addEventListener('click',()=>download('motif-field010-board.json',JSON.stringify(project,null,2),'application/json'));
  byId('svgBtn').addEventListener('click',()=>{
    const x=svg.cloneNode(true);const src=x.querySelector('#sourceImage');
    if(!sketchSrc && src)src.remove();
    x.setAttribute('xmlns',svgNS);x.setAttribute('width','1400');x.setAttribute('height','630');
    download('motif-field010-annotated.svg',new XMLSerializer().serializeToString(x),'image/svg+xml');
    notify('Exported visual diagram. If you loaded a sketch, the SVG includes its pixels: treat it as private.');
  });
  function download(name,content,mime){const url=URL.createObjectURL(new Blob([content],{type:mime}));const a=dom('a',{href:url,download:name});document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1200);}
  function loadSketch(src){sketchSrc=src;byId('sourceImage').setAttribute('href',src);}
  byId('sketchUpload').addEventListener('change',e=>{
    const file=e.target.files?.[0];if(!file)return;if(file.size>15*1024*1024||!/^image\/(png|jpeg|webp)$/.test(file.type)){notify('Sketch must be PNG/JPEG/WebP under 15MB.');return;}
    const reader=new FileReader();reader.onload=()=>{
      if(project.base.source==='synthetic'){
        project.base.source='user_sketch';project.base.items=[];project.events=[];selected=null;seq=1;
      }
      project.base.sketch_name=file.name;
      loadSketch(String(reader.result));state=M.replay(project);recompute();render();notify('Original sketch preserved as a non-scaling background. Trace corrected geometry directly; no automatic interpretation claimed.');
    };reader.readAsDataURL(file);
  });
  function displayPhotos(){const root=byId('photolist');root.replaceChildren();photos.forEach((p,idx)=>{
    const b=dom('button',{type:'button',title:p.name});const im=dom('img',{alt:'Photo '+(idx+1)+' thumbnail',src:p.url});b.append(im,dom('span',{class:'micro'},p.name.slice(0,13)));
    b.addEventListener('click',()=>{byId('photoViewer').src=p.url;byId('photoViewer').alt=p.name;
      byId('photoNotice').textContent=`${p.name} — separate photo witness; not registered to sketch coordinates.`;});root.append(b);
  });}
  byId('photoUpload').addEventListener('change',e=>{Array.from(e.target.files||[]).slice(0,20).forEach(file=>{
    if(!/^image\/(png|jpeg|webp)$/.test(file.type)||file.size>15*1024*1024)return;
    const rd=new FileReader();rd.onload=()=>{photos.push({name:file.name,url:rd.result});displayPhotos();};rd.readAsDataURL(file);
  });});
  byId('importBtn').addEventListener('click',()=>byId('importFile').click());
  byId('importFile').addEventListener('change',e=>{
    const file=e.target.files?.[0];if(!file)return;if(file.size>2e6){notify('Board JSON too large.');return;}
    const reader=new FileReader();reader.onload=()=>{try{const incoming=JSON.parse(reader.result);M.replay(incoming);
      project=incoming;selected=null;seq=project.events.length+1;state=M.replay(project);recompute();render();
      notify('Board loaded. If it used a private sketch, select that sketch again; images are intentionally excluded from JSON exports.');
    }catch(ex){notify('Invalid board JSON: '+ex.message);}};reader.readAsText(file);
  });
  if (sketchSrc)loadSketch(sketchSrc);
  if (Array.isArray(window.MOTIF010_PRIVATE_PHOTOS)) {
    window.MOTIF010_PRIVATE_PHOTOS.forEach(p=>photos.push(p));displayPhotos();
  }
  render();recompute();
  window.MOTIF010_DEBUG = {getProject:()=>D(project),getState:()=>D(state),getBranches:()=>D({solverData,interfaceData}),
    apply:stamp, tool:setTool};
})();
