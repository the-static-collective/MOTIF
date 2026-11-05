import {readFileSync} from "node:fs";
const path=new URL("../public/attention-v1.json",import.meta.url);
export function validatePublicAttention(feed) {
  if(feed?.schema!=="planz/public-attention-v1"||feed.authority!=="INDEX_ONLY"||!/^ATTENTION-\d{4}-\d{2}-\d{2}-\d{3}$/.test(feed.edition))throw Error("Invalid planZ publication");
  if(!Array.isArray(feed.entries)||feed.entries.length<1||feed.entries.length>40)throw Error("Invalid bounded entry list");
  const ids=new Set(feed.entries.map(e=>e.id));if(ids.size!==feed.entries.length)throw Error("Duplicate plan IDs");
  for(const e of feed.entries){
    if(!/^[A-Z0-9-]{5,44}$/.test(e.id)||typeof e.title!=="string"||e.title.length<10||e.title.length>140)throw Error("Invalid plan identity");
    if(!/^https:\/\/github\.com\/the-static-collective\/[A-Za-z0-9_.-]+\/issues\/[1-9][0-9]*$/.test(e.source))throw Error("Non-attributable source link");
    if(!["AWAITING_LOCAL_STEWARD","OWNER_REVIEW_REQUIRED","PROPOSED"].includes(e.disposition)||e.fieldOutcome!=="NOT_VERIFIED"||e.executionAllowed!==false||e.thirdPartyApproval!=="NOT_ESTABLISHED")throw Error("Plan not on HOLD boundary");
    if(typeof e.region!=="string"||e.region.length>100||typeof e.nextGate!=="string"||e.nextGate.length<25||e.nextGate.length>260)throw Error("Invalid region or next gate");
    if(!Array.isArray(e.tags)||e.tags.length<3||e.tags.length>16||e.tags.some(t=>! /^[a-z0-9-]{2,30}$/.test(t)))throw Error("Invalid tags");
    if(!Array.isArray(e.blockedBy)||e.blockedBy.length<1||e.blockedBy.length>8||e.blockedBy.some(t=>! /^[A-Z_]{4,40}$/.test(t)))throw Error("Missing explicit blockers");
    if(!Array.isArray(e.related)||e.related.some(x=>!ids.has(x)||x===e.id))throw Error("Invalid relation");
    const serialized=JSON.stringify(e);if(/@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|(?:\+?\d[\d ().-]{9,})/.test(serialized))throw Error("Potential contact/private data in public index");
  }
  return feed;
}
if(process.argv[1]&&new URL("file://"+process.argv[1]).href===import.meta.url){
  validatePublicAttention(JSON.parse(readFileSync(path,"utf8")));
  console.log("planZ public attention map: validated, index-only.");
}
