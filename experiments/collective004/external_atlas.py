"""Independent-origin Graph Atlas pressure test for COLLECTIVE-004.

Uses the exact original LEGIT-022 Read/Wilson 1998 Graph Atlas carrier,
its pinned NetworkX 3.4.2 data SHA, 14 TRAIN + 28 HELDOUT split.
MOTIF's previously authored OLD feature menu is frozen before any heldout
question synthesis. The new bounded endpoint-degree AST grammar is also
frozen. Selection is allowed to inspect both possible graph models, but
never the owner's hidden realized-world selection. Honest HOLD is a result.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from question_inventor import (HOLD, digest, canonical, emit_program,
                               execute, independent_execute, old_measurements)

LEGIT022_COMMIT = "375df67205fbae5788a9feb3b79a339ef4e423b4"
LEGIT022_ATLAS_BLOB = "55d60dacd0dc55b9ab3f618311e881efd5017da0"
ATLAS_DATA_SHA256 = "73fc416df0164923607751cb759f4ae81deb5f6550bf25be59c86de3b747e41d"
SCHEMA = "motif.collective004.external-atlas-question-transport.v1"


def source_module(atlas_root):
    root = Path(atlas_root).resolve()
    path = root / "experiments/legit022/atlas.py"
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root):
        raise HOLD("No approved original Atlas carrier source")
    def git(*argv):
        p = subprocess.run(("git", *argv), cwd=root, capture_output=True,
                           text=True, timeout=20)
        if p.returncode != 0:
            raise HOLD("Failed source Git pin")
        return p.stdout.strip()
    if git("rev-parse", "HEAD") != LEGIT022_COMMIT or git(
        "hash-object", "experiments/legit022/atlas.py"
    ) != LEGIT022_ATLAS_BLOB:
        raise HOLD("Original Atlas source revision/blob changed")
    spec = importlib.util.spec_from_file_location("source_owned_legit022_atlas",
                                                  path)
    if spec is None or spec.loader is None:
        raise HOLD("Cannot import pinned Atlas carrier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if module.EXPECTED_ATLAS_SHA256 != ATLAS_DATA_SHA256:
        raise HOLD("Original Atlas data pin drift")
    return module


def carrier(pair):
    n, edges = pair
    if n != 7 or type(edges) is not tuple:
        raise HOLD("Only original seven-vertex external Atlas graphs")
    normalized = set()
    for a, b in edges:
        if not (type(a) is int and type(b) is int and 0 <= a < b < 7):
            raise HOLD("Bad independent Atlas edge")
        normalized.add((a,b))
    if len(normalized) != len(edges):
        raise HOLD("Duplicate Atlas carrier edge")
    return {"n":7,"edges":[list(e) for e in sorted(normalized)]}


def external_queries(worlds):
    """Frozen synthetic grammar; no target oracle observations used."""
    a,b = worlds
    ds = sorted(set(sum(v in edge for edge in a["edges"]) for v in range(7)) |
                set(sum(v in edge for edge in b["edges"]) for v in range(7)))
    ds = [d for d in ds if d > 0]
    # The grammar did NOT change after inspecting the heldout Atlas. These
    # are the same two-ended, typed edge-quantification questions from 004.
    return [emit_program(k,j) for k in ds for j in ds if k <= j]


def native_nx_eval(ast, graph):
    """Strong independent NetworkX baseline, NOT the MOTIF interpreter."""
    import networkx as nx
    g = nx.Graph()
    g.add_nodes_from(range(graph["n"]))
    g.add_edges_from(graph["edges"])
    k = ast["endpoints"][0]["degree_equals"]
    j = ast["endpoints"][1]["degree_equals"]
    if ast["schema"] != "motif.collective004.graph-question-ast.v1":
        raise HOLD("Unexpected grammar")
    return any(sorted((g.degree(u),g.degree(v))) == [k,j]
               for u,v in g.edges())


def select_question(worlds):
    left,right=worlds
    if old_measurements(left)!=old_measurements(right):
        return {"status":"OLD_MENU_SUFFICIENT_NO_EXPANSION",
                "new_grammar_questions_executed":0}
    options=external_queries(worlds)
    scored=[]
    for ast in options:
        native=[native_nx_eval(ast,g) for g in worlds]
        motif=[execute(ast,g) for g in worlds]
        matrix=[independent_execute(ast,g) for g in worlds]
        if motif!=native or motif!=matrix:
            raise HOLD("Three independent question evaluators disagree")
        scored.append({"ast":ast,"fingerprint":native,
                       "distinguishes":native[0]!=native[1]})
    separating=sorted(
        (canonical(item["ast"]),item) for item in scored if item["distinguishes"]
    )
    if not separating:
        return {"status":"HOLD_NEW_GRAMMAR_STILL_INSUFFICIENT",
                "catalog":scored,"new_grammar_questions_executed":0}
    selected=separating[0][1]
    # Strong separate classical exhaustive selection over the SAME typed
    # possible-world views, costs, AST grammar, and independent NetworkX API.
    classical=next(
        (ast for _,ast in sorted((canonical(q),q) for q in options)
         if native_nx_eval(ast,left)!=native_nx_eval(ast,right)),
        None,
    )
    if selected["ast"]!=classical:
        raise HOLD("Fair classical comparator does not tie selected program")
    return {"status":"NEW_GRAMMAR_SEPARATES_ATLAS_PAIR",
            "catalog":scored,
            "selected_program":selected["ast"],
            "predictions":selected["fingerprint"],
            "classical_exhaustive_exact_tie":True,
            "new_grammar_questions_executed":1}


class AtlasOwner:
    def __init__(self, pair_ids, realized_graph, *, revision=1):
        if (type(pair_ids) not in (tuple,list) or len(pair_ids)!=2
                or any(type(v) is not int for v in pair_ids)):
            raise HOLD("Missing public external Atlas pair identity")
        self._ids=list(pair_ids)
        self._graph=deepcopy(realized_graph)
        self._revision=revision
        self.questions=0
        self.rechecks=0
    def contract(self):
        return {"kind":"PUBLIC_ATLAS_GRAPH_SIMULATED_OWNER",
                "candidate_graph_ids":self._ids,
                "revision":self._revision,
                "external_source_authenticated_as_human":False,
                "which_candidate_realized_is_not_in_contract":True}
    def ask(self, ast):
        self.questions+=1
        receipt={"schema":"motif.collective004.external-atlas-observation.v1",
                 "owner_contract":self.contract(),
                 "selected_question":deepcopy(ast),
                 "value":native_nx_eval(ast,self._graph),
                 "synthetic_fixture_not_real_world_instrument":True}
        receipt["integrity_digest"]=digest(receipt)
        return receipt
    def recheck(self, receipt):
        self.rechecks+=1
        if (type(receipt) is not dict or set(receipt)!={
                "schema","owner_contract","selected_question","value",
                "synthetic_fixture_not_real_world_instrument","integrity_digest"
            } or receipt["integrity_digest"]!=digest({
                k:v for k,v in receipt.items() if k!="integrity_digest"
            }) or receipt["owner_contract"]!=self.contract()
            or receipt["schema"]!="motif.collective004.external-atlas-observation.v1"
            or type(receipt["value"]) is not bool
            or receipt["synthetic_fixture_not_real_world_instrument"] is not True
            or receipt["value"]!=native_nx_eval(
                receipt["selected_question"],self._graph)):
            raise HOLD("Atlas source observation cannot be reauthenticated/replayed")
        return True


def inspect_pair(task, *, include_evidence=True):
    worlds=tuple(carrier(z) for z in task.graphs)
    proposed=select_question(worlds)
    case={"pair_ids":list(task.atlas_ids),
          "old_feature_collision":old_measurements(worlds[0])==old_measurements(worlds[1]),
          "result":proposed["status"]}
    if proposed["status"]!="NEW_GRAMMAR_SEPARATES_ATLAS_PAIR":
        case["no_outcome_claimed"]=True
        case["fresh_source_calls"]=0
        case["reason"]="Old operator sufficient or new grammar lacks discriminator"
        return case
    ast=proposed["selected_program"]
    cases=[]
    for realized_index in (0,1):
        owner=AtlasOwner(task.atlas_ids,worlds[realized_index])
        receipt=owner.ask(ast)
        owner.recheck(receipt)
        survivors=[i for i,x in enumerate(proposed["predictions"])
                   if x==receipt["value"]]
        if survivors!=[realized_index]:
            raise HOLD("Classified wrong independent Atlas graph")
        before=owner.questions
        owner.recheck(json.loads(json.dumps(receipt)))
        if owner.questions!=before:
            raise HOLD("Unexpected new Atlas question on re-entry")
        cases.append({"actual_index_evaluator_only":realized_index,
                      "identified_world_index":survivors[0],
                      "new_source_queries":owner.questions,
                      "reentry_new_source_queries":0,
                      "owner_rechecks":owner.rechecks,
                      "evidence_receipt":receipt if include_evidence else None})
    case.update({
        "generated_candidate_count":len(proposed["catalog"]),
        "invented_program":ast,
        "candidate_fingerprints":proposed["catalog"] if include_evidence else [],
        "classical_exhaustive_exact_tie":True,
        "source_observations":cases,
        "fresh_source_calls":sum(x["new_source_queries"] for x in cases),
    })
    return case


def run(atlas_root):
    atlas=source_module(atlas_root)
    train,test,protocol=atlas.cohort()
    atlas.verify_prepared(train,test,protocol)
    train_records=[inspect_pair(t,include_evidence=False) for t in train]
    test_records=[inspect_pair(t,include_evidence=True) for t in test]

    def counts(records):
        old_resolved=sum(not r["old_feature_collision"] for r in records)
        unsolved=sum(r["old_feature_collision"] for r in records)
        new=sum(r["result"]=="NEW_GRAMMAR_SEPARATES_ATLAS_PAIR" for r in records)
        held=sum(r["result"]=="HOLD_NEW_GRAMMAR_STILL_INSUFFICIENT" for r in records)
        if old_resolved+new+held!=len(records) or new+held!=unsolved:
            raise HOLD("Missing or silently omitted independent Atlas case")
        return {"total":len(records), "old_menu_resolved":old_resolved,
                "old_menu_unresolved":unsolved,
                "new_grammar_additionally_resolved":new,
                "honest_new_grammar_holds":held,
                "matched_classical_successes":new,
                "owner_questions_for_two_realizations":
                    sum(r["fresh_source_calls"] for r in records)}
    summary={
        "schema":SCHEMA, "source":"Read/Wilson 1998 Graph Atlas via source-owned LEGIT-022",
        "atlas_source_commit":LEGIT022_COMMIT,
        "atlas_loader_blob_sha":LEGIT022_ATLAS_BLOB,
        "atlas_data_sha256":ATLAS_DATA_SHA256,
        "original_source_protocol":protocol,
        "train":counts(train_records), "heldout":counts(test_records),
        "train_trials":train_records,"heldout_trials":test_records,
        "question_ast_grammar_frozen_before_heldout":True,
        "source_pairing_unaffected_by_new_grammar_results":True,
        "equal_information_classical_best_same_grammar":True,
        "heldout_is_public_not_cryptographically_blind":True,
        "question_oracle_is_synthetic_public_dataset_not_actual_external_agent":True,
        "no_new_scientific_law_or_historical_truth_proven":True,
        "automatic_admission":False,"installed":False,
        "external_authority":"NONE",
    }
    summary["integrity_digest"]=digest(summary)
    return summary


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--atlas-root",required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.atlas_root),indent=2,sort_keys=True))
