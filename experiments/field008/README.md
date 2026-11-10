# MOTIF FIELD-008 — THE BLANCHING FRONTIER

> **A hypothesis may be used as a provisional foothold without becoming a fact.**
> From that foothold, explore its conditional consequences, identify an especially
> consequential measurement several reasoning steps away, and ask the *actual source*
> exactly once. Keep the full source receipt and retract only the contradicted pencil
> branches. Source facts are INK; conditional scenarios remain PENCIL.

**Status: RESEARCH HOLD, unmerged stacked draft.** This experiment is a bounded implementation of the user's *blanching* idea, not a claimed discovery of new mathematics, real-world fact authentication, a calibrated probability estimator, or autonomous scientific exploration. A source-derived mathematical corpus is not a blind live laboratory. **Original pre-score protocol:** [PREREGISTRATION.md](PREREGISTRATION.md). Its commit must remain earlier than the experiment's score commit.

## What was actually examined

- **Outside authored source data:** Read & Wilson, *An Atlas of Graphs* (1998), through **NetworkX 3.6.1** `graph_atlas_g()` (1,253 graph types, up to seven vertices). Six-vertex population: **all 156** source graphs. Seven-vertex additional challenge: **96** graph IDs selected by a predeclared SHA-256 rule from all 1,044 seven-vertex graphs. Source revision SHA-256: `17f940be3d89a623bc291e0e3eb64b108987cd68a2c4f0a82b98b3294153bad9`. Full graph atlas remains available as the catalogue of *possible* worlds; it does **not** expose the hidden current graph to the question selector.
- **Starting INK fact:** The source-reported number of vertices and edges. This is one owner-origin record, **not two independent witnesses**. Possible worlds matching that record remain hypothetical; all distinguishable graph questions are pre-authored mathematical transformations.
- **Conditional reasoning depth 1–5:** Edge presence (1); degree (2); mutual neighbors/triangle count (3); four-cycle count/connectivity (4); bridge count/articulation count (5). Each candidate answer is computed *conditionally* for each consistent model, then the chosen question is answered by a separate source-owner routine. These depths count symbolic derivation hops, **not automatically executed physical procedures**, and every allowed probe costs one source question in this synthetic benchmark. CPU work is not equal.
- **Proof gates:** A query is proposed and sealed **before** the actual answer is requested; source replay independently recomputes answers with different algorithms where possible; results have corpus revision hashes and chronological source-query counters. Rehashed false source answers, stale revisions and unknown operations fail. Every hypothetical candidate remains PENCIL; matching an observation does not itself turn a model into an established fact.
- **AND/OR truth maintenance:** `grounding.py` extends the original FIELD-006 `Lineage` implementation. Ancestry counts distinct source origins, **not repeated copies**; OR alternatives do not fuse into bogus combined evidence. A refuted local prediction loses only its dependent support routes. Even two origins do not establish a numeric probability.

## Predeclared experiment and strong controls

Give each policy at most **four** extra source questions and the same graph catalogue. Report whether the hidden Atlas graph is *uniquely* determined, and separately whether five downstream graph properties have become logically fixed across all surviving possibilities.

| Policy | Question selection |
|---|---|
| NEAR (shallow) | Best edge-only question; depth-1 only. |
| Classical ENTROPY | Maximum Shannon information across **all** depth-1..5 questions. |
| Classical GINI | Maximum pair-discrimination across **all** depth-1..5 questions. |
| MOTIF BLANCH | Largest expected number of resolved **structural properties** across consistent conditional worlds; ties by pair-discrimination and shallower cost; retain and trace a small set of provisional branches. |
| Classical VALUE (additional **post-score diagnostic**, NOT preregistered) | Same exhaustive property-resolution objective, **without** a PENCIL branch object. It should tie BLANCH exactly; a classical solver can optimize the same goal. |

The BLANCH selector scores **all** surviving world hypotheses, not just the illustrative four PENCIL models preserved in each proof packet. It never prunes a hypothesis because it was less appealing or less grounded; eliminating a world requires a verified source result that contradicts its prediction. The version space is a finite possibility catalogue, not a posterior probability distribution over reality.

## Results — independently sourced mathematical archive, authored investigation

