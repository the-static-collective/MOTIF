// PHI SHARK 003 — fixed geometric views over one graph.
function run(){
 const J=JSON.stringify, A=(v,m)=>{if(!v)throw Error(m)}, phi=(1+Math.sqrt(5))/2;
 let seed=26112603;const rand=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n};
 const laws=["uniform","phi","hyperbolic","graph"];
 function build(kind){
  const nodes=[{p:-1,d:0,lo:0,hi:1}], edges=[], extra=[];
  for(let i=0;i<nodes.length;i++){const u=nodes[i];if(u.d>=5)continue;const b=kind==="irregular"?1+rand(3):2;
   for(let j=0;j<b;j++){const id=nodes.length;nodes.push({p:i,d:u.d+1,lo:u.lo+(u.hi-u.lo)*j/b,hi:u.lo+(u.hi-u.lo)*(j+1)/b});edges.push([i,id])}}
  if(kind==="crosslinked"){for(let k=0;k<12;k++){const a=1+rand(nodes.length-1),b=1+rand(nodes.length-1);if(a!==b&&!edges.concat(extra).some(([x,y])=>x===a&&y===b||x===b&&y===a))extra.push([Math.min(a,b),Math.max(a,b)])}}
  return {nodes,edges,extra};
 }
 function distGraph(n,edges){const adj=Array.from({length:n},()=>[]);for(const [a,b] of edges){adj[a].push(b);adj[b].push(a)}return {adj,D:adj.map((_,i)=>{const d=Array(n).fill(Infinity),q=[i];d[i]=0;for(let p=0;p<q.length;p++)for(const v of adj[q[p]])if(!Number.isFinite(d[v])){d[v]=d[q[p]]+1;q.push(v)}return d})}}
 function coords(nodes,law){return nodes.map(u=>{const theta=Math.PI*2*(u.lo+u.hi)/2;const r=law==="uniform"?u.d:law==="phi"?(phi**u.d-1)/(phi-1):Math.tanh(u.d*Math.log(2)/2);return [r*Math.cos(theta),r*Math.sin(theta)]})}
 function distance(a,b,law){const sq=(a[0]-b[0])**2+(a[1]-b[1])**2;if(law!=="hyperbolic")return Math.sqrt(sq);return Math.acosh(1+2*sq/((1-a[0]**2-a[1]**2)*(1-b[0]**2-b[1]**2)))}
 // Same parent/extra event sequence reconstructs topology; geometry is a view, never inferred authority.
 function replay(p,extra){return p.slice(1).map((v,i)=>[v,i+1]).concat(extra)}
 const results=[];let histories=0,queries=0,replays=0,newEdgeEvents=0;
 for(const kind of ["binary","irregular","crosslinked"]){
  const S=Object.fromEntries(laws.map(l=>[l,{recall:0,stretch:0,pairs:0,queries:0,archive:0,layout:0,novelRecall:0,novelN:0,scan:0}]));
  for(let trial=0;trial<16;trial++){
   const {nodes,edges,extra}=build(kind),p=nodes.map(n=>n.p),all=edges.concat(extra),n=nodes.length;
   const {adj,D}=distGraph(n,all);histories++;newEdgeEvents+=extra.length;
   for(const law of laws){
    const archive={parents:p,extra,view:law}, e=replay(archive.parents,archive.extra);A(J(e)===J(all),"history replay");replays++;
    const s=S[law],C=law==="graph"?null:coords(nodes,law);s.archive+=J(archive).length;s.layout+=C?J(C.map(a=>a.map(x=>Number(x.toFixed(6))))).length:0;
    const F=(i,j)=>law==="graph"?D[i][j]:distance(C[i],C[j],law);
    // Fit scale on even-index source pairs only; evaluate on disjoint odd sources.
    let dot=0,norm=0;for(let i=0;i<n;i+=2)for(let j=0;j<n;j++)if(i!==j){const f=F(i,j);dot+=f*D[i][j];norm+=f*f}
    const scale=dot/norm;
    for(let i=1;i<n;i+=2){
     const k=adj[i].length,near=Array.from({length:n},(_,j)=>j).filter(j=>j!==i).sort((a,b)=>F(i,a)-F(i,b)||a-b).slice(0,k);
     s.recall+=near.filter(j=>adj[i].includes(j)).length/k;s.queries++;s.scan+=n-1;
     for(let j=0;j<n;j++)if(j!==i){s.stretch+=Math.abs(scale*F(i,j)-D[i][j])/D[i][j];s.pairs++}
     for(const [a,b] of extra)if(a===i||b===i){s.novelN++;s.novelRecall+=Number(near.includes(a===i?b:a))}
    }
   }
   queries+=Math.floor(n/2);
  }
  results.push({kind,worlds:16,methods:Object.fromEntries(laws.map(l=>{const s=S[l];return [l,{neighborRecall:s.recall/s.queries,relativeDistanceError:s.stretch/s.pairs,meanRecipeBytes:s.archive/16,meanMaterializedCoordinateBytes:s.layout/16,crosslinkRecall:s.novelN?s.novelRecall/s.novelN:null,queries:s.queries,meanCandidateScan:s.scan/s.queries}]}))})
 }
 // The same geometry for the same tree, with or without crosslinks: geometry cannot identify novel semantic edges.
 const w=build("crosslinked");A(w.extra.length>0,"extra");const c=coords(w.nodes,"phi");A(J(c)===J(coords(w.nodes,"phi")),"same coordinates");A(J(w.edges)!==J(w.edges.concat(w.extra)),"different topology");
 return {version:3,seed:26112603,histories,queries,representationReplays:replays,newEdgeEvents,results,collision:{sameCoordinates:true,differentTopology:true},limitations:["Synthetic rooted growth, fixed depth five, fixed angular interval recipe; not optimized embeddings.","Uniform and phi use Euclidean distance; hyperbolic uses Poincare disk distance with fixed log(2) radial scale; no curvature tuning.","Graph uses exact shortest paths on the authoritative edge set and is a reference, not a learned embedding.","Scale fitted on even-source pairs; odd-source evaluation shares the same graphs, not independent heldout worlds. All methods scan every candidate; no latency claims.","Recipe bytes include parent list, extra links and view label; angular intervals and arity reconstructed from ordered parent children in principle, not independently replayed here; only topology replay tested. Coordinate byte counts rounded for illustrative materialization, not included in recipe size.","No historical source commitments, graph deletions, semantic retrieval or novel relationship prediction; crosslinks are supplied events, not discoveries."]};
}
console.log(JSON.stringify(run(),null,2));
