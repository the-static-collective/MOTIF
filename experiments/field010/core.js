/* MOTIF FIELD-010 — browser-side deterministic projection.
 * Every edit is a user input to the shared thought surface, not observed physical work.
 * Function bodies intentionally serializable into independent local Web Workers.
 */
(function (root) {
  'use strict';
  function span(item, size) {
    if (!item || !item.points || item.points.length !== 2) return null;
    const a = item.points[0], b = item.points[1];
    return Math.hypot((a[0] - b[0]) * size[0], (a[1] - b[1]) * size[1]);
  }
  function finite(x) { return typeof x === 'number' && Number.isFinite(x); }
  function goodPoint(p) { return Array.isArray(p) && p.length === 2 && p.every(x => finite(x) && x >= 0 && x <= 1); }
  function validItem(i) {
    if (!i || typeof i.id !== 'string' || !i.id || !['current','desired','panel','support','access'].includes(i.kind) ||
        !['tentative','user_confirmed','user_rejected'].includes(i.status) || typeof i.label !== 'string' ||
        i.label.length > 120 || typeof i.movable !== 'boolean' || !Array.isArray(i.points) ||
        i.points.length !== (i.kind === 'support' ? 1 : 2) || !i.points.every(goodPoint)) throw Error('Invalid object or coordinate');
    return i;
  }
  function validMaterial(m){
    if(!m || typeof m.id!=='string' || !/^material-[a-zA-Z0-9_-]{1,80}$/.test(m.id) ||
       typeof m.label!=='string'||!m.label.trim()||m.label.length>120 ||
       !['boundary_module','support_candidate','flexible_barrier','visual_cue','unknown'].includes(m.role) ||
       !['tentative','user_confirmed','user_rejected'].includes(m.status) ||
       !['unknown','movable','fixed'].includes(m.mobility) || m.source_frame!=='photo_normalized' ||
       typeof m.photo_id!=='string'||!m.photo_id||m.photo_id.length>120 ||
       !/^[a-f0-9]{64}$/.test(m.photo_sha256) ||
       !['LOCAL_VLM_TENTATIVE','HUMAN_REGION_TAG'].includes(m.provenance) ||
       !Array.isArray(m.bbox)||m.bbox.length!==4||!m.bbox.every(x=>finite(x)&&x>=0&&x<=1) ||
       m.bbox[2]-m.bbox[0]<=.005 ||m.bbox[3]-m.bbox[1]<=.005 ||
       m.registered_to_sketch!==false||m.certified_safe!==false ||
       m.width!=null && (!finite(m.width.value)||m.width.value<=0||m.width.value>1000 ||
           !['ft','m','cm','in'].includes(m.width.unit)||!['rough_guess','user_measured'].includes(m.width.quality)))
      throw Error('Untrusted photo material or geometry');
    return m;
  }
  function replay(project) {
    if (!project || project.schema !== 'motif.field010.v1' || !project.base ||
        project.base.coordinate_frame !== 'sketch_normalized' ||
        !['synthetic','user_sketch'].includes(project.base.source) ||
        !Array.isArray(project.base.items) || !Array.isArray(project.events) || project.events.length > 5000) throw Error('Invalid project');
    const size = project.base.sketch_size;
    if (!Array.isArray(size) || size.length !== 2 || !size.every(x => finite(x) && x > 0)) throw Error('Invalid sketch dimensions');
    const clone = x => JSON.parse(JSON.stringify(x));
    const items = {};
    project.base.items.forEach(i => { validItem(i); if (items[i.id]) throw Error('Duplicate object'); items[i.id] = clone(i); });
    const measure = {}, relations = [], materials = {};
    let proportional = false, tolerance = null;
    const suppressed = new Set(project.events.filter(e => e.type === 'revert').map(e => e.target_event));
    const seen = new Set();
    project.events.forEach(e => {
      if (!e || typeof e.id !== 'string' || seen.has(e.id)) throw Error('Invalid/duplicate event ID');
      seen.add(e.id);
      if (e.type === 'revert' || suppressed.has(e.id)) return;
      const i = items[e.target];
      switch (e.type) {
        case 'add': validItem(e.item); if (items[e.item.id]) throw Error('Already exists'); items[e.item.id] = clone(e.item); break;
        case 'remove': delete items[e.target]; break;
        case 'move':
          if (!i || !Array.isArray(e.delta) || !e.delta.every(finite)) throw Error('Invalid move');
          i.points = i.points.map(p => p.map((x,idx) => Math.round((x+e.delta[idx])*1e6)/1e6));
          if(!i.points.every(goodPoint))throw Error('Rigid move would leave image bounds');
          break;
        case 'endpoint':
          if (!i || ![0,1].includes(e.index) || !i.points[e.index] || !goodPoint(e.point)) throw Error('Invalid endpoint');
          i.points[e.index] = clone(e.point); break;
        case 'set':
          if (!i || !['label','movable','kind','status'].includes(e.prop)) throw Error('Invalid property');
          i[e.prop] = e.value; validItem(i); break;
        case 'measure':
          if (!i || i.points.length !== 2 || !finite(e.value) || e.value <= 0 || e.value > 1e7 ||
              !['ft','m'].includes(e.unit) || !['user_measured','rough_guess'].includes(e.quality)) throw Error('Invalid measurement');
          measure[e.target] = { value:e.value, unit:e.unit, quality:e.quality, event_id:e.id }; break;
        case 'material_add':
          validMaterial(e.material);
          if(materials[e.material.id])throw Error('Material already recorded');
          materials[e.material.id]=clone(e.material);break;
        case 'material_set':
          if(!materials[e.target] || !['label','role','status','mobility','width'].includes(e.prop))throw Error('Invalid material update');
          materials[e.target][e.prop]=clone(e.value);
          validMaterial(materials[e.target]);break;
        case 'material_remove':
          if(!materials[e.target])throw Error('Material not found');
          delete materials[e.target];break;
        case 'ratio':
          if (!i || !items[e.other] || !finite(e.value) || e.value < .05 || e.value > 20) throw Error('Invalid relative ratio');
          relations.push({ target:e.target, other:e.other, ratio:e.value, event_id:e.id, status:'user_relation_not_measured' }); break;
        case 'proportional':
          if (typeof e.value !== 'boolean' || !finite(e.tolerance) || e.tolerance < 0 || e.tolerance > .85) throw Error('Invalid proportionality assumption');
          proportional = e.value; tolerance = proportional ? e.tolerance : null; break;
        default: throw Error('Unknown event type');
      }
    });
    const alive = new Set(Object.keys(items));
    return {items:Object.values(items), measurements:Object.fromEntries(Object.entries(measure).filter(([k])=>alive.has(k))),
      relations:relations.filter(r=>alive.has(r.target)&&alive.has(r.other)), proportional,tolerance,
      materials:Object.values(materials), source:project.base.source, sketch_size:size, version:project.events.length};
  }
  function computeSolver(state) {
    // Keep no external references except `span`; sent into a dedicated Web Worker.
    const size = state.sketch_size, lines = state.items.filter(i=>i.points.length===2 && i.status!=='user_rejected');
    const desired = lines.filter(i=>i.kind==='desired'), current=lines.filter(i=>i.kind==='current');
    const movable = current.filter(i=>i.movable), panels=lines.filter(i=>i.kind==='panel');
    const supports=state.items.filter(i=>i.kind==='support');
    const hypotheses=[], ratios=[], estimates=[], warnings=[];
    if (desired.length && movable.length) hypotheses.push({id:'reuse',title:'Move existing boundary modules',
      why:'The existing fencing might be reusable inventory.',evidence:movable.slice(0,3).map(i=>i.id),
      hold:'Check actual mobility, access and connections before physical use.'});
    if (desired.length && (panels.length || supports.length)) hypotheses.push({id:'compose',title:'Test connected panels and supports',
      why:'A network of pieces may work differently from isolated pieces.',evidence:panels.concat(supports).slice(0,4).map(i=>i.id),
      hold:'A zip-tie rating does not certify assembled stability or safe animal containment.'});
    if (desired.length) hypotheses.push({id:'reroute',title:'Try a different boundary route',
      why:'Shorter drawn routes or existing obstacles may reduce needed material.',evidence:desired.map(i=>i.id),
      hold:'Paper lengths do not prove yard distances.'});
    else hypotheses.push({id:'trace',title:'First trace the intended boundary',why:'No confirmed target geometry exists.',evidence:[],
      hold:'Do not invent the intended route.'});
    if (desired.length>1) {
      const ref = desired[0], refLen=span(ref,size);
      if(refLen>0) desired.slice(1).forEach(i=>ratios.push({id:i.id,ref:ref.id,value:Math.round(span(i,size)/refLen*100)/100,
        status:state.proportional?'conditional proportionality':'drawn-only'}));
    }
    const refs = lines.filter(i=>state.measurements[i.id] && state.measurements[i.id].quality==='user_measured')
      .map(i=>({i,m:state.measurements[i.id]}));
    if (refs.length && !state.proportional) warnings.push('Known span available, but the sketch has not been declared proportional.');
    if (refs.length && state.proportional) {
      const unit = refs[0].m.unit, scales=refs.filter(r=>r.m.unit===unit).map(r=>r.m.value/span(r.i,size));
      if(refs.some(r=>r.m.unit!==unit)) warnings.push('Mixed measurement units; explicitly convert before scaling.');
      else if(scales.length && Math.max(...scales)/Math.min(...scales)>1.08) warnings.push('Measured anchors conflict; cannot transfer scale.');
      else if(scales.length) {
        const scale=scales.reduce((a,b)=>a+b,0)/scales.length, t=state.tolerance;
        desired.forEach(i=>{ const L=span(i,size)*scale;
          const m=state.measurements[i.id];
          if(m && m.quality==='user_measured' && m.unit===unit) {
            estimates.push({id:i.id,low:m.value,high:m.value,nominal:m.value,unit,status:'human-entered measurement, not independently verified'});
          } else estimates.push({id:i.id,low:Math.round(L*(1-t)*100)/100,high:Math.round(L*(1+t)*100)/100,
            nominal:Math.round(L*100)/100,unit,status:'conditional sketch guess, not surveyed'});
        });
      }
    }
    const ratioCues=state.relations.map(r=>{const m=state.measurements[r.other];const cue={target:r.target,other:r.other,ratio:r.ratio,
      status:'user-asserted approximate relation; not a measurement'};
      if(m && m.quality==='user_measured')Object.assign(cue,{implied_nominal:Math.round(m.value*r.ratio*100)/100,
        unit:m.unit,status:'hypothesis from approximate relation and human-measured reference'});
      return cue;});
    const materialSuggestions=[];
    for(const m of (state.materials||[])){
      if(m.status==='user_rejected')continue;
      if(m.role==='boundary_module' && desired.length) materialSuggestions.push({material:m.id,target:desired[0].id,
        title:'Examine '+m.label+' as a candidate boundary section',
        reason:'A photo-region role could be reassigned as a boundary module; dimensions and physical fitting remain unverified.',
        status:'TENTATIVE_NOT_PHOTO_REGISTERED'});
      if(m.role==='support_candidate' && desired.length) materialSuggestions.push({material:m.id,target:desired[0].id,
        title:'Consider '+m.label+' as a candidate support',
        reason:'Connecting separate modules might change support geometry; actual stability is UNKNOWN.',
        status:'TENTATIVE_NOT_STRUCTURAL_PROOF'});
      if(m.role==='flexible_barrier')warnings.push(m.label+' may present entanglement hazards; do not infer containment from a photo.');
    }
    if(materialSuggestions.length) hypotheses.push({id:'photo-objects',title:'Photo inventory creates new possible arrangements',
      why:'Pictured objects are candidates for alternative roles and connector networks; photo bounding boxes do not provide map positions.',
      evidence:materialSuggestions.slice(0,4).map(x=>x.material),
      hold:'Review physical widths, mobility, sharp edges, anchors and dog safety before any construction.'});
    return {branch:'A',version:state.version,hypotheses,materialSuggestions,ratios,ratioCues,estimates,warnings,
      verified_physical_assembly:false, photo_georegistered:false};
  }
  function computeInterface(state) {
    const lines=state.items.filter(i=>i.points.length===2), desired=lines.filter(i=>i.kind==='desired'),
      current=lines.filter(i=>i.kind==='current'), measurements=Object.values(state.measurements);
    const a=[];
    if(!desired.length) a.push({id:'trace',title:'Trace your intended route',tool:'desired',score:100,
      why:'Mark intent directly on the board instead of describing it twice.'});
    else a.push({id:'review',title:'Check the traced target',tool:'select',score:55,
      why:'Confirm which dashed marks are really the planned fence.'});
    if(desired.length && !state.proportional) a.push({id:'proportions',title:'Is the drawing approximately proportional?',tool:'proportions',score:72,
      why:'Without that assumption, ratios describe the paper only.'});
    if(desired.length && !measurements.some(m=>m.quality==='user_measured'))
      a.push({id:'measure',title:'Enter one measured length',tool:'measure',score:68,
        why:'One reference could calibrate the drawing, conditionally.'});
    if(current.length && desired.length) a.push({id:'mobility',title:'Which existing sections can move?',tool:'select',score:64,
      why:'Reusing material may reduce new construction.'});
    if(state.items.some(i=>i.kind==='support'||i.kind==='panel'))
      a.push({id:'supports',title:'Mark actual connection constraints',tool:'select',score:60,
        why:'Stability, snags and anchor movement remain unverified.'});
    if(!current.length) a.push({id:'current',title:'Trace existing fence segments',tool:'current',score:59,
      why:'Existing boundaries can become movable inventory.'});
    const materials=(state.materials||[]).filter(m=>m.status!=='user_rejected');
    if(!materials.length)a.push({id:'photo-material',title:'Mark useful objects directly on a photo',tool:'photo-region',score:80,
      why:'Photographs may reveal reusable pieces; keep their coordinates separate from the yard sketch.'});
    if(materials.some(m=>m.role==='unknown'))a.push({id:'material-role',title:'Identify a pictured object',tool:'photo-region',score:82,
      why:'A useful role may be present without having to describe it in language.'});
    if(materials.some(m=>m.mobility==='unknown'))a.push({id:'material-mobility',title:'Which pictured materials can move?',tool:'photo-region',score:75,
      why:'Movable materials can support different counterfactual arrangements.'});
    if(materials.length&&desired.length)a.push({id:'material-preview',title:'Try a hypothetical object placement',tool:'material-preview',score:78,
      why:'Preview against a boundary without inventing physical fit or photo-to-map coordinates.'});
    a.sort((x,y)=>y.score-x.score);
    return {branch:'B',version:state.version,actions:a.slice(0,4),compulsory:false};
  }
  const api={span,validItem,validMaterial,replay,computeSolver,computeInterface};
  if (typeof module !== 'undefined' && module.exports) module.exports=api;
  root.MOTIF010=api;
})(typeof window !== 'undefined'?window:globalThis);
