"""LEGIT-029: observe shift in *inputs*, test empirical worst-world regret.

This is an engineer-authored, finite method-selection policy, inspired
by group-DRO and selective prediction. It is NOT a conformal method,
does NOT furnish a distribution-free risk bound or calibrated OOD
probability, and is not a newly invented general reasoning algorithm.

Question values from future problems are NEVER supplied to the router.
Inputs are explicitly available; metadata measurement is counted as
free here, a benchmark-specific choice reported honestly.
"""
from __future__ import annotations
from hashlib import sha256
from math import sqrt
from pathlib import Path
from time import process_time_ns
import json
import sys

HERE=Path(__file__).resolve().parent
for sibling in ("legit021","legit022","legit023","legit025",
                "legit026","legit027","legit028"):
    sys.path.insert(0,str(HERE.parent/sibling))
import information_engine as engine
import information_worlds as legacy
import shift_worlds as worlds

STATUS="RESEARCH_HOLD_NO_STATISTICALLY_VALID_SHIFT_GUARANTEE"
COST_PENALTY=0.025
ROBUST_MEAN_MARGIN=0.1
ROBUST_WORST_WORLD_MARGIN=0.0
OOD_QUANTILE=0.9
OOD_BUFFER=0.05
META_ARMS=("LEGIT028_SIMPLE_CV","WORST_WORLD_REGRET_GUARD",
           "METADATA_SHIFT_GUARD","SHIFT_GATED_SIMPLE_CV",
           "STRONG_CLASSICAL_ONLY")


def training_cv(domain,world_rows):
    """Train on all but one training world; evaluate only the omitted TRAIN world.

    Per-world regret is relative to a fit-on-identical-worlds conventional
    residual greedy, not an oracle with future answers.
    """
    labels=tuple(sorted(world_rows))
    if len(labels)<3:
        raise worlds.HOLD("at least 3 training research worlds required")
    results={m:[] for m in engine.ALL_METHODS}
    for excluded in labels:
        fitted=tuple(r for label,rows in sorted(world_rows.items())
                     if label!=excluded for r in rows)
        held=world_rows[excluded]
        for name in engine.ALL_METHODS:
            model=engine.compile_policy(domain,fitted,name)
            counts=[]
            for row in held:
                trial=engine.simulate(model,row["id"],
                    lambda q,row=row:row["answers"][q])
                if not trial["solved"]:
                    raise worlds.HOLD("a training candidate ran out of witnesses")
                counts.append(trial["question_count"])
            results[name].append({
                "excluded_training_world":excluded,
                "cases":len(counts),
                "questions":sum(counts),
                "mean_questions":sum(counts)/len(counts),
                "per_case_question_costs":counts,
            })
    conventional=engine.CONVENTIONAL
    macro_baseline=sum(x["mean_questions"] for x in results[conventional])/len(labels)
    summary={}
    for name, folds in results.items():
        regrets=[f["mean_questions"]-g["mean_questions"]
                 for f,g in zip(folds,results[conventional])]
        summary[name]={
            "mean_questions":sum(f["mean_questions"] for f in folds)/len(folds),
            "macro_regret_vs_classical":sum(regrets)/len(regrets),
            "worst_world_regret_vs_classical":max(regrets),
            "world_regrets":regrets,
            "folds":folds,
        }
    by_mean=min(engine.METHODS,
                key=lambda m:(summary[m]["mean_questions"],m))
    if summary[by_mean]["mean_questions"]+COST_PENALTY<macro_baseline:
        selected_mean=by_mean
    else:
        selected_mean=conventional

    # This check is deliberately conservative and *empirical*, not a
    # Hoeffding/CRC/conformal risk guarantee. Rare shifts can still
    # dominate performance after any finite set of training worlds.
    eligible=[m for m in engine.METHODS
              if summary[m]["macro_regret_vs_classical"]<=-ROBUST_MEAN_MARGIN
              and summary[m]["worst_world_regret_vs_classical"]<=-
                  ROBUST_WORST_WORLD_MARGIN]
    selected_robust=min(eligible,key=lambda m:(
        summary[m]["worst_world_regret_vs_classical"],
        summary[m]["macro_regret_vs_classical"],m)) if eligible else conventional
    return {
        "domain":domain, "train_world_count":len(labels),
        "strong_conventional":conventional,
        "every_candidate_crossworld_performance":summary,
        "mean_cv_candidate":by_mean,
        "mean_cv_candidate_selected":selected_mean,
        "robust_empirical_candidate_selected":selected_robust,
        "robust_reason":("All training-world checks passed" if eligible
                         else "No candidate met mean AND worst-world regret margins"),
        "eligible_empirical_robust_candidates":eligible,
        "assumes_no_exchangeability_or_iid_guarantee":True,
        "future_seed_graph_or_math_not_consulted":True,
    }


