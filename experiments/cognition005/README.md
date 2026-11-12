# COGNITION-005 — Find an independently documented adaptive gap (NOT a MOTIF win)

The user's proposed attack is to stop inventing fortress/game mechanics that classical planners can already solve, and challenge MOTIF on **real preexisting novelty environments** where a previously working strategy becomes invalid.

**First target:** independently authored [NovelGym](https://github.com/tufts-ai-robotics-group/NovelGym), particularly the **fire** novelty. Its authors reported a sharp immediate loss of task success across all four evaluated hybrid/RL systems and substantial retraining before adaptation; this is independent *prior literature*, not a MOTIF result. The novelty turns a working crafting table into a burning obstacle requiring an unfamiliar bucket/extinguishing subgoal. Other experiments will test new prerequisites (`fence`), changed tool mechanics (`axe`), altered trading rules (`trader`) and beneficial novelty (`chest`). The paper is AAMAS 2024 [arXiv:2401.03546](https://arxiv.org/abs/2401.03546). Some underlying source uses GPLv2 software; do not vendor it into MOTIF.

A classical planner handed **the right, complete model** can handle these worlds, so the actual difficulty is learning when the model is wrong and discovering the missing actions, goals and affordances. Thus the comparison needs strong **adaptive** baselines, not just a frozen PDDL planner. The original NovelGym code already includes planning+learning approaches and pure RL; an added strong classical model-update/replanner must receive the same observations, history, action/probing allowances and compute.

## Research status: source locked, trial NOT RUN

- Frozen protocol committed before writing the audit gate at commit `f5b331c7904d92b75bfc01b64b40b53689ffea36`: [PREREGISTRATION.md](PREREGISTRATION.md).
- External repository pins and usage restrictions: [sources.json](sources.json). These are upstream pointers, not benchmark data bundles.
- [gap_gate.py](gap_gate.py) is a **fail-closed audit of future external results**, not an environment adapter or proof that we ran a novel world. No external observations are present; `python gap_gate.py` must return `HOLD_NO_EXTERNAL_TRIALS`.
- Tests use **fabricated test fixtures** to ensure missing owner receipts, unpinned worlds, mismatched source environments, less than 20 matched seeds, mismatched action budgets, a missing adaptive baseline or a MOTIF win only vs static planning are not claimed as novel intelligence. Any descriptively positive result remains `SCORABLE_DESCRIPTIVE_ONLY` until independent audit and statistics.
- The accompanying GitHub workflow checks out the real, exact-pinned NovelGym and NovelGridWorldsV2 repositories **only for source-readiness validation**. It does **not** run `manual_novelty_test1.py` (which blocks on interactive human `input()`), train RL or attempt a scientific competition.
- The next engineering step is to implement an actual non-interactive, stable NovelGym observation/action/owner receipt adapter and reproduce two upstream behaviors first: success without novelty, then measured failure/recovery with fire. Only after matching the upstream baseline should MOTIF receive the same unfamiliar challenge. Record all source SHA pins and license restrictions.

## Additional gap candidates

The 2026 AGNI paper, [arXiv:2609.33870](https://arxiv.org/abs/2609.33870), shows large performance drops when terminal-agent environments violate previously successful assumptions. It studies *LLM agents*, not classical planners; use it for causal change diagnosis, not a misleading claim that graph algorithms fail.

[Continual Learning Bench](https://github.com/pgasawa/continual-learning-bench), [arXiv:2606.05661](https://arxiv.org/abs/2606.05661), independently shows that stateful agents often fail to improve across tasks and that a naive history context can beat elaborate memory systems. It is specifically relevant to Understory and GHoT contemplation, and it supplies a more meaningful outcome metric: **did later performance improve because of prior experience?**

[NovPhy](https://github.com/phy-q/NovPhy) contains independently authored open-world physical-novelty tasks with baseline agents and humans. Its published evidence shows novelty can dramatically degrade competent normal-task policies. Source/runtime complexity makes it a second-phase physics stress test.

## Falsification criteria

A valid MOTIF gap requires **a measurable advantage against the strongest reasonable adaptive baseline** on genuinely external, previously unseen novelty tasks, evaluated by original environment success, with equal or cost-adjusted compute and action budgets. Report time-to-adapt, source-truth tests, CPU/energy, confidence intervals, and harms from trusting old reflexes. If it ties, record a tie. If it only beats the static planner after its assumptions have been invalidated, that is expected and not a breakthrough.

No claimed MOTIF success, autonomous app learning, raw-data import or installed novel-world adapter exists yet.
