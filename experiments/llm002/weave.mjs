/* LLM-002 crosswire: LLM-001 evidence compiler -> source-scoped numeric
 * causal-attention KV forks -> PENCIL-only scores -> independent policy view.
 * Not a deployed JAR;VIS model, not real learned language intelligence.
 */
import {compile,available,rank,valid} from '../llm001/loom.mjs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const SCRIPT=fileURLToPath(new URL('./bridge_cli.py',import.meta.url));
const sha256=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');

function weave(world,{consent=false,tenant='fixture-tenant',goal=[],budget=8,
                      maxForks=6,runner=spawnSync}={}) {
  valid(world);
  if(!consent)return {status:'HOLD_NO_OFFLINE_MODEL_CONSENT',forks:[]};
  if(world.fixture_only!==true)return {status:'HOLD_NON_FIXTURE_DATA',forks:[]};
  if(typeof tenant!=='string'||!/^fixture-[a-z0-9-]{1,40}$/.test(tenant))
    return {status:'HOLD_SCOPE',forks:[]};
  if(!Number.isInteger(maxForks)||maxForks<1||maxForks>6)throw Error('BAD_FORK_LIMIT');
  const compiled=compile(world,{budget,goal});
  if(compiled.packet.status!=='READY_FOR_PENCIL')
    return {status:'HOLD_INCOMPLETE_EVIDENCE',forks:[],withheld:compiled.omitted};
  const options=available(world).filter(m=>['probe','simulate'].includes(m.kind)).slice(0,maxForks);
  if(options.length===0)return {status:'HOLD_NO_HYPOTHETICAL_ACTIONS',forks:[]};
  const tool=world.facts.includes('tool_selected')?1:0;
  const permission=world.facts.includes('steward_opted_in')?1:0;
  const root=sha256({schema:compiled.packet.schema,packet:compiled.packet,
                     source_evidence:world.evidence,scope:world.id});
  const payload={schema:'motif.llm002.weave.v0',scope:'PUBLIC_SYNTHETIC_FIXTURE',
    tenant,root,world_id:world.id,
    branches:options.map(m=>({id:m.id,kind:m.kind,tool,permission}))};
  const result=runner('python3',[SCRIPT],{
    input:JSON.stringify(payload),encoding:'utf8',timeout:20000,maxBuffer:1_000_000
  });
  if(result?.status!==0)
    return {status:'HOLD_NUMERIC_ENGINE',forks:[],details:'offline subprocess unavailable or failed'};
  let output;
  try {output=JSON.parse(result.stdout);}catch {return {status:'HOLD_MALFORMED_OUTPUT',forks:[]};}
  if(output?.schema!=='motif.llm002.weave-result.v0' ||
     output.world_id!==world.id ||output.source_root!==root ||
     output.external_actions!==false ||output.decision_authority!=='NONE'||
     output.verified_equal!==true ||!Array.isArray(output.forks)||
     output.forks.length!==options.length ||
     output.forks.some((f,i)=>f.id!==options[i].id||f.status!=='PENCIL_SCORE_ONLY'||
       !Number.isFinite(f.latent_logit)||!Number.isFinite(f.cached_vs_full_delta)||
       f.cached_vs_full_delta>1e-11)) {
    return {status:'HOLD_INVALID_ENGINE_RECEIPT',forks:[]};
  }
  const policy=rank(world,'classical',goal);
  const heuristic=rank(world,'affordance',goal);
  return {status:'PENCIL_PARALLEL_FORKS_ONLY',source_root:root,tenant,
    world_id:world.id,forks:output.forks,
    attention_qk_full:output.attention_qk_full,
    attention_qk_shared:output.attention_qk_shared,
    classical_preferred:policy.preferred?.id||null,
    affordance_preferred:heuristic.preferred?.id||null,
    source_witnesses:compiled.packet.witnesses.map(e=>({id:e.id,root:e.root,kind:e.kind})),
    side_effects:0,model_real:false,review_required:true};
}
export {weave};