def _normalized_vector(raw,low,high):
    return tuple((float(value)-low[i])/max(1.0,high[i]-low[i])
                 for i,value in enumerate(raw))


def _nearest(value,others,low,high):
    first=_normalized_vector(value,low,high)
    return min(sum(abs(a-b) for a,b in zip(first,
               _normalized_vector(point,low,high)))/len(first)
               for point in others)


def fit_shift_detector(domain,training_cases):
    """Calibration uses only TRAIN cases and their labels-free input shapes.

    Leave-one-training-WORLD-out nearest-neighbor score quantile:
    potential shift in observable input geometry, NOT a label-risk
    guarantee and NOT a statistically valid p-value.
    """
    groups={name:tuple(worlds.metadata(domain,x) for x in cases)
            for name,cases in training_cases.items()}
    all_vectors=[v for items in groups.values() for v in items]
    if not all_vectors:raise worlds.HOLD("no shift calibration inputs")
    dims=len(all_vectors[0])
    if any(len(v)!=dims for v in all_vectors):
        raise worlds.HOLD("inconsistent input shape descriptors")
    low=tuple(min(row[i] for row in all_vectors) for i in range(dims))
    high=tuple(max(row[i] for row in all_vectors) for i in range(dims))
    distances=[]
    for name,points in sorted(groups.items()):
        others=[v for group,items in groups.items() if group!=name
                for v in items]
        if not others:raise worlds.HOLD("cannot calibrate without other worlds")
        distances.extend(_nearest(v,others,low,high) for v in points)
    sorted_d=sorted(distances)
    idx=max(0,min(len(sorted_d)-1,int(OOD_QUANTILE*len(sorted_d))-1))
    threshold=sorted_d[idx]+OOD_BUFFER
    return {
        "dimension":dims, "min_by_feature":low,
        "max_by_feature":high,
        "training_input_vectors":tuple(all_vectors),
        "world_out_training_nearest_distances":tuple(distances),
        "threshold":threshold,
        "quantile":OOD_QUANTILE,
        "absolute_buffer":OOD_BUFFER,
        "input_metadata_only_no_question_answers":True,
        "threshold_empirical_not_conformal_risk_bound":True,
    }


def input_shift_score(detector,domain,case):
    raw=worlds.metadata(domain,case)
    if len(raw)!=detector["dimension"]:
        raise worlds.HOLD("unexpected future metadata dimension")
    return _nearest(raw,detector["training_input_vectors"],
                    detector["min_by_feature"],detector["max_by_feature"])


def select_method(report,detector,domain,case,arm):
    plain=report["mean_cv_candidate_selected"]
    robust=report["robust_empirical_candidate_selected"]
    if arm=="STRONG_CLASSICAL_ONLY":
        return engine.CONVENTIONAL,None,"BASELINE"
    if arm=="LEGIT028_SIMPLE_CV":
        return plain,None,"TRAINING_MEAN"
    if arm=="WORST_WORLD_REGRET_GUARD":
        return robust,None,"TRAINING_WORST_WORLD"
    if arm in ("METADATA_SHIFT_GUARD","SHIFT_GATED_SIMPLE_CV"):
        score=input_shift_score(detector,domain,case)
        novel=score>detector["threshold"]
        if novel:
            return engine.CONVENTIONAL,score,"NOVEL_INPUT_REFUSAL"
        return (robust if arm=="METADATA_SHIFT_GUARD" else plain,
                score,"IN_DISTRIBUTION_EMPIRICAL")
    raise worlds.HOLD("unregistered selector arm")


