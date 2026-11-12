/* MOTIF RECIPROCAL-002 — Two Doors. Finite, local-first inquiry controller.
   No network calls, hidden profiles, contact invitations, LLM semantics, or truth adjudication. */
(function(root) {
  "use strict";
  const SCHEMA="motif.reciprocal002/v1";
  const ROLES=Object.freeze(["anyone","newcomer","organizer","maker","researcher","artist","developer"]);
  const METHODS=Object.freeze(["experience","observation","experiment","reasoning"]);
  const MAXQ=100, MAXEVENTS=3000;
  const safeId=s=>typeof s==="string" && /^[a-zA-Z0-9_-]{2,72}$/.test(s);
  const has=(object,key)=>Object.prototype.hasOwnProperty.call(object,key);
  const copy=value=>JSON.parse(JSON.stringify(value));
  function check(ok,code){if(!ok)throw Error(code);}
  function bounded(s,n){return typeof s==="string"&&s.trim().length>0&&s.trim().length<=n;}
  function unique(values){return [...new Set(values)];}
  function makeQuestion(data,now,id){
    check(safeId(id),"INVALID_ID");
    check(Number.isInteger(now)&&now>0,"INVALID_TIME");
    const options=(data.options||[]).map(x=>String(x).trim());
    const roles=unique(data.roles||["anyone"]);
    check(bounded(data.title,170)&&bounded(data.why,320)&&bounded(data.decision,320),"MISSING_PURPOSE");
    check(options.length>=2&&options.length<=5&&options.every(x=>bounded(x,85))&&unique(options).length===options.length,"INVALID_OPTIONS");
    check(roles.length>=1&&roles.every(x=>ROLES.includes(x)),"INVALID_ROLES");
    const priority=Number(data.priority||3);
    const minRoots=Number(data.minRoots||3),maxRoots=Number(data.maxRoots||8);
    const openAt=Number(data.openAt||now),closeAt=Number(data.closeAt||now+7*86400000);
    check(Number.isInteger(priority)&&priority>=1&&priority<=5,"INVALID_PRIORITY");
    check(Number.isInteger(minRoots)&&minRoots>=2&&minRoots<=10&&Number.isInteger(maxRoots)&&maxRoots>=minRoots&&maxRoots<=20,"INVALID_BUDGET");
    check(Number.isInteger(openAt)&&Number.isInteger(closeAt)&&openAt>=now&&closeAt>openAt&&closeAt-openAt<=30*86400000,"INVALID_WINDOW");
    return {id,title:data.title.trim(),why:data.why.trim(),decision:data.decision.trim(),
      options,roles,priority,minRoots,maxRoots,openAt,closeAt,createdAt:now,
      seed:data.seed===true};
  }
  function empty(){return {schema:SCHEMA,questions:[],events:[]};}
  function validateState(state){
    check(state&&state.schema===SCHEMA&&Array.isArray(state.questions)&&Array.isArray(state.events),"INVALID_DOCUMENT");
    check(state.questions.length<=MAXQ&&state.events.length<=MAXEVENTS,"DOCUMENT_TOO_LARGE");
    const ids=new Set();
    for(const q of state.questions) {
      check(q&&safeId(q.id)&&!ids.has(q.id),"QUESTION_ID_COLLISION"); ids.add(q.id);
      const re=makeQuestion(q,q.createdAt,q.id);
      check(JSON.stringify(re)===JSON.stringify(q),"INVALID_QUESTION_SHAPE");
    }
    const eventIds=new Set();
    for(const e of state.events){
      check(e&&safeId(e.id)&&!eventIds.has(e.id)&&ids.has(e.questionId)&&safeId(e.root),"INVALID_EVENT");eventIds.add(e.id);
      check(Number.isInteger(e.at)&&e.at>0&&ROLES.includes(e.role),"INVALID_EVENT_SOURCE");
      check(["ANSWER","REVISE","DECLINE"].includes(e.kind),"INVALID_EVENT_KIND");
      if(e.kind==="ANSWER"||e.kind==="REVISE"){
        const q=state.questions.find(x=>x.id===e.questionId);
        check(Number.isInteger(e.choice)&&e.choice>=0&&e.choice<q.options.length&&METHODS.includes(e.method),"INVALID_ANSWER");
        check(typeof e.note==="string"&&e.note.length<=500,"INVALID_NOTE");
        check(e.kind==="ANSWER" ? e.revises===null : safeId(e.revises),"INVALID_REVISION");
      } else {
        check(e.choice===null&&e.method===null&&e.note===""&&e.revises===null,"INVALID_DECLINE");
      }
    }
    return true;
  }
  function addQuestion(state,raw,now,id){
    validateState(state);check(state.questions.length<MAXQ,"QUESTION_CAP");
    const q=makeQuestion(raw,now,id);
    check(!state.questions.some(x=>x.id===q.id),"QUESTION_EXISTS");
    return {...copy(state),questions:[...copy(state.questions),q]};
  }
  function event(state,raw){
    validateState(state);
    check(state.events.length<MAXEVENTS,"EVENT_CAP");
    check(raw&&safeId(raw.id)&&!state.events.some(e=>e.id===raw.id),"EVENT_EXISTS");
    const q=state.questions.find(x=>x.id===raw.questionId);
    check(q,"UNKNOWN_QUESTION");
    check(safeId(raw.root)&&raw.root.length>=3&&ROLES.includes(raw.role),"BAD_SOURCE");
    check(Number.isInteger(raw.at)&&raw.at>0,"BAD_EVENT_TIME");
    const e={id:raw.id,questionId:q.id,root:raw.root,role:raw.role,at:raw.at,
      kind:raw.kind,choice:null,method:null,note:"",revises:null};
    if(raw.kind==="ANSWER"||raw.kind==="REVISE"){
      check(Number.isInteger(raw.choice)&&raw.choice>=0&&raw.choice<q.options.length,"BAD_CHOICE");
      check(METHODS.includes(raw.method),"BAD_METHOD");
      check(typeof raw.note==="string"&&raw.note.length<=500,"BAD_NOTE");
      e.choice=raw.choice;e.method=raw.method;e.note=raw.note;
      if(raw.kind==="REVISE"){
        check(safeId(raw.revises),"MISSING_REVISION_TARGET");
        const old=state.events.find(x=>x.id===raw.revises);
        check(old&&old.questionId===q.id&&old.root===raw.root&&
              (old.kind==="ANSWER"||old.kind==="REVISE"),"INVALID_REVISION_TARGET");
        e.revises=old.id;
      }
    }else check(raw.kind==="DECLINE","BAD_KIND");
    return {...copy(state),events:[...copy(state.events),e]};
  }
  function effective(state,qid){
    validateState(state);
    const all=state.events.filter(e=>e.questionId===qid).slice().sort((a,b)=>a.at-b.at||a.id.localeCompare(b.id));
    const roots=new Map(), contested=[],declined=new Set();
    for(const e of all){
      if(e.kind==="DECLINE"){declined.add(e.root);continue;}
      const prev=roots.get(e.root);
      if(!prev){
        if(e.kind==="REVISE"){contested.push(e);continue;}
        roots.set(e.root,e);continue;
      }
      if(e.kind==="REVISE"&&e.revises===prev.id){roots.set(e.root,e);continue;}
      // Same claimed source root without a valid causal revision is *not*
      // another independent vote. Preserve it as contested evidence.
      contested.push(e);
    }
    return {answers:[...roots.values()],contested,declined:[...declined]};
  }
  function inspect(state,qid,now){
    validateState(state);
    const q=state.questions.find(x=>x.id===qid);check(q,"UNKNOWN_QUESTION");
    const {answers,contested,declined}=effective(state,qid);
    const counts=q.options.map(()=>0),roleVotes=new Map(),sourceTypes=new Set();
    for(const a of answers) {
      counts[a.choice]++;sourceTypes.add(a.method);
      if(!roleVotes.has(a.role))roleVotes.set(a.role,q.options.map(()=>0));
      roleVotes.get(a.role)[a.choice]++;
    }
    const n=answers.length,max=Math.max(0,...counts),leader=counts.indexOf(max);
    const share=n?max/n:0;
    const requiredRoles=q.roles.length>1&&!q.roles.includes("anyone")?2:1;
    const hasDiversity=roleVotes.size>=requiredRoles;
    const roleLeads=[...roleVotes.values()].filter(v=>v.reduce((s,x)=>s+x,0)>=2)
      .map(v=>v.indexOf(Math.max(...v)));
    const roleSplit=unique(roleLeads).length>1;
    let status="OPEN",reason="Collect source-scoped contributions before a human reviews the evidence.";
    if(contested.length){status="HOLD_CONTEST";reason="Same claimed source has conflicting events; do not count it twice.";}
    else if(now<q.openAt){status="WAIT_WINDOW";reason="The stated asking window has not opened.";}
    else if(now>=q.closeAt){status="HOLD_EXPIRED";reason="The asking window ended; surface the evidence for review.";}
    else if(n>=q.minRoots&&share>=.75&&hasDiversity&&!roleSplit){
      status="READY_FOR_REVIEW";reason="Enough varied claimed sources converge to warrant human review, not automatic truth.";
    }else if(n>=q.maxRoots){status="HOLD_BUDGET";reason="Asking budget exhausted; do not harvest endless responses.";}
    else if(n>=Math.max(q.minRoots,Math.ceil(q.maxRoots*.75))&&share<.65){
      status="NEEDS_REFRAME";reason="Substantial disagreement; ask a better, more discriminating question instead of polling forever.";
    }else if(n>=q.minRoots&&!hasDiversity){
      status="NEED_OTHER_ROLE";reason="Look for a voluntarily participating perspective not yet represented.";
    }
    return {questionId:qid,status,reason,n,counts,lead:leader,leadShare:share,
      diversity:roleVotes.size,requiredRoles,roleSplit,methods:[...sourceTypes],contested:contested.length,
      declines:declined.length,remaining:Math.max(0,q.maxRoots-n),ready:status==="READY_FOR_REVIEW",
      evidenceLabel:"CLAIMED_LOCAL_SOURCES_NOT_VERIFIED_GROUND_TRUTH"};
  }
  function choose(state,person,now){
    validateState(state);
    check(person&&Array.isArray(person.roles)&&person.roles.length&&person.roles.every(x=>ROLES.includes(x))&&
      safeId(person.root)&&person.root.length>=3&&person.willing===true,"NOT_OPTED_IN");
    const viable=[];
    for(const q of state.questions){
      const a=inspect(state,q.id,now);
      if(!["OPEN","NEED_OTHER_ROLE"].includes(a.status))continue;
      const matching=q.roles.includes("anyone")||person.roles.includes("anyone")||
        q.roles.some(role=>person.roles.includes(role));
      if(!matching)continue;
      const e=effective(state,q.id);
      if(e.answers.some(x=>x.root===person.root)||e.declined.includes(person.root))continue;
      if(a.status==="NEED_OTHER_ROLE" && !person.roles.some(role =>
          q.roles.includes(role) && !e.answers.some(x=>x.role===role)))continue;
      // Role variety, urgency and remaining decision impact are deliberate
      // authored heuristics, not a learned optimal policy.
      const gap=Math.max(0,q.minRoots-a.n);
      const roleBonus=a.status==="NEED_OTHER_ROLE" ? 3 : 0;
      const urgency=Math.max(0,3-(q.closeAt-now)/86400000);
      const uncertainty= a.n===0 ? 2 : 2*(1-a.leadShare);
      const score=3*q.priority+gap+roleBonus+uncertainty+urgency;
      viable.push({question:q,analysis:a,score,
        why:["Could change: "+q.decision,
          "Relevant to self-declared role: "+(q.roles.includes("anyone")?"anyone":q.roles.join(", ")),
          "Remaining distinct claimed source slots: "+a.remaining,
          a.reason]});
    }
    viable.sort((a,b)=>b.score-a.score||a.question.closeAt-b.question.closeAt||
      a.question.id.localeCompare(b.question.id));
    return viable[0]||null;
  }
  function merge(a,b){
    validateState(a);validateState(b);
    const result=copy(a),qMap=new Map(result.questions.map(q=>[q.id,q]));
    for(const q of b.questions){
      if(qMap.has(q.id))check(JSON.stringify(qMap.get(q.id))===JSON.stringify(q),"QUESTION_SOURCE_CONFLICT");
      else {result.questions.push(copy(q));qMap.set(q.id,q);}
    }
    const eMap=new Map(result.events.map(e=>[e.id,e]));
    for(const e of b.events){
      if(eMap.has(e.id))check(JSON.stringify(eMap.get(e.id))===JSON.stringify(e),"EVENT_SOURCE_CONFLICT");
      else {result.events.push(copy(e));eMap.set(e.id,e);}
    }
    // No conclusions are imported, only source-scoped events; re-evaluate locally.
    validateState(result);return result;
  }
  function demo(now){
    let s=empty();
    s=addQuestion(s,{
      title:"Where does our two-door introduction confuse a first-time visitor?",
      why:"Improve the first-screen explanation before inviting a real pilot.",
      decision:"Rewrite whichever onboarding step people struggle with.",
      options:["I don't know which door to use","I don't know what happens to my answer",
        "I don't understand how MOTIF uses the answer","The explanation is clear"],
      roles:["newcomer","maker"],priority:5,minRoots:3,maxRoots:8,seed:true
    },now,"demo_first_inch");
    s=addQuestion(s,{
      title:"Which source of uncertainty should an inquiry tool explain first?",
      why:"Determine what uncertainty the user must see before trusting a question.",
      decision:"Prioritize the explanation of evidence gaps, disagreement or time cost.",
      options:["What evidence is missing","Why people disagree",
        "What asking costs","Why the question affects a decision"],
      roles:["anyone"],priority:3,minRoots:3,maxRoots:8,seed:true
    },now,"demo_uncertainty");
    return s;
  }
  const api={SCHEMA,ROLES,METHODS,empty,makeQuestion,addQuestion,event,effective,inspect,choose,merge,validateState,demo};
  if(typeof module==="object"&&module.exports)module.exports=api;
  else root.TwoDoors=api;
})(typeof window==="undefined"?globalThis:window);
