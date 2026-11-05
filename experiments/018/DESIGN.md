# MOTIF-018 — THE WITNESS OF THE WITNESS

> A system that questions its own methods must also question the evidence **about** those methods.

**Status:** executable, source-pinned, synthetic finite research. This does not authenticate real sources, discover genuine ground truth, launch OpenManus/ELF, or edit any external or production system.

## Architecture and upstream boundaries

MOTIF-018 stacks on the **MOTIF-017 question-before-question draft PR #22** (itself stacked on MOTIF-016 PR #19, MOTIF-015 PR #18, and MOTIF-014 PR #16). No branch is implicitly merged and no upstream source authority is inherited.

MOTIF-018 calls MOTIF-017's actual question desk, which invokes the original byte-pinned **National Treasure Question Box** and **native Dogram finite partition-refinement** source in MOTIF-014. Missing primary evidence causes a genuine National Treasure source-object HOLD *before* Dogram runs. The new experiment does not impersonate these source-owned modules.

## Two problems that a naïve self-corrector confuses

1. **World shift.** The distribution of things being witnessed changes. A stable source may legitimately report something different.
2. **Witness drift.** The conditional accuracy of a reporter relative to an independently supplied reference changes. The world may remain unchanged, or both may change.

Raw report frequency is insufficient to distinguish them. The experiment separately measures:
- correctness of a reporter against a synthetic reference,
- distribution of independently referenced synthetic labels,
- raw reports, the intentionally weaker control.

Each synthetic source has a fixed upstream origin. Forwarded copies never count as additional independent witnesses.

## Synthetic reference of the reference

Every synthetic record contains **two distinct declared reference families** that must agree. Missing, contradictory, same-origin, or malformed references cause HOLD. This is a procedural consistency check, **not proof of independent origin or objective truth**. Both reference feeds originate in one toy simulator. A pair of colluding, jointly corrupted reference feeds can agree while being wrong; this is a required falsifying case.

**The failure is preserved:** under the reference-collusion regime, the old reporter's true accuracy remains unchanged, but both false references agree. MOTIF-018 can then incorrectly attribute the discrepancy to the reporter. It cannot solve source-of-source trust by decree.

## Fixed quantitative protocol

- Two reporter origins: north and south.
- Fixed old calibration cohort: **480 observations per origin**.
- Two preregistered independent later cohorts: **early 80**, **late 320** per origin.
- Overall family-wise false-alarm budget: **0.05**, conservatively corrected for **eight predeclared contrasts** (two reporter origins × two checkpoints × two metrics).
- Two-sample bounded Hoeffding threshold for each comparison:
  
      sqrt( (1/2)*(1/n_old + 1/n_recent) * log(2*8 / 0.05) )

  The guarantee is *conditional* on the explicit within-era independent bounded sampling model. It does not guarantee discrimination under adversarial common-mode reference corruption or nonstationarity within the fixed cohorts.

- Results are **evidence flags**, not authenticated causal conclusions or automated permission to revise methods.
- No detection is labeled **NO_CHANGE_DETECTED_NOT_PROOF_OF_STABILITY**. Small changes can remain indistinguishable with finite samples.

## Source-audit question portfolio

A bounded research planner proposes zero, one or two **synthetic** independent-origin audits using declared impact/cost. These are inert question proposals; neither audit is performed in reality. The ranking is a **declared impact-per-cost heuristic**, not an optimal Bayesian value-of-information algorithm. MOTIF-017 already contains the stronger exact conventional Bayesian information-acquisition benchmark; MOTIF-018 does not claim to beat it.

## Adversarial / disambiguation cases

- Stable reporter and stable world: no change detected, but never proven reliable.
- World prevalence changes with stable reporter accuracy: world-regime evidence without reporter-accuracy flags; raw report-rate heuristics often misattribute this.
- Reporter inversion under stable world: reporter-accuracy flags.
- Both change simultaneously: preserve both hypotheses.
- Subtle deterioration: limited power, remain uncertain.
- Forwarded duplicate origin: deduplicate; contradictory same-origin copies: HOLD.
- Missing / disagreeing source-independent claims: HOLD.
- **Two correlated false adjudicators**: confidently misleading references can produce a false reporter-drift signal. This is an important *negative* result.
- Out-of-scope evidence, missing audit, altered checksum or attempt to infer hidden simulator truth: refuse.
- Multiple predetermined seeds: count change detections under each named synthetic regime, without advertising sensitivity outside those families.

## Reproduction

Node 20+, Python 3.10+; no dependencies or network calls:

    node --test experiments/018/test_witness_machine.mjs
    node experiments/018/witness_machine.mjs > motif018-research.json

The CI workflow re-runs 014–017 and uploads the full machine-readable 018 research receipt. The PR remains draft and unmerged, awaiting explicit review of assumptions and limits.

**A witness to a witness is not automatically an independent witness. Agreement != authentication. No detectable change != known stability. An observed mismatch != permission to rewrite the reasoning system.**
