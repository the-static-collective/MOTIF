# BRANCH SANDBOX 001 — run unmerged research without merging it

## The distinction

Main does not have to contain every experimental implementation. It needs a stable index, a safe source reader, an explicit contract for each approved candidate runtime and a way to carry the result back as evidence.

The source registry is dynamic; runtime permission is deliberately not.

1. Every visible remote head is discoverable as a pinned source pointer: python -m motif.cli branches --all.
2. Every permitted UTF-8 source file is readable by exact observed commit with: python -m motif.branch_source --ref BRANCH --list or --path PATH --show. No code is run.
3. A reviewed runtime profile can execute original tests from a pinned unmerged commit in a fresh, ephemeral Docker sandbox. This is not unrestricted code execution and cannot merge.
4. Results stay HELD until independently compared against a strong baseline, checked for regressions and reviewed by the adopting project's owner.

## Actual unmerged reciprocal 004 profile

A concrete profile exists for the RECIPROCAL-004 branch. It executes the original 002/003 native Node test suites, not a rewritten mock. CI confirms the actual source commit used and produces an evidence artifact.

Preview only:

    python -m motif.branch_runner \
      --ref experiment/reciprocal-004-ecosystem-crosswire-20261112 \
      --profile reciprocal-004-smoke

Explicitly execute in Docker:

    python -m motif.branch_runner \
      --ref experiment/reciprocal-004-ecosystem-crosswire-20261112 \
      --profile reciprocal-004-smoke --execute

Requirements: local MOTIF Git checkout, live Git origin, Python 3.11+, Docker, ability to obtain the pinned Node image. Execution is not attempted without --execute. No generated code, human testimony, private key, live model, or third-party action is needed.

The sandbox mounts ONLY the selected source files, read-only, at /work. It disables container networking; runs non-root; drops Linux capabilities; activates no-new-privileges, a read-only root filesystem, a small private tmpfs, CPU/RAM/PID limits and a timeout. Test logs and success/failure are recorded. Docker is not a perfect security boundary; more privileged or third-party supplied candidates need stronger isolation and independent review.

## Main composition gate

MOTIF's merge_verdict evaluates provenance, independent tests, comparison against strong controls, regressions, measured transfer and local owner approval. It may recommend a merge review or keeping a branch unmerged. It never writes a Git ref, invokes GitHub merge, or silently promotes an observed branch's claim.

Branch discovery is not merge selection. Native tests passing is not correctness on new tasks. A branch can remain an active *experimental organ* while its results inform the main reasoning spine. Its source identity must remain visible.

## What is and is not connected

Working: live remote enumeration, original source inspection, reviewed source-only planning, branch-specific no-network execution of original tests, and a stable conservative decision protocol with classical controls.

Not yet working: a generally trusted arbitrary-method executor, automated PR composition, a JAR;VIS live reasoning UI, cross-repo personal memory sharing, real LLM hybrid test, independent human learning outcomes or autonomous merge.

Source code for other organs belongs to those projects; schema compatibility alone does not transfer their authority.
