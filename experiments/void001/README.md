# VOID-001 — The Missing Middle: research feed + first question-to-outcome mesh

**DRAFT / RESEARCH HOLD, stacked on CONFLUENCE-003.** This is an intentionally small executable intervention, not a trained LLM, an AGI breakthrough, an authorized physical-world agent, or proof that MOTIF beats strong baselines.

## What this actually feeds MOTIF

- `sources.json` registers **11 verified external source entrances**. It distinguishes benchmark code, gated task files, research papers, and a survey report. No task files or hidden answer keys are smuggled into the repository. **OSWorld-V2 task classes and assets require separate Hugging Face acceptance**. The Traverse first-error annotations in the cited paper are not confused with the unrelated ByteDance *Traverse* project. AIDE² and G2 are research constraints, not runnable task datasets.
- `challenges.json` stores **14 original derivative problem cards**, inspired by specific published failure modes (changing constraints, lost state, oversight cost, incomplete authority, adversarial reports, incorrect action confirmations, hidden prerequisites, and more). **No upstream official benchmark problems have been imported into these cards**.
- `mesh.py` imports and executes **original main-tree MOTIF-003** read-only affordance analysis. It generates two candidate outcomes per simulated observation without exposing hidden truth. It records verified source receipts and keeps historical receipts when a synthetic source epoch changes. Plans are gated on permission being true in *every* surviving world, and outcome success requires a separately attested synthetic owner result.
- The frozen finite classical comparators are an exhaustive uniform-prior active-query DP and an entropy-greedy selector; all three get identical 3-bit hypothesis space, 2-query budget, and unseen actual fixture truth. These are **engineered synthetic worlds**, not independently authored benchmark tasks. Strong DP is explicitly allowed to match or win.
- `--external` re-runs the existing CONFLUENCE-003 **16 external-origin Moving AI map scenarios** through the real pinned source+native adapters. It creates a verified evidence adapter receipt **without** claiming that the new VOID inquiry policy competed on these maps. The blocked-cell changes in that benchmark remain explicitly engineered interventions.

## Reproduce

From repo root, Python >=3.10, no paid API:

```sh
python -m unittest discover -s experiments/void001 -p 'test_*.py' -v
python experiments/void001/mesh.py > void001-synthetic-audit.json
```

To include the actual external map replay, first check out all three repos at the *exact* SHAs in `.github/workflows/void-001.yml` (including the original FIELD/PROOF research branches), then:

```sh
python experiments/void001/mesh.py --external > void001-with-external-replay.json
```

CI executes both and uploads evidence JSON. No upstream OSWorld, tau², ALFWorld, WebArena, BEHAVIOR-1K, Traverse, AIDE², or G2 raw datasets are silently downloaded or run. Follow the upstream license, privacy, and task-leakage requirements before a new adapter is admitted.

## Honest target and experiment order

1. Establish the provenance-aware catalog and actual native MOTIF-003 end-to-end synthetic smoke (this PR).
2. Align a new **read-only, source-authorized** adapter to one held-out *independently authored* task dataset, without exposing hidden labels to the model or policy. Candidate starting points are publicly distributable tau² task fixtures or existing Crafter games; OSWorld-V2 is gated and resource-intensive.
3. Compare matched model, token, tool, query, time and action budgets against a competent model agent, its classical verification baseline, and a mesh ablation; define and freeze metric and holdout BEFORE evaluation.
4. Primary: independently verified **useful outcome minus false successes, harmful side effects, query cost and human oversight**. Secondary: information gain, opportunity discovery, source drift recovery and first mistake localization. Count clean-workflow false holds as failures too.
5. Never let source hashes substitute for real provenance/authentication, a simulated permission bit substitute for human consent, or an action request count as observed execution.

The native four-method bridge is inherited from CONFLUENCE-003, not rebased/merged into main. The new smoke adds an executable inquiry-to-outcome seam **but does not yet execute native FIELD-008/006 or COLLECTIVE-001 in its own toy episodes**; only the separately labelled `--external` replay runs all four. That limitation is deliberate and auditable.
