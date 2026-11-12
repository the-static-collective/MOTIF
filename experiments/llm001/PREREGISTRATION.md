# LLM-001 / Convergence Gate — frozen test plan (before implementation)

Date: 2026-11-12. Branch parent: COGNITION-010 draft, itself a stacked/unmerged research lineage.

## Research question
Can an LLM become a low-authority *hypothesis/code-proposal engine* inside MOTIF, while an independent typed state graph chooses evidence, verifies the proposed move, and limits the prompt to high-decision-value material? Is useful progress per context byte or model call improved over flat context and a strong non-LLM graph-search baseline?

## Actual scope of this first test
A **dependency-free, offline JS contract experiment**, not an LLM benchmark. Three invented domains: FIELD-014-like unmeasured physical layout, COGNITION-010-like blocked action, and a consent-gated community exchange. One external branch is observed only by a pinned contract description, NOT merged. This first step tests safe state transitions, source-root deduplication, hypothesis rejection, branching, cache-key stability, exact action receipts, and model-interface payload shape.

## Frozen comparison and success criteria
- Arm A: myopic highest immediate value (greedy).
- Arm B: finite exact exhaustive reachability over the same exposed graph and action budget (strong classical baseline).
- Arm C: MOTIF-style affordance-gain ranking (JS adapter), with LLM **not yet called**. This adapter does not execute native MOTIF-003.
- Report all ties and classical wins. Compare reachable goals, valid action recommendations, amount of evidence presented, rejected unsafe proposals, and retries; not imagined IQ.
- Hard assertions: a model cannot manufacture a graph fact, use duplicate source roots as independent witnesses, bypass a HOLD/consent gate, claim physical containment from diagram dimensions, or effect a side change. Every proposal is PENCIL until a deterministic simulation receipt.
- At least 3 source-bound fixtures, at least 12 boundary tests. Failure cases remain in results.

## Live LLM phase (not part of offline proof)
Use locally provisioned open weights or an explicitly approved paid endpoint, with the same model/seed/temperature, same facts and budgets across (i) flat RAG, (ii) full graph-scaffold, (iii) branch compiler. Score task success verified by **separate owner**, unsupported claims, tokens, wall-clock, user corrections, and total cost. Include withheld independent tasks; do not use the fixture author's correct actions as unseen validation. Strong graph BFS and programmatic methods are obligatory controls.

## Novelty status
Speculative reasoning, graph-grounded RAG, proof checking, context selection and agent memory all have substantial prior art. This experiment tests a particular combination: *counterfactual action-affordance value as the selection signal for LLM input, with immutable world forks and source-bound verification receipts*. No algorithmic breakthrough or superiority is claimed in advance.

## Source boundary
Do not merge draft cognition and field branches. FIELD-014 (PR #310) source at 5f1f0ddca303616a4fd1805522c58a45baff934e is a separate diagram-only owner; COGNITION-010 PR #308 at 143ad57170091487433307ec9ad5208376dda76e supplies the selected base. Model-provider keys, personal photos, private MEMENTO and field coordinates must never enter this repository.
