// PHI SHARK 001 — synthetic integer recurrence and negative controls.
// Run: node experiments/phi-shark-001/experiment.js
function experiment() {
  const assert=(x,m)=>{if(!x)throw Error(m)};
  const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
  const add=(a,b)=>a.map((x,i)=>x+b[i]);
  const sub=(a,b)=>a.map((x,i)=>x-b[i]);
  const scale=(a,k)=>a.map(x=>x*k);
  const models={lucas:[1,1],linear:[2,-1],delta:[1,0]};
  const zero=[0,0,0,0], n=16;
  let rng=240611;
  const pick=k=>{rng=(Math.imul(rng,1664525)+1013904223)>>>0;return (rng>>>8)%k};
  const vec=()=>Array.from({length:4},()=>pick(11)-5);
  function predict(a,b,m){return add(scale(a,m[0]),scale(b,m[1]))}
  function encode(s,name) {
    if(name==="snapshot")return {name,states:s};
    const m=models[name],order=name==="delta"?1:2, residuals=[];
    for(let i=order;i<s.length;i++){
      const d=sub(s[i],predict(s[i-1],s[i-2]||zero,m));
      if(d.some(Boolean))residuals.push([i,d]);
    }
    return {name,length:s.length,tail:s.slice(-order),residuals};
  }
  function decode(a) {
    if(a.name==="snapshot")return a.states;
    const m=models[a.name],order=a.name==="delta"?1:2;
    const s=Array(a.length);
    a.tail.forEach((x,j)=>s[a.length-order+j]=x);
    const ds=new Map(a.residuals);
    if(ds.size!==a.residuals.length)throw Error("duplicate residual");
    for(let i=a.length-1;i>=order;i--){
      const d=ds.get(i)||zero;
      if(order===1)s[i-1]=sub(s[i],d);
      else s[i-2]=scale(sub(sub(s[i],scale(s[i-1],m[0])),d),m[1]);
    }
    return s;
  }
  const regimes=["lucas_exact","lucas_innovations","linear_innovations","random_walk","independent"];
  const methods=["lucas","linear","delta","snapshot"],results=[];
  for(const regime of regimes){
    const stats=Object.fromEntries(methods.map(k=>[k,{exact:0,totalBytes:0,nonzeroResiduals:0}]));
    for(let j=0;j<40;j++){
      const s=[vec(),vec()];
      for(let i=2;i<n;i++){
        const d=i%5===0?vec():zero;
        if(regime==="lucas_exact")s.push(predict(s[i-1],s[i-2],models.lucas));
        if(regime==="lucas_innovations")s.push(add(predict(s[i-1],s[i-2],models.lucas),d));
        if(regime==="linear_innovations")s.push(add(predict(s[i-1],s[i-2],models.linear),d));
        if(regime==="random_walk")s.push(add(s[i-1],vec()));
        if(regime==="independent")s.push(vec());
      }
      for(const method of methods){
        const a=encode(s,method);const v=stats[method];
        v.exact+=Number(equal(s,decode(a)));
        v.totalBytes+=JSON.stringify(a).length;
        v.nonzeroResiduals+=a.residuals?.length||0;
      }
    }
    for(const v of Object.values(stats))assert(v.exact===40,"round trip");
    results.push({regime,cases:40,methods:Object.fromEntries(methods.map(k=>[k,{exact:stats[k].exact,meanJSONBytes:stats[k].totalBytes/40,meanResidualEvents:stats[k].nonzeroResiduals/40}]))});
  }
  // Cassini identity and reversible second-order state, separately from archive size.
  let l=[2,1];for(let i=2;i<24;i++)l.push(l[i-1]+l[i-2]);
  for(let i=1;i<23;i++)assert(l[i]**2-l[i-1]*l[i+1]===5*(-1)**i,"Cassini");
  const pure=[2,1];for(let i=2;i<10;i++)pure.push(pure[i-1]+pure[i-2]);
  let a=pure.at(-2),b=pure.at(-1);
  for(let i=8;i>0;i--){[a,b]=[b-a,a]}
  assert(a===2&&b===1,"reverse Lucas");
  // The single-state collision is constructive, not a probabilistic result.
  const collision=[[2,3],[1,4]];
  assert(collision[0].reduce((a,b)=>a+b)===collision[1].reduce((a,b)=>a+b),"collision");
  const history=[[1,0,0,0],[2,0,0,0],[7,0,0,0],[9,0,0,0]];
  const archive=encode(history,"lucas"), damaged={...archive,residuals:[]};
  assert(equal(decode(archive),history),"innovation");
  assert(!equal(decode(damaged),history),"loss");
  // A reversible codec without an independently trusted commitment cannot detect an omitted residual.
  const cassiniPassesWrongSequence=[3,4]; // a phase-shifted Lucas pair can satisfy an invariant with the correct parity.
  return {version:1,seed:240611,dimensions:4,statesPerCase:n,cases:200,roundTrips:800,results,controls:{cassiniChecks:22,singleStateCollision:collision,missingResidual:{original:history,decoded:decode(damaged),detectedByIndependentComparison:true,detectedByDecoderAlone:false},limitations:["Synthetic integer vectors, not semantic memory or model identity","JSON character count (ASCII fixtures) is representation-specific, not entropy or compression optimum","No cryptographic integrity or authenticated provenance; absence of residual is ambiguous without independent evidence","Exact reversibility is also available to other matched codecs; no special phi advantage is presumed"]}};
}
console.log(JSON.stringify(experiment(), null, 2));
