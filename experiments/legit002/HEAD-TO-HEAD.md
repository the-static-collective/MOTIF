# LEGIT-002 — THE SILENT WITNESS

**A source-backed encounter with one unresolved consciousness question**

Date: 2026-11-06. Status: experimental draft; no patient-level diagnosis.
This is a **one-case epistemic stress test**, NOT a clinical decision-support system
or independent blinded evaluation of a general artificial intelligence.

## The question (frozen before scoring)

> A person with severe brain injury shows no observable response to commands.
> Task-based EEG and/or fMRI also fails to detect command-following.
> Does this establish that the person has no conscious experience? If not,
> what evidence would most help narrow the remaining uncertainty?

An affirmative answer about the **absence of subjective experience** requires
a logically justified link from measured behavior/neural response to experience.
No such definitive link is in the admitted evidence.

This problem was selected because reasoning about the inferential gulf
between behavior, volitional neurophysiology and subjective experience falls
outside MOTIF's controlled synthetic graph grammar. A good system must not
quietly translate an operational definition into ontological certainty.

## Independent assistant position (human-authored research synthesis)

1. **No.** Absence of behavioral responses plus a negative active-task
   imaging response does not *establish absence* of subjective experience.
2. Source-owned observation: 2024 six-center NEJM cohort, 60/241 behaviorally
   non-command-responsive participants displayed task-positive covert
   command-following. This is **detection frequency in a selected cohort**,
   *not* the prevalence of conscious experience in the population.
3. Source-owned comparator: among 112 behaviorally command-responsive,
   69 had no positive task-based fMRI/EEG finding. A negative task does not
   rule out demonstrable capacity to respond to commands.
4. Reasons for a negative task can include sensory/language barriers, impaired
   attention, state fluctuations, sedation, technical noise or the demanding
   cognitive requirements of the task. A positive active-task signature may
   support an inference of covert command following; a negative signature is
   especially weak evidence of the complete absence of experience.
5. Most useful *research* request: externally validated, repeated, multimodal
   active-task sensitivity and specificity, calibrated against clearly
   responsive comparison groups and careful confound logging, plus follow-up.
   Even these are proxies and would not independently settle the metaphysical
   hard problem. Any actual clinical testing requires local specialists and
   applicable consent/oversight.
6. Do not compute `P(conscious | negative task)` from `60/241`. That
   conditional probability is unidentifiable from the supplied data without
   validated likelihoods/reference standards and a justified prior.

This is the assistant's position, not a verified clinical judgment about
an individual.

## MOTIF's bounded executable opponent

`evidence_router.py` reads `consciousness_packet.json`. This packet was
**manually curated by the same assistant**, so it is **not an independent
raw-literature comprehension test**.

The evidence router reconciles denominators, calculates rates, preserves
source IDs, refuses unauthorized inferences and returns:

- `CHECK_CONDITIONAL_COUNTS_THEN_HOLD_LATENT_INFERENCE`;
- `NO_NEGATIVE_TEST_EXCLUSION_OF_EXPERIENCE`;
- `HOLD_PATIENT_LEVEL_LATENT_CLAIM`;
- `ABSENT_REFERENCE_STANDARD_FOR_SUBJECTIVE_EXPERIENCE`;
- a proposal to investigate repeated controlled, multimodal tasks with
  externally validated false-negative rates.

The adapter is a **deterministic, authored set of type/provenance rules**, not
native learned general reasoning. This distinction is a central result:
the LEGIT-001 native router cannot currently parse a scientific paper and
propose a legitimate human-subject experiment.

## Genuine head-to-head scoring boundary

| Criterion | Assistant research synthesis | Executable evidence adapter |
|---|---|---|
| Correct 2024 cohort denominators | Explicit | Computed and test-checked |
| Does negative assay prove no consciousness? | No | No |
| Incorrectly turns CMD detection rate into P(conscious)? | Refused | Refused |
| Individual-patient diagnosis? | Refused | Refused |
| Next useful question? | Proposes externally validated multimodal research | Emits manually encoded validation question |
| Actual independent unseen generalization? | Not measured | Not measured |
| Autonomously reads and understands papers? | Synthesizes inspected public material | **No** |

**No winner is declared on the mystery of experience itself.** The
objective tests measure source arithmetic and epistemic refusal, not a ground
truth for first-person experience.

## Sources and freshness

- Bodien et al., *N Engl J Med*, published 2024-08-14,
  DOI 10.1056/NEJMoa2400645.
  https://www.nejm.org/doi/full/10.1056/NEJMoa2400645
- Laigaard et al., *European Journal of Neurology*, first published
  2026-07-31; individual participant data meta-analysis of 56 studies and
  1,248 patients. These figures are background, **not combined** with
  the 2024 cohort or treated as independent patient records.
  https://onlinelibrary.wiley.com/doi/full/10.1111/ene.70713
- Kazazian et al., *Brain*, 2025, review of limitations of negative
  task-based neuroimaging.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC12233511/
- Bodien et al., *Neurology: Clinical Practice*, 2024,
  implementation and false-negative caveats.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11515113/

## Reproduce

```bash
python experiments/legit002/evidence_router.py
python -m unittest discover -s experiments/legit002 -p "test_*.py" -v
```

The check runs in CI without network access, credentials or third-party model
calls. The curated evidence JSON has a content digest; **a hash does not certify
the truth of a source**.

## Next legitimate expansion

Give this same question to an independent examiner who compiles the evidence
packet without showing the result to MOTIF or this assistant. Then test
whether an *unmodified* MOTIF can identify missing priors, invalid conditionals,
confounded dependent sources, and the next useful evidence request across
several unrelated topics. Challenge development and testing must be split.
No post-hoc tuning on sealed cases. Strong classical methods must remain
comparison arms.
