# VOID-005 — The Learning Adversary

**DRAFT / RESEARCH HOLD**, stacked on VOID-004 (#291). This experiment asks whether reusable memories stay useful when a source-owned fortress *changes two attack directions in response to accumulated successful defenses*, and occasionally presents a validly sealed but false relay report.

The 24-wave fortress, maze, four reachable relay outposts, one shared information charge, and 14-attempt cap are inherited from VOID-004. No policy may inspect its seed-specific attack schedule; an epoch counter indicates a change but not where. Defense failures and correctly timed sonar checks disclose true source-owned outcomes, distinct from unverifiable relay claims. All research is deterministic and synthetic: **the enemy is scripted, not an independently trained or online-learning opponent**.

## Actual comparison

`motif_native` runs original canonical MOTIF-003 affordance discovery with a bounded novelty dividend layered over conventional predicted progress. `classical_voi` is the main competent, iteration-aware comparator, with the same observations, recency/confidence assumptions and future-utility model. `classical_stale` is a deliberately overconfident memory-ablation control, not evidence against good classical planning.

All controllers maintain historical receipts and can revise tentative claims after verified contradiction. A source hash only establishes the integrity of the author's own record, not the truth of a compromised relay's claim. The experiment uses zero model calls or real-world actions.

## Reproduce

Python 3.11+, stdlib, on the stacked branch:

```sh
python -m unittest discover -s experiments/void005 -p 'test_*.py' -v
python experiments/void005/adversary.py --split development --full-receipts > void005-development.json
python experiments/void005/adversary.py --split heldout --full-receipts > void005-heldout.json
```

The workflow checks the **frozen preregistration file against its historical Git commit**, tests the native source integration, scores separately on 4 prior-seen development and 16 fresh heldout seeds, verifies the receipts and uploads full evidence. Do not report wins based only on a queued run. Primary outcome is paired **restricted first-clear attempt (15 if unfinished)**, separately by regime. All ties and losses are outcomes, not exceptions.

## Limits

This is a bounded adversarial *fixture*, not an external game environment or a demonstration of autonomous adaptive AI. Source events are programmer-defined, relay deceit is injected by the authored owner, and classical VOI is not globally optimal dynamic programming or compute-matched. No human survival, agent deployment, API access, credential use, or evidence of recursive self-improvement is implied.