| Six-vertex cohort (156 hidden targets) | Graph identified after ≤4 queries | Target properties resolved /780 | Source questions |
|---|---:|---:|---:|
| NEAR | 103/156 | 713/780 | 563 |
| Classical ENTROPY | **156/156** | **780/780** | 344 |
| Classical GINI | **156/156** | **780/780** | 344 |
| BLANCH | 154/156 | **780/780** | 370 |
| Classical VALUE (post-score) | 154/156 | **780/780** | 370 |

| Seven-vertex SHA-selected cohort (96 targets) | Graph identified after ≤4 queries | Target properties resolved /480 | Source questions |
|---|---:|---:|---:|
| NEAR | 6/96 | 138/480 | 377 |
| Classical ENTROPY | 84/96 | 471/480 | 294 |
| Classical GINI | **87/96** | 473/480 | 294 |
| BLANCH | 79/96 | **480/480** | 300 |
| Classical VALUE (post-score) | 79/96 | **480/480** | 300 |

**Primary preregistered verdict: NO win over strong classical.** Entropy and GINI outperform BLANCH at identifying the precise graph. BLANCH completely resolves the **five explicitly prioritized structural properties** in the seven-vertex cohort, while GINI does so for 473/480 and ENTROPY 471/480. But its *identical classical VALUE control* also achieves 480/480; that is a **change of objective**, not a new algorithm or classical superiority. BLANCH uses more source queries and more conditional evaluations than strong classical GINI. No claim of general computational or query efficiency is supported.

### Concrete one-question-to-many-properties example

Source target **G608** (seven vertices): starting edge-count fact leaves **148 possible graph models**. BLANCH asks a sequence of four verified source questions:

1. Four-cycle count (depth 4) = **5** → 31 possibilities.
2. Triangle count (depth 3) = **5** → 12 possibilities.
3. Articulation count (depth 5) = **2** → 8 possibilities.
4. Degree of vertex 0 (depth 2) = **4** → 4 possibilities.

The remaining four graphs are *not* identified as the same graph. However, their values for the five targeted properties are identical. **The properties are determined relative to this complete, explicitly bounded Atlas catalogue; this is not an unrestricted-world proof.** Each queried answer comes from the archive owner, not the speculation. Each abandoned graph possibility is marked retracted; surviving alternatives remain.

## Reproduction

```bash
# checkout this unmerged FIELD-008 branch, Python 3.13
python -m pip install 'networkx==3.6.1'
python -m unittest discover -s experiments/field008 -p 'test_blanch.py' -v
python experiments/field008/blanch.py > /tmp/field008-results.json
cmp /tmp/field008-results.json experiments/field008/experiment-results.json
python experiments/field008/demo.py > /tmp/field008-demo.json
```

Local unit tests cover the independently recomputed source predictions over all 156 six-vertex graphs and 96 seven-vertex cases, source drift, forged-and-rehashed reports, source isolation, proposal-before-query ordering, selective retraction, independent-origin support counts, full-vs-shallow baselines and exact result reproduction. GitHub Actions runs these checks in the original stacked repository.

## What this confirms / what it does not

**Confirmed in a finite mathematical sandbox:** deeper conditional queries can eliminate large sets of potential worlds and resolve multiple important facts with one sourced observation; provisional branches can be traced without becoming observations; source contradictions selectively retract unsupported branches. The approach can favor resolving *consequential properties* rather than identifying every detail of a model.

**Not confirmed:** probability calibration, genuine source independence, learning a new reasoning grammar, true prediction of external events, invention of wholly new test operators, novel mathematics, the superiority of BLANCH over the strong classical solver allowed the same objective, or improved efficiency in physical investigations. Candidate graphs and the full question menu are already known. The utility objectives and costs are authored. This experiment should stay a draft research HOLD, with no merges, deployments, credentials, or real-world actions.

**Next falsifier:** Give two groups of source-owned observations whose provenance and relevance genuinely differ, plus unseen source mechanisms, unequal measurement costs and missing candidate-world hypotheses. Freeze a conditional search policy *before* seeing external answers. Require the possibility search to retain unknown/OTHER hypotheses and choose an informative deep test while both strong entropy and strong **value-aware** classical lookahead get equal compute and measurement budgets. Test independent prospective outcomes, not only one preexisting graph archive.
