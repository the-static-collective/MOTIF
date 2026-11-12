"""Emit a real public 200+-action Reason Hypermap replay dossier and offline HTML.

The display seed is deliberately curated for inspectability. Experimental
metrics are from the full separate registered 64-seed trial, not the display.
"""
import argparse,json
from pathlib import Path
from odyssey import LongChain,SCENARIO_SEEDS,POLICIES,experiment
from viewer_long import render

def select_specimen():
    for seed in SCENARIO_SEEDS:
        runs={p:LongChain(seed,p) for p in POLICIES}
        summaries={p:run.execute() for p,run in runs.items()}
        if all(s["completed"] for s in summaries.values()) and (
            summaries["hypermap_voi"]["metrics"]["optional_probes"]>0
            and summaries["hypermap_voi"]["metrics"]["wrong_commits"]>0):
            return seed,runs
    raise ValueError("NO_COMPLETE_ILLUSTRATIVE_WORLD")

def payload(study,seed,runs):
    if study.get("schema")!="motif.odyssey-240-study/v0":
        raise ValueError("NONSTUDY")
    out={"schema":"motif.odyssey-viewer/v0","seed":seed,
         "selection_note":"Curated first scenario where all four policies finish with verified wrong guesses and optional independent probes in the hypermap arm. Display not used for benchmark statistics.",
         "study":study,"traces":{p:runs[p].public_trace() for p in POLICIES},
         "reason_maps":{str(i):m.public_graph()
                  for i,m in enumerate(runs["hypermap_voi"].maps)},
         "external_actions":False,"real_model":False,"no_private_sources":True}
    return out

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",default="/tmp/odyssey240")
    a.add_argument("--study-file")
    args=a.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    if args.study_file:
        study=json.loads(Path(args.study_file).read_text())
    else:study=experiment()
    seed,runs=select_specimen()
    d=payload(study,seed,runs)
    (out/"odyssey240-dossier.json").write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    (out/"odyssey240.html").write_text(render(d))
    (out/"odyssey240-display-summary.json").write_text(json.dumps({
        "seed":seed,"selection_note":d["selection_note"],
        "min_required_actions":219,
        "policies":{p:runs[p].summary() for p in POLICIES},
        "source_boundary":"PUBLIC_AUTHOR_SYNTHETIC_ONLY",
        "real_pretrained_model":"NOT_EXECUTED_THIS_PHASE"},sort_keys=True,indent=2)+"\n")
    print("ILLUSTRATIVE_SCENARIO",seed)
    for p in POLICIES:
        s=runs[p].summary()
        print("ILLUSTRATIVE_ARM",p,"status",s["state"],"actions",s["actions"],
              "wrong",s["metrics"]["wrong_commits"],"cost",s["cost"])
    print("GENERATED_OFFLINE_VIEWER_BYTES",(out/"odyssey240.html").stat().st_size)
if __name__=="__main__":main()
