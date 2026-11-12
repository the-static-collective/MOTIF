/* LLM-001 opt-in LOCAL Ollama model aperture, no credentials, no effects.
 * An LLM may supply a PENCIL only; model output never becomes a receipt.
 * No network call without explicit consent and a loopback-only destination.
 */
import {gate} from './loom.mjs';

const SYSTEM = [
  'You are a hypothesis proposer, not an authority or physical actuator.',
  'Read ONLY the source-bound input packet supplied as JSON.',
  'Return exactly one JSON object: {"action_id":"...", "cite":["..."], "hypothesis":"..."}',
  'action_id MUST be among possible_moves; cite MUST contain witness ids.',
  'Never invent a permission, measurement, real event, source or completed action.',
  'Your output remains PENCIL until a separate source-owner TEST.'
].join('\n');

function loopbackURL(url) {
  let u;
  try {u = new URL(url);}catch {throw Error('INVALID_LOCAL_URL');}
  if(u.protocol!=='http:' || !['127.0.0.1','localhost','[::1]'].includes(u.hostname) ||
     u.pathname!=='/api/chat'||u.username||u.password||u.search||u.hash)
    throw Error('NOT_LOOPBACK_OLLAMA');
  return u.href;
}
function parseProposal(raw) {
  if(typeof raw!=='string'||raw.length>10000)throw Error('BAD_MODEL_TEXT');
  let content=raw.trim();
  // Do not accept markdown, leading explanations or implicit JSON repair.
  if(!content.startsWith('{')||!content.endsWith('}'))throw Error('NOT_STRICT_JSON');
  let p;
  try{p=JSON.parse(content);}catch {throw Error('NOT_STRICT_JSON');}
  if(!p||Array.isArray(p)||Object.keys(p).some(k=>!['action_id','cite','hypothesis'].includes(k)))
    throw Error('EXTRA_MODEL_FIELDS');
  return p;
}
async function proposeLocal({world,compiled,consent=false,model,url='http://127.0.0.1:11434/api/chat',fetchImpl=fetch,timeoutMs=30000}={}) {
  if(!consent)return {status:'HOLD_NO_LOCAL_MODEL_CONSENT'};
  const safe=loopbackURL(url);
  if(!model||typeof model!=='string'||model.length>100||!Number.isInteger(timeoutMs)||timeoutMs<100||timeoutMs>120000)
    throw Error('INVALID_LOCAL_MODEL_CONFIG');
  if(compiled?.packet?.status!=='READY_FOR_PENCIL')return {status:'HOLD_CONTEXT_NO_MODEL_CALL'};
  const body={model,stream:false,format:'json',options:{temperature:0,num_predict:160},
    messages:[{role:'system',content:SYSTEM},{role:'user',content:JSON.stringify(compiled.packet)}]};
  const response=await fetchImpl(safe,{method:'POST',headers:{'content-type':'application/json'},
    body:JSON.stringify(body),signal:AbortSignal.timeout(timeoutMs),redirect:'error'});
  if(!response||!response.ok)return {status:'HOLD_MODEL_TRANSPORT'};
  let payload;
  try {payload=await response.json();}catch {return {status:'HOLD_INVALID_MODEL_RESPONSE'};}
  try {
    const proposal=parseProposal(payload?.message?.content);
    return gate(world,compiled,proposal);
  }catch {
    return {status:'HOLD_MODEL_FORMAT_OR_EVIDENCE'};
  }
}
export {SYSTEM,loopbackURL,parseProposal,proposeLocal};
