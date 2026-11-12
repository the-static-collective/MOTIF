// RECIPROCAL-004 — public-only, deterministic, source-owned Git ecosystem crossing.
// The producer may read ONLY its OWN authored synthetic 003 fixture. It never
// accepts a people's source ledger, performs remote I/O, or issues admissions.
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
const require=createRequire(import.meta.url);
const R=require("../reciprocal-003/reason_loop.js");
const M=require("../reciprocal-002/two_doors.js");
const HERE=dirname(fileURLToPath(import.meta.url));
export const PASSPORT_PATH=resolve(HERE,"capability-passport.v1.json");
export const PROTOCOL="motif.reciprocal-crosswire/v1";
export const FIXTURE_TIME=1800000000000; // invented world clock, not realtime human history
export const FREE_GRAPH_SHA="ec0ad8743c5faac3f3675760bbafcbcb1df846c1";
export const MOTIF_003_SHA="4cd625daea43d48248a062d6c686cc42940f2f01";
const clone=v=>JSON.parse(JSON.stringify(v));
const assert=(yes,m)=>{if(!yes)throw Error(m);};
function canonical(v){
  if(Array.isArray(v))return "["+v.map(canonical).join(",")+"]";
  if(v!==null&&typeof v==="object"){
    return "{"+Object.keys(v).sort().map(k=>JSON.stringify(k)+":"+canonical(v[k])).join(",")+"}";
  }
  return JSON.stringify(v);
}
function sha(text){return createHash("sha256").update(text,"utf8").digest("hex");}
function addressed(prefix,obj){return prefix+":sha256:"+sha(canonical(obj));}
function withId(prefix,record){return {...record,id:addressed(prefix,record)};}

export function validatePassport(passport){
  assert(passport&&passport.schema==="motif.reciprocal-capability-passport/v1","BAD_PASSPORT_SCHEMA");
  assert(passport.owner==="the-static-collective/MOTIF" && passport.source?.mergedToMain===false
    && passport.source.deployed===false && passport.source.realHumanData===false,"BAD_SOURCE_BOUNDARY");
  assert(passport.source.inheritedResearchHead===MOTIF_003_SHA,"WRONG_SOURCE_HEAD");
  assert(Array.isArray(passport.capabilities)&&passport.capabilities.length===3,"BAD_CAPABILITIES");
  assert(passport.exchange?.schema===PROTOCOL&&passport.exchange.status==="PROPOSAL_ONLY"
    && passport.exchange.admissible==="PUBLIC_SYNTHETIC_FIXTURE_SUMMARY_ONLY"
    && passport.exchange.reviewedReceiverRequired===true,"BAD_EXCHANGE_GATE");
  assert(passport.gate?.disposition==="HOLD_FOR_OWNER_REVIEW"
    && passport.gate.autoApproval===false,"UNAUTHORIZED_ADMISSION");
  assert(passport.neighboringDoors?.length>=10
    && passport.neighboringDoors.every(x=>x.crossed===false),"PREMATURE_CROSSING");
  assert(Object.values(passport.claims||{}).every(v=>typeof v==="boolean"||typeof v==="string"),
    "UNTRUSTED_PASSPORT_CLAIM");
  for(const [k,v] of Object.entries(passport.claims||{})){
    if(k.endsWith("Verified"))assert(v===false,"PROMOTED_UNVERIFIED_"+k);
  }
  return true;
}

export function readPassport(){
  const p=JSON.parse(readFileSync(PASSPORT_PATH,"utf8"));
  validatePassport(p);return p;
}
function demoResults(){
  // Code is deliberately hardwired to the source-owner's authored fixture.
  // No --input path and no imported event data.
  const state=R.authoredDemo(FIXTURE_TIME);
  M.validateState(state);
  assert(state.questions.length===1&&state.questions[0].seed===true
    &&state.events.length===8,"UNEXPECTED_OWNER_FIXTURE");
  const q=state.questions[0];
  const method=R.methodCandidate(state,q.id,FIXTURE_TIME);
  const graph=R.toGraph(state,q.id,FIXTURE_TIME);
  const imagined=R.previewOneMore(state,q.id,FIXTURE_TIME);
  assert(method.status==="PROPOSED_FOR_HUMAN_REVIEW"
    &&method.global_policy.correct===2 &&method.role_policy.correct===4,"UNEXPECTED_FIXTURE_SCORES");
  return {q,method,graph,imagined};
}

