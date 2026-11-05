# MOTIF-Q-001 — THE FIRST QUESTION × DOGRAM

**Status: bounded synthetic active-query experiment, proposed branch.**

MOTIF-001 through 005 learned toy graph transformations, compared toy
affordances, retained non-effects, and derived one anonymous composite graph
condition. This experiment is deliberately smaller than a general learning
architecture: **when several declared explanations remain plausible, can an
agent select an affordable permitted trial that resolves a target-relevant
disagreement?**

## The finite specimen

The toy learner sees two synthetic observations:

- part present + badge present: effect
- neither present: no effect

Four candidate rules remain: part required, badge required, both required,
either sufficient. The simulator alone knows which rule governs its world.

The learner wants to predict whether a *different fictional actor* can succeed
with a part but no badge. It may try synthetic surrogate actions, each assigned
a declared cost and synthetic admission flag. It cannot attempt the target,
read the simulator's hidden rule, or treat a refused trial as evidence of failure.

Selection chooses the affordable permitted question maximizing the number of
hypothesis states that would be left in a target-pure outcome group **per unit
cost**. That score is a count under a declared finite hypothesis family, *not*
a calibrated probability or proof of causal relevance.

The predeclared baseline spends the same one-unit budget on a redundant
repeat of the positive observation. Both strategies run on the same four
hidden synthetic rules. Report *coverage* and *correct among answered*
separately; an abstaining baseline has no measured answer accuracy.

## Dogram seam

The optional `dogram_bridge.py` accepts a **trusted local checkout of
Dogram** and calls its existing `probe_cost_pareto.analyze_probe_costs` kernel.
It computes finite separating-probe and information/cost Pareto receipts
for every hypothesis pair that disagrees about the declared target, using
`probe_cost_pareto`. A second native calculation, `anti_collapse_reachability`,
counts which distinctions between candidate mechanisms are lost when MOTIF
retains only its selected probe. This deliberately allows the important
case: **the target is predictable although the underlying mechanism remains
ambiguous**. The lost distinctions are preserved, not declared irrelevant.

The pinned Dogram checkout used by this branch's CI is commit
`551b5f9df18f17ec69b452ddcdff01718e0ff771`.

**Dogram does not choose the next query.** It calculates finite partitions and
declared costs. MOTIF owns the toy question policy; ALEX would independently
challenge evidence; 3rdi would bound observer access; MEMENTO would own
durable admitted histories; Free Graph would hold traversable provenance.
Those other systems are **not invoked** by this experiment.

The export is a `motif.dogram-probe-family/v0` input adapter, not an official
Dogram specimen or receipt. The native calculation is only performed when the
operator explicitly provides `--dogram-root`. It does not clone or install
anything. A native calculation receipt must not be called a new world fact.

## Reproduce

```sh
cd research/first-question
python question.py
python -m unittest -v test_question.py

# Optional: only with a local trusted Dogram checkout, not required for MOTIF CI
python dogram_bridge.py --dogram-root /path/to/Dogram
```

Python 3.10+ standard library, no credentials or online dependencies.

## What earns the next milestone

- Test procedurally varied ambiguous mechanisms; avoid rewarding questions
  whose features literally encode the final target.
- Introduce delayed/noisy observations, costs, and explicit `HOLD` receipts.
- Compare equal-budget finite decision trees, random and fixed policies,
  not just the intentionally weak redundant-query baseline.
- Evaluate transfer under held-out structures and actor-specific mechanisms.
- Check that private ground truth is unavailable in the selector's interface.
- Where representation cannot distinguish target states, test a bounded
  representation refinement against simpler engineered-feature baselines.
- Keep separate cost, information, option growth, permission and desirability.

## Explicit falsifier

If a simpler finite hypothesis-elimination policy gives the same target
prediction quality and query cost, MOTIF has **not** demonstrated a novel
intelligence architecture. Better record keeping or a Dogram receipt can still
be a legitimate engineering benefit.

**Synthetic part/badge rule != physical reality.
Dogram calculation != evidentiary validation.
Observer-visible possibility != admissible action.
An informative question != permission to execute it.**
