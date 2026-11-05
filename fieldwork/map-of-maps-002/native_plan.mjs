// Real source-owned planZ finite Dijkstra/STRIPS engine, selected by MOTIF.
// The plan is a hypothetical research procedure, not permission to run it.
// No shell, network, deployment, codegen or account access.
import {readFileSync} from "node:fs";
import {resolve,join} from "node:path";
import {pathToFileURL} from "node:url";
const root=resolve(process.argv[2]||".");
const {solve,replaySteps}=await import(pathToFileURL(join(root,"planz-native/scripts/motif-classical.mjs")).href);
const actions=[
 {name:"PIN_SOURCES",pre:["QUESTION_FROM_MAP"],add:["PINS_CHECKED"],del:[],cost:1},
 {name:"SCOUT_DOCS",pre:["PINS_CHECKED"],add:["SCOUT_INSPECTED"],del:[],cost:2},
 {name:"ALEX_REVIEW",pre:["PINS_CHECKED"],add:["CLAIM_SCREENED"],del:[],cost:2},
 {name:"DOGRAM_PROBE",pre:["PINS_CHECKED"],add:["TOPOLOGY_TESTED"],del:[],cost:2},
 {name:"CHECK_PLAYDECK_TYPES",pre:["PINS_CHECKED"],add:["TYPE_CONTRACT_READ"],del:[],cost:1},
 {name:"HOLD_BAD_CAST",pre:["CLAIM_SCREENED","TYPE_CONTRACT_READ","TOPOLOGY_TESTED","SCOUT_INSPECTED"],
  add:["CANDIDATE_TESTABLE"],del:[],cost:1},
 {name:"RETURN_REVIEW_PACKET",pre:["CANDIDATE_TESTABLE"],add:["RECEIPT_READY"],del:[],cost:1},
 // This deliberately slower path has no actual extra benefits. A declared
 // integer ranking is NOT a physical resource, measured energy or attention.
 {name:"UNNEEDED_NOTE",pre:["PINS_CHECKED"],add:["PINS_CHECKED"],del:[],cost:9}
];
const initial=["QUESTION_FROM_MAP"],goal=["CANDIDATE_TESTABLE","RECEIPT_READY"];
const shortest=solve(actions,initial,goal);
if(shortest.status!=="PLAN_FOUND"||shortest.steps.length!==7)
 throw Error("HOLD_NATIVE_PLANNER_FAILED");
const replay=replaySteps(actions,shortest.steps,initial);
if(!replay.reached_goal||replay.cost!==shortest.cost)
 throw Error("HOLD_NATIVE_PLANNER_REPLAY_DISAGREEMENT");
process.stdout.write(JSON.stringify({
 schema:"motif.map-002-native-planz-plan/v1",
 native_owner:"the-static-collective/planZ",
 source_entrypoint:"scripts/motif-classical.mjs",
 planner:"source-owned uniform-cost search + independent replay",
 mode:"LOCAL_RESEARCH_PROPOSAL",
 actions:shortest.steps,declared_example_cost:shortest.cost,
 costs_are_measured_energy:false,expanded:shortest.expanded,
 simulated_trace:replay.trace,
 plan_executed_by_planz:false,external_actions:0,
 source_owner_approval:false,approval:"HUMAN_REVIEW_REQUIRED"
})+"\n");
