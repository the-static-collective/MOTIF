# MOTIF-014 — THE ORGAN GARDENER / THE QUESTION IS ALSO AN ORGAN

**Status: executable, offline, deterministic synthetic research. NOT self-improving AGI, an autonomous patch system, an authenticated research assistant, or an external-action pipeline.**

## What is real in this experiment
- The **original National Treasure Question Box v0.1** engine is included **byte for byte** from the still-unmerged National Treasure PR #70, exact source commit `28fbf9b10d003f7c577143550d17cc17f8109cb1`, Git blob `83574ed0a927fdefe1a53b3ece0960f011b875d0`. The `buildQuestionFrontier` function really runs. It preserves provenance/support axes and outputs questions with NO answer or conclusion.
- The **original Dogram `analyze_probe_family`** Python implementation is included **byte for byte** from Dogram main commit `551b5f9df18f17ec69b452ddcdff01718e0ff771`, Git blob `c201ce28ff7bb18a28496c0a2eefe2f9451526cc`. A separate JSON/stdin adapter validates its original Git blob identity and invokes it, keeping native Dogram partition-refinement semantics. This research module is **not** a promoted Dogram public operator.
- The MOTIF-014 coordinator invokes both original organs, receipts their results, and evaluates **three developer-supplied** inquiry policies: fixed probe order, Dogram-minimal separator, and Dogram cost-aware separator. It changes the *method proposal*, not Dogram, National Treasure, the installed runtime, or Git history.

## Flow
```
Synthetic question + source/evidence assertions
  -> genuine National Treasure Question Box
  -> if missing source/chronology/counterevidence/falsifier/rivals: HOLD
  -> if question is a minimum discriminator: genuine Dogram native probe
  -> compose candidate inquiry method (fixed / minimal / cost-aware)
  -> freeze predicted probe plan (no probe is performed in reality)
  -> compare same task/cost/observation budget with fixed & classical cost-minimum
  -> training gain + independent held-out parity
  -> REFUSE or HOLD_FOR_HUMAN_REVIEW
```

This is **not** a claim that a populated source locator is independently recovered evidence. Every locator in the fixtures is explicitly invented. A real implementation would need independently inspected source custody before considering it verified.

## Falsifying counterexample (not dropped)
The original National Treasure Box permits a discriminator question only after its earlier gaps are filled. Dogram exposes two *incomparable minimal probes* in the finite test family. On ordinary cases, choosing one saves cost versus probing in a fixed order. On an out-of-sample case a **stronger** joint probe is cheaper than the minimal separators. The naive 'always choose minimal separator' proposed method LOSES to the conventional cost-optimal selector. The garden's gate returns **REFUSE_HOLDOUT_REGRET** rather than promoting it. The cost-aware method ties the strong classical baseline and stays **HOLD_FOR_HUMAN_REVIEW**.

No oracle outcomes, user identities, real external data, tool authority, human permission, or third-party API calls enter. The experiment does not learn the policy family from scratch. It does **not** demonstrate architectural superiority; its cost-aware variant is itself the classical optimization baseline.

## Reproduce (Python 3.10+, Node 20+, no dependencies)
```sh
node --test experiments/014/test_garden.mjs
node experiments/014/organ_garden.mjs > /tmp/motif014-results.json
```
For the native math entry alone:
```sh
echo '{"states":["a","b","c","d"],"target":["a","d"],"probes":{"coarse":["all","all","all","all"],"vertical":["L","L","R","R"],"diagonal":["U","D","U","D"],"joint":["LU","LD","RU","RD"]}}' | python3 experiments/014/dogram_bridge.py
```

## Neighboring organs — source-preserving future crossing, not live bindings
- **National Treasure Question Box PR #70**: required question-origin / source-recovery aperture. Its separate MEMENTO held-seed adapter in PR #85 is not imported; private sources do not cross.
- **Dogram**: original finite information/refinement math; experimental adaptive probe cost and anti-collapse work inform future *reviewed* cartridge contracts, not magically promoted operators.
- **LOADOUT**: future exact body/effect fences for any effectful worker.
- **3rdi**: future questioner's observer-local epistemic cut; later knowledge cannot rewrite earlier access.
- **ALEX.2**: hypothesis, evidence provenance, source-family independence and claim support.
- **OpenManus**: optional isolated, reviewed candidate code-authoring worker. No worker runs here.
- **ELF / Seedbank**: bounded per-occurrence reproduction of admitted method cartridges, not agent immortality or authority transport.
- **GRAFT**: source-preserving research grafts and retained parent methods.
- **JAR;VIS**: optional human-facing inquiry/answer/return surface; no live runtime binding or external exchange is claimed.
- **Cultural attention / BananaGraft**: candidate environmental surprise and recombination inputs; public cultural observations never become causally established simply by repetition.

## Specific next trials
1. Compare earned National Treasure questions with random, simple checklist, learned inquiry-selection and conventional adaptive testing under matched missingness and cost.
2. Generate genuinely unfamiliar, noisy/nonstationary probe families before revealing holdouts; test performance against decision trees, Bayesian experiment design, and robust policies.
3. Change the *questioner-selection method* itself and compare old/new from IDENTICAL initial evidence, not from different experience totals.
4. Introduce separately frozen effect fences, independent source adjudication, limited resource/compute cost and explicit human review.
5. Test guarded OpenManus edits only in disposable trees, verify source-native tests and leave source owners to decide adoption.

**Question != answer. Measured gain != permission. A changed method != a better method. A useful graft != a merged organ.**
