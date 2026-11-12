/* RECIPROCAL-003 — source-scoped inquiry → hypergraph → method candidate.
   This is NOT the LLM-004 Python ReasonHypermap owner oracle, pretrained
   reasoning, an authenticated witness network, nor human-outcome data. */
(function (root) {
  "use strict";
  const M = typeof module === "object" && module.exports
    ? require("../reciprocal-002/two_doors.js") : root.TwoDoors;
  if (!M) throw Error("TWO_DOORS_ENGINE_REQUIRED");
  const SCHEMA="motif.reciprocal003.reason-field/v0";
  const CANDIDATE_SCHEMA="motif.reciprocal003.method-candidate/v0";
  const SOURCE_PIN={name:"MOTIF LLM-004 original Reason Hypermap",
    blob:"33e0ed2521f9d1eb4bdaf9208b68e434ce80eda0",
    status:"inspiration_only_not_imported_owner"};
  const deep=value=>JSON.parse(JSON.stringify(value));
  function check(v,msg){if(!v)throw Error(msg);}
  function qFrom(state,qid){M.validateState(state);const q=state.questions.find(x=>x.id===qid);check(q,"UNKNOWN_QUESTION");return q;}
  function stableSort(values){return [...values].sort((a,b)=>a.at-b.at||a.id.localeCompare(b.id));}
  function plurality(labels,options){
    check(labels.length>0,"NO_TRAINING_DATA");
    const counts=Array(options).fill(0);
    for(const choice of labels)counts[choice]++;
    const max=Math.max(...counts);
    return {choice:counts.indexOf(max),counts,
      tie:counts.filter(x=>x===max).length>1};
  }
  function entropy(counts){
    const n=counts.reduce((a,b)=>a+b,0);
    return !n?0:-counts.reduce((sum,c)=>c ? sum+(c/n)*Math.log2(c/n):sum,0);
  }
  function toGraph(state,qid,at){
    const q=qFrom(state,qid),seen=M.effective(state,qid),assessment=M.inspect(state,qid,at);
    const nodes=[],edges=[];
    const put=(id,kind,label,status,original=null)=>{
      nodes.push({id,kind,label,status,original,authority:"none"});
      return id;
    };
    const link=(id,kind,tails,heads,status,refs,detail="")=>{
      edges.push({id,kind,tails,heads,status,source_event_ids:refs,detail,
        authority:"none",no_fact_promotion:true});
    };
    const question=put("q:"+qid,"question",q.title,"declared");
    const decision=put("decision:"+qid,"decision","Could change: "+q.decision,"declared");
    link("decision-link:"+qid,"might_change_decision",[question],[decision],
      "proposed",[],"Decision effect is only claimed, not measured.");
    for(let i=0;i<q.options.length;i++)
      put("option:"+qid+":"+i,"possible_answer",q.options[i],"proposed");
    const events=stableSort(state.events.filter(e=>e.questionId===qid));
    const roots=new Map();
    for(const e of events){
      const ref="event:"+e.id;
      // Root handles never turn into independent-person authentication.
      if(!roots.has(e.root)){
        const rid="source:"+qid+":"+e.root;
        roots.set(e.root,rid);
        put(rid,"claimed_source","Claimed root "+e.root,"unverified");
      }
      const verifiedCurrent=seen.answers.some(x=>x.id===e.id);
      const contested=seen.contested.some(x=>x.id===e.id);
      put(ref,e.kind==="DECLINE"?"decline":e.kind==="REVISE"?"correction":"report",
        e.kind==="DECLINE"?"A voluntary refusal":
        e.kind+" / "+e.method+" / choice "+(e.choice+1),
        contested?"contested":verifiedCurrent?"reported":"superseded",
        {event_id:e.id,at:e.at,method:e.method,role:e.role,
         choice:e.choice,source_root:e.root,revises:e.revises});
      const tails=[question,roots.get(e.root)];
      const heads=[ref];
      if(e.kind!=="DECLINE") heads.push("option:"+qid+":"+e.choice);
      link("report-link:"+e.id,"source_reports",tails,heads,
        contested?"contested":"reported",[e.id],
        "Reported choice, not actual physical fact or authenticated person.");
      if(e.kind==="REVISE")
        link("revision-link:"+e.id,"revises_record",["event:"+e.revises],[ref],
          "reported",[e.revises,e.id],"Previous statement remains historically visible.");
    }
    const roleMap=new Map();
    for(const e of seen.answers){
      if(!roleMap.has(e.role))roleMap.set(e.role,[]);
      roleMap.get(e.role).push(e);
    }
    if(roleMap.size>1){
      const rid=put("hypothesis:role-context:"+qid,"missing_distinction",
        "PENCIL: answer may depend on volunteered role/context","proposed");
      link("role-context:"+qid,"suggests_test",seen.answers.map(x=>"event:"+x.id),
        [rid,question],"proposed",seen.answers.map(x=>x.id),
        "A role association is not a causal explanation or verified identity.");
    }
    return {schema:SCHEMA,question_id:qid,as_of:at,question_status:assessment.status,
      question_purpose:q.why,decision:q.decision,nodes,hyperedges:edges,
      current_claimed_roots:seen.answers.length,contested_events:seen.contested.length,
      source_provenance:SOURCE_PIN,
      owner_truth:"not_available",model_prediction:"none",
      all_reports_are_claimed_unverified:true,action_authority:"none"};
  }
  function previewOneMore(state,qid,at){
    const q=qFrom(state,qid),before=M.inspect(state,qid,at);
    const allowed=["OPEN","NEED_OTHER_ROLE"].includes(before.status);
    const result={schema:"motif.reciprocal003.counterfactual/v0",question_id:qid,
      before:{status:before.status,counts:before.counts,n:before.n},
      assumption:"One imaginary independent willing person, NOT an actual observation.",
      branches:[],status:allowed?"PENCIL_ONLY":"HOLD_NOT_ASKING"};
    if(!allowed)return result;
    const prev=M.effective(state,qid);
    let role=q.roles[0]||"anyone";
    if(before.status==="NEED_OTHER_ROLE"){
      role=q.roles.find(r=>!prev.answers.some(x=>x.role===r))||role;
    }
    // Unique *fictional* identifiers, no collision and no mutation to observed state.
    let salt=0,source,identity;
    do{salt++;source="hypothetical_person_"+salt;identity="hypothetical_event_"+salt;}
    while(state.events.some(x=>x.root===source||x.id===identity));
    for(let choice=0;choice<q.options.length;choice++){
      const imaginary=M.event(state,{id:identity,questionId:qid,root:source,role,
        at,kind:"ANSWER",choice,method:"reasoning",note:""});
      const after=M.inspect(imaginary,qid,at);
      result.branches.push({choice,answer:q.options[choice],
        status_if_reported:after.status,
        counts_if_reported:after.counts,
        before_entropy:entropy(before.counts),
        after_entropy:entropy(after.counts),
        status:"HYPOTHETICAL_ONLY_NOT_OBSERVED",
        review_would_be_triggered:after.ready});
    }
    return result;
  }
  function methodCandidate(state,qid,at){
    const q=qFrom(state,qid),view=M.inspect(state,qid,at),all=M.effective(state,qid);
    const base={schema:CANDIDATE_SCHEMA,question_id:qid,as_of:at,
      status:"HOLD",reason:"",hypothesis:"PENCIL: volunteered role may distinguish reports",
      compares:"Later reported options, not reality or usefulness",
      role_policy:null,global_policy:null,
      training_event_ids:[],heldout_event_ids:[],
      evidence_truth:"unverified_claimed_reports",human_review_required:true,
      automatic_admission:false,external_actions:false,source_provenance:SOURCE_PIN};
    function hold(reason){return {...base,reason};}
    if(all.contested.length)return hold("Conflicted claimed-source evidence; no method can be promoted.");
    const groups=new Map();
    for(const a of all.answers){
      if(a.role==="anyone")continue;
      if(!groups.has(a.role))groups.set(a.role,[]);
      groups.get(a.role).push(a);
    }
    const roles=[...groups.keys()].filter(r=>groups.get(r).length>=3)
      .sort((a,b)=>groups.get(b).length-groups.get(a).length||a.localeCompare(b)).slice(0,2);
    if(roles.length<2)return hold("Need at least three distinct claimed roots in each of two self-declared role groups.");
    const train=[],holdout=[];
    for(const role of roles){
      const group=stableSort(groups.get(role));
      train.push(...group.slice(0,2));
      holdout.push(...group.slice(2));
    }
    const global=plurality(train.map(x=>x.choice),q.options.length);
    const perRole=Object.fromEntries(roles.map(role=>[role,plurality(
      train.filter(x=>x.role===role).map(x=>x.choice),q.options.length)]));
    const globalCorrect=holdout.filter(e=>e.choice===global.choice).length;
    const conditionedCorrect=holdout.filter(e=>e.choice===perRole[e.role].choice).length;
    const gain=conditionedCorrect-globalCorrect;
    const out={...base,roles,
      training_event_ids:train.map(x=>x.id),heldout_event_ids:holdout.map(x=>x.id),
      evaluations:holdout.map(e=>({source_event_id:e.id,role:e.role,
        reported_choice:e.choice,baseline_prediction:global.choice,
        candidate_prediction:perRole[e.role].choice})),
      global_policy:{type:"classical_global_plurality",option:global.choice,
        correct:globalCorrect,holdout_size:holdout.length},
      role_policy:{type:"classical_role_conditioned_plurality",
        mapping:Object.fromEntries(roles.map(role=>[role,perRole[role].choice])),
        correct:conditionedCorrect,holdout_size:holdout.length},
      gain_over_global_on_later_reports:gain,
      matched_strong_classical_control:"Same role-conditioned plurality method; exact tie by design.",
      test_leakage_prevented_by_event_ids:true,
      sampled_independence_not_authenticated:true};
    if(Object.values(perRole).every(x=>x.choice===global.choice)){
      out.reason="Role condition predicts no different outcome than global baseline.";
      return out;
    }
    if(gain<2){
      out.reason=gain<0?
        "The conditional method regressed on later reports; hold and preserve failure.":
        "No sufficient heldout advantage over a matched global-plurality baseline.";
      return out;
    }
    out.status="PROPOSED_FOR_HUMAN_REVIEW";
    out.reason="Conditional method predicted later volunteered reports better in this tiny sample; not evidence of causal truth or general usefulness.";
    return out;
  }
  function lesson(state,qid,at){
    const f=toGraph(state,qid,at),p=previewOneMore(state,qid,at),m=methodCandidate(state,qid,at);
    const observation=f.current_claimed_roots;
    const consider=m.status==="PROPOSED_FOR_HUMAN_REVIEW"?
      "A method might transfer to future reports; check context change, source independence, and an independently owned decision outcome before relying on it.":
      "No source-tested conditional method is ready. Preserve the unresolved question and inspect what evidence would change a decision.";
    return {schema:"motif.reciprocal003.lesson/v0",question_id:qid,
      problem:"Distinguish reported agreement from established truth, and past reports from imagined futures.",
      guidance:"A good new question rules out more interpretations or changes a specific choice at lower cost. Never confuse a respondent's answer with verification.",
      observed_claimed_sources:observation,
      hypothetical_branches:p.branches.length,
      current_hold_or_review_status:f.question_status,
      lesson_for_human:consider,
      transfer_exercise:"Before reading any future answer, predict which conclusion could change and what would *falsify* your preferred explanation.",
      not_measured_human_learning:true};
  }
  const api={SCHEMA,CANDIDATE_SCHEMA,SOURCE_PIN,entropy,plurality,toGraph,previewOneMore,methodCandidate,lesson};
  if(typeof module==="object"&&module.exports)module.exports=api;
  else root.ReciprocalLoop=api;
})(typeof window==="undefined"?globalThis:window);
