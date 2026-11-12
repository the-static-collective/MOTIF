"""LLM-004 bounded source-owner study; export artifacts for inspection.

This test does NOT use model weights. It exercises the actual imported LLM-003
hidden owner and records which counterexamples were *useful after* verification.
All 160 x 4 x 4 x 4 trials are human-authored toy tasks, not an independent
general intelligence evaluation. Never use oracle accuracy as model input.
"""
import argparse,json
from pathlib import Path
from error_dividend import Owner,HELDOUT,REGIMES,BUDGETS,accuracy
from hypermap import ReasonHypermap,grade
from free_graph_adapter import packet_from_hypermap

POLICIES=("classical_ig","classical_ig_stop","challenge_favorite","decision_gain","no_probe")

def one(seed,regime,policy,budget):
    owner=Owner(seed,regime)
    m=ReasonHypermap(owner)
    start=accuracy(owner,m.weights)
    scores=[]
    for step in range(budget):
        proposal=m.choose_test(policy)
        if proposal is None:break
        before=list(m.weights)
        event=m.resolve(owner,proposal)
        scores.append(grade(owner,(before,m.weights),event))
    final=accuracy(owner,m.weights)
    return {"start":start,"final":final,"net":final-len(scores)*m.cost,
            "cost":len(scores)*m.cost,"probes":len(scores),
            "wrong_proposals":sum(s["actual_wrong_provisional"] for s in scores),
            "verified_counterexamples":sum(s["verified_counterexample"] for s in scores),
            "wrong_helpful_net":sum(s["wrong_helpful_net"] for s in scores),
            "wrong_not_helpful":sum(s["actual_wrong_provisional"] and not s["wrong_helpful_net"] for s in scores),
            "regressions":sum(s["regression"] for s in scores),
            "false_contradiction_reports":sum(s["reported_contradiction_not_ground_truth"] for s in scores)}

def run(seeds=HELDOUT):
    rows=[]
    for regime in REGIMES:
        for budget in BUDGETS:
            for policy in POLICIES:
                cases=[one(s,regime,policy,budget) for s in seeds]
                n=len(cases)
                a={"regime":regime,"budget":budget,"policy":policy,"n":n}
                for metric in ("start","final","net","probes"):
                    a["mean_"+metric]=round(sum(c[metric] for c in cases)/n,6)
                for metric in ("wrong_proposals","verified_counterexamples",
                  "wrong_helpful_net","wrong_not_helpful","regressions","false_contradiction_reports"):
                    a[metric]=sum(c[metric] for c in cases)
                rows.append(a)
    wins=[]
    for regime in REGIMES:
        for budget in BUDGETS:
            r=[x for x in rows if x["regime"]==regime and x["budget"]==budget]
            top=max(x["mean_net"] for x in r)
            wins.append({"regime":regime,"budget":budget,
                "winner_ties":[x["policy"] for x in r if abs(x["mean_net"]-top)<1e-9],
                "net":top})
    return {"schema":"motif.reason-hypermap.study/v0",
        "author_synthetic_only":True,"hidden_truth_unavailable_to_policy":True,
        "n_seeded_worlds":len(seeds),"n_conditions":len(rows),
        "score_definition":"actual owner prediction accuracy - 0.04 per attempted probe",
        "not_real_model_benchmark":True,"posthoc_arm":"classical_ig_stop",
        "arms":rows,"winners":wins}

def specimen(seed=None,regime="truthful"):
    # DISPLAY-ONLY curated illustrative source case. The separate independent
    # grader selects one test with a helpful, independently verified
    # counterexample. The model policy never receives the hidden owner truth.
    # Selection is NOT included in the 160-world outcome statistics.
    candidates=(seed,) if seed is not None else HELDOUT
    for chosen in candidates:
        o=Owner(chosen,regime)
        m=ReasonHypermap(o)
        p=m.choose_test("challenge_favorite",allow_costly=True)
        if p is None:continue
        imagination=m.imagined_outcomes(p)
        before=list(m.weights);event=m.resolve(o,p)
        score=grade(o,(before,m.weights),event)
        if seed is None and not score["wrong_helpful_net"]:continue
        return m,{"schema":"motif.reason-hypermap.specimen/v0",
                "world":"PUBLIC_AUTHOR_SYNTHETIC","source_seed":chosen,
                "display_case_selection":"CURATED_FIRST_HELPFUL_WRONG_FROM_HELDOUT_SET_NOT_RANDOM_SAMPLE" if seed is None else "EXPLICIT_SEED",
                "pencil_counterfactuals":imagination,
                "event":event,"separate_scoring_summary":score,
                "model_output_authority":"none"}
    raise ValueError("NO_ILLUSTRATIVE_SOURCE_CASE")

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",default=".")
    p.add_argument("--no-sweep",action="store_true")
    args=p.parse_args()
    path=Path(args.out);path.mkdir(parents=True,exist_ok=True)
    m,ex=specimen()
    print("CURATED_DISPLAY_ONLY",ex["source_seed"],
          "verified_wrong",ex["separate_scoring_summary"]["verified_counterexample"],
          "wrong_helpful_net",ex["separate_scoring_summary"]["wrong_helpful_net"])
    files={"specimen-map.json":m.public_graph(),
           "specimen-free-graph.json":packet_from_hypermap(m),
           "specimen-counterfactuals.json":ex}
    if not args.no_sweep:
        files["reason-hypermap-study.json"]=run()
    for name,obj in files.items():
        (path/name).write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
    print("LLM004_FILES",sorted(files))
    if "reason-hypermap-study.json" in files:
        for a in files["reason-hypermap-study.json"]["arms"]:
            if a["regime"] in ("truthful","noise20","echo_origin") and a["budget"] in (1,3):
                print("ARM",a["regime"],a["budget"],a["policy"],
                      "accuracy",a["mean_final"],"net",a["mean_net"],
                      "useful_wrong",a["wrong_helpful_net"],
                      "costly_wrong",a["wrong_not_helpful"])
        print("WINNERS",json.dumps(files["reason-hypermap-study.json"]["winners"],sort_keys=True))
if __name__=="__main__":main()
