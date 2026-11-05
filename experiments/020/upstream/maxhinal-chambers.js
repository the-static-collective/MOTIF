(function(root, factory) {
  const base = typeof module === 'object' && module.exports ? require('./maxhinal-modes.js') : root.MaxhinalModes;
  const api = factory(base);
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.MaxhinalChambers = api;
  root.MaxhinalModes = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function(Base) {
  if (!Base) throw new Error('MaxhinalModes is required');
  const STOP = new Set(['the','a','an','and','or','of','to','in','is','it','that','this','what','why','how','with','without','as','for','from','be','been','are','was','were','them','one','two','new']);
  const VERBS = new Set(['predict','compose','construct','create']);
  const CO_PHASES = new Set(['co','not-co','unknown']);
  const normalize = Base.normalize;

  function emptyResult(status, code, message) { return { status, projection:null, residuals:[{code,message}], bad_spins:[] }; }
  function sourceRef(entry) { return entry && entry.provenance && (entry.provenance.slice_id || entry.provenance.output_id) || entry && entry.ref && (entry.ref.slice_id || entry.ref.output_id) || null; }
  function stableText(value) {
    if (Array.isArray(value)) return `[${value.map(stableText).join(',')}]`;
    if (value && typeof value === 'object') return `{${Object.keys(value).sort().map((key)=>`${JSON.stringify(key)}:${stableText(value[key])}`).join(',')}}`;
    return JSON.stringify(value);
  }
  function textForValue(value) {
    if (!value) return '';
    if (typeof value === 'string') return value;
    const textual=[value.title,value.summary,value.carry,value.text].filter(Boolean);
    return textual.length ? textual.join(' ') : stableText(value);
  }
  function inputTokens(entry) { return new Set(normalize(textForValue(entry.value)).split(' ').filter((word)=>word.length>2&&!STOP.has(word))); }

  function runWalkBraid(context) {
    const parameters=context.parameters||{};
    const steps=Array.isArray(parameters.steps)?parameters.steps:[];
    if(!steps.length)return emptyResult('INSUFFICIENT_INPUT','INSUFFICIENT_INPUT','Walk Braid requires at least one step.');
    for(const step of steps)if(!VERBS.has(step.verb)||!CO_PHASES.has(step.co_phase))return emptyResult('INVALID_MODEL','INVALID_WALK_STEP','Walk Braid steps require a declared verb and co phase.');
    const last=steps[steps.length-1];
    return {status:'OK',projection:{endpoint:{verb:last.verb,co_phase:last.co_phase},path_word:steps.map((step)=>`${step.verb}:${step.co_phase}`),steps:steps.map((step,index)=>({...step,index})),commuting_diagnostic:parameters.operator_model==='co-sensitive'?'ORDER_MAY_MATTER_BY_DECLARED_MODEL':'COMMUTES_WHEN_INDEPENDENT'},residuals:[],bad_spins:[]};
  }

  function runFiber(context) {
    const inputs=context.resolvedInputs||[];
    if(!inputs.length)return emptyResult('INSUFFICIENT_INPUT','INSUFFICIENT_INPUT','Fiber requires selected Slice or derived roads.');
    const parameters=context.parameters||{};
    const target=normalize(parameters.target||'');
    const targetTokens=new Set(target.split(' ').filter((word)=>word.length>2&&!STOP.has(word)));
    const compatible=[];const exclusions=[];
    if(!targetTokens.size){for(const entry of inputs)compatible.push(sourceRef(entry));return {status:'UNRESOLVED',projection:{target:parameters.target||'',compatible_refs:compatible,exclusions,representative:parameters.representative_slice_id?{ref:parameters.representative_slice_id,basis:'declared-policy'}:null,posture:'FIBER_NOT_REPRESENTATIVE'},residuals:[{code:'EMPTY_TARGET',message:'No target text was declared; all selected roads remain compatible.'}],bad_spins:[]};}
    for(const entry of inputs){const tokens=inputTokens(entry);let score=0;targetTokens.forEach((token)=>{if(tokens.has(token))score+=1;});const ref=sourceRef(entry);if(score>0)compatible.push(ref);else exclusions.push({ref,reason:'NO_TOKEN_OVERLAP'});}
    return {status:'OK',projection:{target:parameters.target||'',compatible_refs:compatible,exclusions,representative:parameters.representative_slice_id?{ref:parameters.representative_slice_id,basis:'declared-policy'}:null,posture:'FIBER_NOT_REPRESENTATIVE'},residuals:[],bad_spins:[]};
  }

  function runCompose(context) {
    const inputs=context.resolvedInputs||[];
    if(inputs.length<2)return emptyResult('INSUFFICIENT_INPUT','INSUFFICIENT_INPUT','Compose requires at least two inputs.');
    const parameters=context.parameters||{};const byRef=new Map(inputs.map((entry)=>[sourceRef(entry),entry]));const requested=Array.isArray(parameters.order)?parameters.order:[];const order=requested.length?requested.filter((ref)=>byRef.has(ref)):inputs.map(sourceRef);for(const ref of inputs.map(sourceRef))if(!order.includes(ref))order.push(ref);
    return {status:'OK',projection:{kind:'composition/v0',source_order:order,parts:order.map((ref)=>{const entry=byRef.get(ref);return {ref,title:entry.value&&(entry.value.title||entry.value.kind)||'derived',excerpt:entry.value&&(entry.value.summary||entry.value.text)||stableText(entry.value)};}),seams:Array.isArray(parameters.seams)?parameters.seams:[],posture:'COMPOSITION_NOT_EVIDENCE'},residuals:[],bad_spins:[]};
  }

  const PRESSURE_CANDIDATES={lineage:'What attributable road or carrier distinguishes lineage from resemblance?',identity:'What persistent carrier makes this one identity rather than two similar occurrences?',causation:'What observation would distinguish causal influence from temporal or thematic adjacency?',composition:'What disagreement or missing source would most change this composition?',model:'What measurement would discriminate this model from the nearest simpler model?'};
  function runPressure(context){const parameters=context.parameters||{};const question=PRESSURE_CANDIDATES[parameters.candidate_kind];if(!question)return {status:'REFUSED',projection:null,residuals:[{code:'NO_DISCRIMINATOR',message:'No supported candidate kind was declared.'}],bad_spins:[]};return {status:'OK',projection:{question,candidate_probe:question,counterpressure:'PROMOTION_NOT_GRANTED',promotion:'NONE'},residuals:[],bad_spins:[]};}

  function runMovingOrigin(context){const inputs=context.resolvedInputs||[];const parameters=context.parameters||{};const originRef=parameters.origin_slice_id;const origin=inputs.find((entry)=>sourceRef(entry)===originRef);if(!origin)return emptyResult('INSUFFICIENT_INPUT','MISSING_ORIGIN','Moving Origin requires the declared origin among selected inputs.');const originDate=origin.value&&origin.value.date||null;const before=[];const after=[];const unavailable=[];for(const entry of inputs){const ref=sourceRef(entry);if(ref===originRef)continue;const date=entry.value&&entry.value.date||null;const row={ref,date};if(!date||!originDate)unavailable.push(row);else if(date<originDate)before.push(row);else if(date>originDate)after.push(row);else unavailable.push(row);}before.sort((a,b)=>a.date.localeCompare(b.date)||String(a.ref).localeCompare(String(b.ref)));after.sort((a,b)=>a.date.localeCompare(b.date)||String(a.ref).localeCompare(String(b.ref)));return {status:'OK',projection:{origin_ref:originRef,before,now:{ref:originRef,date:originDate},after,unavailable,posture:'NEW_CURRENT_NOT_OLD_CURRENT_REWRITTEN'},residuals:[],bad_spins:[]};}

  function gcd(a,b){let x=Math.abs(a);let y=Math.abs(b);while(y)[x,y]=[y,x%y];return x;}
  function runQuantumSlinky(context){const p=context.parameters||{};const N=p.N;const mDeclared=p.m;if(!Number.isSafeInteger(N)||N<=0||!Number.isSafeInteger(mDeclared))return emptyResult('INVALID_MODEL','INVALID_MODEL','QuantumSlinky requires positive safe-integer N and integer m.');const m=((mDeclared%N)+N)%N;const d=gcd(N,m);let winding=null;if(p.k!=null){if(!Number.isSafeInteger(p.k))return emptyResult('INVALID_MODEL','INVALID_MODEL','Winding k must be a safe integer.');winding={w:Math.floor(p.k/N),r:((p.k%N)+N)%N};}let twisted=null;if(p.model==='twisted-boundary'){if(!Number.isFinite(p.L)||p.L<=0||!Number.isSafeInteger(p.n)||!Number.isSafeInteger(p.mode_k))return emptyResult('INVALID_MODEL','INVALID_MODEL','Twisted-boundary model requires L > 0 and integer n and mode_k.');twisted={model:'twisted-boundary',L:p.L,n:p.n,mode_k:p.mode_k,kappa:(2*Math.PI/p.L)*(p.n+(p.mode_k*m/N))};}return {status:'OK',projection:{N,m_declared:mDeclared,m,gcd:d,components:d,orbit_length:N/d,primitive:d===1,winding,numeric_sources:{...(p.numeric_sources||{})},twisted_resonance:twisted,posture:'MATH_TRANSFORM_NOT_CLAIM_ABOUT_NATURE'},residuals:[],bad_spins:[]};}

  const MADD_PROMPTS=['What resemblance here is pretending to be ancestry?','What would make this relation fail cleanly?','Which source road is doing the most unsupported work?','What survives if the funniest interpretation is wrong?'];
  function overlapTokens(left,right){const a=inputTokens(left);const b=inputTokens(right);return [...a].filter((token)=>b.has(token)).sort();}
  function runMaddclown(context){const inputs=context.resolvedInputs||[];const p=context.parameters||{};if(!inputs.length)return emptyResult('INSUFFICIENT_INPUT','INSUFFICIENT_INPUT','MADDCL0WN requires gas or a derived target.');const random=context.rng||(()=>0);const prompt=()=>MADD_PROMPTS[Math.min(MADD_PROMPTS.length-1,Math.floor(random()*MADD_PROMPTS.length))];if(inputs.length===1)return {status:'UNRESOLVED',projection:{target_ref:sourceRef(inputs[0]),overlap_tokens:[],pressure_question:p.context_text?`${prompt()} Context: ${p.context_text}`:prompt(),promotion:'NONE'},residuals:[{code:'NO_COMPARISON_CONTEXT',message:'Global MADDCL0WN targeted one output without a second comparison road.'}],bad_spins:[]};const overlap=overlapTokens(inputs[0],inputs[1]);if(!overlap.length)return {status:'REFUSED',projection:null,residuals:[{code:'NO_SURVIVING_RELATION',message:'No inspectable token overlap survived the collision.'}],bad_spins:[]};return {status:'OK',projection:{overlap_tokens:overlap,pressure_question:prompt(),promotion:'NONE'},residuals:[],bad_spins:[]};}

  Object.assign(Base.MODES,{'walk-braid':runWalkBraid,fiber:runFiber,compose:runCompose,pressure:runPressure,'moving-origin':runMovingOrigin,quantumslinky:runQuantumSlinky,maddclown:runMaddclown});
  return Object.assign(Base,{runWalkBraid,runFiber,runCompose,runPressure,runMovingOrigin,runQuantumSlinky,runMaddclown});
});
