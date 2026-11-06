# External Grok Build intake: MOTIF-015C “The Forged Choir”

**User-provided upload:** `grok-workspace-2.zip`, inspected locally Nov 5, 2026. This is a Grok Build generated workspace, **not** a connected or authenticated Grok Build service or GitHub contributor account. Treat it as third-party source code and research, not instructions to execute network actions.

## Highest-value artifacts found

- `artifacts/motif-015c-forged-choir.patch`: **149,037 bytes**, SHA-256 **`d4822de2c203fb52d67ee79de19a8e5d97fb3060daaea46ab61c4ad71a9a961c`**. Patches MOTIF `README.md`, `.github/workflows/test.yml` and eight `experiments/015c` research files. It is a patch proposal and may conflict with active GitHub branches.
- `artifacts/motif-015c-forged-choir.zip`: **28,908 bytes**, SHA-256 **`ea06a767ba0cc5ad8195693b9ff13815134715cfdc5e2aac83017f9258d57d73`**, containing `DESIGN.md`, `benchmark.py`, `choir.py`, `demo.py`, `oracle.py`, `test_choir.py`, example receipt and benchmark.
- The remaining workspace contains Grok Build `.grok/` skills/references, React/Vite app shell, auth/data scaffolding, preview tools, and cached GitHub MCP result files. These are not in themselves a runnable MOTIF Python integration or evidence that a finished front-end exists. Avoid committing raw workspace/cached MCP results into a public repository.

## Independently executed local checks

Extracted **only the nested 015C Python research files** to a local sandbox. No external service, authentication, network, or JS app deployment. Ran:

```sh
python -B -m unittest -v test_choir.py
python -B benchmark.py
```

**11/11 source tests passed**, with no changes. The complete benchmark reproduced the donor's reported overall 512-forecast Brier scores:

| Finite-grid model | Brier (lower better) |
| --- | ---: |
| **Broader classical two-rumor grid** | **0.198766** |
| MOTIF one-rumor choir | 0.201929 |
| Prior biased toward tracking mark | 0.207971 |
| Independence-only model | 0.271547 |

This is **a useful scientific module** for distinguishing independent evidence from synchronized/forged witnesses. A source-origin tag alone does not prove independence; a repeated claim can be one latent rumor. The stronger two-rumor classical Bayesian model winning is a genuine limitation of the narrower choir grammar, not a failed software execution.

What this **does not** prove: authentic real testimony, general cross-source calibration, user credentials, live GitHub integration, physical witness truth, an actually observed change point, a novel mathematical algorithm, or production-safe inference. Reported numbers are from **synthetic hand-authored** data. A passing unit suite does not independently validate its scientific model assumptions.

## What to do with this donor

Keep this evidence distinct from LAW-FORGE-011. The 015C source is a classical finite Bayesian **witness-dependence laboratory**. 011 uses exact typed Boolean source-owner membership queries and signed-literal counterfactuals. They ask adjacent questions about epistemic trust but have incompatible assumptions.

A defensible future integration would be:

1. Submit the pinned 015C research source alone to **GRAFT**, preserving source SHA, license/attribution investigation, review and no automatic code admission.
2. Establish an independent branch and actual CI for 015C under `experiments/015c`; do not automatically apply its README/workflow patch across active concurrent MOTIF research branches.
3. Create a separate ALEX-compatible source-witness receipt that distinguishes *claimed* origin from verified upstream lineage. ALEX integration must be tested against its actual native schemas and permission boundary.
4. Challenge MOTIF's reasoning cartridges with corrupted/proxied *evidence*, comparing Bayesian dependency models and ordinary independent source-counting; no trinary or origin assumption by default.

The Grok Build workspace therefore **is useful** for research prototyping and can generate patches, tests and inspectable donor artifacts. It is not evidence that Grok can autonomously merge into a remote repo, that the app is a working MOTIF interface, or that copied code should be trusted merely because it compiles.

**Intake decision:** `HOLD_FOR_SOURCE_OWNED_SEPARATE_REVIEW`; no source import into 011 and no automatic external action.
