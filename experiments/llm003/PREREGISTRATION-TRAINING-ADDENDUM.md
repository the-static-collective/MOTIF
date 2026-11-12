# LLM-003B ADDENDUM (EXPLORATORY): Train a graph-suffix adapter on a pretrained LLM using verified vs erroneous examples
Added AFTER the first LLM-003 pretrained KV result and author-synthetic error-dividend result were inspected. This protocol is a post-hoc follow-up, not the original preregistered experiment.

Question: Does *verified negative feedback* improve a tiny trainable rank-2 graph-control adapter on a frozen, actual pretrained 135M-parameter language model? Distinguish this from merely increasing the amount of compute.

Fixed scope: exactly HuggingFaceTB/SmolLM2-135M-Instruct at ee72e5415c002e8fc0566a191a07c0b2b708875a, frozen model parameters, CPU float32. Only low-rank U[hidden,2], V[2,6] are updated. Input graph features are the authored tool/permission/action indicators; labels are the already-registered fictional truth rule from LLM-002. No natural-world permission or independent benchmark is implied.

Three equal-step arms: (1) verified labels, including true negative/counterexample cases; (2) positive-only labels sampled with replacement for the same number of steps; (3) deliberately corrupted negative labels at a fixed 50% error rate, but the same sampled graph inputs as (1). All trained with the same optimizer, 48 updates, same initialization and learning rate. Baselines: frozen pretrained model without adapter, shuffled graph features at evaluation, and exact authored classical rule. Unseen evaluation prefix phrasings with all 12 binary-action cases; every arm uses identical test inputs.

Frozen primary metrics: overall heldout accuracy (48), negative-class recall and positive-class recall; cross-entropy and label regression. Report adaptation time and upper bound on injected vector norm. Report train and evaluation separately. A positive-only baseline can lose simply because it has no negative labels: this is ordinary supervised-learning behavior, not novel intelligence. False negative labels may harm.

Guardrails: No model-generated answer may authorize user-facing actions; all logits remain PENCIL. No private prompts, user data or state changes. If learning fails or a baseline wins, preserve results. Prior art includes contrastive examples, DPO, negative training and low-rank adaptation.