export function buildCrosswire(){
  const passport=readPassport();
  const {q,method,graph,imagined}=demoResults();
  const payload={
    schema:PROTOCOL,
    owner:passport.owner,
    provenance:{
      sourceRepo:passport.owner,
      sourceCommit:MOTIF_003_SHA,
      sourcePaths:[...passport.source.relativeFiles],
      sourceType:"authored_test_fixture",
      observedTime:"2026-11-12",
      payloadContainsRawResponses:false,
      actualLiveSource:false,
      identityVerified:false,
      responseIndependenceVerified:false
    },
    question:{
      sourceId:q.id,
      title:q.title,why:q.why,decision:q.decision,
      isFictional:true
    },
    trial:{
      status:method.status,
      methodKind:"classical_role_conditioned_plurality",
      trainingExamples:method.training_event_ids.length,
      laterTestExamples:method.heldout_event_ids.length,
      candidateLaterCorrect:method.role_policy.correct,
      globalLaterCorrect:method.global_policy.correct,
      strongMatchedClassical:"exact_tie",
      assessedProperty:"reported_option_prediction_only",
      realWorldTruth:false,
      methodInstalled:false,
      importedHumanData:false
    },
    sourceGraph:{
      schema:graph.schema,
      nodes:graph.nodes.length,
      hyperedges:graph.hyperedges.length,
      currentClaimedRoots:graph.current_claimed_roots,
      contestedEvents:graph.contested_events,
      roleHypothesisStillProposed:true,
      originalLLM004OwnerOracleImported:false
    },
    inquiryPreview:{
      schema:imagined.schema,
      fictionalBranches:imagined.branches.length,
      assumedAnswerNotInActualLedger:true
    },
    crossing:{
      status:"HOLD_FOR_OWNER_REVIEW",
      mode:"LOCAL_RESEARCH_READ_ONLY",
      authority:"none",
      receiverMayRead:true,
      receiverMayReview:true,
      receiverMayAdmit:false,
      receiverMayAct:false,
      automaticPromotion:false,
      requiredFurtherTests:["independent_owner_truth","strong_baselines","human_unaided_transfer"]
    }
  };
  return {...payload,receiptSha256:"sha256:"+sha(canonical(payload))};
}
export function validateCrosswire(packet){
  assert(packet?.schema===PROTOCOL&&packet.owner==="the-static-collective/MOTIF","BAD_CROSSWIRE");
  assert(packet.provenance?.sourceCommit===MOTIF_003_SHA
    &&packet.provenance.sourceType==="authored_test_fixture"
    &&packet.provenance.payloadContainsRawResponses===false
    &&packet.provenance.identityVerified===false
    &&packet.provenance.responseIndependenceVerified===false
    &&packet.provenance.actualLiveSource===false,"UNSAFE_PROVENANCE");
  assert(packet.trial?.status==="PROPOSED_FOR_HUMAN_REVIEW"
    &&packet.trial?.strongMatchedClassical==="exact_tie"
    &&packet.trial.realWorldTruth===false&&packet.trial.methodInstalled===false
    &&packet.trial.importedHumanData===false,"UNSUPPORTED_LEARNING_CLAIM");
  assert(packet.crossing?.status==="HOLD_FOR_OWNER_REVIEW"
    &&packet.crossing.authority==="none"&&packet.crossing.receiverMayAct===false
    &&packet.crossing.receiverMayAdmit===false
    &&packet.crossing.automaticPromotion===false,"UNAUTHORIZED_CROSSING");
  assert(packet.receiptSha256==="sha256:"+sha(canonical(Object.fromEntries(
    Object.entries(packet).filter(([k])=>k!=="receiptSha256")))),"TAMPERED_RECEIPT");
  const forbidden=["events","pseudonyms","sourceRoots","rawNotes","secret","email","phone"];
  assert(!forbidden.some(k=>Object.hasOwn(packet,k)),"PRIVATE_DATA_NOT_ALLOWED");
  return true;
}