def prepare_training():
    begin=process_time_ns()
    incoming,provenance=worlds.training_worlds()
    models={}
    receipts={}
    for domain in worlds.DOMAINS:
        train={label:engine.records(domain,items)
               for label,items in incoming[domain].items()}
        cv=training_cv(domain,train)
        pooled=tuple(row for label,rows in sorted(train.items()) for row in rows)
        fitted={name:engine.compile_policy(domain,pooled,name)
                for name in engine.ALL_METHODS}
        detector=fit_shift_detector(domain,incoming[domain])
        frozen={name:engine.sha256_plan(model)
                for name,model in fitted.items()}
        frozen["DETECTOR"]=sha256(json.dumps(detector,sort_keys=True,
                    separators=(",",":")).encode()).hexdigest()
        frozen["SELECTORS"]=sha256(json.dumps({
            "plain":cv["mean_cv_candidate_selected"],
            "robust":cv["robust_empirical_candidate_selected"],
            "arms":META_ARMS,
        },sort_keys=True,separators=(",",":")).encode()).hexdigest()
        models[domain]=(fitted,cv,detector)
        receipts[domain]={
            "training_world_sizes":{k:len(v) for k,v in train.items()},
            "crossworld_policy_scores_and_decisions":cv,
            "input_shift_detector":detector,
            "frozen_model_components_sha256":frozen,
            "model_hash_sha256":sha256(json.dumps(frozen,sort_keys=True,
                                separators=(",",":")).encode()).hexdigest(),
        }
    hashes={name:detail["model_hash_sha256"] for name,detail in receipts.items()}
    root=sha256(json.dumps(hashes,sort_keys=True,
                separators=(",",":")).encode()).hexdigest()
    return models,{
        "training_corpus_provenance":provenance,
        "per_domain":receipts,
        "frozen_all_domain_hashes":hashes,
        "frozen_research_plan_sha256":root,
        "future_seed_datasets_not_requested_before_freeze":True,
        "training_cpu_ms":round((process_time_ns()-begin)/1e6,5),
        "risk_controls_are_empirical_selection_not_distribution_free":True,
    }


def _exact_replay(domain,case,policy,verified_cache=None):
    """Observe only queried questions; verify against an independent oracle.

    The optional cache is scoped to a single evaluated research world;
    it stores exact reference observations by (domain, case ID, question)
    when competing methods ask an IDENTICAL question on the same case.
    The independent calculation still occurs at least once per
    distinct evidence item, never by assuming a candidate result true.
    """
    cache={} if verified_cache is None else verified_cache
    def oracle(q):
        observed=legacy.observation(domain,case,q)
        key=(domain,case["id"],q)
        if key not in cache:
            cache[key]=legacy.independent_observation(domain,case,q)
        independently=cache[key]
        if observed!=independently:
            raise worlds.HOLD("exact proposed witness disagrees with reference")
        return observed
    result=engine.simulate(policy,case["id"],oracle)
    return {
        "case_id":case["id"],
        "solved":result["solved"],
        "questions":result["question_count"],
        "question_receipts":[{
            "question":(list(q) if isinstance(q,tuple) else q),
            "observed_pair":list(answer),
            "independent_oracle_agreed":True,
            "is_exact_counterexample":engine.is_witness(answer),
        } for q,answer in result["all_attempted_questions"]],
    }


