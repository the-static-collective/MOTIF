import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  MOTIF_003_SHA,FREE_GRAPH_SHA,validatePassport,readPassport,buildCrosswire,validateCrosswire,
  freeGraphPacket,writeArtifacts
} from "./ecosystem-crosswire.mjs";

test("this donor is an exact-source public research capability offer, not production",()=>{
 const p=readPassport();
 assert.equal(validatePassport(p),true);
 assert.equal(p.source.deployed,false);
 assert.equal(p.source.mergedToMain,false);
 assert.equal(p.exchange.status,"PROPOSAL_ONLY");
 assert.equal(p.gate.disposition,"HOLD_FOR_OWNER_REVIEW");
 assert.equal(p.gate.autoApproval,false);
 assert.equal(p.neighboringDoors.length,12);
 assert.equal(p.neighboringDoors.filter(x=>x.crossed).length,0);
 assert.equal(p.source.inheritedResearchHead,MOTIF_003_SHA);
});
test("crosswire executes original 003 fictional method (not a mock outcome packet)",()=>{
 const x=buildCrosswire();
 assert.equal(validateCrosswire(x),true);
 assert.equal(x.provenance.sourceCommit,MOTIF_003_SHA);
 assert.equal(x.trial.trainingExamples,4);
 assert.equal(x.trial.laterTestExamples,4);
 assert.equal(x.trial.candidateLaterCorrect,4);
 assert.equal(x.trial.globalLaterCorrect,2);
 assert.equal(x.trial.strongMatchedClassical,"exact_tie");
 assert.equal(x.inquiryPreview.assumedAnswerNotInActualLedger,true);
 assert.equal(x.crossing.receiverMayAdmit,false);
 assert.equal(x.crossing.receiverMayAct,false);
});
test("tampering or claiming independent identities or automatic admission fails closed",()=>{
 const x=buildCrosswire();
 for(const fn of [
  q=>{q.crossing.receiverMayAct=true;},
  q=>{q.crossing.receiverMayAdmit=true;},
  q=>{q.trial.realWorldTruth=true;},
  q=>{q.trial.methodInstalled=true;},
  q=>{q.provenance.identityVerified=true;},
  q=>{q.provenance.responseIndependenceVerified=true;},
  q=>{q.trial.candidateLaterCorrect=5;},
 ]){
   const altered=structuredClone(x);fn(altered);
   assert.throws(()=>validateCrosswire(altered));
 }
});
test("export is bounded to fictional aggregate and cannot reveal input pseudonyms",()=>{
 const x=buildCrosswire();
 const text=JSON.stringify(x);
 assert.equal(x.provenance.payloadContainsRawResponses,false);
 assert.equal(x.question.isFictional,true);
 for(const marker of ["newcomer_fictional_","maker_fictional_","fixture_newcomer_",'"events":','"rawNotes"','"email":']){
   assert.equal(text.includes(marker),false,marker);
 }
 assert.deepEqual(Object.keys(x).sort(),[
  "crossing","inquiryPreview","owner","provenance","question","receiptSha256","schema","sourceGraph","trial"
 ].sort());
});
test("Free Graph export is content-addressed, read-only, finite, and never constitutes",()=>{
 const g=freeGraphPacket();
 assert.equal(g.schema,"free-graph.packet/v0");
 assert.equal(g.extensions.free_graph_contract_source_commit,FREE_GRAPH_SHA);
 assert.ok(g.packet_id.startsWith("fgp:sha256:"));
 assert.equal(g.sources.length,2);
 assert.equal(g.nodes.length,5);
 assert.equal(g.links.length,4);
 assert.deepEqual(g.modes,["seed","metabolize"]);
 assert.equal(g.task_world_cut.status,"sufficient");
 assert.ok(g.links.some(l=>l.verb==="bears-on"&&l.bearing==="supports"));
 assert.ok(g.links.every(l=>l.verb!=="constitutes"&&l.authority==="none"));
 assert.ok(g.task_world_cut.selected_ids.every(id=>
   [...g.sources,...g.nodes,...g.links].some(x=>x.id===id)));
 assert.ok(g.non_imports.some(x=>x.includes("private human")));
});
test("determinism with frozen synthetic fixture: both artifacts and IDs replay bit-identically",()=>{
 assert.deepEqual(buildCrosswire(),buildCrosswire());
 assert.deepEqual(freeGraphPacket(),freeGraphPacket());
});
test("generate actual downloaded artifacts with no remote calls or external permissions",async()=>{
 const tmp=await mkdtemp(join(tmpdir(),"motif-crosswire-"));
 try{
   const summary=writeArtifacts(tmp);
   assert.equal(summary.records,5);
   const x=JSON.parse(await readFile(join(tmp,"motif-reciprocal-crosswire.json"),"utf8"));
   const fg=JSON.parse(await readFile(join(tmp,"motif-reciprocal-free-graph.json"),"utf8"));
   const p=JSON.parse(await readFile(join(tmp,"motif-reciprocal-passport.json"),"utf8"));
   assert.equal(validateCrosswire(x),true);
   assert.equal(fg.packet_id,freeGraphPacket().packet_id);
   assert.equal(validatePassport(p),true);
 }finally{await rm(tmp,{recursive:true,force:true})}
});
