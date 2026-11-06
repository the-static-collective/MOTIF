# MOTIF RING-004 — Same Evidence, Three Original Methods, One Falsifier

**Status:** experimentally implemented, source-native, auditable *synthetic* shared-world benchmark; not merged into production. This experiment follows RING-003's typed many-to-many affordance hypotheses and tests whether they have measurable value beyond the graph's author-declared numbers.

## Research question

Does applying multiple source-owned reasoning methods to the **same previously unseen-to-native test cases** improve task outcomes over each constituent method, simpler combinations, and strong classical controls?

The common task is deliberately small: a human asks whether a synthetic route S → A → T survives removal of S → T. An observer records events on channels a and b, some events duplicated with identical declared IDs. The derived boolean for edge A → T is XOR of the unique-record count parities; the independent gate S → A is known. An unsafe effectful utterance or invalid recorded witness must HOLD. Each source-owned method must process the **same exact public case packet**, not unrelated demonstration fixtures.

### Three genuinely original source-owned methods

1. **THOUGHT-014** original `LanguageSpace.explore` with the source's actual locally trained, offline `TinyTextModel`, plus the original conservative THOUGHT-013 interpreter. The classifier is trained **only on original THOUGHT-014 source-authored TRAIN examples**. It can propose a speech act for a bounded previously UNKNOWN phrase but cannot approve any effectful text, generate concept IDs, or edit a graph. No LLM, T5, or network inference.
2. **GEOM-013** original `demo.two_revisions()` develops a duplicate-aware `Revision` on its separate original development data. Both the original raw instrument and the learned procedure are actually called via `Revision.measure` on the same new public held-out traces; no hidden expected label is provided to these measurements.
3. **REASON-006** original source-pinned `run_council` with its graph owner/proof checks and synthetic source witnesses, runs on each case's route graph using both raw and repaired measurements, independently. These are mathematical proof results **relative to declared synthetic inputs**. They do not authenticate the underlying event identities or establish physical reality.

### Source isolation, fair witnesses, hidden scoring labels

The controller extracts each native codebase at its **exact pinned Git commit**, without copying or rewriting its owner implementation. The source trees and a common **public input only** are mounted into an unprivileged Docker container as read-only files, with network disabled, no host Git credentials or Docker socket, bounded CPU/memory/PIDs and no installed external services.

Two deterministic author-generated seeds give **32 distinct shared-world tasks each**, with a mixture of duplicate records, clean records, gate-open/closed, unsafe human requests, missing traces, and missing IDs. The fixture generator keeps task labels and true unique-event parities entirely in the host controller. Hidden labels are never written into the mounted native-source filesystem. One native adapter's `RecordedCase` constructor requires a Boolean expected field; it receives the **same constant false sentinel on every case**, and the `measure` method does not use it. Labels are used by the controller only after native source inference returns.

This is a genuine input-label separation **relative to the pinned models**, but not a third-party blind test. The scenario, source mechanisms, and scoring logic are all author-designed, and the synthetic traces contain no authenticated world observations.

### Ablations and controls

The benchmark evaluates the same cases and exact labels through these controls:

- **All 3 original source methods**, including original trained tiny classifier, duplicate-aware GEOM-013, source-bound REASON-006 council.
- The same composition but without original TinyTextModel suggestions, using deterministic THOUGHT-013 interpreter alone.
- REASON-006 with raw record counts, no GEOM-013 deduplication or language membrane.
- THOUGHT-014 + REASON-006, but with raw measurements.
- GEOM-013 + REASON-006, but without language guard.
- GEOM-013 alone with no graph reasoning, THOUGHT-014 alone without graph/measurements.
- **THOUGHT-014 + GEOM-013 + direct classical graph interpretation**, without REASON-006. This is an important stronger substitute; on this simple graph it can match all three on decision accuracy.
- A weak classical raw-record parity baseline.
- A deliberately **strong classical baseline** using effect filtering, exact declared-ID deduplication, parity, and BFS on the same public evidence. On this toy world it is expected to tie the full composition.

