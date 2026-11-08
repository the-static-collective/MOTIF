# MOTIF — ADAPTER-INVENTION-001: Discover the missing crossing

**Status:** bounded, supervised program-synthesis research on synthetic data; real MOTIF source modules called; code generated and exercised in a subprocess. **Not** general algorithm invention, unsupervised semantic understanding, a security sandbox, or autonomous deployment.

## User's frontier question

> What is the smallest missing transformation that would allow two existing cartridges with incompatible ports to communicate? Can MOTIF propose one, construct it, test counterexamples, and decide whether to retain it?

This first executable answer deliberately chooses a small, falsifiable instance. `MOTIF-003.analyze_first_moves` returns action **dictionaries**, while the actual `SELF-MIRROR-001 Policy.choose` expects immutable `Move` objects. The existing repository already contains a manually implemented bridge in `selfmirror.preview_motif003`. **We do not claim to invent a previously unknown conversion.** Instead we test whether a generic constrained synthesizer can infer an equivalent *standalone* typed adapter from examples and execute it against real upstream/downstream modules.

## How the prototype works

1. Inspect `Move`'s actual runtime dataclass fields, test a direct call with a MOTIF-003-shaped row, and record the incompatible ports.
2. Enumerate a **finite, known expression grammar**: field projection, tuple length, an operator/roles name join, and a deliberately tempting `false` constant.
3. Learn **five target-field transformations** from 64 author-supplied synthetic labeled examples (`train`), disambiguating with 64 separate examples (`validation`). A mapping must be **unique** across training and validation or the synthesizer abstains. No holdout is passed to this function.
4. Freeze the proposed mapping and test on independently generated `test` and `ood` examples. The labels themselves are supervision and **do not prove that inferred semantics transfer to unobserved data**.
5. Emit a fixed-template Python child containing the inferred expression specification. Pin the actual `selfmirror.py`, own `adapterinvention.py`, and emitted child bytes. Execute an **actual `SELF-MIRROR-001 Policy`** in a separate interpreter. The child does not accept arbitrary code, file paths as expressions, network calls, or side-effectful actions.
6. Compare the resulting policy choices against the **existing handwritten** `preview_motif003` control. In the full GitHub checkout, also execute **actual `MOTIF-003.analyze_first_moves`** and verify the generated adapter's choices against that control.

The generated source is a *fixed interpreter of a learned expression spec*. This is not independent invention of Python syntax or unseen operators. A subprocess provides interpreter separation, **not a security boundary against malicious trusted-repository Python code**. SHA-256 checks detect source changes, not authorship.

## Reproduce

From the full stacked MOTIF checkout:

```bash
cd experiments/adapterinvention001
python -m unittest -v test_adapterinvention.py
python adapterinvention.py
python benchmark.py
```

Standard-library Python 3.10+. Depends on `experiments/selfmirror001` and its stacked FIR/mathal modules. The full-checkout integration check uses `experiments/003/affordance.py` and the actual `assemblylab001` simulation fixture. The additional conditional-policy control uses `contextgate001.Gate`.

## Observed frozen synthetic results

- **22** candidate expressions inspected across five output slots.
- **200/200** fresh contract examples reproduced exactly (fixture-authored labels).
- **50/50** downstream `SELF-MIRROR` policy choices matched the existing manually implemented adapter.
- **200/200** renamed/missing-field specimens held instead of inventing a value.
- A deliberately hostile *semantic shift* (swapping two integer fields without changing types) matched old labels in **10/181** cases. The adapter **did not detect that shift** from shape checks alone.
- The original direct dictionaries-to-`Move` call has an incompatible port type. A fixed no-bridge baseline cannot execute the downstream policy.

Those are generated test-fixture counts and prove neither novel mathematics nor superior ML accuracy. The strong manual bridge is on par with the generated bridge. The new contribution is **executable supervised bridge search and refusal on ambiguity**, not improved decision quality.

## Adversarial controls

Tests cover contradictory supervision, insufficient examples, duplicate/leaked split identifiers, ambiguous `false` constants, target identity collisions, truncated upstream searches, malformed rows, injected expression names, hidden target-label changes, missing fields, emitted-child tampering, source drift, independent subprocess execution, real downstream invocation, context-gate consumption, and end-to-end integration with actual MOTIF-003 when checked out.

`HOLD_UNPROVEN_GENERALITY` is intentional: passing exact finite fixtures does not establish that an adapter is semantically reliable or independently authorized for other domains. The system never modifies a running agent, merges a PR, fetches arbitrary code, or executes real-world actions.

## Next genuine frontier

Reduce dependence on the manually supplied target labels by inferring and *testing* behavioral contracts from source, then try a truly absent cross-cartridge bridge against a classical code-synthesis baseline. A meaningful improvement would require unseen families of transformations and semantic-shift detection—not merely matching an existing adapter's decisions.

**Stack:** Draft branch atop `SELF-ASSEMBLY-001`, which itself sits atop previous unmerged NEXT-STEP / self-build / witness / mathematical experiments.
