/* FIELD-010 offline workbench: no network, no automatic photos-to-plan registration. */
(() => {
  'use strict';
  const M = window.MOTIF010;
  let project = JSON.parse(JSON.stringify(window.MOTIF010_FIXTURE));
  let state = M.replay(project);
  let tool = 'select', selected = null, pending = null, drag = null, seq = 1;
  let sketchSrc = window.MOTIF010_PRIVATE_SOURCE || '';
  let solverData = null, interfaceData = null, latest = 0;
  let sketchFile = null, sketchDigest = null, lastDraft = null, uploadVersion = 0;
  const AUTODRAFT = window.MOTIF011;
  const MATERIAL = window.MOTIF012;
  const PHOTO_SCAN = window.MOTIF013_SCAN;
  const PROPOSALS = window.MOTIF013_PLAN;
  let activePhoto=null, photoRegion=null, regionStart=null, ghost=null, materialTicket=0;
  function dataDigest(bytes){
    if(typeof crypto!=='undefined'&&crypto.subtle)return crypto.subtle.digest('SHA-256',bytes).then(data=>Array.from(new Uint8Array(data),x=>x.toString(16).padStart(2,'0')).join(''));
    return Promise.resolve(AUTODRAFT.sha256Bytes(new Uint8Array(bytes)));
  }
  async function shaDataURL(str){
    const part=str.split(',');if(part.length!==2||!part[0].includes('base64'))throw Error('Sketch image must be base64 encoded');
    const s=atob(part[1]);const bytes=new Uint8Array(s.length);for(let i=0;i<s.length;i++)bytes[i]=s.charCodeAt(i);
    return dataDigest(bytes.buffer);
  }
  async function decodeToPixels(source){
    const img=new Image();img.src=source;
    await img.decode();
    const max=1050,k=Math.min(1,max/Math.max(img.naturalWidth,img.naturalHeight));
    const w=Math.max(90,Math.round(img.naturalWidth*k)),h=Math.max(90,Math.round(img.naturalHeight*k));
    const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;
    const ctx=canvas.getContext('2d',{willReadFrequently:true});ctx.drawImage(img,0,0,w,h);
    return {pixels:ctx.getImageData(0,0,w,h).data,width:w,height:h};
  }
  function installDraft(packet){
    if(!AUTODRAFT)throw Error('Missing FIELD-011 draft engine');
    AUTODRAFT.validate(packet,sketchDigest);
    if(project.base.source==='synthetic')throw Error('Sketch must be loaded first');
    if(lastDraft && lastDraft.source_sha256!==packet.source_sha256)throw Error('Draft belongs to a different image');
    const entries=AUTODRAFT.toEvents(project,packet,()=>uid('guess'));
    if(project.events.length+entries.length>5000)throw Error('Event limit exceeded');
    const snapshot=D(project);
    project.events.push(...entries);
    try{state=M.replay(project);}catch(error){project=snapshot;state=M.replay(project);throw error;}
    lastDraft=packet;recompute();render();
    notify(`${packet.items.length} tentative visual hypotheses; ${entries.length} new editable strokes. None is a verified route or dimension.`);
    return entries.length;
  }
  async function runAutoDraft(){
    if(!sketchSrc){notify('Load a source sketch before drafting.');return;}
    const ticket=uploadVersion;byId('draftCount').textContent='Inspecting local pixels…';
    try {
      if(!sketchDigest)sketchDigest=await shaDataURL(sketchSrc);
      if(lastDraft?.source_sha256===sketchDigest){
        byId('draftCount').textContent=`${state.items.filter(i=>i.evidence && i.status!=='tentative').length}/${state.items.filter(i=>i.evidence).length} reviewed`;
        notify('This sketch already has tentative proposals. Edit or reject them rather than duplicating a second detector pass.');return;
      }
      const data=await decodeToPixels(sketchSrc);if(ticket!==uploadVersion)return;
      // Only local OpenCV-style browser short-stroke detector. No VLM or server.
      const packet=AUTODRAFT.fromRGBA(data.pixels,data.width,data.height,sketchDigest,
        {desiredDottedRule:false,sourceId:'sketch-1'});
      // A preview with zero detected lines is an honest HOLD, not a fabricated route.
      installDraft(packet);
      if(!packet.items.length)notify('No defensible dashed stroke group identified. Trace directly or import an explicitly sourced local vision draft.');
    }catch(ex){notify('Automatic visual draft held: '+ex.message);byId('draftCount').textContent='HOLD';}
  }

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
    if(ghost){
      const pts=ghost.points.map(ptPixels),isNode=ghost.kind==='support';
      if(isNode){const [x,y]=pts[0];add(draft,newElt('circle',{cx:x,cy:y,r:19,fill:'#e5c77e', 'fill-opacity':'.12',stroke:'#e5c77e','stroke-width':4,'stroke-dasharray':'5 4'}));}
      else {const [[x1,y1],[x2,y2]]=pts;
        add(draft,newElt('line',{x1,y1,x2,y2,stroke:'#f3bd70','stroke-width':13,'stroke-opacity':'.78','stroke-dasharray':'12 7','pointer-events':'none'}));}
      const [x,y]=pts[0];const gt=add(draft,newElt('text',{x:x+13,y:y-17,fill:'#ffe2a7','font-size':16,'paint-order':'stroke',stroke:'#132430','stroke-width':3}));
      gt.textContent='WHAT IF? Unscaled candidate · no physical fit';
    }
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
    host.append(dom('strong',{},item.label));
    if(item.evidence){
      const e=item.evidence;
      host.append(dom('div',{class:'note warn'},`Tentative source ${e.method||'unverified model'} · ${e.semantic_status||'unknown'} · original pixels preserved. Grouped strokes need not form a physically continuous boundary. Source pin ${String(e.source_sha256||'').slice(0,12)}.`));
    }
    host.append(inputField('Name','text',item.label,v=>stamp({type:'set',target:item.id,prop:'label',value:v.slice(0,120)})));
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
  function renderDraftReview(){
    const root=byId('draftReview');if(!root)return;
    root.replaceChildren();const guesses=state.items.filter(i=>i.evidence && i.evidence.semantic_status==='POSSIBLE_MARK__NOT_CONFIRMED_BOUNDARY');
    const reviewed=guesses.filter(x=>x.status!=='tentative').length;
    byId('draftCount').textContent=guesses.length?`${reviewed}/${guesses.length} reviewed`:'No candidates';
    guesses.slice(0,18).forEach(i=>{
      const t=tile(i.label,`Status: ${i.status}. Provenance: ${i.evidence.method}. Not a verified intended fence.`,
                   'Edit it directly, then choose confirm or reject.');
      const row=dom('div',{class:'row'});
      const edit=dom('button',{type:'button',class:'mini'},'Edit line');edit.addEventListener('click',()=>{selected=i.id;setTool('select');render();});row.append(edit);
      if(i.status==='tentative'){
        const yes=dom('button',{type:'button',class:'mini'},'Confirm mark');yes.addEventListener('click',()=>stamp({type:'set',target:i.id,prop:'status',value:'user_confirmed'}));row.append(yes);
        const no=dom('button',{type:'button',class:'mini danger'},'Reject');no.addEventListener('click',()=>stamp({type:'set',target:i.id,prop:'status',value:'user_rejected'}));row.append(no);
      }
      t.append(row);root.append(t);
    });
    if(!guesses.length)root.append(dom('p',{class:'small'},'No tentative line groups found. Use the canvas or import a local model proposal packet.'));
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
    if(toolName==='photo-region'||toolName==='material-preview'){byId('objectPhotoCanvas').scrollIntoView({block:'center',behavior:'smooth'});notify('Tag a visible object in the photograph, or preview a material beside an intended route.');return;}
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
    draw();renderInspector();renderRatioControls();renderMeasurementQueue();renderEvents();renderDraftReview();renderMaterials();renderPossibilities();updateSummary();}
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
  function recompute(){latest=`${uploadVersion}:${state.version}`;const v=latest;const snapshot=D(state);
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
    if(project.base.source==='user_sketch' && project.events.length && !window.confirm('Replace the source sketch? Existing edits belong to the old image and will be cleared. Export board JSON first to save them.')){
      e.target.value='';notify('Original board preserved; choose a source replacement only after saving edits.');return;
    }
    const reader=new FileReader();reader.onload=()=>{
      project.base.source='user_sketch';project.base.items=[];project.events=[];selected=null;seq=1;
      project.base.sketch_name=file.name;sketchFile=file;sketchDigest=null;lastDraft=null;ghost=null;uploadVersion++;
      loadSketch(String(reader.result));state=M.replay(project);recompute();render();
      notify('Sketch loaded locally. Inspecting pixels and proposing editable tentative marks.');
      runAutoDraft();
    };reader.readAsDataURL(file);
  });
  function photoCanvasPos(e){
    const s=byId('objectPhotoCanvas'), pt=s.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;
    const m=s.getScreenCTM();if(!m)return null;const xy=pt.matrixTransform(m.inverse());
    const vb=s.viewBox.baseVal;return [Math.max(0,Math.min(1,xy.x/vb.width)),Math.max(0,Math.min(1,xy.y/vb.height))];
  }
  function regionBox(a,b){return [Math.min(a[0],b[0]),Math.min(a[1],b[1]),Math.max(a[0],b[0]),Math.max(a[1],b[1])].map(round);}
  function svgBox(elt,bbox){const vb=byId('objectPhotoCanvas').viewBox.baseVal;
    elt.setAttribute('x',bbox[0]*vb.width);elt.setAttribute('y',bbox[1]*vb.height);
    elt.setAttribute('width',(bbox[2]-bbox[0])*vb.width);elt.setAttribute('height',(bbox[3]-bbox[1])*vb.height);
  }
  async function scanMaterialPhoto(p,{force=false}={}){
    if(!PHOTO_SCAN||!p)throw Error('Missing local photo scan or photograph');
    if(p.scanDone&&!force)return 0;
    if(!p.digest)p.digest=await shaDataURL(p.url);
    if(!p.id)p.id='photo-'+photos.indexOf(p);
    const data=await decodeToPixels(p.url);
    // Reusable deterministic pixel-region detector: NOT a material/object labeler.
    const regions=PHOTO_SCAN.scanRGBA(data.pixels,data.width,data.height,{maxCandidates:4});
    const old=new Set(state.materials.map(m=>m.id));let added=0;
    for(let i=0;i<regions.length;i++){
      const id=`material-cv-${p.digest.slice(0,10)}-${p.id.replace(/[^a-zA-Z0-9_-]/g,'').slice(0,20)}-${i}`;
      if(old.has(id))continue;
      const entry=PHOTO_SCAN.materialRegion(regions[i],p.id,p.digest,id);
      MATERIAL.validateMaterial(entry);
      stamp({type:'material_add',material:entry});added++;
    }
    p.scanDone=true;
    if(activePhoto===p)renderMaterials();
    return added;
  }
  async function scanAllPhotos(){
    const status=byId('autoPhotoStatus');
    if(!photos.length){notify('Add a photograph first.');return;}
    byId('autoAllPhotosBtn').disabled=true;let total=0,completed=0;
    try {
      for(const p of photos){
        status.textContent=`Scanning ${++completed}/${photos.length} locally…`;
        total+=await scanMaterialPhoto(p);
        await new Promise(resolve=>setTimeout(resolve,0));
      }
      status.textContent=`${total} unclassified pixel regions proposed across ${photos.length} photo(s).`;
      notify(status.textContent+' Regions are not identified objects. Select one and correct its role.');
    }catch(err){status.textContent='Scan held: '+err.message;notify(status.textContent);}
    finally{byId('autoAllPhotosBtn').disabled=false;}
  }
  function renderPossibilities(){
    const host=byId('possibilityTiles');if(!host||!PROPOSALS)return;
    host.replaceChildren();const report=PROPOSALS.evaluate(state);
    const header=dom('p',{class:'micro'},`${report.candidate_count} conditional possibilities · ${report.questions.length} clarification opportunities · no physical fit checked`);
    host.append(header);
    for(const p of report.candidates.slice(0,7)){
      const card=tile(p.title,p.status,p.hold[0]);
      if(p.material_id && p.route_id){
        const m=state.materials.find(m=>m.id===p.material_id),target=state.items.find(t=>t.id===p.route_id);
        if(m&&target){
          const btn=dom('button',{type:'button',class:'mini'},'Preview unscaled');
          btn.addEventListener('click',()=>previewMaterial(m,target));card.append(btn);
        }
      }else card.append(dom('small',{},'Idea only — no source geometry changed.'));
      host.append(card);
    }
    if(report.questions.length){
      const q=report.questions[0];host.append(tile('Most useful missing input',q.question,`Material ${q.material_id} · no prose explanation required: edit the photo-region card.`));
    }
  }
  async function selectPhoto(p){
    const ticket=++materialTicket;activePhoto=p;photoRegion=null;regionStart=null;
    if(!p.digest){try{p.digest=await shaDataURL(p.url);}catch(err){notify('Photo hash failed: '+err.message);return;}}
    if(ticket!==materialTicket)return;
    const im=new Image();im.src=p.url;
    try{await im.decode();}catch(err){notify('Photo decoding failed.');return;}
    if(ticket!==materialTicket)return;
    p.id ||= 'photo-'+photos.indexOf(p);p.w=im.naturalWidth;p.h=im.naturalHeight;
    byId('objectPhotoCanvas').setAttribute('viewBox',`0 0 ${p.w} ${p.h}`);
    for(const a of ['x','y'])byId('objectPhotoImage').setAttribute(a,'0');
    byId('objectPhotoImage').setAttribute('width',p.w);byId('objectPhotoImage').setAttribute('height',p.h);
    byId('objectPhotoImage').setAttribute('href',p.url);
    byId('photoViewer').src=p.url;byId('photoViewer').alt=p.name;
    byId('photoNotice').textContent=`${p.name} — separate source. No automatic location on sketch.`;
    byId('regionHint').textContent='Drag around an object directly on this photo. Bounds are PHOTO pixels, not yard coordinates.';
    renderMaterials();
    // Progressive, on-device region candidates. No semantic model or external call.
    if(!p.scanDone) {try{const n=await scanMaterialPhoto(p);if(ticket===materialTicket)byId('autoPhotoStatus').textContent=`${n} unclassified regions proposed for selected photo.`;}
      catch(ex){notify('Automatic photo-region scan held: '+ex.message);}}
  }
  const photoBoard=byId('objectPhotoCanvas');
  photoBoard.addEventListener('pointerdown',e=>{
    if(!activePhoto?.digest)return;const pt=photoCanvasPos(e);if(!pt)return;
    regionStart=pt;photoRegion=null;
    photoBoard.setPointerCapture(e.pointerId);svgBox(byId('objectRegionDraft'),[pt[0],pt[1],pt[0],pt[1]]);e.preventDefault();
  });
  photoBoard.addEventListener('pointermove',e=>{
    if(!regionStart)return;const pt=photoCanvasPos(e);if(pt)svgBox(byId('objectRegionDraft'),regionBox(regionStart,pt));
  });
  photoBoard.addEventListener('pointerup',e=>{
    if(!regionStart)return;const pt=photoCanvasPos(e)||regionStart;
    const box=regionBox(regionStart,pt);regionStart=null;
    if(box[2]-box[0]<.025||box[3]-box[1]<.025){byId('regionHint').textContent='Select a larger region around a visible object.';photoRegion=null;return;}
    photoRegion=box;svgBox(byId('objectRegionDraft'),box);
    byId('regionHint').textContent=`Region selected (${Math.round((box[2]-box[0])*100)}% × ${Math.round((box[3]-box[1])*100)}% of this photo). Label or classify it; nothing placed on the yard.`;
  });
  photoBoard.addEventListener('pointercancel',()=>{regionStart=null;});
  byId('addMaterialBtn').addEventListener('click',()=>{
    if(!activePhoto?.digest||!photoRegion){notify('Select a photo and drag around one visible material first.');return;}
    const role=byId('materialRole').value,label=byId('materialLabel').value.trim()||'Unidentified salvaged object';
    const material={id:uid('material'),label,role,status:'tentative',mobility:'unknown',
      source_frame:'photo_normalized',photo_id:activePhoto.id,photo_sha256:activePhoto.digest,bbox:photoRegion,
      provenance:'HUMAN_REGION_TAG',registered_to_sketch:false,certified_safe:false,width:null};
    try{MATERIAL.validateMaterial(material);}catch(err){notify('Object held: '+err.message);return;}
    stamp({type:'material_add',material});photoRegion=null;svgBox(byId('objectRegionDraft'),[0,0,0,0]);
  });
  byId('autoPhotoBtn').addEventListener('click',async()=>{if(!activePhoto)return notify('Select a photo first.');
    try{const n=await scanMaterialPhoto(activePhoto);notify(`${n} new local visual regions. Review before assigning object roles.`);}
    catch(e){notify('Photo scan held: '+e.message);}});
  byId('autoAllPhotosBtn').addEventListener('click',scanAllPhotos);
  byId('materialImportBtn').addEventListener('click',()=>byId('materialImportFile').click());
  byId('materialImportFile').addEventListener('change',async e=>{
    const file=e.target.files?.[0];if(!file)return;
    if(file.size>500000){notify('Model packet too large.');return;}
    try{
      const packet=JSON.parse(await file.text());
      const packets=packet?.schema==='motif.field013.batch.v1'?packet.packets:[packet];
      if(!Array.isArray(packets)||packets.length>20)throw Error('Invalid bounded photo packet set');
      const existing=new Set(state.materials.map(m=>m.id));let n=0;
      for(const part of packets){
        const p=photos.find((photo,idx)=>(photo.id||('photo-'+idx))===part.photo_id);
        if(!p)throw Error('No loaded photograph matches packet ID: '+part.photo_id);
        p.id||='photo-'+photos.indexOf(p);
        if(!p.digest)p.digest=await shaDataURL(p.url);
        MATERIAL.validatePacket(part,p.id,p.digest);
      }
      for(const part of packets)for(const m of part.items){
        if(existing.has(m.id))continue;stamp({type:'material_add',material:m});existing.add(m.id);n++;
      }
      notify(`${n} tentative local model photo objects imported. Source checks passed; labels, physical dimensions and usefulness remain unverified.`);
    }catch(err){notify('Vision candidates held: '+err.message);}
  });
  function renderPhotoRegions(){const host=byId('objectPhotoRegions');host.replaceChildren();
    if(!activePhoto?.digest)return;
    const vb=photoBoard.viewBox.baseVal;
    state.materials.filter(m=>m.photo_sha256===activePhoto.digest&&m.photo_id===activePhoto.id).forEach(m=>{
      const rect=add(host,newElt('rect',{x:m.bbox[0]*vb.width,y:m.bbox[1]*vb.height,
        width:(m.bbox[2]-m.bbox[0])*vb.width,height:(m.bbox[3]-m.bbox[1])*vb.height,fill:'none',
        stroke:m.status==='user_rejected'?'#d17c7a':m.status==='user_confirmed'?'#83e1ae':'#e7d687',
        'stroke-width':Math.max(2,vb.width/280),'stroke-dasharray':m.status==='tentative'?'6 4':''}));
      const t=add(host,newElt('text',{x:m.bbox[0]*vb.width,y:Math.max(17,m.bbox[1]*vb.height-5),
        fill:'#edf2bf','font-size':Math.max(12,vb.width/70),'paint-order':'stroke',stroke:'#18303b','stroke-width':3}));
      t.textContent=m.label.slice(0,30);
    });
  }
  function previewMaterial(m,target){
    try {ghost=MATERIAL.ghostPlacement(m,target);draw();notify('Hypothetical unscaled overlay. Click Place to record it as a tentative board object.');}
    catch(err){notify(err.message);}
  }
  function placeMaterial(m,target){
    try{
      ghost=MATERIAL.ghostPlacement(m,target);
      const item=MATERIAL.materialToBoardItem(ghost,m,uid('object'));
      stamp({type:'add',item});selected=item.id;ghost=null;render();
    }catch(err){notify('Candidate placement held: '+err.message);}
  }
  function renderMaterials(){
    const host=byId('materials');if(!host)return;host.replaceChildren();
    byId('materialCount').textContent=`${state.materials.length} objects`;
    renderPhotoRegions();
    const routes=state.items.filter(i=>i.kind==='desired'&&i.status!=='user_rejected');
    const interactions=MATERIAL.nextInteractions(state.materials,state);
    if(interactions.length){const node=tile('Next useful photo interaction',interactions[0].title,'Automatic option from uncertainty, not a proven information-gain optimum.');host.append(node);}
    state.materials.forEach(m=>{
      const card=tile(m.label,`${m.role.replaceAll('_',' ')} · ${m.mobility} · ${m.status}`,
        `${m.provenance} / ${m.photo_id} · photo box only (not a yard position)`);
      const s=dom('select',{class:'mini'});
      for(const role of MATERIAL.ROLES){const o=dom('option',{value:role},role.replaceAll('_',' '));s.append(o);}
      s.value=m.role;s.addEventListener('change',()=>stamp({type:'material_set',target:m.id,prop:'role',value:s.value}));card.append(s);
      const actions=dom('div',{class:'row'});
      for(const [name,prop,val] of [
        ['Confirm description','status','user_confirmed'],['Reject','status','user_rejected'],
        ['Movable','mobility','movable'],['Fixed','mobility','fixed']]){
        const b=dom('button',{type:'button',class:'mini'},name);b.addEventListener('click',()=>stamp({type:'material_set',target:m.id,prop,value:val}));actions.append(b);
      }
      card.append(actions);
      const input=dom('input',{type:'number',min:'.01',max:'1000',step:'.25',placeholder:'Width (optional)' });
      input.value=m.width?.value||'';
      const units=dom('select');for(const unit of ['ft','m','cm','in'])units.append(dom('option',{value:unit},unit));units.value=m.width?.unit||'ft';
      const quality=dom('select');quality.append(dom('option',{value:'rough_guess'},'Approximate'),dom('option',{value:'user_measured'},'Measured'));quality.value=m.width?.quality||'rough_guess';
      const b=dom('button',{class:'mini',type:'button'},'Save width');b.addEventListener('click',()=>{
        const n=Number(input.value);if(!Number.isFinite(n)||n<=0||n>1000){notify('Enter a valid positive width.');return;}
        stamp({type:'material_set',target:m.id,prop:'width',value:{value:n,unit:units.value,quality:quality.value}});
      });
      const measureRow=dom('div',{class:'row'});measureRow.append(input,units,quality,b);card.append(measureRow);
      if(routes.length){
        const chooser=dom('select',{class:'mini'});
        routes.forEach(t=>chooser.append(dom('option',{value:t.id},t.label.slice(0,50))));
        const preview=dom('button',{type:'button',class:'mini'},'Preview position');
        const place=dom('button',{type:'button',class:'mini'},'Place tentative copy');
        preview.addEventListener('click',()=>previewMaterial(m,routes.find(x=>x.id===chooser.value)));
        place.addEventListener('click',()=>placeMaterial(m,routes.find(x=>x.id===chooser.value)));
        const row=dom('div',{class:'row'});row.append(chooser,preview,place);card.append(row);
      }else card.append(dom('p',{class:'micro'},'Trace a desired route to explore where a copy might go.'));
      host.append(card);
    });
  }
  function displayPhotos(){const root=byId('photolist');root.replaceChildren();photos.forEach((p,idx)=>{
    const b=dom('button',{type:'button',title:p.name});const im=dom('img',{alt:'Photo '+(idx+1)+' thumbnail',src:p.url});b.append(im,dom('span',{class:'micro'},p.name.slice(0,13)));
    b.addEventListener('click',()=>selectPhoto(p));root.append(b);
  });if(photos.length&&!activePhoto)selectPhoto(photos[0]);}
  byId('photoUpload').addEventListener('change',async e=>{
    const uploads=Array.from(e.target.files||[]).slice(0,20).filter(file=>/^image\/(png|jpeg|webp)$/.test(file.type)&&file.size<=15*1024*1024);
    for(const file of uploads){
      const url=await new Promise((res,rej)=>{const rd=new FileReader();rd.onerror=rej;rd.onload=()=>res(String(rd.result));rd.readAsDataURL(file);});
      photos.push({name:file.name,url});
    }
    displayPhotos();
    if(uploads.length)void scanAllPhotos();
  });

  byId('autoDraftBtn').addEventListener('click',()=>runAutoDraft());
  byId('draftImportBtn').addEventListener('click',()=>byId('draftImportFile').click());
  byId('draftImportFile').addEventListener('change',e=>{
    const file=e.target.files?.[0];if(!file)return;
    if(file.size>1800000){notify('Draft JSON too large.');return;}
    const reader=new FileReader();reader.onload=async()=>{try{
      if(!sketchDigest && sketchSrc)sketchDigest=await shaDataURL(sketchSrc);
      const packet=JSON.parse(String(reader.result));installDraft(packet);
    }catch(ex){notify('Draft import held: '+ex.message);}};reader.readAsText(file);
  });
  byId('importBtn').addEventListener('click',()=>byId('importFile').click());
  byId('importFile').addEventListener('change',e=>{
    const file=e.target.files?.[0];if(!file)return;if(file.size>2e6){notify('Board JSON too large.');return;}
    const reader=new FileReader();reader.onload=()=>{try{const incoming=JSON.parse(reader.result);M.replay(incoming);
      project=incoming;selected=null;seq=project.events.length+1;state=M.replay(project);recompute();render();
      notify('Board loaded. If it used a private sketch, select that sketch again; images are intentionally excluded from JSON exports.');
    }catch(ex){notify('Invalid board JSON: '+ex.message);}};reader.readAsText(file);
  });
  if (sketchSrc){loadSketch(sketchSrc);project.base.source='user_sketch';project.base.items=[];}
  if (Array.isArray(window.MOTIF010_PRIVATE_PHOTOS)) {
    window.MOTIF010_PRIVATE_PHOTOS.forEach(p=>photos.push(p));displayPhotos();
    // Illustrative private demonstration begins scanning its images without asking users to outline objects.
    void scanAllPhotos();
  }
  render();recompute();
  if (sketchSrc){
    (async()=>{try{
      sketchDigest=await shaDataURL(sketchSrc);
      if(window.MOTIF011_PRIVATE_DRAFT){installDraft(window.MOTIF011_PRIVATE_DRAFT);}
      else{await runAutoDraft();}
    }catch(ex){notify('Preloaded draft held: '+ex.message);}})();
  }
  window.MOTIF010_DEBUG = {getProject:()=>D(project),getState:()=>D(state),getBranches:()=>D({solverData,interfaceData}),
    getObjectGhost:()=>D(ghost),apply:stamp, tool:setTool,previewMaterial,placeMaterial,scanMaterialPhoto,scanAllPhotos,visualPossibilities:()=>PROPOSALS.evaluate(state)};
})();
