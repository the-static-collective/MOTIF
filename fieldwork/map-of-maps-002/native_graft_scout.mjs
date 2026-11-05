// GRAFT's original public-source scout is actually executed against two
// byte-pinned original Git documents, using a deliberately offline replay
// of the GitHub API. No network is contacted. Search hits are source leads,
// not evidence of compatibility, and replay is not a live current scout.
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {resolve,join} from "node:path";
import {pathToFileURL} from "node:url";

const root=resolve(process.argv[2]||".");
const config=JSON.parse(readFileSync(new URL("./source-pins.json",import.meta.url)));
const {scout}=await import(pathToFileURL(join(root,"graft-native/src/live-scout.mjs")).href);
const pins=config.snapshot_documents;
const docs=new Map();
const sha1=bytes=>createHash("sha1").update(Buffer.from("blob "+bytes.length+"\0")).update(bytes).digest("hex");
for(const p of pins){
 const bytes=readFileSync(join(root,p.checkout,p.path));
 if(sha1(bytes)!==p.blob||bytes.length>20000)throw Error("HOLD_DOC_SOURCE_DRIFT");
 docs.set(p.repo+"#"+p.branch,{...p,content:bytes.toString("base64")});
}
let replayReads=0;
const fetcher=async url=>{
 replayReads++;
 if(replayReads>10)throw Error("HOLD_REPLAY_TOO_MANY_SOURCE_READS");
 const u=new URL(url);
 if(u.hostname!=="api.github.com"||u.protocol!=="https:")
  throw Error("HOLD_UNEXPECTED_SOURCE_HOST");
 const path=decodeURIComponent(u.pathname);
 if(/\/branches$/.test(path)){
  const repo=path.split("/")[3];
  if(!["planZ","CANNON","JAR-VIS","webZ"].includes(repo)||
     u.searchParams.get("per_page")!=="100")throw Error("HOLD_UNEXPECTED_BRANCH_DISCOVERY");
  // Empty branch observations are a *fixture*, never a claim there are
  // actually no branches. Only known documents are replayed in this run.
  return {ok:true,status:200,text:async()=>JSON.stringify([])};
 }
 for(const p of pins){
  const prefix="/repos/"+p.repo+"/";
  if(path===prefix+"git/ref/heads/"+p.branch){
   return {ok:true,status:200,text:async()=>JSON.stringify({
    ref:"refs/heads/"+p.branch,object:{type:"commit",sha:p.commit}})};
  }
  if(path===prefix+"contents/"+p.path && u.searchParams.get("ref")===p.commit){
   return {ok:true,status:200,text:async()=>JSON.stringify({
     type:"file",encoding:"base64",content:docs.get(p.repo+"#"+p.branch).content})};
  }
 }
 throw Error("HOLD_UNALLOWLISTED_REPLAY_URL");
};
const question="Can a proposed planZ plan satisfy a PlayDeck full-performance receipt contract?";
const r=await scout(question,{
 fetcher,token:"",
 clock:()=> "2026-11-05T19:00:00.000Z",
 sources:pins.map(p=>({
  repo:p.repo.split("/")[1],branch:p.branch,path:p.path,
  pin:p.commit,title:p.id+" proposed plan PlayDeck receipt contract"
 }))
});
if(r.schema!=="graft.live-public-scout/v1"||r.coverage.known_documents_read!==2||
  r.coverage.source_errors!==0||r.authority!=="none")
 throw Error("HOLD_GRAFT_SOURCE_SCAN_FAILED");
process.stdout.write(JSON.stringify({
 schema:"motif.map-002-native-graft-scour/v1",
 native_owner:"the-static-collective/GRAFT",
 native_scout_schema:r.schema,
 replay_mode:"OFFLINE_PUBLIC_EXACT_GIT_SNAPSHOTS_NOT_LIVE_NETWORK",
 observed_docs:r.observed_sources.map(s=>({
  source_url:s.source_url,source_sha256:s.source_sha256,
  topic_score:s.topic_score,source_state:s.source_state_at_observation
 })),
 relevant_docs:r.relevant_sources.map(x=>x.source_url),
 original_scout_limitations:r.coverage,
 mock_fetch_invocations:replayReads,actual_network_gets:0,
 source_admitted_as_evidence:false,permission:"NONE"
})+"\n");
