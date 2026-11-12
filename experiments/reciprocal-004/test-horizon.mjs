import test from "node:test";
import assert from "node:assert/strict";
import {readCatalog,checkCatalog,researchLeads} from "./repo-horizon.mjs";
const catalog=readCatalog();
test("the public catalog is verified metadata only and explicitly partial",()=>{
 assert.equal(checkCatalog(catalog),true);
 assert.ok(catalog.records.length>=70);
 assert.ok(catalog.records.length<150);
 assert.equal(catalog.coverage,"PARTIAL_PUBLIC_ONLY_UNVERIFIED_COMPLETENESS");
 assert.equal(catalog.constraints.privateRepositoriesExcluded,true);
 assert.equal(catalog.constraints.issueContentsNotInspected,true);
});
test("MOTIF, GRAFT and source-owner research lead addresses are present without claiming import",()=>{
 const names=new Set(catalog.records.map(x=>x.repository));
 for(const name of ["MOTIF","GRAFT","JAR-VIS","free-graph","planZ"]){
  assert.ok(names.has("the-static-collective/"+name),name);
 }
 const motif=researchLeads("MOTIF",{catalog});
 assert.equal(motif[0].repository,"the-static-collective/MOTIF");
 assert.equal(motif[0].observedMatch,"REPOSITORY_NAME_ONLY");
 assert.equal(motif[0].state,"PENCIL_LEAD_NOT_INSPECTED");
 assert.equal(motif[0].automaticGitActions,false);
 assert.equal(motif[0].ownerAdmission,false);
});
test("unverified source names cannot become inferred capability or real-world permission",()=>{
 const x=researchLeads("free graph",{catalog});
 assert.ok(x.some(r=>r.repository==="the-static-collective/free-graph"));
 assert.ok(x.every(r=>r.observedMatch==="REPOSITORY_NAME_ONLY"
   &&r.ownerAdmission===false &&r.humanContact===false
   &&r.proposedNextQuestion.includes("actually address")));
});
test("invalid, private, duplicate, forged and expanded repository entries are rejected",()=>{
 const make=()=>structuredClone(catalog);
 const bad=[
  x=>{x.constraints.privateRepositoriesExcluded=false;},
  x=>{x.records[0].repository="someone-else/private-data";},
  x=>{x.records[0].observed_from="stolen-personal-note";},
  x=>{x.records.push({...x.records[0]});},
  x=>{x.records[0].default_branch="steal-secret-branch";}
 ];
 for(const fn of bad){
   const x=make();fn(x);assert.throws(()=>checkCatalog(x));
 }
});
test("refuses personal query strings, URLs, contact strings and unbounded enumerations",()=>{
 for(const q of ["","a","foo@example.com","https://evil.example","123456789012","a".repeat(300)]){
   assert.throws(()=>researchLeads(q,{catalog}));
 }
 assert.throws(()=>researchLeads("graph",{catalog,limit:500}));
 assert.deepEqual(researchLeads("there are no repo names like this",{catalog}),[]);
});
test("ranked source leads are deterministic without touching the network",()=>{
 assert.deepEqual(researchLeads("motif",{catalog}),researchLeads("motif",{catalog}));
 assert.ok(researchLeads("MOTIF",{catalog}).length>=1);
});