def evaluate_world(domain,cases,programs):
    fitted,cv,detector=programs
    arms={}
    # Strong source-to-source comparison: one independently computed exact
    # reference receipt can be reused if another competing method asks
    # precisely the SAME question on the SAME case.
    exact_reference_receipts={}
    # Transparent baselines plus the shift-aware/robust selectors.
    for arm in (engine.CONVENTIONAL,"RAW_OBSERVATION_DIVERSITY",
                "JOINT_SHANNON_ENTROPY","CONTEXTUAL_VALUE_OF_INFORMATION",
                *META_ARMS):
        start=process_time_ns()
        rows=[]
        for case in cases:
            if arm in fitted:
                selected=arm
                distance=None
                gate="DIRECT_METHOD"
            else:
                selected,distance,gate=select_method(cv,detector,domain,
                                                     case,arm)
            outcome=_exact_replay(domain,case,fitted[selected],
                                  exact_reference_receipts)
            rows.append({
                **outcome, "selected_method":selected,
                "input_shift_score":distance,
                "shift_threshold":detector["threshold"] if distance is not None else None,
                "shift_gate_decision":gate,
                "selected_using_earlier_training_only":True,
            })
        arms[arm]={
            "cases":len(cases),
            "solved":sum(x["solved"] for x in rows),
            "questions":sum(x["questions"] for x in rows),
            "empirical_shift_refusals":sum(x["shift_gate_decision"]==
                                       "NOVEL_INPUT_REFUSAL" for x in rows),
            "cpu_ms_including_independent_exact_verification":
                round((process_time_ns()-start)/1e6,5),
            "question_and_gate_receipts":rows,
        }
    return arms


def run():
    models,training=prepare_training()
    # This call only occurs AFTER all all-domain SHA256 fingerprints exist.
    future,provenance=worlds.future_worlds()
    out={}
    summary={}
    diagnosis={}
    for domain in worlds.DOMAINS:
        out[domain]={name:evaluate_world(domain,cases,models[domain])
                     for name,cases in future[domain].items()}
        first=next(iter(out[domain].values()))
        summary[domain]={}
        for arm in first:
            allworld=[x[arm] for x in out[domain].values()]
            summary[domain][arm]={
                "cases":sum(x["cases"] for x in allworld),
                "solved":sum(x["solved"] for x in allworld),
                "questions":sum(x["questions"] for x in allworld),
                "shift_refusals":sum(x["empirical_shift_refusals"]
                                     for x in allworld),
            }
        # Post-evaluation hindsight is NEVER available to selectors.
        regret={}
        for arm in summary[domain]:
            regret[arm]=(summary[domain][arm]["questions"]-
                         summary[domain][engine.CONVENTIONAL]["questions"])
        diagnosis[domain]={
            "empirical_query_regret_vs_conventional":regret,
            "winner_on_these_seen_future_worlds_only":min(
                regret,key=lambda arm:(regret[arm],arm)),
            "winner_not_promoted_to_same_evaluation":True,
            "next_question":"Which input-shift features and training-world "
                            "diversity best predict regret before seeing "
                            "unasked mathematical evidence?",
        }
    return {
        "experiment":"MOTIF-LEGIT-029",
        "title":"DISTRIBUTION SHIFT — CAN A RESEARCHER DISTRUST ITS OWN METRIC?",
        "status":STATUS,
        "three_mathematical_goal_contracts":worlds.DOMAINS,
        "expert_principles":[
            "group-risk and worst-environment comparisons (not a DRO theorem)",
            "selective deferral to known classical greedy (not conformal coverage)",
            "free observable task metadata for empirical OOD scoring",
            "independent exact oracle and training/evaluation isolation",
        ],
        "candidate_selectors":list(META_ARMS),
        "training_and_frozen_methods":training,
        "future_world_provenance":provenance,
        "future_results":out,
        "aggregate_results":summary,
        "posthoc_diagnosis_not_used_for_any_future_policy":diagnosis,
        "limitations":[
            "No exchangeability, independence or conformal risk guarantee",
            "Complement graph tasks are dependent transformations of sampled carriers",
            "Synthetic math shifts were authored by experiment engineer",
            "Future worlds screened for old-probe failure and witness existence",
            "Input metadata are free by protocol; real collection may cost time",
            "Graph or polynomial direct solvers can have different better task contracts",
            "No independently administered blinded benchmark",
            "No new mathematical theory or fully autonomous self-modifying general reasoning",
            "No human engineer time, maintenance or external review costs measured",
        ],
    }


if __name__=="__main__":
    if sys.argv[1:]!=["--emit"]:
        raise SystemExit("Usage: python experiments/legit029/meta_guard.py --emit")
    print(json.dumps(run(),indent=2,sort_keys=True))
