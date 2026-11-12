// RECIPROCAL-004 — public Git horizon. A source address is not code, truth or permission.
import {readFileSync} from "node:fs";
import {resolve,dirname} from "node:path";
import {fileURLToPath} from "node:url";
const HERE=dirname(fileURLToPath(import.meta.url));
export const PATH=resolve(HERE,"public-git-horizon.v1.json");
const EXPECTED="motif.reciprocal-public-repository-horizon/v1";
const OWNER="the-static-collective/";
const PUNCT=/[^a-z0-9]+/g;
const toks=text=>[...new Set((String(text).toLowerCase().match(/[a-z0-9]+/g)||[]).filter(x=>x.length>1))];
export function checkCatalog(cat){
  if(cat?.schema!==EXPECTED||cat.owner!=="the-static-collective"||
    cat.coverage!=="PARTIAL_PUBLIC_ONLY_UNVERIFIED_COMPLETENESS"||
    cat.constraints?.privateRepositoriesExcluded!==true||
    cat.constraints?.metadataIsNotCodeInspection!==true||
    cat.constraints?.issueContentsNotInspected!==true||
    !Array.isArray(cat.records)||!cat.records.length||cat.records.length>150)
    throw Error("BAD_PUBLIC_REPO_CATALOG");
  const ids=new Set();
  for(const r of cat.records){
    if(typeof r.repository!=="string"||!r.repository.startsWith(OWNER)||
       !/^the-static-collective\/[A-Za-z0-9_.-]{1,100}$/.test(r.repository)||
       !["main","master","gh-pages"].includes(r.default_branch)||
       r.observed_from!=="public-repository-metadata"||ids.has(r.repository))
      throw Error("UNSAFE_OR_DUPLICATE_REPOSITORY");
    ids.add(r.repository);
  }
  return true;
}
export function readCatalog(){
  const cat=JSON.parse(readFileSync(PATH,"utf8"));
  checkCatalog(cat);
  return cat;
}
export function researchLeads(query,{limit=8,catalog=readCatalog()}={}){
  checkCatalog(catalog);
  if(typeof query!=="string"||query.length<3||query.length>200||
    /(?:@|https?:\/\/|\+?\d[\d .()-]{8,})/.test(query))
    throw Error("INQUIRY_MUST_BE_NONPERSONAL_TERMS");
  if(!Number.isInteger(limit)||limit<1||limit>20)throw Error("BAD_LIMIT");
  const words=toks(query);
  if(!words.length)return [];
  return catalog.records.map(r=>{
    const name=r.repository.slice(OWNER.length);
    const nameWords=toks(name);
    let score=0;
    for(const q of words){
      if(name.toLowerCase()===q)score+=10;
      else if(nameWords.includes(q))score+=5;
      else if(q.length>=4&&name.toLowerCase().includes(q))score+=2;
    }
    return {repository:r.repository,ref:r.default_branch,score};
  }).filter(x=>x.score>0)
    .sort((a,b)=>b.score-a.score||a.repository.localeCompare(b.repository))
    .slice(0,limit).map(x=>({
       repository:x.repository,
       publicSource:"https://github.com/"+x.repository,
       observedDefaultBranch:x.ref,
       observedMatch:"REPOSITORY_NAME_ONLY",
       proposedNextQuestion:"Does the current public, project-owned source actually address this inquiry?",
       decisionIfReviewed:"Whether a reviewer should inspect exact source bytes before claiming a relevant capability.",
       state:"PENCIL_LEAD_NOT_INSPECTED",
       ownerAdmission:false,
       humanContact:false,
       automaticGitActions:false
    }));
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const args=process.argv.slice(2);
 if(args.length<2||args[0]!=="--query")throw Error("USAGE: node repo-horizon.mjs --query 'nonpersonal topic terms'");
 const results=researchLeads(args.slice(1).join(" "));
 console.log(JSON.stringify({schema:"motif.reciprocal-source-leads/v1",coverage:"partial",results},null,2));
}
