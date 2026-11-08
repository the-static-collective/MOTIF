# RING-015 — Value of the **Second Real Experiment**

**Goal:** Don't force MOTIF to choose the strongest expensive test first. Let it perform a cheap **real** source observation, choose a **different second test** based on what it actually observed, and optionally perform a third source test after new evidence. Compare this strategy against the strongest simple baseline that always runs the complete suite.

**Status:** Research draft, stacked on RING-014. All tool execution is restricted to reviewed RING-013 source copies in network-disabled, read-only Docker. The planner **does not modify the original repository, send messages, use network services, call cloud tools, commit fixes, or gain any new external permissions**.

## The question

```text
             AMBIGUITY PRESERVED (RING-012)
                            │
          EMPIRICALLY ESTIMATED VALUE OF WORK
                            │
            ┌───────────────┴────────────────┐
            ▼                                ▼
      FULL regression                  CHEAP TRIAGE
                                          │
                   Actual AST change-region observation
                  ┌───────────┬────────────┼───────────┐
                  ▼           ▼            ▼           ▼
                MATH        CONTROL       MIXED       CLEANISH
                  │           │            │           │
                  ▼           ▼            ▼           ▼
               Focused      Focused       FULL       STOP / FULL
               math test    control test
                  │           │
                  └─────┬─────┘
                        ▼
                  ACTUAL PASS/FAIL
                        │
                 PASS ──┴── FAIL
                   │        │
                   ▼        ▼
           Evaluate value   STOP + source
           of deeper FULL   failure receipt
                   │
                 STOP/FULL
```

**The important distinction:** TRIAGE is not an oracle: it reports *which reviewed AST function region differs from a pinned baseline*, and cannot determine whether the difference is a real defect. Benign changed code is included specifically to test that limitation. The language-reasoning system has no authority to execute a tool merely by recognizing a command.

## Real, differentiated internal tools

The planner can invoke exactly **TRIAGE, MATH, CONTROL, FULL, or STOP**:

| Action | Actual read-only source work | Limits |
| --- | --- | --- |
| **TRIAGE** | Parse copied Python with `ast.parse`; compare function-level AST structures to the pinned previous source; report MATH, CONTROL, MIXED, OTHER, UNCHANGED or real syntax failure. | A changed region is *not proof* of defect. |
| **MATH** | Execute the real copied RING-013 Bayesian posterior, entropy and information-gain functions against independently calculated invariants. | Won't establish budget or authority correctness. |
| **CONTROL** | Execute actual forbidden-action, negative-value STOP, finite-budget and external-effect-claim tests against the copied code. | Won't establish mathematical posterior correctness. |
| **FULL** | Execute **both** focused checks, the inherited RING-013 regression suite, and 140 additional deterministic actual planner calls on reviewed source. | Stronger, broader and more costly than either focused test. |
| **STOP** | Consume no additional test resources and preserve the uncertainty / failure receipt. | May miss a defect. |

The worker runs inside a tightly scoped Docker container: `--network none --read-only`, unprivileged UID, dropped capabilities, no-new-privileges, strict memory/CPU/PID limits, read-only source + fixture mounts, and no host-test fallback. These controls are practical source-research containment for **reviewed** code, not a formally verified sandbox for arbitrary adversarial programs.

## Experimental design

Source target: the actual predecessor's reviewed `experiments/cartridge-ring-013/value.py` and `scenario.py`.

- **Training:** 12 source copies, including deliberately faulty, unchanged, and benign-but-changed code.
- **Development:** 6 separate source copies used **only after** failure probabilities are fitted from training. Real dev test outcomes and authored defect labels select a decision policy.
- **Source measurements:** 18 source copies × four real test phases = **72 executed isolated calibration tests**. Evidence contains actual Python interpreter/test returns, source hashes and measured wall time, rather than fabricated PASS/FAIL messages.
- **Value-policy search:** 18 combinations of author-defined detection benefit, time cost and false-alarm penalty × either autonomous first-test choice or experimental triage-first = **36** evaluated calibration policies.
- **Freeze:** Source training measurements, empirical cue-frequency estimates, observed phase sensitivity, original source code hashes, Docker image content ID, frozen 012 ambiguity provenance, value settings and selected mode are all receipt-bound **before** the next source challenge enters.
- **Post-freeze:** 18 new-to-selection reviewed source copies: **12 developer-injected defect cases** (including mixed source changes), **6 unchanged or benign-edit controls**. Every case receives a **live** initial action. Its next action is selected only after the previous actual Docker observation returns.
- **Comparators:** always FULL, always STOP, TRIAGE-only, TRIAGE then targeted test, TRIAGE then optionally deeper test, autonomously chosen first-test strategy, and run all tests until failure.