export function freeGraphPacket(){
  const research=buildCrosswire();
  validateCrosswire(research);
  const summary="A public synthetic MOTIF fixture proposes a conditional method after "+
    "four later reported choices, without evidence of real participant identities or objective truth.";
  const sources=[];
  const source=(kind,coordinate,excerpt)=>{
    const s=withId("fgs",{
      source_class:kind,
      locator:{
        system:"the-static-collective/MOTIF GitHub experiment",
        coordinate,
        revision:MOTIF_003_SHA,
        resolution:"authored synthetic public fixture, not human participant"
      },
      observed_at:"2026-11-12",
      acquisition:"Source-checked public committed synthetic code; evaluated locally",
      digest:"sha256:"+sha(excerpt),access:"public",export:"portable",
      authority:"source-local",excerpt,
      extensions:{synthetic:true,no_real_identity:true,not_owner_admission:true}
    });
    sources.push(s);return s.id;
  };
  const sourceCode=source("project-source",
    "experiments/reciprocal-003/reason_loop.js@"+MOTIF_003_SHA,
    "Synthetic Reason Loop source implements role-labeled trial and explicit HUMAN_REVIEW proposal.");
  const testReport=source("specimen-receipt",
    "RECIPROCAL-003 authored role-dependent eight-report fixture@"+MOTIF_003_SHA,
    summary);
  const nodes=[],links=[];
  const node=(kind,label,status,ids,extras={})=>{
    const n=withId("fgn",{kind,label,status,source_ids:ids,
      extensions:{synthetic:true,automatically_admitted:false,...extras}});
    nodes.push(n);return n.id;
  };
  const link=(from,to,verb,qualifier,status,ids,other={})=>{
    const l=withId("fgl",{from,to,verb,qualifier,status,
      source_ids:ids,authority:"none",...other});
    links.push(l);return l.id;
  };
  const q=node("question","Could a context-sensitive explanation improve the synthetic first entrance?","proposed",[sourceCode]);
  const choice=node("claim","PENCIL: role-conditioned predictions may fit distinct reported experiences","proposed",[sourceCode],{not_an_observed_fact:true,question_owned:true});
  const test=node("test","Compare 2 initial reports per role to 2 later ones, against global majority","tested",[sourceCode,testReport]);
  const receipt=node("receipt","Synthetic later-reply scores: conditional 4/4, global 2/4; no real user outcome","tested",[testReport]);
  const method=node("artifact","Held classical conditional method candidate; no executable graft/admission","proposed",[sourceCode,testReport]);
  link(q,choice,"connects","hypothesis-created-to-investigate-the-question","proposed",[sourceCode]);
  link(test,choice,"tests","authored-heldout-choice-predictions","tested",[sourceCode,testReport]);
  link(receipt,choice,"bears-on","synthetic-source-bearing-not-causal-truth","tested",[testReport],{bearing:"supports"});
  link(method,test,"descends-from","candidate-comes-from-a-synthetic-evaluation","proposed",[sourceCode,testReport]);
  const ids=[...sources,...nodes,...links].map(x=>x.id);
  const packet={
    schema:"free-graph.packet/v0",
    purpose:"Read-only fixture-only historical path: useful question → source-scoped report → counterexample-worthy proposed method.",
    modes:["seed","metabolize"],
    scope:{
      task:"Inspect the synthetic reciprocal question and held method without importing actual people or authority.",
      worlds:["MOTIF synthetic research","Free Graph portable review"],
      as_of:"2026-11-12",
      resolution:"one authored-eight-report finite research fixture"
    },
    task_world_cut:{
      status:"sufficient",selected_ids:ids,owner_head_source_ids:[],
      omitted:[
        {door:"MEMENTO private Understory",reason:"Source-scoped fictional reports only; private personal memory not imported."},
        {door:"JAR;VIS live intake",reason:"No production integration or permission to ask real people."},
        {door:"GRAFT donor admission",reason:"Review only; no code import or runtime execution."}
      ],
      rationale:"This complete public toy example requires no real-world owner state, credentials or person-level source data."
    },
    sources,nodes,links,
    residual_fog:[
      "Synthetic reported answers are not ground truth; the strong classical role-conditioned comparator ties.",
      "Pseudonymous roots are not verified independent persons and this specimen contains no real reports.",
      "No independent human improvement, novel general reasoning, or deployed service has been demonstrated."
    ],
    non_imports:[
      "No private human source records or contact details.",
      "No original LLM-004 Python owner instance or direct Free Graph mutation.",
      "No model weights, permission, action or cross-repository automatic admission."
    ],
    extensions:{producer:"MOTIF RECIPROCAL-004",source_commit:MOTIF_003_SHA,
      free_graph_contract_source_commit:FREE_GRAPH_SHA,projection_only:true,
      reviewedReceiverRequired:true}
  };
  return {...packet,packet_id:addressed("fgp",packet)};
}
export function writeArtifacts(dir){
  const output=resolve(dir);
  mkdirSync(output,{recursive:true});
  const cw=buildCrosswire();validateCrosswire(cw);
  const graph=freeGraphPacket();
  writeFileSync(resolve(output,"motif-reciprocal-crosswire.json"),JSON.stringify(cw,null,2)+"\n");
  writeFileSync(resolve(output,"motif-reciprocal-free-graph.json"),JSON.stringify(graph,null,2)+"\n");
  writeFileSync(resolve(output,"motif-reciprocal-passport.json"),JSON.stringify(readPassport(),null,2)+"\n");
  return {dir:output,records:graph.nodes.length,links:graph.links.length,sources:graph.sources.length};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const args=process.argv.slice(2);
  if(args.length!==2||args[0]!=="--out")throw Error("USAGE: node ecosystem-crosswire.mjs --out OUTPUT_DIRECTORY");
  console.log(JSON.stringify(writeArtifacts(args[1])));
}
