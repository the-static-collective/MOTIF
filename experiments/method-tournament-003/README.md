# MOTIF TOURNAMENT-003 — Source-owned method transfer without merging

**Status:** research stacked after Source Council 002. This tests whether an ORIGINAL unmerged experimental method generalizes to different future scenarios, rather than merely passing its own native test suite.

## Original donor and authority

The sole reviewed donor is original RECIPROCAL-003 reason_loop.js and its original RECIPROCAL-002 dependency, fetched from the remote experimental branch experiment/reciprocal-004-ecosystem-crosswire-20261112 at a live observed source SHA. Its original native tests are executed without copying its code into main. Unknown profiles or irrelevant queries HOLD; a branch label cannot authorize executing unreviewed code.

The Source Council's original lexical document-coverage method reads exact original README and PREREGISTRATION files from the immutable donor commit. The source inspection is not validation that the method works.

## Six separate synthetic future regimes

The fixture and evaluator belong to this comparison experiment, not the donor, and are hashed:

1. Stable role signal: positive calibration control.
2. Inverted role signal: adverse future transfer.
3. Collapsed role signal: weaker global baseline can outperform the candidate.
4. Balanced future noise: neutral comparison.
5. No useful role distinction: original method must HOLD.
6. Too few reported roots: original method must HOLD.

The original candidate receives ONLY calibration records. The independent test harness measures its frozen candidate predictions on separately supplied fictional future labels. Controls: global classical plurality and independently implemented strong role-conditioned classical plurality using exactly the same first-two-per-role training data.

The strong role-conditioned comparator is mathematically the same conditional policy. An exact tie is the expected honest result; positive transfer superiority is NOT established. Adverse future regimes must demonstrate regression. No human evidence, truth verification, or model-weight learning is involved. The test author could see every synthetic fixture, so this is not a genuinely blind scientific evaluation.

## Reproduce

Requires Python 3.11+, Git, Docker, and an already locally available node:22-alpine image.

    python -m unittest discover -s tests -v
    python -m motif.method_tournament --query "reciprocal role conditioned prediction"
    python -m motif.method_tournament --query "reciprocal role conditioned prediction" \
      --execute --out /tmp/motif-method-tournament-evidence.json

The first command is read-only preflight. The second explicitly executes the original method in an ephemeral nonroot, read-only, no-network Docker container, with CPU/RAM/PID/time limits, fixed command arguments, and no mounted credentials. The full original source commit, source documents, fixture/evaluator hashes, original native tests and measured negative and positive comparisons are recorded.

Afterward, reuse the HELD method locator without merging or executing its source:

    python -m motif.method_tournament \
      --receipt /tmp/motif-method-tournament-evidence.json \
      --query "reciprocal role conditioned prediction"

The saved output is a create-only local file. A second invocation verifies the held receipt digest, reobserves the source head and refuses to reuse it silently if the branch moved. An explicit --execute may rerun the same fixed original method; nothing auto-installs or merges.

## Verdict

A green native test suite alone is not transfer. A favorable toy case alone is not transfer. The expected result here is a strong-classical tie, identifiable negative transfer regimes and a content-addressed **HELD SOURCE LOCATOR**, not an admitted method. The SHA-256 receipt detects accidental modification but is not an authentic signature.

Follow-on gates: new independent unseen task families, stronger drift-aware classical methods, source-owned GRAFT admission, and separate owner review. Source ownership and Git merge decisions stay independent. This experiment builds a working tool to compare existing methods without merging their source into MOTIF core.