Both the written source-native `REASON-006` proof and the handwritten classical BFS are conditional on synthetic declared witness truth. Reporting a proof receipt does not establish independence of those observations.

### Initial measured results: two seeds, 64 cases

| Method | Correct / 32, seed 2026110615 | Correct / 32, seed 2026110616 |
|---|---:|---:|
| All 3 native, including source-trained tiny classifier | **32** | **32** |
| All 3 without tiny classifier | 20 | 20 |
| THOUGHT-014 + REASON-006, raw measurement | 24 | 26 |
| GEOM-013 + REASON-006, no language membrane | 29 | 29 |
| REASON-006 only, raw measurements | 21 | 23 |
| GEOM-013 alone (no graph proof) | 23 | 24 |
| THOUGHT-014 + GEOM-013 + direct classical graph | **32** | **32** |
| Strong classical exact dedup + BFS | **32** | **32** |

The paired condition with actual original trained THOUGHT-014 model returns 12 additional correct decisions per seed compared with the deterministic interpreter, because the latter HOLDs some unfamiliar phrase forms. The improvement on these selected synthetic task phrases does **not** establish open-domain natural-language competence. Separate GEOM-013 repaired measurements address raw duplicate-count errors, and language authorization avoids treating effect requests as ordinary reasoning instructions.

**Negative result:** the full three-native composition **does not outperform the strongest classical baseline** and does not outperform the simpler THOUGHT-014 + GEOM-013 + classical graph substitution in decision accuracy on this artificial graph. REASON-006 contributes a source-owned proof/council receipt but not an additional correct decision in these fixtures. This is valuable because it provides a falsifiable measure of redundancy and potential computation waste rather than a false "emergence" claim.

### Measured hypergraph feedback, not automatic adoption

`feedback.py` validates each experiment's source pins, full case-by-case predictions, author labels, checksum, and no-authority claims, prevents re-counting a duplicate case packet, then creates multi-tail conditional **`OBSERVED_SYNTHETIC_CONDITIONAL_ABLATION`** evidence hyperedges. The tails identify both the source methods used and the original trial evidence; the heads identify the control's measured results and counterfactual contrast with full native.

These **observed synthetic edges** remain separate from RING-003's merely declared affordance hypotheses. They cannot grant new executors, mutate method graph truth, or authorize external effects. The measurements identify specific conditional contrasts, not independent causal contributions from each method and not general transfer to other problems.

## Reproduce in GitHub Actions

```sh
python -m unittest discover -s experiments/cartridge-ring-004 -p 'test_*.py' -v
docker pull python:3.11-slim

python experiments/cartridge-ring-004/comparator.py \
  --seed 2026110615 --count 32 --out /tmp/shared-a.json
python experiments/cartridge-ring-004/comparator.py \
  --seed 2026110616 --count 32 --out /tmp/shared-b.json

python experiments/cartridge-ring-004/feedback.py \
  --trials /tmp/shared-a.json /tmp/shared-b.json --out /tmp/hypergraph-feedback.json
```

A full Git fetch of all three pinned source commits is required (`actions/checkout` uses `fetch-depth: 0`). No network is available inside the execution container. The reference Docker image tag should be pinned to a digest in production-grade replications; the current exercise is draft research.

## Next falsification frontier

A more meaningful future test should: diversify tasks beyond tiny graph XOR, freeze strong baseline protocols **before** new experiments, include held-out scenarios written by independent operators, stress adversarial and conflicting source evidence, perform measured resource/latency accounting, compare original council to a fully verified classical graph prover on the same packets, and learn generalizable conditionally useful hyperedges only from *repeated independent evidence*. A cartridge that contributes no incremental value in the tested context must remain optional, not be rewarded merely for joining the composition.

**No arbitrary branch executes; no automatic code generation, merging, source authentication, external communication, or PEN authority is granted.**