### Scoring and source limitations

The principal noninvented measurements are **actual test PASS/FAIL**, **actual executed tests**, **source assertions**, and **measured Docker wall time**. Developer-created test edits and their *defect* labels make the controlled comparison possible. They do **not** demonstrate independent bug-finding ability on unpredictable software.

The benchmark's utility numbers combine actual measurements with **researcher-chosen reward for finding a seeded bug and penalty for missing one, false alarms and resource cost**. These units are not dollars, independently verified human interests, or proved real-world benefits. Development results were used for policy selection; heldout evaluation is deliberately synthetic and not independently generated by a second experimenter.

The frozen selection is allowed to conclude that FULL is better than TRIAGE. That would be a legitimate negative result, **not** a failure to execute this experiment. The triage-first comparator separately tests whether an observed first result can guide a real second test.

## Provenance and risk reporting

- `fixtures.py`: reviewable byte-exact source-copy changes, intentional defects and harmless AST edits. Source generator labels are evaluator-only.
- `worker.py`: actual differentiated test functions. No fabricated source-test success flags.
- `runner.py`: strict Docker action enumeration and source-bound JSON evidence.
- `policy.py`: empirically derived action cost/sensitivity, prior updates, source-cue-conditioned follow-ups and STOP.
- `learn.py`: frozen 72-real-test calibration, source-only train/dev sampling and 36 policy candidates.
- `sealed.py`: separate 18-case test specification, never imported by selection.
- `trial.py`: **live** adaptive test execution before additional comparator measurements. Stores every source witness, next-action decision and complete diagnostic test matrix.
- `evidence_graph.py`: recomputes selected next actions without hidden mutation labels and reconciles every observed test against the selected and baseline scores, including missed defects, false positives, second/third tests, CPU/test counts and wall time.
- `test_contracts.py`: actually executes source triage, mathematical and control regressions, benign changed-code checks and the FULL suite inside the Docker environment.

## Reproduction

```sh
docker pull python:3.11-slim
python -m unittest discover -s experiments/cartridge-ring-015 -p 'test_*.py' -v

python experiments/cartridge-ring-015/learn.py \
  --out /tmp/ring015-frozen-policy.json

python experiments/cartridge-ring-015/trial.py \
  --frozen /tmp/ring015-frozen-policy.json \
  --out /tmp/ring015-real-followup-trial.json

python experiments/cartridge-ring-015/evidence_graph.py \
  --frozen /tmp/ring015-frozen-policy.json \
  --trial /tmp/ring015-real-followup-trial.json \
  --out /tmp/ring015-source-evidence-graph.json
```

GitHub Actions executes the actual source tests, freezes the selected policy, measures the live next-action sequence on never-consulted new source copies, then tests strong comparators and audits the complete source-linked evidence graph. Three JSON artifacts preserve the freeze, per-case observations, and supporting hypergraph.

## Verified results — source-owned tests, not simulated PASS/FAIL

