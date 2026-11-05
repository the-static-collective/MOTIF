// GRAFT-027 live public-API boundary: a separate, explicitly approved pilot.
// Fixed, independently documented Open-Meteo HTTPS endpoint, Berlin example
// coordinates, no auth, no redirect, no arbitrary source-controlled URL.
import {createHash} from 'node:crypto';
const url='https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m';
const hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
export const PILOT={service:'Open-Meteo public non-commercial forecast',
 documentation:'https://open-meteo.com/en/docs',
 example_location:'Berlin fixed published example, not the user location',
 host:'api.open-meteo.com',http_method:'GET',
 no_api_key:true,commercial_rights_not_assumed:true,
 maximum_response_bytes:24000,requests_per_explicit_approval:1};
export async function probePublicExample(input={},options={}){
 if(input.approvedPublicPilot!==true){
  return {schema:'graft027.public-live-read/v0',status:'HOLD_LIVE_CONTACT_NOT_APPROVED',
   requests:0,source:'Open-Meteo',data:null,code_installed:false};
 }
 if(Object.keys(input).some(k=>k!=='approvedPublicPilot')||
  options.token!==undefined||options.url!==undefined)
  throw Error('HOLD_UNSUPPORTED_LIVE_API_ARGUMENTS');
 const transport=options.transport??globalThis.fetch;
 if(typeof transport!=='function')throw Error('HOLD_MISSING_PUBLIC_READ_TRANSPORT');
 // Zero parameters from OpenAPI proposals or user text enter this URL.
 const response=await transport(url,{
  method:'GET',redirect:'error',headers:{Accept:'application/json'},
  signal:AbortSignal.timeout(5500)
 });
 if(!response||response.status!==200||response.redirected)
  throw Error('HOLD_PUBLIC_PILOT_HTTP_RESPONSE');
 const mime=response.headers?.get?.('content-type')??'';
 if(!mime.toLowerCase().startsWith('application/json'))
  throw Error('HOLD_PUBLIC_PILOT_NOT_JSON');
 const contentLength=Number(response.headers?.get?.('content-length')||0);
 if(contentLength>24000)throw Error('HOLD_PUBLIC_PILOT_TOO_LARGE');
 let bytes;
 if(response.body?.getReader){
  const reader=response.body.getReader();let count=0;const chunks=[];
  try{
   while(true){
    const {done,value}=await reader.read();
    if(done)break;
    count+=value.byteLength;
    if(count>24000)throw Error('HOLD_PUBLIC_PILOT_TOO_LARGE');
    chunks.push(Buffer.from(value));
   }
  }finally{reader.releaseLock()}
  bytes=Buffer.concat(chunks);
 }else if(typeof response.text==='function'){
  // This branch is for the transport-controlled test double.
  const value=await response.text();
  bytes=Buffer.from(value);
  if(bytes.length>24000)throw Error('HOLD_PUBLIC_PILOT_TOO_LARGE');
 }else throw Error('HOLD_PUBLIC_PILOT_UNREADABLE');
 let raw;
 try{raw=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes))}
 catch{throw Error('HOLD_PUBLIC_PILOT_NOT_PARSEABLE')}
 const temp=raw?.current?.temperature_2m;
 if(typeof temp!=='number'||!Number.isFinite(temp)||
    temp<-120||temp>75)
  throw Error('HOLD_PUBLIC_PILOT_TEMPERATURE_SHAPE');
 if(!Number.isFinite(raw?.latitude)||!Number.isFinite(raw?.longitude)||
    Math.abs(raw.latitude-52.52)>1||Math.abs(raw.longitude-13.41)>1)
  throw Error('HOLD_PUBLIC_PILOT_LOCATION_MISMATCH');
 const body={schema:'graft027.public-live-read/v0',status:'READ_ONLY_THIRD_PARTY_RESPONSE_OBSERVED',
  source:'Open-Meteo',endpoint_host:'api.open-meteo.com',
  example_location:'Berlin, Germany (fixed example)',
  response_fields:['current.temperature_2m'],
  observation:{temperature_2m:temp,time:String(raw.current?.time||'').slice(0,32),
   unit:String(raw.current_units?.temperature_2m||'').slice(0,10)},
  actual_response_digest_sha256:createHash('sha256').update(bytes).digest('hex'),
  source_claims_not_independently_verified:true,
  API_usage_noncommercial_terms_apply:true,
  actual_live_read:true,requests:1,redirects_followed:0,
  private_identity_used:false,credentials_sent:false,
  source_owner_approval_inherited:false,code_installed:false,
  authority:'PUBLIC_READ_ONLY_PILOT'};
 return {...body,receipt_sha256:hash(body)};
}
