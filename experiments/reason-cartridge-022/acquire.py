"""Acquire INDEPENDENT bAbI task examples from a pinned third-party GitHub repo.

Task datasets were authored by other researchers, before this experiment,
and are not MOTIF's own source-owned synthetic case scripts. Files originate
from the Grokking-Deep-Learning copy of Facebook's bAbI tasksv11 corpus.
Each raw Git blob is pinned by its actual source Git SHA-1; each fetched file
is checked byte-for-byte against the pinned Git blob, not just its URL.

Citations:
- Weston et al., Towards AI-Complete Question Answering (2015), arXiv:1502.05698
- https://github.com/facebookarchive/bAbI-tasks
- https://github.com/iamtrask/Grokking-Deep-Learning/tree/e665168b4aefe3256360951504103cf98827ca51/tasksv11/en
- Dataset copyright remains with its original owners; CC BY 3.0 dataset.

The learner must not use task answer/support columns to solve a task. Those
fields are used ONLY for supervision and independently scored evaluation.
"""
from __future__ import annotations

from hashlib import sha1
from pathlib import Path
from urllib.request import urlopen
import json
import sys

SOURCE_REPO="iamtrask/Grokking-Deep-Learning"
COMMIT="e665168b4aefe3256360951504103cf98827ca51"
BASE="https://raw.githubusercontent.com/"+SOURCE_REPO+"/"+COMMIT+"/tasksv11/en/"
SOURCES={
    "COUNT": {
        "train":("qa7_counting_train.txt","6bb22084f6f832a7e31a24eb91dcd67c29188e3d"),
        "test":("qa7_counting_test.txt","970737f3bff6896c73e0e9cdf4050bd9fb38dcf8"),
    },
    "TRANSFER": {
        "train":("qa5_three-arg-relations_train.txt","ddfcb940b0c0f57ff6b14747241227751eb88541"),
        "test":("qa5_three-arg-relations_test.txt","ed9758be5dff62875321aa2ac2f5a35ae785b620"),
    },
    "TIME": {
        "train":("qa14_time-reasoning_train.txt","4e65c0b7597cd4441e1bf9da663689ad4e95119d"),
        "test":("qa14_time-reasoning_test.txt","c0c88cd92b690d6c533c3e532cb8a9e38ae8f1bf"),
    },
}
LICENSE="CC BY 3.0 (original bAbI dataset)"


class SourceUnavailable(RuntimeError):
    pass


def git_blob(raw):
    return sha1(b"blob "+str(len(raw)).encode("ascii")+b"\x00"+raw).hexdigest()


def get_sources(folder):
    root=Path(folder)
    root.mkdir(parents=True,exist_ok=True)
    audit=[]
    for family,parts in SOURCES.items():
        for split,(filename,expected_sha) in parts.items():
            dest=root/filename
            if dest.is_file():
                raw=dest.read_bytes()
            else:
                # Network is used for the public dataset only; no credentials
                # or personal sources ever cross this boundary.
                try:
                    with urlopen(BASE+filename,timeout=25) as handle:
                        raw=handle.read(1200001)
                except Exception as exc:
                    raise SourceUnavailable("Pinned external task unavailable: "+filename) from exc
                if len(raw)>1200000:
                    raise SourceUnavailable("External source exceeds size bound")
            if git_blob(raw)!=expected_sha:
                raise SourceUnavailable("External dataset changed or is not byte authentic: "+filename)
            if b"\t" not in raw or b"\n" not in raw or not raw.startswith(b"1 "):
                raise SourceUnavailable("External task is not a bAbI source file")
            if not dest.exists():
                dest.write_bytes(raw)
            audit.append({
                "task_family":family,"split":split,"filename":filename,
                "source_url":BASE+filename,"git_blob_sha1":expected_sha,
                "bytes":len(raw),"external_authorship":True,
                "dataset_license":LICENSE,
                "download_is_not_real_person_contact":True,
            })
    receipt={
        "schema":"motif.reason022.independent-external-source.v1",
        "source_repo":SOURCE_REPO,"source_commit":COMMIT,
        "attribution":"Facebook bAbI tasks; Weston et al. (2015)",
        "sources":audit,"real_human_wishes_not_observed":True,
    }
    (root/"provenance.json").write_text(
        json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf8")
    return receipt


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: python acquire.py reason-022-sources")
    report=get_sources(sys.argv[1])
    print(json.dumps({"source_files":len(report["sources"]),
                      "git_blob_verified":True,
                      "dataset":report["attribution"],
                      "source_commit":report["source_commit"]},
                     sort_keys=True))
