// GRAFT-023: compiler of small new executable review functions from source-verified
// live ALEX packets and ORIGINAL planZ finite classical plan source.
// All generated code comes from fixed source-owned templates, not user text.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {verifyPlan} from '../vendor/planZ/motif023-replan.mjs';
const SHA='5e4073cd245714eaca63036d60190780feb22171';
const SHA_CLASSICAL='22d75c26039e5783b59cf71be02982428603128c';
const MODES=['LINEAGE','COMPOSITION','REFERENCE'];
const hash=x=>createHash('sha256').update(x).digest('hex');
const blob=x=>createHash('sha1').update(Buffer.from('blob '+x.length+'\0')).update(x).digest('hex');
export function verifyNativePlanZ(){
 const o=readFileSync(new URL('../vendor/planZ/motif023-replan.mjs',import.meta.url));
 const c=readFileSync(new URL('../vendor/planZ/motif-classical.mjs',import.meta.url));
 if(blob(o)!==SHA||blob(c)!==SHA_CLASSICAL)
  throw Error('HOLD_ORIGINAL_PLANZ_SOURCE_DRIFT');
 return {source_repo:'the-static-collective/planZ',
  exact_replan_blob:SHA,original_classical_blob:SHA_CLASSICAL,
  inspected_original_source_and_no_grant:true};
}
const BODY="export function execute(packet,plan) {\n if(!packet||!plan||\n  packet.schema!=='alex.motif023.live-public-evidence/v0'||\n  plan.schema!=='planz.motif023.observed-plan/v0'||\n  packet.status!=='HELD_SOURCE_RESEARCH_PACKET'||\n  plan.status!=='HELD_CLASSICAL_PLAN'||\n  plan.mode!==MODE||plan.receipt_sha256!==RECEIPT_SHA||\n  plan.source_receipt_sha256!==packet.receipt_sha256||\n  packet.authority!=='none'||plan.authority!=='none'||\n  packet.private_material_accessed!==false||\n  !Array.isArray(packet.hits)||packet.hits.length>20||\n  !Array.isArray(packet.sources)||packet.sources.length>2||\n  !Array.isArray(plan.steps)||plan.steps.join('|')!==STEPS.join('|'))\n   throw Error('HOLD_COMPILED_CAPABILITY_INVALID_SOURCE');\n const loci=new Map();\n for(const h of packet.hits) {\n  const k=h.repository+'@'+h.source_commit+'#'+h.path;\n  if(!loci.has(k))loci.set(k,[]);\n  loci.get(k).push(h.line);\n }\n const gaps=['UNCERTIFIED_SOURCE_FAMILY','SOURCE_SCOPE_PARTIAL'];\n if(packet.errors.length)gaps.push('SOURCE_FETCH_GAPS');\n if(packet.sources.length===1)gaps.push('SINGLE_REPO_SAMPLE');\n if(loci.size<=1)gaps.push('SOURCE_PATH_CONCENTRATION');\n const question=MODE==='LINEAGE'?\n  'What independently attributable original would distinguish copying from shared environmental difficulty?':\n  MODE==='COMPOSITION'?\n  'Which source-owning human and exact code tests would admit this proposed execution contract?':\n  'What third reference family could detect common-mode reference corruption?';\n return {\n  schema:'graft.motif023.capability-observation/v0',\n  mode:MODE,source_alex_receipt:packet.receipt_sha256,\n  source_plan_receipt:plan.receipt_sha256,\n  reviewed_source_loci:[...loci].map(([location,lines])=>({location,lines})),\n  visible_source_location_count:loci.size,\n  observed_public_repositories:packet.sources.map(s=>s.repository),\n  reviewed_classical_steps:[...STEPS],\n  next_discriminating_question:question,\n  gaps,independent_custody_confirmed:false,\n  source_coverage_complete:false,\n  no_automatic_source_finding_or_contact:true,\n  source_lineage_inferred_as_verified:false,\n  code_install_authorized:false,\n  authority:'none',external_actions:0\n };\n}";

export function compileEvidenceCapability(packet,plan){
 verifyNativePlanZ();
 verifyPlan(plan,packet);
 if(plan.status!=='HELD_CLASSICAL_PLAN'||!MODES.includes(plan.mode)||
  packet.sources.length<1||packet.sources.length>2||
  packet.hits.length<1||packet.hits.length>20||
  plan.steps.length>12)
  throw Error('HOLD_UNSAFE_CANDIDATE_BLUEPRINT');
 const prefix='const MODE='+JSON.stringify(plan.mode)+';\n'+
  'const STEPS='+JSON.stringify(plan.steps)+';\n'+
  'const RECEIPT_SHA='+JSON.stringify(plan.receipt_sha256)+';\n';
 const source=prefix+BODY+'\n';
 if(source.length>15000)throw Error('HOLD_GENERATED_CODE_BUDGET');
 return {
  schema:'graft.motif023.compiled-executable/v0',
  status:'EXECUTABLE_RESEARCH_CANDIDATE_NOT_INSTALLED',
  source,source_sha256:hash(source),mode:plan.mode,
  source_alex_receipt:packet.receipt_sha256,
  source_plan_receipt:plan.receipt_sha256,
  original_planz_verified:true,
  synthesis:'FIXED_AUDITED_OPERATIONS_AND_VALIDATED_CLASSICAL_STEPS',
  unsanitized_user_text_in_generated_code:false,
  executable_in_test_sandbox:true,
  source_owner_approved:false,production_installed:false,
  authority:'none',external_actions:0
 };
}
export async function executeCandidate(candidate,packet,plan){
 if(!candidate||candidate.schema!=='graft.motif023.compiled-executable/v0'||
  candidate.status!=='EXECUTABLE_RESEARCH_CANDIDATE_NOT_INSTALLED'||
  candidate.authority!=='none'||candidate.external_actions!==0||
  candidate.source_owner_approved!==false||candidate.production_installed!==false||
  candidate.source_sha256!==hash(candidate.source))
  throw Error('HOLD_INVALID_EXECUTABLE_CANDIDATE');
 const regenerated=compileEvidenceCapability(packet,plan);
 if(candidate.source!==regenerated.source)
  throw Error('HOLD_GENERATED_CODE_IS_NOT_REPRODUCIBLE');
 // Execute ONLY exact reconstructed closed-template code, never an arbitrary string.
 const module=await import('data:text/javascript;base64,'+
  Buffer.from(regenerated.source).toString('base64'));
 const result=module.execute(packet,plan);
 if(!result||result.schema!=='graft.motif023.capability-observation/v0'||
  result.authority!=='none'||result.external_actions!==0||
  result.independent_custody_confirmed!==false||
  result.code_install_authorized!==false)
   throw Error('HOLD_INVALID_COMPOSED_RESULT');
 return result;
}
