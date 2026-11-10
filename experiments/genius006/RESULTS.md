# GENIUS-006 — First measured research results / full classical control

**Research status: HOLD.** All task worlds, utility points, question grammar and evaluation procedures are engineer-authored. This experiment demonstrates executable **conditional inquiry over a finite known model**, not independent new mathematics or real-world collective intelligence.

## Original prospectively frozen benchmark

The first run of the six-family test (before addition of the post-hoc research promotion gate) passed **15 adversarial tests** in GitHub Actions run **#42855030698**. The validation-only policy choice and study protocol were frozen with SHA-256:

**126498d46a2c3972a82e78dfdda68c449fc90284adaccc74697a2c190e741126**

Every family was evaluated against identical secret future target worlds selected from three heldout synthetic seeds (60631/60632/60633), for 96 cases per family, 3 query opportunities except 4 for DEEP_CHAIN.

**Mean independently checked downstream capability value (higher is better):**

| Task family | Entropy | Diversity | Immediate gain | Affordance 2-step | Classical exact Bellman | Validation selected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CHAIN | 0.0000 | 0.0000 | 1.6146 | **1.7396** | **1.7396** | Affordance 2-step |
| DEEP_CHAIN | 0.0000 | 0.0000 | 0.0000 | 0.0000 | **2.0000** | Entropy (zero-value tie) |
| MIXED | 0.8438 | 0.8438 | 1.8854 | **2.6875** | **2.6875** | Affordance 2-step |
| NOISE_USEFUL | **4.1667** | **4.1667** | **4.1667** | **4.1667** | **4.1667** | Entropy |
| PARALLEL | 1.4063 | 1.4063 | **4.4167** | **4.4167** | **4.4167** | Immediate gain |
| SPARSE | 0.0000 | 0.0000 | 0.5729 | **1.0833** | **1.0833** | Affordance 2-step |

All methods reported **zero false capability certificates** because the independently implemented direct-world prerequisite verifier checks each certified result and fails the run on invalidity. No real action was executed.

### Exact finite expected value under the published uniform prior

The Bellman planner independently calculated the complete expected values over all 256 possible hidden targets: CHAIN 2.5; DEEP_CHAIN 2.0; MIXED 2.375; NOISE_USEFUL 4.0; PARALLEL 4.875; SPARSE 1.5. These are theoretical expected values **for this model only**, not measured general-world accuracy. The sampled 96-case means can be above or below the full uniform-prior expectation.

An adversarial test also enumerates every one of the 256 possible CHAIN worlds and confirms that a realized exact-policy mean equals the Bellman dynamic-programming value. The public hypothesis grammar is assumed correct, and the secret actual world is not disclosed until a specific question is chosen.

## What the evidence supports

1. **Information gain is not automatically useful.** CHAIN and SPARSE have 4-way high-entropy distractions that consume question budgets. The selected bounded affordance policy obtains nonzero conditional capability value while pure entropy obtains zero.
2. **Entropy is not inherently defective.** Under NOISE_USEFUL those high-information measurements are relevant, and all methods agree. Changing the actual goal changes which research question is valuable.
3. **A shallow successor planner does not generalize.** DEEP_CHAIN is a decisive counterexample: value appears only after four prerequisite questions, all four limited methods get 0, while the full classical Bellman method gets 2.0 (a 32-point capability whenever the four Boolean requirements are true: 1/16 under the declared prior).
4. **This is not victory over classical planning.** The full-horizon Bellman method is the strongest applicable conventional oracle and never loses in population expectation. It requires more search effort; runtime budgets have not yet been matched. The finite expected value and these samples do not establish autonomous invention or mathematically novel capabilities.

## Post-hoc policy safety response

After discovering the DEEP_CHAIN failure, a **validation-only classical adoption gate** was implemented. It checks whether a limited candidate's mean verified value lies within 0.05 points of the exact Bellman result on the preselected validation cases. If not, it returns:

**HOLD_NO_PROMOTION_FALLBACK_CLASSICAL**

and recommends exact Bellman instead of silently promoting the underperforming short-horizon planner.

This safeguard was added **after inspecting the original future outcomes**. Even though its calculation uses validation-only observations, it is *post-hoc research repair*, not independently preregistered evidence of superior generalization. The unchanged original results remain above; no benchmark failure is erased.

The guarded action is a **nonexecuting research recommendation**, not a Trench deployment or automatic permission to act. The experimental method remains inspectable alongside the comparator it failed to beat.

## Next independently meaningful test

Unseen external task authorship, operator/question invention under a typed hypothesis language, imperfect/contested model sets, honest abstention when assumptions break, evidence transport receipts, and matched compute cost versus high-quality classical search. Until these are demonstrated, the claimed result is a **finite model-based proof of concept with a documented generalization failure**.
