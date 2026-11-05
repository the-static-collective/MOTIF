const MODE="RELIABILITY";
export function execute(packet) {
  if (!packet || packet.schema!=='alex.motif022.question-packet/v0' ||
      packet.status!=='RESEARCH_PACKET_HELD' || packet.authority!=='none' ||
      packet.external_actions!==0 || !Array.isArray(packet.hits) ||
      packet.hits.length>18) throw Error('HOLD_UNSAFE_COMPILED_INPUT');
  const groups=new Map();
  for(const hit of packet.hits) {
    const key=hit.repository+'|'+hit.source_commit+'|'+hit.source_path;
    if(!groups.has(key)) groups.set(key,[]);
    groups.get(key).push(hit.line);
  }
  const questions=MODE==='LINEAGE'?
    ['Which independently recoverable original carrier connects these sources?']:
    MODE==='COMPOSITION'?
    ['Which source owner and tests would permit installing this capability?']:
    ['Could these apparent references share the same upstream failure?'];
  return {
    schema:'graft.motif022.executable-review/v0',mode:MODE,
    query_hash:packet.query_hash,source_location_count:groups.size,
    matched_line_count:packet.hits.length,
    source_locations:[...groups].map(([key,lines])=>({key,lines})),
    questions,
    warnings:['Distinct source paths do not prove independence.',
      'No original witness or source identity was authenticated.'],
    evidence_admission:'NONE',output:'REVIEW_ONLY',
    authority:'none',external_actions:0,
    autonomous_deployment:false,source_custody_verified:false
  };
}
