# PROVENANCE-PROBE-001 — When witnesses agree, what has been learned?

**Experimental / synthetic / proposal-only.** Stacked upon the unmerged `DECODER-INTEGRITY-001` → `CONTEXT-GATE-001` → `SELF-MIRROR-001` → `MATHAL-001` → `FIR-001` branches. This is *not* evidence of trustworthy real-world sensors, authenticated identity, general mathematical invention, or autonomous investigative authority.

## Question

The previous decoder monitor noticed when two nominally separate readings disagreed. It could not see a **common-mode inversion**: two corrupted sensors could continue to agree. Can a reasoning cartridge (1) preserve the distinction between copied reports and independent evidence, (2) prove where *two-channel observation alone is non-identifying*, and (3) propose a bounded inquiry that could break that symmetry under clearly stated assumptions?

## Executable construction

- **Declared witness ancestry:** `SourceClaim` explicitly labels the *asserted* upstream root. Forwarded copies of a source are deduplicated; internally contradictory roots are flagged. Distinct root strings are **not authentication or evidence of independence**. Spoofed root labels demonstrate this gap.
- **Four fixed competing polarity models:** clean, inverted primary, inverted audit, inverted both. The toy simulator supplies balanced latent truth and **fixed known** nominal accuracy (`primary=0.85`, `audit=0.90`), with independent sampling conditional on the hidden truth. That assumption is deliberately fragile.
- **A strict identifiability witness:** without a truth anchor, clean and both-inverted have *exactly equal* pair-reading likelihood for **every** `(primary,audit)` outcome; primary-inverted and audit-inverted likewise. More of the *same observation type* cannot distinguish these pairs. The experiment does not claim to infer real provenance from labels.
- **A controlled anchor:** a synthetic fixture can provide the actual hidden truth after the event. This is **not a real verification service**; attestation is an explicit experimental assumption. The hostile tampered-anchor test proves that an incorrect reference can cause confident **wrong** identification.
- **Existing-module connection:** `ingest_decoder_witness_pairs` consumes actual `DECODER-INTEGRITY-001` `WitnessPair` records without reading their generating `Episode`, reward or hidden regime; missing audits are held with an explicit receipt and cannot be interpreted as agreement.
- **Inquiry selection:** exact expected information gain over the four-model posterior compares `AUDIT_PAIR` (cost 1) and `VERIFY_ANCHOR` (cost 3). A query is proposed only if permitted, affordable, and informative. No query is dispatched to real tools, sensors or humans; its output remains `I_SYNTHETIC_INQUIRY_PROPOSAL`.
- **FIR contract:** the candidate explanation stays **Idea (I)**, including after a high posterior. Only the exact count of synthetic fixture-attested anchors is recorded as a finite `F_LOCAL` fact with a source receipt. Neither a claim of mechanism nor of source authenticity is promoted.

### Reproduce

```bash
cd experiments/provenanceprobe001
python -m unittest -v test_provenanceprobe.py
python provenanceprobe.py
python benchmark.py
```

Python 3.10+ standard library only, with sibling `fir001` and `mathal001` code on the stacked branch.

### Results (deterministic toy fixtures)

- 160 ordinary paired observations leave **two** unresolved polarity explanations at posterior **0.5 / 0.5** for each matched pair. This is an exact model symmetry, not mere insufficient sample size.
- An anchor-based inquiry is selected from the ambiguous posterior; its calculated expected information is **0.681332 bits** at cost 3. A new unanchored pair has essentially zero expected information within that posterior symmetry.
- Equal inquiry-cost benchmark, **200 independently seeded model-matched trials** (50 per generating hypothesis): after 100 paired observations, **two** trusted synthetic truth anchors (total cost 6) yield **194/200 = 97%** correct model rankings, versus **100/200 = 50%** with six more ordinary paired observations (same declared cost 6). This comparison is favorable by construction because the anchor can break the symmetry, the model family contains the truth, and the accuracies are known; it is **not** an external generalization claim.
- Three forwarded `blue` reports from one asserted root outvote one `amber` in raw-majority counting, but collapse to **1 versus 1** after ancestry grouping. False distinct-root assertions defeat this grouping.
- **Compromised reference negative control:** swapping all anchor truths reverses the model identification while appearing highly confident. An anchor is a modeled trust dependency, not automatic authority.

### Failure boundaries / next frontier

1. Different asserted provenance strings are not authenticated. A malicious witness can fabricate new roots.
2. A shared latent confounder, drift, continuous accuracy uncertainty, skewed truth prevalence, or unreliable anchor can falsify the fixed likelihoods.
3. Exact posterior probabilities in a deliberately four-model world are not independently calibrated uncertainty about the real world.
4. Queries are hypothetical, read-only. No access to devices, human witnesses, external apps, or user permissions is implied.
5. This is classical finite Bayesian experimental design and de-duplication, not historically new mathematics or general self-improvement.

## Source ancestry

User-owned Google Drive: *nuMATHELOLOGY*, 2nd ed., and *nunuMATH: First Course in FIR Systems* (FIR role and receipt discipline, decoder dependence, hostile controls); MOTIF 010 Scientist (synthetic informational questions), 014W Witness of Witnesses (fallible adjudicators), and 2026-11-07 stacked mathematical cartridge sequence. The user owns the conceptual direction; this file is a reproducible implementation proposal, not a replacement for those sources.
