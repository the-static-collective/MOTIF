"""Independent 2017 SyGuS public input, pinned by original Git blob hashes.

The original benchmark authors were independent of MOTIF (2017 vintage).
The research engineer selected these four tasks after browsing the 10-example
file headers. Public 100-example sets are NOT secret blind benchmarks, and
the same researchers wrote the experimental search code. They must never be
labeled completely blinded or independently evaluated inventions.

Source bytes for 10 and 100 examples, not merely parsed labels, are
archived under source/. The SHA-1 check uses the actual Git blob format.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from hashlib import sha1,sha256
import json
import re

HERE=Path(__file__).resolve().parent
FIXTURE=HERE/"source"/"sygus2017_2017PBE_BV_4cases.json"
PATTERN=re.compile(r"\(constraint\s*\(=\s*\(f\s+(#x[0-9a-f]{16})\)\s+(#x[0-9a-f]{16})\)\)")
PUBLIC_REPO="SyGuS-Org/benchmarks"
REVISION="13c8deb68a873635879c9a69bc78caebd340f646"
IDENTIFIERS=(101,112,100,103)
class HOLD(ValueError):pass

@dataclass(frozen=True)
class Problem:
    identifier: int
    train: tuple[tuple[int,int],...]
    test: tuple[tuple[int,int],...]
    sha_train: str
    sha_test: str

def git_blob_sha1(data:bytes)->str:
    return sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def load():
    obj=json.loads(FIXTURE.read_text(encoding="utf-8"))
    if (obj.get("schema")!="motif.sygus2017-public-source-corpus.v1"
        or obj.get("origin")!=PUBLIC_REPO
        or obj.get("repository_revision")!=REVISION
        or obj.get("benchmark_ids")!=list(IDENTIFIERS)
        or len(obj.get("cases",[]))!=4):
        raise HOLD("Unknown external original benchmark")
    tasks=[]
    for indexed,datum in zip(IDENTIFIERS,obj["cases"]):
        if datum["task_id"]!=indexed:
            raise HOLD("Reordered external source benchmark")
        extracted={}
        shas={}
        for key,expected_count,tag in (
                ("train_10",10,"10"),("external_test_100",100,"100")):
            original=datum["sources"][key]
            path=f"comp/2017/PBE_BV_Track/{indexed}_{tag}.sl"
            if original["path"]!=path:
                raise HOLD("External source path substitution")
            data=original["source"].encode("utf-8")
            sha=git_blob_sha1(data)
            if sha!=original["git_blob_sha1"] or original["rows"]!=expected_count:
                raise HOLD("External competition source content tampering")
            if "check-synth" not in original["source"] or "(set-logic BV)" not in original["source"]:
                raise HOLD("Not a source benchmark")
            rows=PATTERN.findall(original["source"])
            if len(rows)!=expected_count:
                raise HOLD("Incorrect number of competition examples")
            parsed=tuple((int(x[2:],16),int(y[2:],16)) for x,y in rows)
            if len(set(x for x,y in parsed))!=len(parsed):
                raise HOLD("Inconsistent/duplicated input examples")
            extracted[key]=parsed
            shas[key]=sha
        tasks.append(Problem(indexed,extracted["train_10"],
                             extracted["external_test_100"],
                             shas["train_10"],shas["external_test_100"]))
    return tuple(tasks)

def train_only(tasks):
    """Returns a fresh set of inputs with no public heldout examples."""
    return tuple((task.identifier,task.train) for task in tasks)

def external_test_for(tasks,solved):
    """Heldout labels accessed ONLY after the full source search is frozen."""
    if not isinstance(solved,dict):
        raise HOLD("Missing frozen source decisions")
    return {
        task.identifier:task.test for task in tasks
        if task.identifier in solved
    }

def provenance(tasks):
    return {
        "origin":"SyGuS-Org/benchmarks",
        "original_public_repository_commit":REVISION,
        "track":"SyGuS-Comp 2017 PBE_BV",
        "source_blob_git_sha1":{
            str(t.identifier):{"10":t.sha_train,"100":t.sha_test}
            for t in tasks},
        "competition_2017_precedes_experiment_2026":True,
        "task_authors_independent_of_MOTIF":True,
        "researcher_selected_task_ids":list(IDENTIFIERS),
        "benchmark_labels_public_not_private_blind":True,
        "no_independent_experiment_operator":True,
    }
