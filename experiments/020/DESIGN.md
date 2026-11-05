# MOTIF-020 — Embodied Inquiry (No Credits)

**Question:** Could an intelligence determine whether another question deserves computation *without pricing that computation in artificial credits?*

MOTIF-019 revealed that assigning an arbitrary high cost made the reasoning policy abstain from collecting measurements despite a lower raw prediction error for other predeclared alternatives. The user's architecture instead asks for a **local-first, credits-free useful machine**, eventually able to assess actual energy and resource constraints through **GHoT**.

## GHoT is the source owner

This experiment does **not** invent a CPU budget of its own. It imports a pinned, read-only GHoT physical resource receipt produced by actual test execution on a GitHub runner. The GHoT owner already contains native `power_field.probe_power`, `apply_power_policy`, and `energy_scheduler.decide_from_candidates`; see https://github.com/the-static-collective/GHoT/pull/135 .

The GHoT source file `evidence/resource-witness-2026-11-05.json` at pinned source commit `0cbd111a1f7d58a3e4d1dacaeb6be067cbffe9ad` is copied byte-for-byte under `experiments/020/evidence/`, checked with Git SHA-1 blob identity and CI byte comparison against the source commit. The witness is about repeated questions over **MOTIF-019's existing documented public river analysis**, not repeated physical network acquisition.

The two bounded modes give the same user-visible answer:
- **reparse** read source bytes + hash + parse and validate on every question.
- **reuse** read source bytes + hash on every question, reuse a previously validated answer when and only when SHA-256 matches (else re-validate).

Both perform identical bytes-read and SHA counts, and all answer digests match. The benchmark includes 5 alternating-order trials per mode, 250 repeated questions per trial.

## Actual measured computation

The first GHoT GitHub Actions source-owned run reported:
- Reparse median **100,424,701 process CPU ns** per 250 questions.
- Verified reuse median **28,376,628 process CPU ns** per 250 questions.
- An observed reduction of **72,048,073 process CPU ns** (~71.74%) on that specific machine/workload.
- Elapsed-wall time and Python tracemalloc memory high-water are recorded separately.
- Each mode read **2,426,750 source bytes** per trial; no I/O byte savings.
- Full validation ran 250 times with reparsing, only once with verified reuse.
- **Electrical joules, actual watts, battery drain, and CO₂ were not measured.** No energy-use or carbon savings inferred from CPU time.

This is a proof of **resource-aware reasoning against real execution metrics**, not an energy-optimization guarantee. The runner's power class was `normal` with an *unknown* power source; GHoT's scheduler returned hypothetical `run_here` for a simulated local offer. There was **no real capability assignment, lease, or remote execution**.

## The new decision organism

`ghot_resource_bridge.py` is a fail-closed **evidence consumer**, not an autonomous controller. It independently checks per-trial CPU readings, wall readings, parse counts, byte counts, identical answer digest, GHoT native dry-run limitations, and known-missing Joules before composing an explicit, held-for-independent-test improvement proposal:

> Could verified answer reuse reduce computation on the actual operator device without losing freshness, reliability or useful outcomes?

It never chooses a global optimum by adding unlike units: nanoseconds, bytes, memory, and (future) joules remain distinct. Unknown energy stays `null`, never zero. User urgency, deferrability, quality requirements, and energy constraints must be supplied by the operator or actual physical probes.

## How to reproduce

```sh
python3 -m unittest discover -s experiments/020 -p 'test_*.py' -v
python3 experiments/020/ghot_resource_bridge.py --out embodied-resource-question.json
```

The GitHub Actions workflow independently compares the source-owned GHoT evidence bytes to the pinned source commit, runs tests, and uploads MOTIF's derived diagnostic JSON.

**Next stage:** GHoT on actual low-power hardware can record attributable battery/power meter readings or external metered watt-hours and persistent task receipts, alongside observed task quality, latency, data-transfer cost, and explicit urgency. Cross-body comparisons require measured and consistent conditions. Until those receipts exist, energy-based strategy admission remains HELD.

No hosted AI credit dependency, no arbitrary token-dollar conversion, no autonomous source rewriting, no external actions, and no claim of truly free compute.