**Passing GitHub Actions run:** [RING-015 real source experiment #42507101452](https://github.com/the-static-collective/MOTIF/actions/runs/42507101452), source SHA `5731fc672225929e8a0b498baf6e672259d318a9`. The run completed **11 unit/contract tests**, **72 real Docker source-test invocations for calibration**, **72 post-freeze case-phase source measurements**, the live conditional follow-up probe, and the receipt-reconciled evidence graph.

### The negative decision-quality finding is real

The frozen model selected:

```json
{
  "detection_benefit": 24.0,
  "false_alarm_penalty": 10.0,
  "time_weight": 0.5,
  "force_triage": false
}
```

On **18 new-to-model-selection, developer-authored source copies** (12 intentionally faulty, six unchanged/benign), it chose **FULL immediately in every case**, rather than pay for TRIAGE first. The source tests are real; the mutation distribution and reward conversion are written by the experimenter.

| Decision method | Planted defects found | Real test phases counted | Observed Docker wall time | Missed defects | Clean false alarms |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Frozen autonomous value policy** | **12/12** | **18** | **10.68 seconds** | **0** | **0/6** |
| Strong **FULL-only** control | **12/12** | **18** | **10.68 seconds** | **0** | **0/6** |
| TRIAGE → target based on observed region | 12/12 | 33 | 13.34 seconds | 0 | 0/6 |
| TRIAGE → value-selected follow-up, sometimes FULL | 12/12 | 39 | 19.10 seconds | 0 | 0/6 |
| Exhaustive TRIAGE → MATH → CONTROL → FULL until failure | 12/12 | 52 | 24.47 seconds | 0 | 0/6 |
| TRIAGE-only | 1/12 | 18 | 7.14 seconds | 11 | 0/6 |
| Always STOP | 0/12 | 0 | 0 | 12 | 0/6 |

The **autonomous selected strategy tied FULL-only exactly**. It did **not** discover a more cost-efficient multi-step decision strategy on this task distribution. In particular, the larger number of separate cold Docker invocations in triage-first strategies contributed substantial measured wall time; the experiment does not separately identify Docker startup as the sole causal reason.

The triage-based comparator results were computed **after the selected policy completed**, by replaying alternative action choices against separately executed real code tests. Those comparators are **not** evidence that the selected autonomous policy dynamically launched a second tool invocation in the main heldout trial. They *do* preserve the actual measured source-test outcomes and costs for each method.

### Separate live end-to-end demonstration of the second experiment

To test the actual conditional **execution mechanism** instead of merely replaying a comparator, `probe_live.py` performed a separately authorized research intervention: **TRIAGE was deliberately forced as the first action** on three additional source copies, but the *subsequent* test choice was made by the frozen value policy **after receiving the first real Docker observation**. All requested subsequent tests then actually executed in separate no-network read-only Docker invocations.

The verified real sequences were:

```text
Real source math change    → TRIAGE → MATH
Real source control change → TRIAGE → CONTROL
Benign control code change → TRIAGE → CONTROL → FULL
```

**3/3 new demonstration cases executed a real second test**, and one proceeded to a third after its focused check passed. No external effects occurred. The test therefore establishes that the mechanism can do conditional further work in reality under an explicitly permitted first action. It **does not** show that the *autonomous value selector* chose this intervention on its own, nor that using it improved aggregate efficiency or independent real-world defect detection.

The source model retained open-world language uncertainty and never interpreted an apparent directive as tool-execution permission.

### The actual frontier revealed

**Capability gained:** credible, evidence-bound, real-tool, multi-step conditional source testing with an independent permission boundary and source-level negative-result reporting.

**Capability NOT established:** discovering when that path *beats* the simplest strong full test under the observed total cost. An obvious next falsifier is one **persistent networkless test session** per source case, where executing a second focused check does not incur a fresh container startup, or genuinely heterogeneous test operations whose costs and coverage make inspection worthwhile. That must be compared fairly against the same strong full-suite control, with an untouched new evaluation set. Other unresolved frontiers remain independently authored bugs and authorized disposable source repair.

## What would constitute a meaningful RING-015 result?

- **Capability demonstration:** At least one case executes an actual **first source observation** and chooses a **different second source test based on the observed cue**; the chosen test truly runs and its outcome is recorded, with no outside effects.
- **Evidence of superior selection:** A calibrated **autonomous** strategy finds at least as many seeded defects as FULL-only while consuming materially less real source-test time. If that does not happen, report the tie/loss and retain the useful conditional-execution mechanism.
- **Remaining frontier:** Distinct real test families and imperfect probes from **independently sourced** issues, without letting fixture generation encode how to find them. Actual source repair should stay in a disposable reviewed branch with separate explicit merge/deployment permissions.

**Ambiguity remains an ordinary state. The value of doing one more thing must justify the resource cost, not the excitement of continuing.**
