"""RING-003: discover *multiple possible uses* for any pinned source-only branch.

This is deliberately a source-text term lens, NOT an AI model, code execution,
causal inference, or verified capability admission. One source branch can have
several independent potential uses. Each suggestion carries its exact source
line and the weaker status SOURCE_WORD_MATCH_ONLY. Inference and runtime are
strictly downstream review steps, never automatic from the words alone.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import source_reader
import hypergraph

# A bounded, auditable vocabulary. Tokens are searched as literal text.
# Many use heads can come from one token. The same use can be proposed by
# multiple sources; it stays an unverified many-to-many relationship.
TERM_MAP={
    "graph":("graph-inspection","structural-visualization"),
    "question":("question-construction","evidence-gap-triage"),
    "proof":("proof-checking","counterargument-review"),
    "counterexample":("falsification-search","hypothesis-revision"),
    "instrument":("measurement-instrument-analysis","procedure-debugging"),
    "measurement":("measurement-design","data-quality-audit"),
    "language":("utterance-interpretation","human-interface-design"),
    "model":("model-evaluation","hypothesis-comparison"),
    "planning":("plan-inspection","affordance-search"),
    "memory":("failure-recall","continuity-tracing"),
    "consent":("permission-boundary-review","handoff-audit"),
    "test":("test-design","regression-review"),
}
MAX_TERMS=12


def analyze(catalog,ref,*,repo_root:Path,prefix=None,terms=None):
    source=source_reader.choose_passport(catalog,ref)
    terms=("question","proof","counterexample","instrument",
           "language","model","planning","memory") if terms is None else tuple(terms)
    if (not 1<=len(terms)<=MAX_TERMS or len(set(terms))!=len(terms)
            or any(type(t) is not str or t not in TERM_MAP for t in terms)):
        raise hypergraph.HOLD("Unknown, repeated, or excessive analyst vocabulary")
    bid="source:"+source["id"]
    nodes=[{"id":bid,"type":"PINNED_NON_EXECUTABLE_BRANCH_SOURCE",
            "ref":source["ref"],"commit":source["commit"]}]
    edges=[]
    proposals={}
    partial_terms=[]
    for term in terms:
        packet=source_reader.inspect(catalog,ref,term,repo_root=repo_root,
                                     path_prefix=prefix,max_hits=5)
        if packet["status"]=="PARTIAL":
            partial_terms.append(term)
        if not packet["matches"]:
            continue
        spans=[]
        for match in packet["matches"][:3]:
            body=(source["commit"]+"|"+match["path"]+"|"+str(match["line"])+"|"+term)
            witness_id="witness:"+sha256(body.encode()).hexdigest()[:24]
            nodes.append({
                "id":witness_id,"type":"UNTRUSTED_SOURCE_TEXT_OCCURRENCE",
                "path":match["path"],"line":match["line"],
                "excerpt_untrusted_document_text":match["excerpt_untrusted_document_text"],
                "is_not_a_verified_method_output":True,
            })
            spans.append(witness_id)
        suggested=list(TERM_MAP[term])
        edges.append({
            "id":"suggestion:"+term,
            "tails":[bid,*spans],
            "heads":suggested,
            "kind":"SOURCE_WORD_MATCH_ONLY",
            "verified_use":False,
            "admitted_for_execution":False,
            "provenance_paths":[
                {"path":m["path"],"line":m["line"]} for m in packet["matches"][:3]
            ],
        })
        for possible in suggested:
            proposals.setdefault(possible,[]).append(term)
    for affordance in sorted(proposals):
        nodes.append({"id":affordance,"type":"UNVERIFIED_POSSIBLE_USE",
                      "matched_terms":sorted(proposals[affordance])})
    report={
        "schema":"motif.branch-multiuse-analysis.v1",
        "source":bid,"source_ref":source["ref"],
        "pinned_commit":source["commit"],
        "vertices":nodes,"hyperedges":edges,
        "proposed_uses":sorted(proposals),
        "unsearched_terms_are_not_absent_capabilities":True,
        "partial_term_searches":partial_terms,
        "text_cooccurrence_is_not_verified_capability":True,
        "does_not_infer_all_sibling_branch_ancestry":True,
        "does_not_change_live_method_registry":True,
        "branch_code_executed":False,"authority":"NONE",
    }
    report["receipt_sha256"]=sha256(json.dumps(report,sort_keys=True,
        separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--catalog",type=Path,required=True)
    p.add_argument("--ref",required=True)
    p.add_argument("--prefix")
    p.add_argument("--terms",nargs="+",choices=sorted(TERM_MAP))
    p.add_argument("--repo-root",type=Path,
                   default=Path(__file__).resolve().parents[2])
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        cat=json.loads(a.catalog.read_text())
        result=analyze(cat,a.ref,repo_root=a.repo_root,prefix=a.prefix,
                       terms=a.terms)
        data=json.dumps(result,indent=2,sort_keys=True)+"\n"
        if a.out:
            a.out.parent.mkdir(parents=True,exist_ok=True)
            a.out.write_text(data)
            print(json.dumps({"status":"UNVERIFIED_MULTIUSE_CANDIDATES",
                "uses":len(result["proposed_uses"]),"receipt":result["receipt_sha256"],
                "output":str(a.out)}))
        else:
            print(data,end="")
    except (hypergraph.HOLD,source_reader.HOLD) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc),
            "branch_code_executed":False}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
