// GRAFT-022: closed-template compiler, not arbitrary source generation.
import {createHash} from 'node:crypto';
const sha=x=>createHash('sha256').update(x).digest('hex');
const MODES=new Set(['LINEAGE','COMPOSITION','RELIABILITY']);
const TEMPLATE="export function execute(packet) {\n  if (!packet || packet.schema!=='alex.motif022.question-packet/v0' ||\n      packet.status!=='RESEARCH_PACKET_HELD' || packet.authority!=='none' ||\n      packet.external_actions!==0 || !Array.isArray(packet.hits) ||\n      packet.hits.length>18) throw Error('HOLD_UNSAFE_COMPILED_INPUT');\n  const groups=new Map();\n  for(const hit of packet.hits) {\n    const key=hit.repository+'|'+hit.source_commit+'|'+hit.source_path;\n    if(!groups.has(key)) groups.set(key,[]);\n    groups.get(key).push(hit.line);\n  }\n  const questions=MODE==='LINEAGE'?\n    ['Which independently recoverable original carrier connects these sources?']:\n    MODE==='COMPOSITION'?\n    ['Which source owner and tests would permit installing this capability?']:\n    ['Could these apparent references share the same upstream failure?'];\n  return {\n    schema:'graft.motif022.executable-review/v0',mode:MODE,\n    query_hash:packet.query_hash,source_location_count:groups.size,\n    matched_line_count:packet.hits.length,\n    source_locations:[...groups].map(([key,lines])=>({key,lines})),\n    questions,\n    warnings:['Distinct source paths do not prove independence.',\n      'No original witness or source identity was authenticated.'],\n    evidence_admission:'NONE',output:'REVIEW_ONLY',\n    authority:'none',external_actions:0,\n    autonomous_deployment:false,source_custody_verified:false\n  };\n}\n";
export function validateHandoff(packet,plan){
 if(!packet||!plan||packet.schema!=='alex.motif022.question-packet/v0'||
  plan.schema!=='planz.motif022.question-plan/v0'||
  packet.status!=='RESEARCH_PACKET_HELD'||plan.status!=='PLAN_HELD_FOR_OWNER'||
  !MODES.has(plan.intent)||plan.alex_checksum!==packet.checksum||
  !Array.isArray(plan.actions)||plan.actions.length>12||
  !plan.actions.includes('EMIT_HELD_CANDIDATE')||
  !Array.isArray(packet.hits)||packet.hits.length>18||
  packet.authority!=='none'||packet.external_actions!==0||
  packet.partial_coverage!==true||packet.real_independence_proved!==false||
  plan.authority!=='none'||plan.external_actions!==0||
  plan.no_owner_approval!==true||plan.no_independence_certification!==true)
  throw Error('HOLD_GRAFT_UNADMITTED_HANDOFF');
 const {checksum:alexSha,...alexBody}=packet;
 const {checksum:planSha,...planBody}=plan;
 if(alexSha!==sha(JSON.stringify(alexBody))||
    planSha!==sha(JSON.stringify(planBody)))
  throw Error('HOLD_GRAFT_CHECKSUM_MISMATCH');
 return true;
}
export function compileTemplate(mode){
 if(!MODES.has(mode))throw Error('HOLD_UNKNOWN_COMPILE_MODE');
 return 'const MODE='+JSON.stringify(mode)+';\n'+TEMPLATE;
}
export function compileCapability(packet,plan){
 validateHandoff(packet,plan);
 const source=compileTemplate(plan.intent);
 return {
  schema:'graft.motif022.compiled-candidate/v0',
  mode:plan.intent,source,sha256:sha(source),
  source_plan_checksum:plan.checksum,
  source_alex_checksum:packet.checksum,
  compilation_kind:'FINITE_ALLOWLIST_TEMPLATE',
  user_text_interpolated_into_code:false,
  executable_candidate:true,production_installed:false,
  authority:'none',external_actions:0
 };
}
