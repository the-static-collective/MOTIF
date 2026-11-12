# LLM-002 — Graph-conditioned forked inference (PREREGISTRATION)

2026-11-12, frozen before implementation. Parent: unmerged LLM-001 draft #311. No merge of FIELD-014 or private MEMENTO.

## Paired hypotheses
**H1 hidden-state graph conditioning:** source-scoped graph features, inserted as a bounded low-rank additive change to the *post-prefix* hidden state of a small causal attention model, can influence branch predictions without rewriting the common token prefix. Train only the adapter on explicitly synthetic examples while the attention backbone is frozen. Compare on a held-out enumerated synthetic split to (a) no graph features, (b) shuffled/wrong graph, and (c) an exact classical admissibility rule.

**H2 shared-prefix multi-fork inference:** fork-specific graph conditioning can reuse the exact numeric KV cache of a frozen shared prefix *without changing outputs relative to a fully recomputed conditioned forward pass*. Compare prefix recomputation counts and maximum absolute logit delta under deterministic, matched computation.

**Interaction:** a graph-conditioned control applied to the *prefix*, a changed attention model, changed tokenizer/template, adapter version, different source authority, or a different privacy tenant MUST invalidate cache reuse. An adapter applied after the prefix should not affect cached prefix K/V. Source-lineage forks never reconcile predicted facts back into observed history.

## Frozen tests / falsifiers
- Implement actual floating-point causal masked dot-product attention, not a fake cache counter.
- >= 3 heterogeneous invented branch scenarios and >= 3 forks from one common prefix.
- Assert full vs cached branch logits agree (numeric tolerance) for *all* forks, with no hidden parameter/position changes.
- Assert off-by-one position, mutated K/V, cache aliasing, cross-tenant scope, changed model/adapter graph-control-in-prefix, stale-token prefix and cache metadata mismatches fail closed.
- Train bounded rank-2 graph adapter on fixture train split, report held-out classification against identical frozen backbone with disabled adapter, and exact authored classical truth. Neither held-out split nor author-designed task constitutes an external benchmark.
- A model cannot emit authorized actions or self-verify; all outputs PENCIL.
- Measure operation-count savings as precise number of QK dot products, not wall-clock or monetary savings. At 1 token input, branches may cost more than recomputation; preserve negative results.
- Explicitly report static shared prefix vs branch-specific graph input. Do not claim that incompatible graph-conditioned prefix activations share KV states.
- No model download, no real pretrained weights, no real-world actions, no private images or source data in public CI.

## Model phase beyond toy
Optional real local pretrained model (Torch/Transformers or vLLM) requires pinned model/tokenizer, template, adapter state, model provider and owner consent, same-prefix proof, attention mask/position verification, per-tenant scoped cache ownership and measured latency. One eval must use truly independently authored tasks and strong graph/planning baseline. Compare number of genuinely verified useful actions, not merely more branches or hallucinated insight.

## Security and literature
vLLM automatic prefix caching explains prompt-prefill reuse and its inability to accelerate decoding; vLLM security guidance warns that cache salt is not tenant isolation. Transformers KV docs show prefilled-cache reuse. Low-rank adaptation and activation steering are known technologies; any novel claim depends on independent controlled evidence, not the presence of a new name.
