// PHI SHARK 002 — synthetic typed graph recurrence and controlled rule transfer.
function run() {
 const A=(x,m)=>{if(!x)throw Error(m)}, J=JSON.stringify;
 const sort=o=>Object.fromEntries(Object.entries(o).filter(([,v])=>v!==0).sort(([a],[b])=>a<b?-1:a>b?1:0));
 const add=(a,b,k=1)=>{const c={...a};for(const [x,v] of Object.entries(b))c[x]=(c[x]||0)+k*v;return sort(c)};
 const mul=(a,k)=>sort(Object.fromEntries(Object.entries(a).map(([x,v])=>[x,k*v])));
 const modes={lucas:[1,1],linear:[2,-1],delta:[1,0]};
 const key=(...p)=>J(p), empty={};
 function valid(s){const nodes=new Set();for(const [k,v] of Object.entries(s)){const p=JSON.parse(k);if(p[0]==="node"){if(p.length!==3||v!==1||nodes.has(p[1]))return false;nodes.add(p[1])}}
 for(const [k,v] of Object.entries(s)){const p=JSON.parse(k);if(p[0]==="edge"){if(p.length!==5||!nodes.has(p[1])||!nodes.has(p[3])||!["support","oppose"].includes(p[4])||!Number.isSafeInteger(v)||v<=0)return false}else if(p[0]!=="node")return false}return true}
 const predict=(a,b,m)=>add(mul(a,m[0]),b,m[1]);
 function encode(s,name){
  if(name==="snapshot")return {name,states:s};
  const m=modes[name],order=name==="delta"?1:2, scars=[];
  for(let i=order;i<s.length;i++){const d=add(s[i],predict(s[i-1],s[i-2]||empty,m),-1);if(Object.keys(d).length)scars.push([i,d])}
  return {name,n:s.length,tail:s.slice(-order),scars};
 }
 function decode(a){
  if(a.name==="snapshot")return a.states;
  const order=a.name==="delta"?1:2,m=modes[a.name],s=Array(a.n),ds=new Map(a.scars);
  A(ds.size===a.scars.length,"duplicate scar");
  a.tail.forEach((x,i)=>s[a.n-order+i]=x);
  for(let i=a.n-1;i>=order;i--){const v=add(s[i],ds.get(i)||empty,-1);if(order===1)s[i-1]=v;else s[i-2]=mul(add(v,mul(s[i-1],m[0]),-1),m[1])}return s;
 }
 // Independent witness holds exact canonical source strings, NOT counted as archive or claimed compact.
 function verify(a,w){try{const s=decode(a);return s.length===w.length&&s.every((x,i)=>valid(x)&&J(sort(x))===w[i])?"EXACT":"FOG"}catch{return "FOG"}}
 let seed=261126;const rand=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n};
 function make(regime,id){
  const u="u"+id,v="v"+id,z="z"+id;
  const ns={[key("node",u,"agent")]:1,[key("node",v,"artifact")]:1};
  const edge=key("edge",u,"observes",v,"support"), opposite=key("edge",u,"observes",v,"oppose"), extra=key("edge",z,"observes",v,"support");
  let a=1+rand(3),b=1+rand(3);const s=[];
  for(let t=0;t<14;t++){
   let val=t===0?a:t===1?b:regime==="lucas"?a+b:regime==="linear"?b+2:regime==="walk"?Math.max(1,b+rand(5)-2):1+rand(8);
   if(t>=2){a=b;b=val}
   const g={...ns,[edge]:val};
   if(t>=4&&t<10){g[key("node",z,"agent")]=1;g[extra]=1+rand(3)}
   if(t>=6&&t<12)g[opposite]=1;
   if(t===8)delete g[edge]; // disappearance of evidence, not negation
   if(t>=11){delete g[key("node",u,"agent")];delete g[edge];delete g[opposite];g[key("node",u,"device")]=1;g[key("edge",u,"observes",v,"support")]=1;} // type reassignment
   const x=sort(g);A(valid(x),"invalid fixture");s.push(x)
  }
  return s;
 }
 const methods=["lucas","linear","delta","snapshot"],regimes=["lucas","linear","walk","independent"],results=[];
 let tamper=0,miss=0,unwitnessedValid=0,projectionCollisions=0;
 for(const regime of regimes){
  const sums=Object.fromEntries(methods.map(m=>[m,0]));let exact=0;
  for(let i=0;i<32;i++){
   const s=make(regime,i),w=s.map(J);
   for(const m of methods){const a=encode(s,m);A(verify(a,w)==="EXACT","round trip");exact++;sums[m]+=J(a).length}
   const a=encode(s,"lucas");const damaged={...a,scars:a.scars.slice(1)};tamper++;if(verify(damaged,w)==="FOG")miss++;if(decode(damaged).every(valid))unwitnessedValid++;
   const project=g=>sort(Object.fromEntries(Object.entries(g).filter(([k])=>!k.includes('"oppose"'))));
   const g=s[6],h=project(g);A(valid(h)&&J(g)!==J(h)&&J(project(g))===J(project(h)),"projection collision");projectionCollisions++;
  }
  results.push({regime,cases:32,exact,meanArchiveBytes:Object.fromEntries(methods.map(m=>[m,sums[m]/32]))})
 }
 // A finite hypothesis family: learner sees only labeled donor examples.
 const hypotheses={a:(a,b)=>a,b:(a,b)=>b,and:(a,b)=>a&&b,or:(a,b)=>a||b,never:()=>false,always:()=>true};
 function world(prefix,a,b){const x=prefix+"A",y=prefix+"B",z=prefix+"C";return {nodes:[[x,"agent"],[y,"artifact"],[z,"resource"]],edges:[...(a?[[x,"knows",y]]:[]),...(b?[[y,"needs",z]]:[])],expected:a&&b?[x,"can_help",z]:null}}
 function read(w){const [x,y,z]=w.nodes.map(n=>n[0]);return [w.edges.some(e=>J(e)===J([x,"knows",y])),w.edges.some(e=>J(e)===J([y,"needs",z]))]}
 const train=[[false,false],[true,false],[false,true],[true,true]].map(([a,b],i)=>world("donor"+i,a,b));
 const surviving=Object.entries(hypotheses).filter(([,f])=>train.every(w=>f(...read(w))===Boolean(w.expected))).map(([k])=>k);
 A(J(surviving)===J(["and"]),"identification");
 const hold=Array.from({length:64},(_,i)=>world("receiver"+i,Boolean(i&1),Boolean(i&2)));
 const scores=Object.fromEntries(Object.entries(hypotheses).map(([k,f])=>[k,hold.filter(w=>f(...read(w))===Boolean(w.expected)).length]));
 let novel=0;for(const w of hold){if(hypotheses[surviving[0]](...read(w))){const proposed=[w.nodes[0][0],"can_help",w.nodes[2][0]];A(J(proposed)===J(w.expected)&&!w.edges.some(e=>J(e)===J(proposed)),"novel");novel++}}
 return {version:2,seed:261126,histories:128,statesPerHistory:14,roundTrips:512,results,tamper:{removedScar:tamper,independentWitnessRefusals:miss,validButWrongWithoutWitness:unwitnessedValid,projectionCollisions},transfer:{hypotheses:Object.keys(hypotheses),trainingCases:4,selected:surviving,heldOut:64,scores,newProposedEdges:novel,scope:"finite hypothesis family; fresh identities only; no authority, semantic emergence or out-of-family transfer"},limits:["Synthetic graph generator constructed with known regimes; not independently authored heldouts.","Edge weights are synthetic counts, not beliefs; contradictory signed stances coexist.","Canonical graph strings held externally as independent exact witness; witness storage excluded from archive sizes, no cryptographic authentication claimed.","A raw snapshot and delta are strong controls; no universal phi advantage.","A learned two-hop rule proposes edges only; no graph mutation or model continuity claim."]};
}
console.log(JSON.stringify(run(), null, 2));
