"""Evaluator-only graph families: freeze teacher / hidden review splits.

This code intentionally knows graph labels to stratify samples. The pupil only
receives specimen/receipt pairs emitted by the original Dogram CLI.
"""
from __future__ import annotations

from collections import deque
from itertools import combinations
from pathlib import Path
from hashlib import sha256
import json
import random

DOGRAM_COMMIT = "551b5f9df18f17ec69b452ddcdff01718e0ff771"
DOGRAM_REPO = "the-static-collective/Dogram"
SPLITS = {"train": (5, 4), "withheld": (6, 6)}


def check_path(nodes, edges, source="S", target="T"):
    active = set(edges)
    frontier = deque([source])
    reached = {source}
    while frontier:
        node = frontier.popleft()
        if node == target:
            return True
        for a, b in sorted(active):
            if a == node and b not in reached:
                reached.add(b)
                frontier.append(b)
    return False


def specimen(split, index, nodes, edges, removed):
    return {
        "schema": "dogram.specimen/v0",
        "specimen_id": f"motif-reason-003-{split}-{index:02d}",
        "operator": "ablate", "operator_version": 1,
        "inputs": {
            "graph": {"nodes": list(sorted(nodes)),
                      "edges": [list(e) for e in sorted(edges)]},
            "target": {"kind": "edge", "source": removed[0],
                       "target": removed[1]},
            "requested_targets": [["S", "T"]],
        },
        "assumptions": [],
        "metadata": {
            "synthetic_only": True,
            "teacher_repo": DOGRAM_REPO,
            "teacher_commit": DOGRAM_COMMIT,
            "observed_teaching_only": True,
        },
    }


def specimens(split):
    if split not in SPLITS:
        raise ValueError("Unknown evidence split")
    width, count = SPLITS[split]
    nodes = ("S",) + tuple("ABCDE"[:width-2]) + ("T",)
    possible = list(combinations(nodes, 2))
    rng = random.Random(80221 if split == "train" else 91337)
    targets = [(False, False), (True, False), (True, True)]
    outputs, seen = [], set()
    for status in targets:
        made, tries = 0, 0
        while made < count:
            tries += 1
            if tries > 40000:
                raise RuntimeError(f"Insufficient synthetic {split} examples for {status}")
            density = rng.uniform(0.18, 0.78)
            edges = tuple(e for e in possible if rng.random() < density)
            if not edges:
                continue
            removed = rng.choice(edges)
            key = (edges, removed)
            if key in seen:
                continue
            before = check_path(nodes, edges)
            after = check_path(nodes, tuple(e for e in edges if e != removed))
            if (before, after) != status:
                continue
            seen.add(key)
            outputs.append(specimen(split, len(outputs), nodes, edges, removed))
            made += 1
    return tuple(outputs)


def emit(directory):
    root = Path(directory)
    for split in SPLITS:
        folder = root / split
        folder.mkdir(parents=True, exist_ok=True)
        for item in specimens(split):
            (folder / (item["specimen_id"] + ".json")).write_text(
                json.dumps(item, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps({
        "schema": "motif.reason.foreign-teacher-manifest.v1",
        "source_repo": DOGRAM_REPO, "source_commit": DOGRAM_COMMIT,
        "split_counts": {name: len(specimens(name)) for name in SPLITS},
        "native_teacher_required": True, "teacher_remove_before_evaluation": True,
        "real_world_authority": False,
    }, sort_keys=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("usage: python fixtures.py <output-directory>")
    emit(sys.argv[1])
