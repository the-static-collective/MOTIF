# FIELD-001 — One fact, many possible worlds

**Question:** Can a single source-checked graph fact generate a recursive field of *ideas*, attributed *relations*, newly observed *facts*, and progressively less overgeneralized conjectures — without confusing hypotheses with observations? Does the repeated field reduce inquiries, or only reproduce ordinary classical search?

**Status:** Executed finite research prototype; **RESEARCH HOLD**, not a MOTIF deployment or a generally intelligent discovery system.

## One source fact and an explicit background grammar

The seed is an externally listed five-vertex path graph, Graph Atlas **G31**, with edges `(0,1),(1,2),(2,3),(3,4)`. The independent, historically published corpus is Ronald C. Read & Robin J. Wilson, *An Atlas of Graphs* (Oxford University Press, 1998), accessed through NetworkX **3.6.1** `graph_atlas_g()`. See <https://networkx.org/documentation/stable/reference/generated/networkx.generators.atlas.graph_atlas_g.html>.

The seed **does not** spontaneously supply a language, transformations, facts about graphs, verification machinery, or motivation. Researchers supply all of those: five labeled vertices, an edge-toggle operator, a 3-generation BFS, a four-context/four-target hypothesis grammar, and a corpus observation function. Only one *starting graph observation* is initially admitted. Do not mistake the supplied apparatus for discoveries from nothing.

For each *verified graph state*: (1) create one-edge-toggle **ideas**, (2) record edge-operation **relations** to their parent, (3) query a separate corpus-derived Atlas observer, (4) promote a proposed graph state to an **observed finite fact** only when an Atlas entry matches, and (5) repeat from newly admitted facts. Retain distinct labeled states even when their underlying unlabeled graph type is shared; store source id, corpus checksum, observed properties, revision, and content checksum with each receipt. A checksum identifies bytes, **not origin/authenticity**; `verify_receipt` independently queries the corpus again.

This is a complete finite graph universe of 5 labeled vertices, **not** access to arbitrary real-world facts. If the observer errors or fails, no additional fact is admitted.

## Executed experiment: expansion

| Observed generation | Distinct labeled graph states first encountered |
|---|---:|
| 0 (source) | 1 |
| 1 | 10 |
| 2 | 45 |
| 3 | 120 |
| **Total** | **176** |

After 3 generations the system has **175 new source-checked labeled graph observations**, **560** recorded proposed relation paths, and **27** distinct Atlas graph types. The labeled worlds overlap structurally; 175 is emphatically **not** 175 new mathematical theorems. The same original fact supports hundreds of branches, but their count is *finite and grammar-dependent*.

Memoization makes **176** Atlas source queries instead of **561** naive repeated-observation queries (**68.6275% fewer**). An independent, strong classical baseline using all ten labeled edge positions and exact Hamming-distance enumeration obtains the **same 176** distinct states and can use the **same 176** queries. **No computational advantage over classical deduplicated search** is demonstrated.

## Did the ideas form useful, revisable generalizations?

Two *predeclared* stages are frozen before examining the six-vertex holdout corpus. An authored hypothesis grammar examines an edit (`ADD` or `REMOVE`), optionally conditions on pre-edit graph properties (`all`, `parent_tree`, `parent_connected`, `parent_forest`), and nominates exactly one post-edit relationship (`delta_components`, `delta_cycle_rank`, `post_tree`, `post_connected`). A conjecture is proposed only when all training transitions in its scope have the same result and >=3 support cases. Repeated relation paths are not independent statistical samples.

| Training source | Proposed candidate rules | Holdout-supported | Refuted on holdout |
|---|---:|---:|---:|
| Generation 1 only: 10 transitions from a tree | 32 | 16 | **16** |
| Generations 1–3: 560 transition paths | 16 | **16** | 0 |

Holdout consists of **156 six-vertex graphs** from the same independently authored Atlas corpus, with **2,340 independently computed one-edge transitions**. Freeze SHA-256 values, exact rules and counterexamples appear in `experiment-results.json`.

Concrete negative finding: from the tree-only initial experience, the system incorrectly generalizes `REMOVE any edge -> components increase by one`. The heldout corpus supplies counterexamples (edges on cycles). Later observations of cyclic and disconnected graphs prevent that **unconditional** hypothesis from surviving training; the narrower `REMOVE edge FROM A TREE -> components increase by one` remains holdout-supported. This is a transfer result on **finite graphs**, not a novel theorem or globally guaranteed induction.

The later field contains more relational variety, filters spurious claims, and provides richer evidence ancestry. The validated pattern is **better discrimination under the declared hypothesis grammar**, not measured recursive improvement of arbitrary scientific research capability. No claim that an LLM automatically invented the grammar is warranted.

## Reproduction

```bash
python -m pip install networkx==3.6.1
cd experiments/field001
python field.py > /tmp/field001-reproduced.json
python -m unittest -v test_field.py
python - <<'PY'
import json
assert json.load(open('/tmp/field001-reproduced.json')) == json.load(open('experiment-results.json'))
print('MATCH')
PY
```

The tests include source-receipt corruption and a forged rehash; unknown source availability; connected 3-generation ancestry; 176-versus-561 accounting; classical exhaustive coverage; 16 false first-stage generalizations; fixed six-node holdout; and exact result reproduction.

## Scientific limitations and next falsifiers

This is research scaffolding, not autonomous general intelligence. The same *Atlas* corpus supplies both the 5-vertex observations and the 6-vertex holdout, though their graphs are disjoint. The source itself is externally authored, while the edit and hypothesis languages and the validation procedure were created for this experiment. The local Atlas package is not a separately authenticated live witness. No unknown-world intervention, creativity metric, independent experimental science, or general proof of compounding intelligence has been established.

A useful next falsifier is to **freeze the entire hypothesis generation program**, then move it to an independent domain and independent source corpus. Require at least one *verified hypothesis unavailable to the starting grammar*, with reproducible proof ancestry and matched classical controls. Stop or hold on absent evidence, corpus drift, forged claims, or incompatible semantics. Do not turn a conjecture into a fact merely because it has many descendants.
